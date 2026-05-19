# Compliance Checker

A small, transparent example that uses the **InParallel MCP** to audit
a workspace for execution-governance and sensitive-data issues.

It is *not* an LLM agent: every rule is a plain Python function so you
can read it, audit it, and extend it.

## What it checks

| Rule ID prefix         | What it verifies                                                                              | MCP tools used                                              |
|------------------------|-----------------------------------------------------------------------------------------------|-------------------------------------------------------------|
| `action_item.*`        | Every action item has an `owner_email`, `due_date`, and `source_meeting_id`; nothing overdue. | `list_action_items`                                         |
| `decision.*`           | Every `approved` / `rejected` decision has an owner, rationale, and source meeting.           | `list_decisions`, `get_decision`                            |
| `sensitive_data.*`     | Regex scan for AWS keys, generic api keys, passwords, bearer tokens, SSNs, private-key blobs. | `list_meeting_records`, `get_meeting_record` (+ optionally `get_transcript`) |

Severity is `high` / `medium` / `low`. Counts and grouped findings are
printed at the end.

## How to run

From the repo root, with `IN_PARALLEL_API_KEY` set in your env or
`.env`:

```bash
python -m compliance_checker.main                       # first workspace
python -m compliance_checker.main --workspace Marketing # by name
python -m compliance_checker.main --include-transcripts # also scan transcripts (opt-in)
```

Transcripts are gated behind an explicit flag because they may contain
sensitive discussion (see README §12.2 of the main project).

## Files

- `rules.py`   — `Finding` dataclass + rule functions (`check_action_items`,
  `check_decisions`, `check_sensitive_data`). Regex patterns live here.
- `checker.py` — `ComplianceChecker` wires MCP calls to rules. Fetches
  independent resources concurrently with `asyncio.gather`.
- `report.py`  — Plain-text formatter, grouped by severity then rule.
- `main.py`    — CLI entry point.

## Adding a new rule

1. Write a function in `rules.py` that takes already-decoded data and
   returns a `list[Finding]`. Pick a unique `rule_id` prefix.
2. Fetch any extra MCP data you need inside `ComplianceChecker.run`
   and pass it to your new function.
3. That's it — `report.py` groups findings by `rule_id` automatically.

## Note on "security skills"

This repo does not ship a dedicated security-compliance skill. The
checker above implements compliance from scratch with explicit,
auditable rules so you can adapt it to your own policy.
