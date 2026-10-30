# Phase 1 decisions

This is the record of the decisions taken for **Phase 1 (MVP)** of Conceito OS, with
the reason for each one and where it lives in the code. A decision is either
**Built** (in the code and tested), **Decided, not built** (agreed, pending work,
listed in the [technical debt](technical-debt.md)), or **Changed** (replaced by a
later decision).

Each decision has an ID (`PD-NN`) so code, tests, specs and commits can refer to it.

Phase 1 goal: a functional MVP. An agency can sign in, manage clients and briefings,
produce content through its review stages, get client approval in the portal, and
receive notifications. Everything beyond that is in the technical debt document.

---

## Product scope

| ID | Decision | Status | Why | Where |
| --- | --- | --- | --- | --- |
| PD-01 | Phase 1 is an MVP that proves the core flow: produce, review, client approval, publish status. | Built | Smaller scope gets real use sooner; the spec's full vision is delivered in phases (VIS-006). | [roadmap](../specs/planning/roadmap.md) |
| PD-02 | CRM, proposals and reports in Phase 1 are a **manual minimum**: records typed by people, no automation, no AI, no PDF generation. | Built (manual minimum) | The product owner's answer to open decision D-01. Keeps the agency's pipeline in the tool without building the research and automation features yet. | [debt TD-01](technical-debt.md) |
| PD-03 | Brand files are stored as **links** (Drive, Dropbox and the like). No file upload in Phase 1. | Built (links) | Vercel has no persistent file storage. Uploads need an external storage service, which needs an account and keys. The product owner chose links for now. | [debt TD-02](technical-debt.md) |
| PD-04 | Notifications go to **the app and by email**. | Built | The product owner's answer. Email reaches people who do not open the app daily. | `notifications/` |
| PD-05 | Publishing to Instagram and TikTok is **manual**: a person posts by hand and marks the piece as published. | Built | Meta and TikTok APIs need app review and approval (spec section 5). Manual publishing covers the MVP. | `production/domain/states.py` |
| PD-06 | Tablet has no dedicated layout. The phone layout is the responsive layout. | Built | Approved in the spec (NAV-003). | `templates/`, `static/css/app.css` |
| PD-07 | Dark mode is not built now; the tokens are ready for it. | Decided, not built | Spec D-23. | `static/css/app.css` |

---

## Architecture and stack

| ID | Decision | Status | Why | Where |
| --- | --- | --- | --- | --- |
| PD-10 | Python 3.12 with Django 5.2 LTS. | Built | Auth, admin, forms, migrations and security defaults included; large community. | `requirements.txt` |
| PD-11 | MySQL 8.4 (utf8mb4) as the database. Supabase and Postgres are not used. | Built | Chosen by the product owner (closes D-04). | `docker-compose.yml`, `config/settings/base.py` |
| PD-12 | PyMySQL as the MySQL driver. | Built | Pure Python: installs on Windows and Vercel without compiling. | `config/__init__.py` |
| PD-13 | Server-rendered templates, not a separate frontend. | Built | One codebase, one deploy, fewer moving parts for the team. | `templates/` |
| PD-14 | Hosting on Vercel as a Python serverless function, WhiteNoise for static files. | Built (not yet deployed) | The product owner's choice. Migrations run from the developer machine, not in the build. | `vercel.json`, `api/index.py`, [deployment guide](deployment.md) |
| PD-15 | `production` (content lifecycle) uses **hexagonal architecture with DDD tactical patterns**. `clients` and `accounts` use simple services. | Built | The lifecycle has many rules that must be testable without a database. Simple CRUD does not need the extra layers. | [architecture](architecture.md) |
| PD-16 | Domain code never imports Django. Business messages are English identifiers, translated at the web edge. | Built | Keeps the rules portable and testable; enforced by convention and review. | `production/domain/`, `core/http.py` |
| PD-17 | Reads (lists, counts) query the ORM directly; writes go through application services. | Built | A list does not need to rebuild the whole aggregate. A test checks the read filter agrees with the domain policy. | `production/queries.py`, `production/tests/test_queries.py` |
| PD-18 | Django's built-in users and sessions are used. Authorization is our own (see PD-30). | Built | Less code to maintain; the built-in parts are well tested. | `accounts/` |

---

## Authorization and multi-tenancy

