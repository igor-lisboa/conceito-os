# Specs — Conceito OS

Source of truth for **Conceito OS** (Conceito Co). Derived from the product specification v1.0 (October 2026) and refined into modular files for versioning and day-to-day development.

> Nothing here is implemented unless the file's `status` and "Evidence" section say so, backed by code and passing tests.

## How to use

- **Before building**: read the module spec plus the cross-cutting specs (roles & permissions, security, states, data model).
- **When behavior changes**: update the spec in the same piece of work. See [PROCESS.md](PROCESS.md).
- **Spec and code disagree**: never resolve silently. Fix one of them and log it in the [changelog](CHANGELOG.md).

## Index

### Product

| File | Content |
| --- | --- |
| [product/00-vision.md](product/00-vision.md) | Vision, principles, scope, glossary |
| [product/01-roles-permissions.md](product/01-roles-permissions.md) | Roles, permission matrix, access rules |
| [product/02-journey-use-cases.md](product/02-journey-use-cases.md) | End-to-end journey, use cases UC-01..15 |

### Modules

| File | Prefix | Phase |
| --- | --- | --- |
| [modules/auth-organization.md](modules/auth-organization.md) | AUTH | MVP |
| [modules/clients-briefing.md](modules/clients-briefing.md) | CLI | MVP |
| [modules/calendar-seasonal.md](modules/calendar-seasonal.md) | CAL | MVP / P2 |
| [modules/production-approval.md](modules/production-approval.md) | PRO | MVP |
| [modules/client-portal.md](modules/client-portal.md) | POR | MVP / P2 |
| [modules/notifications.md](modules/notifications.md) | NTF | MVP / P3 |
| [modules/crm-prospecting.md](modules/crm-prospecting.md) | CRM | MVP basic / P2 (D-01) |
| [modules/proposals-contracts-onboarding.md](modules/proposals-contracts-onboarding.md) | ONB | MVP basic / P2 (D-01) |
| [modules/metrics-reports.md](modules/metrics-reports.md) | MET | MVP manual / P2 (D-01) |
| [modules/diagnosis-strategy.md](modules/diagnosis-strategy.md) | STR | P2 |
| [modules/brand-identity.md](modules/brand-identity.md) | BRD | P2 |
| [modules/agency-finance.md](modules/agency-finance.md) | FIN | P2 |
| [modules/social-integrations.md](modules/social-integrations.md) | INT | P2 |
| [modules/ai-intelligence.md](modules/ai-intelligence.md) | AI | P2 / P3 |
| [modules/automations.md](modules/automations.md) | AUT | P3 |
| [modules/saas-billing.md](modules/saas-billing.md) | BIL | P4 |

### UX

| File | Prefix | Content |
| --- | --- | --- |
| [ux/design-system.md](ux/design-system.md) | DSG | Brand, tokens, typography, accessibility |
| [ux/navigation-responsive.md](ux/navigation-responsive.md) | NAV | Desktop, mobile, tablet policy, portal |
| [ux/screens.md](ux/screens.md) | SCR | Screen inventory, routes, phases, actions, destinations |

### Technical

| File | Prefix | Content |
| --- | --- | --- |
| [technical/architecture.md](technical/architecture.md) | ARC | Suggested stack, layers, infra |
| [technical/security-privacy.md](technical/security-privacy.md) | SEC | Multi-tenancy, RLS, secrets, LGPD |
| [technical/data-model.md](technical/data-model.md) | DAT | Entities and relationships |
| [technical/states-events.md](technical/states-events.md) | EVT | State machines and events |
| [technical/non-functional.md](technical/non-functional.md) | NFR | Locale, accessibility, performance, reliability |

### Planning

| File | Content |
| --- | --- |
| [planning/roadmap.md](planning/roadmap.md) | Phases 1–4 and suggested MVP build order |
| [planning/mvp-acceptance.md](planning/mvp-acceptance.md) | MVP acceptance checklist |
| [planning/risks-open-decisions.md](planning/risks-open-decisions.md) | Risks and pending decisions (D-NN) |
| [planning/engineering-deliverables.md](planning/engineering-deliverables.md) | Next engineering artifacts |

### Meta

| File | Content |
| --- | --- |
| [PROCESS.md](PROCESS.md) | How to keep the specs alive |
| [CHANGELOG.md](CHANGELOG.md) | Spec change history |
| [_templates/module.md](_templates/module.md) | Template for new module specs |

## Conventions

- **Language**: specs and code in English. Product UI copy is Brazilian Portuguese (pt-BR); UI terms quoted in specs may keep the pt-BR label in parentheses, e.g. *More* ("Mais"). User-facing URL routes stay in pt-BR (`/clientes`), as in the source specification.
- **Requirement IDs**: `<PREFIX>-NNN`, stable. **Never reuse or renumber** an ID; mark removed ones as `[removed]`.
- **Keywords**: **MUST**, **MUST NOT**, **SHOULD**, **MAY**.
- **Status** per file: `draft` → `in-review` → `approved` → `partially-implemented` → `implemented`.
- **PROPOSAL**: content added during refinement that was not in the source spec. Needs product-owner confirmation before it becomes binding.
- **Open decisions** are referenced as `D-NN` and tracked in [risks-open-decisions.md](planning/risks-open-decisions.md).
- **Phases**: **MVP**, **P2** (operations/strategy), **P3** (advanced AI), **P4** (multi-agency SaaS).
- **Product owner**: Beatriz. Business decisions are hers.
