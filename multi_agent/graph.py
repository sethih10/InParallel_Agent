"""LangGraph assembly for the compliance multi-agent system.

This file only wires nodes and edges. All business logic lives in:
    - ``multi_agent.agents.*``   (LLM agents)
    - ``multi_agent.nodes.*``    (deterministic nodes)
    - ``multi_agent.tools.*``    (tools available to the agents)

Graph topology::

    START
      |
      v
    orchestrator         (LLM - context & legal assessment)
      |
      v
    compliance_analyst   (LLM)
      |
      v
    [interrupt_before]   (HITL Gate 1: legal team confirms findings)
      |
      v
    legal_researcher     (LLM)
      |
      v
    [interrupt_before]   (HITL Gate 2: legal team approves solutions)
      |
      v
    notifier             (LLM)
      |
      v
    report_generator     (deterministic)
      |
      v
    END

A ``MemorySaver`` checkpointer is required because the graph uses
``interrupt_before`` — the checkpointer is what lets the graph pause and
resume across user turns.
"""

from __future__ import annotations

import json
import re
import uuid
from typing import Any, Dict, List, Optional

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from multi_agent.agents import (
    build_compliance_analyst,
    build_legal_researcher,
    build_notifier,
    build_orchestrator,
)
from multi_agent.nodes.report_generator import report_generator_node
from multi_agent.policies import get_regulation


# --------------------------------------------------------------------------- #
# Inner-agent recursion limit                                                 #
# --------------------------------------------------------------------------- #
# Each ReAct agent (compliance_analyst, legal_researcher, notifier) runs its
# own internal LangGraph: every tool call adds two ticks (LLM -> tool -> LLM).
# The default cap of 25 is too low for the compliance analyst, which inspects
# 7 decisions against ~24 regulations. Raise it; each agent still terminates
# via its system-prompt "produce JSON and stop" instruction.
INNER_AGENT_RECURSION_LIMIT = 80
from multi_agent.state import ComplianceState


# --------------------------------------------------------------------------- #
# JSON extraction helper                                                      #
# --------------------------------------------------------------------------- #

_JSON_BLOCK_RE = re.compile(r"```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```", re.DOTALL)


def _extract_json(text: str) -> Dict[str, Any]:
    """Best-effort extraction of a JSON object from an agent's final message.

    Tries (in order):
      1. ```json ... ``` fenced block
      2. The largest ``{...}`` substring
    Returns ``{}`` if no JSON can be parsed.
    """
    if not isinstance(text, str):
        return {}

    m = _JSON_BLOCK_RE.search(text)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass

    # Fallback: find the outermost { ... } span.
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidate = text[start : end + 1]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            return {}
    return {}


def _last_message_content(agent_result: Dict[str, Any]) -> str:
    msgs = agent_result.get("messages", [])
    if not msgs:
        return ""
    last = msgs[-1]
    content = getattr(last, "content", last)
    if isinstance(content, list):
        # Anthropic may return content as a list of blocks
        return "".join(b.get("text", "") for b in content if isinstance(b, dict))
    return content or ""


# --------------------------------------------------------------------------- #
# Node: Orchestrator                                                          #
# --------------------------------------------------------------------------- #


def orchestrator_node(state: ComplianceState) -> Dict[str, Any]:
    """Run the Orchestrator agent to assess meeting context and legal presence.
    
    The orchestrator inspects the meeting within the company's organizational
    and regulatory context, assessing whether a lawyer should have been present.
    """
    meeting_id = state.get("meeting_id")
    company_id = state.get("company_id", "org-lumiere")  # default demo company
    
    if not meeting_id:
        raise ValueError("orchestrator_node: meeting_id is required in state")

    agent = build_orchestrator()
    user_msg = HumanMessage(
        content=(
            f"Please assess meeting_id=\"{meeting_id}\" within company_id=\"{company_id}\". "
            "Follow the workflow in your system prompt and return the JSON "
            "object with all required fields as your final message."
        )
    )
    result = agent.invoke(
        {"messages": [user_msg]},
        config={"recursion_limit": INNER_AGENT_RECURSION_LIMIT},
    )
    parsed = _extract_json(_last_message_content(result))

    # Store the full orchestrator output in state
    orchestrator_output = parsed if isinstance(parsed, dict) else {}
    
    return {"orchestrator_output": orchestrator_output}


