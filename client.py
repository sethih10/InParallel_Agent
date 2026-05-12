"""
In Parallel MCP Client

A thin wrapper around the MCP SDK for calling In Parallel tools.

Usage:
    from client import InParallelClient

    async with InParallelClient() as ip:
        workspaces = await ip.list_workspaces()
        print(workspaces)
"""

import os
from contextlib import asynccontextmanager
from typing import Any

from dotenv import load_dotenv
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

load_dotenv()


class InParallelClient:
    """Async context manager that connects to the In Parallel MCP server."""

    def __init__(
        self,
        api_key: str | None = None,
        url: str | None = None,
    ) -> None:
        self._api_key = api_key or os.environ["IN_PARALLEL_API_KEY"]
        self._url = url or os.getenv(
            "IN_PARALLEL_MCP_URL", "https://www.in-parallel.ai/mcp"
        )
        self._session: ClientSession | None = None
        self._exit_stack = None

    async def __aenter__(self) -> "InParallelClient":
        from contextlib import AsyncExitStack

        self._exit_stack = AsyncExitStack()
        await self._exit_stack.__aenter__()

        transport = await self._exit_stack.enter_async_context(
            streamablehttp_client(
                self._url,
                headers={"Authorization": f"Bearer {self._api_key}"},
            )
        )
        read, write, _ = transport
        self._session = await self._exit_stack.enter_async_context(
            ClientSession(read, write)
        )
        await self._session.initialize()
        return self

    async def __aexit__(self, *args: Any) -> None:
        if self._exit_stack:
            await self._exit_stack.__aexit__(*args)

    async def _call(self, tool: str, **kwargs: Any) -> Any:
        """Call an MCP tool and return the first text content."""
        if self._session is None:
            raise RuntimeError("Client is not connected. Use 'async with' context.")
        # Strip None values so optional params are omitted
        args = {k: v for k, v in kwargs.items() if v is not None}
        result = await self._session.call_tool(tool, args)
        if result.content:
            return result.content[0].text if hasattr(result.content[0], "text") else result.content[0]
        return None

    # ------------------------------------------------------------------ #
    # Workspace tools                                                       #
    # ------------------------------------------------------------------ #

    async def list_workspaces(self) -> Any:
        """List all workspaces accessible to the authenticated user."""
        return await self._call("list_workspaces")

    # ------------------------------------------------------------------ #
    # Meeting tools                                                        #
    # ------------------------------------------------------------------ #

    async def list_meeting_records(
        self,
        workspace_id: str,
        page_cursor: str | None = None,
    ) -> Any:
        """List recent meetings for a workspace, ordered newest first."""
        return await self._call(
            "list_meeting_records",
            workspace_id=workspace_id,
            page_cursor=page_cursor,
        )

    async def get_meeting_record(self, meeting_id: str) -> Any:
        """Retrieve the complete structured record for a meeting."""
        return await self._call("get_meeting_record", meeting_id=meeting_id)

    async def get_transcript(self, meeting_id: str) -> Any:
        """Retrieve the speaker-attributed transcript for a meeting."""
        return await self._call("get_transcript", meeting_id=meeting_id)

    # ------------------------------------------------------------------ #
    # Decision tools                                                       #
    # ------------------------------------------------------------------ #

    async def list_decisions(
        self,
        workspace_id: str,
        status: str | None = None,
        page_cursor: str | None = None,
    ) -> Any:
        """List decisions within a workspace."""
        return await self._call(
            "list_decisions",
            workspace_id=workspace_id,
            status=status,
            page_cursor=page_cursor,
        )

    async def get_decision(self, decision_id: str) -> Any:
        """Retrieve the full details of a specific decision."""
        return await self._call("get_decision", decision_id=decision_id)

    # ------------------------------------------------------------------ #
    # Action item tools                                                    #
    # ------------------------------------------------------------------ #

    async def list_action_items(
        self,
        workspace_id: str,
        status: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        page_cursor: str | None = None,
    ) -> Any:
        """List action items within a workspace."""
        return await self._call(
            "list_action_items",
            workspace_id=workspace_id,
            status=status,
            start_date=start_date,
            end_date=end_date,
            page_cursor=page_cursor,
        )

    async def get_action_item(self, action_item_id: str) -> Any:
        """Retrieve the full details of an action item."""
        return await self._call("get_action_item", action_item_id=action_item_id)

    async def create_action_item(
        self,
        workspace_id: str,
        source_meeting_id: str,
        title: str,
        summary: str | None = None,
        owner_email: str | None = None,
        due_date: str | None = None,
        status: str | None = None,
    ) -> Any:
        """Create a new action item linked to a source meeting."""
        return await self._call(
            "create_action_item",
            workspace_id=workspace_id,
            source_meeting_id=source_meeting_id,
            title=title,
            summary=summary,
            owner_email=owner_email,
            due_date=due_date,
            status=status,
        )

    async def update_action_item(
        self,
        action_item_id: str,
        title: str | None = None,
        summary: str | None = None,
        owner_email: str | None = None,
        due_date: str | None = None,
        status: str | None = None,
    ) -> Any:
        """Update an existing action item."""
        return await self._call(
            "update_action_item",
            action_item_id=action_item_id,
            title=title,
            summary=summary,
            owner_email=owner_email,
            due_date=due_date,
            status=status,
        )

    async def close_action_item(
        self,
        action_item_id: str,
        resolution: str | None = None,
    ) -> Any:
        """Mark an action item as done."""
        return await self._call(
            "close_action_item",
            action_item_id=action_item_id,
            resolution=resolution,
        )

    # ------------------------------------------------------------------ #
    # Execution plan tools                                                 #
    # ------------------------------------------------------------------ #

    async def get_execution_plan(self, workspace_id: str) -> Any:
        """Retrieve the current execution plan for a workspace."""
        return await self._call("get_execution_plan", workspace_id=workspace_id)

    async def get_plan_versions(self, workspace_id: str) -> Any:
        """Retrieve version history for a workspace's execution plan."""
        return await self._call("get_plan_versions", workspace_id=workspace_id)
