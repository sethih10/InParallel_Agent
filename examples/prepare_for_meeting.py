"""
Example: Prepare for the next meeting.

Pulls open action items, recent decisions, and the current execution plan
for a workspace to build a pre-meeting brief.

Run:
    python examples/prepare_for_meeting.py
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
        workspace_id = workspaces[0]["id"]
        workspace_name = workspaces[0]["name"]
        print(f"=== Pre-Meeting Brief: {workspace_name} ===\n")

        # 2. Open action items
        raw = await ip.list_action_items(workspace_id, status="assigned")
        items = json.loads(raw) if isinstance(raw, str) else raw
        print(f"Open Action Items ({len(items)}):")
        for item in items:
            due = item.get("due_date", "no due date")
            owner = item.get("owner_email", "unassigned")
            print(f"  - [{owner}] {item['title']}  (due: {due})")

        # 3. Recent decisions
        raw = await ip.list_decisions(workspace_id)
        decisions = json.loads(raw) if isinstance(raw, str) else raw
        print(f"\nRecent Decisions ({len(decisions)}):")
        for d in decisions[:5]:
            print(f"  - [{d.get('status', '?')}] {d['title']}")

        # 4. Current execution plan
        raw = await ip.get_execution_plan(workspace_id)
        plan = json.loads(raw) if isinstance(raw, str) else raw
        print(f"\nExecution Plan: {plan.get('title', 'Untitled')}")
        print(f"Last updated: {plan.get('updated_at', 'unknown')}")
        if plan.get("content"):
            print("\n" + plan["content"][:500] + ("..." if len(plan.get("content", "")) > 500 else ""))


if __name__ == "__main__":
    asyncio.run(main())
