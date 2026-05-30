"""Decision categorizer for legal relevance assessment.

This module categorizes decisions by type and risk level, allowing the
orchestrator to assess whether specific legal/compliance personnel should
have been present at a meeting.

Decision categories are industry-agnostic; each category is mapped to
which types of expertise are relevant (legal, data protection, regulatory, etc.).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


# ============================================================================ #
# Decision Categories & Risk Levels                                           #
# ============================================================================ #

DECISION_CATEGORIES = {
    "product_claims": {
        "name": "Product Claims & Marketing",
        "description": "Marketing claims, product benefits, promotional messaging",
        "keywords": [
            "claim",
            "claim",
            "marketing",
            "advertise",
            "benefit",
            "efficacy",
            "skin",
            "anti-aging",
            "dermatolog",
        ],
        "requires_legal": True,
        "requires_regulatory": False,
        "requires_dpo": False,
        "risk_level": "high",
    },
    "data_processing": {
        "name": "Data Collection & Processing",
        "description": "Customer data handling, processing, consent, DPIA",
        "keywords": [
            "data",
            "processing",
            "consent",
            "dpia",
            "biometric",
            "health data",
            "personal data",
            "analysis",
        ],
        "requires_legal": True,
        "requires_regulatory": False,
        "requires_dpo": True,
        "risk_level": "critical",
    },
    "third_party_sharing": {
        "name": "Third-Party Data Sharing",
        "description": "Sharing customer data with external parties, partners, vendors",
        "keywords": [
            "share",
            "sharing",
            "third party",
            "partner",
            "vendor",
            "external",
            "transfer",
        ],
        "requires_legal": True,
        "requires_regulatory": False,
        "requires_dpo": True,
        "risk_level": "critical",
    },
    "ingredient_sourcing": {
        "name": "Ingredient Sourcing & Restrictions",
        "description": "Ingredient selection, restricted substances, safety assessments",
        "keywords": [
            "ingredient",
            "substance",
            "preservative",
            "restricted",
            "banned",
            "sourcing",
            "formulation",
            "safety",
        ],
        "requires_legal": True,
        "requires_regulatory": True,
        "requires_dpo": False,
        "risk_level": "high",
    },
    "animal_testing": {
        "name": "Animal Testing",
        "description": "Animal testing practices, bans, compliance",
        "keywords": [
            "animal test",
            "cruelty",
            "animal",
            "test",
            "testing",
        ],
        "requires_legal": True,
        "requires_regulatory": False,
        "requires_dpo": False,
        "risk_level": "high",
    },
    "regulatory_notification": {
        "name": "Regulatory Notification & Submission",
        "description": "Product notification, regulatory filings, CPNP submission",
        "keywords": [
            "notification",
            "filing",
            "cpnp",
            "regulatory",
            "submission",
            "echa",
        ],
        "requires_legal": True,
        "requires_regulatory": True,
        "requires_dpo": False,
        "risk_level": "high",
    },
    "manufacturing": {
        "name": "Manufacturing & Good Manufacturing Practice",
        "description": "GMP compliance, facility operations, production standards",
        "keywords": [
            "manufacturing",
            "gmp",
            "facility",
            "production",
            "quality",
            "inspection",
        ],
        "requires_legal": True,
        "requires_regulatory": True,
        "requires_dpo": False,
        "risk_level": "high",
    },
    "labeling": {
        "name": "Product Labeling & Packaging",
        "description": "Label content, warnings, compliance with regulations",
        "keywords": [
            "label",
            "labeling",
            "packaging",
            "warning",
            "instruction",
        ],
        "requires_legal": True,
        "requires_regulatory": False,
        "requires_dpo": False,
        "risk_level": "medium",
    },
    "general_business": {
        "name": "General Business Decision",
        "description": "General business matters without high compliance risk",
        "keywords": [
            "budget",
            "hiring",
            "meeting",
            "schedule",
            "timeline",
        ],
        "requires_legal": False,
        "requires_regulatory": False,
        "requires_dpo": False,
        "risk_level": "low",
    },
}


# ============================================================================ #
# Classification Functions                                                    #
# ============================================================================ #


def categorize_decision(
    decision_summary: str,
    decision_description: str = "",
) -> Dict[str, Any]:
    """Categorize a single decision by matching keywords to decision types.

    Args:
        decision_summary: Title or summary of the decision
        decision_description: Detailed description of the decision

    Returns:
        A dictionary with:
            - category: matched category key (e.g. 'product_claims')
            - category_name: human-readable name
            - risk_level: 'low', 'medium', 'high', or 'critical'
            - requires_legal: bool
            - requires_regulatory: bool
            - requires_dpo: bool
            - confidence: float 0.0-1.0 (how confident the match is)
            - matched_keywords: list of keywords that triggered the match
    """
    full_text = (decision_summary + " " + decision_description).lower()

    # Score each category based on keyword matches
    scores = {}
    for cat_key, cat_info in DECISION_CATEGORIES.items():
        matched = [kw for kw in cat_info["keywords"] if kw in full_text]
        if matched:
            scores[cat_key] = {
                "matched_keywords": matched,
                "score": len(matched),
            }

    if not scores:
        # Default to general business
        best_match = "general_business"
        confidence = 0.0
        matched_keywords = []
    else:
        best_match = max(scores, key=lambda k: scores[k]["score"])
        matched_keywords = scores[best_match]["matched_keywords"]
        # Confidence is based on proportion of category keywords matched
        total_keywords = len(DECISION_CATEGORIES[best_match]["keywords"])
        confidence = min(len(matched_keywords) / max(total_keywords, 1), 1.0)

    category_info = DECISION_CATEGORIES[best_match]
    return {
        "category": best_match,
        "category_name": category_info["name"],
        "risk_level": category_info["risk_level"],
        "requires_legal": category_info["requires_legal"],
        "requires_regulatory": category_info["requires_regulatory"],
        "requires_dpo": category_info["requires_dpo"],
        "confidence": confidence,
        "matched_keywords": matched_keywords,
    }


def categorize_decisions(
    decisions: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Categorize a list of decisions.

    Args:
        decisions: List of decision dicts with 'summary' and 'description' keys

    Returns:
        List of categorized decision dicts with all original fields plus
        the categorization results.
    """
    categorized = []
    for decision in decisions:
        summary = decision.get("summary", "")
        description = decision.get("description", "")
        category_result = categorize_decision(summary, description)
        categorized.append({**decision, **category_result})
    return categorized


