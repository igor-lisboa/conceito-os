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
| Login, logout, organizations, memberships, roles | Working | `apps/accounts/` |
| Role-based permissions (owner, account manager, creative, freelancer, client) | Working and tested | `apps/accounts/permissions.py` |
| Clients and brand briefing | Working | `apps/clients/` |
| Client access (who sees which brand) | Working, managed in the admin | `apps/clients/models.py` |
| Content lifecycle (draft → planned → production → internal review → client review → approved → scheduled → published / failed) | Working and tested | `apps/production/domain/` |
| Versions, with approvals tied to the version reviewed | Working | `apps/production/domain/content.py` |
| Editing after approval returns the piece to review | Working | `apps/production/domain/states.py` |
| Freelancers see only the pieces assigned to them | Working | `apps/production/domain/policy.py` |
| Client portal: approve or request changes with a comment | Working | `apps/portal/` |
| English and Português (Brasil) interface, chosen per browser | Working and tested | `web/locale/`, `apps/core/http.py` |
| Audit trail of every state change and approval (append-only) | Working | `apps/core/audit.py` |
| Dashboard counts | Working | `apps/core/views.py` |
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

The root holds only what the tools expect there. Everything else is grouped:

```text
proj-beatriz/
├── manage.py               Django command entry point
├── README.md, CLAUDE.md    this guide, and the instructions for the AI assistant
├── docker-compose.yml      local MySQL and Mailpit
├── vercel.json             Vercel routing (every request goes to api/)
├── requirements*.txt       production and development dependencies
├── ruff.toml               lint rules
├── .env.example            list of environment variables (copy to .env)
│
├── apps/                   the system's contexts (each one is a Django app)
│   ├── accounts/           users, organizations, roles, team, MFA, sign-in
│   ├── clients/            clients, briefing, brand library (links)
│   ├── production/         content lifecycle (hexagonal core with DDD)
│   │   ├── domain/         business rules in plain Python (no Django)
│   │   ├── application/    use cases and port interfaces
│   │   └── adapters/       Django implementation of the ports
│   ├── portal/             client portal (approvals, calendar, results, files)
│   ├── crm/                leads and proposals (manual)
│   ├── reports/            monthly metrics (manual, N/D when missing)
│   ├── tasks/              follow-up tasks
│   ├── notifications/      in-app and email notifications
│   └── core/               shared base: errors, enums, actor, audit log, HTTP helpers
│
├── config/                 Django settings, URLs and WSGI entry point
├── api/                    Vercel entry point (exposes the WSGI app)
├── web/                    what the browser receives
│   ├── templates/          HTML templates
│   ├── static/             CSS and other static files
│   └── locale/             Portuguese (pt-BR) translations
│
├── docs/                   architecture, phase 1 decisions, technical debt, deployment
├── specs/                  product specifications (the source of truth for behavior)
├── scripts/                maintenance scripts (translations)
└── docker/                 initialization of the local MySQL container
```

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

