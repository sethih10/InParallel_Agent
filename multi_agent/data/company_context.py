"""Company context and profile system for the general compliance checker.

This module provides a mock database of company profiles that can be queried
at runtime. Company profiles include industry, risk level, applicable regulations,
and personnel roles. This allows the orchestrator agent to understand the
company's compliance landscape and assess whether legal personnel should have
been present at a meeting.

Each company profile is independently loadable, making the compliance system
general-purpose: the same agents work for any company, with company data
as a runtime input.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


# ============================================================================ #
# Company Profiles Database                                                   #
# ============================================================================ #


def get_company_profile(company_id: str) -> Optional[Dict[str, Any]]:
    """Fetch a company profile by id from the mock database.

    Args:
        company_id: The company identifier (e.g. ``org-lumiere`` or ``org-pharma-demo``).

    Returns:
        A dictionary with company metadata (industry, risk level, regulations,
        personnel, legal requirements) or None if not found.
    """
    profiles = {
        "org-lumiere": _LUMIERE_PROFILE,
        "org-pharma-demo": _PHARMA_DEMO_PROFILE,
    }
    return profiles.get(company_id)


def list_companies() -> List[Dict[str, str]]:
    """Return a list of all available companies with basic metadata."""
    return [
        {
            "id": "org-lumiere",
            "name": "Lumière Cosmetics OY",
            "industry": "Cosmetics & Personal Care",
        },
        {
            "id": "org-pharma-demo",
            "name": "Pharma Demo Inc.",
            "industry": "Pharmaceuticals & Medical Devices",
        },
    ]


# ============================================================================ #
# Lumière Cosmetics Profile (Demo Company 1)                                  #
# ============================================================================ #


_LUMIERE_PROFILE: Dict[str, Any] = {
    "id": "org-lumiere",
    "name": "Lumière Cosmetics OY",
    "headquarters": "Helsinki, Finland",
    "industry": "Cosmetics & Personal Care",
    "size": "mid-market",  # <50 to 500 employees
    "risk_level": "high",  # Cosmetics + sensitive data = high regulatory exposure
    "established": 2015,
    "description": (
        "A Finnish EU cosmetics company manufacturing premium skincare products. "
        "Subjects to EC 1223/2009 (Cosmetics Regulation), EU 655/2013 (Claims), "
        "and GDPR for customer data including health/biometric information."
    ),
    "applicable_regulation_categories": [
        "EU Cosmetics Regulation (EC 1223/2009)",
        "Cosmetic Claims Regulation (EU 655/2013)",
        "General Data Protection Regulation (GDPR 2016/679)",
    ],
    "key_personnel": {
        "ceo": {"name": "Petri Halonen", "role": "Chief Executive Officer"},
        "general_counsel": {
            "name": "Mikael Vanhanen",
            "role": "General Counsel",
            "optional_at_meetings": False,  # legal should always attend strategic meetings
        },
        "data_protection_officer": {
            "name": "Anneli Saarinen",
            "role": "Data Protection Officer",
            "optional_at_meetings": False,  # DPO should attend if data handling is on agenda
        },
        "regulatory_affairs_manager": {
            "name": "Henrik Aalto",
            "role": "Regulatory Affairs Manager",
            "optional_at_meetings": True,
        },
        "r_and_d_director": {
            "name": "Dr. Lauri Rantanen",
            "role": "R&D Director",
            "optional_at_meetings": True,
        },
    },
    "legal_requirements": {
        "high_risk_decision_topics": [
            "Product claims and advertising",
            "Ingredient sourcing and restricted substances",
            "Data collection and processing",
            "Third-party data sharing",
            "Animal testing",
            "Regulatory notifications and compliance",
        ],
        "requires_legal_presence": [
            "Product safety assessments",
            "Marketing claims review",
            "Data handling and privacy decisions",
            "Restricted substance approvals",
            "New market entry decisions",
        ],
        "general_counsel_mandatory": True,
        "dpo_mandatory_if_data_topic": True,
    },
}


# ============================================================================ #
# Pharma Demo Profile (Demo Company 2 — placeholder for future)               #
# ============================================================================ #


_PHARMA_DEMO_PROFILE: Dict[str, Any] = {
    "id": "org-pharma-demo",
    "name": "Pharma Demo Inc.",
    "headquarters": "New Jersey, USA",
    "industry": "Pharmaceuticals & Medical Devices",
    "size": "large",
    "risk_level": "critical",  # Pharma = highest regulatory exposure
    "established": 2000,
    "description": (
        "A demonstration pharmaceutical and medical device company. "
        "Subjects to FDA regulations, EU pharmacovigilance, and GDPR."
    ),
    "applicable_regulation_categories": [
        "FDA Drug Approval & Manufacturing (CDER/CBER)",
        "EU Pharmacovigilance Directive",
        "General Data Protection Regulation (GDPR 2016/679)",
    ],
    "key_personnel": {
        "ceo": {"name": "Jane Smith", "role": "Chief Executive Officer"},
        "general_counsel": {
            "name": "Robert Chen",
            "role": "General Counsel",
            "optional_at_meetings": False,
        },
        "regulatory_affairs_director": {
            "name": "Dr. Maria Garcia",
            "role": "VP Regulatory Affairs",
            "optional_at_meetings": False,  # Regulatory leads most decisions
        },
    },
    "legal_requirements": {
        "high_risk_decision_topics": [
            "Drug formulation changes",
            "Clinical trial design",
            "Manufacturing facility changes",
            "Labeling and safety information",
            "Market authorization strategy",
        ],
        "requires_legal_presence": [
            "Clinical decision-making",
            "Manufacturing approval decisions",
            "Regulatory submission strategy",
            "Adverse event handling",
        ],
        "general_counsel_mandatory": True,
        "dpo_mandatory_if_data_topic": True,
    },
}


__all__ = [
    "get_company_profile",
    "list_companies",
]
