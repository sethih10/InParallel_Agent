"""LangChain-based agent wrapper for the compliance checker.

This module creates a LangChain Agent that exposes the MCP-style functions as
tools. It requires `langchain` and Anthropic Claude Sonnet 4.5 to be installed
and configured; no rule-based fallback is provided.

The integration reads `ANTHROPIC_API_KEY` from the environment or `setup.md`.
"""

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
    list_meeting_records,
    get_meeting_record,
    get_transcript,
    list_decisions,
    get_decision,
    list_action_items,
    get_action_item,
    get_execution_plan,
    get_plan_versions,
    list_organizations,
)


def create_langchain_tools():
    """Wrap the MCP-style functions as LangChain Tool objects."""
    if not LANGCHAIN_AVAILABLE:
        raise RuntimeError("LangChain not available")

    tools = [
        tool("list_meeting_records", description="List meeting records.")(list_meeting_records),
        tool("get_meeting_record", description="Get a meeting record by id.")(get_meeting_record),
        tool("get_transcript", description="Get a transcript by meeting id.")(get_transcript),
        tool("list_decisions", description="List decisions.")(list_decisions),
        tool("get_decision", description="Get a decision by id.")(get_decision),
        tool("list_action_items", description="List action items.")(list_action_items),
        tool("get_action_item", description="Get an action item by id.")(get_action_item),
        tool("get_execution_plan", description="Get the current execution plan.")(get_execution_plan),
        tool("get_plan_versions", description="Get plan version history.")(get_plan_versions),
        tool("list_organizations", description="List organizations.")(list_organizations),
    ]
    return tools


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


def build_agent_for_demo():
    """Build and return a LangChain agent for demo purposes.

    This uses Anthropic Claude Sonnet 4.5 and the simulated MCP-style tools
    defined in `compliance_tools.py`.
    """
    if not LANGCHAIN_AVAILABLE:
        raise RuntimeError("LangChain not available")

    load_anthropic_api_key()
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise RuntimeError(
            "Missing Anthropic API key. Set ANTHROPIC_API_KEY in the environment "
            "or add an API_KEY line to setup.md."
        )

    try:
        llm = init_chat_model(
            "anthropic:claude-sonnet-4-20250514",
            anthropic_api_key=os.environ["ANTHROPIC_API_KEY"],
        )
    except ImportError as exc:
        raise RuntimeError(
            "The langchain-anthropic package is required for Anthropic models. "
            "Install it with `pip install langchain-anthropic`."
        ) from exc

    tools = create_langchain_tools()
    agent = create_agent(
        llm,
        tools,
        system_prompt=(
            "You are a compliance assessment assistant. Use only the available tools "
            "to inspect meeting records, transcripts, decisions, action items, and "
            "execution plans. Provide a compliance summary with flags and recommendations."
        ),
        debug=False,
    )
    return agent


def run_query_with_agent(prompt: str, meeting_id: str = None) -> Dict[str, Any]:
    """Run a query via the LangChain/Anthropic agent.

    This function requires the Anthropic-backed LangChain agent to be
    installed and configured; it no longer falls back to a rule-based agent.
    """
    if not LANGCHAIN_AVAILABLE:
        raise RuntimeError("LangChain is not available. Install langchain first.")

    agent = build_agent_for_demo()
    if meeting_id:
        prompt = f"{prompt}\nMeeting ID: {meeting_id}"

    response = agent.invoke({"messages": [HumanMessage(content=prompt)]})
    final_message = response["messages"][-1].content
    return {"agent_response": final_message}
