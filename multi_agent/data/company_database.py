"""Fake company knowledge base for the Legal Research agent.

Contains four collections, all stored as in-memory lists/dicts:

    PAST_CASES         - prior compliance incidents the company has handled,
                         including outcome and resolution notes
    INTERNAL_POLICIES  - company-issued policies / SOPs
    LEGAL_OPINIONS     - external counsel opinions referenced internally
    DEPARTMENT_DIRECTORY - who owns which compliance topic

All records carry a unique ``id`` (e.g. ``case-2024-001``) that the agent
cites as evidence in the final report.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional


# --------------------------------------------------------------------------- #
# Past cases / incidents                                                      #
# --------------------------------------------------------------------------- #

PAST_CASES: List[Dict[str, Any]] = [
    {
        "id": "case-2024-001",
        "year": 2024,
        "title": "Finnish DPA warning - skin analysis data processing",
        "regulation_ids": ["GDPR-ART9", "GDPR-ART35"],
        "summary": (
            "The Finnish Data Protection Ombudsman (Tietosuojavaltuutettu) "
            "issued a formal warning to Lumière for processing customer skin "
            "condition data through an earlier diagnostic feature without a "
            "DPIA and without explicit Article 9 consent."
        ),
        "outcome": "Warning + 14-day remediation order. No fine.",
        "resolution_notes": (
            "Conducted DPIA within 10 days; rebuilt consent flow with separate, "
            "granular opt-in for health data; appointed dedicated DPO contact; "
            "published transparent privacy notice. Ombudsman closed the case."
        ),
        "tags": ["GDPR", "health data", "DPIA", "skin", "biometric", "consent"],
    },
    {
        "id": "case-2025-002",
        "year": 2025,
        "title": "Consumer authority challenged 'dermatologically tested' claim",
        "regulation_ids": ["EU-COSM-ART20", "CLAIM-CRIT3"],
        "summary": (
            "The Finnish Consumer Authority (KKV) challenged a 'dermatologically "
            "tested' claim used on the Pure Hydration line on grounds of "
            "insufficient evidential support."
        ),
        "outcome": "Voluntary claim withdrawal + advertising correction. No fine.",
        "resolution_notes": (
            "Commissioned an independent dermatological study with 60 subjects "
            "via SGS; updated packaging to 'dermatologically tested on 60 "
            "subjects'; created Claims Substantiation SOP (POL-MKT-002)."
        ),
        "tags": ["claims", "evidence", "marketing", "dermatologically tested", "substantiation"],
    },
    {
        "id": "case-2023-003",
        "year": 2023,
        "title": "Internal audit finding - supplier safety documentation gap",
        "regulation_ids": ["EU-COSM-ART10", "EU-COSM-ART11"],
        "summary": (
            "Internal audit found that two ingredient suppliers had not "
            "provided complete safety dossiers and the Product Information "
            "Files for three SKUs were incomplete."
        ),
        "outcome": "Internal finding. No external enforcement action.",
        "resolution_notes": (
            "Halted use of affected ingredients for 6 weeks; commissioned full "
            "CPSRs from external safety assessor (Eurofins); updated Supplier "
            "Due Diligence Policy (POL-PROC-001); added pre-launch PIF gate."
        ),
        "tags": ["safety", "PIF", "CPSR", "supplier", "ingredient", "documentation"],
    },
    {
        "id": "case-2024-004",
        "year": 2024,
        "title": "US ad-tech vendor terminated after Schrems II review",
        "regulation_ids": ["GDPR-ART28", "GDPR-ART44"],
        "summary": (
            "Internal Schrems II review identified that an existing US ad-tech "
            "vendor lacked adequate safeguards for personal data transferred "
            "from EU customers."
        ),
        "outcome": "Vendor relationship terminated; transfers ceased.",
        "resolution_notes": (
            "Conducted Transfer Impact Assessment (TIA); attempted SCC "
            "renegotiation with supplementary measures (encryption-in-use, "
            "pseudonymisation); concluded measures insufficient given vendor's "
            "FISA 702 exposure; migrated workload to EU-based vendor."
        ),
        "tags": ["GDPR", "international transfer", "Schrems II", "US", "SCC", "TIA"],
    },
    {
        "id": "case-2022-005",
        "year": 2022,
        "title": "Influencer used unverified 'natural' claim on social media",
        "regulation_ids": ["CLAIM-CRIT2"],
        "summary": (
            "An influencer partner posted a video stating Lumière's Botanica "
            "line was '100% natural and organic'. The product had no "
            "certification."
        ),
        "outcome": "Voluntary takedown + influencer guidelines updated.",
        "resolution_notes": (
            "Removed posts within 48h; issued Influencer Compliance Guidelines "
            "(POL-MKT-003); required pre-approval of all on-pack and on-air "
            "claims; ran mandatory training for marketing team."
        ),
        "tags": ["claims", "natural", "organic", "influencer", "social media"],
    },
]


# --------------------------------------------------------------------------- #
# Internal policies / SOPs                                                    #
# --------------------------------------------------------------------------- #

INTERNAL_POLICIES: List[Dict[str, Any]] = [
    {
        "id": "POL-DPO-001",
        "title": "Lumière Data Protection & Privacy Policy",
        "version": "2.1",
        "last_updated": "2025-02-12",
        "owner_department": "Data Protection Office",
        "summary": (
            "Master policy for personal data handling. Covers lawful basis "
            "selection, consent management, retention, data subject rights, "
            "incident response. Section 6 addresses international transfers "
            "but is acknowledged to have gaps post-Schrems II."
        ),
        "regulation_ids": ["GDPR-ART6", "GDPR-ART7", "GDPR-ART13", "GDPR-ART44"],
        "tags": ["GDPR", "privacy", "consent", "transfers", "retention"],
    },
    {
        "id": "POL-MKT-002",
        "title": "Marketing Claims Substantiation SOP",
        "version": "1.3",
        "last_updated": "2025-09-30",
        "owner_department": "Marketing",
        "summary": (
            "Required process before any new marketing claim is approved: "
            "evidence package, sample size guidance, sign-off by Regulatory "
            "Affairs. Created after case-2025-002. Forbids the words "
            "'clinically proven' without external study."
        ),
        "regulation_ids": ["EU-COSM-ART20", "CLAIM-CRIT3", "CLAIM-CRIT4"],
        "tags": ["claims", "marketing", "evidence", "substantiation", "approval"],
    },
    {
        "id": "POL-RND-001",
        "title": "Product Safety Assessment Procedure",
        "version": "3.0",
        "last_updated": "2025-06-20",
        "owner_department": "R&D / Product Safety",
        "summary": (
            "Mandates that a Cosmetic Product Safety Report (CPSR) signed by a "
            "qualified safety assessor must be on file before CPNP "
            "notification and before any market launch. Includes a pre-launch "
            "PIF gate added after case-2023-003."
        ),
        "regulation_ids": ["EU-COSM-ART3", "EU-COSM-ART10", "EU-COSM-ART11"],
        "tags": ["safety", "CPSR", "PIF", "pre-launch", "assessor"],
    },
    {
        "id": "POL-PROC-001",
        "title": "Supplier Due Diligence & Compliance Policy",
        "version": "1.5",
        "last_updated": "2024-11-05",
        "owner_department": "Procurement / Regulatory Affairs",
        "summary": (
            "Requires written confirmation from every ingredient supplier that "
            "(a) no animal testing was conducted on the ingredient by the "
            "supplier or any third party for cosmetic purposes and (b) full "
            "safety dossier is provided before purchase order."
        ),
        "regulation_ids": ["EU-COSM-ART10", "EU-COSM-ART18", "CLAIM-CRUELTY-FREE"],
        "tags": ["supplier", "animal testing", "safety", "due diligence", "ingredient"],
    },
    {
        "id": "POL-REG-001",
        "title": "CPNP Notification & Reformulation Procedure",
        "version": "1.1",
        "last_updated": "2024-08-14",
        "owner_department": "Regulatory Affairs",
        "summary": (
            "Specifies when re-notification is required after a formulation "
            "change (any change to a substance present at >1% w/w, or any "
            "change in CMR/restricted substance content) and forbids placing "
            "a re-notifiable product on market until the new notification is "
            "submitted."
        ),
        "regulation_ids": ["EU-COSM-ART13"],
        "tags": ["CPNP", "notification", "reformulation", "regulatory"],
    },
]


# --------------------------------------------------------------------------- #
# External legal opinions                                                     #
# --------------------------------------------------------------------------- #

LEGAL_OPINIONS: List[Dict[str, Any]] = [
    {
        "id": "opinion-2024-001",
        "year": 2024,
        "title": "International data transfers post EU-US Data Privacy Framework",
        "author": "Borenius Attorneys, Helsinki",
        "regulation_ids": ["GDPR-ART44", "GDPR-ART28"],
        "summary": (
            "Confirms the EU-US Data Privacy Framework provides an adequacy "
            "decision but only for vendors self-certified under the framework. "
            "Recommends maintaining SCCs as a fallback and conducting a "
            "Transfer Impact Assessment regardless of certification status."
        ),
        "recommended_actions": [
            "Verify vendor self-certification on the DPF list",
            "Maintain SCCs as fallback safeguard",
            "Always conduct and document a Transfer Impact Assessment",
            "Execute a signed Data Processing Agreement before any transfer",
        ],
        "tags": ["GDPR", "international transfer", "DPF", "SCC", "US", "TIA"],
    },
    {
        "id": "opinion-2025-002",
        "year": 2025,
        "title": "Permissible use of 'natural' and 'organic' in cosmetics",
        "author": "Roschier Attorneys, Helsinki",
        "regulation_ids": ["CLAIM-CRIT2", "CLAIM-CRIT3"],
        "summary": (
            "Concludes that '100% Natural' and '100% Organic' claims should be "
            "substantiated by an external certification (COSMOS, Ecocert, "
            "NaTrue) or by detailed ingredient documentation showing every "
            "input meets the ISO 16128 natural-origin definition."
        ),
        "recommended_actions": [
            "Obtain COSMOS or Ecocert certification before using '100% Organic'",
            "If certification is not available, replace with substantiated terms "
            "(e.g. 'with X% natural-origin ingredients per ISO 16128')",
            "Document the natural-origin index for every ingredient",
        ],
        "tags": ["claims", "natural", "organic", "COSMOS", "Ecocert", "ISO 16128"],
    },
    {
        "id": "opinion-2024-003",
        "year": 2024,
        "title": "CPNP re-notification triggers for reformulations",
        "author": "Castrén & Snellman, Helsinki",
        "regulation_ids": ["EU-COSM-ART13"],
        "summary": (
            "Re-notification is required for any qualitative change in "
            "composition (new substance) and for any quantitative change >10% "
            "in substances of concern. The product may NOT be placed on market "
            "under the prior notification once re-notification is triggered."
        ),
        "recommended_actions": [
            "Treat new peptide as a qualitative change - re-notification required",
            "Submit re-notification before first market placement of reformulated product",
            "Do not rely on the existing notification, even for the first batch",
        ],
        "tags": ["CPNP", "notification", "reformulation", "regulatory"],
    },
    {
        "id": "opinion-2023-004",
        "year": 2023,
        "title": "Cruelty-Free claims and Article 18 supplier obligations",
        "author": "Borenius Attorneys, Helsinki",
        "regulation_ids": ["EU-COSM-ART18", "CLAIM-CRUELTY-FREE"],
        "summary": (
            "A 'cruelty-free' claim is misleading where any ingredient has "
            "been tested on animals - including by the supplier abroad for a "
            "non-EU regulatory submission. The Article 18 ban looks at the "
            "ingredient regardless of where the test was conducted."
        ),
        "recommended_actions": [
            "Require supplier attestation that no animal testing was conducted "
            "on the ingredient anywhere in the world, for any purpose",
            "Drop the 'cruelty-free' claim if the attestation cannot be provided",
            "Consider alternative substantiation (e.g. Leaping Bunny program)",
        ],
        "tags": ["animal testing", "cruelty-free", "supplier", "Article 18"],
    },
]


# --------------------------------------------------------------------------- #
# Department directory                                                        #
# --------------------------------------------------------------------------- #

DEPARTMENT_DIRECTORY: List[Dict[str, Any]] = [
    {
        "id": "dept-dpo",
        "name": "Data Protection Office",
        "lead": "Anneli Saarinen (DPO)",
        "email": "dpo@lumiere.example",
        "owns_topics": [
            "GDPR",
            "consent",
            "international transfers",
            "DPIA",
            "data subject rights",
            "privacy",
        ],
    },
    {
        "id": "dept-legal",
        "name": "Legal",
        "lead": "Mikael Vanhanen (General Counsel)",
        "email": "legal@lumiere.example",
        "owns_topics": [
            "contracts",
            "DPA",
            "regulatory enforcement",
            "litigation",
            "external counsel",
        ],
    },
    {
        "id": "dept-marketing",
        "name": "Marketing",
        "lead": "Marja Nieminen (Head of Marketing)",
        "email": "marketing@lumiere.example",
        "owns_topics": [
            "claims",
            "advertising",
            "packaging copy",
            "influencer partnerships",
        ],
    },
    {
        "id": "dept-rnd",
        "name": "R&D / Product Safety",
        "lead": "Dr. Lauri Rantanen (R&D Director)",
        "email": "rnd@lumiere.example",
        "owns_topics": [
            "safety assessment",
            "CPSR",
            "formulation",
            "ingredients",
        ],
    },
    {
        "id": "dept-regulatory",
        "name": "Regulatory Affairs",
        "lead": "Henrik Aalto (Regulatory Affairs Manager)",
        "email": "regulatory@lumiere.example",
        "owns_topics": [
            "CPNP",
            "notification",
            "PIF",
            "labeling",
            "regulatory submissions",
            "animal testing compliance",
        ],
    },
    {
        "id": "dept-procurement",
        "name": "Procurement",
        "lead": "Sanna Heikkilä (Head of Procurement)",
        "email": "procurement@lumiere.example",
        "owns_topics": [
            "supplier",
            "due diligence",
            "supplier attestations",
            "sourcing",
        ],
    },
    {
        "id": "dept-digital",
        "name": "Data & Digital",
        "lead": "Iina Mäkinen (Data & Digital Lead)",
        "email": "digital@lumiere.example",
        "owns_topics": [
            "app",
            "AI",
            "personalisation",
            "analytics",
            "vendor management",
        ],
    },
]


# --------------------------------------------------------------------------- #
# Lookup helpers                                                              #
# --------------------------------------------------------------------------- #


def _search(records: Iterable[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
    """Simple case-insensitive search across title / summary / tags."""
    q = query.lower().strip()
    if not q:
        return list(records)
    out: List[Dict[str, Any]] = []
    for r in records:
        haystack_parts = [
            str(r.get("title", "")),
            str(r.get("summary", "")),
            " ".join(r.get("tags", []) or []),
            " ".join(r.get("regulation_ids", []) or []),
        ]
        haystack = " ".join(haystack_parts).lower()
        if q in haystack:
            out.append(r)
    return out


def search_past_cases(query: str) -> List[Dict[str, Any]]:
    return _search(PAST_CASES, query)


def search_internal_policies(query: str) -> List[Dict[str, Any]]:
    return _search(INTERNAL_POLICIES, query)


def search_legal_opinions(query: str) -> List[Dict[str, Any]]:
    return _search(LEGAL_OPINIONS, query)


def get_document_by_id(doc_id: str) -> Optional[Dict[str, Any]]:
    """Look up any document (case, policy, opinion) by its id."""
    for collection in (PAST_CASES, INTERNAL_POLICIES, LEGAL_OPINIONS):
        for r in collection:
            if r["id"] == doc_id:
                return r
    return None


def list_departments() -> List[Dict[str, Any]]:
    return list(DEPARTMENT_DIRECTORY)


def find_departments_for_topics(topics: List[str]) -> List[Dict[str, Any]]:
    """Return departments whose ``owns_topics`` intersect any of the given topics."""
    if not topics:
        return []
    lowered = [t.lower() for t in topics]
    matches: List[Dict[str, Any]] = []
    seen = set()
    for dept in DEPARTMENT_DIRECTORY:
        owned = [t.lower() for t in dept.get("owns_topics", [])]
        if any(any(o in t or t in o for o in owned) for t in lowered):
            if dept["id"] not in seen:
                matches.append(dept)
                seen.add(dept["id"])
    return matches


__all__ = [
    "PAST_CASES",
    "INTERNAL_POLICIES",
    "LEGAL_OPINIONS",
    "DEPARTMENT_DIRECTORY",
    "search_past_cases",
    "search_internal_policies",
    "search_legal_opinions",
    "get_document_by_id",
    "list_departments",
    "find_departments_for_topics",
]
