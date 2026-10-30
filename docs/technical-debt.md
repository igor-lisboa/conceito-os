# Technical debt against the full specification

This document lists what the full specification (in `specs/`) requires and the code
does **not** yet do, plus shortcuts taken to reach a functional MVP. Each item says
which spec requirement it pays off, how urgent it is, and what it depends on.

Use it to plan work. When an item is done, move it to the **Paid** section at the
bottom with the commit or PR and the test that proves it. Update the module spec
status and Evidence at the same time (see [specs/PROCESS.md](../specs/PROCESS.md)).

Sizes are rough guides for planning, not estimates: **S** is a few days of
work, **M** is one to two weeks, **L** is more than two weeks. Engineering confirms
them when the backlog is built (see [engineering deliverables](../specs/planning/engineering-deliverables.md)).

---

## Where the functional MVP stands

Working today, with tests on SQLite and MySQL (181 tests at the time of writing):

- Sign-in by email, password recovery, welcome email, first administrator command.
- Organizations, memberships, the role matrix, and per-client visibility.
- Clients, archiving, and the brand briefing.
- Content lifecycle with versions, internal review, client approval through the
  portal, scheduling, manual publishing, and failure handling.
- Audit trail of every change (append-only).
- Notifications in the app and by email for the review events.
- Language choice (English and Portuguese), local Docker database and mail server.

Not working yet, and needed for a team to use it day to day: see the **P0** and
**P1** items below.

---

## Priorities

| Priority | Meaning |
| --- | --- |
| **P0** | Needed before the first real agency uses the system. Safety, data, or the team cannot work without it. |
| **P1** | Needed to finish Phase 1 (the MVP as agreed in [phase-1-decisions](phase-1-decisions.md)). |
| **P2** | Phase 2: operations and strategy. |
| **P3** | Phase 3: advanced intelligence and automation. |
| **P4** | Phase 4: multi-agency SaaS. |

---

## P0: before real use

| ID | Debt | Spec reference | Why it matters | Size | Depends on |
| --- | --- | --- | --- | --- | --- |
| TD-03 | Invite team members by email, set their role and client access, and remove their access (immediately effective). Today members are created in the Django admin. | AUTH-011, AUTH-012, CLI-004, PRM-007 | Without it, adding people needs a developer. Removing access is a security requirement. | M | Email (done), team screens |
| TD-12 | Limit repeated failed sign-in attempts per account and per address. | SEC-008 | The login page is public on the internet. The counts must be shared between serverless instances, so the choice depends on the hosting setup. | S | Hosting setup |
| TD-13 | Backups of the production database, with a restore test that is run and recorded. | ARC-005, NFR-040 | Losing agency content would be irreversible. | S | Production database provider |
| TD-39 | Deploy to Vercel and check it end to end against a real MySQL server, with real SMTP. | PD-14, deployment guide | Only the local Docker setup has been exercised. | S | TD-13, TD-45 |
| TD-40 | Rotate the administrator password for production, and set every production secret only in the hosting settings. | PD-76, PD-94 | The local development password must not be used in production. | S | TD-39 |
| TD-45 | Verified email domain and SMTP account with the provider. | AUTH-002, PD-73, NTF-001 | Welcome and reset emails need a provider that delivers them. | S | Provider account |
| TD-47 | Personal data: export and deletion on request, retention rules, and legal review of the bases. | SEC-009, SEC-011 | Required by LGPD for personal data of clients and team. | M | Legal review (D-17) |
| TD-44 | Clear the two remaining HSTS warnings from `manage.py check --deploy` (subdomains and preload), once the domain is stable. | SEC-006 | Only worth doing after the domain is final, because preload is hard to undo. | S | TD-39 |

## P1: to finish Phase 1

