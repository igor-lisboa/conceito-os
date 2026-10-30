---
id: prm
status: draft
phase: MVP
version: 1.1
updated: 2026-10-30
---

# Roles and permissions

Permissions apply per **agency (tenant)**, **client** and **action**. Each user only sees the clients they are assigned to, except the agency's own administrators. Technical roles do not imply any ownership stake in the business.

## Roles

| Role | Scope |
| --- | --- |
| Owner / admin | Settings, clients, team, operations, costs, audit |
| Account manager | Assigned clients |
| Creative / collaborator | Data and activities authorized by function and client |
| Invited freelancer | Only explicitly assigned tasks and files |
| End client | Restricted portal: own briefing, materials, approvals and reports |
| SaaS administrator (future) | Technical and plan management, **without** blanket read access to tenants' private data |

## Matrix

| Resource / action | Owner/admin | Account manager | Creative/collab. | Freelancer | End client |
| --- | --- | --- | --- | --- | --- |
| Configure agency, team and plans | Full | No | No | No | No |
| View client portfolio | All in tenant | Assigned | Assigned | Assigned projects | Own space only |
| Strategic data and briefing | All | Assigned clients | Read/write, assigned | Relevant materials only | Own released data |
| Create/edit strategies | Yes | Yes | If authorized | Authorized tasks only | View published versions |
| Create post/caption, attach media | Yes | Yes | Yes, assigned | Assigned only | No (can comment) |
| Approve internally | Yes | Yes | Not by default | No | No |
| Approve/reject own client's content | Optional | Optional | No | No | Yes |
| Schedule/publish to networks | Yes | If permitted | Not by default | No | No |
| Read metrics | All | Assigned | If permitted | Not by default | Own accounts only |
| Prospect and move CRM | Yes | If permitted | Not by default | No | No |
| Prices, contracts, internal finance | Full | Limited, configurable | No | No | Own published proposals/contracts only |
| Manage credentials and integrations | Yes | Not by default | No | No | Only authorize own accounts via secure flow |
| Export/delete data | Yes, audited | Limited | No | No | Request own data per policy |

"If permitted", "not by default" and "limited, configurable" are per-member permission flags set by the owner. Their exact granularity is D-16.

## Job functions → roles (PROPOSAL, D-20)

Use cases name job functions that are not roles. Until D-20 is settled:

| Job function | Role + flags |
| --- | --- |
| Commercial | Account manager (or owner) with CRM flag |
| Strategist | Account manager |
| Analyst | Account manager or collaborator with metrics flag |
| Creative / designer | Creative / collaborator |

## Requirements

- **PRM-001** Every permission MUST be enforced on the backend; hiding it in the UI is not enough.
- **PRM-002** Isolation by `organization_id` in the database (RLS where applicable) and by client in authorization.
- **PRM-003** Changing an ID in a URL or API call MUST NOT expose another client's or tenant's data (no IDOR).
- **PRM-004** File links MUST be signed and short-lived.
- **PRM-005** Network tokens MUST be encrypted; no secrets in the browser.
- **PRM-006** Approvals and publishing MUST produce audit events.
- **PRM-007** Invitations MUST expire; access MUST be revocable.
- **PRM-008** Least privilege: "not by default" permissions change only through explicit owner configuration.
- **PRM-009** The UI hides unauthorized modules, and the server blocks them too.
- **PRM-010** Every permission change MUST be audited (who, what, when, before/after).

## Acceptance criteria

- [ ] A direct API call without permission returns access denied.
- [ ] An automated test proves a tenant A user cannot read tenant B data.
- [ ] An automated test proves a user cannot read a client in the same tenant they aren't assigned to.
- [ ] A freelancer only sees assigned tasks/files.
- [ ] An end client never sees margins, internal prices or other clients' data.

## Open decisions

- D-16 Permission flag granularity.
- D-20 Job function → role mapping.
