"""MCP Server for compliance notification integration.

This module sets up a Model Context Protocol (MCP) server that exposes tools
for sending notifications via Slack. The server can run in two modes:

1. **Mock mode** (demo): Logs messages to stdout instead of actually sending
2. **Real mode** (production): Uses a Slack bot token and the Slack Web API

Environment variables:
    - MCP_MODE: "mock" or "real" (default: "mock")
    - MCP_SERVER_HOST: host for MCP server (default: "localhost")
    - MCP_SERVER_PORT: port for MCP server (default: 3000)
    - SLACK_BOT_TOKEN: Slack bot token with `chat:write` permission
    - SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD: For real mode (optional)
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict

import mcp.server.stdio
import mcp.types as types
from mcp.server import Server

from multi_agent.config import (
    MCP_MODE,
    MCP_SERVER_HOST,
    MCP_SERVER_PORT,
    SLACK_BOT_TOKEN,
)

# ============================================================================ #
# Configuration                                                               #
# ============================================================================ #

logger = logging.getLogger("mcp.notification_server")

SMTP_HOST = ""
SMTP_PORT = 587
SMTP_USER = ""
SMTP_PASSWORD = ""


# ============================================================================ #
# Mock Implementation (for demo)                                              #
# ============================================================================ #


def mock_send_slack_message(
    channel: str, subject: str, message: str
) -> Dict[str, Any]:
    """Mock Slack message sender (logs to stdout/file in demo mode)."""
    log_entry = {
        "service": "slack",
        "channel": channel,
        "subject": subject,
        "message": message,
        "status": "logged",
    }
    logger.info(f"[MOCK SLACK] {json.dumps(log_entry)}")
    return {
        "success": True,
        "service": "slack",
        "message": f"Mocked Slack message to {channel}",
    }


# ============================================================================ #
# Real Implementation (production)                                            #
# ============================================================================ #


def real_send_slack_message(
    channel: str, subject: str, message: str
) -> Dict[str, Any]:
    """Send real Slack message using Slack bot token."""
    if not SLACK_BOT_TOKEN:
        return {
            "success": False,
            "error": "SLACK_BOT_TOKEN not configured",
        }

    try:
        import requests

        url = "https://slack.com/api/chat.postMessage"
        headers = {
            "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
            "Content-Type": "application/json; charset=utf-8",
        }
        payload = {
            "channel": channel,
            "text": f"*{subject}*\n{message}",
        }

        response = requests.post(url, headers=headers, json=payload, timeout=5)
        response.raise_for_status()
        data = response.json()

        if not data.get("ok"):
            return {
                "success": False,
                "error": data.get("error", "unknown Slack API error"),
                "response": data,
            }

        return {
            "success": True,
            "service": "slack",
            "message": f"Slack message sent to {channel}",
        }
    except Exception as e:
        logger.error(f"Slack error: {e}")
        return {
            "success": False,
            "error": str(e),
        }


# ============================================================================ #
# Notification Tool Implementations                                           #
# ============================================================================ #


def send_slack_message(
    channel: str, subject: str, message: str
) -> Dict[str, Any]:
    """Route to real or mock Slack sender based on MCP_MODE."""
    if MCP_MODE == "mock":
        return mock_send_slack_message(channel, subject, message)
    else:
        return real_send_slack_message(channel, subject, message)



# ============================================================================ #
# MCP Server Setup                                                            #
# ============================================================================ #


def setup_mcp_server() -> Server:
    """Create and configure the MCP server with notification tools."""
    server = Server("compliance-notifier-mcp")

    # Define the send_slack_message tool
    @server.call_tool()
    async def call_send_slack(
        name: str, arguments: Dict[str, Any]
    ) -> list[types.TextContent | types.ImageContent]:
        if name == "send_slack_message":
            result = send_slack_message(
                channel=arguments.get("channel", ""),
                subject=arguments.get("subject", ""),
                message=arguments.get("message", ""),
            )
            return [types.TextContent(type="text", text=json.dumps(result))]
        raise ValueError(f"Unknown tool: {name}")

    # Register the tools with the server
    @server.list_tools()
    async def list_tools() -> list[types.Tool]:
        return [
            types.Tool(
                name="send_slack_message",
                description="Send a notification message to a Slack channel",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "channel": {
                            "type": "string",
                            "description": "Slack channel name (e.g., #compliance)",
                        },
                        "subject": {
                            "type": "string",
                            "description": "Message subject/title",
                        },
                        "message": {
                            "type": "string",
                            "description": "Message body (supports Markdown)",
                        },
                    },
                    "required": ["channel", "subject", "message"],
                },
            ),
        ]

    return server


async def main():
    """Run the MCP server."""
    server = setup_mcp_server()
    logger.info(
        f"Starting MCP notification server (mode={MCP_MODE}) on "
        f"{MCP_SERVER_HOST}:{MCP_SERVER_PORT}"
    )
    async with mcp.server.stdio.stdio_server(server) as streams:
        await server.request_channel(streams)


if __name__ == "__main__":
    import asyncio

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    asyncio.run(main())
