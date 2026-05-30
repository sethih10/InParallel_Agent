"""Demo script showcasing the orchestrator agent in the compliance checker.

This script demonstrates:
1. How the orchestrator assesses meeting context within company profile
2. Whether legal personnel should have been present
3. Full compliance checking flow with orchestrator as first step

Run with:
    python examples/demo_with_orchestrator.py [meeting_id] [company_id]

Example:
    python examples/demo_with_orchestrator.py meeting-glow-001 org-lumiere
    python examples/demo_with_orchestrator.py meeting-glow-002 org-lumiere
"""

import json
import sys
from pathlib import Path

# Add parent directory to path so we can import multi_agent
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from multi_agent.data.company_context import get_company_profile
from multi_agent.data.decision_categorizer import (
    categorize_decisions,
    determine_legal_requirements,
)
from multi_agent.data import meetings
from multi_agent.graph import build_compliance_graph, new_thread_config
from langgraph.types import Command
from multi_agent.nodes import human_review
from multi_agent.nodes.report_generator import format_report_text, save_report_json


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}\n")


def demonstrate_orchestrator_assessment(meeting_id: str, company_id: str):
    """Demonstrate what the orchestrator does without running the full graph."""
    print_section("Orchestrator Assessment (Pre-Run)")

    company = get_company_profile(company_id)
    if not company:
        print(f"[!] Company not found: {company_id}")
        return

    meeting = meetings.get_meeting(meeting_id)
    if not meeting:
        print(f"[!] Meeting not found: {meeting_id}")
        return

    print(f"Company: {company.get('name')}")
    print(f"Industry: {company.get('industry')}")
    print(f"Risk Level: {company.get('risk_level')}")
    print(f"\nMeeting: {meeting.get('title')}")
    print(f"Attendees: {len(meeting.get('participants', []))}")

    # Categorize decisions
    decisions = meetings.list_decisions(meeting_id)
    if decisions:
        categorized = categorize_decisions(decisions)
        assessment = determine_legal_requirements(company, categorized)

        print(f"\nDecisions: {len(categorized)}")
        print(f"High-risk decisions: {len(assessment['high_risk_decisions'])}")

        if assessment["high_risk_decisions"]:
            print("\nHigh-Risk Decision Categories:")
            for decision in assessment["high_risk_decisions"]:
                print(f"  - {decision.get('category_name')} (confidence: {decision.get('confidence'):.1%})")

        print(f"\n[Assessment Result]")
        print(f"Should lawyer be present: {assessment['should_have_lawyer']}")
        print(f"Reason: {assessment['reason']}")
        print(f"Required personnel: {', '.join(assessment['relevant_personnel'])}")

        # Check if lawyer was actually present
        participants = meeting.get("participants", [])
        has_lawyer = any(
            "counsel" in p.lower() or "legal" in p.lower()
            for p in participants
        )
        print(f"\nLawyer actually present: {has_lawyer}")

        if assessment["should_have_lawyer"] and not has_lawyer:
            print("⚠️  CONCERN: Legal personnel should have been present but were not!")


def run_full_demo(meeting_id: str, company_id: str) -> int:
    """Run the full compliance checker pipeline."""
    print_section("Running Full Compliance Checker Pipeline")

    graph = build_compliance_graph()
    config = new_thread_config()

    # --- Orchestrator -------
    print("[*] Running Orchestrator...")
    graph.invoke({"meeting_id": meeting_id, "company_id": company_id}, config=config)

    def _get_state_values(graph, config):
        snapshot = graph.get_state(config)
        return dict(snapshot.values or {})

    state = _get_state_values(graph, config)
    orchestrator_output = state.get("orchestrator_output", {})

    if orchestrator_output:
        print(f"\n[Orchestrator Output]")
        lawyer_assessment = orchestrator_output.get("lawyer_assessment", {})
        print(f"  Meeting Summary: {orchestrator_output.get('meeting_summary', 'N/A')[:80]}...")
        print(f"  Lawyer present: {lawyer_assessment.get('was_lawyer_present')}")
        print(f"  Lawyer required: {lawyer_assessment.get('should_lawyer_have_been_present')}")

    # --- Compliance Analyst -------
    print("\n[*] Running Compliance Analyst...")
    findings = state.get("potential_findings", []) or []

    if not findings:
        print("[!] No findings - meeting appears compliant.")
        # Continue to completion
        graph.update_state(config, {"confirmed_findings": [], "gate1_complete": True})
        graph.update_state(config, {"proposed_solutions": [], "approved_solutions": []})
        graph.invoke(Command(resume=True), config=config)
        graph.invoke(Command(resume=True), config=config)
    else:
        print(f"[!] Found {len(findings)} potential findings.")
        print("\nPress Ctrl+C to skip HITL review (auto-approve all).")
        print("Otherwise, the normal HITL gates will appear.\n")

        # --- HITL Gate 1 -------
        try:
            print(human_review.render_findings_for_review(findings))
            confirmed = human_review.collect_finding_confirmations(findings)
        except KeyboardInterrupt:
            print("\n[!] Skipping HITL - auto-approving all findings.")
            confirmed = findings

        graph.update_state(
            config,
            {
                "confirmed_findings": confirmed,
                "gate1_complete": True,
            },
        )

        if confirmed:
            # --- Legal Researcher -------
            print("\n[*] Running Legal Research agent...")
            graph.invoke(Command(resume=True), config=config)

            # --- HITL Gate 2 -------
            state = _get_state_values(graph, config)
            solutions = state.get("proposed_solutions", []) or []

            try:
                findings_by_id = {f["id"]: f for f in confirmed}
                print(human_review.render_solutions_for_review(solutions, findings_by_id))
                approved = human_review.collect_solution_approvals(solutions)
            except KeyboardInterrupt:
                print("\n[!] Skipping HITL - auto-approving all solutions.")
                approved = solutions

            graph.update_state(
                config,
                {
                    "approved_solutions": approved,
                    "gate2_complete": True,
                },
            )

            # --- Notifier & Report -------
            print("\n[*] Running Notification & Coordination agent...")
            graph.invoke(Command(resume=True), config=config)
        else:
            # No confirmed findings - skip to end
            graph.update_state(config, {"proposed_solutions": [], "approved_solutions": []})
            graph.invoke(Command(resume=True), config=config)
            graph.invoke(Command(resume=True), config=config)

    # --- Final Report -------
    state = _get_state_values(graph, config)
    report = state.get("final_report") or {}

    print("\n")
    print(format_report_text(report))

    out_path = save_report_json(report)
    print(f"\n[OK] JSON report saved to: {out_path}")

    return 0


def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        return 0

    meeting_id = sys.argv[1] if len(sys.argv) > 1 else "meeting-glow-001"
    company_id = sys.argv[2] if len(sys.argv) > 2 else "org-lumiere"

    print_section("Compliance Checker with Orchestrator")
    print(f"Meeting: {meeting_id}")
    print(f"Company: {company_id}\n")

    # Show what the orchestrator will assess
    demonstrate_orchestrator_assessment(meeting_id, company_id)

    # Run the full pipeline
    print_section("Full Pipeline Execution")
    return run_full_demo(meeting_id, company_id)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user.")
        sys.exit(130)
    except Exception as exc:
        print(f"\n[ERROR] {type(exc).__name__}: {exc}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