| ID | Decision | Status | Why | Where |
| --- | --- | --- | --- | --- |
| PD-30 | Roles are fixed: owner, account manager, creative, freelancer, end client. Each role maps to a set of **capabilities** in one place. | Built | The spec's role matrix (section 16). One file to audit. | `accounts/permissions.py` |
| PD-31 | Capabilities added in Phase 1: archive client, manage team, view audit, manage CRM, enter metrics. | Built (capabilities); screens partly built | Each sensitive action has a named permission. | `accounts/permissions.py` |
| PD-32 | A user only sees the clients they were given, except owners who see all clients of their organization. | Built | Spec PRM-002. Enforced in the query and in the service. | `clients/queries.py` |
| PD-33 | Freelancers only see and edit the pieces assigned to them. | Built | Spec PRM-009 and the matrix. | `production/domain/policy.py` |
| PD-34 | Something outside the user's scope returns **404**, the same as something that does not exist. | Built | Stops people from finding out which IDs exist in another agency or client (IDOR). | `core/exceptions.py`, `core/http.py` |
| PD-35 | Every business table carries `organization_id`; each query filters by it. | Built | Spec DAT-001 and tenant isolation. Tested in `test_queries.py` and the scope tests. | all apps |
| PD-36 | Permission problems return 403; buttons are hidden as a convenience only. The server always checks. | Built | Spec PRM-001. | `production/views.py` |
| PD-37 | A user with several organizations picks one; the choice is kept in the session. | Built (no switcher screen) | Spec AUTH-013. The switcher screen is debt. | `accounts/middleware.py` |

---

## Content lifecycle

| ID | Decision | Status | Why | Where |
| --- | --- | --- | --- | --- |
| PD-40 | Content moves through: draft, planned, in production, internal review, client review, changes requested, approved, scheduled, published, failed. | Built | Spec section 10 and the production stages of section 3.6. | `production/domain/states.py` |
| PD-41 | Only four moves are made by hand: draft to planned, planned to in production, changes requested to in production, in production to internal review. Every other move is a named decision. | Built | A decision needs a comment, a date or a version, so it cannot be a plain move. | `MANUAL_MOVES` |
| PD-42 | Leaving internal review is always a decision with a comment when rejecting. | Built | Rejection without a reason gives the maker nothing to fix. | `production/domain/content.py` |
| PD-43 | Client approval can be turned off per client. The setting is **copied into each piece when it is created**. | Built | Changing a client's rule later should not change pieces already in progress. Open decision D-21 is partly closed: per client, not per content type. | `production/models.py`, `clients/models.py` |
| PD-44 | Every approval records the **version** that was reviewed. | Built | Spec PRO-008: the record always shows what was approved. | `Approval.version` |
| PD-45 | Saving a new version of an approved, client-review, or failed piece returns it to internal review. | Built | Spec PRO-013: an approval never covers text the approver did not see. | `production/domain/states.py` |
| PD-46 | A scheduled piece cannot be edited; it must be unscheduled first. A published piece is final. | Built | Protects what is about to be or was published. | `production/domain/states.py` |
| PD-47 | A publishing failure stays visible as failed, with its reason. It is never shown as published. | Built | Spec INT-006 and "never hide the error". | `production/domain/content.py` |
| PD-48 | A piece only enters "scheduled" from approved or failed, with a future date. | Built | Spec PRO-009. | `production/domain/content.py` |

---

## Clients and briefing

| ID | Decision | Status | Why | Where |
| --- | --- | --- | --- | --- |
| PD-50 | A brand is a **client**. Clients are never deleted: they can be **archived**, which hides them and blocks new content. | Built | Spec CLI-005; keeps history. | `clients/services.py`, `clients/queries.py` |
| PD-51 | The briefing is one record per client with fixed sections (objective, audience, tone, competitors, notes). | Built | Enough for the MVP. The conditional questions of spec ONB-005 are debt. | `clients/models.py` |
| PD-52 | Every client change is audited. | Built | Spec CLI-008. | `core/audit.py` |

---

## Notifications

| ID | Decision | Status | Why | Where |
| --- | --- | --- | --- | --- |
| PD-60 | Events that notify people: internal review requested, client review requested, client asked for changes, client approved, internal rejection, publishing failed. | Built | The moments where someone has to act. | `production/application/content_service.py` |
| PD-61 | Who gets a notification follows visibility: the client's users for client review; owners and managers of that brand for internal events; the piece's maker for a rejection. The person who caused the event is never notified. | Built | Spec NTF-004. | `notifications/adapters.py` |
| PD-62 | Each notification has an event key, unique per person. Repeating the same event creates nothing new. | Built | Spec NTF-003. | `notifications/models.py` |
| PD-63 | Emails are sent after the transaction commits. A failed send is logged and does not undo the in-app notification. | Built | No email about data that was rolled back; a broken mail server does not break the work. | `notifications/adapters.py` |
| PD-64 | Per-user notification preferences (on or off per type) are not built. | Decided, not built | Spec NTF-005. Everyone gets the notifications their role requires. | [debt TD-10](technical-debt.md) |

