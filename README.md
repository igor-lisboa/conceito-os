# Conceito OS

A web platform for social media agencies. It covers the work from the first
client briefing to the published post and its results: client records, content
production, internal review, client approval through a portal, scheduling and
publishing status.

Built by and for **Conceito Co**, with **Beatriz** as product owner.

> **Status: early development.** The core of the content lifecycle and the
> client portal work and are tested. CRM, billing, metrics, social network
> integrations, notifications and AI features are specified but not built yet.
> See [What works today](#what-works-today) and the [roadmap](specs/planning/roadmap.md).

---

## Contents

- [What works today](#what-works-today)
- [Tech stack](#tech-stack)
- [Project layout](#project-layout)
- [Getting started (local)](#getting-started-local)
- [Running the tests](#running-the-tests)
- [Database (MySQL)](#database-mysql)
- [Deployment (Vercel)](#deployment-vercel)
- [Configuration reference](#configuration-reference)
- [How we work](#how-we-work)
- [Known limitations](#known-limitations)
- [Documentation map](#documentation-map)

---

## What works today

| Area | Status | Where to look |
| --- | --- | --- |
| Login, logout, organizations, memberships, roles | Working | `accounts/` |
| Role-based permissions (owner, account manager, creative, freelancer, client) | Working and tested | `accounts/permissions.py` |
| Clients and brand briefing | Working | `clients/` |
| Client access (who sees which brand) | Working, managed in the admin | `clients/models.py` |
| Content lifecycle (draft → planned → production → internal review → client review → approved → scheduled → published / failed) | Working and tested | `production/domain/` |
| Versions, with approvals tied to the version reviewed | Working | `production/domain/content.py` |
| Editing after approval returns the piece to review | Working | `production/domain/states.py` |
| Freelancers see only the pieces assigned to them | Working | `production/domain/policy.py` |
| Client portal: approve or request changes with a comment | Working | `portal/` |
| English and Português (Brasil) interface, chosen per browser | Working and tested | `locale/`, `core/http.py` |
| Audit trail of every state change and approval (append-only) | Working | `core/audit.py` |
| Dashboard counts | Working | `core/views.py` |
| Publishing to Instagram / TikTok | **Not built.** Publishing is marked manually. | specs/modules/social-integrations.md |
| CRM, proposals, contracts, metrics, reports, finance, billing | **Not built.** Specified only. | specs/modules/ |
| Notifications, AI engines, automations | **Not built.** Specified only. | specs/modules/ |

---

## Tech stack

| Layer | Choice | Why |
| --- | --- | --- |
| Language | Python 3.12 | Readable, widely known, good libraries. |
| Web framework | Django 5.2 (LTS) | Auth, admin, forms, migrations and security defaults included. |
| Database | MySQL 8 through PyMySQL | Chosen by the product owner. PyMySQL is pure Python, so it installs on Windows and Vercel without build tools. |
| Static files | WhiteNoise | Serves static files from the app itself, so the serverless deployment needs no extra storage. |
| Hosting | Vercel (Python runtime) | Git-based deploys and previews. |
| Tests | Django's test runner | Built in. No extra framework to learn. |
| Lint | Ruff | One fast tool for style and common bugs. |

The architecture (hexagonal core with DDD for the content lifecycle) is explained in
[docs/architecture.md](docs/architecture.md). It also lists the alternatives we
considered and why we did not choose them.

---

## Project layout

```text
proj-beatriz/
├── manage.py                 Django command entry point
├── api/index.py              Vercel entry point (exposes the WSGI app)
├── vercel.json               Routes every request to api/index.py
├── requirements.txt          Production dependencies
├── requirements-dev.txt      Development tools (ruff)
├── .env.example              Environment variables template (never commit .env)
│
├── config/                   Project settings and URLs
│   └── settings/base.py      Everything configurable comes from environment variables
│   └── settings/test.py      Test settings (SQLite in memory, so tests need no MySQL)
│
├── accounts/                 Users, organizations, memberships, roles, permission matrix
├── clients/                  Client brands, briefing, client access (simple services)
├── production/               Content lifecycle (hexagonal core + DDD)
│   ├── domain/               Business rules in plain Python (no Django)
│   ├── application/          Use cases (ContentService) and port interfaces
│   ├── adapters/             Django implementation of the repository port
│   ├── composition.py        Wires the real adapters into the use cases
│   └── tests/                domain/, application/, adapters/, HTTP and query tests
├── portal/                   Client-facing approval screens
├── core/                     Shared kernel: errors, Actor, enums, audit log, HTTP helpers
│
├── templates/                HTML templates (one folder per app)
├── static/                   CSS and other static files
├── docs/                     Architecture and deployment guides
└── specs/                    Product specifications (the source of truth for behavior)
```

---

## Getting started (local)

You need Python 3.12 and, to run the app with real data, a MySQL 8 server (see
[Database](#database-mysql)). The tests do not need MySQL.

### 1. Create the virtual environment and install dependencies

```powershell
# Windows PowerShell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
```

```bash
# macOS / Linux / Git Bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
```

### 2. Set the environment variables

Django does not read `.env` files on its own. Set the variables in your shell
before each command. The full list is in [Configuration reference](#configuration-reference).

```powershell
# Windows PowerShell (for local development)
$env:DJANGO_SECRET_KEY = python -c "import secrets; print(secrets.token_urlsafe(50))"
$env:DJANGO_DEBUG = "True"
```

```bash
# macOS / Linux / Git Bash
export DJANGO_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(50))')"
export DJANGO_DEBUG=True
```

Keep the generated key the same while you develop, or your sessions reset.

### 3. Run the development server

This needs the MySQL database to exist and have its tables (see [Database](#database-mysql)).

```bash
python manage.py runserver
```

Open <http://127.0.0.1:8000/accounts/login/>.

---

## Running the tests

```bash
python manage.py test --settings=config.settings.test
python -m ruff check .
```

The test settings use SQLite in memory, so the tests never touch MySQL. The
suite runs in a few seconds. Test layers:

| Folder | What it checks | Database? |
| --- | --- | --- |
| `production/tests/domain/` | The lifecycle rules, approvals, scheduling, failures, policy | No |
| `production/tests/application/` | Permissions, scope, audit and transactions, with in-memory fakes | No |
| `production/tests/adapters/` | Saving and loading the aggregate through real tables | Yes |
| `production/tests/test_views.py`, `portal/tests/` | Full HTTP flows, 403/404 rules, data hidden from clients | Yes |
| `production/tests/test_queries.py` | The read side agrees with the domain policy | Yes |
| `accounts/tests/`, `clients/tests/`, `core/tests/` | Role matrix, sessions, client scope, actors | Yes |

Run one test module while developing:

```bash
python manage.py test production.tests.domain --settings=config.settings.test
```

---

## Database (MySQL)

The database is not provisioned yet, so the code is ready but **no migrations
have been applied to a real server**. When the MySQL server is ready:

1. Create the database and user:

   ```sql
   CREATE DATABASE conceito_os CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
   CREATE USER 'conceito'@'%' IDENTIFIED BY 'a-strong-password';
   GRANT ALL PRIVILEGES ON conceito_os.* TO 'conceito'@'%';
   ```

2. Set `MYSQL_*` variables (see the reference) and run:

   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

Migrations are already generated in each app's `migrations/` folder. Run `python manage.py showmigrations` to see them. When you change a
model, run `python manage.py makemigrations <app>` and review the file before
committing it.

---

## Deployment (Vercel)

Full step-by-step guide: [docs/deployment.md](docs/deployment.md).

In short:

1. Push the repository and import it in Vercel (framework preset **Other**).
2. Set the environment variables in the Vercel project (Production).
3. Run `python manage.py migrate` **once from your machine** against the production
   database. Vercel does not run migrations.
4. Create the first owner in the Django admin and add clients and memberships.

---

## Configuration reference

All configuration comes from environment variables. See `config/settings/base.py`.

| Variable | Required | Default | Purpose |
| --- | --- | --- | --- |
| `DJANGO_SECRET_KEY` | Yes | none | Signing key. Django refuses to start without it. |
| `DJANGO_DEBUG` | No | `False` | `True` only on your machine. |
| `DJANGO_ALLOWED_HOSTS` | No | `localhost,127.0.0.1` | Comma-separated host names. |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | No | empty | Comma-separated `https://` origins for production. |
| `DJANGO_CONN_MAX_AGE` | No | `0` | Database connection reuse, in seconds. Keep 0 on Vercel. |
| `MYSQL_DATABASE` | No | `conceito_os` | |
| `MYSQL_USER` | Yes, for MySQL | empty | |
| `MYSQL_PASSWORD` | Yes, for MySQL | empty | |
| `MYSQL_HOST` | No | `127.0.0.1` | |
| `MYSQL_PORT` | No | `3306` | |

---

## Language

The interface is available in **English** and **Português (Brasil)**. Each
visitor picks the language with the selector at the top of every page. The
choice is stored in a cookie for that browser, so it stays until they change it.

How it works:

- Source text in the code and templates is English. Django's translation system
  (`gettext`) turns it into Portuguese using `locale/pt_BR/LC_MESSAGES/django.po`.
- Business rule messages (for example "Cannot change from 'Published' to 'Draft'.")
  are raised by the domain in English and translated at the web edge
  (`core/http.py`), so the domain never depends on Django.
- Enum labels (stages, roles, formats) are translated when they are displayed.

To change or add a translation:

1. Wrap new text with `{% trans "..." %}` in a template, or `gettext("...")` in Python.
2. Add the English text as `msgid` and the Portuguese as `msgstr` in
   `locale/pt_BR/LC_MESSAGES/django.po`.
3. Compile the catalog. This uses a pure Python script, so no GNU gettext tools are needed:

   ```bash
   python scripts/compile_translations.py
   ```

The test suite fails if an entry in the Portuguese catalog has no translation.
A string that is missing from the catalog altogether is not caught by a test, so
check the Portuguese screen after adding text. Dates and numbers follow the
selected language automatically.

## How we work

- **Specs first.** Behavior is defined in [specs/](specs/README.md). A change to a
  rule starts with the spec, then the code, then the tests. The spec keeps a
  changelog and an "Evidence" section that names the tests proving each rule.
- **Rules live in the domain.** `production/domain/` has no Django imports. Views
  never change a content state directly; they call `ContentService`.
- **Every rule has a test that describes a situation**, such as "a freelancer
  cannot approve their own piece" or "a client cannot see another brand's piece".
- **Lint before you commit:** `python -m ruff check .`
- **Read the guides** before a large change: [docs/architecture.md](docs/architecture.md)
  has a recipe for adding a feature.

Working with Claude Code in this repository: `CLAUDE.md` and `.claude/rules/`
describe the rules the assistant follows (spec-driven, no invented requirements,
architecture boundaries).

---

## Known limitations

These are known gaps, not bugs. They are tracked in the specs.

- **No database has been migrated yet.** Migrations are generated; they have not been run against MySQL.
- **Publishing is manual.** Scheduling marks the intent; a person publishes and marks it published. Automatic publishing needs the Meta and TikTok integrations ([spec](specs/modules/social-integrations.md)).
- **No file uploads.** Media is a link. Storage on Vercel needs an external service (decision pending).
- **Dates use UTC in forms.** The spec asks for each agency's timezone. The data is stored in UTC; the per-organization timezone is not applied to the screens yet.
- **Client access is managed in the admin.** There is no screen yet for the owner to grant brand access.
- **One organization per screen session.** A user in several organizations can be switched by setting the session key; there is no switcher in the UI yet.
- **No password reset, MFA or invitations by email.** Spec items AUTH-002, AUTH-004 and AUTH-011 are pending.
- **Dark mode and tablet-specific layouts** are out of scope (see the design system spec).

---

## Documentation map

| Document | What it is for |
| --- | --- |
| [specs/README.md](specs/README.md) | Product specifications: what the product must do, with requirement IDs. Start here for the product. |
| [specs/PROCESS.md](specs/PROCESS.md) | How to keep the specs and the code in sync. |
| [specs/planning/roadmap.md](specs/planning/roadmap.md) | Phases and build order. |
| [specs/planning/risks-open-decisions.md](specs/planning/risks-open-decisions.md) | Open decisions waiting for the product owner. |
| [docs/architecture.md](docs/architecture.md) | How the code is organized, why, and the alternatives we rejected. |
| [docs/deployment.md](docs/deployment.md) | Vercel and MySQL setup, step by step. |
| [CLAUDE.md](CLAUDE.md) | Instructions for the AI assistant working in this repository. |

---

## Glossary

| Term | Meaning |
| --- | --- |
| Organization / agency | The company using the platform. All data belongs to one organization. |
| Client | A brand served by the agency. Not the platform's subscriber. |
| Content / piece | One post or video for a client. Its text is kept in versions. |
| Version | A saved state of a piece's text and media. |
| Approval | A decision (internal or client) tied to the version that was reviewed. |
| Internal review | The agency checks the piece before the client sees it. |
| Client review | The client approves or asks for changes in the portal. |
| Scheduled / published / failed | Publishing states. A failure is never shown as published. |
| N/D | Data not available. Shown instead of an invented number. |
