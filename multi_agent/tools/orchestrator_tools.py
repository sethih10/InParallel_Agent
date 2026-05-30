"""Tools used by the Orchestrator agent.

The orchestrator agent uses these tools to:
  1. Fetch meeting details (attendees, decisions, agenda)
  2. Fetch company context and profile
  3. Assess decision types and legal relevance
  4. Determine if legal personnel should have been present
"""

from __future__ import annotations

import json
from typing import Any, Dict, Optional

from langchain_core.tools import tool

from multi_agent.data import meetings
from multi_agent.data.company_context import get_company_profile
from multi_agent.data.decision_categorizer import (
    categorize_decisions,
    determine_legal_requirements,
)


@tool
def get_meeting_details(meeting_id: str) -> str: # TODO: rename to get_meeting_record as per InParallel mcp naming conventions
    """Return high-level details about a meeting (without full decisions/transcript).

    Args:
        meeting_id: The meeting id (e.g. ``meeting-glow-001``).

    Returns:
        A JSON string with meeting metadata: title, date, participants, summary.
    """
    meeting = meetings.get_meeting(meeting_id)
    if not meeting:
        return json.dumps({"error": f"Meeting not found: {meeting_id}"})

    return json.dumps(
        {
            "id": meeting.get("id"),
            "title": meeting.get("title"),
            "date": meeting.get("date"),
            "duration_minutes": meeting.get("duration_minutes"),
            "participants": meeting.get("participants", []),
            "summary": meeting.get("summary"),
        },
        indent=2,
    )


@tool
def get_meeting_decisions(meeting_id: str) -> str: # TODO: rename to list_decisions as per InParallel mcp naming conventions
    """Return all decisions made during the meeting.

    Args:
        meeting_id: The meeting id (e.g. ``meeting-glow-001``).

    Returns:
        A JSON string with the list of decisions for the meeting.
    """
    decisions = meetings.list_decisions(meeting_id)
    return json.dumps(decisions, indent=2)


@tool
def fetch_company_context(company_id: str) -> str:
    """Fetch the company profile, including industry, risk level, and legal requirements.

    Args:
        company_id: The company identifier (e.g. ``org-lumiere``).

    Returns:
        A JSON string with the company profile (name, industry, risk level, 
        key personnel, legal requirements). Returns an error if company not found.
    """
    profile = get_company_profile(company_id)
    if not profile:
        return json.dumps(
            {"error": f"Company profile not found: {company_id}"}
        )

    # Return a simplified version for agent consumption
    return json.dumps(
        {
            "id": profile.get("id"),
            "name": profile.get("name"),
            "industry": profile.get("industry"),
            "risk_level": profile.get("risk_level"),
            "applicable_regulations": profile.get(
                "applicable_regulation_categories"
            ),
            "key_personnel_roles": list(
                profile.get("key_personnel", {}).keys()
            ),
            "legal_requirements": profile.get("legal_requirements", {}),
        },
        indent=2,
    )


@tool
def assess_decision_types(meeting_id: str, company_id: str) -> str:
    """Analyze all decisions in the meeting and categorize them by risk level.

    Uses keyword matching to categorize decisions (e.g., 'product claims',
    'data processing', 'ingredient sourcing') and determine which types of
    expertise are required for each.

    Args:
        meeting_id: The meeting id
        company_id: The company id

    Returns:
        A JSON string with categorized decisions, including risk levels
        and which personnel types should have been involved.
    """
    decisions = meetings.list_decisions(meeting_id)
    if not decisions:
        return json.dumps({"error": f"No decisions found for {meeting_id}"})

    categorized = categorize_decisions(decisions)

    # Group by risk level
    by_risk = {"critical": [], "high": [], "medium": [], "low": []}
    for decision in categorized:
        risk = decision.get("risk_level", "low")
        by_risk[risk].append(decision)

    return json.dumps(
        {
            "total_decisions": len(categorized),
            "by_risk_level": {
                k: len(v) for k, v in by_risk.items() if v
            },
            "categorized_decisions": categorized,
        },
        indent=2,
    )


@tool
def get_lawyer_requirements(
    meeting_id: str, company_id: str
) -> str:
    """Determine whether a lawyer should have been present based on decisions and company profile.

    Combines:
      1. Company risk level and mandatory legal requirements
      2. Decision types and their legal complexity
      3. Applicable regulations for the industry

    Args:
        meeting_id: The meeting id
        company_id: The company id

    Returns:
        A JSON string with:
            - should_have_lawyer: bool
            - lawyer_mandatory_for_company: bool
            - required_personnel: list of roles needed
            - high_risk_decisions: list of decisions requiring legal
            - assessment_reasoning: explanation
    """
    company = get_company_profile(company_id)
    if not company:
        return json.dumps(
            {"error": f"Company profile not found: {company_id}"}
        )

    decisions = meetings.list_decisions(meeting_id)
    if not decisions:
        return json.dumps({"error": f"No decisions found for {meeting_id}"})

    categorized = categorize_decisions(decisions)
    assessment = determine_legal_requirements(company, categorized)

    return json.dumps(
        {
            "should_have_lawyer_present": assessment[
                "should_have_lawyer"
            ],
            "lawyer_is_mandatory_for_company": assessment[
                "lawyer_mandatory"
            ],
            "required_personnel": assessment["relevant_personnel"],
            "reason": assessment["reason"],
            "high_risk_decision_count": len(
                assessment["high_risk_decisions"]
            ),
            "high_risk_decision_categories": [
                d.get("category_name")
                for d in assessment["high_risk_decisions"]
            ],
        },
        indent=2,
    )


__all__ = [
    "get_meeting_details",
    "get_meeting_decisions",
    "fetch_company_context",
    "assess_decision_types",
    "get_lawyer_requirements",
]
