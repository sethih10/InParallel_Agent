"""Central configuration for the compliance multi-agent system.

Reads environment variables (and `.env`) so the rest of the code can stay
free of `os.getenv()` calls. Modify this file - not the agents - to change
the model, temperature, or output directory.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from the project root if present.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_PROJECT_ROOT / ".env")


# --------------------------------------------------------------------------- #
# Model configuration                                                         #
# --------------------------------------------------------------------------- #

ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5")
ANTHROPIC_API_KEY: str | None = os.getenv("ANTHROPIC_API_KEY")

# Lower temperature for deterministic, audit-friendly compliance reasoning.
DEFAULT_TEMPERATURE: float = 0.0

# Cap on ReAct loop iterations per agent node (safety net).
MAX_AGENT_ITERATIONS: int = 12

# Inner agent recursion limit.
INNER_AGENT_RECURSION_LIMIT: int = 150


# --------------------------------------------------------------------------- #
# Paths                                                                       #
# --------------------------------------------------------------------------- #

PROJECT_ROOT: Path = _PROJECT_ROOT
REPORTS_DIR: Path = PROJECT_ROOT / "reports"
PROMPTS_DIR: Path = Path(__file__).resolve().parent / "prompts"


def ensure_reports_dir() -> Path:
    """Create the reports directory if it does not exist."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    return REPORTS_DIR


def require_api_key() -> str:
    """Return the Anthropic API key or raise a clear error."""
    if not ANTHROPIC_API_KEY:
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not set. Copy .env.example to .env and "
            "fill in your Anthropic API key, or export it in your shell."
        )
    return ANTHROPIC_API_KEY


__all__ = [
    "ANTHROPIC_MODEL",
    "ANTHROPIC_API_KEY",
    "DEFAULT_TEMPERATURE",
    "MAX_AGENT_ITERATIONS",
    "INNER_AGENT_RECURSION_LIMIT",
    "PROJECT_ROOT",
    "REPORTS_DIR",
    "PROMPTS_DIR",
    "ensure_reports_dir",
    "require_api_key",
]
