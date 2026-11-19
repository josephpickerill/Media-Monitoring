# Build plan

Each phase has a **prompt to paste into Claude Code** and a **done when** list. Do one phase per session or PR. Commit at the end of each phase. If a phase's "done when" isn't met, don't start the next one.

---

## Phase 0 — Validate the value with no code (1–2 weeks)

Before building a pipeline, check that "why it matters to *you*" is actually good for your people.

1. In Claude (claude.ai, Team/Enterprise), connect the **Microsoft 365** (or Google Workspace) connector.
2. Create a Project per pilot role. Paste that person's `RoleProfile` (from `docs/DECISIONS.md` §6) and your Org profile into the project instructions.
3. Each morning, paste in 10–20 real items from your current monitoring alerts / Hansard / regulator feeds, and run this prompt:

```
Here are today's media, parliamentary and regulatory items. Using my role profile in the project
instructions, and by searching my Outlook mail and calendar for the last 3 weeks, give me only the
items that genuinely matter to me (max 5). For each:
1) What happened (2 sentences, cite the item)
2) Why it matters to me specifically: name the email thread, meeting or commitment it touches
3) What I should do, and a ready-to-edit draft (statement / outreach email / briefing note)
Then list anything you excluded that a person in my role might expect to see, with one line why.
```

4. Have each pilot user rate every item: Useful / Not relevant / Wrong reason / Already knew.

**Done when:** you have ≥ 50 rated items, and ≥ 60% are "Useful". Keep the rated items: they become your evaluation set in Phase 6. If it's well below 60%, fix the profiles and prompt before building anything.

---

## Phase 1 — Skeleton, data model, tenancy

```
Read CLAUDE.md, docs/ARCHITECTURE.md and docs/DECISIONS.md.
Set up the project skeleton: Python 3.12, uv, FastAPI, SQLAlchemy 2 + Alembic, PostgreSQL 16 with
pgvector via docker-compose, pytest, ruff, mypy. Create Alembic migrations for: tenants, users,
org_profiles, role_profiles, work_context_cards, signals, stories, story_signals, briefs,
feedback, llm_calls (audit + cost), and source_cursors. Every table has tenant_id; personal tables
also have user_id. Enable Postgres Row-Level Security so a session with app.user_id set can only
read its own personal rows, and write a pytest that proves user A cannot read user B's card or
briefs even with a hand-written query. Reuse the Pydantic models in src/briefing/schemas.py as the
API schemas. Add a seed script that loads the pilot users from docs/DECISIONS.md.
```

**Done when:** `docker compose up` + `pytest` pass, including the RLS cross-user test; seed data loads.

---

## Phase 2 — External ingestion

```
Implement source adapters under src/briefing/sources/, each implementing a SourceAdapter protocol
(fetch_since(cursor) -> list[Signal], idempotent on source_id, cursor persisted in source_cursors).
Start with: (1) <your news API from DECISIONS.md §4>, (2) UK Parliament Bills + Hansard APIs,
(3) GOV.UK Search API. Then follow docs/JURISDICTIONS.md in the order UK → US → Canada → EU →
China, one PR per jurisdiction. Non-English signals get excerpt_en via Claude Haiku 5.5 at
ingestion. Add a source-health table (last success, signals/day) and alert on silent adapters. Read each API's official docs before writing
code; don't guess endpoints. Store licensed excerpt + metadata, not full text unless
LICENCE_ALLOWS_FULLTEXT is set. Add entity extraction (people, orgs, bills, committees, places)
using Claude Haiku 5.5 with structured output, cached per signal. Add story clustering: embed
headline+excerpt with the embedding provider in settings, cluster within a 48h window by cosine
similarity >= 0.82 plus at least one shared entity. Schedule adapters with the job queue. Add
recorded-response tests (vcrpy or saved JSON fixtures) for every adapter.
```

**Done when:** a 24h run produces deduplicated stories with correct entity tags; tests run offline.

---

## Phase 3 — Internal context: Work Context Cards

