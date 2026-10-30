---
id: evt
status: draft
phase: all
version: 1.1
updated: 2026-10-30
---

# States and events

Every transition records actor, timestamp, version, rationale and external ID when there is one.

## Content

`draft → planned → in_production → internal_review → client_review → changes_requested | approved → scheduled → published | failed`

### Mapping to production stages (PROPOSAL, D-12 / D-19)

| Production stage (UI, pt-BR) | Technical state |
| --- | --- |
| Idea ("ideia") | `draft` |
| Planned ("planejado") | `planned` |
| Script ("roteiro") | `in_production` (sub-stage) |
| Production ("produção") | `in_production` |
| Internal review ("revisão interna") | `internal_review` |
| Client approval ("aprovação do cliente") | `client_review` → `changes_requested` or `approved` |
| Scheduled ("agendado") | `scheduled` |
| Published ("publicado") | `published` |
| Analyzed ("analisado") | `published` + `analyzed_at` set (flag, not a state) |

### Rules

- `changes_requested` returns to `in_production` with a new version.
- If the client's "client approval required" setting is off ([CLI-010](../modules/clients-briefing.md)), `internal_review → approved` is allowed directly, and the record says so.
- `approved` is bound to a specific content version; editing it afterwards returns it to `internal_review` ([PRO-013](../modules/production-approval.md)).
- `scheduled` requires `approved`, a valid connection and permission.
- `failed` NEVER masquerades as `published`; controlled retry from `failed → scheduled`.
- Manual fallback: `approved → published` with `publish_method = manual` ([INT-010](../modules/social-integrations.md)).

## Lead

`new → researched → qualified → contact_pending → contacted → meeting → proposal → negotiating → won | lost`

| CRM pipeline stage | Technical state |
| --- | --- |
| (just created) | `new` |
| Researched | `researched` |
| Qualified | `qualified` |
| Approach approved | `contact_pending` |
| Contacted | `contacted` |
| Meeting | `meeting` |
| Proposal | `proposal` |
| Negotiation | `negotiating` |
| Won / lost | `won` / `lost` (with reason) |

- `contacted` requires a recorded approved approach.
- Opt-out is a flag (`opted_out_at`) that blocks `contact_pending → contacted` from any state ([CRM-007](../modules/crm-prospecting.md)).

## Automated execution

`queued → running → succeeded | retryable_failed | permanently_failed | cancelled`

- `retryable_failed → queued` up to a configured limit, then `permanently_failed` (dead-letter).

## SaaS subscription

`trialing → active → past_due → grace_period → suspended → canceled`; `past_due | grace_period | suspended → active` with a gateway-confirmed payment. Durations per plan. See [saas-billing](../modules/saas-billing.md).

## Trends and updates

- Trend: `emerging | growing | established | declining`
- Platform update: `confirmed | testing | rumor`

## Rules

- **EVT-001** Invalid transitions are rejected by the backend.
- **EVT-002** Notification events are idempotent (no duplicates).
- **EVT-003** New states MUST be recorded here before being implemented.
- **EVT-004** Each state machine is implemented once, server-side, and covered by tests of every allowed and a sample of forbidden transitions. PROPOSAL.
