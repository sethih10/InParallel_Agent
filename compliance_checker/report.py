"""
Render a ``ComplianceReport`` as plain text. No external deps.
"""

from __future__ import annotations

from .checker import ComplianceReport

_SEVERITY_ORDER = ("high", "medium", "low")


def format_report(report: ComplianceReport) -> str:
    lines: list[str] = []
    header = f"Compliance Report: {report.workspace_name or report.workspace_id}"
    lines.append(header)
    lines.append("=" * len(header))

    groups = report.by_severity()
    total = sum(len(v) for v in groups.values())

    if total == 0:
        lines.append("")
        lines.append("No findings. All checked rules passed.")
        return "\n".join(lines)

    lines.append("")
    lines.append(
        "Summary: "
        + ", ".join(
            f"{sev}={len(groups.get(sev, []))}" for sev in _SEVERITY_ORDER
        )
        + f"  (total={total})"
    )

    for sev in _SEVERITY_ORDER:
        items = groups.get(sev, [])
        if not items:
            continue
        lines.append("")
        lines.append(f"[{sev.upper()}] {len(items)} finding(s)")
        lines.append("-" * 60)
        # Group by rule_id for readability.
        by_rule: dict[str, list] = {}
        for f in items:
            by_rule.setdefault(f.rule_id, []).append(f)
        for rule_id, findings in by_rule.items():
            lines.append(f"  {rule_id}  ({len(findings)})")
            for f in findings:
                lines.append(f"    - {f.message}")

    return "\n".join(lines)
