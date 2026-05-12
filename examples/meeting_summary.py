"""
Example: Summarize the latest meeting in a workspace.

Run:
    python examples/meeting_summary.py
"""

import asyncio
import json
import sys

sys.path.insert(0, "..")
from client import InParallelClient


async def main() -> None:
    async with InParallelClient() as ip:
        # 1. Resolve workspace
        raw = await ip.list_workspaces()
        workspaces = json.loads(raw) if isinstance(raw, str) else raw
        print("Available workspaces:")
        for ws in workspaces:
            print(f"  {ws['name']}  ({ws['id']})")

        workspace_id = workspaces[0]["id"]

        # 2. Get the latest meeting
        raw = await ip.list_meeting_records(workspace_id)
        meetings = json.loads(raw) if isinstance(raw, str) else raw
        if not meetings:
            print("No meetings found.")
            return

        latest = meetings[0]
        print(f"\nLatest meeting: {latest['topic']}  ({latest['start_time']})")

        # 3. Fetch the full record
        raw = await ip.get_meeting_record(latest["id"])
        record = json.loads(raw) if isinstance(raw, str) else raw

        print("\n--- Summary ---")
        print(record.get("summary", "No summary available."))

        print("\n--- Action Items ---")
        for item in record.get("action_items", []):
            print(f"  [{item.get('status', '?')}] {item['title']}")

        print("\n--- Decisions ---")
        for decision in record.get("decisions", []):
            print(f"  {decision['title']}")


if __name__ == "__main__":
    asyncio.run(main())