For local work, put the variables in a file named `.env` in the project root.
Copy `.env.example` to `.env` and fill it in. The settings load it automatically,
and variables already set in your shell take priority. The file is git-ignored.
The full list is in [Configuration reference](#configuration-reference).

The values for the Docker database are already in the example:
`MYSQL_HOST=127.0.0.1`, `MYSQL_USER=conceito`, `MYSQL_PASSWORD=conceito-local-only`.
If you see `Access denied for user '<your Windows name>'`, the `MYSQL_USER` variable
is missing: the driver then falls back to your operating system user.

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

Open <http://127.0.0.1:8080/accounts/login/>.

We use port **8080** locally. On some Windows machines port 8000 is blocked
(`Error: You don't have permission to access that port.`) because another program
holds it. To pick a different port, run for example `python manage.py runserver 8090`.

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
| `apps/production/tests/domain/` | The lifecycle rules, approvals, scheduling, failures, policy | No |
| `apps/production/tests/application/` | Permissions, scope, audit and transactions, with in-memory fakes | No |
| `apps/production/tests/adapters/` | Saving and loading the aggregate through real tables | Yes |
| `apps/production/tests/test_views.py`, `apps/portal/tests/` | Full HTTP flows, 403/404 rules, data hidden from clients | Yes |
| `apps/production/tests/test_queries.py` | The read side agrees with the domain policy | Yes |
| `apps/accounts/tests/`, `apps/clients/tests/`, `apps/core/tests/` | Role matrix, sessions, client scope, actors | Yes |

Run one test module while developing:

```bash
python manage.py test production.tests.domain --settings=config.settings.test
```

---

## Database (MySQL)

### Local MySQL with Docker (recommended)

`docker-compose.yml` starts MySQL 8.4 with `utf8mb4` on `127.0.0.1:3306`. Data
is kept in a Docker volume. The passwords are for your machine only.

```bash
docker compose up -d --wait        # start MySQL and wait until it is healthy
docker compose ps                  # should show "healthy"
```

Point the app at it. Use the variables from the Docker file (the defaults match):

```powershell
# Windows PowerShell
$env:MYSQL_HOST = "127.0.0.1"
$env:MYSQL_USER = "conceito"
$env:MYSQL_PASSWORD = "conceito-local-only"
$env:MYSQL_DATABASE = "conceito_os"
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

```bash
# macOS / Linux / Git Bash
export MYSQL_HOST=127.0.0.1 MYSQL_USER=conceito MYSQL_PASSWORD=conceito-local-only MYSQL_DATABASE=conceito_os
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Run the test suite against MySQL instead of SQLite (Django creates and drops a
`test_conceito_os` database; your data is not touched):

```bash
TEST_DATABASE=mysql python manage.py test --settings=config.settings.test
```

Stop or reset the database:

```bash
docker compose down        # stop, keep the data
docker compose down -v     # stop and delete all local data (then run migrate again)
```

The init script in `docker/mysql/init/` runs only when the volume is first
created. If you change it, run `docker compose down -v` and start again.

After the migrations, run `python manage.py createcachetable` once. It creates the
table that counts failed sign-in attempts.

### First administrator

The administrator is created with a command, not by hand. The email and password
come from the `INITIAL_ADMIN_*` values in your `.env` file, so the password is
never written in the code:

```bash
python manage.py create_initial_admin
```

It is safe to run again: it does not duplicate the user or the organization. It
creates the account as a superuser (for `/admin/`) and makes the user the owner of
the default organization, so the same login works in the app. Sign in with the
email address on the login page.

To change the administrator's password, set the new `INITIAL_ADMIN_PASSWORD` and run
`python manage.py create_initial_admin --reset-password`.

### Email (SMTP) and password recovery

The app sends two kinds of email: a **welcome** message when a user is created, and
the **password reset** link from "Forgot your password?". Locally they go to the
Mailpit container, which catches them. Nothing leaves your machine.

Open the inbox at <http://127.0.0.1:8025> after you create the admin or request a reset.

The SMTP settings are the `EMAIL_*` variables in the [configuration reference](#configuration-reference).
The welcome email is written in Portuguese (pt-BR); change `WELCOME_EMAIL_LANGUAGE`
in `apps/accounts/emails.py` to change it. Password reset emails follow the language
the person is browsing in.

### Your own MySQL server

Create the database and user yourself, then set the `MYSQL_*` variables:

```sql
CREATE DATABASE conceito_os CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
CREATE USER 'conceito'@'%' IDENTIFIED BY 'a-strong-password';
GRANT ALL PRIVILEGES ON conceito_os.* TO 'conceito'@'%';
GRANT ALL PRIVILEGES ON `test_conceito_os`.* TO 'conceito'@'%';  -- only if you run tests on MySQL
```

Then run `python manage.py migrate` and `python manage.py createsuperuser`.

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
| `EMAIL_HOST` | No | `127.0.0.1` | SMTP server. Locally the Mailpit container. |
| `EMAIL_PORT` | No | `1025` | SMTP port. |
| `EMAIL_HOST_USER` | Production | empty | SMTP login, if the provider needs one. |
| `EMAIL_HOST_PASSWORD` | Production | empty | SMTP password. Mark as sensitive. |
| `EMAIL_USE_TLS` | No | `False` | Set `True` for most providers on port 587. |
| `EMAIL_USE_SSL` | No | `False` | Set `True` for port 465. |
| `DEFAULT_FROM_EMAIL` | No | `Conceito OS <no-reply@conceito.com.br>` | Sender address. |
| `SITE_URL` | No | `http://127.0.0.1:8080` | Public address of the site, used in email links. |
| `INITIAL_ADMIN_EMAIL` | For the admin command | empty | Email of the first administrator. |
| `INITIAL_ADMIN_PASSWORD` | For the admin command | empty | Its password. Never commit it. |
| `INITIAL_ADMIN_NAME` | No | `Administrador` | Display name. |
| `INITIAL_ADMIN_ORGANIZATION` | No | `Conceito Co` | Organization the admin owns. |

---

## Language

The interface is available in **English** and **Português (Brasil)**. Each
visitor picks the language with the selector at the top of every page. The
choice is stored in a cookie for that browser, so it stays until they change it.

How it works:

- Source text in the code and templates is English. Django's translation system
  (`gettext`) turns it into Portuguese using `web/locale/pt_BR/LC_MESSAGES/django.po`.
- Business rule messages (for example "Cannot change from 'Published' to 'Draft'.")
  are raised by the domain in English and translated at the web edge
  (`apps/core/http.py`), so the domain never depends on Django.
- Enum labels (stages, roles, formats) are translated when they are displayed.

To change or add a translation:

1. Wrap new text with `{% trans "..." %}` in a template, or `gettext("...")` in Python.
2. Add the English text as `msgid` and the Portuguese as `msgstr` in
   `web/locale/pt_BR/LC_MESSAGES/django.po`.
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
- **Rules live in the domain.** `apps/production/domain/` has no Django imports. Views
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

- **Only the local Docker database is migrated.** The production MySQL server does not exist yet; run `migrate` against it once it is ready ([deployment guide](docs/deployment.md)).
- **Publishing is manual.** Scheduling marks the intent; a person publishes and marks it published. Automatic publishing needs the Meta and TikTok integrations ([spec](specs/modules/social-integrations.md)).
- **No file uploads.** Media is a link. Storage on Vercel needs an external service (decision pending).
- **Dates use UTC in forms.** The spec asks for each agency's timezone. The data is stored in UTC; the per-organization timezone is not applied to the screens yet.
- **Client access is managed in the admin.** There is no screen yet for the owner to grant brand access.
- **One organization per screen session.** A user in several organizations can be switched by setting the session key; there is no switcher in the UI yet.
- **Two-step sign-in is optional.** Each person can turn it on under Security. Making it mandatory for owners waits for the decision recorded as D-17.
- **Calendar and board do not drag.** Reschedule and change stages with the buttons on each piece.
- **Alerts for failures go to the logs only.** Paging a person needs an external service.
- **Welcome and invitation emails are in Portuguese.** The language is not stored per person yet.
- **Sign-in attempt counters are per instance on Vercel.** The per-account limit still holds within a shared database cache; a shared store is debt (TD-12).
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
| [docs/phase-1-decisions.md](docs/phase-1-decisions.md) | Every decision taken for the Phase 1 MVP, with its reason and where it lives in the code. |
| [docs/technical-debt.md](docs/technical-debt.md) | What the full specification needs and the code does not do yet, by priority. |
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
