"""Tools used by the Legal Research agent.

The agent uses these tools to search the company's historical knowledge base
(past cases, internal policies, legal opinions) for precedents that inform
remediation. Every solution drafted by the agent MUST cite at least one
document id returned by these tools.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List

from langchain_core.tools import tool

from multi_agent.data import company_database as db


@tool
def search_past_cases(query: str) -> str:
    """Search the company's past compliance cases.

    Args:
        query: A free-text search string. Matches against the case title,
            summary, tags and regulation ids (case-insensitive).

    Returns:
        A JSON string listing matching cases. Each case includes the
        resolution notes describing how the company handled the issue.
    """
    return json.dumps(db.search_past_cases(query), indent=2)


@tool
def search_internal_policies(query: str) -> str:
    """Search the company's internal policies and SOPs.

    Args:
        query: A free-text search string.

    Returns:
        A JSON string listing matching policies.
    """
    return json.dumps(db.search_internal_policies(query), indent=2)


@tool
def search_legal_opinions(query: str) -> str:
    """Search external legal opinions held by the company.

    Args:
        query: A free-text search string.

    Returns:
        A JSON string listing matching legal opinions, including the
        recommended actions from external counsel.
    """
    return json.dumps(db.search_legal_opinions(query), indent=2)


@tool
def get_document_by_id(doc_id: str) -> str:
    """Fetch a single document (case, policy, or legal opinion) by its id.

    Args:
        doc_id: The document id, e.g. ``case-2024-001``, ``POL-DPO-001``,
            ``opinion-2024-001``.

    Returns:
        A JSON string with the full document, or an error message.
    """
    doc = db.get_document_by_id(doc_id)
    if doc is None:
        return json.dumps({"error": f"Unknown document id: {doc_id}"})
    return json.dumps(doc, indent=2)


LEGAL_TOOLS = [
    search_past_cases,
    search_internal_policies,
    search_legal_opinions,
    get_document_by_id,
]


__all__ = ["LEGAL_TOOLS"]
