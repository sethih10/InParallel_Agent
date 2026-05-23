"""General Data Protection Regulation - Regulation (EU) 2016/679.

Selected articles relevant to a cosmetics company processing customer data
(skin photos, health questionnaires, marketing analytics, etc.).
Each article follows the standard policy schema defined in policies/__init__.py.
"""

from __future__ import annotations

GDPR_REGULATION = {
    "name": "General Data Protection Regulation",
    "reference": "Regulation (EU) 2016/679",
    "jurisdiction": "European Union / EEA",
    "version": "2016-original",
    "last_updated": "2018-05-25",
}


GDPR_ARTICLES = [
    {
        "id": "GDPR-ART6",
        "regulation": "GDPR (EU 2016/679)",
        "article": "Article 6",
        "title": "Lawfulness of Processing",
        "requirements": (
            "Processing of personal data shall be lawful only if and to the extent "
            "that at least one of the following applies: (a) consent, (b) contract "
            "performance, (c) legal obligation, (d) vital interests, (e) public "
            "task, or (f) legitimate interests (not overridden by data subject "
            "rights). The lawful basis must be documented before processing begins."
        ),
        "violation_indicators": [
            "no lawful basis",
            "unclear basis",
            "process without consent",
            "collect data",
            "no legal ground",
        ],
        "severity": "High",
        "max_fine": "Up to EUR 20M or 4% global annual turnover (Art 83(5))",
        "responsible_department": "Data Protection Office / Legal",
    },
    {
        "id": "GDPR-ART7",
        "regulation": "GDPR (EU 2016/679)",
        "article": "Article 7",
        "title": "Conditions for Consent",
        "requirements": (
            "Where processing is based on consent, the controller must be able to "
            "demonstrate that the data subject has given freely-given, specific, "
            "informed and unambiguous consent. Consent must be as easy to withdraw "
            "as to give."
        ),
        "violation_indicators": [
            "pre-ticked",
            "implied consent",
            "bundled consent",
            "no opt-out",
            "buried in T&Cs",
        ],
        "severity": "High",
        "max_fine": "Up to EUR 20M or 4% global annual turnover (Art 83(5))",
        "responsible_department": "Data Protection Office / Digital / Marketing",
    },
    {
        "id": "GDPR-ART9",
        "regulation": "GDPR (EU 2016/679)",
        "article": "Article 9",
        "title": "Special Categories of Personal Data",
        "requirements": (
            "Processing of personal data revealing racial or ethnic origin, "
            "political opinions, religious beliefs, genetic data, biometric data "
            "for unique identification, data concerning health, sex life or sexual "
            "orientation shall be prohibited unless one of the specific exceptions "
            "applies (e.g. explicit consent, vital interests, public health). Skin "
            "condition data and health questionnaires fall under 'health data'. "
            "Skin photographs used for analysis may constitute biometric data."
        ),
        "violation_indicators": [
            "health data",
            "skin condition",
            "skin photos",
            "biometric",
            "medical history",
            "health questionnaire",
            "special category",
            "sensitive data",
        ],
        "severity": "Critical",
        "max_fine": "Up to EUR 20M or 4% global annual turnover (Art 83(5))",
        "responsible_department": "Data Protection Office / R&D / Digital",
    },
    {
        "id": "GDPR-ART13",
        "regulation": "GDPR (EU 2016/679)",
        "article": "Article 13",
        "title": "Information to be Provided When Personal Data are Collected",
        "requirements": (
            "Where personal data are collected from the data subject, the "
            "controller shall, at the time when the data are obtained, provide the "
            "data subject with: identity of the controller, contact details of the "
            "DPO, purposes and lawful basis, recipients, transfers to third "
            "countries, retention period, and data subject rights."
        ),
        "violation_indicators": [
            "no privacy notice",
            "incomplete privacy policy",
            "missing transparency",
            "hidden purpose",
        ],
        "severity": "Medium",
        "max_fine": "Up to EUR 20M or 4% global annual turnover (Art 83(5))",
        "responsible_department": "Data Protection Office / Legal",
    },
    {
        "id": "GDPR-ART25",
        "regulation": "GDPR (EU 2016/679)",
        "article": "Article 25",
        "title": "Data Protection by Design and by Default",
        "requirements": (
            "The controller shall implement appropriate technical and "
            "organisational measures, such as pseudonymisation and data "
            "minimisation, designed to implement data protection principles in an "
            "effective manner and to integrate the necessary safeguards into the "
            "processing."
        ),
        "violation_indicators": [
            "no minimization",
            "collect everything",
            "no pseudonymisation",
            "default sharing on",
            "privacy as afterthought",
        ],
        "severity": "Medium",
        "max_fine": "Up to EUR 10M or 2% global annual turnover (Art 83(4))",
        "responsible_department": "Data Protection Office / Engineering",
    },
    {
        "id": "GDPR-ART28",
        "regulation": "GDPR (EU 2016/679)",
        "article": "Article 28",
        "title": "Processor",
        "requirements": (
            "Processing by a processor shall be governed by a written contract "
            "(Data Processing Agreement) that binds the processor to the "
            "controller and sets out the subject-matter, duration, nature, "
            "purpose, categories of data, obligations and rights of the controller."
        ),
        "violation_indicators": [
            "no DPA",
            "no processor contract",
            "informal arrangement",
            "marketing partner",
            "third party",
        ],
        "severity": "High",
        "max_fine": "Up to EUR 10M or 2% global annual turnover (Art 83(4))",
        "responsible_department": "Data Protection Office / Legal / Procurement",
    },
    {
        "id": "GDPR-ART35",
        "regulation": "GDPR (EU 2016/679)",
        "article": "Article 35",
        "title": "Data Protection Impact Assessment (DPIA)",
        "requirements": (
            "Where a type of processing is likely to result in a high risk to the "
            "rights and freedoms of natural persons (e.g. systematic and extensive "
            "evaluation, processing of special categories on a large scale), the "
            "controller shall, prior to the processing, carry out a Data "
            "Protection Impact Assessment."
        ),
        "violation_indicators": [
            "no DPIA",
            "skip DPIA",
            "AI personalization",
            "profiling",
            "automated decision",
            "large scale",
            "high risk processing",
        ],
        "severity": "High",
        "max_fine": "Up to EUR 10M or 2% global annual turnover (Art 83(4))",
        "responsible_department": "Data Protection Office",
    },
    {
        "id": "GDPR-ART44",
        "regulation": "GDPR (EU 2016/679)",
        "article": "Articles 44-49",
        "title": "Transfers of Personal Data to Third Countries",
        "requirements": (
            "Any transfer of personal data to a third country or international "
            "organisation shall take place only if the conditions of Chapter V are "
            "met: (a) adequacy decision, (b) appropriate safeguards (Standard "
            "Contractual Clauses with Transfer Impact Assessment, Binding "
            "Corporate Rules), or (c) specific derogations. Following Schrems II, "
            "transfers to the US require additional safeguards beyond SCCs."
        ),
        "violation_indicators": [
            "US transfer",
            "share with US",
            "international transfer",
            "third country",
            "no SCC",
            "no adequacy",
            "no TIA",
            "US firm",
            "US analytics",
            "Schrems",
        ],
        "severity": "Critical",
        "max_fine": "Up to EUR 20M or 4% global annual turnover (Art 83(5))",
        "responsible_department": "Data Protection Office / Legal",
    },
]
