"""Compliance Analyst agent.

A LangGraph ReAct agent that inspects meeting decisions against the EU
regulation policy dictionaries and emits a JSON list of potential findings.
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
from multi_agent.tools import COMPLIANCE_TOOLS


def build_compliance_analyst():
    """Build and return the Compliance Analyst ReAct agent."""
    api_key = require_api_key()
    llm = ChatAnthropic(
        model=ANTHROPIC_MODEL,
        temperature=DEFAULT_TEMPERATURE,
        api_key=api_key,
    )
    return create_react_agent(
        model=llm,
        tools=COMPLIANCE_TOOLS,
        prompt=load_prompt("compliance_analyst"),
    )


__all__ = ["build_compliance_analyst"]
