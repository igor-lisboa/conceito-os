---
id: rsk
status: draft
phase: all
version: 1.2
updated: 2026-11-04
---

# Risks and open decisions

Claude does NOT decide items on this list without approval from Beatriz (product owner). It proposes options with a recommendation. When a decision is made, move it to "Decided" with date and outcome, and update the affected specs.

## Risks

| Topic | Risk |
| --- | --- |
| Instagram/TikTok APIs | App approval, scopes, quotas, account types, metric and publishing limits |
| Trend monitoring | Uneven coverage, collection limits, vendor licenses |
| AI | Cost per operation, errors, transparency, review, data isolation |
| Data protection | LGPD, contracts, legal bases, retention, incidents |
| Video files | Storage, compression, processing, bandwidth, cost |
| Multi-company SaaS | Isolation, billing, quotas, support, abuse |
| Visual identity | Symbol vectorization, final tokens, accessibility (palette fails contrast as text, see [design system](../ux/design-system.md)) |
| Contracts and billing | Legal review, integrations, applicable law |
| Prioritization | Development capacity, maintenance, real feedback from the agency |
| Scope | The full vision is very large for a first build; MVP discipline is the main schedule risk |

## Open decisions

| # | Decision | Where | Initial recommendation |
| --- | --- | --- | --- |
| D-01 | Which parts of CRM, proposals and reports are in the MVP (roadmap vs. screen inventory disagree) | roadmap, CRM, ONB, MET | Minimal cuts as proposed in each module; confirm with Beatriz |
| D-02 | Desktop sidebar items (two different lists in the source) | navigation | Single unified list as proposed |
| D-03 | Mobile bottom bar: "Alerts" tab vs "More" with alerts in the header | navigation | Home · Clients · Calendar · Tasks · More |
| D-04 | Supabase vs self-managed Postgres | architecture | Evaluate Supabase for speed with RLS |
| D-05 | Own job queue vs n8n | architecture, AUT | Own queue for core flows; n8n only for peripheral ones |
| D-06 | AI provider(s) and budget per task | AI | Provider-agnostic layer; choose per task |
| D-07 | Contract e-signature solution and legal templates | ONB | External integration; lawyer-reviewed templates |
| D-08 | SaaS payment gateway | BIL | Decide in P4 |
| D-09 | Grace period length (3–7 days suggested) | BIL | Configurable per plan |
| D-10 | Scheduled posts during suspension | BIL | Pause at suspension start, warn beforehand |
| D-11 | Single `invoices` table or split agency vs platform | data model | Split |
| D-12 | "Analyzed" as a state or a flag | states | Flag (`analyzed_at`) |
| D-13 | Allowed prospecting and trend sources | CRM, AI | Official/licensed sources only |
| D-14 | Design pipeline for vector logos and editable files; final Conceito OS logo vector | BRD, DSG | Human designer + integrated tool |
| D-15 | Font licensing and loading | DSG | Both on Google Fonts (OFL); self-host |
| D-16 | Granularity of "if permitted / limited" permission flags | roles | Configurable flags per module |
| D-17 | Retention policy, legal bases, MFA per role | security | Define with legal review; MFA mandatory for owner/admin |
| D-18 | Validate novelty claims with users before marketing them | vision | Don't claim novelty before testing |
| D-19 | Configurable production stages vs fixed states | PRO, states | Fixed technical states; agencies may rename UI labels only |
| D-20 | Job function → role mapping (commercial, strategist, analyst, designer) | roles | Map to existing roles + flags, no new roles |
| D-21 | "Client approval required": per client, per content type, or both | CLI, PRO | Per client, default on |
| D-22 | Numeric non-functional targets (latency, availability, RPO/RTO, upload limits) | NFR | Set before production launch |
| D-23 | Dark mode timing | DSG | After MVP; tokens ready from day one |
| D-24 | Languages beyond pt-BR | NFR | Decided 2026-11-01: English and pt-BR. Others not planned. |
| D-25 | Capabilities actually available per account type in Meta/TikTok APIs (publishing, metrics) | INT, MET | Technical spike before P2 |
| D-26 | Date change after client approval requires re-approval | CAL | Confirmed by the product owner (2026-11-02): the planned date stays locked from client review, so no re-approval flow is needed; the publishing date is set after approval through unschedule and schedule, which the approval already covers. |
| D-27 | Planned date (PRO-015, PRO-016): changes need a recorded reason; the date locks once the piece reaches client review, or is scheduled or published | PRO, CAL | Confirmed by the product owner (2026-11-02): reason always required; lock from client review, scheduled and published. |
| D-28 | Board drag: which moves a card may take by drag (PRO-017) | PRO | Confirmed by the product owner (2026-11-02): only the four manual moves of PD-41. Approvals, rejections, scheduling and publishing stay on the piece page because they need a comment, date or link. |
| D-30 | Who may edit or delete a comment (PRO-004): author only, or also owners and managers; and whether an edit notifies newly mentioned people | PRO | Built as PROPOSAL: author only, edits marked as edited, no new notifications on edit. Recommendation: keep author only, because it matches a comment being the author's own note; owners/managers can still act through the team. Pending product owner. |
| D-29 | Phone layout: filters as a drawer, and the piece editor in steps (NAV-002, NAV-014) | NAV, PRO | Confirmed by the product owner (2026-11-02): filters are a collapsed panel that opens when a filter is set; the step-by-step editor moves to P2, because the single page works on phones. |

## Decided

| # | Decision | Date | Outcome |
| --- | --- | --- | --- |
| D-04 | Database engine | 2026-11-01 | MySQL 8 (product owner). Supabase and Postgres are not used. |
| — | Backend framework | 2026-11-01 | Django 5.2 LTS (product owner). See [docs/architecture.md](../../docs/architecture.md). |
| — | Architecture of the content context | 2026-11-01 | Hexagonal + DDD tactical patterns in `production`; simple services in `clients` and `accounts`. |
| — | Hosting | 2026-11-01 | Vercel Python runtime; migrations run from the developer machine. |
| — | URL routes in English | 2026-11-04 | Requested by Igor Lisboa; replaces the pt-BR routes of the source spec (`/clientes` becomes `/clients`). Route names in code were already English. Pending confirmation by Beatriz (product owner). |
| — | Frontend | 2026-11-01 | Server-rendered templates for now; SPA deferred. |