---

## Accounts, sign-in and password recovery

| ID | Decision | Status | Why | Where |
| --- | --- | --- | --- | --- |
| PD-70 | People sign in with their **email**. The username still works. | Built | Email is what people remember and what password recovery needs. | `accounts/backends.py`, `accounts/forms.py` |
| PD-71 | Emails are stored in lowercase and must be unique. | Built | Uniqueness must mean the same thing on MySQL and SQLite. | `accounts/models.py` |
| PD-72 | Password recovery sends a link valid for 24 hours, usable once. An unknown email gets the same answer. | Built | Spec AUTH-002. Stops account discovery. | `accounts/urls.py`, templates |
| PD-73 | A **welcome email** is sent when a user is created, written in pt-BR. Changing the language is one line. | Built | The team is Brazilian. The welcome is sent after commit and never breaks account creation. | `accounts/emails.py`, `accounts/signals.py` |
| PD-74 | There is no MFA yet. | Decided, not built | Spec AUTH-004 is pending a risk decision per role (D-17). | [debt TD-11](technical-debt.md) |
| PD-75 | Failed sign-in attempts are limited: 5 per account and 20 per address in 15 minutes. | Built (counts are per instance on Vercel, see TD-12) | Spec SEC-008. Needs a shared store for counts, which needs a decision on hosting. | [debt TD-12](technical-debt.md) |
| PD-76 | The first administrator is created with a command, from environment variables. The password is never in the code. | Built | Spec ops practice; no default password in the repository. | `accounts/management/commands/create_initial_admin.py` |
| PD-77 | Inviting people by email and removing their access are built. Invitations reuse the password-reset link (see PD-96). | Built | Spec AUTH-011 and AUTH-012. | [debt TD-03](technical-debt.md) |

---

## Language

| ID | Decision | Status | Why | Where |
| --- | --- | --- | --- | --- |
| PD-80 | English is the default; Portuguese (Brazil) is available. Each browser chooses; the choice is kept in a cookie. | Built | The product owner asked for both. The cookie avoids a profile setting for the MVP. | `config/settings/base.py`, `templates/base.html` |
| PD-81 | Translations are written by hand in `.po` files and compiled with a pure-Python script. The `.mo` files are committed. | Built | Windows does not ship GNU gettext. Vercel cannot compile at build time. | `scripts/compile_translations.py`, `locale/` |
| PD-82 | A test fails if any catalog entry lacks a translation. | Built | Catches forgotten strings in the catalog. Strings missing from the catalog are a review item. | `core/tests/test_i18n.py` |
| PD-83 | Dates are stored in UTC and shown and typed in the organization's time zone (set by the owner). | Built | Spec CAL-011. Applying the timezone is debt. | [debt TD-13](technical-debt.md) |

---

## Local environment and operations

| ID | Decision | Status | Why | Where |
| --- | --- | --- | --- | --- |
| PD-90 | Local development uses Docker Compose: MySQL and a Mailpit SMTP server with a web inbox. Both bound to 127.0.0.1. | Built | The same database engine as production; no email leaves the machine. | `docker-compose.yml` |
| PD-91 | Local settings are read from a git-ignored `.env` file. Shell variables win over the file. | Built | Removes dependence on what is set in the current terminal. | `config/settings/base.py` |
| PD-92 | Tests run on SQLite in memory by default and on MySQL with `TEST_DATABASE=mysql`. The full suite runs on both before a change is accepted. | Built | Fast by default; MySQL is the real target. | `config/settings/test.py` |
| PD-93 | Port 8080 is the default local port. | Built | Port 8000 is blocked on some Windows machines. | README |
| PD-94 | Secrets (database passwords, SMTP credentials, the secret key) never go into code, migrations, fixtures or docs. | Built | Basic security hygiene; written into the assistant's rules too. | `.claude/rules/security-and-data.md`, `.gitignore` |
| PD-95 | Email sending is configured by `EMAIL_*` variables. Locally it points to Mailpit. | Built | Production uses the provider's SMTP settings. | `config/settings/base.py`, [deployment guide](deployment.md) |

---

## Added in the final Phase 1 pass

