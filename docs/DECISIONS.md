# Decisions

Claude Code reads this file, so these answers flow straight into the build. Items marked **TBC** still need an answer before the phase noted next to them.

**Status (19 Nov 2026):** decided: workspace, audience, jurisdictions, media vendor approach, AI platform, delivery. Still open: pilot names (§6, before Phase 0), vendor contract confirmation (§4, before Phase 2), exclusions sign-off by DPO/Legal (§8, before Phase 3).

## 1. Workspace ecosystem
- [x] Microsoft 365 (Outlook, Teams, Entra ID)
- [ ] Google Workspace (Gmail, Chat, Google SSO)
- [ ] Both

## 2. Who is it for, first?
- [x] **Our own organisation first; client organisations later.**
- [ ] Clients from day one

Build rule: single tenant in practice, but `tenant_id` on every table, in every query and in RLS policies from Phase 1, so serving clients later is configuration (Entra admin consent per client tenant, onboarding, billing), not a rewrite. Don't build client onboarding or billing until we decide to.

## 3. Jurisdictions for government relations
- [x] Canada
- [x] UK
- [x] EU
- [x] USA
- [x] China: **media coverage about China only** (see 3a). No Chinese government sources, no China-based mailboxes.
- [ ] Devolved / state / provincial: **TBC** (not in the first build; add Scottish Parliament, US states, Ontario/Quebec etc. only when a pilot user's mandate needs them)

Government-relations sources and legal rules for Canada, UK, EU and USA are in `docs/JURISDICTIONS.md`. Build order: UK → US → Canada → EU, then China coverage.

## 3a. China: coverage *about* China

**Scope.** We track what international and Hong Kong media report about China (policy, trade, regulation, diplomacy, technology, markets) where it touches our organisation, sector, clients or stakeholders. We do **not** ingest media or official sources *from* mainland China, and we don't process email of staff based in mainland China. This keeps the build simple: no Chinese-language scraping, no data-export (PIPL) work, and no question of running the AI service in China.

**Anchor source: South China Morning Post (SCMP).** It's the most-read English-language outlet on China policy, and it's based in Hong Kong. Note that it's owned by Alibaba, so pair it with the outlets below for balance.

| SCMP section | Why it matters |
|---|---|
| China > Politics / Policies | Central policy direction, Party and State Council decisions |
| China > Diplomacy | Bilateral relations with Canada, the UK, the EU and the US; sanctions and retaliation |
| China > Military | Security issues that drive Western policy responses |
| Economy > China Economy | Trade, tariffs, export controls, investment rules |
| Business, Tech | Corporate and regulatory moves (data, AI, platforms, EVs, semiconductors) |
| Hong Kong (Politics, Economy) | Hong Kong policy and financial-centre developments |
| Opinion / Analysis | Elite and Hong Kong commentary; early signals of a change in tone |

How to get SCMP into the pipeline (pick one; Phase 2 adapter):
1. **Through your licensed monitoring vendor** (preferred). Check whether your Meltwater, Cision, Factiva or other contract includes SCMP full text. This also covers licensing for internal redistribution and AI processing.
2. **SCMP's public section RSS feeds** (scmp.com/rss) give headlines, standfirsts and links. These are fine for alerting and triage, but the feed terms may limit commercial use, so check before relying on them in production. *The feed URLs and terms haven't been verified yet: www.scmp.com wasn't reachable from the build environment. Claude Code should confirm them in Phase 2.*
3. **SCMP content licensing/syndication**, if you want full text without a vendor.

Within SCMP, add the reporters and columnists who cover your issues as `tracked_entities` (in the role profiles of GR and PR users), so their pieces score higher.

**Other outlets on China** (via the same vendor where possible): Reuters, Bloomberg, Financial Times, Nikkei Asia, The Economist, Wall Street Journal, Politico (China coverage), Caixin Global (English edition), plus think-tank output (e.g. MERICS for the EU angle, CSIS and Brookings for the US, Chatham House for the UK, the Asia Pacific Foundation of Canada).

**What "China" stories should trigger:** Chinese measures affecting our sector or clients (export controls, tariffs, sanctions, unreliable-entity listings, data rules); Western government action on China (in the UK/EU/US/Canada legislative feeds, tag `topic: china`); and China-linked reputational stories touching us, our clients or our stakeholders (supply chain, investment, partnerships).

**Revisit if:** we later add staff based in mainland China or want Chinese-language sources. Both bring in PIPL data-export rules and the fact that Claude isn't offered in mainland China, so they need legal sign-off first.

## 4. Media source (licensed)
- [x] **Choose an enterprise vendor now.** Lead candidate: **Meltwater** (global news, broadcast and social in one contract, with an API). Shortlist to compare: Cision, Signal AI.
- [ ] Budget news API for the pilot

Our requirements for the contract, in priority order (put these to each vendor in writing):
1. **API access** to mentions/articles with metadata, not just dashboards and email alerts. Ask for the API docs and rate limits.
2. **Coverage:** Canada (English and French), UK, EU (major languages), US national + trade press, broadcast transcripts, and **South China Morning Post** plus Reuters, Bloomberg, FT, Nikkei Asia, Caixin Global (see §3a). *None of this is confirmed yet; get the vendor's source list.*
3. **Licence terms** that allow: internal redistribution of excerpts and summaries to the number of users we plan; processing of content by an AI model (Claude on Microsoft Foundry); retention of excerpts for at least 90 days. See GOVERNANCE.md §3.
4. **Social:** X and LinkedIn first (where journalists, officials and stakeholders talk); Reddit only if a pilot user's stakeholders are there. Through the vendor, not direct platform APIs.
5. Price for ~20 pilot users, then 100–250.

- Vendor chosen: **TBC** (before Phase 2)
- SCMP included in contract: **TBC**
- AI-processing clause agreed: **TBC**

Fallback if the contract takes longer than Phase 1: build the Phase 2 adapters against Event Registry (NewsAPI.ai) behind the same `SourceAdapter` interface, then swap.

## 5. Where the AI runs
- [x] **Claude on Microsoft Foundry** (billed on our Microsoft agreement, sits alongside M365 and Entra ID)
- [ ] Anthropic API directly
- [ ] Amazon Bedrock / Google Vertex

What this means for the build (also in CLAUDE.md):
- Python client: `anthropic.AnthropicFoundry`. Deploy `claude-opus-5-5` (synthesis, context cards) and `claude-haiku-5-5` (triage, entity extraction, translation) in our Foundry resource.
- **No Message Batches API on Foundry.** The nightly digest runs as ordinary concurrent requests (bounded worker pool), so budget at full price rather than the 50% batch discount. Prompt caching does work on Foundry and is the main cost lever.
- **No server-side refusal fallback on Foundry.** A declined request returns `stop_reason: "refusal"`; we log it and skip the brief (client-side fallback middleware can be added later).
- **Data residency** is set by the Foundry deployment (region, and whether it's "Hosted on Azure" or "Hosted on Anthropic"), not per request. Choose this with IT/DPO before Phase 3. Requirement: process and store UK users' data in the UK/EU, EU users' in the EU, Canadian users' in Canada or with a documented transfer basis (Quebec Law 25 assessment for Quebec staff), US users' in the US. Context cards are stored in each user's `data_region` in our own Azure Postgres.
- Foundry deployment region(s) and hosting type: **TBC** (before Phase 3)

## 6. Pilot roles and people (3–6 people)

Pick people who'll give honest feedback daily for two weeks, ideally spread across at least two jurisdictions. The titles and mandates below are **starting templates**; replace them with each person's real ones (ask them: "what are the three things you'll be judged on this year?").

| Person | Location | Role type | Title (template) | Mandates (template) | Tracked entities (examples to replace) |
|---|---|---|---|---|---|
| **TBC** | **TBC** | PR_Comms | Head of Communications | 1. Protect and build reputation with Tier-1 media; 2. Respond to emerging issues within 2 hours; 3. Land proactive stories on strategic priorities | Tier-1 outlets and named journalists on our beat, incl. SCMP China reporters; competitors; spokespeople |
| **TBC** | **TBC** | Gov_Relations | Director, Government Relations | 1. Shape priority bills/regulations in UK, EU, US, Canada; 2. Maintain relationships with key ministers, officials, committee members; 3. Meet consultation deadlines with strong submissions | Specific bills, committees, ministers/MPs/MEPs/members of Congress, regulators; China trade/export-control measures |
| **TBC** | **TBC** | Stakeholder_Relations | Head of Stakeholder Engagement | 1. Keep key NGOs, investors, partners and communities informed before they read it in the press; 2. Spot shifts in stakeholder positions early; 3. Build coalitions on priority issues | Named NGOs, investor groups, industry associations, community groups, unions |
| **TBC** | **TBC** | Executive_Strategy | CEO / Chief Strategy Officer | 1. Deliver the strategic plan; 2. Anticipate regulatory and geopolitical risk (incl. China); 3. Keep the board ahead of material issues | Competitors, major clients, board-level risks, macro/geopolitical themes |
| *optional* | | Gov_Relations | GR lead, second jurisdiction (e.g. Brussels or Ottawa) | | |

For each pilot user also record: `language` (en/fr), `timezone`, `data_region` (UK/EU/US/CA), and whether they've opted in to email context (`context_source`).

## 7. Delivery
- [x] **Teams adaptive card** for `urgency = immediate` only (e.g. a Reputation_Risk story breaking, a bill amendment tabled for a vote today). Cap: 3 per user per day; anything beyond goes to the digest, so Teams stays a signal people trust.
- [x] **Morning email digest** at **07:00 in each user's own time zone**, Monday–Friday, max 7 items, ordered by severity. Weekend digest on Monday covers Fri 07:00 → Mon 07:00.
- [x] **Web inbox**: all briefs, sources, "why am I seeing this?", feedback buttons, edit-my-context-card, and admin (org profile, role templates, exclusions, sources).
- Quiet hours: no Teams cards 20:00–07:00 local, unless severity = high and implication = Reputation_Risk.

## 8. Hard exclusions

Proposed defaults below: enforced in code *before* any text reaches Claude (CLAUDE.md rule 3). **DPO and Legal must confirm this list before Phase 3. TBC.** Replace the bracketed names with our real labels, lists and domains.

**Never read: skip the whole message/event**
- Microsoft Purview sensitivity labels: [Highly Confidential], [Confidential – Legal], [Privileged], [Board], [HR], [Personal]. Get the real label names from IT; read labels via Graph and fail closed if the label can't be read.
- Messages marked Sensitivity = Private or Personal; calendar events marked Private.
- Folders: Legal, HR, Personal, Board, Deleted Items, Junk Email, Drafts, plus any folder the user adds in the web inbox.
- Distribution lists and shared mailboxes: [legal@], [hr@], [board@], [payroll@], [whistleblowing@], [it-security@].
- Senders/recipients at external counsel domains: [law firm domains]; anything with "privileged", "without prejudice" or "attorney-client" in the subject.
- Mailboxes of anyone who hasn't opted in, and all mailboxes outside the pilot group.

**Read but redact before Claude** (Presidio): personal phone numbers, home addresses, ID/passport numbers, bank details, health information, and other special-category data.

**Never stored anywhere:** email/calendar bodies (only Work Context Card items + Graph IDs).
