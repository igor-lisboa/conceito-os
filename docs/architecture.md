# Architecture

This document explains **how the code is organized, why, and what we gave up**.
Read it before adding a feature or moving code between folders.

Short version: Django provides the web, admin, auth and ORM. The business rules
of the content lifecycle live in a plain-Python domain model (DDD), reached
through application services, with Django kept at the edges (hexagonal /
ports-and-adapters). Simple parts of the system are not forced into this shape.

---

## 1. The decision in one page

| Question | Answer | Why |
| --- | --- | --- |
| Framework | Django 5.2 (LTS) | Auth, admin, migrations, forms and security come built in; a junior developer can find help for almost anything. |
| Database | MySQL (via PyMySQL) | Chosen by the product owner. PyMySQL is pure Python, so it installs on Windows and Vercel without compiling. |
| Where do rules live? | In a domain model that does not import Django | The lifecycle of a piece of content has many rules (approval, edit invalidation, scheduling, failures). They must be testable without a database and must not be scattered across views and model methods. |
| Pattern | Hexagonal (ports and adapters) + DDD tactical patterns | Keeps the rules independent of Django, the database and the clock. The spec describes these rules in detail, so the code should mirror the spec. |
| Where do we NOT apply it? | `clients` (briefing, client records) and `accounts` (login, roles) | These are mostly CRUD with a few rules. A full hexagon there would add files and mapping code with no benefit. See section 6. |

---

## 2. Layers and the dependency rule

```text
            ┌─────────────────────────────────────────────────────┐
            │  Web / delivery (Django views, templates, forms)     │  driving adapters
            │  production/views.py, portal/views.py, clients/...   │
            └───────────────┬─────────────────────────────────────┘
                            │ calls
            ┌───────────────▼─────────────────────────────────────┐
            │  Application (use cases)                             │
            │  production/application/content_service.py          │
            │  - checks capability, scope, transaction, audit      │
            │  - depends on PORTS (interfaces), not on Django      │
            └───────────────┬───────────────────┬─────────────────┘
                            │ uses              │ uses (port)
            ┌───────────────▼─────────┐   ┌─────▼──────────────────────────────┐
            │  Domain (business rules)│   │  Adapters (driven)                  │
            │  production/domain/     │   │  production/adapters/               │
            │  - Content aggregate    │   │  - DjangoContentRepository          │
            │  - state machine        │   │  core/audit.py (DjangoAuditLog)     │
            │  - policy (who sees what)│  │  composition.py (wires everything)  │
            │  NO Django. NO database.│   └─────┬──────────────────────────────┘
            └─────────────────────────┘         │ ORM
                                       ┌────────▼────────┐
                                       │  MySQL tables    │
                                       └─────────────────┘
```

**The dependency rule:** arrows only point inward. The domain knows nothing
about the application, the adapters or Django. The application knows the domain
and the port interfaces, but not the Django adapters. Only the adapters and the
web layer import Django models.

This is enforced by:
- the test suite: `production/tests/domain/` runs with no database and no Django models;
- code review and the rule file `.claude/rules/architecture.md`;
- `ruff`, which flags unused or missing imports (it does not enforce layering, so review matters).

---

## 3. Bounded contexts

A bounded context is a part of the business with its own words and rules. We
keep each one in its own Django app.

| App | Context | Style | Notes |
| --- | --- | --- | --- |
| `accounts` | Identity, organizations, roles | Django + capability matrix | `permissions.py` is the single source of the role matrix. |
| `clients` | Client brands, briefing, client access | Simple services (Django ORM) | Few rules; kept simple on purpose. |
| `production` | Content lifecycle, versions, approvals, scheduling | **Hexagonal + DDD** | The core of the product. Most business rules live here. |
| `portal` | Client-facing approval screens | Delivery adapter | Calls the same `production` use cases as the internal app, with a smaller surface. |
| `core` | Shared kernel and cross-cutting code | Plain Python + adapters | Errors, `Actor`, enums, audit log, HTTP error translation. |

### 3.1 The `production` folder map

```text
production/
  domain/                  pure Python. Test without a database.
    states.py              the lifecycle as data: allowed moves, edit rules
    content.py             Content aggregate, value objects, domain events
    policy.py              who may see a piece (pure function)
  application/             use cases. Depends on domain + port interfaces.
    ports.py               Protocols: ContentRepository, AuditLog
    content_service.py     one method per user action
  adapters/                Django implementations of the ports
    django_repository.py   Content <-> ContentItem / ContentVersion / Approval
  composition.py           wires the real Django adapters into the service
  models.py                database tables (NOT the domain model)
  queries.py               read side for lists and counts (ORM)
  forms.py, views.py, urls.py   web layer
  tests/
    domain/                pure tests of the rules (fastest)
    application/           use cases with in-memory fakes (no database)
    adapters/              save/load through the real tables
    test_views.py          HTTP flow end to end
    test_queries.py        read side agrees with the domain policy
```

