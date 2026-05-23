"""EU Cosmetics Regulation (EC) No 1223/2009.

Selected articles relevant to product launch / marketing meeting compliance.
Each entry follows the standard policy schema defined in policies/__init__.py.
"""

from __future__ import annotations

EU_COSMETICS_REGULATION = {
    "name": "EU Cosmetics Regulation",
    "reference": "Regulation (EC) No 1223/2009",
    "jurisdiction": "European Union",
    "version": "consolidated-2024",
    "last_updated": "2024-04-15",
}


EU_COSMETICS_ARTICLES = [
    {
        "id": "EU-COSM-ART3",
        "regulation": "EC 1223/2009",
        "article": "Article 3",
        "title": "Safety",
        "requirements": (
            "A cosmetic product made available on the market shall be safe for "
            "human health when used under normal or reasonably foreseeable "
            "conditions of use."
        ),
        "violation_indicators": [
            "skip safety",
            "no safety assessment",
            "untested ingredient",
            "fast-track launch",
            "ship without testing",
        ],
        "severity": "Critical",
        "max_fine": "Product withdrawal + national administrative fines",
        "responsible_department": "Product Safety / Regulatory Affairs",
    },
    {
        "id": "EU-COSM-ART8",
        "regulation": "EC 1223/2009",
        "article": "Article 8",
        "title": "Good Manufacturing Practice (GMP)",
        "requirements": (
            "Manufacture of cosmetic products must comply with Good Manufacturing "
            "Practice (ISO 22716) to ensure consistent product quality and safety."
        ),
        "violation_indicators": [
            "skip GMP",
            "no ISO 22716",
            "unaudited factory",
            "manufacturing shortcut",
        ],
        "severity": "High",
        "max_fine": "National authority fines + production halt",
        "responsible_department": "Manufacturing / Quality Assurance",
    },
    {
        "id": "EU-COSM-ART10",
        "regulation": "EC 1223/2009",
        "article": "Article 10",
        "title": "Safety Assessment",
        "requirements": (
            "Before a cosmetic product is placed on the market, the Responsible "
            "Person must ensure that a Product Information File (PIF) including a "
            "cosmetic product safety report has been carried out by a qualified "
            "safety assessor, on the basis of the relevant information."
        ),
        "violation_indicators": [
            "no safety assessment",
            "no PIF",
            "no safety report",
            "unassessed ingredient",
            "new peptide",
            "novel ingredient",
            "skip CPSR",
        ],
        "severity": "Critical",
        "max_fine": "Product withdrawal + national authority fines up to EUR 100,000",
        "responsible_department": "Regulatory Affairs / Product Safety",
    },
    {
        "id": "EU-COSM-ART11",
        "regulation": "EC 1223/2009",
        "article": "Article 11",
        "title": "Product Information File",
        "requirements": (
            "The Responsible Person must keep a Product Information File (PIF) for "
            "10 years following the date on which the last batch of the product was "
            "placed on the market, and make it available to competent authorities."
        ),
        "violation_indicators": [
            "no PIF",
            "missing documentation",
            "incomplete records",
        ],
        "severity": "Medium",
        "max_fine": "National authority fines",
        "responsible_department": "Regulatory Affairs",
    },
    {
        "id": "EU-COSM-ART13",
        "regulation": "EC 1223/2009",
        "article": "Article 13",
        "title": "CPNP Notification",
        "requirements": (
            "Prior to placing a cosmetic product on the market, the Responsible "
            "Person must notify the European Commission via the Cosmetic Products "
            "Notification Portal (CPNP). Re-notification is required when the "
            "formulation changes materially."
        ),
        "violation_indicators": [
            "skip CPNP",
            "no notification",
            "reformulation",
            "skip re-notification",
            "speed up launch",
            "bypass CPNP",
        ],
        "severity": "Medium",
        "max_fine": "National authority fines + market withdrawal until notified",
        "responsible_department": "Regulatory Affairs",
    },
    {
        "id": "EU-COSM-ART14",
        "regulation": "EC 1223/2009",
        "article": "Article 14",
        "title": "Restricted and Prohibited Substances",
        "requirements": (
            "Cosmetic products shall not contain substances listed in Annex II "
            "(prohibited) or substances listed in Annex III (restricted) beyond "
            "the limits or outside the conditions laid down."
        ),
        "violation_indicators": [
            "Annex II",
            "Annex III",
            "prohibited ingredient",
            "restricted substance",
            "exceeds limit",
        ],
        "severity": "Critical",
        "max_fine": "Product withdrawal + criminal liability in some Member States",
        "responsible_department": "Product Safety / R&D",
    },
    {
        "id": "EU-COSM-ART18",
        "regulation": "EC 1223/2009",
        "article": "Article 18",
        "title": "Animal Testing Ban",
        "requirements": (
            "It is prohibited to place on the EU market cosmetic products where "
            "the final formulation OR ingredients have been tested on animals to "
            "meet the requirements of this Regulation. This ban applies to the "
            "company AND its ingredient suppliers."
        ),
        "violation_indicators": [
            "animal test",
            "animal testing",
            "supplier tested",
            "cruelty-free",
            "tested on rabbits",
            "in vivo",
            "ingredient tested abroad",
        ],
        "severity": "High",
        "max_fine": "Market ban + reputational damage + national authority fines",
        "responsible_department": "Regulatory Affairs / Procurement",
    },
    {
        "id": "EU-COSM-ART19",
        "regulation": "EC 1223/2009",
        "article": "Article 19",
        "title": "Labelling",
        "requirements": (
            "Cosmetic products shall be made available on the market only where "
            "the container and packaging bear in indelible, easily legible and "
            "visible lettering: the name and address of the Responsible Person, "
            "nominal content, date of minimum durability or PAO, precautions, "
            "batch number, function, and a list of ingredients (INCI names)."
        ),
        "violation_indicators": [
            "missing label",
            "no INCI",
            "incomplete labeling",
            "no PAO",
            "no batch number",
        ],
        "severity": "Low",
        "max_fine": "National authority fines + labeling correction order",
        "responsible_department": "Packaging / Regulatory Affairs",
    },
    {
        "id": "EU-COSM-ART20",
        "regulation": "EC 1223/2009",
        "article": "Article 20",
        "title": "Product Claims",
        "requirements": (
            "In the labelling, making available on the market and advertising of "
            "cosmetic products, text, names, trade marks, pictures and figurative "
            "or other signs shall not be used to imply that these products have "
            "characteristics or functions which they do not have. Medicinal claims "
            "are strictly prohibited."
        ),
        "violation_indicators": [
            "clinically proven",
            "medical claim",
            "cures",
            "treats",
            "removes wrinkles",
            "anti-aging cure",
            "dermatologically proven",
            "scientifically proven",
        ],
        "severity": "High",
        "max_fine": "National authority fines + advertising correction orders",
        "responsible_department": "Marketing / Regulatory Affairs",
    },
]
