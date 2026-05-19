"""
Compliance rules for InParallel workspace data.

Each rule is a small, transparent function that takes already-fetched MCP
data and returns a list of ``Finding`` objects. Rules are intentionally
pure-Python and side-effect free so they are easy to read, unit test,
and extend.

Severity convention:
    - "high":   policy violation that should block a release / report.
    - "medium": violation that should be fixed but is not blocking.
    - "low":    informational / hygiene issue.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any


# --------------------------------------------------------------------------- #
# Data model                                                                  #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class Finding:
    """A single rule violation."""

    rule_id: str
    severity: str  # "high" | "medium" | "low"
    message: str
    context: dict[str, Any] = field(default_factory=dict)


# --------------------------------------------------------------------------- #
# Sensitive-data patterns                                                     #
# --------------------------------------------------------------------------- #
# Compiled once at import time. Keep these conservative; false positives are
# preferable to silently missing a leaked secret.

_SENSITIVE_PATTERNS: dict[str, re.Pattern[str]] = {
    "aws_access_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "generic_api_key": re.compile(r"(?i)\bapi[_-]?key\s*[:=]\s*[\"']?[A-Za-z0-9_\-]{16,}"),
    "password_assignment": re.compile(r"(?i)\bpassword\s*[:=]\s*[\"'][^\"']{4,}"),
    "bearer_token": re.compile(r"(?i)\bbearer\s+[A-Za-z0-9_\-\.]{20,}"),
    "ssn_like": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "private_key_header": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
}


# --------------------------------------------------------------------------- #
# Helpers                                                                     #
# --------------------------------------------------------------------------- #


def _parse_date(value: Any) -> date | None:
    if not value or not isinstance(value, str):
        return None
    # Accept "YYYY-MM-DD" or ISO datetimes.
    try:
        return date.fromisoformat(value[:10])
    except ValueError:
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
        except ValueError:
            return None


# --------------------------------------------------------------------------- #
# Rule: action-item governance                                                #
# --------------------------------------------------------------------------- #


def check_action_items(
    action_items: list[dict[str, Any]],
    *,
    today: date | None = None,
) -> list[Finding]:
    """Validate action-item hygiene.

    Required fields:
        - ``owner_email``: someone must own the task.
        - ``due_date``:    every task needs a target date.
        - ``source_meeting_id``: tasks must trace back to a meeting
          (README §7.9: "Every action item should trace back to a source
          meeting").

    Additionally, an item that is past due and not in ``done`` / ``cancelled``
    / ``archived`` is flagged as overdue.
    """
    today = today or date.today()
    findings: list[Finding] = []

    closed_statuses = {"done", "cancelled", "archived"}

    for item in action_items:
        item_id = item.get("id", "<unknown>")
        title = item.get("title", "<untitled>")
        status = item.get("status", "")
        ctx = {"action_item_id": item_id, "title": title, "status": status}

        if not item.get("owner_email"):
            findings.append(
                Finding(
                    rule_id="action_item.missing_owner",
                    severity="high",
                    message=f"Action item '{title}' has no owner_email.",
                    context=ctx,
                )
            )

        if not item.get("due_date"):
            findings.append(
                Finding(
                    rule_id="action_item.missing_due_date",
                    severity="medium",
                    message=f"Action item '{title}' has no due_date.",
                    context=ctx,
                )
            )

        if not item.get("source_meeting_id"):
            findings.append(
                Finding(
                    rule_id="action_item.missing_source_meeting",
                    severity="high",
                    message=f"Action item '{title}' is not linked to a source meeting.",
                    context=ctx,
                )
            )

        due = _parse_date(item.get("due_date"))
        if due and due < today and status not in closed_statuses:
            findings.append(
                Finding(
                    rule_id="action_item.overdue",
                    severity="high",
                    message=(
                        f"Action item '{title}' was due {due.isoformat()} "
                        f"and is still '{status or 'unset'}'."
                    ),
                    context={**ctx, "due_date": due.isoformat()},
                )
            )

    return findings


# --------------------------------------------------------------------------- #
# Rule: decision audit trail                                                  #
# --------------------------------------------------------------------------- #


def check_decisions(decisions: list[dict[str, Any]]) -> list[Finding]:
    """Validate that finalized decisions carry an audit trail.

    For any decision in status ``approved`` or ``rejected``:
        - must have an ``owner`` (or ``owner_email``);
        - must have a ``rationale`` (or non-empty ``context`` / ``summary``);
        - must link to a ``source_meeting_id``.
    """
    findings: list[Finding] = []
    finalized = {"approved", "rejected"}

    for d in decisions:
        status = (d.get("status") or "").lower()
        if status not in finalized:
            continue

        title = d.get("title", "<untitled>")
        d_id = d.get("id", "<unknown>")
        ctx = {"decision_id": d_id, "title": title, "status": status}

        if not (d.get("owner") or d.get("owner_email")):
            findings.append(
                Finding(
                    rule_id="decision.missing_owner",
                    severity="high",
                    message=f"Decision '{title}' is {status} but has no owner.",
                    context=ctx,
                )
            )

        rationale = d.get("rationale") or d.get("context") or d.get("summary")
        if not rationale:
            findings.append(
                Finding(
                    rule_id="decision.missing_rationale",
                    severity="medium",
                    message=f"Decision '{title}' is {status} but has no rationale.",
                    context=ctx,
                )
            )

        if not d.get("source_meeting_id"):
            findings.append(
                Finding(
                    rule_id="decision.missing_source_meeting",
                    severity="high",
                    message=f"Decision '{title}' has no source meeting.",
                    context=ctx,
                )
            )

    return findings


# --------------------------------------------------------------------------- #
# Rule: sensitive data scan                                                   #
# --------------------------------------------------------------------------- #


def scan_text(text: str) -> list[tuple[str, str]]:
    """Return a list of ``(pattern_name, matched_excerpt)`` hits in ``text``."""
    if not text:
        return []
    hits: list[tuple[str, str]] = []
    for name, pattern in _SENSITIVE_PATTERNS.items():
        for match in pattern.finditer(text):
            excerpt = match.group(0)
            # Truncate long matches so reports stay readable.
            if len(excerpt) > 80:
                excerpt = excerpt[:77] + "..."
            hits.append((name, excerpt))
    return hits


def check_sensitive_data(
    documents: list[dict[str, Any]],
) -> list[Finding]:
    """Scan a list of ``{source, text}`` documents for sensitive patterns.

    ``source`` is a free-form label (e.g. ``"meeting:<id>:summary"``) that
    is echoed back in the finding context so reviewers can locate the hit.
    """
    findings: list[Finding] = []
    for doc in documents:
        source = doc.get("source", "<unknown>")
        text = doc.get("text") or ""
        for pattern_name, excerpt in scan_text(text):
            findings.append(
                Finding(
                    rule_id=f"sensitive_data.{pattern_name}",
                    severity="high" if pattern_name != "ssn_like" else "medium",
                    message=f"Possible {pattern_name} in {source}: {excerpt!r}",
                    context={"source": source, "pattern": pattern_name},
                )
            )
    return findings