---

## 4. One request, step by step

Example: an account manager approves a piece internally.

1. **URL** `POST /conteudos/12/acao/approve_internal/` reaches `ContentActionView` (web layer).
2. The view checks the user is logged in and has `ACCESS_INTERNAL` (`CapabilityRequiredMixin`).
3. The view builds an `Actor` from the logged-in membership (`core/actors.py`). The actor is a plain object: user id, organization, role, the client ids it may see.
4. The view calls `ContentService.decide_internal(actor, 12, approve=True, comment="")`.
5. The service checks the capability `APPROVE_INTERNAL` (`accounts/permissions.py`).
6. The service loads the piece through the `ContentRepository` port. The adapter returns a `Content` aggregate.
7. The service checks the actor may access the piece (`policy.can_access`). If not, `NotFound` (HTTP 404).
8. The service opens a transaction and calls `content.decide_internal(...)`. **This is where the business rule runs**: the piece must be in internal review; approval moves it to client review, or straight to approved when the client does not need to approve. The aggregate records an `Approval` and emits domain events.
9. The service saves the aggregate through the repository adapter (inserts only the new version and approval rows), then writes one audit row per domain event.
10. The transaction commits. The view turns the result into a success message and a redirect. `DomainError` becomes an error message; `Forbidden` becomes HTTP 403.

If step 8 breaks a rule, nothing is saved and nothing is audited (tested in
`test_failed_domain_rule_saves_nothing_and_audits_nothing`).

---

## 5. Why this structure is worth it

### Concrete benefits in this codebase

- **Rules are readable in one place.** `domain/states.py` is the whole lifecycle on one screen. A product owner can check it against `specs/technical/states-events.md`.
- **Fast, precise tests.** The domain has 48 tests that run without a database. The application layer has 19 more that use in-memory fakes. Only the adapter, query, HTTP and portal tests (26 in total) touch the database.
- **Rules cannot be skipped by accident.** Views never change a state directly. Every change goes through `Content`, so the edit rule (an approved piece returns to review), the rule that a scheduled piece cannot be edited, and the rule that approvals point at the exact version reviewed are enforced everywhere.
- **Audit is a by-product.** Each domain event becomes an audit row in the same transaction. A rule failure leaves no half-written trail.
- **Swappable infrastructure.** The MySQL decision was made after the design. Changing the database, the clock or the audit storage touches only `adapters/` and `composition.py`.
- **Specs and code speak the same language.** Names such as `CLIENT_REVIEW`, `decide_internal`, `RETURNS_TO_INTERNAL_REVIEW_ON_EDIT` map to spec IDs (PRO-013, CRM-007, BIL-010…). This matters because the product owner reads the specs, not the code.
- **Maintenance for juniors.** Each folder has one job, and a feature has a clear recipe (section 8).

### Honest costs

- **More files and more indirection.** A feature touches domain, service, adapter and view. For a small CRUD screen that is overkill, which is why `clients` is not built this way.
- **A mapping layer.** `django_repository.py` converts between the aggregate and the ORM rows. It is about 150 lines that a simpler design would not have. The cost is paid once per table and is covered by round-trip tests.
- **Two representations of "who can see what".** The domain policy (`policy.py`) and the database filter (`queries.py`) express the same rule. `test_queries.py` checks that they agree on the same data, so drift is caught.
- **The team must learn the vocabulary.** Aggregate, port, adapter, use case. This document and the module docstrings are the onboarding material.

---

## 6. Where we deliberately did NOT apply it

Good sense means not paying the cost where there is no benefit. We use the
simple style (Django models plus service functions) when **all** of these hold:

- the rules are few and obvious (for example, "a briefing belongs to one client");
- the data is mostly created, read and updated as is;
- no state machine, no approvals, no external side effects.

`clients` and `accounts` meet these conditions. If `clients` grows real rules
(for example, client archiving with contract checks), move that part into a
domain model in the same way as `production`. Do not rewrite it before then.

Reads (lists, counts, dashboards) use the ORM directly in `queries.py`. A list
does not need the full aggregate, and rebuilding every piece just to show a
table would be slow. Writes always go through the application layer.

---

## 7. Alternatives we considered

