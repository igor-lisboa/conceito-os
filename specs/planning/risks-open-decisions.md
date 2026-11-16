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

## Decided

| # | Decision | Date | Outcome |
| --- | --- | --- | --- |
| D-04 | Database engine | 2026-11-16 | Changed at the owner's request (Igor Lisboa): PostgreSQL in production with a read/write and an optional read-only connection; MySQL kept for local Docker and tests. Pending Beatriz's confirmation. Was: MySQL 8 (2026-11-01). |
| — | Backend framework | 2026-11-01 | Django 5.2 LTS (product owner). See [docs/architecture.md](../../docs/architecture.md). |
| — | Architecture of the content context | 2026-11-01 | Hexagonal + DDD tactical patterns in `production`; simple services in `clients` and `accounts`. |
| — | Hosting | 2026-11-01 | Vercel Python runtime; migrations run from the developer machine. |
| — | URL routes in English | 2026-11-04 | Requested by Igor Lisboa; replaces the pt-BR routes of the source spec (`/clientes` becomes `/clients`). Route names in code were already English. Pending confirmation by Beatriz (product owner). |
| — | Frontend | 2026-11-01 | Server-rendered templates for now; SPA deferred. |
| D-01 | Scope of CRM, proposals and reports in the MVP | 2026-11-16 | Minimal manual version in the MVP (answer 15A). Phase 2 details to be added to the spec: PDF, automation, proposal detail. |
| D-02 | Desktop sidebar items | 2026-11-16 | One unified list (16A). |
| D-03 | Mobile bottom bar | 2026-11-16 | Home · Clients · Calendar · Tasks · More (17A). |
| D-05 | Job queue (Phase 3) | 2026-11-16 | Answer 12A: our own queue for core work; n8n only for side tasks. Phase 3. |
| D-06 | AI provider (Phase 3) | 2026-11-16 | Provider-agnostic layer (19A). The product owner plans to build an LLM in-house later, so the layer must allow it. |
| D-07 | Contract e-signature (Phase 2) | 2026-11-16 | Upload a signed PDF by hand (20B). |
| D-08 | SaaS payment gateway (Phase 4) | 2026-11-16 | Decide in Phase 4 (21C). |
| D-09 | Grace period after non-payment (Phase 4) | 2026-11-16 | 3 days by default, configurable per plan (22A, with the configurable option). Confirm the exact default. |
| D-10 | Scheduled posts during suspension (Phase 4) | 2026-11-16 | Cancel scheduled posts, with alerts (23C). |
| D-11 | Invoices table (Phase 2) | 2026-11-16 | Answer 8A: two tables, one for the agency and one for the platform. Phase 2. |
| D-12 | "Analyzed" as state or flag | 2026-11-16 | Flag (25A). |
| D-13 | Prospecting and trend sources | 2026-11-16 | Official or licensed sources only (26A). |
| D-14 | Logo design pipeline | 2026-11-16 | Human designer with an integrated tool (27A). |
| D-15 | Font licensing | 2026-11-16 | Google Fonts, self-hosted (28A). |
| D-16 | CRM permission flags ("if permitted") | 2026-11-16 | Owners set a permission flag per person (4B). Built 2026-11-16: account managers manage CRM only when an owner grants it; existing account managers keep it. |
| D-18 | Validate novelty claims before marketing | 2026-11-16 | Test with real users first (29A). |
| D-19 | Configurable production stages | 2026-11-16 | Answer 9A: fixed technical states; agencies may rename the labels only. |
| D-20 | Job function to role mapping | 2026-11-16 | Map to existing roles plus flags (31A). |
| D-21 | Client approval required | 2026-11-16 | Per client, on by default (9A). |
| D-23 | Dark mode timing | 2026-11-16 | Answer 10B: dark mode ships with the MVP. Built with a PROPOSAL palette (contrast tested); the designer confirms the colours. |
| D-25 | Social network capabilities before Phase 2 | 2026-11-16 | Answer 11B: assume and build, keeping the integration swappable. No spike first. |
| D-24 | Languages beyond pt-BR | 2026-11-01 | English and pt-BR only (decided earlier). |
| D-26 | Date change after client approval | 2026-11-02 | Confirmed by the product owner: no re-approval flow. |
| D-27 | Planned date lock and reason | 2026-11-02 | Confirmed by the product owner: reason required; locked from client review, scheduled and published. |
| D-28 | Board drag moves | 2026-11-02 | Confirmed by the product owner: the four manual moves only. |
| D-29 | Phone layout (filters, editor) | 2026-11-02 | Confirmed by the product owner. Reversed for the editor by PRO-003 below, pending confirmation. |
| D-30 | Comment edit, delete and re-notification | 2026-11-16 | Author only (2A). An edit notifies people mentioned for the first time (3B). Implemented. |
| D-31 | Who is notified about a mention | 2026-11-16 | Only internal members who can open the piece (1A). Implemented; client-role members never notified. |
| TD-S5 | Sign in with username | 2026-11-16 | Email only (12A). Implemented; usernames no longer sign in. |
| CRM-001 | Lead pipeline stages | 2026-11-16 | Keep the five stages: new, contacted, meeting, won, lost (13A). Spec wording to be fixed. |
| PRO-003 | Mobile piece editor | 2026-11-16 | Answer 2A: single page on phones for the MVP (confirmed D-29). The step-by-step editor is Phase 2. |
| CAL-001 | Campaign filter on the calendar | 2026-11-16 | Add a campaign entity now (10A). Built 2026-11-16. |
| PD-46 | Dragging scheduled pieces | 2026-11-16 | Answer 1A: keep the lock (confirmed D-27). Nothing to build. |
| D-22 | Numeric non-functional targets | 2026-11-16 | Approved as proposed (2026-11-16). Expected users: 10 (answer 4); the load test runs at twice that. Confirm the meaning of "10". |
| D-17 | Legal basis per data type | 2026-11-16 | Answer 3A: the suggested bases in docs/data-types.md are adopted. The lawyer confirms them before real personal data is used. |
| TD-S6 | Manual publication | 2026-11-16 | Answer 7A: a manual publication always keeps the link as proof. Built. |
| TD-S7 | Row-level security | 2026-11-16 | Answer 5A: keep the application-level rule, covered by tests. Accepted. |
| TD-S8 | Session limits | 2026-11-16 | Answer 6A: sign out after a period without activity (8 hours is a PROPOSAL, to confirm). Built. |
