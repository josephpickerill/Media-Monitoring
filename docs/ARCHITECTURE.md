# Architecture

## Layers

### 1. External ingestion → `Signal`
Pluggable source adapters, each producing normalised `Signal` records (see `src/briefing/schemas.py`).

| Source type | Examples | Notes |
|---|---|---|
| News & broadcast | Licensed monitoring API (Meltwater, Cision, Agility, Signal AI) or Event Registry / Newsdata.io for a pilot | Store headline, outlet, URL, date, licensed excerpt/summary. Don't store full text unless your licence allows it. |
| Social | Provider API or your monitoring vendor's social feed | Keep author handle + follower reach for "who said it" weighting. |
| Legislative | UK Hansard & Bills APIs; Congress.gov; LEGISinfo/OpenParliament; EUR-Lex | Track bill stage changes, amendments, committee sessions, written questions mentioning tracked entities. |
| Regulatory / government | GOV.UK search & Atom feeds, Federal Register, Regulations.gov, regulator press pages | Consultations open/close dates are high-value "what to do" triggers. |

Every adapter: idempotent (`source_id` unique), polls on a schedule or receives webhooks, records raw payload hash for audit.

**Story clustering.** Ten outlets covering the same announcement must become one `Story`, not ten alerts. Cluster by embedding similarity + shared entities within a 48h window. Briefs are written about stories; signals are the citations.

### 2. Internal context → `WorkContextCard` (not raw email embeddings)

The earlier thread suggested embedding every user's last 14–30 days of email into a vector store. This kit does something different, for privacy, cost and quality reasons:

- A **weekly (plus on-demand) distillation job** reads the user's recent mail and calendar via Microsoft Graph (or Gmail/Calendar), applies exclusions and redaction, and asks Claude to produce a short structured **Work Context Card**: active issues, key stakeholders and how the user relates to them, upcoming meetings/deadlines, open commitments.
- **Raw email is never persisted.** Only the card is stored (plus message IDs for provenance, so a brief can link back to "your thread with X").
- **The user can see and edit their card** in the web inbox. This is the single biggest trust feature: people accept "it reads my email" much more readily when they can see exactly what it concluded and correct it.
- Cards are small (≈1–2k tokens), so they go straight into the synthesis prompt. No vector search needed for most users. Add per-user retrieval over recent thread *summaries* later only if evaluation shows cards miss things.

Use **delta queries + change notifications** in Graph (not polling 50 messages) so updates are cheap, and refresh a card immediately when a new thread with a tracked stakeholder appears.

### 3. Profiles
- `OrgProfile`: mission, strategic priorities, known risks, competitors, live issues & crisis playbooks, tone of voice, who's authorised to say what.
- `RoleProfile` per user: role type, mandates, tracked entities (bills, committees, ministers/MPs, journalists, NGOs, competitors), authority level (what they can action without sign-off), delivery preferences.
- Admins edit Org; users edit their own Role within guardrails set by admins.

### 4. Relevance: a funnel, not a fan-out

The earlier thread ran an LLM call per signal × per user. At 5,000 signals/day × 200 users that's a million calls a day. Use a funnel instead:

| Stage | Method | Cost | Purpose |
|---|---|---|---|
| A. Hard match | Entity/keyword/bill-ID match against Org + Role tracked entities | ~free | Catches the obvious. |
| B. Semantic match | Embedding similarity: story vs. each user's card + mandates | cheap | Catches "this matters but doesn't name us". Anthropic has no embeddings endpoint; use Voyage AI, Azure OpenAI embeddings, or a local model (e.g. `bge`/`e5`) in pgvector. |
| C. Triage | Claude Haiku 5.5, one call per (story, candidate user), returns score 0–1 + one-line reason + urgency | low | Decides "brief / digest / ignore". |
| D. Synthesis | Claude Opus 5.5 (structured output), only for stories that pass C | the real spend | Writes what / why / do + draft. |

Urgency routing: `immediate` → Teams card now; everything else → into the morning digest, generated overnight by a bounded worker pool. (On the Anthropic API you'd use the Message Batches API for 50% off; it isn't offered on Microsoft Foundry, which we chose. See DECISIONS.md §5.)

### 5. Synthesis
See `src/briefing/synthesis.py`. Key rules:
- Structured output (Pydantic) via `client.messages.parse` on an `AnthropicFoundry` client. Refusals are logged and skipped.
- Every factual claim cites a `signal_id`; every "why it matters" claim cites the card item it relies on. Unciteable claims are dropped. This is what stops it inventing meetings.
- The model never sees another user's card. Org-level context is shared; personal context is not.
- Org profile + role guidance go first in the prompt and are prompt-cached; the story and card go last.

### 6. Delivery and the human loop
- Teams adaptive card / email digest / web inbox.
- Buttons: **Open draft in Outlook** (creates a draft via Graph, never sends), **Useful**, **Not relevant**, **Wrong reason**, **Already knew**.
- Feedback adjusts per-user thresholds and is the dataset for evaluation (Phase 6).
- **Escalation:** when synthesis flags `Reputation_Risk` with high severity, notify the designated issue owner(s) from the Org profile, not just the person whose card matched.

## Stack

| Concern | Choice | Why |
|---|---|---|
| Language / API | Python 3.12, FastAPI | Matches the earlier thread; good SDKs for Graph and Anthropic. |
| Jobs | Postgres-backed queue (Procrastinate) or Celery + Redis to start; Temporal if workflows get complex | Don't take on Temporal until you need durable multi-step sagas. |
| Database | PostgreSQL + pgvector, Row-Level Security on `tenant_id` and `user_id` | One store for relational, audit and vectors. |
| Auth | Entra ID (OIDC) for users; Graph via **delegated** permissions with per-user opt-in | Application-wide `Mail.Read` reads every mailbox incl. the CEO's; security teams rightly refuse it. If you must use app permissions, scope them with Exchange RBAC for Applications to a pilot group. |
| LLM platform | Claude on Microsoft Foundry | Billed on the Microsoft agreement, Entra-aligned, region chosen per deployment. |
| LLM | Claude Opus 5.5 (synthesis, card distillation), Claude Haiku 5.5 (triage) | Opus 5.5 is the current default; Haiku is ~40x cheaper for high-volume yes/no work. |
| Hosting | Your cloud (Azure fits M365 shops). Containers + managed Postgres. | Keeps email-derived data in your estate. |
| Observability | OpenTelemetry + structured logs; LLM call log with prompt hash, model, tokens, cost, latency | You will need cost per user per day and an audit trail. |

## Corrections to the earlier thread, in one list
1. Model names were out of date and the code called OpenAI. This kit uses the Anthropic SDK with Claude Opus 5.5 / Haiku 5.5. `temperature` is no longer accepted on current Claude models; use the `effort` setting instead.
2. Fetching Gmail with `format=metadata` gives only a ~200-character snippet, which is too thin to reason over. Fetch bodies, strip quoted replies/signatures, redact, distil, then discard.
3. Per-signal × per-user LLM fan-out doesn't scale. Use the 4-stage funnel above.
4. Raw-email vector stores are a large privacy liability with modest quality gain. Use editable Work Context Cards.
5. Media licensing and employee-privacy law were missing. They're in `GOVERNANCE.md`.
6. Skipping the no-code validation step. Phase 0 tests the core value in two weeks before you write the pipeline.