| Option | What it is | Good | Problem for this project | Why not now |
| --- | --- | --- | --- | --- |
| **Fat Django models** (MVT, rules in `models.py` and views) | The Django default. Logic lives in model methods and views. | Least code. Everyone knows it. Fast to start. | Rules end up in views, admin actions and model `save()` methods. Hard to test without the database. Hard to see the whole lifecycle. The content rules are too rich for this. | Works for the first screens; becomes hard to trust once approvals, versions and schedules interact. We kept Django models as persistence, which is the best part of this option. |
| **Django REST Framework + SPA** (React/Next.js front end) | API in Django, separate front end | Clean split of front and back. Good for mobile apps later. | Two codebases, two deploys, auth over tokens, more moving parts for a small team. The spec's mobile needs can be met with responsive server-rendered pages. | Revisit when a native app or a rich editor needs an API. The application layer means an API can be added as one more driving adapter. |
| **Full Clean Architecture everywhere** | Interfaces and a dependency-injection container for every class, every app. | Maximum flexibility. | Heavy ceremony for CRUD parts. Many files with one method each. Hard for a junior developer. | We use the pattern only where the rules are. The composition root is a single function. |
| **Microservices** | One service per context, over the network | Independent deploys and scaling. | Distributed transactions, network failures, observability cost. The product has one team and one database. | Not needed at this size. The bounded contexts are already separate modules, so a split is possible later. |
| **Event sourcing + CQRS everywhere** | Store events as the source of truth; separate read and write models | Perfect audit trail. Powerful projections. | Complex to build and to reason about. Schema changes of events are hard. | We take the useful part: domain events drive the audit log. Full event sourcing is not needed for approvals. |
| **Backend as a service** (Supabase / Firebase with RLS or cloud functions) | Database and auth provided; rules in SQL policies or serverless functions | Fast start. Built-in auth and row security. | Business rules spread across SQL policies, functions and the front end. Hard to test as a unit. Vendor lock-in. The product owner chose MySQL. | Rules must stay in one testable place. Authorization lives in the application code, so it is unit-testable. Database-level row security can still be added later as a second line of defence. |
| **FastAPI / Flask with SQLAlchemy** | Lighter Python frameworks | Less framework, more control. Async support. | We would rebuild auth, admin, forms, CSRF and migrations ourselves. The admin is a real productivity tool for the owner. | Django's built-in admin, auth and security defaults are worth more for this team. |
| **Node.js / Next.js full stack** (the first suggestion in the spec) | JavaScript everywhere | One language across the stack. Good hosting on Vercel. | The rules would be written in TypeScript with the same layering questions. The product owner asked for Django. | The spec kept the stack "to be validated"; Django was chosen explicitly. |

---

## 8. Recipe: adding a feature in `production`

1. **Spec first.** Update the module spec and `specs/technical/states-events.md` if a state changes. Give the rule an ID.
2. **Domain.** Add the rule to `Content` (or a new value object). Raise `DomainError` for invalid input. No Django imports. Write a test in `tests/domain/`.
3. **Application.** Add a method to `ContentService`: capability check, load with scope, call the domain, save, audit. Test with the fakes in `tests/application/`.
4. **Adapter.** Only if the stored data changes: update the ORM model and the mapping in `django_repository.py`. Add a migration with `makemigrations`. Add a round-trip test in `tests/adapters/`.
5. **Web.** Add the form, view and URL. Map errors with `run_action`. Add an HTTP test for the flow and for the permission/404 cases.
6. **Spec evidence.** Record the test paths in the module spec's "Evidence" section and add a CHANGELOG line.

---

## 9. Rules for contributors

- The domain (`production/domain/`) never imports Django, the database, `datetime.now()` or request data. Pass `now` in as an argument.
- Views never change a `Content` state or create approvals directly. Call `ContentService`.
- Every use case checks the capability first, then the scope, then the domain rule.
- Out-of-scope records return `NotFound`, never `Forbidden`, so IDs cannot be probed.
- Audit events are written inside the same transaction as the change.
- The Django admin is read-only for content and approvals. Changes go through the application so the rules always apply.
- Enums are `LabeledEnum` from `core/enums.py` (pure Python). Use `translated_choices()` from `core/choices.py` for Django fields.
- Domain messages are English identifiers with named parameters: `DomainError("Cannot change from '{source}' to '{target}'.", source=..., target=...)`. The web edge translates them (`core/http.py`). Never import `gettext` into `production/domain/`.
- Add a test with every new rule. Prefer a test that describes a user situation over a test that checks a getter.
