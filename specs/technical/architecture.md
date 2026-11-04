---
id: arc
status: partially-implemented
phase: all
version: 1.2
updated: 2026-11-04
---

# Technical architecture

## Decided stack (updated 2026-11-01)

The product owner chose this stack. It supersedes the suggestion from the source spec, which stays below for reference.

| Layer | Decision | Notes |
| --- | --- | --- |
| Backend | Python 3.12, Django 5.2 LTS | See [docs/architecture.md](../../docs/architecture.md) for the reasons and the rejected alternatives. |
| Architecture | Hexagonal (ports and adapters) with DDD tactical patterns in the `production` context; simple services in `clients` and `accounts` | Rules for each context are in section "Layering" below. |
| Database | MySQL 8 through PyMySQL | Not provisioned yet. Migrations generated, not applied. Supabase is not used (D-04 closed). |
| Frontend | Server-rendered Django templates, responsive CSS | A separate SPA is deferred until an API or native app needs it. Next.js from the source spec is not used now. |
| Static files | WhiteNoise | Served from the app folders; no separate storage. |
| Hosting | Vercel, Python serverless runtime, `api/index.py` entry point | Migrations run from the developer machine, not in Vercel. No file storage on the platform. |
| Tests | Django test runner, SQLite in memory for tests | The MySQL-specific behavior is limited to what SQLite also supports. |

## Layering (ARC-010..ARC-016)

- **ARC-010** The domain of each context with business rules (`apps/production/domain/`) MUST NOT import Django, the database, the clock or request data.
- **ARC-011** Use cases (`apps/production/application/`) depend on domain code and on port interfaces, not on Django adapters.
- **ARC-012** Adapters implement ports and are the only place that imports Django models for those rules (`apps/production/adapters/`, `apps/core/audit.py`).
- **ARC-013** Web views call use cases and never change a state or create an approval directly.
- **ARC-014** The composition root (`apps/production/composition.py`) is the only place that wires real adapters into use cases.
- **ARC-015** Read-side lists may query the ORM directly. A test MUST check that the read filter agrees with the domain policy.
- **ARC-016** A context may stay in the simple style (Django models and service functions) while its rules are few. Moving it to the hexagonal style is required when it gains a state machine or approvals.

## Requirements (from the source spec)

- **ARC-001** Centralized authorization on the backend; the frontend is never the barrier.
- **ARC-002** Segregation by `organization_id` in every business table.
- **ARC-003** Idempotent jobs; authenticated, idempotent webhooks.
- **ARC-004** Separate environments; secrets outside code and the browser (environment variables only).
- **ARC-005** Versioned migrations; backups with **tested restore** (not yet done: no database).
- **ARC-006** Observability: structured logs, metrics, alerts on job and integration failures (not yet done).
- **ARC-007** AI behind an internal interface (swap provider without touching modules), recording cost per task (AI not built).
- **ARC-008** Abstract social-network layer (Instagram/TikTok as implementations) (not built).
- **ARC-009** All business rules (state transitions, permissions, suspension) live server-side in one place, testable without the UI. Met for content and permissions; billing not built.

## Evidence

- Layering: `apps/production/tests/domain/` (no database), `apps/production/tests/application/` (fakes), `apps/production/tests/test_queries.py`.
- Deployment entry and settings: `api/index.py`, `vercel.json`, `config/settings/base.py`, [docs/deployment.md](../../docs/deployment.md).

## Open decisions

- D-05 Queue (own vs n8n) for jobs; D-06 AI provider; hosting of media (storage service) and video processing.

## Original suggestion (reference only)

| Layer | Suggestion from the source spec |
| --- | --- |
| Frontend | Next.js, TypeScript, React, Tailwind, accessible components |
| Backend | API/services with centralized authorization, business rules, queues, AI integration |
| Database | PostgreSQL, possibly Supabase; migrations, indexes, RLS, backup and **tested** restore |
| Media | Private object storage, short-lived URLs, versioning, quotas; video compression/processing |
| AI | Provider-agnostic layer; per-client knowledge retrieval; cost per task; limits; logs |
| Jobs | Scheduling, queues, idempotent retries, dead-letter queue; n8n optional for peripheral integrations |
| Social networks | OAuth, official Meta/TikTok connectors, secure token revocation and renewal |
| Infra | dev/staging/production, CI/CD, tests, monitoring, secure credential management |
