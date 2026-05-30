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
from multi_agent.config import MCP_MODE, SLACK_BOT_TOKEN


DEFAULT_MEETING_ID = "meeting-glow-001"


def _check_slack_config() -> bool:
    """Verify Slack is configured for real message sending."""
    if MCP_MODE != "real":
        print(f"[ERROR] MCP_MODE is '{MCP_MODE}' but must be 'real' to send Slack messages.")
        print("        Set MCP_MODE=real in your .env file.")
        return False
    
    if not SLACK_BOT_TOKEN:
        print("[ERROR] SLACK_BOT_TOKEN is not set.")
        print("        Set SLACK_BOT_TOKEN=xoxb-... in your .env file.")
        return False
    
    print(f"[OK] Slack configured (MCP_MODE={MCP_MODE}, token present)")
    return True


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


def main(meeting_id: str = DEFAULT_MEETING_ID, company_id: str = "org-lumiere") -> int:
    print("=" * 78)
    print("  Compliance Multi-Agent Demo")
    print("=" * 78)
    print(f"  Company: {company_id}")
    print(f"  Meeting under review: {meeting_id}")
    print()

    # Verify Slack is configured before proceeding
    if not _check_slack_config():
        return 1

    graph = build_compliance_graph()
    config = new_thread_config()

    # --- Run until first interrupt (before legal_researcher) -----------
    print("[*] Running Orchestrator...")
    graph.invoke({"meeting_id": meeting_id, "company_id": company_id}, config=config)
    
    # Show orchestrator output
    state = _get_state_values(graph, config)
    orchestrator_output = state.get("orchestrator_output", {})
    if orchestrator_output:
        print(f"\n[Orchestrator Assessment]")
        print(f"  Meeting: {orchestrator_output.get('meeting_title', 'N/A')}")
        lawyer_assessment = orchestrator_output.get("lawyer_assessment", {})
        if lawyer_assessment:
            was_present = lawyer_assessment.get("was_lawyer_present")
            should_present = lawyer_assessment.get("should_lawyer_have_been_present")
            print(f"  Lawyer present: {was_present}")
            print(f"  Lawyer required: {should_present}")
            if should_present and not was_present:
                print(f"  ⚠️  WARNING: Legal personnel should have been present!")
    
    print("\n[*] Running Compliance Analyst...")

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
        print("\n[*] Running Notification & Coordination agent (sending to Slack)...")
        graph.invoke(Command(resume=True), config=config)

    # --- Check Slack notifications were sent ----------------------------
    final_state = _get_state_values(graph, config)
    notifications = final_state.get("department_notifications") or []
    meeting_agenda = final_state.get("meeting_agenda")
    
    # Count Slack sends (look at console output [SLACK OK] / [SLACK ERROR])
    total_items = len(notifications) + (1 if meeting_agenda else 0)
    
    if total_items == 0:
        print("\n[ERROR] No notifications or agenda were generated!")
        return 1
    
    print(f"\n[OK] Notifier completed. {len(notifications)} notification(s) + agenda processed.")
    print("     Check [SLACK OK] / [SLACK ERROR] messages above for Slack status.")
    return 0


if __name__ == "__main__":
    meeting = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_MEETING_ID
    company = sys.argv[2] if len(sys.argv) > 2 else "org-lumiere"
    try:
        sys.exit(main(meeting, company))
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user.")
        sys.exit(130)
    except Exception as exc:  # noqa: BLE001
        print(f"\n[ERROR] {type(exc).__name__}: {exc}")
        raise
