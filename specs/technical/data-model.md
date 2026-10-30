---
id: dat
status: draft
phase: all
version: 1.1
updated: 2026-10-30
---

# Data model — initial entities

## From the source spec

| Entities | Responsibility |
| --- | --- |
| `organizations` | Companies/agencies; future subscriptions |
| `users`, `memberships`, `roles` | Users and permissions |
| `clients`, `social_accounts` | Clients and authorized social accounts |
| `brand_dna`, `strategies`, `strategy_versions` | Knowledge and versioned strategy |
| `competitors`, `research_sources` | Research with source and date |
| `content_items`, `assets`, `content_versions` | Content, media and revisions |
| `calendar_entries`, `campaigns`, `seasonal_events` | Schedule, campaigns, seasonality |
| `tasks`, `comments`, `approvals`, `audit_events` | Operations, feedback and trails |
| `platform_metrics`, `metric_snapshots` | Metrics, source and period |
| `leads`, `interactions`, `deals`, `proposals` | Prospecting and sales |
| `contracts`, `invoices`, `costs`, `time_entries` | Finance, scope, effort |
| `trend_signals`, `platform_updates`, `experiments` | Intelligence and experiments |
| `notifications`, `automations`, `executions` | Alerts, workflows and errors |
| `connectors`, `oauth_tokens` | Configuration and secure credentials |

## Added in the review (PROPOSAL)

| Entity | Why | Source |
| --- | --- | --- |
| `invitations` | Expiring invitations with role, client scope, flags | AUTH-011, PRM-007 |
| `member_client_access` | Which clients each member can access (could also live in `memberships`) | PRM-002 |
| `notification_preferences` | Per-user preferences by type/channel | NTF-005 |
| `brand_identity_versions` | Versioned identity proposals and approvals | BRD-008 |
| `proposal_templates`, `contract_templates` | Reusable templates | ONB-001, ONB-003 |
| `onboarding_checklists` | Checklist templates and per-client instances | ONB-006 |
| `subscriptions`, `platform_invoices`, `payment_events` | SaaS billing kept separate from agency finance | BIL-*, D-11 |
| `agency_invoices` | Rename of `invoices` for context A if D-11 splits them | FIN-*, D-11 |

## Mandatory rules

- **DAT-001** Every business table has `organization_id`; every query filters on it.
- **DAT-002** Authorization by organization, user and client; RLS tested where applicable.
- **DAT-003** Private storage; versions; audit; no secrets in the browser.
- **DAT-004** Researched records store `source` and `observed_at`; metrics store source, window and availability.
- **DAT-005** Versioned records (strategy, content, identity) are append-only per version.
- **DAT-006** Relevant events record actor, timestamps, version, rationale and external ID.
- **DAT-007** Soft delete/archive by default; hard deletion only through an audited flow (LGPD).
- **DAT-008** Timestamps stored in UTC; display in the organization's timezone. PROPOSAL.
- **DAT-009** Money stored as integer cents (or exact decimal) with currency. PROPOSAL.

## Main relationships

```text
Organization
  ├── Memberships → Users / Roles
  ├── Clients
  │     ├── SocialAccounts → MetricSnapshots
  │     ├── BrandDNA → Strategies → Versions
  │     ├── Competitors / ResearchSources
  │     ├── Campaigns → CalendarEntries → ContentItems
  │     │                                  ├── Assets / Versions
  │     │                                  ├── Approvals
  │     │                                  └── Tasks / Comments
  │     └── Contracts / Costs / TimeEntries
  ├── Leads → Interactions → Deals → Proposals
  └── Automations → Executions → Notifications
```

## Open decisions

- D-11 Single `invoices` table or split by context (recommendation: split).
- Detailed fields and indexes: to be defined in the ER model and migrations ([deliverables](../planning/engineering-deliverables.md)).
