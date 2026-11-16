---
id: sec
status: draft
phase: all
version: 1.3
updated: 2026-11-16
---

# Security, multi-tenancy and privacy (LGPD)

LGPD = Lei Geral de Proteção de Dados, Brazil's data protection law.

## Requirements

- **SEC-001** Strong authentication; MFA according to risk; session protection (idle sign-out after 8 hours without activity, a PROPOSAL pending confirmation; decided 2026-11-16, answer 6A); failed login never reveals whether an account exists ([AUTH](../modules/auth-organization.md)).
- **SEC-002** Tenant isolation by `organization_id`; authorization by organization, user and client.
- **SEC-003** Row Level Security where applicable, **with tests** proving isolation.
- **SEC-004** Private storage; signed short-lived links; permissions checked when the link is issued.
- **SEC-005** Network tokens encrypted; no secrets in the browser; revocation.
- **SEC-006** Least privilege; invitations expire; access revocable.
- **SEC-007** Audit of approvals, publishing, export/deletion, permission changes and administrative access.
- **SEC-008** Abuse prevention (rate limits, quotas) and IDOR protection.
- **SEC-009** LGPD: legal bases and consents, data export, incident handling. Retention (decided 2026-11-16, D-17): everything is kept forever; personal data is anonymized on request or at contract end ([DAT-011](data-model.md)). Legal bases per data type remain open until the legal review.
- **SEC-010** The SaaS administrator cannot read tenants' private data indiscriminately; any support access is explicit, time-boxed and audited.
- **SEC-011** End-client and lead data have a recorded purpose and legal basis; opt-out is respected ([CRM-007](../modules/crm-prospecting.md)).
- **SEC-012** Periodic backup restore tests.
- **SEC-013** Data sent to AI providers follows per-client isolation and minimization; provider terms must not allow training on it. PROPOSAL for the last part.
- **SEC-014** Never collect or store social network passwords.
- **SEC-015** Uploaded files are validated (type, size) and served from an isolated domain or with safe content headers. PROPOSAL.
- **SEC-016** Audit events are append-only; no user, including the owner, can edit or delete them. PROPOSAL.
- **SEC-017** The client wall: a person sees only the clients they have access to, on every screen, list, count, search, notification, export and link. Owners see all clients of their organization. Another client's data is answered as not found, never as forbidden, and every screen is covered by a test (decided 2026-11-16, "chinese wall").

## Acceptance criteria

- [ ] Test suite for isolation between tenants and between clients of the same tenant.
- [ ] A direct API call without permission is denied.
- [ ] A backup restore has been performed and documented.

## Open decisions

- D-17 Legal bases per data type, retention policy, MFA per role.
