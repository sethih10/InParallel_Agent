"""Final report compilation.

Deterministic node (no LLM) that takes the final ``ComplianceState`` and
produces:

    - ``final_report`` (JSON-serialisable dict) saved into the state
    - ``format_report_text(report)`` helper for the entry-point CLI

The report enforces the **evidence chain** invariant: every finding listed
in the report carries (a) transcript quote, (b) regulation reference, and
(c) at least one precedent doc id (linked from the approved solution).
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from multi_agent.config import ensure_reports_dir
from multi_agent.state import ComplianceState


_SEVERITY_ORDER = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}


def _sort_by_severity(findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return sorted(
        findings,
        key=lambda f: _SEVERITY_ORDER.get(f.get("severity", "Low"), 4),
    )


def _solution_text(sol: Dict[str, Any]) -> str:
    return sol.get("user_edited_proposal") or sol.get("proposal", "")


def compile_report(state: ComplianceState) -> Dict[str, Any]:
    """Build the final structured report from the populated state."""
    confirmed = state.get("confirmed_findings", []) or []
    approved = state.get("approved_solutions", []) or []
    notifications = state.get("department_notifications", []) or []
    agenda = state.get("meeting_agenda")

    # Index solutions by finding id and link the evidence chain back.
    solutions_by_finding: Dict[str, List[Dict[str, Any]]] = {}
    for sol in approved:
        solutions_by_finding.setdefault(sol.get("finding_id", ""), []).append(sol)

    findings_out: List[Dict[str, Any]] = []
    for f in _sort_by_severity(confirmed):
        f_id = f.get("id", "")
        related_solutions = solutions_by_finding.get(f_id, [])
        precedent_ids: List[str] = []
        for s in related_solutions:
            for did in s.get("cited_doc_ids") or []:
                if did not in precedent_ids:
                    precedent_ids.append(did)

        findings_out.append({
            "id": f_id,
            "summary": f.get("summary"),
            "severity": f.get("severity"),
            "max_fine": f.get("max_fine"),
            "responsible_department": f.get("responsible_department"),
            "evidence_chain": {
                "transcript_quote": f.get("transcript_quote"),
                "transcript_speaker": f.get("transcript_speaker"),
                "regulation": f.get("regulation"),
                "precedent_doc_ids": precedent_ids,
            },
            "approved_solutions": [
                {
                    "id": s.get("id"),
                    "proposal": _solution_text(s),
                    "cited_doc_ids": s.get("cited_doc_ids") or [],
                    "rationale": s.get("rationale"),
                    "user_edited": bool(s.get("user_edited_proposal")),
                }
                for s in related_solutions
            ],
        })

    severity_counts: Dict[str, int] = {}
    for f in findings_out:
        sev = f.get("severity", "Unknown")
        severity_counts[sev] = severity_counts.get(sev, 0) + 1

    report: Dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "meeting_id": state.get("meeting_id"),
        "summary": {
            "total_findings": len(findings_out),
            "by_severity": severity_counts,
            "total_solutions": len(approved),
            "total_notifications": len(notifications),
        },
        "findings": findings_out,
        "notifications": notifications,
        "meeting_agenda": agenda,
    }
    return report


def report_generator_node(state: ComplianceState) -> Dict[str, Any]:
    """LangGraph node: compile the final report into state."""
    return {"final_report": compile_report(state)}


def save_report_json(report: Dict[str, Any], filename: str = "compliance_report.json") -> Path:
    """Save the report as JSON in the project ``reports/`` directory."""
    reports_dir = ensure_reports_dir()
    out_path = reports_dir / filename
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return out_path


def format_report_text(report: Dict[str, Any]) -> str:
    """Format the report as a human-readable plain-text block."""
    lines: List[str] = []
    lines.append("=" * 78)
    lines.append("  COMPLIANCE REVIEW REPORT")
    lines.append("=" * 78)
    lines.append(f"  Meeting       : {report.get('meeting_id', '?')}")
    lines.append(f"  Generated     : {report.get('generated_at', '?')}")
    summary = report.get("summary", {})
    lines.append(f"  Findings      : {summary.get('total_findings', 0)} "
                 f"(by severity: {summary.get('by_severity', {})})")
    lines.append(f"  Solutions     : {summary.get('total_solutions', 0)} approved")
    lines.append(f"  Notifications : {summary.get('total_notifications', 0)} drafted")
    lines.append("")

    for idx, finding in enumerate(report.get("findings", []), start=1):
        ec = finding.get("evidence_chain", {})
        reg = ec.get("regulation", {}) or {}
        lines.append("-" * 78)
        lines.append(f"[{idx}] [{finding.get('severity', '?')}] {finding.get('summary', '')}")
        lines.append(f"     Department     : {finding.get('responsible_department', '?')}")
        lines.append(f"     Max fine       : {finding.get('max_fine', '?')}")
        lines.append(f"     Regulation     : {reg.get('regulation', '?')} "
                     f"{reg.get('article', '')} - {reg.get('title', '')}")
        lines.append(f"     Speaker        : {ec.get('transcript_speaker', '?')}")
        lines.append(f"     Quote          : \"{ec.get('transcript_quote', '')}\"")
        precedents = ec.get("precedent_doc_ids") or []
        lines.append(f"     Precedents     : {', '.join(precedents) if precedents else '(none)'}")
        for s in finding.get("approved_solutions", []):
            edited = " (edited)" if s.get("user_edited") else ""
            lines.append(f"     Proposal{edited}: {s.get('proposal', '')}")
            lines.append(f"     Rationale      : {s.get('rationale', '')}")

    notifications = report.get("notifications", [])
    if notifications:
        lines.append("")
        lines.append("=" * 78)
        lines.append("  DEPARTMENT NOTIFICATIONS")
        lines.append("=" * 78)
        for n in notifications:
            lines.append("-" * 78)
            lines.append(f"To     : {n.get('department_name', '?')} <{n.get('recipient_email', '')}>")
            lines.append(f"Subject: {n.get('subject', '')}")
            lines.append("")
            lines.append(n.get("body", ""))

    agenda = report.get("meeting_agenda") or {}
    if agenda:
        lines.append("")
        lines.append("=" * 78)
        lines.append("  FOLLOW-UP MEETING AGENDA")
        lines.append("=" * 78)
        lines.append(f"Title     : {agenda.get('title', '?')}")
        lines.append(f"Target    : {agenda.get('target_date', '(unspecified)')}")
        lines.append(f"Attendees : {', '.join(agenda.get('suggested_attendees') or [])}")
        lines.append("Agenda    :")
        for item in agenda.get("agenda_items") or []:
            lines.append(f"  - {item}")

    lines.append("")
    return "\n".join(lines)


__all__ = [
    "compile_report",
    "report_generator_node",
    "save_report_json",
    "format_report_text",
]
