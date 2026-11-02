---
id: ntf
status: partially-implemented
phase: MVP (basic) / P3 (digests and intelligence alerts)
version: 1.1
updated: 2026-11-02
---

# Notifications

New in the review: consolidates notification requirements from UC-14, the MVP acceptance criteria, cross-cutting features and the Updates engine.

## Requirements

- **NTF-001** In-app notifications and email (MVP).
- **NTF-002** Each notification states origin (what happened, which client, who) and links to the item (UC-14).
- **NTF-003** Delivery MUST be idempotent: one event produces at most one notification per recipient and channel.
- **NTF-004** Notifications respect permissions: a user is never notified about a client they can't access.
- **NTF-005** Per-user preferences by type and channel; organization defaults ([AUTH-014](auth-organization.md)).
- **NTF-006** Mentions in comments notify the mentioned user.
- **NTF-007** MVP events: task assigned, review requested, client approved/requested changes, due date approaching, publishing failed, integration expired.
- **NTF-008** (P3) Critical intelligence alerts per event; daily/weekly digests for Updates and Trends.
- **NTF-009** Notifications to end clients only go through the apps/portal/email and never include internal data.
- **NTF-010** Each person chooses the language of the emails they receive on their own account page, in English or pt-BR, and the email is written in that language. When nothing was chosen, emails use pt-BR. PROPOSAL: the pt-BR default matches the welcome and invitation emails; product owner to confirm.

## Data

`notifications`, notification preferences (PROPOSAL: `notification_preferences`).

## Acceptance criteria

- [ ] Notifications work and don't duplicate events (retry of the same event = no new notification).
- [ ] A user without access to client X receives no notification about client X.

## Evidence

- Recipients and idempotency: `apps/notifications/tests/test_adapters.py`
- Inbox, open and mark-read: `apps/notifications/tests/test_views.py`
- Which content events notify: `apps/production/tests/application/test_notifications_events.py`
- Email language per person (NTF-010): `apps/notifications/tests/test_email_language.py`, `apps/accounts/tests/test_account_language.py`

Not built yet: notification preferences (NTF-005), digests and intelligence alerts (NTF-008). See docs/technical-debt.md (TD-10, TD-27).
