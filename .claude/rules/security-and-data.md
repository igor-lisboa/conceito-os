---
paths:
  - "src/**"
  - "app/**"
  - "supabase/**"
  - "migrations/**"
  - "**/*.sql"
---

# Security and data (when writing code)

Sources: `specs/technical/security-privacy.md`, `specs/product/01-roles-permissions.md`, `specs/technical/data-model.md`, `specs/technical/states-events.md`.

- Every business table has `organization_id`; every query filters on it; RLS with tests where applicable.
- Authorization by organization + user + client on the **backend**, in one central place; never only in the UI.
- Endpoints that receive an ID verify that the resource belongs to the caller's tenant/client (no IDOR).
- Files in private storage, served through signed short-lived URLs.
- No secrets/tokens on the client; OAuth tokens encrypted; never store social network passwords.
- Webhooks and jobs: authenticated, idempotent, tolerant of duplicates and out-of-order delivery.
- Sensitive actions (approve, publish, export/delete, permission change) write `audit_events`.
- State transitions only through the machines in `specs/technical/states-events.md`; reject invalid ones.
- Integration errors never delete drafts nor fake success.
- No fictitious data shown as real; missing = `N/D`.
- Timestamps in UTC; money as integer cents or exact decimal.
- Passwords and SMTP credentials never go into code, migrations, fixtures, docs or commit messages. They come from environment variables (`.env` locally, the hosting settings in production). `.env` is git-ignored; never print or copy its values into other files.
- Emails are sent only through `accounts/emails.py` or Django's password reset views, so the failure handling and the link format stay in one place.
