"""Fake/seed data for the multi-agent compliance demo.

This package isolates ALL mock data from the agent and graph logic. Replace
this package with a real database adapter to move from demo to production.
"""

from . import company_database, meetings

__all__ = ["company_database", "meetings"]
