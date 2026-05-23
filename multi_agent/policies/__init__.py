"""Policy dictionaries for EU cosmetic-company compliance.

Each policy dictionary entry follows the schema below so the agents can
consume them uniformly:

    {
        "id": "EU-COSM-ART10",                  # stable unique key
        "regulation": "EC 1223/2009",           # short citation
        "article": "Article 10",                # human-readable article ref
        "title": "Safety Assessment",
        "requirements": "<plain-English summary of the legal requirement>",
        "violation_indicators": ["keyword", ...],  # hints for matching
        "severity": "Critical" | "High" | "Medium" | "Low",
        "max_fine": "<short description of maximum fine>",
        "responsible_department": "<department(s) responsible>",
    }

The module exposes:
    - ALL_REGULATIONS:        dict[str, article_entry] keyed by ``id``
    - REGULATION_METADATA:    dict[str, regulation_metadata]
    - get_regulation(id):     look up a single article by id
    - list_regulations():     list every article as a list
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .eu_cosmetics import EU_COSMETICS_ARTICLES, EU_COSMETICS_REGULATION
from .claims_regulation import CLAIMS_ARTICLES, CLAIMS_REGULATION
from .gdpr import GDPR_ARTICLES, GDPR_REGULATION


REGULATION_METADATA: Dict[str, Dict[str, Any]] = {
    "EC 1223/2009": EU_COSMETICS_REGULATION,
    "EU 655/2013": CLAIMS_REGULATION,
    "GDPR (EU 2016/679)": GDPR_REGULATION,
}


_ALL_ARTICLES: List[Dict[str, Any]] = (
    EU_COSMETICS_ARTICLES + CLAIMS_ARTICLES + GDPR_ARTICLES
)


ALL_REGULATIONS: Dict[str, Dict[str, Any]] = {
    article["id"]: article for article in _ALL_ARTICLES
}


def get_regulation(regulation_id: str) -> Optional[Dict[str, Any]]:
    """Return a single article entry by id, or ``None`` if not found."""
    return ALL_REGULATIONS.get(regulation_id)


def list_regulations() -> List[Dict[str, Any]]:
    """Return all article entries as a list."""
    return list(_ALL_ARTICLES)


__all__ = [
    "ALL_REGULATIONS",
    "REGULATION_METADATA",
    "get_regulation",
    "list_regulations",
]
