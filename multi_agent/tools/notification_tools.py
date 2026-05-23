"""Tools used by the Notification & Coordination agent.

The agent uses these tools to identify which internal departments need to be
notified about confirmed compliance issues and to draft per-department
messages plus a cross-functional follow-up meeting agenda.
"""

from __future__ import annotations

import json
from typing import List

from langchain_core.tools import tool

from multi_agent.data import company_database as db


@tool
def list_departments() -> str:
    """Return the company department directory.

    Each entry includes the department id, name, lead, email, and the
    compliance topics it owns. Use this to route notifications.

    Returns:
        A JSON string listing every department.
    """
    return json.dumps(db.list_departments(), indent=2)


@tool
def find_departments_for_topics(topics: List[str]) -> str:
    """Find the departments responsible for the given compliance topics.

    Args:
        topics: A list of topic keywords, e.g.
            ``["GDPR", "international transfers", "marketing claims"]``.

    Returns:
        A JSON string listing matching departments.
    """
    return json.dumps(db.find_departments_for_topics(topics), indent=2)


NOTIFICATION_TOOLS = [
    list_departments,
    find_departments_for_topics,
]


__all__ = ["NOTIFICATION_TOOLS"]
