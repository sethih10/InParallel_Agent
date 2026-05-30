"""MCP Server for compliance notification integration.

This module sets up a Model Context Protocol (MCP) server that exposes tools
for sending notifications via Slack and email. The server can run in two modes:

1. **Mock mode** (demo): Logs messages to stdout instead of actually sending
2. **Real mode** (production): Uses real Slack API and SMTP integration

Environment variables:
    - MCP_MODE: "mock" or "real" (default: "mock")
    - MCP_SERVER_HOST: host for MCP server (default: "localhost")
    - MCP_SERVER_PORT: port for MCP server (default: 3000)
    - SLACK_WEBHOOK_URL: For real mode (optional)
    - SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD: For real mode (optional)
    - DEFAULT_NOTIFICATION_EMAIL: Target email for notifications (default: "compliance-team@demo.internal")
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, Optional

import mcp.server.stdio
import mcp.types as types
from mcp.server import Server

# ============================================================================ #
# Configuration                                                               #
# ============================================================================ #

logger = logging.getLogger("mcp.notification_server")

# Read environment configuration
import os

MCP_MODE = os.getenv("MCP_MODE", "mock")
MCP_SERVER_HOST = os.getenv("MCP_SERVER_HOST", "localhost")
MCP_SERVER_PORT = int(os.getenv("MCP_SERVER_PORT", "3000"))
DEFAULT_NOTIFICATION_EMAIL = os.getenv(
    "DEFAULT_NOTIFICATION_EMAIL", "compliance-team@demo.internal"
)
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")


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


def mock_send_email(
    recipient: str, subject: str, message: str
) -> Dict[str, Any]:
    """Mock email sender (logs to stdout/file in demo mode)."""
    log_entry = {
        "service": "email",
        "recipient": recipient,
        "subject": subject,
        "message": message,
        "status": "logged",
    }
    logger.info(f"[MOCK EMAIL] {json.dumps(log_entry)}")
    return {
        "success": True,
        "service": "email",
        "message": f"Mocked email to {recipient}",
    }


# ============================================================================ #
# Real Implementation (production)                                            #
# ============================================================================ #


def real_send_slack_message(
    channel: str, subject: str, message: str
) -> Dict[str, Any]:
    """Send real Slack message via webhook (production)."""
    if not SLACK_WEBHOOK_URL:
        return {
            "success": False,
            "error": "SLACK_WEBHOOK_URL not configured",
        }

    try:
        import requests

        payload = {
            "channel": channel,
            "text": f"*{subject}*\n{message}",
        }
        response = requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=5)
        response.raise_for_status()
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


def real_send_email(
    recipient: str, subject: str, message: str
) -> Dict[str, Any]:
    """Send real email via SMTP (production)."""
    if not SMTP_HOST:
        return {
            "success": False,
            "error": "SMTP not configured",
        }

    try:
        import smtplib
        from email.mime.text import MIMEText

        msg = MIMEText(message)
        msg["Subject"] = subject
        msg["From"] = SMTP_USER
        msg["To"] = recipient

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            if SMTP_PASSWORD:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)

        return {
            "success": True,
            "service": "email",
            "message": f"Email sent to {recipient}",
        }
    except Exception as e:
        logger.error(f"Email error: {e}")
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


def send_email(
    recipient: Optional[str], subject: str, message: str
) -> Dict[str, Any]:
    """Route to real or mock email sender based on MCP_MODE.
    
    Args:
        recipient: Email address. If None, uses DEFAULT_NOTIFICATION_EMAIL.
        subject: Email subject line
        message: Email body
    """
    if recipient is None:
        recipient = DEFAULT_NOTIFICATION_EMAIL

    if MCP_MODE == "mock":
        return mock_send_email(recipient, subject, message)
    else:
        return real_send_email(recipient, subject, message)


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

    @server.call_tool()
    async def call_send_email(
        name: str, arguments: Dict[str, Any]
    ) -> list[types.TextContent | types.ImageContent]:
        if name == "send_email":
            result = send_email(
                recipient=arguments.get("recipient"),
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
            types.Tool(
                name="send_email",
                description="Send a notification email",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "recipient": {
                            "type": "string",
                            "description": (
                                "Email address. If null, uses "
                                "DEFAULT_NOTIFICATION_EMAIL"
                            ),
                        },
                        "subject": {
                            "type": "string",
                            "description": "Email subject line",
                        },
                        "message": {
                            "type": "string",
                            "description": "Email body (supports HTML and plain text)",
                        },
                    },
                    "required": ["subject", "message"],
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
