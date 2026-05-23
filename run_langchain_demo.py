"""Run the multi-agent compliance checker demo.

Flow
----
1. The Compliance Issue Detector agent scans the meeting for potential issues.
2. If issues are found it delegates to the Legal Compliance Checker agent,
   which evaluates the transcript against GDPR, ePrivacy, Finnish law, and
   company policies.
3. The detector agent then emails the full compliance report to the person
   who initiated the meeting.
"""

from langchain_agent import run_query_with_agent


def main():
    print("=" * 60)
    print("  Multi-Agent Compliance Checker Demo")
    print("=" * 60)
    print()
    print("Agent 1: Compliance Issue Detector  (orchestrator)")
    print("Agent 2: Legal Compliance Checker   (specialist)")
    print()
    print("The compliance report will be emailed to the meeting")
    print("initiator instead of being printed to the console.")
    print("-" * 60)
    print()

    resp = run_query_with_agent(
        "Analyse the specified meeting for potential compliance issues. "
        "If any issues are found, delegate a full legal compliance check "
        "to the Legal Compliance Checker agent. Once the analysis is "
        "complete, email the compliance report to the meeting initiator.",
        meeting_id="meeting-001",
    )

    print("\n" + "-" * 60)
    if "agent_response" in resp:
        print("Orchestrator summary:\n")
        print(resp["agent_response"])
    elif "error" in resp:
        print("Error:\n")
        print(resp["error"])
    else:
        print("Unexpected response:\n", resp)


if __name__ == "__main__":
    main()
