"""Hierarchical multi-agent compliance system for cosmetics companies.

Top-level public surface::

    from multi_agent import build_compliance_graph, new_thread_config

For the demo entry point, see ``run_multi_agent_demo.py`` at the project
root.
"""

from .graph import build_compliance_graph, new_thread_config

__all__ = ["build_compliance_graph", "new_thread_config"]
