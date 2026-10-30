---
name: new-feature
description: Add a feature to the Conceito OS project in the order the architecture requires (spec, domain rule, use case, adapter, web, tests, evidence). Use when the user asks to build a new function, screen, rule or model.
---

# New feature

Follow the recipe in `docs/architecture.md`, section 8. Do the steps in order. Do not skip the spec step.

## Before any code

1. **Find the spec.** Look in `specs/modules/` for the requirement ID. If there is none, write the requirement in the module spec first, with a new ID in the module's prefix. Mark anything not in the source spec as `PROPOSAL`.
2. **Find the layer.** Ask: is this a business rule with states, approvals or scope? Then it belongs in `apps/production/domain` (or the matching context) with a use case. Is it simple CRUD? Then use the simple style used by `apps/clients` and `apps/accounts`. Check `docs/architecture.md` section 6.
3. **Check the rules for the feature.** Read `.claude/rules/` for the paths you will touch.

## Steps

1. **Domain rule** (if any): code with no Django import, a test in `tests/domain/` that describes a situation.
2. **Use case / service**: check the capability first, then the scope (out of scope returns `NotFound`, never `Forbidden`), then the domain. Write the audit event in the same transaction. Test with the fakes in `tests/application/`.
3. **Model** (if any): inherit `UUIDModel` from `apps/core/models.py`. Never use a plain `models.Model` for a business record. Then `./.venv/Scripts/python.exe manage.py makemigrations <app> --settings=config.settings.test`. Review the migration file.
4. **Web**: form, view, URL. Route params use `<uuid:pk>`. Errors go through `run_action` in `apps/core/http.py`. Every user-visible string uses `{% trans %}` or `gettext`.
5. **Translations**: run the `i18n-sync` skill.
6. **Tests**:
   - the happy path;
   - the wrong role gets 403;
   - the record of another client or organization gets 404;
   - the invalid input is refused and nothing changes.
7. **Evidence**: list the test files in the spec's `## Evidence` section. Add a changelog line.
8. Run the `quality-gate` skill.

## Report

The spec ID covered, the files created or changed by layer, the test counts, and any decision you had to make (list them, so the user can confirm).
