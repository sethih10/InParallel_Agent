"""Tools used by the Compliance Analyst agent.

The agent uses these tools to read the meeting, look at decisions, inspect
the transcript, and consult the EU regulation dictionaries.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List

from langchain_core.tools import tool

from multi_agent.data import meetings
from multi_agent.policies import (
    get_regulation,
    list_regulations,
)


@tool
def get_meeting_decisions(meeting_id: str) -> str: # TODO: rename to list_decisions as per InParallel mcp naming conventions
    """Return all decisions made during the given meeting.

    Args:
        meeting_id: The meeting id (e.g. ``meeting-glow-001``).

    Returns:
        A JSON string with the list of decisions for the meeting.
    """
    decisions = meetings.list_decisions(meeting_id)
    return json.dumps(decisions, indent=2)


@tool
def get_transcript_excerpt(meeting_id: str, speaker_or_keyword: str = "") -> str: # TODO: rename to get_transcript as per InParallel mcp naming conventions
    """Return the meeting transcript, optionally filtered.

    Args:
        meeting_id: The meeting id (e.g. ``meeting-glow-001``).
        speaker_or_keyword: Optional. If provided, only utterances containing
            this string (case-insensitive) in either the speaker name or the
            text are returned. Leave empty to return the full transcript.

    Returns:
        A JSON string with the list of utterances.
    """
    transcript = meetings.get_transcript(meeting_id) or []
    if speaker_or_keyword:
        q = speaker_or_keyword.lower()
        transcript = [
            entry for entry in transcript
            if q in entry["speaker"].lower() or q in entry["text"].lower()
        ]
    return json.dumps(transcript, indent=2)


@tool
def lookup_regulation(regulation_id: str) -> str:
    """Return the full text of a single regulation article by its id.

    Args:
        regulation_id: The article id (e.g. ``GDPR-ART9`` or ``EU-COSM-ART10``).

    Returns:
        A JSON string with the regulation article, or an error message.
    """
    reg = get_regulation(regulation_id)
    if reg is None:
        return json.dumps({
            "error": f"Unknown regulation id: {regulation_id}",
            "hint": "Call list_all_regulations to see available ids.",
        })
    return json.dumps(reg, indent=2)


@tool
def list_all_regulations() -> str:
    """Return a compact catalogue of every regulation article in the policy library.

    Each entry includes id, regulation, article, title, severity, and the
    list of violation indicators. Use this catalogue to decide which
    regulations to inspect more closely with ``lookup_regulation``.

    Returns:
        A JSON string with the regulation catalogue.
    """
    catalogue: List[Dict[str, Any]] = []
    for entry in list_regulations():
        catalogue.append({
            "id": entry["id"],
            "regulation": entry["regulation"],
            "article": entry["article"],
            "title": entry["title"],
            "severity": entry["severity"],
            "violation_indicators": entry["violation_indicators"],
        })
    return json.dumps(catalogue, indent=2)


COMPLIANCE_TOOLS = [
    get_meeting_decisions,
    get_transcript_excerpt,
    lookup_regulation,
    list_all_regulations,
]


__all__ = ["COMPLIANCE_TOOLS"]
