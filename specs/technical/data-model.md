---
id: dat
status: draft
phase: all
version: 1.3
updated: 2026-11-16
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
- **DAT-007** Soft delete always: no business record is ever removed from the database (decided 2026-11-16, D-17). Deleted rows are hidden from every screen and kept for audit.
- **DAT-012** A campaign belongs to one client. A piece may reference one campaign of its own client; the service rejects any other (decided 2026-11-16, CAL-001). Campaigns are soft deleted like every other record.
- **DAT-011** Personal data is anonymized, not deleted (decided 2026-11-16, D-17): on a person's request or when a contract ends, names, emails and contact fields are replaced by an anonymous marker; the record and its links stay. Anonymization is audited.
- **DAT-010** Every record has a GUID (UUID) as its primary key, including people (users). Numbers are never used as record identifiers, so URLs and events cannot reveal how many records exist. Documentation codes (requirement IDs such as `CRM-001`, decision IDs `PD-NN`, debt IDs `TD-NN`) are names for people to read, not record keys. Evidence: `apps/core/tests/test_identifiers.py`.
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