# --------------------------------------------------------------------------- #
# Node: Compliance Analyst                                                    #
# --------------------------------------------------------------------------- #


def _enrich_finding(raw: Dict[str, Any], index: int) -> Optional[Dict[str, Any]]:
    """Combine the agent's raw finding with policy-library metadata."""
    regulation_id = raw.get("regulation_id")
    reg = get_regulation(regulation_id) if regulation_id else None
    if reg is None:
        return None  # drop hallucinated regulation ids

    return {
        "id": f"finding-{index:03d}",
        "decision_id": raw.get("decision_id", ""),
        "summary": raw.get("summary", ""),
        "transcript_quote": raw.get("transcript_quote", ""),
        "transcript_speaker": raw.get("transcript_speaker", ""),
        "regulation": {
            "id": reg["id"],
            "regulation": reg["regulation"],
            "article": reg["article"],
            "title": reg["title"],
            "requirement_text": reg["requirements"],
        },
        "severity": reg["severity"],
        "max_fine": reg["max_fine"],
        "responsible_department": reg["responsible_department"],
        "confirmed": False,
        "precedent_doc_ids": [],
    }


def compliance_analyst_node(state: ComplianceState) -> Dict[str, Any]:
    """Run the Compliance Analyst agent and store potential findings."""
    meeting_id = state.get("meeting_id")
    if not meeting_id:
        raise ValueError("compliance_analyst_node: meeting_id is required in state")

    agent = build_compliance_analyst()
    user_msg = HumanMessage(
        content=(
            f"Analyse meeting_id=\"{meeting_id}\" for compliance issues. "
            "Follow the workflow in your system prompt and return the JSON "
            "object with the `findings` key as your final message."
        )
    )
    result = agent.invoke(
        {"messages": [user_msg]},
        config={"recursion_limit": INNER_AGENT_RECURSION_LIMIT},
    )
    parsed = _extract_json(_last_message_content(result))

    raw_findings = parsed.get("findings", []) if isinstance(parsed, dict) else []
    enriched: List[Dict[str, Any]] = []
    for i, raw in enumerate(raw_findings, start=1):
        f = _enrich_finding(raw, i)
        if f is not None:
            enriched.append(f)

    return {"potential_findings": enriched}


# --------------------------------------------------------------------------- #
# Node: Legal Researcher                                                      #
# --------------------------------------------------------------------------- #


def _solution_from_raw(raw: Dict[str, Any], index: int) -> Optional[Dict[str, Any]]:
    cited = raw.get("cited_doc_ids") or []
    if not cited:
        return None  # enforce evidence-chain invariant
    return {
        "id": f"solution-{index:03d}",
        "finding_id": raw.get("finding_id", ""),
        "proposal": raw.get("proposal", ""),
        "cited_doc_ids": list(cited),
        "rationale": raw.get("rationale", ""),
        "approved": None,
        "user_edited_proposal": None,
    }


def legal_researcher_node(state: ComplianceState) -> Dict[str, Any]:
    """Run the Legal Research agent and store proposed solutions."""
    confirmed = state.get("confirmed_findings") or []
    if not confirmed:
        return {"proposed_solutions": []}

    # Hand the confirmed findings to the agent as a structured payload.
    payload = json.dumps(
        [
            {
                "finding_id": f["id"],
                "summary": f.get("summary"),
                "regulation": f.get("regulation"),
                "severity": f.get("severity"),
                "transcript_quote": f.get("transcript_quote"),
                "responsible_department": f.get("responsible_department"),
            }
            for f in confirmed
        ],
        indent=2,
    )
    agent = build_legal_researcher()
    user_msg = HumanMessage(
        content=(
            "The legal team has confirmed the following findings as real legal "
            "issues. For each finding, produce one remediation solution that "
            "cites company-database documents as evidence. Follow the workflow "
            "in your system prompt and return the JSON object with the "
            "`solutions` key as your final message.\n\n"
            f"CONFIRMED FINDINGS:\n{payload}"
        )
    )
    result = agent.invoke(
        {"messages": [user_msg]},
        config={"recursion_limit": INNER_AGENT_RECURSION_LIMIT},
    )
    parsed = _extract_json(_last_message_content(result))

    raw_solutions = parsed.get("solutions", []) if isinstance(parsed, dict) else []
    solutions: List[Dict[str, Any]] = []
    for i, raw in enumerate(raw_solutions, start=1):
        s = _solution_from_raw(raw, i)
        if s is not None:
            solutions.append(s)

    return {"proposed_solutions": solutions}


