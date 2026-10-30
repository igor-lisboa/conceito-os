---
name: quality-gate
description: Run the full quality check of the Conceito OS project (lint, tests on SQLite and MySQL, migrations in sync, system check) and report the real result. Use before saying a change is done, before a commit, or when the user asks "está tudo ok?".
---

# Quality gate

Run these steps in order from the project root. Show the real output of each step. Never say a step passed without seeing its output.

Python in this project is the virtualenv interpreter. On Windows Git Bash use `./.venv/Scripts/python.exe`. If the venv is missing, stop and say so.

## Steps

1. **Lint** (report only, do not fix unless asked):
   `./.venv/Scripts/python.exe -m ruff check .`

2. **Tests on SQLite** (default, no database server needed):
   `./.venv/Scripts/python.exe manage.py test --settings=config.settings.test`

3. **Tests on MySQL** (real engine). It needs the local container running. Check first with `docker compose ps`; if it is not healthy, run `docker compose up -d --wait`. Then:
   `TEST_DATABASE=mysql ./.venv/Scripts/python.exe manage.py test --settings=config.settings.test`

4. **Migrations in sync** (must print "No changes detected"):
   `./.venv/Scripts/python.exe manage.py makemigrations --check --dry-run --settings=config.settings.test`

5. **System check**:
   `./.venv/Scripts/python.exe manage.py check --settings=config.settings.test`

6. **Translations complete** (the catalog test already covers it, but report the count):
   `./.venv/Scripts/python.exe scripts/compile_translations.py`

## Report

Give a short table: step, result, and the failing test names or error lines if any. Keep the counts ("279 tests, OK") as printed.

If a step fails, stop there and show the first failure. Do not change code in this skill. Fixing is a separate task.
