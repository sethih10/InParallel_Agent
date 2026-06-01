# Compliance Multi-Agent System

A hierarchical multi-agent system that reviews a cosmetics company's meeting decisions against EU regulations (Cosmetics Regulation EC 1223/2009, Cosmetic Claims Regulation EU 655/2013, GDPR), runs the legal team through a two-gate human-in-the-loop review, and produces an auditable compliance report with full evidence chain.

Built with **LangGraph** + **Anthropic Claude Sonnet 4.5**.

---

## Table of contents

1. [Quick start](#1-quick-start)
2. [What it does](#2-what-it-does)
3. [Architecture](#3-architecture)
4. [Folder structure](#4-folder-structure)
5. [How data flows through the graph](#5-how-data-flows-through-the-graph)
6. [The three agents](#6-the-three-agents)
7. [Two human-in-the-loop gates](#7-two-human-in-the-loop-gates)
8. [Evidence chain and severity scoring](#8-evidence-chain-and-severity-scoring)
9. [Policy dictionaries](#9-policy-dictionaries)
10. [Company database (fake)](#10-company-database-fake)
11. [Meeting scenarios](#11-meeting-scenarios)
12. [Running and debugging](#12-running-and-debugging)
13. [Extending the system](#13-extending-the-system)

---

## 1. Quick start

```bash
# 1. Set up the Python environment
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. Configure your API key
cp .env.example .env
# Edit .env and set ANTHROPIC_API_KEY=...

# 3. Run the demo (default: meeting-glow-001)
python run_multi_agent_demo.py

# Or pick the wider-coverage meeting
python run_multi_agent_demo.py meeting-glow-002

# Verbose diagnostics (prints what each agent returned)
COMPLIANCE_DEBUG=1 python run_multi_agent_demo.py meeting-glow-002
```

You will be prompted twice during the run:

1. **Gate 1** — confirm each potential finding `[y/N]`
2. **Gate 2** — approve / edit / reject each proposed solution `[a/e/r]`

The final report is printed to the terminal and saved to `reports/compliance_report.json`.

---

## 2. What it does

You hand it a meeting id. The system:

1. **Inspects the meeting** for decisions that violate EU regulations.
2. **Pauses** so the legal team can confirm which findings are real legal issues.
3. **In parallel** — once findings are confirmed:
   - The **Notifier** immediately alerts each affected department and proposes a cross-functional meeting between them and the legal team.
   - The **Legal Researcher** searches the company knowledge base (past cases, internal policies, external legal opinions) and drafts remediation proposals backed by precedent.
4. **Pauses again** so the legal team can approve, edit, or reject each proposed solution.
5. **Compiles** a final structured report — JSON for machine consumption, plain text for humans — sorted by severity with full evidence chain.

The legal team makes legal judgments. The agents do the research and drafting.

---

## 3. Architecture

```
                        ┌────────────────────────┐
                        │       START            │
                        └───────────┬────────────┘
                                    ▼
                  ┌────────────────────────────────────┐
                  │  compliance_analyst   (ReAct LLM)  │
                  │  tools: get_meeting_decisions,     │
                  │         get_transcript_excerpt,    │
                  │         lookup_regulation,         │
                  │         list_all_regulations       │
                  └────────────────┬───────────────────┘
                                   ▼
                  ╔════════════════════════════════════╗
                  ║  HITL GATE 1                       ║
                  ║  legal team confirms findings      ║
                  ╚════════════════╤═══════════════════╝
                                   ▼
                  ┌────────────────────────────────────┐
                  │  fan_out            (deterministic) │
                  └────────┬──────────────────┬─────────┘
                           ▼                  ▼
           ┌───────────────────┐  ┌───────────────────────┐
           │ notifier          │  │ legal_researcher       │
           │ (ReAct LLM)       │  │ (ReAct LLM)            │
           │ tools:            │  │ tools:                 │
           │  list_departments │  │  search_past_cases     │
           │  find_depts_for   │  │  search_internal_      │
           │   _topics         │  │   policies             │
           │                   │  │  search_legal_opinions │
           │                   │  │  get_document_by_id    │
           └────────┬──────────┘  └──────────┬────────────┘
                    └──────────┬─────────────┘
                               ▼
                  ┌────────────────────────────────────┐
                  │  fan_in             (deterministic) │
                  └────────────────────┬───────────────┘
                                       ▼
                  ╔════════════════════════════════════╗
                  ║  HITL GATE 2                       ║
                  ║  legal team approves solutions     ║
                  ╚════════════════╤═══════════════════╝
                                   ▼
                  ┌────────────────────────────────────┐
                  │  report_generator   (deterministic)│
                  │  compiles JSON + text report       │
                  └────────────────┬───────────────────┘
                                   ▼
                        ┌────────────────────────┐
                        │        END             │
                        └────────────────────────┘
```

### Why this shape?

- **Hierarchical, not flat** — each agent has a single, narrow responsibility. A flat ReAct agent with all 10 tools would get distracted; specialised agents stay focused.
- **Parallel notification + research** — once Gate 1 confirms findings, there is no reason to wait for the researcher before alerting departments. `fan_out` fires both branches simultaneously; `fan_in` joins them before Gate 2. This cuts wall-clock time and ensures departments get notified at the earliest possible moment.
- **Two HITL gates, not one** — legal judgement happens at two distinct points: *"is this actually a legal issue?"* (Gate 1, before the parallel phase) and *"is this proposed solution acceptable?"* (Gate 2, after both parallel branches complete). Bundling them is impossible because the second question depends on research that hasn't happened yet at the first gate.
- **Autonomous tool-using legal research, not RAG** — pulling one set of similar documents isn't enough. The legal researcher genuinely does multi-step reasoning: search past cases → cross-reference with internal policies → check what external counsel said. That's a tool-using agent, not a one-shot retrieval.
- **Deterministic report generator** — the final compilation step is plain Python. No LLM is needed to assemble structured output from already-structured pieces; an LLM there would only add hallucination risk.

---

## 4. Folder structure

```
InParallel/
├── README.md                       ← this file
├── requirements.txt
├── .env.example                    ← copy to .env, fill in API key
├── run_multi_agent_demo.py         ← interactive CLI entry point
│
├── multi_agent/                    ← main package
│   ├── __init__.py                 ← public API: build_compliance_graph, ...
│   ├── config.py                   ← env loading, model name, recursion limits
│   ├── state.py                    ← ComplianceState TypedDict (the contract)
│   ├── schemas.py                  ← Finding / Solution / Notification dataclasses
│   ├── graph.py                    ← StateGraph wiring + interrupts + checkpointer
│   │
│   ├── agents/                     ← LLM-backed ReAct agents (one file each)
│   │   ├── compliance_analyst.py
│   │   ├── legal_researcher.py
│   │   └── notifier.py
│   │
│   ├── nodes/                      ← deterministic graph nodes (no LLM)
│   │   ├── human_review.py         ← HITL gate CLI prompts
│   │   └── report_generator.py     ← final JSON + text compilation
│   │
│   ├── tools/                      ← agent tools, grouped by consumer
│   │   ├── compliance_tools.py     ← 4 tools for the analyst
│   │   ├── legal_tools.py          ← 4 tools for the researcher
│   │   └── notification_tools.py   ← 2 tools for the notifier
│   │
│   ├── prompts/                    ← system prompts as editable .md files
│   │   ├── compliance_analyst.md
│   │   ├── legal_researcher.md
│   │   └── notifier.md
│   │
│   ├── policies/                   ← EU regulation dictionaries (24 articles)
│   │   ├── eu_cosmetics.py         ← EC 1223/2009 (9 articles)
│   │   ├── claims_regulation.py    ← EU 655/2013 (7 criteria)
│   │   └── gdpr.py                 ← GDPR (8 articles)
│   │
│   └── data/                       ← fake/seed data (swap for real DB)
│       ├── meetings.py             ← 2 meeting fixtures, 17 decisions total
│       └── company_database.py     ← past cases, policies, opinions, dept directory
│
└── reports/                        ← generated JSON reports (gitignored)
    └── compliance_report.json
```

### Why this layout

| Folder | Purpose | Why separate |
|---|---|---|
| `state.py` | The TypedDict that flows between every node | LangGraph convention — isolating state makes data flow explicit |
| `schemas.py` | Typed records (`Finding`, `Solution`, `Notification`) | IDE autocomplete + stable shapes instead of raw dicts |
| `graph.py` | Only node wiring | A new contributor reads ONE file to understand the topology |
| `agents/` (one file each) | Easy to add / remove an agent | No giant "agents.py" to scroll through |
| `nodes/` separate from `agents/` | Splits LLM nodes from deterministic ones | `report_generator` doesn't need an LLM — mixing them would confuse readers |
| `tools/` grouped by agent | `from multi_agent.tools import legal_tools` is self-documenting | Tells you which agent uses which tools at a glance |
| `prompts/` as `.md` files | Non-engineers (legal SMEs) can edit prompts | Prompt iteration shouldn't require Python edits |
| `policies/` registry | `ALL_REGULATIONS` exposed via one import | One place to add a new regulation |
| `data/` isolated | All mock data lives here | Swapping to a real DB means replacing this folder, nothing else |

### Reading order for a new contributor

1. This README
2. `multi_agent/state.py` — what data flows
3. `multi_agent/graph.py` — how nodes connect
4. `multi_agent/agents/compliance_analyst.py` — example agent pattern
5. `multi_agent/policies/eu_cosmetics.py` — example policy dict
6. `run_multi_agent_demo.py` — how it's invoked

---

## 5. How data flows through the graph

The single `ComplianceState` TypedDict is the contract between all nodes. Each node populates only the keys it owns.

```python
class ComplianceState(TypedDict, total=False):
    messages: list[BaseMessage]          # accumulated chat history

    # Input
    meeting_id: str                      # set by the caller

    # Set by compliance_analyst
    potential_findings: list[dict]

    # Set by HITL Gate 1
    confirmed_findings: list[dict]
    gate1_complete: bool

    # Set by legal_researcher
    proposed_solutions: list[dict]

    # Set by HITL Gate 2
    approved_solutions: list[dict]
    gate2_complete: bool

    # Set by notifier
    department_notifications: list[dict]
    meeting_agenda: dict

    # Set by report_generator
    final_report: dict
```

Inspect the live state at any point: `graph.get_state(config).values`.

A `MemorySaver` checkpointer is attached to the graph — this is what lets the graph **pause at the `interrupt_before` gates and resume across user turns**. Without a checkpointer, interrupts don't work.

---

## 6. The three agents

All three are LangGraph **ReAct agents** built with `langgraph.prebuilt.create_react_agent`. Each runs an inner Reason → Act → Observe loop until it emits its final structured JSON.

### Compliance Analyst

**File:** `multi_agent/agents/compliance_analyst.py`  
**Prompt:** `multi_agent/prompts/compliance_analyst.md`

**Job:** Find decisions in the meeting that violate EU regulations.

**Tools:**
| Tool | What it does |
|---|---|
| `get_meeting_decisions(meeting_id)` | List the meeting's decisions |
| `get_transcript_excerpt(meeting_id, keyword)` | Read the (optionally filtered) transcript |
| `list_all_regulations()` | Compact catalogue of all 24 regulation articles |
| `lookup_regulation(regulation_id)` | Full text of one article |

**Output:** `{"findings": [{decision_id, summary, transcript_quote, transcript_speaker, regulation_id}]}`

**Workflow:** decisions → transcript → regulation catalogue → per-decision `lookup_regulation` → JSON findings.

### Legal Researcher

**File:** `multi_agent/agents/legal_researcher.py`  
**Prompt:** `multi_agent/prompts/legal_researcher.md`

**Job:** For each confirmed finding, draft a remediation backed by company precedent.

**Tools:**
| Tool | What it does |
|---|---|
| `search_past_cases(query)` | Prior incidents with resolution notes |
| `search_internal_policies(query)` | Company SOPs |
| `search_legal_opinions(query)` | External counsel opinions |
| `get_document_by_id(doc_id)` | Fetch one document's full text |

**Output:** `{"solutions": [{finding_id, proposal, cited_doc_ids, rationale}]}`

**Enforcement:** Every solution MUST cite ≥1 document id. Solutions without citations are dropped at the graph-node boundary.

### Notifier

**File:** `multi_agent/agents/notifier.py`  
**Prompt:** `multi_agent/prompts/notifier.md`

**Job:** Identify affected departments, draft notifications, draft a follow-up meeting agenda.

**Tools:**
| Tool | What it does |
|---|---|
| `list_departments()` | Full department directory (7 depts) |
| `find_departments_for_topics(topics)` | Match keyword topics to departments |

**Output:** `{"notifications": [{department_id, subject, body, related_finding_ids}], "meeting_agenda": {title, attendees, items}}`

---

## 7. Two human-in-the-loop gates

LangGraph's `interrupt_before=["fan_out", "fan_in"]` pauses the graph **before** those nodes run. The CLI handler reads the pending state, prompts the user, injects the user's decisions via `graph.update_state(...)`, then resumes with `graph.invoke(Command(resume=True), ...)`.

### Gate 1 — Confirm findings (before `fan_out`)

For each potential finding (sorted Critical → Low), the user sees:
- the verbatim transcript quote and speaker
- the regulation article and severity
- the max fine
- the responsible department

…and answers `[y/N]`. Only confirmed findings flow downstream.

Once the user resumes, `fan_out` fires both parallel branches simultaneously:
- **Branch A (notifier)** — immediately alerts each affected department and proposes a cross-functional meeting.
- **Branch B (legal_researcher)** — searches the company knowledge base and drafts remediation solutions.

### Gate 2 — Approve solutions (before `fan_in` → `report_generator`)

Both parallel branches must finish before Gate 2 fires. At this point the legal team has already received their notifications. The user sees each proposed solution:
- the proposal text
- the cited company-database document ids (evidence)
- the rationale

…and answers `[a]pprove / [e]dit / [r]eject`. Edited solutions store the user's replacement text under `user_edited_proposal` so the audit trail records human modifications. Rejected solutions are dropped.

Implementation: `multi_agent/nodes/human_review.py`.

---

## 8. Evidence chain and severity scoring

### Evidence chain (enforced)

Every finding in the final report carries **three linked elements**:

```
transcript_quote  →  regulation_reference  →  precedent_doc_ids
(who said what)      (which law it breaks)    (company history)
```

System prompts require all three. The graph nodes enforce defensively:

| Guard | Where | What happens |
|---|---|---|
| `regulation_id` not in policy library | `graph.py::_enrich_finding` | Finding **dropped** |
| `cited_doc_ids` empty | `graph.py::_solution_from_raw` | Solution **dropped** |

So even if the LLM hallucinates, the report stays clean.

### Severity scoring

Each regulation article carries `severity` and `max_fine`. Findings inherit from the article they violate. The report sorts Critical → Low.

| Severity | Examples | Max fine |
|---|---|---|
| **Critical** | GDPR Art 9 (health data), Art 44–49 (intl transfer), Cosmetics Art 10 (safety), Art 14 (restricted substances) | EUR 20M or 4% turnover / product withdrawal |
| **High** | Cosmetics Art 18 (animal testing), Art 8 (GMP), GDPR Art 6/7 | National authority fines + market action |
| **Medium** | Cosmetics Art 13 (CPNP), Claims criteria 1/4, GDPR Art 25/35 | National authority fines |
| **Low** | Labelling (Art 19), claims criteria 5/6 | Warning letters |

---

## 9. Policy dictionaries

24 regulation articles across three modules, all keyed by stable id:

| Module | File | Articles |
|---|---|---|
| EU Cosmetics Regulation EC 1223/2009 | `policies/eu_cosmetics.py` | Art 3, 8, 10, 11, 13, 14, 18, 19, 20 |
| EU Claims Regulation 655/2013 | `policies/claims_regulation.py` | 6 common criteria + cruelty-free guidance |
| GDPR EU 2016/679 | `policies/gdpr.py` | Art 6, 7, 9, 13, 25, 28, 35, 44–49 |

Every article follows the same dict schema:

```python
{
    "id": "GDPR-ART9",                          # stable unique key
    "regulation": "GDPR (EU 2016/679)",
    "article": "Article 9",
    "title": "Special Categories of Personal Data",
    "requirements": "<plain-English summary>",
    "violation_indicators": ["health data", "skin photos", "biometric", ...],
    "severity": "Critical",
    "max_fine": "Up to EUR 20M or 4% global annual turnover (Art 83(5))",
    "responsible_department": "Data Protection Office / R&D / Digital",
}
```

`violation_indicators` is a keyword list the LLM uses for matching. `policies/__init__.py` exposes `ALL_REGULATIONS` (dict by id) and `get_regulation(id)`.

---

## 10. Company database (fake)

`multi_agent/data/company_database.py` — four in-memory collections:

| Collection | Count | Key fields |
|---|---|---|
| `PAST_CASES` | 5 | summary, outcome, **resolution_notes**, regulation_ids, tags |
| `INTERNAL_POLICIES` | 5 | summary, version, owner_department, regulation_ids |
| `LEGAL_OPINIONS` | 4 | summary, **recommended_actions**, author, regulation_ids |
| `DEPARTMENT_DIRECTORY` | 7 | name, lead, email, owns_topics |

Search uses simple case-insensitive keyword matching. **Not vector RAG** — keeps the demo self-contained. To go to production, swap this module for a vector store; nothing else changes.

---

## 11. Meeting scenarios

Two fake meetings in `multi_agent/data/meetings.py`:

### `meeting-glow-001` — 7 decisions (default)

Glow Sérum product launch go/no-go review.

| Decision | Regulation | Severity |
|---|---|---|
| "Clinically proven 80% wrinkle reduction" | Claims Crit 3 / Cosmetics Art 20 | High |
| New peptide, no safety assessment | Cosmetics Art 10 | Critical |
| "100% Natural & Organic" without certification | Claims Crit 2 | Medium |
| Skin photos + health questionnaire | GDPR Art 9, Art 35 | Critical |
| Share data with US analytics firm | GDPR Art 44–49, Art 28 | Critical |
| "Cruelty-Free" but supplier animal-tested | Cosmetics Art 18 | High |
| Skip CPNP re-notification | Cosmetics Art 13 | Medium |

### `meeting-glow-002` — 10 decisions (wide coverage)

Production & go-to-market readiness. Exercises **every regulation article**, **all DB collections**, and **all 7 departments**.

| Decision | Regulation | Severity |
|---|---|---|
| Manufacture at unaudited facility | Cosmetics Art 8 (GMP) | High |
| MIT preservative in leave-on product | Cosmetics Art 14 (restricted) | Critical |
| Incomplete PIF | Cosmetics Art 11 | Medium |
| Missing INCI / batch / PAO on packaging | Cosmetics Art 19 | Low |
| "Only sérum that works" | Claims Criterion 4 (honesty) | Medium |
| Denigrating competitors | Claims Criterion 5 (fairness) | Low |
| Pre-ticked bundled consent | GDPR Art 7 | High |
| "Collect everything, decide later" | GDPR Art 25 (by design) | Medium |
| No lawful basis for skin scans | GDPR Art 6 | High |
| Delay privacy notice update | GDPR Art 13 | Medium |

```bash
python run_multi_agent_demo.py meeting-glow-002
```

---

## 12. Running and debugging

### Normal run

```bash
python run_multi_agent_demo.py                      # meeting-glow-001
python run_multi_agent_demo.py meeting-glow-002     # wider coverage
```

### Verbose diagnostics

```bash
COMPLIANCE_DEBUG=1 python run_multi_agent_demo.py meeting-glow-002
```

Prints: raw final LLM message from each agent, parsed keys, message count. Use this when findings or solutions are unexpectedly empty.

### Common issues

| Symptom | Likely cause | Fix |
|---|---|---|
| `GraphRecursionError` | Inner-agent recursion limit too low | Increase `INNER_AGENT_RECURSION_LIMIT` in `config.py` |
| 0 findings on a meeting that should flag issues | Agent emitted free text instead of JSON, or JSON truncated | `COMPLIANCE_DEBUG=1` and inspect the last message |
| `RuntimeError: ANTHROPIC_API_KEY is not set` | `.env` missing or key empty | Check `.env` exists at project root |
| Solution dropped from report | `cited_doc_ids` was empty (evidence-chain enforcement) | Check `COMPLIANCE_DEBUG` output |

### Output format

Saved to `reports/compliance_report.json`:

```json
{
  "generated_at": "2026-05-22T13:45:00+00:00",
  "meeting_id": "meeting-glow-002",
  "summary": {
    "total_findings": 10,
    "by_severity": {"Critical": 1, "High": 4, "Medium": 4, "Low": 1},
    "total_solutions": 9,
    "total_notifications": 6
  },
  "findings": [
    {
      "id": "finding-001",
      "severity": "Critical",
      "evidence_chain": {
        "transcript_quote": "...",
        "regulation": {"id": "...", "article": "...", "title": "..."},
        "precedent_doc_ids": ["case-2024-001", "POL-DPO-001"]
      },
      "approved_solutions": [{"proposal": "...", "cited_doc_ids": [...]}]
    }
  ],
  "notifications": [...],
  "meeting_agenda": {"title": "...", "suggested_attendees": [...], "agenda_items": [...]}
}
```

---

## 13. Extending the system

### Add a new regulation article

1. Append a new entry to the appropriate file in `multi_agent/policies/`, following the standard schema.
2. Done. The analyst picks it up via `list_all_regulations()`.

### Add a new agent

1. Write a prompt in `multi_agent/prompts/<name>.md`.
2. Build a tool group in `multi_agent/tools/<name>_tools.py`.
3. Create a builder in `multi_agent/agents/<name>.py`.
4. Add a node function and edge in `multi_agent/graph.py`.

### Swap fake data for a real database

Replace `multi_agent/data/` with a real adapter exposing the same function signatures (`list_decisions`, `search_past_cases`, etc.). Nothing else changes.

### Roadmap (v2 — not implemented)

- **Remediation Drafter agent** — between Gate 2 and the Notifier; drafts action items with deadlines, owners, success criteria.
- **Policy version tracking** — `version` and `last_updated` fields already exist in the schema; add a diff tool to detect regulation changes.
- **Vector search** — replace keyword matching with embeddings when the company DB grows past ~100 documents.
