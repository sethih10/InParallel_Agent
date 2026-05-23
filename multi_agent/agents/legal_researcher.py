"""Legal Research agent.

A LangGraph ReAct agent that searches the company's historical knowledge
base for precedents and drafts evidence-backed remediation proposals.
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
from multi_agent.tools import LEGAL_TOOLS


def build_legal_researcher():
    """Build and return the Legal Research ReAct agent."""
    api_key = require_api_key()
    llm = ChatAnthropic(
        model=ANTHROPIC_MODEL,
        temperature=DEFAULT_TEMPERATURE,
        api_key=api_key,
    )
    return create_react_agent(
        model=llm,
        tools=LEGAL_TOOLS,
        prompt=load_prompt("legal_researcher"),
    )


__all__ = ["build_legal_researcher"]
