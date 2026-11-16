---
name: code-health
description: Measure how easy the code is to read, change and test for a junior developer: test coverage, function and file size, nesting, complexity (ruff C901), missing docstrings in the domain and application layers, and lint. Use before a release, when a module feels hard to change, or when asked about code quality or coverage.
model: haiku
effort: medium
---

# Code health

Run the measurements first; judge the results second.

## Steps

1. Lint (report only):
   `./.venv/Scripts/python.exe -m ruff check .`
2. Size, nesting and docstrings, plus complexity:
   `./.venv/Scripts/python.exe scripts/audit/code_health.py`
3. Coverage. This runs the whole test suite under coverage (about 30 seconds):
   `./.venv/Scripts/python.exe scripts/audit/code_health.py --coverage`
   If `coverage` is not installed, run `pip install -r requirements-dev.txt` first.
4. Read the three largest findings in each category. Open only the top three files; do not
   read the whole codebase.

## Thresholds (in `scripts/audit/code_health.py`)

| Measure | Limit |
| --- | --- |
| Function length | 50 lines |
| Nesting depth | 4 levels of if, for, while, with, try |
| File length | 400 lines |
| Cyclomatic complexity (ruff C901) | 10 |

Migrations and tests are excluded from the size and nesting checks.

## What to report

- Lint: count and first error, or "clean".
- Coverage: total percentage, and the three lowest modules under `apps/` with their numbers.
- Over-limit code: file and function, one line each, with the simplest fix (split the
  function, return early, move a block into a named helper).
- Missing docstrings: only the count by layer, unless asked for the list.

Do not change code in this skill. A refactor is a separate task, done with a test first.
