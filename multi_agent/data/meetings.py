"""Fake meeting fixtures for the multi-agent compliance demo.

Scenario: Lumière Cosmetics is preparing to launch a new anti-aging product
("Glow Sérum"). The product-launch meeting contains seven decisions that each
trigger a different EU regulatory issue, ranging from GDPR special-category
data (Critical) to minor labelling (Low).

This is the ONLY meeting record in v1. The structure mirrors the
`meeting_data.py` schema used elsewhere in the repo so it stays familiar.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


COMPANY = {
    "id": "org-lumiere",
    "name": "Lumière Cosmetics OY",
    "industry": "Cosmetics & Personal Care",
    "headquarters": "Helsinki, Finland",
    "data_protection_officer": "Anneli Saarinen",
}


MEETING_RECORDS: List[Dict[str, Any]] = [
    {
        "id": "meeting-glow-001",
        "title": "Glow Sérum Product Launch - Go/No-Go Review",
        "date": "2026-05-18",
        "duration_minutes": 75,
        "participants": [
            "Petri Halonen (CEO)",
            "Marja Nieminen (Head of Marketing)",
            "Dr. Lauri Rantanen (R&D Director)",
            "Iina Mäkinen (Data & Digital Lead)",
            "Henrik Aalto (Regulatory Affairs Manager)",
        ],
        "organization_id": "org-lumiere",
        "summary": (
            "Final go/no-go review for the Glow Sérum anti-aging line. The team "
            "discussed marketing claims, ingredient sourcing, the new AI skin-"
            "analysis app, third-party data sharing, animal-testing claims, and "
            "regulatory notification."
        ),
        "decision_ids": [
            "decision-glow-001",
            "decision-glow-002",
            "decision-glow-003",
            "decision-glow-004",
            "decision-glow-005",
            "decision-glow-006",
            "decision-glow-007",
        ],
    }
]


TRANSCRIPTS: Dict[str, List[Dict[str, str]]] = {
    "meeting-glow-001": [
        {
            "speaker": "Petri Halonen (CEO)",
            "text": (
                "Let's keep this short. We need to launch Glow Sérum in eight "
                "weeks to hit the back-to-school season. Marja, walk us through "
                "the marketing claims."
            ),
        },
        {
            "speaker": "Marja Nieminen (Head of Marketing)",
            "text": (
                "The lead claim is 'clinically proven to reduce wrinkles by 80%'. "
                "We ran a small internal panel of twelve people, our R&D team "
                "scored the photos, and the results looked very positive. We "
                "want this on the front of the box."
            ),
        },
        {
            "speaker": "Dr. Lauri Rantanen (R&D Director)",
            "text": (
                "Just to flag - we are also adding a new peptide complex from a "
                "supplier in Shanghai. The supplier provided their own data "
                "sheet but we have not done the full cosmetic product safety "
                "report yet. I think we can launch first and finalise the CPSR "
                "in the next quarter."
            ),
        },
        {
            "speaker": "Marja Nieminen (Head of Marketing)",
            "text": (
                "We also want to put '100% Natural & Organic' on the label. "
                "Our formulation is mostly natural - we don't have COSMOS or "
                "Ecocert certification but I think we can still use the claim "
                "because it's a strong message for consumers."
            ),
        },
        {
            "speaker": "Iina Mäkinen (Data & Digital Lead)",
            "text": (
                "On the digital side, we are launching the Glow companion app. "
                "Users upload a selfie and answer a short health questionnaire "
                "- skin conditions, allergies, hormonal changes, current "
                "medications - and we use AI to recommend a personalised "
                "routine. We capture and store the skin photos so the model "
                "can improve over time."
            ),
        },
        {
            "speaker": "Iina Mäkinen (Data & Digital Lead)",
            "text": (
                "We also want to share the aggregated customer data with our "
                "US marketing analytics partner in California. They will help "
                "us segment audiences and optimise ad spend. We have an "
                "informal arrangement with them - no signed data processing "
                "agreement yet."
            ),
        },
        {
            "speaker": "Marja Nieminen (Head of Marketing)",
            "text": (
                "And we should definitely add 'Cruelty-Free, Not Tested on "
                "Animals' to the box. It's a key differentiator in this segment."
            ),
        },
        {
            "speaker": "Dr. Lauri Rantanen (R&D Director)",
            "text": (
                "Quick caveat there - the Shanghai supplier confirmed they "
                "tested the new peptide on rabbits as part of their domestic "
                "regulatory submission in China. That's outside our control, "
                "but the ingredient itself was animal-tested."
            ),
        },
        {
            "speaker": "Henrik Aalto (Regulatory Affairs Manager)",
            "text": (
                "One more thing - since the formulation has changed (the new "
                "peptide complex), we technically need to re-notify CPNP. To "
                "save time and avoid the review delay, I propose we ship the "
                "first batch under the existing notification and re-notify "
                "after launch."
            ),
        },
        {
            "speaker": "Petri Halonen (CEO)",
            "text": (
                "Approved on all counts. Let's move fast. Henrik, please draft "
                "the actions and we'll review on Monday."
            ),
        },
    ]
}


DECISIONS: List[Dict[str, Any]] = [
    {
        "id": "decision-glow-001",
        "meeting_id": "meeting-glow-001",
        "title": "Use 'clinically proven 80% wrinkle reduction' claim",
        "context": (
            "Marketing wants to lead with 'clinically proven to reduce wrinkles "
            "by 80%' based on a small internal twelve-person panel scored by "
            "the company's own R&D team. The claim will appear on packaging "
            "and in advertising."
        ),
        "category": "Marketing Claims",
    },
    {
        "id": "decision-glow-002",
        "meeting_id": "meeting-glow-001",
        "title": "Launch with new peptide from non-EU supplier before CPSR",
        "context": (
            "A novel peptide complex sourced from a supplier in Shanghai will "
            "be included in the formulation. The Cosmetic Product Safety "
            "Report has not been completed; R&D proposes to finalise it after "
            "market launch."
        ),
        "category": "Product Safety",
    },
    {
        "id": "decision-glow-003",
        "meeting_id": "meeting-glow-001",
        "title": "Use '100% Natural & Organic' label without certification",
        "context": (
            "Marketing wants '100% Natural & Organic' on the front-of-pack "
            "despite the absence of COSMOS, Ecocert or equivalent third-party "
            "certification of the formulation."
        ),
        "category": "Marketing Claims",
    },
    {
        "id": "decision-glow-004",
        "meeting_id": "meeting-glow-001",
        "title": "Collect skin photos and health questionnaires via Glow app",
        "context": (
            "The Glow companion app will collect customer selfies (used for AI "
            "skin analysis), and a health questionnaire covering skin "
            "conditions, allergies, hormonal status and current medications, "
            "stored for ongoing model training. No DPIA has been conducted."
        ),
        "category": "Data Protection",
    },
    {
        "id": "decision-glow-005",
        "meeting_id": "meeting-glow-001",
        "title": "Share customer data with US marketing analytics partner",
        "context": (
            "Aggregated customer data will be shared with a California-based "
            "marketing analytics firm for audience segmentation, under an "
            "informal arrangement and without a signed Data Processing "
            "Agreement or Transfer Impact Assessment."
        ),
        "category": "Data Protection",
    },
    {
        "id": "decision-glow-006",
        "meeting_id": "meeting-glow-001",
        "title": "Use 'Cruelty-Free, Not Tested on Animals' claim",
        "context": (
            "Marketing wants to label the product 'Cruelty-Free, Not Tested on "
            "Animals'. R&D disclosed in the same meeting that the Shanghai "
            "supplier conducted in vivo testing on rabbits for the new peptide "
            "as part of its domestic Chinese regulatory submission."
        ),
        "category": "Marketing Claims / Animal Testing",
    },
    {
        "id": "decision-glow-007",
        "meeting_id": "meeting-glow-001",
        "title": "Skip CPNP re-notification for reformulated product",
        "context": (
            "Although the formulation has materially changed (new peptide "
            "complex), Regulatory Affairs proposes to ship the first batch "
            "under the existing CPNP notification and re-notify only after "
            "launch, in order to avoid the review delay."
        ),
        "category": "Regulatory",
    },
]


# Convenience lookups -------------------------------------------------------


def get_meeting(meeting_id: str) -> Optional[Dict[str, Any]]:
    for record in MEETING_RECORDS:
        if record["id"] == meeting_id:
            return record
    return None


def get_transcript(meeting_id: str) -> Optional[List[Dict[str, str]]]:
    return TRANSCRIPTS.get(meeting_id)


def list_decisions(meeting_id: Optional[str] = None) -> List[Dict[str, Any]]:
    if meeting_id is None:
        return list(DECISIONS)
    return [d for d in DECISIONS if d["meeting_id"] == meeting_id]


def get_decision(decision_id: str) -> Optional[Dict[str, Any]]:
    for decision in DECISIONS:
        if decision["id"] == decision_id:
            return decision
    return None


__all__ = [
    "COMPANY",
    "MEETING_RECORDS",
    "TRANSCRIPTS",
    "DECISIONS",
    "get_meeting",
    "get_transcript",
    "list_decisions",
    "get_decision",
]
