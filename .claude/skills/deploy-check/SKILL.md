---
name: deploy-check
description: Check that Conceito OS is ready to be deployed to Vercel with its MySQL and SMTP, without deploying anything. Verifies environment variables, production security settings, the Vercel entry point, and that no secret is tracked by git. Use before a deploy or when the user asks whether production is ready.
---

# Deploy check

This skill only verifies. It never deploys, never runs migrations on a production database, and never prints secret values. Do not copy real values from `.env` into any output.

## Steps

1. **Environment variables.** Compare the names read by `config/settings/base.py` (`os.environ.get("...")`) with the keys of `.env.example`. Report variables missing from the example, and variables in the example that the settings do not read.

2. **Production settings.** Run the deploy check with production-like values. Generate a throwaway key of 50+ characters in the same command, so no real secret is needed and nothing is printed:
   `DJANGO_DEBUG=False DJANGO_SECRET_KEY="$(./.venv/Scripts/python.exe -c 'import secrets;print(secrets.token_urlsafe(50))')" MFA_ENCRYPTION_KEY="$(./.venv/Scripts/python.exe -c 'from cryptography.fernet import Fernet;print(Fernet.generate_key().decode())')" DJANGO_ALLOWED_HOSTS=example.vercel.app ./.venv/Scripts/python.exe manage.py check --deploy --settings=config.settings.base`
   Expected warnings: only the optional HSTS items (`security.W005`, `security.W021`). Anything else is a finding, including a missing `MFA_ENCRYPTION_KEY` (`accounts.E001`), which the command above avoids by setting a throwaway one. A short-key warning (`security.W009`), which means the key was too short.

3. **Vercel entry point.** Check `api/index.py` exposes `app`, and that it imports without error:
   `./.venv/Scripts/python.exe -c "import api.index as m; print(type(m.app).__name__)"` (with `DJANGO_SECRET_KEY` set to a placeholder). Check `vercel.json` routes everything to `api/index.py`.

4. **Dependencies.** `requirements.txt` must not contain development tools (ruff belongs in `requirements-dev.txt`). Check the pins have upper bounds for Django 5.2 (`>=5.2,<6.0`).

5. **Secrets not in git.** Run `git ls-files | grep -i "\.env$"` (must print nothing). Search tracked files for obvious secrets: `git grep -n "PASSWORD\s*=\s*['\"][^'\"]\+['\"]"` and `git grep -n "SECRET_KEY\s*=\s*['\"]"`. Ignore test settings and documentation examples; report anything else.

6. **Migrations and cache table.** Check the deployment guide lists `migrate` and `createcachetable` (`docs/deployment.md`). Check `makemigrations --check` is clean.

7. **Static files.** Check `web/static` exists and `WHITENOISE_USE_FINDERS` is on in the settings.

8. **Email settings.** Check `EMAIL_BACKEND` defaults to SMTP and that the deployment guide lists the `EMAIL_*` and `SITE_URL` variables.

## Report

A checklist: each item ok / missing / finding. Then a short list of what only the owner can do: create the Vercel project, set the variables in Vercel (secret ones marked sensitive), create the MySQL server and the SMTP account, run `migrate` and `createcachetable` once against production, create the first administrator with `create_initial_admin` (rotate the local password first), and set up backups.
