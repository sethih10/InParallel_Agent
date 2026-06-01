"""LangGraph assembly for the compliance multi-agent system.

This file only wires nodes and edges.  All business logic lives in:
    - ``multi_agent.agents.*``   (LLM agents)
    - ``multi_agent.nodes.*``    (deterministic nodes)
    - ``multi_agent.tools.*``    (tools available to the agents)

Graph topology (v4 — parallel notifier + legal researcher)::

    START
      │
      ▼
    compliance_analyst        (LLM)
      │
      ▼
    [interrupt_before]        HITL Gate 1: legal team confirms findings
      │
      ▼
    fan_out                   (deterministic: no-op pass-through)
      ├─────────────┐
      ▼             ▼
    notifier      legal_researcher
      │             │
      ▼             ▼
    fan_in                    (deterministic: no-op merge)
      │
      ▼
    [interrupt_before]        HITL Gate 2: legal team approves solutions
      │
      ▼
    report_generator          (deterministic)
      │
      ▼
    END

After the legal team confirms findings (Gate 1), TWO things happen in
parallel:
  • The **notifier** immediately alerts the concerned departments and
    proposes a meeting between the legal team and each department.
  • The **legal researcher** searches the company DB for precedents and
    drafts remediation solutions.

Both must complete before Gate 2 (approve solutions) fires.

A ``MemorySaver`` checkpointer is required because the graph uses
``interrupt_before`` — the checkpointer persists state across pauses.
"""

from __future__ import annotations

import json
import os as _os
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
)
from multi_agent.config import INNER_AGENT_RECURSION_LIMIT
from multi_agent.nodes.report_generator import report_generator_node
from multi_agent.policies import get_regulation
from multi_agent.state import ComplianceState


# --------------------------------------------------------------------------- #
# Debug flag                                                                  #
# --------------------------------------------------------------------------- #
# Toggle verbose diagnostics: ``COMPLIANCE_DEBUG=1``
DEBUG_AGENTS = _os.environ.get(
    "COMPLIANCE_DEBUG", ""
).lower() in ("1", "true", "yes")


def _debug(node: str, result: Dict[str, Any], parsed: Any) -> None:
    """Print raw agent output when ``COMPLIANCE_DEBUG`` is set."""
    if not DEBUG_AGENTS:
        return
    content = _last_message_content(result)
    msgs = result.get("messages", []) or []
    print(
        f"\n[DEBUG:{node}] messages={len(msgs)}  "
        f"last_msg_len={len(content)}  "
        f"parsed_keys={list(parsed.keys()) if isinstance(parsed, dict) else 'N/A'}"
    )
    print(f"[DEBUG:{node}] --- first 2000 chars ---")
    print(content[:2000])
    if len(content) > 2000:
        print(f"[DEBUG:{node}] --- last 500 chars ---")
        print(content[-500:])
    print(f"[DEBUG:{node}] --- end ---\n")


# --------------------------------------------------------------------------- #
# JSON extraction helper                                                      #
# --------------------------------------------------------------------------- #

_JSON_BLOCK_RE = re.compile(r"```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```", re.DOTALL)


def _extract_json(text: str) -> Dict[str, Any]:
    """Best-effort extraction of a JSON object from an agent's final message."""
    if not isinstance(text, str):
        return {}
    m = _JSON_BLOCK_RE.search(text)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(text[start : end + 1])
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
        return "".join(b.get("text", "") for b in content if isinstance(b, dict))
    return content or ""


# --------------------------------------------------------------------------- #
# Node: Compliance Analyst                                                    #
# --------------------------------------------------------------------------- #


def _enrich_finding(raw: Dict[str, Any], index: int) -> Optional[Dict[str, Any]]:
    regulation_id = raw.get("regulation_id")
    reg = get_regulation(regulation_id) if regulation_id else None
    if reg is None:
        return None
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
    """Run the Compliance Analyst and store potential findings."""
    meeting_id = state.get("meeting_id")
    if not meeting_id:
        raise ValueError("compliance_analyst_node: meeting_id is required")

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
    _debug("compliance_analyst", result, parsed)

    raw_findings = parsed.get("findings", []) if isinstance(parsed, dict) else []
    enriched: List[Dict[str, Any]] = []
    for i, raw in enumerate(raw_findings, start=1):
        f = _enrich_finding(raw, i)
        if f is not None:
            enriched.append(f)
    return {"potential_findings": enriched}


# --------------------------------------------------------------------------- #
# Node: fan_out  (deterministic pass-through)                                 #
# --------------------------------------------------------------------------- #


def fan_out_node(state: ComplianceState) -> Dict[str, Any]:
    """No-op node that acts as the fork point for parallel branches.

    Both ``notifier`` and ``legal_researcher`` read ``confirmed_findings``
    directly from the shared state, so no data transformation is needed.
    """
    return {}


# --------------------------------------------------------------------------- #
# Node: Notifier  (runs immediately after Gate 1, in parallel with legal)     #
# --------------------------------------------------------------------------- #


