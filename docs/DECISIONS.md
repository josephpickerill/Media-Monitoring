# Decisions to make before Phase 1

Fill these in. Claude Code reads this file, so your answers flow straight into the build.

## 1. Workspace ecosystem
- [x] Microsoft 365 (Outlook, Teams, Entra ID)
- [ ] Google Workspace (Gmail, Chat, Google SSO)
- [ ] Both (multi-tenant product sold to other organisations)

## 2. Who is it for, first?
- [ ] Internal tool for one organisation (simplest: single tenant)
- [ ] Product for client organisations (multi-tenant from day one; adds tenant isolation, onboarding, billing)

Recommendation: build single-tenant with a `tenant_id` column everywhere, so multi-tenant is a later switch, not a rewrite.

## 3. Jurisdictions for government relations
- [x] Canada
- [x] UK
- [x] EU
- [x] USA
- [x] China: **media coverage about China only** (see 3a). No Chinese government sources, no China-based mailboxes.
- [ ] Devolved / state / provincial: ______

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
- [ ] Existing contract with Meltwater / Cision / Agility / Muck Rack / Signal AI → use its API
- [ ] Budget news API (Event Registry / NewsAPI.ai, Newsdata.io) for a pilot
- [ ] Social: X, LinkedIn, Reddit — which matter for your stakeholders?

Check your licence permits (a) API access, (b) internal redistribution of summaries, (c) sending text to an AI model. See GOVERNANCE.md §3.

## 5. Where the AI runs
- [ ] Anthropic API directly (simplest; ask for zero-data-retention on your org)
- [ ] Claude on Microsoft Foundry (billing via Azure, stays in your Microsoft estate)
- [ ] Claude on Amazon Bedrock / Google Vertex
Data residency requirement (UK / EU / US only?): ______

## 6. Pilot roles and people (3–6 people)
| Person | Role type | Title | 3 mandates they're measured on |
|---|---|---|---|
| | PR_Comms | | |
| | Gov_Relations | | |
| | Stakeholder_Relations | | |
| | Executive_Strategy | | |

## 7. Delivery
- [ ] Teams adaptive card (real-time, for high-urgency items)
- [ ] Morning email digest (default for everything else)
- [ ] Web inbox (needed anyway for feedback and admin)
- Morning digest time & time zone: ______

## 8. Hard exclusions
Mailboxes, folders, labels, senders or sensitivity labels that must never be read (e.g. Legal, HR, Board-confidential, "Privileged"): ______
