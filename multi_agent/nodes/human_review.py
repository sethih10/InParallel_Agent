"""Helpers for the two human-in-the-loop gates.

The actual *interrupt* is configured on the graph (``interrupt_before=...``);
this module provides the small helper functions the entry-point CLI uses to:

    - render the pending findings / solutions to the terminal
    - collect the user's accept / reject / edit choices
    - merge those choices back into the LangGraph state

Keeping the I/O logic here (and out of ``graph.py``) means the graph file
stays purely structural and is easy to skim.
"""

from __future__ import annotations

import sys
from typing import Any, Dict, List


# --------------------------------------------------------------------------- #
# Gate 1: Confirm findings                                                    #
# --------------------------------------------------------------------------- #

_SEVERITY_ORDER = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}


def _sort_by_severity(findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return sorted(
        findings,
        key=lambda f: _SEVERITY_ORDER.get(f.get("severity", "Low"), 4),
    )


def render_findings_for_review(findings: List[Dict[str, Any]]) -> str:
    """Pretty-print findings (sorted Critical -> Low) for the legal team."""
    lines: List[str] = []
    lines.append("\n" + "=" * 78)
    lines.append("  GATE 1 - LEGAL REVIEW: confirm which findings are real legal issues")
    lines.append("=" * 78)

    for idx, finding in enumerate(_sort_by_severity(findings), start=1):
        reg = finding.get("regulation", {})
        lines.append(f"\n[{idx}] {finding.get('summary', '<no summary>')}")
        lines.append(f"    Severity      : {finding.get('severity', '?')}")
        lines.append(f"    Max fine      : {finding.get('max_fine', '?')}")
        lines.append(f"    Regulation    : {reg.get('regulation', '?')} - "
                     f"{reg.get('article', '?')}: {reg.get('title', '?')}")
        lines.append(f"    Department    : {finding.get('responsible_department', '?')}")
        lines.append(f"    Speaker       : {finding.get('transcript_speaker', '?')}")
        lines.append(f"    Quote         : \"{finding.get('transcript_quote', '')}\"")
        lines.append(f"    Decision id   : {finding.get('decision_id', '?')}")
        lines.append(f"    Finding id    : {finding.get('id', '?')}")

    lines.append("\n" + "-" * 78)
    return "\n".join(lines)


def collect_finding_confirmations(
    findings: List[Dict[str, Any]],
    *,
    input_stream=None,
    output_stream=None,
) -> List[Dict[str, Any]]:
    """Prompt the user [y/n] per finding, return only the confirmed ones.

    Args:
        findings: list of finding dicts (each must carry ``id``).
        input_stream: defaults to ``sys.stdin`` (overridable for testing).
        output_stream: defaults to ``sys.stdout``.

    Returns:
        The list of findings the user confirmed (with ``confirmed=True``).
    """
    if input_stream is None:
        input_stream = sys.stdin
    if output_stream is None:
        output_stream = sys.stdout

    confirmed: List[Dict[str, Any]] = []
    sorted_findings = _sort_by_severity(findings)

    for idx, finding in enumerate(sorted_findings, start=1):
        prompt = (
            f"\n[{idx}/{len(sorted_findings)}] Confirm finding "
            f"{finding.get('id')} ({finding.get('severity', '?')}: "
            f"{finding.get('summary', '')[:70]}) [y/N]: "
        )
        output_stream.write(prompt)
        output_stream.flush()
        answer = (input_stream.readline() or "").strip().lower()
        if answer in ("y", "yes"):
            finding_copy = dict(finding)
            finding_copy["confirmed"] = True
            confirmed.append(finding_copy)

    return confirmed


# --------------------------------------------------------------------------- #
# Gate 2: Approve solutions                                                   #
# --------------------------------------------------------------------------- #


def render_solutions_for_review(
    solutions: List[Dict[str, Any]],
    findings_by_id: Dict[str, Dict[str, Any]],
) -> str:
    """Pretty-print proposed solutions with full evidence chain."""
    lines: List[str] = []
    lines.append("\n" + "=" * 78)
    lines.append("  GATE 2 - LEGAL APPROVAL: approve / edit / reject each solution")
    lines.append("=" * 78)

    for idx, sol in enumerate(solutions, start=1):
        finding = findings_by_id.get(sol.get("finding_id", ""), {})
        reg = finding.get("regulation", {})
        lines.append(f"\n[{idx}] Solution {sol.get('id', '?')} -> Finding {sol.get('finding_id', '?')}")
        lines.append(f"    Issue       : {finding.get('summary', '?')}")
        lines.append(f"    Regulation  : {reg.get('regulation', '?')} {reg.get('article', '')}")
        lines.append(f"    Severity    : {finding.get('severity', '?')}")
        lines.append(f"    Proposal    : {sol.get('proposal', '')}")
        lines.append(f"    Cited docs  : {', '.join(sol.get('cited_doc_ids') or []) or '(none)'}")
        lines.append(f"    Rationale   : {sol.get('rationale', '')}")

    lines.append("\n" + "-" * 78)
    return "\n".join(lines)


def collect_solution_approvals(
    solutions: List[Dict[str, Any]],
    *,
    input_stream=None,
    output_stream=None,
) -> List[Dict[str, Any]]:
    """Prompt the user [a/e/r] per solution; return updated list.

    Approved solutions have ``approved=True``. Edited solutions store the
    user's replacement text in ``user_edited_proposal``. Rejected solutions
    are dropped from the returned list.
    """
    if input_stream is None:
        input_stream = sys.stdin
    if output_stream is None:
        output_stream = sys.stdout

    out: List[Dict[str, Any]] = []
    for idx, sol in enumerate(solutions, start=1):
        prompt = (
            f"\n[{idx}/{len(solutions)}] Solution {sol.get('id')} "
            f"-> [a]pprove / [e]dit / [r]eject (default reject): "
        )
        output_stream.write(prompt)
        output_stream.flush()
        answer = (input_stream.readline() or "").strip().lower()

        if answer in ("a", "approve"):
            updated = dict(sol)
            updated["approved"] = True
            out.append(updated)
        elif answer in ("e", "edit"):
            output_stream.write("    Enter the replacement proposal text (one line): ")
            output_stream.flush()
            replacement = (input_stream.readline() or "").strip()
            updated = dict(sol)
            updated["approved"] = True
            updated["user_edited_proposal"] = replacement
            out.append(updated)
        # anything else -> reject (drop)

    return out


__all__ = [
    "render_findings_for_review",
    "collect_finding_confirmations",
    "render_solutions_for_review",
    "collect_solution_approvals",
]
