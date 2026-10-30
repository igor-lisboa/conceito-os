---
id: rdm
status: draft
phase: all
version: 1.1
updated: 2026-10-30
---

# Roadmap

## Phase 1 — Foundation and operational MVP

- Authentication, organizations, users, roles and clients ([AUTH](../modules/auth-organization.md), [CLI](../modules/clients-briefing.md)).
- Brand briefing/identity, library and storage.
- Tasks, Kanban, calendar and content creation ([PRO](../modules/production-approval.md), [CAL](../modules/calendar-seasonal.md)).
- Portal with client approval, history and basic notifications ([POR](../modules/client-portal.md), [NTF](../modules/notifications.md)).
- Basic CRM, proposal and report with manual entry or clearly labeled demo data.

> The source screen inventory marks CRM, proposals and reports as P2 while this phase includes their "basic" versions. Each affected module states a PROPOSAL for the MVP cut; D-01 confirms it.

## Phase 2 — Operations and intelligent strategy

- Per-client strategy, Conceito DNA and assisted calendar generation.
- Proposal, contract, campaign, seasonality and report templates.
- Time, cost and profitability tracking.
- First social network integrations and collection of authorized metrics.

## Phase 3 — Differentiating intelligence

- Conceito Lab, Radar, Pulse, Trends and Updates.
- Competitor research, international signals and verifiable alerts.
- Specialized agents and orchestrated automations.
- Quality and effectiveness tests; cost analysis per automation.

## Phase 4 — Multi-agency product

- SaaS plans and billing, self-service onboarding, subscription limits.
- Advanced observability, usage policies, support, export and expanded security.
- Value-proposition validation with external users.

## Rule

A phase is "done" only when its acceptance criteria are verified and its specs are `implemented` with evidence.

## Suggested MVP build order (PROPOSAL)

Dependencies point to this order; engineering confirms it in the backlog:

1. Tenancy, auth, roles, audit, isolation tests (everything depends on it).
2. Clients + briefing + private file storage.
3. Content items + versions + production Kanban + calendar.
4. Approvals (internal + portal) + notifications.
5. MVP cuts of CRM, proposals and manual metrics/report (per D-01).
