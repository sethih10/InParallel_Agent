"""MCP-style tool implementations for meeting compliance data."""

from meeting_data import (
    action_items,
    decisions,
    execution_plan,
    meeting_records,
    organizations,
    plan_versions,
    transcripts,
)


def list_meeting_records():
    """List all available meeting records."""
    return [
        {
            "id": record["id"],
            "title": record["title"],
            "date": record["date"],
            "organization_id": record["organization_id"],
        }
        for record in meeting_records
    ]


def get_meeting_record(meeting_id):
    """Get a single meeting record by ID."""
    for record in meeting_records:
        if record["id"] == meeting_id:
            return record
    raise ValueError(f"Meeting record not found: {meeting_id}")


def get_transcript(meeting_id):
    """Get the transcript for a meeting."""
    if meeting_id in transcripts:
        return transcripts[meeting_id]
    raise ValueError(f"Transcript not found for meeting: {meeting_id}")


def list_decisions():
    """List all decisions made in meetings."""
    return decisions


def get_decision(decision_id):
    """Get a single decision and its context."""
    for decision in decisions:
        if decision["id"] == decision_id:
            return decision
    raise ValueError(f"Decision not found: {decision_id}")


def list_action_items():
    """List all agreed action items."""
    return action_items


def get_action_item(action_item_id):
    """Get a single action item by ID."""
    for item in action_items:
        if item["id"] == action_item_id:
            return item
    raise ValueError(f"Action item not found: {action_item_id}")


def get_execution_plan():
    """Get the current execution plan."""
    return execution_plan


def get_plan_versions():
    """Get the version history of the execution plan."""
    return plan_versions


def list_organizations():
    """List organisations associated with meetings."""
    return organizations
