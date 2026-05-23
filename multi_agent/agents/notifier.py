"""Notification & Coordination agent.

A LangGraph ReAct agent that routes approved compliance solutions to the
right internal departments and drafts a cross-functional follow-up meeting
agenda.
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
from multi_agent.tools import NOTIFICATION_TOOLS


def build_notifier():
    """Build and return the Notification & Coordination ReAct agent."""
    api_key = require_api_key()
    llm = ChatAnthropic(
        model=ANTHROPIC_MODEL,
        temperature=DEFAULT_TEMPERATURE,
        api_key=api_key,
    )
    return create_react_agent(
        model=llm,
        tools=NOTIFICATION_TOOLS,
        prompt=load_prompt("notifier"),
    )


__all__ = ["build_notifier"]
