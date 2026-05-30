"""Fake meeting fixtures for the multi-agent compliance demo.

Scenarios:

1. ``meeting-glow-001`` — Glow Sérum product launch (7 decisions).  Covers
   Claims 655/2013, Cosmetics Art 10/13/18/20, GDPR Art 9/28/35/44.

2. ``meeting-glow-002`` — Glow Sérum production & go-to-market (10 decisions).
   Exercises regulations NOT triggered by meeting-001 (GMP, restricted
   substances, labelling, consent, privacy-by-design, lawful basis,
   transparency, honesty, fairness).  Touches ALL 7 departments, all 5 past
   cases, all 5 internal policies, and all 4 legal opinions so that every
   tool and every agent is fully exercised.
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
        "initiated_by": {
            "name": "Petri Halonen",
            "email": "petri.halonen@lumiere.example",
        },
    },
    {
        "id": "meeting-glow-002",
        "title": "Glow Sérum Production & Go-to-Market — Full Readiness Review",
        "date": "2026-05-22",
        "duration_minutes": 110,
        "participants": [
            "Petri Halonen (CEO)",
            "Marja Nieminen (Head of Marketing)",
            "Dr. Lauri Rantanen (R&D Director)",
            "Iina Mäkinen (Data & Digital Lead)",
            "Henrik Aalto (Regulatory Affairs Manager)",
            "Sanna Heikkilä (Head of Procurement)",
            "Mikael Vanhanen (General Counsel)",
            "Anneli Saarinen (DPO)",
        ],
        "organization_id": "org-lumiere",
        "summary": (
            "Full readiness review for Glow Sérum production ramp and market "
            "launch.  Reviewed manufacturing facility GMP status, a restricted "
            "preservative in the formulation, incomplete PIF, packaging "
            "labelling defects, exaggerated and unfair marketing claims, "
            "pharmacy skin-scan consent design, Glow-app data-minimisation "
            "architecture, lawful-basis mapping, and privacy-notice readiness."
        ),
        "decision_ids": [
            "decision-glow-101",
            "decision-glow-102",
            "decision-glow-103",
            "decision-glow-104",
            "decision-glow-105",
            "decision-glow-106",
            "decision-glow-107",
            "decision-glow-108",
            "decision-glow-109",
            "decision-glow-110",
        ],
        "initiated_by": {
            "name": "Henrik Aalto",
            "email": "henrik.aalto@lumiere.example",
        },
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
    ],

    # ------------------------------------------------------------------ #
    # Meeting 2 — comprehensive scenario (10 decisions, wide coverage)   #
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
            "speaker": "Henrik Aalto (Regulatory Affairs Manager)",
            "text": (
                "On labelling — the first print run of the outer packaging "
                "has already been produced. I reviewed it and noticed the INCI "
                "ingredient list is missing entirely, there is no batch number "
                "field, and the PAO symbol was left off. Reprinting will cost "
                "fifteen thousand euros and delay us two weeks. I suggest we "
                "ship the first batch with the existing packaging and correct "
                "it in the next print run."
            ),
        },
        {
            "speaker": "Marja Nieminen (Head of Marketing)",
            "text": (
                "For the digital campaign, we want to position Glow Sérum as "
                "'the only anti-aging sérum that actually works'. We will say "
                "'unlike other brands that make empty promises, Glow Sérum "
                "delivers real results'. This will be on our Instagram, "
                "TikTok, and the product website."
            ),
        },
        {
            "speaker": "Marja Nieminen (Head of Marketing)",
            "text": (
                "We are also partnering with a chain of pharmacies for an "
                "in-store skin scanning promotion. Customers get a free skin "
                "scan, and their data goes into our loyalty programme. The "
                "sign-up form has a pre-ticked checkbox that says 'I consent "
                "to Lumière processing my personal data for marketing and "
                "product development purposes'. We bundle the marketing "
                "consent with the loyalty sign-up so it is one simple step."
            ),
        },
        {
            "speaker": "Iina Mäkinen (Data & Digital Lead)",
            "text": (
                "For the Glow app version two, the approach is to collect "
                "everything we can from the user upfront — full name, address, "
                "date of birth, purchase history, skin photos, health answers, "
                "location data, browsing behaviour — and we will figure out "
                "later which data points we actually need for personalisation. "
                "Better to have the data and not need it than to need it and "
                "not have it."
            ),
        },
        {
            "speaker": "Anneli Saarinen (DPO)",
            "text": (
                "I want to formally note for the record that I have not been "
                "consulted on the Glow app data architecture, the pharmacy "
                "sign-up form, or the US data sharing arrangement. The current "
                "privacy notice on the app does not mention the skin photo "
                "processing, the health questionnaire, the loyalty programme, "
                "or the US transfer. We need to update it before launch."
            ),
        },
        {
            "speaker": "Petri Halonen (CEO)",
            "text": (
                "Anneli, I hear you, but we cannot afford another delay. "
                "Update the privacy notice after launch. Iina, proceed with "
                "the data collection as planned. Marja, the campaign copy is "
                "approved. Henrik, ship with the existing packaging. Everyone, "
                "we launch on June first. No more changes."
            ),
        },
        {
            "speaker": "Mikael Vanhanen (General Counsel)",
            "text": (
                "For the record, I want to note that several of these "
                "decisions carry significant legal risk. I will prepare a "
                "risk memo for the board, but I understand the business "
                "decision is to proceed."
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

    # ------------------------------------------------------------------ #
    # Meeting 2 decisions (10 new — wide regulation coverage)            #
    #                                                                    #
    # 101 → EU-COSM-ART8  (GMP)               [HIGH]     mfg/QA        #
    # 102 → EU-COSM-ART14 (restricted subst.)  [CRITICAL] R&D/proc      #
    # 103 → EU-COSM-ART11 (PIF incomplete)     [MEDIUM]   reg affairs   #
    # 104 → EU-COSM-ART19 (labelling)          [LOW]      pkg/reg       #
    # 105 → CLAIM-CRIT4   (honesty)            [MEDIUM]   marketing     #
    # 106 → CLAIM-CRIT5   (fairness)           [LOW]      marketing     #
    # 107 → GDPR-ART7     (consent)            [HIGH]     DPO/dig/mkt   #
    # 108 → GDPR-ART25    (privacy by design)  [MEDIUM]   DPO/digital   #
    # 109 → GDPR-ART6     (lawful basis)       [HIGH]     DPO           #
    # 110 → GDPR-ART13    (transparency)       [MEDIUM]   DPO/legal     #
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
    {
        "id": "decision-glow-104",
        "meeting_id": "meeting-glow-002",
        "title": "Ship first batch with packaging missing INCI list, batch number, and PAO",
        "context": (
            "The first print run of outer packaging is missing the INCI "
            "ingredient list, has no batch number field, and the PAO (Period "
            "After Opening) symbol was omitted. Rather than reprint (EUR 15k, "
            "2-week delay), the team decided to ship with the defective "
            "packaging and correct in the next print run."
        ),
        "category": "Labelling",
    },
    {
        "id": "decision-glow-105",
        "meeting_id": "meeting-glow-002",
        "title": "Claim 'the only anti-aging sérum that actually works'",
        "context": (
            "Marketing wants to use 'the only anti-aging sérum that actually "
            "works' as the lead digital campaign message. There is no evidence "
            "that no other product in the market is effective, and the claim "
            "attributes unique characteristics without substantiation."
        ),
        "category": "Marketing Claims",
    },
    {
        "id": "decision-glow-106",
        "meeting_id": "meeting-glow-002",
        "title": "Run campaign denigrating competitor products",
        "context": (
            "The digital advertising copy includes the statement 'unlike other "
            "brands that make empty promises, Glow Sérum delivers real "
            "results'. This directly denigrates competing cosmetic products."
        ),
        "category": "Marketing Claims",
    },
    {
        "id": "decision-glow-107",
        "meeting_id": "meeting-glow-002",
        "title": "Use pre-ticked bundled consent checkbox for pharmacy promotion",
        "context": (
            "The in-store pharmacy sign-up form uses a pre-ticked checkbox "
            "that bundles marketing consent with loyalty programme sign-up. "
            "Customers cannot join the loyalty programme without also "
            "consenting to marketing and product-development data use."
        ),
        "category": "Data Protection",
    },
    {
        "id": "decision-glow-108",
        "meeting_id": "meeting-glow-002",
        "title": "Collect all available user data upfront with no data minimisation",
        "context": (
            "The Glow app v2 will collect full name, address, date of birth, "
            "purchase history, skin photos, health answers, location data, "
            "and browsing behaviour at sign-up before determining which data "
            "points are actually needed. The stated approach is 'collect "
            "everything and decide later'."
        ),
        "category": "Data Protection",
    },
    {
        "id": "decision-glow-109",
        "meeting_id": "meeting-glow-002",
        "title": "Process skin-scan and loyalty data without defined lawful basis",
        "context": (
            "The pharmacy skin-scan promotion and loyalty programme will "
            "process customer personal data (including skin-scan results) "
            "without a documented lawful basis under GDPR Article 6. No "
            "assessment has been done of which legal ground applies."
        ),
        "category": "Data Protection",
    },
    {
        "id": "decision-glow-110",
        "meeting_id": "meeting-glow-002",
        "title": "Delay privacy notice update until after launch",
        "context": (
            "The DPO noted that the current privacy notice does not mention "
            "skin-photo processing, the health questionnaire, the loyalty "
            "programme, or the US data transfer. The CEO decided to update "
            "the privacy notice after launch, meaning personal data will be "
            "collected without required transparency information."
        ),
        "category": "Data Protection",
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


def get_meeting_initiator(meeting_id: str) -> Optional[Dict[str, str]]:
    """Return the initiator (name and email) of a meeting, or None."""
    meeting = get_meeting(meeting_id)
    if meeting is None:
        return None
    return meeting.get("initiated_by")


__all__ = [
    "COMPANY",
    "MEETING_RECORDS",
    "TRANSCRIPTS",
    "DECISIONS",
    "get_meeting",
    "get_transcript",
    "list_decisions",
    "get_decision",
    "get_meeting_initiator",
]
