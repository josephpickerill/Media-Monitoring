# Governance, privacy and licensing

Run this alongside the build. An enterprise customer, or your own CISO / DPO, will ask about every item here before it goes past a pilot. This is a checklist, not legal advice; get your DPO and counsel to sign off.

Jurisdiction-specific rules (Canada incl. Quebec Law 25, UK, EU incl. AI Act, US state laws) are in `docs/JURISDICTIONS.md`. China is in scope as media coverage only (`docs/DECISIONS.md` §3a).

## 1. Employee email processing
- [ ] **DPIA** (UK/EU GDPR Art. 35): systematic processing of employee communications with AI is a textbook DPIA trigger.
- [ ] **Lawful basis:** usually legitimate interests plus opt-in. Make it opt-in per user, revocable, with deletion on opt-out.
- [ ] **Works councils / unions** in EU jurisdictions (e.g. Germany, France, Netherlands) may need to be consulted before any email-reading tool is deployed.
- [ ] **Third parties in emails** (journalists, officials, stakeholders) are data subjects too. Update the privacy notice; minimise what's kept about them.
- [ ] **Exclusions enforced in code before any LLM call:** sensitivity labels (Microsoft Purview), "Privileged"/"Confidential" markers, Legal/HR/Board distribution lists, personal folders, user-defined exclusions.
- [ ] **Redaction** of special-category data and identifiers (Microsoft Presidio or equivalent) before text leaves your estate.
- [ ] **No raw email at rest.** Only distilled cards + message IDs. Card retention ≤ 30 days unless refreshed.
- [ ] **Subject access requests:** a user (or a third party) can export everything stored about them.

## 2. AI provider terms
- [ ] Commercial/enterprise API terms: inputs not used for training (default for Anthropic's commercial API).
- [ ] **Data retention and processing terms for Claude on Microsoft Foundry:** confirm with Microsoft/Anthropic what's logged or retained, for how long, and which terms apply to "Hosted on Azure" vs "Hosted on Anthropic" deployments. Use plain Messages requests only (no stateful features).
- [ ] **Data residency:** set by the Foundry deployment region and hosting type (DECISIONS.md §5).
- [ ] Sub-processor list updated.

## 3. Media and content licensing
- [ ] Your monitoring/news licence covers **API access**, **internal redistribution** of excerpts/summaries, and **processing by an AI system**. Many publisher licences restrict the last two.
- [ ] UK: check whether NLA Media Access / CLA licences are needed for the number of internal recipients. US: CCC. Other markets have equivalents.
- [ ] Store and show: headline, outlet, date, link, licensed excerpt, your own AI summary. Don't republish full articles.
- [ ] Social platform API terms (X, LinkedIn, Reddit) are strict about storage and AI use. Check each.

## 4. Government relations specifics
- [ ] Drafted outreach to officials, MPs or regulators may count as lobbying under transparency registers (UK Consultant Lobbying register, EU Transparency Register, US LDA, Canadian Lobbying Act). Add a "this may be a registrable communication" flag to GR drafts and keep the "human sends" rule absolute.
- [ ] Parliamentary data licences (e.g. UK Open Parliament Licence) generally allow reuse with attribution; show the attribution.

## 5. Security
- [ ] Postgres Row-Level Security on `tenant_id` and `user_id`, tested with a deliberate cross-user retrieval test in CI.
- [ ] Graph tokens encrypted at rest (Key Vault / KMS); least-privilege scopes: `Mail.Read`, `Calendars.Read`, `offline_access`, plus `Mail.ReadWrite` **only** if you implement "create draft".
- [ ] Prompt-injection defence: external articles and emails are **data**. The synthesis prompt says so; the model has no tools that can send, delete or forward; output is schema-validated.
- [ ] Full audit log: who saw which brief, which card items and signals it used, model + prompt version.
- [ ] Pen test before rollout beyond the pilot.

## 6. Human oversight
- [ ] The system never sends, posts or publishes. It drafts; a person sends.
- [ ] Every brief shows its sources and the card items it used ("why am I seeing this?").
- [ ] Clear labelling that content is AI-generated.
