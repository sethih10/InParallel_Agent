"""
Orchestration layer: pulls data from the InParallel MCP server and runs
the rules defined in ``rules.py``.

Design notes
------------
- The MCP returns JSON-encoded strings for most calls (see existing
  examples under ``examples/``). We decode once at the boundary.
- Independent fetches (action items, decisions, meetings) are run
  concurrently via ``asyncio.gather`` to keep the demo snappy.
- Transcript scanning is opt-in (``include_transcripts=True``) because
  transcripts may contain sensitive discussion (README §12.2).
"""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from typing import Any

from client import InParallelClient

from .rules import (
    Finding,
    check_action_items,
    check_decisions,
    check_sensitive_data,
)


def _decode(raw: Any) -> Any:
    """MCP tools return JSON strings; pass-through anything already decoded."""
    if isinstance(raw, str):
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return raw
    return raw


@dataclass
class ComplianceReport:
    workspace_id: str
    workspace_name: str
    findings: list[Finding]

    def by_severity(self) -> dict[str, list[Finding]]:
        groups: dict[str, list[Finding]] = {"high": [], "medium": [], "low": []}
        for f in self.findings:
            groups.setdefault(f.severity, []).append(f)
        return groups


class ComplianceChecker:
    """Run all compliance rules against a single InParallel workspace."""

    def __init__(
        self,
        client: InParallelClient,
        workspace_id: str,
        workspace_name: str = "",
        *,
        include_transcripts: bool = False,
        transcript_limit: int = 3,
    ) -> None:
        self._client = client
        self._workspace_id = workspace_id
        self._workspace_name = workspace_name
        self._include_transcripts = include_transcripts
        self._transcript_limit = transcript_limit

    async def run(self) -> ComplianceReport:
        action_items, decisions, meetings = await self._fetch_core()

        findings: list[Finding] = []
        findings.extend(check_action_items(action_items))
        findings.extend(await self._decision_findings(decisions))
        findings.extend(await self._sensitive_findings(meetings))

        return ComplianceReport(
            workspace_id=self._workspace_id,
            workspace_name=self._workspace_name,
            findings=findings,
        )

    # ----- fetchers ------------------------------------------------------- #

    async def _fetch_core(
        self,
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
        """Fetch action items, decisions, and meeting list concurrently."""
        ai_raw, dec_raw, mtg_raw = await asyncio.gather(
            self._client.list_action_items(self._workspace_id),
            self._client.list_decisions(self._workspace_id),
            self._client.list_meeting_records(self._workspace_id),
        )
        return (
            _decode(ai_raw) or [],
            _decode(dec_raw) or [],
            _decode(mtg_raw) or [],
        )

    async def _decision_findings(
        self, decisions: list[dict[str, Any]]
    ) -> list[Finding]:
        """Decision audit needs per-decision detail for rationale/owner."""
        if not decisions:
            return []

        detailed: list[dict[str, Any]] = []
        for d in decisions:
            d_id = d.get("id")
            if not d_id:
                detailed.append(d)
                continue
            full = _decode(await self._client.get_decision(d_id))
            # Merge: prefer full record fields, fall back to list-view fields.
            if isinstance(full, dict):
                merged = {**d, **full}
            else:
                merged = d
            detailed.append(merged)
        return check_decisions(detailed)

    async def _sensitive_findings(
        self, meetings: list[dict[str, Any]]
    ) -> list[Finding]:
        """Scan meeting summaries (and optionally transcripts) for secrets."""
        if not meetings:
            return []

        documents: list[dict[str, Any]] = []
        # Limit how many recent meetings we scan to keep the demo bounded.
        scan_targets = meetings[: max(self._transcript_limit, 5)]

        for meeting in scan_targets:
            m_id = meeting.get("id")
            if not m_id:
                continue
            record = _decode(await self._client.get_meeting_record(m_id))
            if isinstance(record, dict):
                summary = record.get("summary") or ""
                documents.append(
                    {"source": f"meeting:{m_id}:summary", "text": summary}
                )

            if self._include_transcripts:
                transcript = _decode(await self._client.get_transcript(m_id))
                # Transcripts may come back as a structure or a long string;
                # normalise to text.
                text = (
                    transcript
                    if isinstance(transcript, str)
                    else json.dumps(transcript)
                )
                documents.append(
                    {"source": f"meeting:{m_id}:transcript", "text": text}
                )

        return check_sensitive_data(documents)
