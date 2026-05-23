"""EU Cosmetic Claims Regulation - Commission Regulation (EU) No 655/2013.

Lays down the six common criteria for the justification of claims used in
relation to cosmetic products. Each criterion follows the standard policy
schema defined in policies/__init__.py.
"""

from __future__ import annotations

CLAIMS_REGULATION = {
    "name": "EU Cosmetic Claims Regulation",
    "reference": "Commission Regulation (EU) No 655/2013",
    "jurisdiction": "European Union",
    "version": "2013-original",
    "last_updated": "2013-07-10",
}


CLAIMS_ARTICLES = [
    {
        "id": "CLAIM-CRIT1",
        "regulation": "EU 655/2013",
        "article": "Annex - Criterion 1",
        "title": "Legal Compliance",
        "requirements": (
            "Claims indicating that a product has been authorised or approved by "
            "a competent authority within the Union shall not be allowed. Claims "
            "must not give the impression of legal endorsement that does not exist."
        ),
        "violation_indicators": [
            "EU approved",
            "government approved",
            "officially endorsed",
            "authority-certified",
        ],
        "severity": "Medium",
        "max_fine": "National consumer authority fines + advertising correction",
        "responsible_department": "Marketing / Regulatory Affairs",
    },
    {
        "id": "CLAIM-CRIT2",
        "regulation": "EU 655/2013",
        "article": "Annex - Criterion 2",
        "title": "Truthfulness",
        "requirements": (
            "Claims must be truthful. If a product is claimed to contain a "
            "specific ingredient, that ingredient must be deliberately present. "
            "Claims about properties an ingredient does not possess shall not be made."
        ),
        "violation_indicators": [
            "100% natural",
            "100% organic",
            "all natural",
            "pure organic",
            "no synthetics",
            "without certification",
        ],
        "severity": "Medium",
        "max_fine": "Consumer authority fines + advertising correction order",
        "responsible_department": "Marketing / Regulatory Affairs",
    },
    {
        "id": "CLAIM-CRIT3",
        "regulation": "EU 655/2013",
        "article": "Annex - Criterion 3",
        "title": "Evidential Support",
        "requirements": (
            "Claims for cosmetic products, whether explicit or implicit, must be "
            "supported by adequate and verifiable evidence regardless of the types "
            "of evidential support used. Evidence must be relevant to the product, "
            "the claim, and the conditions of use. Claims should follow the level "
            "of evidence expected by the reasonable end user."
        ),
        "violation_indicators": [
            "clinically proven",
            "scientifically proven",
            "studies show",
            "proven to reduce",
            "small internal study",
            "anecdotal evidence",
            "no peer review",
            "in-house study",
        ],
        "severity": "High",
        "max_fine": "Consumer authority fines (up to EUR 500,000 in some Member States) + claim withdrawal",
        "responsible_department": "Marketing / R&D / Regulatory Affairs",
    },
    {
        "id": "CLAIM-CRIT4",
        "regulation": "EU 655/2013",
        "article": "Annex - Criterion 4",
        "title": "Honesty",
        "requirements": (
            "Presentations of the product's performance shall not go beyond the "
            "available supporting evidence. Claims shall not attribute to the "
            "product concerned specific characteristics if all similar products "
            "have such characteristics."
        ),
        "violation_indicators": [
            "exaggerated claim",
            "overstated",
            "miracle",
            "best in market",
            "only product",
        ],
        "severity": "Medium",
        "max_fine": "Consumer authority fines",
        "responsible_department": "Marketing",
    },
    {
        "id": "CLAIM-CRIT5",
        "regulation": "EU 655/2013",
        "article": "Annex - Criterion 5",
        "title": "Fairness",
        "requirements": (
            "Claims for cosmetic products shall be objective and shall not "
            "denigrate competitors, nor shall they denigrate ingredients legally "
            "used."
        ),
        "violation_indicators": [
            "unlike competitors",
            "better than",
            "denigrate",
            "competitor weakness",
        ],
        "severity": "Low",
        "max_fine": "Consumer authority fines + competitor litigation risk",
        "responsible_department": "Marketing / Legal",
    },
    {
        "id": "CLAIM-CRIT6",
        "regulation": "EU 655/2013",
        "article": "Annex - Criterion 6",
        "title": "Informed Decision-Making",
        "requirements": (
            "Claims shall be clear and understandable to the average end user. "
            "Claims are an integral part of products and shall contain information "
            "allowing the average end user to make an informed choice."
        ),
        "violation_indicators": [
            "vague claim",
            "ambiguous",
            "misleading shorthand",
            "small print",
        ],
        "severity": "Low",
        "max_fine": "Consumer authority fines",
        "responsible_department": "Marketing",
    },
    {
        "id": "CLAIM-CRUELTY-FREE",
        "regulation": "EU 655/2013 + Cosmetics Art 18",
        "article": "Technical Document on Claims - Annex III",
        "title": "Cruelty-Free / No Animal Testing Claims",
        "requirements": (
            "A 'not tested on animals' or 'cruelty-free' claim may only be made "
            "where neither the manufacturer nor its ingredient suppliers carried "
            "out or commissioned any animal tests on the finished product, its "
            "prototypes, or any of the ingredients contained in it, and where no "
            "ingredients have been tested on animals by third parties for use in "
            "other cosmetic products."
        ),
        "violation_indicators": [
            "cruelty-free",
            "not tested on animals",
            "no animal testing",
            "supplier tested",
            "ingredient tested abroad",
        ],
        "severity": "High",
        "max_fine": "Consumer authority fines + ASA/equivalent rulings + reputational damage",
        "responsible_department": "Marketing / Procurement / Regulatory Affairs",
    },
]
