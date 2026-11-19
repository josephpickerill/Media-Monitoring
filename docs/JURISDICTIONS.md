# Jurisdictions: Canada, UK, EU, USA (+ coverage about China)

Each jurisdiction is a set of **source adapters** (see ARCHITECTURE.md §1) plus **legal rules** that apply to processing and outreach there. Before writing any adapter, Claude Code must read that source's current official API documentation and terms of use. The lists below say where to look; they don't describe exact endpoints.

All adapters produce `Signal` records with `jurisdiction`, `language` and, for non-English sources, an English `excerpt_en`. Keep the original-language text too, because officials and journalists will be quoted in the original.

---

## UK  (build first: best open data)

| Need | Source |
|---|---|
| Debates, statements, mentions of tracked entities | Hansard API (Commons & Lords) |
| Bills, stages, amendments | UK Parliament Bills API |
| Written questions & ministerial statements | UK Parliament Written Questions & Statements API |
| Committees, inquiries, evidence calls | UK Parliament Committees API |
| Members (MPs/peers, roles, constituencies) | UK Parliament Members API |
| Legislation & statutory instruments | legislation.gov.uk API/feeds |
| Consultations, policy papers, announcements | GOV.UK Search API & Atom feeds (filter by department/topic) |
| Devolved | Scottish Parliament, Senedd, NI Assembly open data (add if relevant) |

**Rules:** UK GDPR + Data Protection Act 2018; ICO employment monitoring guidance (transparency to staff). Open Parliament Licence attribution. GR drafts to ministers/permanent secretaries may be registrable under the Consultant Lobbying Register if you act for third parties.

## USA

| Need | Source |
|---|---|
| Bills, actions, cosponsors, committee reports, Congressional Record | Congress.gov API (api.data.gov key) |
| Rules, proposed rules, notices, executive orders | Federal Register API |
| Dockets & comment deadlines | Regulations.gov API |
| Official documents (bill text, hearings) | GovInfo API |
| State legislatures (all 50) | Open States (Plural) or LegiScan API |
| Agency press releases | Agency RSS feeds |

**Rules:** No federal GDPR equivalent, but state privacy laws (e.g. California CPRA covers employee data) and state laws requiring notice of electronic monitoring of employees (e.g. New York, Connecticut, Delaware). Lobbying Disclosure Act + state lobbying registration: flag GR drafts.

## Canada  (English + French)

| Need | Source |
|---|---|
| Bills and stages | LEGISinfo (Parliament of Canada; JSON/XML) |
| Debates, votes, MPs | House of Commons open data; OpenParliament.ca API |
| Regulations (proposed & final) | Canada Gazette Part I & II |
| Consultations | Consulting with Canadians (canada.ca) |
| Departmental news | canada.ca news feeds (filter by department) |
| Provinces | Ontario, Quebec, BC, Alberta legislatures (add those that matter) |

**Rules:** PIPEDA; **Quebec Law 25** requires a privacy impact assessment before transferring personal information outside Quebec (relevant if Quebec-based staff opt in). Federal Lobbying Act + Commissioner of Lobbying registry, plus provincial registries: flag GR drafts. Briefs for French-speaking users should be generated in French (set `language` on the RoleProfile).

## EU  (24 languages)

| Need | Source |
|---|---|
| Legislation, proposals, Official Journal | EUR-Lex (web service / Cellar SPARQL) |
| Legislative procedure tracking | European Parliament Legislative Observatory (OEIL) |
| MEPs, plenary, committees, votes | European Parliament Open Data Portal API |
| Commission consultations & feedback | "Have Your Say" portal |
| Commission press | Commission Press Corner feeds |
| Council | Council press releases & meeting calendar |
| Member states | Add national parliaments/ministries for priority member states |

**Rules:**
- GDPR. The DPIA is mandatory in practice. Works councils (e.g. Germany, France, Netherlands) must often be consulted before email-reading tools are deployed. Plan months, not weeks.
- **EU AI Act:** AI systems used to *monitor or evaluate the performance and behaviour of workers* are high-risk (Annex III). This tool must **never** be used for performance assessment, and the product terms and UI should say so. Have counsel confirm the classification.
- Data residency: EU users' context cards stored in EU region; check Claude platform/region options for EU processing (DECISIONS.md §5).
- EU Transparency Register: flag outreach drafts to Commission/Parliament officials.

## China: coverage about China

Scope, sources (South China Morning Post first) and triggers are in `docs/DECISIONS.md` §3a. China is handled as **media coverage**, not as a government-relations jurisdiction: no Chinese official sources, no China-based mailboxes, and no PIPL data-export work. China stories reach users through the media adapters plus a `china` topic tag applied to signals from all sources, including UK/EU/US/Canadian legislative items about China.

---

## Cross-cutting implications for the build

1. `Signal` gains `jurisdiction`, `language`, `excerpt_en`. `RoleProfile` gains `jurisdictions`, `language` (brief language), `timezone`, `context_source` (`email_and_calendar` | `role_only`, for users who haven't opted in).
2. **Translation:** non-English excerpts translated by Claude Haiku 5.5 at ingestion (cached); synthesis sees the English excerpt plus the original.
3. **Data residency by user region:** store context cards in a region matching the user (UK, EU, US, Canada). Design the `work_context_cards` table to be partitionable by region from Phase 1.
4. **Digest timing by time zone:** a morning digest at 07:00 local means several delivery windows (North America and Europe).
5. **Per-jurisdiction outreach flag:** `possible_registrable_lobbying` plus the jurisdiction, so the UI can say *which* register might apply.
6. **Source health dashboard:** with ~40 adapters, something will always be broken. Track last successful fetch and signals/day per adapter.
