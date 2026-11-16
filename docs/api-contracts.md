# Internal contracts: states, events and notifications (TD-49)

Written from the code, as of 2026-11-16. The specification these come from is
[specs/technical/states-events.md](../specs/technical/states-events.md); the rules
live in the code (`apps/production/domain/states.py`, `apps/notifications/adapters.py`).

**What this document covers.** Conceito OS has no public JSON HTTP API yet. Its
contracts are the internal ones below: state machines, the events each change writes to
the audit trail, and the notification kinds. Two things in the spec are **not built**, so
they have no contract here:

- **Jobs and queues.** Automated execution (automations, scheduled publishing by a worker)
  is a later phase (TD-21, TD-22, TD-46). Today publishing is marked by hand.
- **Webhooks and external APIs.** Social network connections are TD-20 (P2).

A test (`apps/production/tests/test_api_contracts.py`) reads the tables below and fails
if they differ from the code. Change the code and this file in the same piece of work.

---

## Content states

Source: `ContentState` and `ALLOWED_TRANSITIONS` in `apps/production/domain/states.py`.
Any change not in the table is rejected by the backend (EVT-001).

| From | To |
| --- | --- |
| `draft` | `planned` |
| `planned` | `in_production` |
| `in_production` | `internal_review` |
| `internal_review` | `approved` |
| `internal_review` | `client_review` |
| `internal_review` | `in_production` |
| `client_review` | `approved` |
| `client_review` | `changes_requested` |
| `client_review` | `internal_review` |
| `changes_requested` | `in_production` |
| `approved` | `internal_review` |
| `approved` | `scheduled` |
| `scheduled` | `approved` |
| `scheduled` | `published` |
| `scheduled` | `failed` |
| `failed` | `internal_review` |
| `failed` | `scheduled` |

`published` has no outgoing change. The states are: `draft`, `planned`, `in_production`,
`internal_review`, `client_review`, `changes_requested`, `approved`, `scheduled`,
`published`, `failed`.

Approval decisions recorded on a version: `approved`, `changes_requested`. Approval
stages: `internal`, `client`.

## Lead and proposal states

Source: `apps/crm/models.py`.

- Lead stage: `new`, `contacted`, `meeting`, `won`, `lost`.
- Proposal status: `draft`, `sent`, `accepted`, `rejected`.
- Lead source: `referral`, `instagram`, `website`, `other`.

## Audit events

Every change writes one row to the append-only audit trail (`AuditEvent`, SEC-007). The
action names come from the code: constants and the events the content lifecycle emits.

| Action | Written when |
| --- | --- |
| `member.invited` | A team member is invited (`apps/accounts/team.py`) |
| `member.removed` | A member's access is removed |
| `client.created` | A client is created (`apps/clients/services.py`) |
| `client.archived` | A client is archived |
| `briefing.updated` | A client's brand briefing is saved |
| `content.created` | A piece is created |
| `content.version_added` | A new version of a piece is saved |
| `content.state_changed` | A piece changes state (this also sends notifications) |
| `content.planned_date_changed` | A planned date changes (with its reason) |
| `content.approval_recorded` | An internal or client decision is recorded on a version |

Each audit row holds: organization, actor, action, entity type and ID, metadata, time.

## Notification kinds

Source: `KIND_MESSAGES`, `CLIENT_KINDS` and `REJECTION_KINDS` in
`apps/notifications/adapters.py`. Each notification is unique per recipient and event
key, so a repeated event creates no duplicate (EVT-002).

Triggered by a state change (`NOTIFICATION_KINDS` in
`apps/production/application/content_service.py`), or by a comment mention.

| Kind | Triggered by | Recipients |
| --- | --- | --- |
| `internal_review` | `in_production` → `internal_review` | Owners and account managers with access to the client, except the actor |
| `client_review` | `internal_review` → `client_review` | Client members with access to the brand |
| `changes_requested` | `client_review` → `changes_requested` | Owners and account managers with access to the client, except the actor |
| `approved_by_client` | `client_review` → `approved` | Owners and account managers with access to the client, except the actor |
| `internal_rejected` | `internal_review` → `in_production` | The piece's owner, if it has one; otherwise owners and account managers |
| `publish_failed` | `scheduled` → `failed` | Owners and account managers with access to the client; carries the failure reason |
| `mention` | A comment that mentions a person | Organization members whose email is mentioned, except the author. **Not checked against who can see the piece: open decision D-31.** |
