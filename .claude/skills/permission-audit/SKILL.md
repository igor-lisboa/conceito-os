---
name: permission-audit
description: Audit the access control of Conceito OS. Checks that every route has a capability check, that the code matches the role matrix in the spec, and that the important permission rules have tests. Use after adding routes or roles, and before any release.
---

# Permission audit

The most serious risk in this system is one client or one agency seeing another's data. This audit looks for that risk. It only reads and reports. It does not change code.

## Sources of truth

- `specs/product/01-roles-permissions.md` — the matrix written for people.
- `apps/accounts/permissions.py` — the matrix in code (`ROLE_CAPABILITIES`).
- `apps/clients/queries.py`, `apps/production/queries.py`, `apps/production/domain/policy.py`, `apps/tasks/queries.py` — the scope rules.

## Steps

1. **Matrix vs spec.** For each role and each row of the spec table, check the capability in `ROLE_CAPABILITIES`. List the differences. A difference is either a bug in the code or a change the spec needs. Report both possibilities, do not decide.

2. **Every route is guarded.** List every URL pattern (`grep -rn "path(" apps/*/urls.py config/urls.py`). For each view, check it has `CapabilityRequiredMixin` with `required_capability`, or is a public page (login, password reset, i18n, static). Views without a guard are findings.

3. **Scope on every lookup.** Search for `get_object_or_404(` and `.objects.get(` / `.filter(pk=` in views and services. Each one must go through a visible queryset (`visible_clients`, `visible_content`, `visible_tasks`) or filter by `organization`. Lookups with only `pk=` are findings.

4. **Out of scope = 404.** The tests must check that another organization's ID returns 404, not 403. Search the tests for `status_code, 404` and `status_code, 403` to confirm both cases exist for the main flows.

5. **Rules that must have tests.** Confirm a test exists for each:
   - a freelancer sees only their assigned pieces;
   - a client sees only their brands and never internal comments;
   - a creative cannot approve or schedule;
   - the last owner cannot be removed, and nobody removes their own access;
   - a removed member loses access on the next request;
   - the audit trail is append-only.
   Search by name in `apps/*/tests/`.

6. **Run the permission tests**: `./.venv/Scripts/python.exe manage.py test apps.accounts.tests apps.portal.tests apps.production.tests --settings=config.settings.test`

## Report

A table: check, status (ok / gap / finding), file and line. Put findings first, most serious first. For each matrix difference, say which side you think is right and why, and ask the product owner to confirm.
