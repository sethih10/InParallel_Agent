"""Run the LangChain/Anthropic-based compliance checker demo."""

from langchain_agent import run_query_with_agent


def main():
    print("Running LangChain-compatible compliance demo with Anthropic...\n")
    resp = run_query_with_agent(
        "Using the available tools, analyze the specified meeting for compliance risks, "
        "including GDPR, DPIA, and legal review needs.",
        meeting_id="meeting-001",
    )

    if "agent_response" in resp:
        print("LangChain agent response:\n")
        print(resp["agent_response"])
    elif "error" in resp:
        print("Error:\n")
        print(resp["error"])
    else:
        print("Unexpected response:\n", resp)


if __name__ == "__main__":
    main()
