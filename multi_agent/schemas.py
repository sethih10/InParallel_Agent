"""Typed records exchanged between agents and graph nodes.

These dataclasses define the *shape* of the data flowing through the system.
Keep them stable - changing a schema means updating every consumer.

Conventions:
    - Plain ``@dataclass`` (no Pydantic dependency on the data path).
    - Optional fields default to ``None`` so partial records can be carried
      forward through the graph (e.g. ``precedent_doc_ids`` is filled in
      AFTER the Legal Research agent runs).
    - ``to_dict()`` helpers produce JSON-serialisable structures used by
      the report generator.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


# --------------------------------------------------------------------------- #
# Evidence chain primitives                                                   #
# --------------------------------------------------------------------------- #


@dataclass
class RegulationReference:
    """Pointer back to a specific article in the policy dictionaries."""

    id: str                       # e.g. "GDPR-ART9"
    regulation: str               # e.g. "GDPR (EU 2016/679)"
    article: str                  # e.g. "Article 9"
    title: str                    # e.g. "Special Categories of Personal Data"
    requirement_text: str         # short summary of the requirement

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# --------------------------------------------------------------------------- #
# Compliance findings                                                         #
# --------------------------------------------------------------------------- #


@dataclass
class Finding:
    """One potential compliance issue raised by the Compliance Analyst.

    Carries the first two links of the evidence chain (transcript quote +
    regulation reference). The third link (``precedent_doc_ids``) is filled
    in by the Legal Research agent.
    """

    id: str                                       # e.g. "finding-001"
    decision_id: str                              # links to meeting decision
    summary: str                                  # short description of the issue
    transcript_quote: str                         # verbatim from meeting
    transcript_speaker: str                       # who said it
    regulation: RegulationReference               # what regulation
    severity: str                                 # Critical | High | Medium | Low
    max_fine: str                                 # short description of max fine
    responsible_department: str                   # which dept owns the issue
    confirmed: bool = False                       # set at HITL Gate 1
    precedent_doc_ids: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["regulation"] = self.regulation.to_dict()
        return d


# --------------------------------------------------------------------------- #
# Proposed / approved solutions                                               #
# --------------------------------------------------------------------------- #


@dataclass
class Solution:
    """A remediation proposal drafted by the Legal Research agent.

    Each solution MUST cite at least one company-database document in
    ``cited_doc_ids`` - this is enforced by the report generator. The
    ``cited_doc_ids`` also populate ``Finding.precedent_doc_ids`` to
    complete the evidence chain.
    """

    id: str                              # e.g. "solution-001"
    finding_id: str                      # which finding this addresses
    proposal: str                        # the actual remediation text
    cited_doc_ids: List[str]             # company DB ids cited as evidence
    rationale: str                       # WHY this solution, given the precedents
    approved: Optional[bool] = None      # set at HITL Gate 2 (None = pending)
    user_edited_proposal: Optional[str] = None  # if user edited at Gate 2

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# --------------------------------------------------------------------------- #
# Department notifications and meeting agenda                                 #
# --------------------------------------------------------------------------- #


@dataclass
class Notification:
    """A drafted message to a specific internal department."""

    department_id: str
    department_name: str
    recipient_email: str
    subject: str
    body: str
    related_finding_ids: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MeetingAgenda:
    """A drafted cross-functional follow-up meeting agenda."""

    title: str
    suggested_attendees: List[str]
    agenda_items: List[str]
    target_date: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


__all__ = [
    "RegulationReference",
    "Finding",
    "Solution",
    "Notification",
    "MeetingAgenda",
]
