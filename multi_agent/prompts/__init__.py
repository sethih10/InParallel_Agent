"""Load agent system prompts from sibling Markdown files at runtime.

Prompts live in plain ``.md`` files so non-engineers (legal SMEs, compliance
officers) can edit them without touching Python code. The loader caches each
prompt on first read.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

_PROMPTS_DIR = Path(__file__).resolve().parent


@lru_cache(maxsize=None)
def load_prompt(name: str) -> str:
    """Load a prompt by short name (without extension).

    Args:
        name: The prompt file stem, e.g. ``"compliance_analyst"``.

    Returns:
        The full Markdown content of the prompt file.

    Raises:
        FileNotFoundError: if the prompt file does not exist.
    """
    path = _PROMPTS_DIR / f"{name}.md"
    if not path.exists():
        raise FileNotFoundError(f"Prompt file not found: {path}")
    return path.read_text(encoding="utf-8")


__all__ = ["load_prompt"]
