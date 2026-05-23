"""LLM-backed ReAct agents used by the graph.

Each module exposes a single ``build_*`` factory function so the graph can
instantiate the agent once at graph-build time.
"""

from .compliance_analyst import build_compliance_analyst
from .legal_researcher import build_legal_researcher
from .notifier import build_notifier

__all__ = [
    "build_compliance_analyst",
    "build_legal_researcher",
    "build_notifier",
]
