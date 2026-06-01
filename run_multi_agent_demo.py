"""Interactive CLI entry point for the compliance multi-agent demo.

Usage::

    python run_multi_agent_demo.py                   # default: meeting-glow-001
    python run_multi_agent_demo.py meeting-glow-002  # wider-coverage meeting

Graph topology (v4 — parallel notifier + legal researcher)::

    compliance_analyst → [Gate 1] → fan_out ─┬─► notifier
                                             └─► legal_researcher
                                    fan_in  → [Gate 2] → report_generator

Gate 1: legal team confirms which findings are real issues.
         Immediately after, the notifier alerts departments AND the legal
         researcher begins drafting solutions — in parallel.
Gate 2: legal team approves / edits / rejects proposed solutions.
         Then the report generator compiles the final output.

Requires ``ANTHROPIC_API_KEY`` in ``.env`` or environment.
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
    snapshot = graph.get_state(config)
    return dict(snapshot.values or {})


def _run_gate_1(graph, config) -> List[Dict[str, Any]]:
    """Render potential findings, collect user confirmations."""
    state = _get_state_values(graph, config)
    findings = state.get("potential_findings", []) or []

    if not findings:
        print("\n[!] Compliance Analyst produced no findings — nothing to confirm.")
        return []

    print(human_review.render_findings_for_review(findings))
    confirmed = human_review.collect_finding_confirmations(findings)
    print(f"\n[OK] {len(confirmed)} of {len(findings)} findings confirmed.")
    return confirmed


def _run_gate_2(graph, config) -> List[Dict[str, Any]]:
    """Render proposed solutions, collect approvals."""
    state = _get_state_values(graph, config)
    solutions = state.get("proposed_solutions", []) or []
    confirmed = state.get("confirmed_findings", []) or []
    findings_by_id = {f["id"]: f for f in confirmed}

    if not solutions:
        print("\n[!] Legal Researcher produced no solutions — nothing to approve.")
        return []

    print(human_review.render_solutions_for_review(solutions, findings_by_id))
    approved = human_review.collect_solution_approvals(solutions)
    print(f"\n[OK] {len(approved)} of {len(solutions)} solutions approved.")
    return approved


def main(meeting_id: str = DEFAULT_MEETING_ID) -> int:
    print("=" * 78)
    print("  Lumière Cosmetics — Compliance Multi-Agent Demo")
    print("=" * 78)
    print(f"  Meeting under review: {meeting_id}")
    print()

    graph = build_compliance_graph()
    config = new_thread_config()

    # ------------------------------------------------------------------
    # Phase 1: Run compliance analyst, pause before fan_out (Gate 1)
    # ------------------------------------------------------------------
    print("[*] Running Compliance Analyst...")
    graph.invoke({"meeting_id": meeting_id}, config=config)

    # -- HITL Gate 1 ---------------------------------------------------
    confirmed_findings = _run_gate_1(graph, config)
    graph.update_state(
        config,
        {
            "confirmed_findings": confirmed_findings,
            "gate1_complete": True,
        },
        as_node="fan_out",
    )

    if not confirmed_findings:
        print("\n[!] No findings confirmed — nothing to do.")
        # Push empty state through remaining interrupts to reach END.
        graph.update_state(
            config,
            {"proposed_solutions": [], "approved_solutions": [],
             "department_notifications": [], "meeting_agenda": None},
            as_node="fan_out",
        )
        graph.invoke(Command(resume=True), config=config)  # past fan_out
        graph.invoke(Command(resume=True), config=config)  # past fan_in
    else:
        # --------------------------------------------------------------
        # Phase 2: Resume — fan_out triggers notifier + legal_researcher
        #          in parallel.  Graph pauses again before fan_in (Gate 2).
        # --------------------------------------------------------------
        print("\n[*] Running Notifier + Legal Researcher in parallel...")
        graph.invoke(Command(resume=True), config=config)

        # -- HITL Gate 2 -----------------------------------------------
        # By now, both branches have written their outputs:
        #   - notifier  → department_notifications, meeting_agenda
        #   - legal_researcher → proposed_solutions
        state = _get_state_values(graph, config)
        notifications = state.get("department_notifications", []) or []
        agenda = state.get("meeting_agenda")

        if notifications:
            print("\n" + "=" * 78)
            print("  DEPARTMENT NOTIFICATIONS SENT")
            print("=" * 78)
            for n in notifications:
                print(f"\n  To: {n.get('department_name', '?')} "
                      f"<{n.get('recipient_email', '')}>")
                print(f"  Subject: {n.get('subject', '')}")
                body = n.get("body", "")
                for line in body.split(". "):
                    print(f"    {line.strip()}")

        if agenda:
            print(f"\n  Meeting proposed: {agenda.get('title', '')}")
            attendees = agenda.get("suggested_attendees", [])
            if attendees:
                print(f"  Attendees: {', '.join(attendees[:5])}"
                      f"{'...' if len(attendees) > 5 else ''}")

        approved_solutions = _run_gate_2(graph, config)
        graph.update_state(
            config,
            {
                "approved_solutions": approved_solutions,
                "gate2_complete": True,
            },
            as_node="fan_in",
        )

        # --------------------------------------------------------------
        # Phase 3: Resume — report_generator compiles everything.
        # --------------------------------------------------------------
        print("\n[*] Generating final report...")
        graph.invoke(Command(resume=True), config=config)

    # -- Final report --------------------------------------------------
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