| ID | Decision | Status | Why | Where |
| --- | --- | --- | --- | --- |
| PD-96 | Invitations create the account with no password. The invited person sets it through the password-reset link, which expires in 24 hours and works once. | Built | No shared password is ever sent by email; reuses a flow that is already tested. | `accounts/team.py`, `accounts/signals.py` |
| PD-97 | Removing someone deletes their membership and client access. The account and its history stay. Removal is effective on the next request. | Built | Access is checked on every request, so there is no session to clear. Spec PRM-007. | `accounts/team.py` |
| PD-98 | Only owners manage the team and the organization settings. An owner cannot remove their own access, and the last owner cannot be removed. | Built | Prevents locking the organization out. | `accounts/permissions.py`, `accounts/team.py` |
| PD-99 | Each organization has a time zone (a short list of Brazilian zones plus UTC). Pages and typed dates use it; storage stays UTC. Unknown zones fall back to UTC. | Built | Spec CAL-011. | `accounts/middleware.py`, `accounts/forms.py` |
| PD-100 | The audit trail is readable by owners, filterable by action prefix. | Built | Spec AUTH-020. | `core/views.py` |
| PD-101 | The link of a post published by hand is kept on the piece, optional, and must be a web address. | Built | Keeps proof of publication (INT-010). | `production/domain/content.py` |
| PD-102 | Brand files are added as links with a kind (logo, font, template, reference, other). Only people who can edit briefings add them. | Built | PD-03. Spec CLI-007 is partly met. | `clients/models.py`, `clients/views.py` |
| PD-103 | Leads have a stage and a next action. Proposals have an amount in BRL and a status. Neither is automated. Only owners and account managers see them. | Built | PD-02. | `crm/` |
| PD-104 | The monthly report shows every expected metric for each network. A month with no value shows as N/D; nothing is estimated. Values are typed by hand, always marked as manual, and entering the same month again updates it. | Built | Spec MET-003 and MET-006. | `reports/` |
| PD-105 | An archived client is hidden from lists and cannot receive new content, a link, or a team assignment. Archiving keeps all history. | Built | Spec CLI-005. | `clients/services.py` |

## Phase 1 close

| ID | Decision | Status | Why | Where |
| --- | --- | --- | --- | --- |
| PD-106 | Comments on a piece are visible to the team; the client sees only comments written by client users. Mentions use the person's email and notify only members of the organization. | Built | PRO-004, NTF-006, POR-003. Internal notes never reach the portal. | `production/comments.py`, `portal/views.py` |
| PD-107 | Tasks belong to a client or to the agency. Tasks without a client are visible to owners and account managers only. | Built | TD-06 and the Phase 1 "tarefas" scope. | `tasks/` |
| PD-108 | The calendar shows scheduled pieces by day, with a grid for wide screens and a list for phones. Duplicating a piece starts a new draft with its latest text. | Built | CAL-001, CAL-002, CAL-004. | `production/planning.py` |
| PD-109 | The production board shows one column per stage. Stage changes still happen through the piece's own buttons, so every change is checked and audited. | Built | PRO-005. Drag and drop is debt. | `production/planning.py` |
| PD-110 | Two-step sign-in with an authenticator app (TOTP, RFC 6238) is optional per account. Once turned on, a code is asked once per session, with the same attempt limits as sign-in. | Built (optional) | AUTH-004. Making it mandatory for owners waits for decision D-17. | `accounts/mfa.py`, `accounts/mfa_views.py`, `accounts/middleware.py` |
| PD-111 | The client portal has calendar, results, files and contact. Each shows only the client's own brands. | Built | POR-002, TD-26. | `portal/sections.py` |
| PD-112 | Logs go to standard output, which Vercel and Docker collect. Failed emails and failed notifications are logged, not raised. | Built | ARC-006, TD-14. Alerts that notify a person need an external service. | `config/settings/base.py` |
| PD-114 | Every record uses a **GUID (UUID)** as its primary key, including users. Numbers are not used as identifiers in URLs or events. Documentation codes (`PD-NN`, `TD-NN`, requirement IDs) stay as readable names. | Built | Numbers in URLs reveal how many records exist and let people guess neighbours. A GUID is not guessable and is the same on every database. Enforced by `core/models.py` (`UUIDModel`) and tested in `core/tests/test_identifiers.py`. | `core/models.py`, all apps |
| PD-113 | On phones, a bottom bar gives the main places. The top bar stays for wide screens. The skip link and the current-page marks help keyboard and screen-reader use. | Built | NAV-002, NFR-011. A full accessibility audit has not been done. | `templates/base.html` |

## Changed decisions (kept for history)

| ID | Original decision | Changed to | When and why |
| --- | --- | --- | --- |
| PD-C1 | Database: Supabase (possibly Postgres). | MySQL 8.4. | 2026-11-01, product owner. |
| PD-C2 | Frontend: Next.js. | Server-rendered Django templates. | 2026-11-01, one codebase for the MVP. |
| PD-C3 | Language: Brazilian Portuguese only. | English and Brazilian Portuguese. | 2026-11-01, product owner. |
| PD-C4 | Login by username. | Login by email. | 2026-11-01, product owner's admin access request. |
