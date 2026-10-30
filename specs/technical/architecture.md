---
id: arc
status: draft (to be validated)
phase: all
version: 1.1
updated: 2026-10-30
---

# Suggested technical architecture

> Suggestion from the source spec, **to be validated** with engineering. Changing the stack requires recording the decision in [risks-open-decisions](../planning/risks-open-decisions.md).

| Layer | Suggestion |
| --- | --- |
| Frontend | Next.js, TypeScript, React, Tailwind, accessible components |
| Backend | API/services with centralized authorization, business rules, queues, AI integration |
| Database | PostgreSQL, possibly Supabase; migrations, indexes, RLS, backup and **tested** restore |
| Media | Private object storage, short-lived URLs, versioning, quotas; video compression/processing |
| AI | Provider-agnostic layer; per-client knowledge retrieval; cost per task; limits; logs |
| Jobs | Scheduling, queues, idempotent retries, failure handling, dead-letter queue, observability; n8n optional for peripheral integrations |
| Social networks | OAuth, official Meta/TikTok connectors, secure token revocation and renewal |
| Infra | dev/staging/production, CI/CD, tests, monitoring, secure credential management |

## Requirements

- **ARC-001** Centralized authorization on the backend; the frontend is never the barrier.
- **ARC-002** Segregation by `organization_id` in every business table.
- **ARC-003** Idempotent jobs; authenticated, idempotent webhooks.
- **ARC-004** Separate environments; secrets outside code and the browser.
- **ARC-005** Versioned migrations; backups with **tested restore**.
- **ARC-006** Observability: structured logs, metrics, alerts on job/integration failures.
- **ARC-007** AI behind an internal interface (swap provider without touching modules), recording cost per task.
- **ARC-008** Abstract social-network layer (Instagram/TikTok as implementations).
- **ARC-009** All business rules (state transitions, permissions, suspension) live server-side in one place, testable without the UI. PROPOSAL.

## Open decisions

- D-04 Supabase vs self-managed Postgres. D-05 Queue (own vs n8n). D-06 AI provider. Hosting and video processing are not decided either.
