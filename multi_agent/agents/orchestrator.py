"""Orchestrator agent.

A LangGraph ReAct agent that inspects a meeting within the company's
organizational and regulatory context. The orchestrator assesses:

  1. Meeting context: what was discussed, who participated
  2. Company context: industry, risk level, applicable regulations
  3. Decision types: which decisions require legal expertise
  4. Lawyer presence: was a lawyer present? should one have been?

The orchestrator produces a meeting summary and assessment of compliance risks
"""

from __future__ import annotations

from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent

from multi_agent.config import (
    ANTHROPIC_MODEL,
    DEFAULT_TEMPERATURE,
    require_api_key,
)
from multi_agent.prompts import load_prompt
from multi_agent.tools.orchestrator_tools import (
    assess_decision_types,
    fetch_company_context,
    get_lawyer_requirements,
    get_meeting_details,
    get_meeting_decisions,
)


ORCHESTRATOR_TOOLS = [
    get_meeting_details,
    get_meeting_decisions,
    fetch_company_context,
    assess_decision_types,
    get_lawyer_requirements,
]


def build_orchestrator():
    """Build and return the Orchestrator ReAct agent."""
    api_key = require_api_key()
    llm = ChatAnthropic(
        model=ANTHROPIC_MODEL,
        temperature=DEFAULT_TEMPERATURE,
        api_key=api_key,
    )
    return create_react_agent(
        model=llm,
        tools=ORCHESTRATOR_TOOLS,
        prompt=load_prompt("orchestrator"),
    )


__all__ = ["build_orchestrator"]
