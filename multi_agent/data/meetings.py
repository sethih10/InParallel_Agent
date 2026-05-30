"""Fake meeting fixtures for the multi-agent compliance demo.

Scenarios:

1. ``meeting-glow-001`` — Glow Sérum product launch (3 decisions).  Covers
   Claims 655/2013, Cosmetics Art 10/13, GDPR Art 9/28/35/44.

2. ``meeting-glow-002`` — Glow Sérum production & go-to-market (3 decisions).
   Exercises GMP, restricted substances, and consent regulations.
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
            "discussed marketing claims and the new AI skin-analysis app."
        ),
        "decision_ids": [
            "decision-glow-001",
            "decision-glow-002",
            "decision-glow-003",
        ],
    },
    {
        "id": "meeting-glow-002",
        "title": "Glow Sérum Production & Go-to-Market — Full Readiness Review",
        "date": "2026-05-22",
        "duration_minutes": 45,
        "participants": [
            "Petri Halonen (CEO)",
            "Dr. Lauri Rantanen (R&D Director)",
            "Sanna Heikkilä (Head of Procurement)",
            "Henrik Aalto (Regulatory Affairs Manager)",
        ],
        "organization_id": "org-lumiere",
        "summary": (
            "Full readiness review for Glow Sérum production ramp and market "
            "launch. Reviewed manufacturing facility GMP status, a restricted "
            "preservative in the formulation, and incomplete PIF documentation."
        ),
        "decision_ids": [
            "decision-glow-101",
            "decision-glow-102",
            "decision-glow-103",
        ],
    },
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
            "speaker": "Petri Halonen (CEO)",
            "text": (
                "Approved on all counts. Let's move fast. Henrik, please draft "
                "the actions and we'll review on Monday."
            ),
        },
    ],

    # ------------------------------------------------------------------ #
    # Meeting 2 — production readiness (3 decisions)                     #
    # ------------------------------------------------------------------ #
    "meeting-glow-002": [
        {
            "speaker": "Petri Halonen (CEO)",
            "text": (
                "Good morning everyone. This is the full readiness review "
                "before we commit to production. I want every department lead "
                "to flag anything that is not ready. Lauri, start with "
                "manufacturing."
            ),
        },
        {
            "speaker": "Dr. Lauri Rantanen (R&D Director)",
            "text": (
                "We have secured production capacity at the new contract "
                "manufacturer in Tallinn. They are keen to start but they "
                "have not completed their ISO 22716 GMP audit yet. They say "
                "it will happen next quarter. I think we can go ahead and "
                "manufacture the first batch there now and audit later."
            ),
        },
        {
            "speaker": "Sanna Heikkilä (Head of Procurement)",
            "text": (
                "On ingredients, I need to flag something. The new preservative "
                "blend from our Italian supplier contains methylisothiazolinone "
                "at 0.02 percent. I checked and the Annex III limit for "
                "rinse-off products is 0.0015 percent. Our product is a "
                "leave-on sérum, so technically MIT should not be present at "
                "all in a leave-on formulation. Lauri says we can dilute in a "
                "later batch but for now we proceed as is."
            ),
        },
        {
            "speaker": "Dr. Lauri Rantanen (R&D Director)",
            "text": (
                "Correct, we will address the MIT concentration in batch two. "
                "Also on documentation — the Product Information File is not "
                "fully assembled yet. We are missing the stability data and "
                "the toxicological profile for two ingredients. I would rather "
                "not delay the launch for paperwork."
            ),
        },
        {
            "speaker": "Petri Halonen (CEO)",
            "text": (
                "Understood. Let's proceed with production and complete the "
                "documentation after launch. We launch on June first."
            ),
        },
    ],
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
        "title": "Use '100% Natural & Organic' label without certification",
        "context": (
            "Marketing wants '100% Natural & Organic' on the front-of-pack "
            "despite the absence of COSMOS, Ecocert or equivalent third-party "
            "certification of the formulation."
        ),
        "category": "Marketing Claims",
    },
    {
        "id": "decision-glow-003",
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

    # ------------------------------------------------------------------ #
    # Meeting 2 decisions (3 — production readiness)                     #
    # ------------------------------------------------------------------ #
    {
        "id": "decision-glow-101",
        "meeting_id": "meeting-glow-002",
        "title": "Manufacture first batch at facility without GMP audit",
        "context": (
            "The Tallinn contract manufacturer has not yet completed its "
            "ISO 22716 Good Manufacturing Practice audit. R&D proposes to "
            "begin production immediately and schedule the audit for next "
            "quarter."
        ),
        "category": "Manufacturing / Quality",
    },
    {
        "id": "decision-glow-102",
        "meeting_id": "meeting-glow-002",
        "title": "Use preservative blend with restricted methylisothiazolinone in leave-on product",
        "context": (
            "The preservative blend from the Italian supplier contains MIT "
            "(methylisothiazolinone) at 0.02%, which exceeds the Annex III "
            "limit of 0.0015% for rinse-off products. MIT is prohibited in "
            "leave-on products entirely. The Glow Sérum is a leave-on product. "
            "The team agreed to proceed and correct in batch two."
        ),
        "category": "Product Safety / Restricted Substances",
    },
    {
        "id": "decision-glow-103",
        "meeting_id": "meeting-glow-002",
        "title": "Launch without complete Product Information File",
        "context": (
            "The PIF is missing stability data and the toxicological profile "
            "for two ingredients. R&D proposes to launch without the complete "
            "PIF and finish the documentation post-launch."
        ),
        "category": "Regulatory Documentation",
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