# --------------------------------------------------------------------------- #
# Node: Notifier                                                              #
# --------------------------------------------------------------------------- #


def notifier_node(state: ComplianceState) -> Dict[str, Any]:
    """Run the Notification & Coordination agent."""
    approved = state.get("approved_solutions") or []
    confirmed = state.get("confirmed_findings") or []
    if not approved:
        return {
            "department_notifications": [],
            "meeting_agenda": None,
        }

    # Build the agent payload combining approved solutions with their findings.
    findings_by_id = {f["id"]: f for f in confirmed}
    payload_rows = []
    for s in approved:
        f = findings_by_id.get(s.get("finding_id", ""), {})
        payload_rows.append({
            "finding_id": s.get("finding_id"),
            "summary": f.get("summary"),
            "severity": f.get("severity"),
            "regulation": f.get("regulation"),
            "responsible_department": f.get("responsible_department"),
            "proposed_solution": s.get("user_edited_proposal") or s.get("proposal"),
            "rationale": s.get("rationale"),
            "cited_doc_ids": s.get("cited_doc_ids") or [],
        })
    payload = json.dumps(payload_rows, indent=2)

    agent = build_notifier()
    user_msg = HumanMessage(
        content=(
            "The legal team has approved the following remediation solutions. "
            "Identify the affected departments, draft per-department "
            "notifications, and a single cross-functional meeting agenda. "
            "Follow the workflow in your system prompt and return the JSON "
            "object with `notifications` and `meeting_agenda` keys as your "
            "final message.\n\n"
            f"APPROVED SOLUTIONS:\n{payload}"
        )
    )
    result = agent.invoke(
        {"messages": [user_msg]},
        config={"recursion_limit": INNER_AGENT_RECURSION_LIMIT},
    )
    parsed = _extract_json(_last_message_content(result))

    notifications = parsed.get("notifications", []) if isinstance(parsed, dict) else []
    meeting_agenda = parsed.get("meeting_agenda") if isinstance(parsed, dict) else None

    return {
        "department_notifications": notifications,
        "meeting_agenda": meeting_agenda,
    }


# --------------------------------------------------------------------------- #
# Graph assembly                                                              #
# --------------------------------------------------------------------------- #


def build_compliance_graph(checkpointer=None):
    """Build and compile the compliance multi-agent graph.

    Args:
        checkpointer: a LangGraph checkpointer (defaults to ``MemorySaver``).
            A checkpointer is required for the ``interrupt_before`` HITL
            gates to pause and resume.

    Returns:
        The compiled graph, ready to be invoked.
    """
    if checkpointer is None:
        checkpointer = MemorySaver()

    builder = StateGraph(ComplianceState)
    builder.add_node("orchestrator", orchestrator_node)
    builder.add_node("compliance_analyst", compliance_analyst_node)
    builder.add_node("legal_researcher", legal_researcher_node)
    builder.add_node("notifier", notifier_node)
    builder.add_node("report_generator", report_generator_node)

    builder.add_edge(START, "orchestrator")
    builder.add_edge("orchestrator", "compliance_analyst")
    builder.add_edge("compliance_analyst", "legal_researcher")
    builder.add_edge("legal_researcher", "notifier")
    builder.add_edge("notifier", "report_generator")
    builder.add_edge("report_generator", END)

    compiled = builder.compile(
        checkpointer=checkpointer,
        interrupt_before=["legal_researcher", "notifier"],
    )
    return compiled


def new_thread_config() -> Dict[str, Any]:
    """Return a fresh LangGraph thread config for a single demo run."""
    return {"configurable": {"thread_id": str(uuid.uuid4())}}


__all__ = [
    "build_compliance_graph",
    "new_thread_config",
    "compliance_analyst_node",
    "legal_researcher_node",
    "notifier_node",
]