def notifier_node(state: ComplianceState) -> Dict[str, Any]:
    """Notify concerned departments and propose meetings with legal team.

    Triggered right after Gate 1 — uses ``confirmed_findings`` (NOT
    approved solutions, which don't exist yet).
    """
    confirmed = state.get("confirmed_findings") or []
    if not confirmed:
        return {"department_notifications": [], "meeting_agenda": None}

    payload = json.dumps(
        [
            {
                "finding_id": f["id"],
                "summary": f.get("summary"),
                "severity": f.get("severity"),
                "regulation": f.get("regulation"),
                "responsible_department": f.get("responsible_department"),
                "transcript_quote": f.get("transcript_quote"),
            }
            for f in confirmed
        ],
        indent=2,
    )

    agent = build_notifier()
    user_msg = HumanMessage(
        content=(
            "The legal team has just confirmed the following compliance "
            "findings as real legal issues that need immediate attention. "
            "Your job is to:\n"
            "1. Identify which departments are affected.\n"
            "2. Draft an urgent notification to each affected department.\n"
            "3. Propose a meeting between the legal team and each concerned "
            "department to discuss the issue.\n\n"
            "Follow the workflow in your system prompt and return the JSON "
            "object with `notifications` and `meeting_agenda` keys.\n\n"
            f"CONFIRMED FINDINGS:\n{payload}"
        )
    )
    result = agent.invoke(
        {"messages": [user_msg]},
        config={"recursion_limit": INNER_AGENT_RECURSION_LIMIT},
    )
    parsed = _extract_json(_last_message_content(result))
    _debug("notifier", result, parsed)

    notifications = parsed.get("notifications", []) if isinstance(parsed, dict) else []
    meeting_agenda = parsed.get("meeting_agenda") if isinstance(parsed, dict) else None

    return {
        "department_notifications": notifications,
        "meeting_agenda": meeting_agenda,
    }


# --------------------------------------------------------------------------- #
# Node: Legal Researcher  (runs in parallel with notifier)                    #
# --------------------------------------------------------------------------- #


def _solution_from_raw(raw: Dict[str, Any], index: int) -> Optional[Dict[str, Any]]:
    cited = raw.get("cited_doc_ids") or []
    if not cited:
        return None
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
    """Search company DB for precedents and draft remediation proposals."""
    confirmed = state.get("confirmed_findings") or []
    if not confirmed:
        return {"proposed_solutions": []}

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
    _debug("legal_researcher", result, parsed)

    raw_solutions = parsed.get("solutions", []) if isinstance(parsed, dict) else []
    solutions: List[Dict[str, Any]] = []
    for i, raw in enumerate(raw_solutions, start=1):
        s = _solution_from_raw(raw, i)
        if s is not None:
            solutions.append(s)
    return {"proposed_solutions": solutions}


# --------------------------------------------------------------------------- #
# Node: fan_in  (deterministic merge)                                         #
# --------------------------------------------------------------------------- #


def fan_in_node(state: ComplianceState) -> Dict[str, Any]:
    """No-op node that acts as the join point after parallel branches.

    By the time this runs, both ``notifier`` and ``legal_researcher`` have
    written their outputs into the shared state (``department_notifications``,
    ``meeting_agenda``, ``proposed_solutions``).  Nothing to transform.
    """
    return {}


# --------------------------------------------------------------------------- #
# Graph assembly                                                              #
# --------------------------------------------------------------------------- #


def build_compliance_graph(checkpointer=None):
    """Build and compile the compliance multi-agent graph.

    Topology after Gate 1 forks into two parallel branches:
        fan_out ──► notifier          ──► fan_in
        fan_out ──► legal_researcher  ──► fan_in

    Both branches read ``confirmed_findings`` from the shared state and
    write to disjoint keys.  ``fan_in`` joins them before Gate 2.
    """
    if checkpointer is None:
        checkpointer = MemorySaver()

    builder = StateGraph(ComplianceState)

    # Nodes
    builder.add_node("compliance_analyst", compliance_analyst_node)
    builder.add_node("fan_out", fan_out_node)
    builder.add_node("notifier", notifier_node)
    builder.add_node("legal_researcher", legal_researcher_node)
    builder.add_node("fan_in", fan_in_node)
    builder.add_node("report_generator", report_generator_node)

    # Edges — linear part
    builder.add_edge(START, "compliance_analyst")
    builder.add_edge("compliance_analyst", "fan_out")

    # Edges — parallel fork (fan_out feeds BOTH branches)
    builder.add_edge("fan_out", "notifier")
    builder.add_edge("fan_out", "legal_researcher")

    # Edges — parallel join (both branches feed fan_in)
    builder.add_edge("notifier", "fan_in")
    builder.add_edge("legal_researcher", "fan_in")

    # Edges — linear part (after join)
    builder.add_edge("fan_in", "report_generator")
    builder.add_edge("report_generator", END)

    compiled = builder.compile(
        checkpointer=checkpointer,
        interrupt_before=["fan_out", "fan_in"],
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
