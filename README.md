# Briefing Engine — build kit

An enterprise intelligence tool that watches media, parliament/regulators and stakeholders, and tells **each person in the organisation**:

1. **What happened** — the facts, with sources.
2. **Why it matters to you** — tied to your role, and to what you're actually working on right now (from your email and calendar).
3. **What to do about it** — a concrete recommendation plus a draft (holding statement, MP/official outreach note, stakeholder email, board paragraph).

One deployment serves the whole organisation; PR, Government Relations, Stakeholder Relations and Executive/Strategy users each get a different brief from the same event.

## What's in this folder

| File | Purpose |
|---|---|
| `CLAUDE.md` | Standing instructions Claude Code reads every session. Architecture, rules, guardrails. |
| `docs/ARCHITECTURE.md` | The system design, and where it differs from the earlier thread's advice (and why). |
| `docs/BUILD_PLAN.md` | **Start here.** Phase 0–7, each with a copy-paste prompt for Claude Code and a "done when" checklist. |
| `docs/JURISDICTIONS.md` | Sources and legal rules for Canada, UK, EU, China and USA. |
| `docs/GOVERNANCE.md` | Privacy, legal and licensing work you must do in parallel. Not optional for an email-reading enterprise tool. |
| `docs/DECISIONS.md` | The decisions only you can make, to fill in before Phase 1. |
| `src/briefing/schemas.py` | Data models: org profile, role profile, work-context card, signal, brief. |
| `src/briefing/synthesis.py` | The "what / why / what to do" generator, already written against the current Claude API. |

## How to use this with Claude Code

1. Put this folder in a GitHub repo (or ask me to push it to one).
2. Fill in `docs/DECISIONS.md` (30 minutes; it shapes everything else).
3. Do **Phase 0** in `docs/BUILD_PLAN.md` first. It costs no code and tells you whether the "why it matters" output is good enough to justify the build.
4. Then open Claude Code in the repo and paste the Phase 1 prompt. One phase per session (or per PR). Don't skip the "done when" checks.

## The short version of the architecture

```
 External sources ──► Ingest & normalise ──► Cheap filter ──► Triage (Haiku) ──► Synthesis (Opus) ──► Review & deliver
 (news API, social,     (dedupe, entities,    (entity + topic    per role/user      what / why / do        (Teams card, email
  Hansard, bills,        clustering into        match against     "is this worth      + draft, citing        digest, web inbox;
  regulators)            "stories")             profiles)         a brief?")         sources)               human sends, never the bot)
                                                     ▲
 Internal context ──► Distil into per-user "Work Context Cards" ──┘
 (M365 Graph or Google:  (active issues, stakeholders, deadlines;
  mail, calendar)         user can see & edit; raw email not stored)
```