| ID | Debt | Spec reference | Why it matters | Size | Depends on |
| --- | --- | --- | --- | --- | --- |
| TD-01 | **CRM, proposals and reports, manual minimum.** Leads with stage and next action; proposals typed by hand with status; a monthly report where people enter metric values by hand, and missing metrics show as `N/D`. No automation, no AI, no PDF. | PD-02, CRM-001, CRM-003, CRM-006, ONB-001, MET-001..003, MET-005 (manual part) | Agreed as part of Phase 1 (decision D-01). The largest gap in the agreed scope. | L | None |
| TD-02 | **Brand file library as links.** Each brand gets a list of links (logo, fonts, templates, references) with a title and a kind. | PD-03, CLI-007 | Agreed in Phase 1. No file upload until a storage service is chosen (TD-33). | S | None |
| TD-04 | **Calendar views:** month, week, and a daily agenda on phones; filter by client, channel, stage, and date; duplicate a piece from the calendar; change a date with validation. | CAL-001..004, CAL-006, CAL-011 | The calendar is how the team plans. Today there is only a filtered list. | M | Timezone (TD-09) |
| TD-05 | **Kanban production board** (desktop columns; phone lists grouped by stage). | PRO-005, section 17.3 item 2 | Spec MVP item. Today the list filter covers the data but not the board. | M | None |
| TD-06 | **Tasks:** create a task for a client or a piece, with an owner and a due date; mark done; list "mine". | Section 8 entity `tasks`, Phase 1 "tarefas" | Phase 1 scope; the team needs to track follow-ups. | M | None |
| TD-07 | **Phone navigation:** bottom bar (Home, Clients, Calendar, Tasks, More); filters in a drawer; the piece editor in steps (text, media, date, review). | NAV-002, 15.1, 18.1 | The spec treats phones as a first-class target, not a shrunk desktop. Today the layout is responsive CSS only. | M | TD-04, TD-05 |
| TD-08 | **Audit log screen** for the owner, filterable by person, action, and client. | AUTH-020, SEC-007 | The data is recorded; only the admin can read it today. | S | None |
| TD-09 | **Apply each organization's timezone** on every screen and in date inputs. | CAL-011, NFR-003 | Dates are stored in UTC and shown in UTC today. A Brazilian team reads them wrong. | S | None |
| TD-11 | **Multi-factor sign-in** for owners and administrators (for others, by risk decision). | AUTH-004, D-17 | Owners can publish and read finances; the spec asks for MFA by risk. | M | Decision D-17 |
| TD-15 | **Organization settings screen:** name, timezone, default notification email. | AUTH-014 | Today these are set only in the admin. | S | TD-09 |
| TD-29 | **Comments on a piece**, with mentions that notify the person. Today comments exist only on approvals. | PRO-004, NTF-006, 17.2 | Spec production item: discussion happens on the piece, not only in decisions. | M | Notifications (done) |
| TD-43 | **Record the published link** of a post, when the team publishes by hand. | INT-010 | Keeps proof of publication for reports and client questions. | S | None |
| TD-36 | **Accessibility check** of the screens against WCAG 2.2 AA, with a keyboard and a screen reader pass. | NFR-010, NFR-011, DSG-003 | The spec makes AA the target; only colour contrast has been checked so far. | S | None |
| TD-14 | **Logs and alerts** for failed emails, failed sign-ins and server errors. | ARC-006 | Today failures are logged to the console only. | S | TD-39 |
| TD-26 | **Client portal:** the Home, Calendar, Results, Files and Contact sections. Only Approvals exists. | POR-002 | Phase 1 has the approvals portal; the other sections are part of the spec's portal. | M | TD-04, TD-02 |
| TD-48 | **Notifications and mail templates in the client's language** (today: the request's language). | NTF-005 partly | Clients may be in a different language from the team. | S | None |

## P2: Phase 2 (operations and strategy)

