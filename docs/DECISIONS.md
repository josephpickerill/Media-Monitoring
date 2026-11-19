# Decisions to make before Phase 1

Fill these in. Claude Code reads this file, so your answers flow straight into the build.

## 1. Workspace ecosystem
- [ ] Microsoft 365 (Outlook, Teams, Entra ID)  ← build plan assumes this by default
- [ ] Google Workspace (Gmail, Chat, Google SSO)
- [ ] Both (multi-tenant product sold to other organisations)

## 2. Who is it for, first?
- [ ] Internal tool for one organisation (simplest: single tenant)
- [ ] Product for client organisations (multi-tenant from day one; adds tenant isolation, onboarding, billing)

Recommendation: build single-tenant with a `tenant_id` column everywhere, so multi-tenant is a later switch, not a rewrite.

## 3. Jurisdictions for government relations
- [ ] UK (Hansard, Parliament Bills API, legislation.gov.uk, GOV.UK search/feeds for consultations & policy papers)
- [ ] EU (EUR-Lex, Commission "Have your say", Parliament)
- [ ] US federal (Congress.gov API, Federal Register API, Regulations.gov)
- [ ] Canada (LEGISinfo, OpenParliament)
- [ ] Devolved / state / provincial: ______

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
