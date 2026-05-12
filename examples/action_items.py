"""
Example: List open action items and create a new one.

Run:
    python examples/action_items.py
"""

import asyncio
import json
import sys

sys.path.insert(0, "..")
from client import InParallelClient


async def main() -> None:
    async with InParallelClient() as ip:
        # 1. Pick a workspace
        raw = await ip.list_workspaces()
        workspaces = json.loads(raw) if isinstance(raw, str) else raw
        workspace_id = workspaces[0]["id"]
        workspace_name = workspaces[0]["name"]
        print(f"Workspace: {workspace_name}")

        # 2. List open action items (assigned + in_progress)
        for status in ("assigned", "in_progress"):
            raw = await ip.list_action_items(workspace_id, status=status)
            items = json.loads(raw) if isinstance(raw, str) else raw
            print(f"\n[{status}] ({len(items)} items)")
            for item in items:
                due = item.get("due_date", "no due date")
                owner = item.get("owner_email", "unassigned")
                print(f"  - {item['title']}  |  owner: {owner}  |  due: {due}")

        # 3. Create a new action item (requires a real meeting ID)
        # Uncomment and replace the IDs to test:
        #
        # raw = await ip.list_meeting_records(workspace_id)
        # meetings = json.loads(raw) if isinstance(raw, str) else raw
        # meeting_id = meetings[0]["id"]
        #
        # result = await ip.create_action_item(
        #     workspace_id=workspace_id,
        #     source_meeting_id=meeting_id,
        #     title="Draft the MCP launch blog post",
        #     owner_email="sami@example.com",
        #     due_date="2026-05-15",
        # )
        # print("\nCreated:", result)


if __name__ == "__main__":
    asyncio.run(main())
