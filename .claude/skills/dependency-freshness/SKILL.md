---
name: dependency-freshness
description: Check that the language version, framework and libraries are current and supported: Python version, Django LTS status, outdated packages and known vulnerabilities. Use monthly, before a deploy, or when asked about upgrades.
model: haiku
effort: low
---

# Dependency and runtime freshness

Report only. Do not upgrade anything: an upgrade is a change that needs a test run and,
for Django or Python, a decision by the team.

## Steps

1. Runtime versions in use:
   `./.venv/Scripts/python.exe --version`
   The project targets Python 3.12 (`ruff.toml`, `target-version = "py312"`). Say if they differ.
2. Pinned constraints: read `requirements.txt` and `requirements-dev.txt`. The framework is
   `Django>=5.2,<6.0`, which is the LTS line. Check the Django download page for the
   current LTS and its end-of-support date; say if the project's line will end soon.
3. Outdated packages in the virtualenv:
   `./.venv/Scripts/python.exe -m pip list --outdated`
4. Known vulnerabilities, only if `pip-audit` is installed:
   `./.venv/Scripts/python.exe -m pip_audit -r requirements.txt`
   If it is not installed, say so and recommend installing it. Do not install it unasked.
5. Report a table: package, installed, latest, constraint, and whether a bump is inside the
   pinned range (a bump outside the range is a decision for the team).

## Rules for the report

- Patch and minor bumps inside the pinned range: list them as safe to batch.
- Major bumps (Django 6, cryptography major): list them with the upgrade risk. Do not recommend
  them without a test run on both SQLite and MySQL.
- Cite the source of any version date. Never state an end-of-support date from memory.