```
Read docs/JURISDICTIONS.md (cross-cutting section and China section) first.
Implement Microsoft Graph integration with delegated OAuth (MSAL, auth code flow) and per-user
opt-in. Scopes: Mail.Read, Calendars.Read, offline_access, User.Read. Store refresh tokens
encrypted (Fernet key from env for now; Key Vault later). Use Graph delta queries for mail and
calendar. Before any text reaches an LLM, apply in this order: (1) exclusions from DECISIONS.md §8
and Purview sensitivity labels, (2) strip quoted replies and signatures, (3) Presidio redaction.
Then distil a WorkContextCard (schema in src/briefing/schemas.py) with Claude Opus 5.5 using
structured output; every card item must carry the Graph message/event IDs it came from. Never
persist message bodies; add a test that fails if a body string appears in the database after a
distillation run. Add GET/PUT /me/context-card so users can view and edit their card; user edits
are pinned and survive re-distillation. Users with context_source="role_only" (China-based staff,
anyone not opted in) are never connected to Graph. Store each card in the user's data_region. Refresh weekly, plus immediately when a delta brings a
new thread with a tracked stakeholder.
```

**Done when:** each pilot user's card looks right *to them*; the "no bodies at rest" test passes.

---

## Phase 4 — Relevance funnel

```
Implement the 4-stage relevance funnel from docs/ARCHITECTURE.md §4 in src/briefing/relevance.py:
A) hard entity/keyword match against org + role tracked entities, B) embedding similarity between
story and each user's card items and mandates, C) triage with Claude Haiku 5.5 returning
TriageResult (schema in schemas.py) for candidates passing A or B, D) enqueue synthesis for
triage score >= the user's threshold (default 0.7). Log every stage decision with its score so
we can explain "why did/didn't I get this". Add a CLI: `briefing explain <story_id> <user_id>`
that prints the funnel trace.
```

**Done when:** on a day of real data, each pilot user has 3–10 candidate stories, and `explain` traces make sense.

---

## Phase 5 — Synthesis and delivery

```
Wire src/briefing/synthesis.py into the pipeline. Urgency "immediate" → synthesise now and post a
Teams adaptive card via a bot (Bot Framework / Teams app) or Graph chat message; everything else →
nightly batch using the Message Batches API, then one email digest per user at 07:00 in their
own timezone (users span Canada, UK, EU, US and China). Validate that every claim in a brief cites a signal_id or card item id that exists and
belongs to that user; drop and log any brief that fails. Add buttons: Open draft in Outlook
(Graph create draft, Mail.ReadWrite, never send), Useful, Not relevant, Wrong reason, Already
knew → POST /feedback. Build a minimal web inbox (FastAPI + HTMX is fine) listing briefs with
sources, the card items used, and the feedback buttons. Add Reputation_Risk escalation to issue
owners defined in the org profile.
```

**Done when:** pilot users receive digests and Teams cards for a week; feedback is recorded.

---

## Phase 6 — Evaluation and tuning

```
Build an eval harness in evals/: load the Phase 0 rated items plus all Phase 5 feedback as cases.
Metrics: precision (Useful / delivered), "wrong reason" rate, citation validity, draft
acceptance (draft opened & edited lightly). Add an LLM-judge (Claude Opus 5.5) that scores a brief
against a rubric: factual accuracy vs. sources, specificity of "why it matters", actionability,
tone matches org profile, no leakage of other users' context. Run the eval on every prompt or
model change in CI and fail if precision drops > 5 points. Use feedback to adjust per-user
thresholds weekly.
```

**Done when:** you have a baseline score and a CI gate; changes are measured, not eyeballed.

---

## Phase 7 — Harden and scale

```
Production hardening: move secrets to Azure Key Vault; managed Postgres with PITR backups;
OpenTelemetry tracing; per-tenant and per-user daily LLM cost dashboards and hard budget caps;
retry/backoff for every external API; admin UI for org profile, role templates, exclusions and
source configuration; tenant onboarding flow (Entra admin consent, role template selection);
data-subject export and delete endpoints; load test at 10x pilot volume.
```

**Done when:** governance checklist (`docs/GOVERNANCE.md`) is fully ticked and signed off.

---

## Rough running cost (pilot, ~20 users)

Order of magnitude only; measure in Phase 5 from the `llm_calls` table.
- Triage (Haiku 5.5): thousands of short calls/day, a few dollars/day.
- Synthesis (Opus 5.5): ~5–10 briefs/user/day × 20 users, mostly via Batches at 50% off, roughly tens of dollars/day.
- Card distillation: weekly, small.
- The licensed media feed will usually cost more than the AI.