def determine_legal_requirements(
    company_profile: Dict[str, Any],
    categorized_decisions: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Determine whether a lawyer should have been present at the meeting.

    Combines company risk level and decision categories to assess if legal
    personnel should have attended.

    Args:
        company_profile: Company context from company_context.py
        categorized_decisions: List of decisions with categorization data

    Returns:
        A dictionary with:
            - should_have_lawyer: bool
            - lawyer_mandatory: bool (always required for this company)
            - relevant_personnel: list of roles required
            - reason: explanation of assessment
            - high_risk_decisions: list of decisions that require legal
    """
    legal_requirements = company_profile.get("legal_requirements", {})
    risk_level = company_profile.get("risk_level", "medium")

    requires_legal = legal_requirements.get("general_counsel_mandatory", False)
    relevant_personnel = []
    high_risk_decisions = []

    # Check if any decision requires legal involvement
    for decision in categorized_decisions:
        if decision.get("requires_legal"):
            requires_legal = True
            high_risk_decisions.append(decision)
            if "Legal/General Counsel" not in relevant_personnel:
                relevant_personnel.append("Legal/General Counsel")

        if decision.get("requires_dpo") and legal_requirements.get(
            "dpo_mandatory_if_data_topic"
        ):
            if "Data Protection Officer" not in relevant_personnel:
                relevant_personnel.append("Data Protection Officer")

        if decision.get("requires_regulatory"):
            if "Regulatory Affairs Manager" not in relevant_personnel:
                relevant_personnel.append("Regulatory Affairs Manager")

    # Assess based on company risk level
    if risk_level == "critical":
        requires_legal = True
        if "Legal/General Counsel" not in relevant_personnel:
            relevant_personnel.append("Legal/General Counsel")

    reason = ""
    if not requires_legal:
        reason = "No high-risk decisions identified; general business meeting."
    else:
        decision_topics = [d.get("category_name") for d in high_risk_decisions]
        reason = (
            f"Company risk level: {risk_level}. Decisions include: "
            f"{', '.join(set(decision_topics))}. Legal expertise required."
        )

    return {
        "should_have_lawyer": requires_legal,
        "lawyer_mandatory": legal_requirements.get(
            "general_counsel_mandatory", False
        ),
        "relevant_personnel": relevant_personnel,
        "reason": reason,
        "high_risk_decisions": high_risk_decisions,
    }


__all__ = [
    "DECISION_CATEGORIES",
    "categorize_decision",
    "categorize_decisions",
    "determine_legal_requirements",
]
