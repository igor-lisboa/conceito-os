---
id: nfr
status: draft
phase: all
version: 1.0
updated: 2026-10-30
---

# Non-functional requirements

New in the review. The source spec states several qualities without targets; this file collects them. Items marked PROPOSAL or with a TBD target need the product owner/engineering to set the number (D-22).

## Locale

- **NFR-001** The UI is available in English (default) and Brazilian Portuguese (pt-BR). Each visitor chooses the language on every page; the choice is kept per browser. Business messages are translated at the web edge, never in the domain. Other languages are not planned (D-24).
- **NFR-002** Every entry in the pt-BR catalog has a translation; an untranslated entry fails the test suite. Strings missing from the catalog are a review item, not a test failure. Evidence: `core/tests/test_i18n.py`.
- **NFR-002** Currency BRL; Brazilian date/number formats in the UI. PROPOSAL.
- **NFR-003** Timezone per organization, default `America/Sao_Paulo`; publishing date/time per channel. PROPOSAL for the default.

## Accessibility

- **NFR-010** Target WCAG 2.2 level AA. PROPOSAL — the source asks for "WCAG contrast", keyboard and touch targets without naming a level.
- **NFR-011** Full keyboard operation, visible focus, touch targets suitable for mobile, no meaning by color alone.

## Compatibility

- **NFR-020** Current Chrome, Safari, Edge, Firefox; tested on Safari iPhone and Chrome Android ([NAV-005](../ux/navigation-responsive.md)).

## Performance (targets TBD)

- **NFR-030** Pages and lists remain usable on mobile networks; large lists paginate or virtualize.
- **NFR-031** Media uploads support large videos with progress and resume or retry. Size limits TBD.
- **NFR-032** Target page-load and API latency: TBD (D-22).

## Reliability

- **NFR-040** Backups with tested restore ([ARC-005](architecture.md)). RPO/RTO targets: TBD (D-22).
- **NFR-041** No loss of drafts on network error, edit conflict or integration failure (UC-EXC-001/002).
- **NFR-042** Availability target: TBD (D-22).

## Cost and observability

- **NFR-050** AI cost tracked per task, client and organization ([AI-003](../modules/ai-intelligence.md)).
- **NFR-051** Storage quotas per organization; video storage cost monitored.
- **NFR-052** Structured logs and alerts for job, webhook and integration failures.

## Open decisions

- D-22 Numeric targets (latency, availability, RPO/RTO, upload limits). D-24 Languages beyond pt-BR.