| ID | Debt | Spec reference | Size |
| --- | --- | --- | --- |
| TD-16 | Briefing with conditional questions, identity and onboarding checklist. | ONB-005, ONB-006 | M |
| TD-17 | Identity audit and redesign with moodboards and before/after comparison. | BRD-001..010, UC-15 | L |
| TD-18 | Strategy, DNA and per-network strategy with versions and approvals. | STR-001..008, UC-05 | L |
| TD-19 | Metrics imported from the networks through their APIs; charts; PDF export. | MET-001, MET-004, MET-006, MET-007 | L |
| TD-20 | Social network connections: OAuth, token renewal, publishing through the APIs, fallback to manual. | INT-001..009, PD-05 | L |
| TD-24 | Agency finance: contracts, instalments, costs, hours, margin and overdue alerts. | FIN-001..009, UC-12 | L |
| TD-28 | Seasonal calendar with Brazilian dates and assisted 30-day planning. | CAL-007..010, UC-06 | M |
| TD-31 | Compare two versions of a piece side by side. | PRO-004 | S |
| TD-35 | Formal design system: SVG logo, token validation, component states guide. | DSG-006, DSG-008 | M |
| TD-37 | End-to-end browser tests of the main flows, and a check that the role matrix is complete. | section 12 | M |
| TD-38 | Performance targets and a load test. | NFR-030..032 | S |
| TD-49 | API contracts for jobs, states and events, written from the code. | section 14.5 | S |

## P3 and P4: later phases

| ID | Debt | Spec reference | Phase |
| --- | --- | --- | --- |
| TD-10 | Per-user notification preferences by type and channel. | NTF-005 | P2 |
| TD-21 | AI engines: DNA memory, Lab experiments, Radar, Pulse, Trends, Updates; provider layer with cost per task. | section 4, AI-001..061, ARC-007 | P3 |
| TD-22 | Automations with triggers, safeguards and an execution log. | AUT-001..020 | P3 |
| TD-25 | Trend pipeline (collection, deduplication, classification) and platform update tracking. | AI-050..061 | P3 |
| TD-27 | Notification digests and intelligence alerts. | NTF-008 | P3 |
| TD-33 | File storage service for uploads, video processing and quotas. | ARC (media), NFR-031, D-14 | P3 |
| TD-34 | Dark mode. | D-23, DSG-002 | P3 |
| TD-46 | Idempotent jobs and webhooks with dead-letter handling. | ARC-003 | P3 |
| TD-23 | SaaS billing: plans, gateway, webhooks, grace periods, suspension, subscription dashboard. | BIL-001..016, section 3.8 | P4 |
| TD-50 | Self-service onboarding, plan limits and usage policies. | Phase 4 | P4 |

---

## Known shortcuts in the code (not spec items)

These are choices made to reach the MVP. They are fine now, but each one has a
cost later.

| ID | Shortcut | Risk | When to fix |
| --- | --- | --- | --- |
| TD-S1 | Some user-facing strings are only in English in the 404, 403 and 500 pages. | Portuguese users see English on error pages. | With TD-36 |
| TD-S2 | The welcome email is always in pt-BR, whatever the new user's browser language. | Minor. | When TD-48 is done |
| TD-S3 | Mailpit image is `latest`, not pinned. | An upgrade could change local behaviour without notice. | Now (one line in compose) |
| TD-S4 | `visible_content` (read side) repeats the rule of `production/domain/policy.py` in ORM form. A test keeps them in step. | Two places to change when the rule changes. | When the policy changes next |
| TD-S5 | Login by username is still allowed next to login by email. | Two ways in; the username is not always private. | Keep until the team agrees; review with TD-11 |
| TD-S6 | Publishing is marked by hand, with no link to the post. | Relies on people remembering to mark it. | With TD-43 and TD-20 |
| TD-S7 | The database has no `WHERE`-level row security; tenant isolation is in application code, tested. | A future bug in a query could leak data. | Consider with TD-37 |
| TD-S8 | Session cookies and password reset links use the Django defaults (sessions in the database). | Fine for now; no session limit per device yet. | With TD-11 |

---

## Paid

Move items here when done, with the reference that proves it.

| ID | Done on | Evidence |
| --- | --- | --- |
| _none yet_ | | |

---

## How to use this list

1. Pick the next **P0** item, then **P1**. Keep each change small enough to test.
2. A change that touches a rule starts in the spec, as in [PROCESS.md](../specs/PROCESS.md).
3. Add a line to [CHANGELOG](../specs/CHANGELOG.md) for each item done.
4. If you find new debt while working, add it here with an ID (`TD-NN`, or `TD-SN` for shortcuts), not in a comment in the code.
