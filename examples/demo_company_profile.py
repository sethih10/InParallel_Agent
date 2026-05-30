"""Demo company profiles for the compliance checker system.

This module demonstrates how to configure different types of companies
for the compliance checker. Each profile shows how industry, regulations,
personnel, and legal requirements are specified.

In production, company profiles would be loaded from a database or
configuration management system. For this demo, they are hardcoded.
"""

from __future__ import annotations

from typing import Any, Dict

# The default demo company is Lumière Cosmetics (already in company_context.py)
# This file is for reference and future expansion.


DEMO_LUMIERE = {
    "company_id": "org-lumiere",
    "description": (
        "Lumière Cosmetics OY — A mid-market cosmetics company based in "
        "Helsinki. Subjects to EU Cosmetics Regulation (EC 1223/2009), "
        "Cosmetic Claims Regulation (EU 655/2013), and GDPR. High compliance "
        "risk due to product safety, marketing claims, and customer data."
    ),
}

DEMO_PHARMA = {
    "company_id": "org-pharma-demo",
    "description": (
        "Pharma Demo Inc. — A large pharmaceutical company based in New Jersey. "
        "Subjects to FDA regulations, EU pharmacovigilance, and GDPR. Critical "
        "compliance risk due to drug safety, manufacturing, and clinical data."
    ),
}

# Map of available demo companies
AVAILABLE_DEMOS = {
    "org-lumiere": DEMO_LUMIERE,
    "org-pharma-demo": DEMO_PHARMA,
}


def get_demo_company_description(company_id: str) -> str:
    """Return a human-readable description of a demo company."""
    demo = AVAILABLE_DEMOS.get(company_id, {})
    return demo.get("description", "Unknown company")


__all__ = [
    "DEMO_LUMIERE",
    "DEMO_PHARMA",
    "AVAILABLE_DEMOS",
    "get_demo_company_description",
]
