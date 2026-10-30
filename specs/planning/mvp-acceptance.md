---
id: acc
status: draft
phase: MVP
version: 1.1
updated: 2026-10-30
---

# MVP acceptance criteria

Tick `[x]` only with evidence (test/PR) recorded in the corresponding module.

| Criterion | Owner spec |
| --- | --- |
| [ ] Admin creates organization, user and client; isolation between organizations proven | [AUTH](../modules/auth-organization.md), [SEC](../technical/security-privacy.md) |
| [ ] Briefing creates a structured record with files and history | [CLI](../modules/clients-briefing.md) |
| [ ] Calendar creates and filters content by client, channel, state and date | [CAL](../modules/calendar-seasonal.md) |
| [ ] Kanban changes state with permission checks and an audit trail | [PRO](../modules/production-approval.md) |
| [ ] Content has briefing, artwork/file, script, caption, CTA and versions | [PRO](../modules/production-approval.md) |
| [ ] Client sees only their pieces, approves or requests changes, and comments | [POR](../modules/client-portal.md) |
| [ ] Notifications work and don't duplicate events | [NTF](../modules/notifications.md) |
| [ ] Report identifies source, dates and missing metrics; no fictitious numbers shown as real | [MET](../modules/metrics-reports.md) |
| [ ] Private upload and short-lived URLs respect permissions | [CLI](../modules/clients-briefing.md), [SEC](../technical/security-privacy.md) |
| [ ] Critical flows have tests, error handling and verified backup/restore | [ARC](../technical/architecture.md) |

## Responsive screens

- [ ] Login and dashboard work on desktop and mobile without unnecessary horizontal scrolling.
- [ ] Desktop Kanban with columns; mobile lists filterable by stage, no horizontal dragging.
- [ ] A client approves/requests a revision on mobile in a few steps, with readable art/video and caption.
- [ ] Calendar: month/week on desktop; daily agenda and compact filters on mobile.
- [ ] A user without permission gets access denied even calling the API directly.
- [ ] Navigation keeps the client context and allows going back.
- [ ] Forms, uploads, alerts and confirmations work by touch and keyboard.
- [ ] An integration error doesn't delete content being edited nor shows as a completed publication.

## Billing (P4, not MVP)

See [saas-billing](../modules/saas-billing.md) acceptance criteria.
