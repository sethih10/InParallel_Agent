"""MCP-style tool implementations for meeting compliance data."""

import json
from datetime import datetime

from meeting_data import (
    action_items,
    company_context,
    decisions,
    execution_plan,
    meeting_records,
    organizations,
    plan_versions,
    transcripts,
)

# In-memory log of sent emails (for demo/testing purposes)
sent_emails_log: list[dict] = []


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


def get_company_context():
    """Get the company context including applicable regulations, internal policies, and key contacts."""
    return company_context


def get_meeting_initiator(meeting_id):
    """Get the initiator (name and email) of a meeting by meeting ID."""
    for record in meeting_records:
        if record["id"] == meeting_id:
            return record.get("initiated_by")
    raise ValueError(f"Meeting record not found: {meeting_id}")


def send_compliance_report_email(recipient_email, recipient_name, meeting_id, subject, body):
    """Send a compliance report email to the specified recipient.

    In production this would integrate with an SMTP server or email API.
    For this demo it logs the email and returns a confirmation.
    """
    email_record = {
        "id": f"email-{len(sent_emails_log) + 1:03d}",
        "timestamp": datetime.now().isoformat(),
        "to": recipient_email,
        "to_name": recipient_name,
        "meeting_id": meeting_id,
        "subject": subject,
        "body": body,
    }
    sent_emails_log.append(email_record)
    print(f"\n{'='*60}")
    print(f"EMAIL SENT (simulated)")
    print(f"{'='*60}")
    print(f"To:      {recipient_name} <{recipient_email}>")
    print(f"Subject: {subject}")
    print(f"Date:    {email_record['timestamp']}")
    print(f"{'-'*60}")
    print(body)
    print(f"{'='*60}\n")
    return {
        "status": "sent",
        "email_id": email_record["id"],
        "to": recipient_email,
        "subject": subject,
    }
