---
id: bil
status: draft
phase: P4
version: 1.1
updated: 2026-10-30
---

# SaaS billing, subscriptions and access control

Context B: billing of the Conceito OS platform, once it is sold. Never mix it with the social media client.

## Subscription dashboard (owner and authorized operators)

- **BIL-001** Show registered companies, active accounts, paying subscribers, free/trial plans, courtesy accounts, delinquent, suspended and canceled.
- **BIL-002** Show estimated MRR, received revenue, open charges, overdue payments, churn and evolution over time; each indicator has an auditable definition.
- **BIL-003** Counters represent defined sets and avoid incorrect double counting.
- **BIL-004** Filterable list: organization, plan, cycle, next charge, invoice, payment method, status, days overdue; export only for administrators.
- **BIL-005** The owner sees overdue invoices, time overdue, plan and attempt history; NEVER full card data.

## Payment gateway

- **BIL-006** Gateway integrated via **authenticated, idempotent** webhooks; the provider's confirmation is the source of truth; NEVER trust a status sent by the frontend.
- **BIL-007** A duplicated or out-of-order webhook MUST NOT create a duplicate charge nor wrongly reactivate an account.
- **BIL-008** A confirmed payment restores the corresponding rights with traceability, without manual intervention in the common case.

## State machine

`trialing → active → past_due → grace_period → suspended → canceled`; `past_due | grace_period | suspended → active` after a confirmed payment. States and durations configurable per plan. See [states-events](../technical/states-events.md#saas-subscription).

## Suspension rules for late payment

- **BIL-009** Do NOT block on the first failure signal; send configurable notices and grant a grace period (example to parameterize: 3 to 7 days, per commercial policy — D-09).
- **BIL-010** After the grace period, **suspend write actions and paid features** of the delinquent organization: new publications/schedules, creating strategies and automations, invitations, normal operational access. The API MUST deny them even on direct route calls.
- **BIL-011** Keep a restricted-access screen (mobile-friendly) with charge summary, pay, update payment method, support and data export per policy.
- **BIL-012** NEVER delete content or data for non-payment; keep the audit trail; don't suspend legal/security obligations.
- **BIL-013** Already scheduled posts: recommendation is to pause them once suspension starts and to warn beforehand (D-10).
- **BIL-014** A subscriber's delinquency blocks only their tenant, never other tenants.
- **BIL-015** Export and access to mandatory information remain available per policy, contract and law.
- **BIL-016** Authorized exceptions and charge resending by an operator, audited.

## Data

`subscriptions`, `platform_invoices`, `payment_events` (webhook log with provider event ID for idempotency). PROPOSAL — see D-11.

## Screens

SaaS billing, Restricted access, Administration. See [screens](../ux/screens.md).

## Acceptance criteria

- [ ] After the grace period, the API denies paid actions for the suspended org.
- [ ] A repeated or out-of-order webhook does not corrupt state.
- [ ] Reactivation by confirmed payment leaves an audit trail.
- [ ] Counters for active, paying, trial, delinquent and suspended match their written definitions.
- [ ] The owner never sees full card data.

## Open decisions

- D-08 Gateway. D-09 Grace period. D-10 Scheduled posts during suspension. D-11 Invoice tables.

## Evidence

—
