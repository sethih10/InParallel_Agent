"""LangChain-based multi-agent compliance checker.

Architecture
------------
1. **Compliance Issue Detector** (orchestrator agent)
   - Reads meeting data (records, transcripts, decisions, action items).
   - Determines whether the meeting content raises potential compliance concerns.
   - When issues are detected it delegates to the Legal Compliance Checker.
   - After receiving the legal analysis it emails the report to the meeting
     initiator instead of just printing it.

2. **Legal Compliance Checker** (specialist sub-agent)
   - Receives the meeting transcript and company context.
   - Evaluates the transcript against applicable laws (GDPR, ePrivacy, Finnish
     Data Protection Act) and internal company policies.
   - Returns a structured legal compliance assessment.

Both agents use Anthropic Claude Sonnet 4 via LangChain.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict

from dotenv import load_dotenv
load_dotenv()

try:
    from langchain.tools import tool
    from langchain.chat_models import init_chat_model
    from langchain.agents import create_agent
    from langchain_core.messages import HumanMessage
    LANGCHAIN_AVAILABLE = True
except Exception:
    LANGCHAIN_AVAILABLE = False

from compliance_tools import (
    get_action_item,
    get_company_context,
    get_decision,
    get_execution_plan,
    get_meeting_initiator,
    get_meeting_record,
    get_plan_versions,
    get_transcript,
    list_action_items,
    list_decisions,
    list_meeting_records,
    list_organizations,
    send_compliance_report_email,
)

# ---------------------------------------------------------------------------
# API key helpers
# ---------------------------------------------------------------------------

def load_anthropic_api_key():
    """Load Anthropic API key from environment or setup.md for demo purposes."""
    key = os.environ.get("ANTHROPIC_API_KEY")
    if key:
        return key

    setup_file = Path(__file__).resolve().parent / "setup.md"
    if not setup_file.exists():
        return None

    for line in setup_file.read_text(encoding="utf-8").splitlines():
        if "API_KEY" in line and "=" in line:
            candidate = line.split("=", 1)[1].strip()
            if candidate:
                os.environ["ANTHROPIC_API_KEY"] = candidate
                return candidate

    return None


def _get_llm():
    """Return a configured LLM instance."""
    load_anthropic_api_key()
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise RuntimeError(
            "Missing Anthropic API key. Set ANTHROPIC_API_KEY in the environment "
            "or add an API_KEY line to setup.md."
        )
    try:
        return init_chat_model(
            "anthropic:claude-sonnet-4-20250514",
            anthropic_api_key=os.environ["ANTHROPIC_API_KEY"],
        )
    except ImportError as exc:
        raise RuntimeError(
            "The langchain-anthropic package is required for Anthropic models. "
            "Install it with `pip install langchain-anthropic`."
        ) from exc

# ---------------------------------------------------------------------------
# Agent 2 – Legal Compliance Checker (specialist)
# ---------------------------------------------------------------------------

def _create_legal_checker_tools():
    """Tools available to the legal compliance checker sub-agent."""
    return [
        tool("get_transcript", description="Get the meeting transcript by meeting id.")(get_transcript),
        tool("get_company_context", description="Get company context: applicable regulations, internal policies, and key contacts.")(get_company_context),
        tool("get_decision", description="Get a single decision by id.")(get_decision),
        tool("list_decisions", description="List all decisions.")(list_decisions),
    ]


def build_legal_checker_agent():
    """Build the Legal Compliance Checker sub-agent."""
    if not LANGCHAIN_AVAILABLE:
        raise RuntimeError("LangChain not available")

    llm = _get_llm()
    tools = _create_legal_checker_tools()
    agent = create_agent(
        llm,
        tools,
        system_prompt=(
            "You are a Legal Compliance Checker specialising in EU data protection law. "
            "Your job is to analyse a meeting transcript against applicable laws and "
            "company policies.\n\n"
            "WORKFLOW:\n"
            "1. Use get_company_context to load the company's applicable regulations "
            "   and internal policies.\n"
            "2. Use get_transcript to retrieve the meeting transcript.\n"
            "3. Use list_decisions / get_decision if you need more context on what was decided.\n"
            "4. Evaluate every statement and decision in the transcript against:\n"
            "   - GDPR requirements (lawful basis, data minimisation, DPIAs, international "
            "     transfers, special category data, etc.)\n"
            "   - ePrivacy Directive requirements\n"
            "   - Finnish Data Protection Act requirements\n"
            "   - The company's internal policies\n"
            "5. Return a structured report with:\n"
            "   - A list of compliance issues found (each with severity: HIGH / MEDIUM / LOW)\n"
            "   - The specific law or policy violated\n"
            "   - Recommended remediation actions\n"
            "   - An overall compliance risk rating (CRITICAL / HIGH / MEDIUM / LOW)\n\n"
            "Be thorough and cite the specific regulation articles where relevant."
        ),
        debug=False,
    )
    return agent


def run_legal_compliance_check(meeting_id: str) -> str:
    """Invoke the Legal Compliance Checker agent for a given meeting."""
    agent = build_legal_checker_agent()
    prompt = (
        f"Analyse meeting {meeting_id} for legal compliance issues. "
        "Retrieve the company context and meeting transcript, then produce "
        "a detailed compliance assessment."
    )
    response = agent.invoke({"messages": [HumanMessage(content=prompt)]})
    return response["messages"][-1].content

# ---------------------------------------------------------------------------
# Agent 1 – Compliance Issue Detector (orchestrator)
# ---------------------------------------------------------------------------

def _create_detector_tools():
    """Tools available to the Compliance Issue Detector (orchestrator)."""

    @tool("run_legal_compliance_check",
          description=(
              "Delegate to the Legal Compliance Checker agent. "
              "Pass a meeting_id (e.g. 'meeting-001'). Returns a detailed "
              "legal compliance report for that meeting."
          ))
    def _run_legal_check(meeting_id: str) -> str:
        return run_legal_compliance_check(meeting_id)

    return [
        tool("list_meeting_records", description="List all meeting records.")(list_meeting_records),
        tool("get_meeting_record", description="Get a meeting record by id.")(get_meeting_record),
        tool("get_transcript", description="Get the meeting transcript by meeting id.")(get_transcript),
        tool("list_decisions", description="List decisions.")(list_decisions),
        tool("list_action_items", description="List action items.")(list_action_items),
        tool("get_action_item", description="Get an action item by id.")(get_action_item),
        tool("get_execution_plan", description="Get the execution plan.")(get_execution_plan),
        tool("get_plan_versions", description="Get plan version history.")(get_plan_versions),
        tool("list_organizations", description="List organizations.")(list_organizations),
        tool("get_company_context", description="Get company context: applicable regulations, internal policies, and key contacts.")(get_company_context),
        tool("get_meeting_initiator", description="Get the name and email of the person who initiated a meeting.")(get_meeting_initiator),
        tool("send_compliance_report_email", description=(
            "Send an email with the compliance report. Parameters: "
            "recipient_email (str), recipient_name (str), meeting_id (str), "
            "subject (str), body (str)."
        ))(send_compliance_report_email),
        _run_legal_check,
    ]


def build_compliance_detector_agent():
    """Build the Compliance Issue Detector (orchestrator) agent."""
    if not LANGCHAIN_AVAILABLE:
        raise RuntimeError("LangChain not available")

    llm = _get_llm()
    tools = _create_detector_tools()
    agent = create_agent(
        llm,
        tools,
        system_prompt=(
            "You are a Compliance Issue Detector – the orchestrating agent in a "
            "multi-agent compliance review system.\n\n"
            "WORKFLOW:\n"
            "1. Retrieve the meeting record and its transcript.\n"
            "2. Quickly scan the transcript for topics that could raise compliance "
            "   concerns (personal data collection, data sharing, international "
            "   transfers, sensitive data, legal obligations, etc.).\n"
            "3. If potential compliance issues are found, call the "
            "   run_legal_compliance_check tool with the meeting id. This delegates "
            "   to a specialist Legal Compliance Checker agent that will analyse the "
            "   transcript against GDPR, ePrivacy, Finnish law, and company policies.\n"
            "4. Once you receive the legal compliance report, use "
            "   get_meeting_initiator to find who initiated the meeting.\n"
            "5. Compose a clear, professional compliance report email and use "
            "   send_compliance_report_email to deliver it to the meeting initiator.\n"
            "6. Summarise what you did and confirm the email was sent.\n\n"
            "IMPORTANT:\n"
            "- Do NOT just print the analysis – always send it via email.\n"
            "- If no compliance issues are detected, still send a brief confirmation "
            "  email to the initiator stating that no issues were found.\n"
            "- Use the company context tool if you need to reference internal "
            "  policies or regulation details."
        ),
        debug=False,
    )
    return agent

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def run_query_with_agent(prompt: str, meeting_id: str = None) -> Dict[str, Any]:
    """Run the multi-agent compliance review.

    The Compliance Issue Detector agent orchestrates the process:
    it inspects the meeting, delegates legal analysis to the Legal
    Compliance Checker, and emails the result to the meeting initiator.
    """
    if not LANGCHAIN_AVAILABLE:
        raise RuntimeError("LangChain is not available. Install langchain first.")

    agent = build_compliance_detector_agent()
    if meeting_id:
        prompt = f"{prompt}\nMeeting ID: {meeting_id}"

    response = agent.invoke({"messages": [HumanMessage(content=prompt)]})
    final_message = response["messages"][-1].content
    return {"agent_response": final_message}
