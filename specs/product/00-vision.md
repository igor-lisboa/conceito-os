---
id: vis
status: draft
phase: all
version: 1.1
updated: 2026-10-30
---

# Product vision

**Product:** Conceito OS, associated with Conceito Co.
**Idea, ownership and direction:** Beatriz (founder, owner and main administrator of the first tenant).
**Source:** product specification v1.0, October 2026 (PDF + Markdown).

## Goal

A standalone web platform for social media professionals and agencies that covers the work end to end: prospecting, negotiation, onboarding, diagnosis, strategy, production, approval, publishing, metrics, reports and financial management.

Conceito Co is the first operating user. An evolution into a **multi-company SaaS** may be evaluated later (phase P4). The pitch: Notion's document flexibility + Trello's visual management + marketing intelligence and operational data.

## Principles

- **VIS-001** Instagram and TikTok are handled natively (different formats and metrics), with room to add other networks.
- **VIS-002** Information is reliable, historical and segregated per client.
- **VIS-003** AI is an explainable copilot, never an unrestricted executor.
- **VIS-004** Routines are automated, but publishing, external prospecting outreach and contracts require human approval.
- **VIS-005** Differentiators are validated with users before claiming market novelty.
- **VIS-006** The full vision is delivered in phases with verifiable criteria.
- **VIS-007** No fictitious number is ever presented as real; missing data shows as `N/D` ("não disponível").
- **VIS-008** Manual fallback wherever a network's API doesn't support publishing or a metric.

## Scope

**In:** the modules listed in the [index](../README.md#modules).

**Out (for now):** a dedicated tablet experience; an in-house e-signature engine (an external integration is fine); bulk/mass messaging; storing social network passwords.

## Target platforms

Desktop (primary) and mobile (truly responsive). No dedicated tablet experience. Details in [navigation](../ux/navigation-responsive.md).

## Glossary

| Term | Meaning |
| --- | --- |
| Organization / agency / tenant | The company using the platform; the unit of data isolation |
| Client | A brand served by the agency. **Not** the platform subscriber |
| Subscriber | An organization paying for Conceito OS (SaaS context) |
| Content item / piece | A planned or produced piece of content (`content_items`) |
| DNA | The brand's strategic memory (Conceito DNA) |
| Lab / Radar / Pulse / Trends / Updates | Intelligence engines; see [AI](../modules/ai-intelligence.md) |
| N/D | Data not available |
| Product owner | Beatriz; final say on business decisions |

## Two financial contexts (never mix them)

- **A)** Finances of the agency and its social media clients → [agency-finance](../modules/agency-finance.md)
- **B)** Billing of the Conceito OS SaaS platform → [saas-billing](../modules/saas-billing.md)
