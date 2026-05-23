"""LangGraph state definition for the compliance multi-agent system.

The graph passes a single ``ComplianceState`` between every node. Keeping
state in one place (not scattered across closures) makes the dataflow
explicit and easy to inspect.

Fields are populated incrementally:
    - ``meeting_id``           : set by caller
    - ``potential_findings``   : after Compliance Analyst
    - ``confirmed_findings``   : after HITL Gate 1
    - ``proposed_solutions``   : after Legal Research agent
    - ``approved_solutions``   : after HITL Gate 2
    - ``department_notifications`` + ``meeting_agenda`` : after Notifier
    - ``final_report``         : after Report Generator
"""

from __future__ import annotations

from typing import Annotated, Any, Dict, List, Optional, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class ComplianceState(TypedDict, total=False):
    """Shared state object for the compliance multi-agent graph.

    ``total=False`` because nodes only populate the keys they own.
    """

    # Conversation history (used by the LLM-based agent nodes).
    messages: Annotated[List[BaseMessage], add_messages]

    # Input ------------------------------------------------------------
    meeting_id: str

    # Compliance Analyst ----------------------------------------------
    potential_findings: List[Dict[str, Any]]    # list of Finding.to_dict()

    # HITL Gate 1 ------------------------------------------------------
    confirmed_findings: List[Dict[str, Any]]
    gate1_complete: bool

    # Legal Research --------------------------------------------------
    proposed_solutions: List[Dict[str, Any]]    # list of Solution.to_dict()

    # HITL Gate 2 ------------------------------------------------------
    approved_solutions: List[Dict[str, Any]]
    gate2_complete: bool

    # Notifier --------------------------------------------------------
    department_notifications: List[Dict[str, Any]]
    meeting_agenda: Optional[Dict[str, Any]]

    # Final ------------------------------------------------------------
    final_report: Dict[str, Any]


__all__ = ["ComplianceState"]
