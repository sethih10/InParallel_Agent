"""Interactive CLI entry point for the compliance multi-agent demo.

Usage::

    python run_multi_agent_demo.py                   # default: meeting-glow-001
    python run_multi_agent_demo.py meeting-glow-002  # wider-coverage meeting

Available meetings:
    meeting-glow-001  — 7 decisions (claims, safety, GDPR, animal testing)
    meeting-glow-002  — 10 decisions (GMP, restricted substances, labelling,
                        consent, privacy-by-design, lawful basis, transparency,
                        plus honesty and fairness claims)

Requires ``ANTHROPIC_API_KEY`` to be set (in ``.env`` or environment).
"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict, List

from langgraph.types import Command

from multi_agent.graph import build_compliance_graph, new_thread_config
from multi_agent.nodes import human_review
from multi_agent.nodes.report_generator import (
    format_report_text,
    save_report_json,
)


DEFAULT_MEETING_ID = "meeting-glow-001"


def _get_state_values(graph, config) -> Dict[str, Any]:
    """Read the current state values for a thread."""
    snapshot = graph.get_state(config)
    return dict(snapshot.values or {})


def _run_gate_1(graph, config) -> List[Dict[str, Any]]:
    """Render potential findings, collect user confirmations, return confirmed list."""
    state = _get_state_values(graph, config)
    findings = state.get("potential_findings", []) or []

    if not findings:
        print("\n[!] Compliance Analyst produced no findings - nothing to confirm.")
        return []

    print(human_review.render_findings_for_review(findings))
    confirmed = human_review.collect_finding_confirmations(findings)
    print(f"\n[OK] {len(confirmed)} of {len(findings)} findings confirmed.")
    return confirmed


def _run_gate_2(graph, config) -> List[Dict[str, Any]]:
    """Render proposed solutions, collect approvals, return approved list."""
    state = _get_state_values(graph, config)
    solutions = state.get("proposed_solutions", []) or []
    confirmed = state.get("confirmed_findings", []) or []
    findings_by_id = {f["id"]: f for f in confirmed}

    if not solutions:
        print("\n[!] Legal Researcher produced no solutions - nothing to approve.")
        return []

    print(human_review.render_solutions_for_review(solutions, findings_by_id))
    approved = human_review.collect_solution_approvals(solutions)
    print(f"\n[OK] {len(approved)} of {len(solutions)} solutions approved.")
    return approved


def main(meeting_id: str = DEFAULT_MEETING_ID) -> int:
    print("=" * 78)
    print("  Lumière Cosmetics - Compliance Multi-Agent Demo")
    print("=" * 78)
    print(f"  Meeting under review: {meeting_id}")
    print()

    graph = build_compliance_graph()
    config = new_thread_config()

    # --- Run until first interrupt (before legal_researcher) -----------
    print("[*] Running Compliance Analyst...")
    graph.invoke({"meeting_id": meeting_id}, config=config)

    # --- HITL Gate 1 ----------------------------------------------------
    confirmed_findings = _run_gate_1(graph, config)
    graph.update_state(
        config,
        {
            "confirmed_findings": confirmed_findings,
            "gate1_complete": True,
        },
    )

    if not confirmed_findings:
        print("\n[!] No findings confirmed by legal team - skipping legal research.")
        # Update state so the rest of the pipeline still completes (empty).
        graph.update_state(
            config,
            {"proposed_solutions": [], "approved_solutions": []},
        )
        # Continue past both interrupts to the end.
        graph.invoke(Command(resume=True), config=config)
        graph.invoke(Command(resume=True), config=config)
    else:
        # --- Resume to next interrupt (before notifier) ----------------
        print("\n[*] Running Legal Research agent...")
        graph.invoke(Command(resume=True), config=config)

        # --- HITL Gate 2 -----------------------------------------------
        approved_solutions = _run_gate_2(graph, config)
        graph.update_state(
            config,
            {
                "approved_solutions": approved_solutions,
                "gate2_complete": True,
            },
        )

        # --- Resume to end (notifier + report_generator) ---------------
        print("\n[*] Running Notification & Coordination agent...")
        graph.invoke(Command(resume=True), config=config)

    # --- Final report ---------------------------------------------------
    final_state = _get_state_values(graph, config)
    report = final_state.get("final_report") or {}

    print("\n")
    print(format_report_text(report))

    out_path = save_report_json(report)
    print(f"\n[OK] JSON report saved to: {out_path}")

    return 0


if __name__ == "__main__":
    meeting = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_MEETING_ID
    try:
        sys.exit(main(meeting))
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user.")
        sys.exit(130)
    except Exception as exc:  # noqa: BLE001
        print(f"\n[ERROR] {type(exc).__name__}: {exc}")
        raise
