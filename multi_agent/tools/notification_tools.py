"""Tools used by the Notification & Coordination agent.

The agent uses these tools to:
1. Identify which internal departments need to be notified
2. Draft per-department messages and follow-up agendas
3. Send notifications via MCP tools (Slack and email)
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from langchain_core.tools import tool

from multi_agent.data import company_database as db
from multi_agent.mcp.server import send_slack_message, send_email


@tool
def list_departments() -> str: # InParallel has MCP tool named list_organizations
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


@tool
def send_slack_notification(
    channel: str,
    subject: str,
    message: str,
) -> str:
    """Send a notification message to a Slack channel via MCP.

    Use this to send compliance notifications to teams. The channel should
    be a Slack channel name (e.g., "#compliance" or "compliance-team").

    Args:
        channel: Slack channel name (with or without #)
        subject: Brief subject line
        message: Detailed message body (supports Markdown)

    Returns:
        A JSON string with the result (success/failure).
    """
    # Ensure channel starts with #
    if not channel.startswith("#"):
        channel = f"#{channel}"

    result = send_slack_message(channel, subject, message)
    return json.dumps(result, indent=2)


@tool
def send_email_notification(
    recipient: Optional[str],
    subject: str,
    message: str,
) -> str:
    """Send a notification email via MCP.

    Use this to send compliance notifications via email. If recipient is
    omitted, the default compliance team email is used.

    Args:
        recipient: Email address (optional; uses default if omitted)
        subject: Email subject line
        message: Email body (supports HTML and plain text)

    Returns:
        A JSON string with the result (success/failure).
    """
    result = send_email(recipient, subject, message)
    return json.dumps(result, indent=2)


NOTIFICATION_TOOLS = [
    list_departments,
    find_departments_for_topics,
    send_slack_notification,
    send_email_notification,
]


__all__ = ["NOTIFICATION_TOOLS"]
