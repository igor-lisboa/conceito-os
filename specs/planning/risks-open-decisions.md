---
id: rsk
status: draft
phase: all
version: 1.3
updated: 2026-11-16
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

| D-17 | Legal basis per data type | security | Retention decided 2026-11-16: keep everything forever; soft delete always; anonymize personal data on request or when a contract ends (DAT-007, DAT-011). MFA optional (5B). Open: the legal basis for each data type; the list is in docs/data-types.md, pending legal review. |
## Decided

| # | Decision | Date | Outcome |
| --- | --- | --- | --- |
| D-04 | Database engine | 2026-11-01 | MySQL 8 (product owner). Supabase and Postgres are not used. |
| — | Backend framework | 2026-11-01 | Django 5.2 LTS (product owner). See [docs/architecture.md](../../docs/architecture.md). |
| — | Architecture of the content context | 2026-11-01 | Hexagonal + DDD tactical patterns in `production`; simple services in `clients` and `accounts`. |
| — | Hosting | 2026-11-01 | Vercel Python runtime; migrations run from the developer machine. |
| — | URL routes in English | 2026-11-04 | Requested by Igor Lisboa; replaces the pt-BR routes of the source spec (`/clientes` becomes `/clients`). Route names in code were already English. Pending confirmation by Beatriz (product owner). |
| — | Frontend | 2026-11-01 | Server-rendered templates for now; SPA deferred. |
| D-01 | Scope of CRM, proposals and reports in the MVP | 2026-11-16 | Minimal manual version in the MVP (answer 15A). Phase 2 details to be added to the spec: PDF, automation, proposal detail. |
| D-02 | Desktop sidebar items | 2026-11-16 | One unified list (16A). |
| D-03 | Mobile bottom bar | 2026-11-16 | Home · Clients · Calendar · Tasks · More (17A). |
| D-05 | Job queue (Phase 3) | 2026-11-16 | n8n for all job work (18B). Core publishing then depends on n8n; review before Phase 3 starts. |
| D-06 | AI provider (Phase 3) | 2026-11-16 | Provider-agnostic layer (19A). The product owner plans to build an LLM in-house later, so the layer must allow it. |
| D-07 | Contract e-signature (Phase 2) | 2026-11-16 | Upload a signed PDF by hand (20B). |
| D-08 | SaaS payment gateway (Phase 4) | 2026-11-16 | Decide in Phase 4 (21C). |
| D-09 | Grace period after non-payment (Phase 4) | 2026-11-16 | 3 days by default, configurable per plan (22A, with the configurable option). Confirm the exact default. |
| D-10 | Scheduled posts during suspension (Phase 4) | 2026-11-16 | Cancel scheduled posts, with alerts (23C). |
| D-11 | Invoices table (Phase 2) | 2026-11-16 | One table (24B). Conflicts with the separation of financial contexts A and B (CLAUDE.md invariants); confirm before building. |
| D-12 | "Analyzed" as state or flag | 2026-11-16 | Flag (25A). |
| D-13 | Prospecting and trend sources | 2026-11-16 | Official or licensed sources only (26A). |
| D-14 | Logo design pipeline | 2026-11-16 | Human designer with an integrated tool (27A). |
| D-15 | Font licensing | 2026-11-16 | Google Fonts, self-hosted (28A). |
| D-16 | CRM permission flags ("if permitted") | 2026-11-16 | Owners set a permission flag per person (4B). Build pending. |
| D-18 | Validate novelty claims before marketing | 2026-11-16 | Test with real users first (29A). |
| D-19 | Configurable production stages | 2026-11-16 | Fully configurable stages (30B). Conflicts with the fixed-states recommendation and the approval rules; confirm before building. |
| D-20 | Job function to role mapping | 2026-11-16 | Map to existing roles plus flags (31A). |
| D-21 | Client approval required | 2026-11-16 | Per client, on by default (9A). |
| D-23 | Dark mode timing | 2026-11-16 | With the MVP (32B). Conflicts with TD-34 (Phase 3); confirm the scope change. |
| D-25 | Social network capabilities before Phase 2 | 2026-11-16 | Assume and build, keeping the integration agnostic (33B). No spike first; confirm. |
| D-24 | Languages beyond pt-BR | 2026-11-01 | English and pt-BR only (decided earlier). |
| D-26 | Date change after client approval | 2026-11-02 | Confirmed by the product owner: no re-approval flow. |
| D-27 | Planned date lock and reason | 2026-11-02 | Confirmed by the product owner: reason required; locked from client review, scheduled and published. |
| D-28 | Board drag moves | 2026-11-02 | Confirmed by the product owner: the four manual moves only. |
| D-29 | Phone layout (filters, editor) | 2026-11-02 | Confirmed by the product owner. Reversed for the editor by PRO-003 below, pending confirmation. |
| D-30 | Comment edit, delete and re-notification | 2026-11-16 | Author only (2A). An edit notifies people mentioned for the first time (3B). Implemented. |
| D-31 | Who is notified about a mention | 2026-11-16 | Only internal members who can open the piece (1A). Implemented; client-role members never notified. |
| TD-S5 | Sign in with username | 2026-11-16 | Email only (12A). Implemented; usernames no longer sign in. |
| CRM-001 | Lead pipeline stages | 2026-11-16 | Keep the five stages: new, contacted, meeting, won, lost (13A). Spec wording to be fixed. |
| PRO-003 | Mobile piece editor (step by step) | 2026-11-16 | Build the step-by-step editor in the MVP (14B). Reverses D-29 for the editor: needs Beatriz's confirmation. Build pending. |
| CAL-001 | Campaign filter on the calendar | 2026-11-16 | Add a campaign entity now (10A). Build pending. |
| PD-46 | Dragging scheduled pieces | 2026-11-16 | Allowed, with a required reason and a notice of the edit (11B). Build pending. |
| D-22 | Numeric non-functional targets | 2026-11-16 | Approved as proposed: availability 99.5% per month; 95% of common pages under 1 second; daily backups kept 30 days; recovery point 24 h; recovery time 4 h; images 10 MB, documents 25 MB; load test at twice the expected users (number still to be given). NFR-031, NFR-032, NFR-040, NFR-042 updated. |
