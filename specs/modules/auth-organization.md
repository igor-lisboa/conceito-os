---
id: auth
status: partially-implemented
phase: MVP
version: 1.0
updated: 2026-10-30
---

# Authentication, organization and team administration

New in the review: these requirements were spread across the source spec (screens, security, permissions, UC-01, UC-13) and are consolidated here.

## Goal

Let people sign in safely, belong to an organization with a role, and let the owner manage team, access, integrations and audit.

## Actors and permissions

Owner/admin manages everything here. Other roles only manage their own session and profile. See [roles](../product/01-roles-permissions.md).

## Requirements

### Authentication

- **AUTH-001** Sign in with email + password or an authorized identity provider; sign out.
- **AUTH-002** Password recovery. Failed sign-in or recovery MUST NOT reveal whether an account exists. *Implemented 2026-11-01: email link valid for 24 hours, one use; same answer for unknown emails.*
- **AUTH-003** Session protection (expiry, revocation on password change or access removal).
- **AUTH-004** MFA available, required according to risk (which roles: D-17).
- **AUTH-005** Accept an invitation and land on `/inicio` or the authorized portal, depending on role.

### Organization and team

- **AUTH-010** Create an organization with name, timezone and owner (UC-01). The first tenant's owner is Beatriz.
- **AUTH-011** Invite members by email with a role, client scope and permission flags. Invitations expire.
- **AUTH-012** Revoke a member's access immediately, including active sessions.
- **AUTH-013** One user MAY belong to more than one organization (memberships); the top bar lets them switch organization. PROPOSAL, implied by the "organization selector" in the source spec.
- **AUTH-014** Organization settings: timezone, brand identity of the agency, notification defaults.

### Administration

- **AUTH-020** Audit log view filterable by actor, action, client and period (owner only).
- **AUTH-021** Integrations page: connected accounts, token status, reconnect, revoke ([INT](social-integrations.md)).
- **AUTH-022** Webhook and policy configuration (P2+).
- **AUTH-023** Every admin action returns to the originating area with confirmation.

## Data

`organizations`, `users`, `memberships`, `roles`, `invitations` (PROPOSAL), `audit_events`, `connectors`.

## Screens

`/login`, `/recuperar-senha`, `/configuracoes` (team, roles, integrations, logs). See [screens](../ux/screens.md).

## Exceptions

Expired invitation; revoked user with an open session; email already a member; last owner tries to remove themselves (MUST be blocked).

## Acceptance criteria

- [ ] Admin creates organization, user and client; isolation between organizations proven by test.
- [ ] Revoked member loses access on the next request.
- [ ] Expired invitation cannot be accepted.
- [ ] Login error messages are identical for existing and non-existing accounts.

## Open decisions

- D-17 MFA policy per role.

## Evidence

- Sign-in by email, password recovery, welcome email, first administrator: `apps/accounts/tests/test_auth.py`
- Roles and capability matrix: `apps/accounts/tests/test_permissions.py`
- Active organization selection: `apps/accounts/tests/test_middleware.py`
- Actor construction: `apps/core/tests/test_actors.py`
