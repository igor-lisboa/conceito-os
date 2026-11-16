# Deployment (Vercel + PostgreSQL)

The app runs on Vercel as a Python serverless function. Vercel routes every
request to `api/index.py`, which exposes the Django WSGI app. Static files are
served by WhiteNoise from the app folders, so no separate build step is needed.

The database is a **PostgreSQL server that you provide** (a managed service).
Vercel cannot host it, and the function must reach it over the network.

Two connection strings are used (see `.env.example`):

- `DATABASE_URL_READWRITE`: the primary. Every write goes here, and reads that must be current.
- `DATABASE_URL_READONLY` (optional): a read-only connection, to a replica or a role with
  SELECT rights only. Lists, counts and reports read from it, which keeps the primary free.

Create the read-only role with `GRANT SELECT` only. The app never writes through it,
but a database-level limit protects the data if a string is ever used by mistake.

## 1. Things to know before you start

- **Migrations are not run by Vercel.** Run them once from your machine against
  the production database, then deploy. Running them on every request would be
  wrong, and the build step has no database access.
- **No file uploads yet.** Vercel's filesystem is read-only except `/tmp`, and it
  is erased between requests. Media is stored as URLs until a storage decision
  is made (see `specs/planning/risks-open-decisions.md`).
- **Serverless database connections.** Each cold start opens new connections.
  Keep `DB_CONN_MAX_AGE=0` and use the provider's connection pooler (PgBouncer or
  equivalent) in the connection string, so many instances share few connections.
- **`/tmp` is the only writable path.** Nothing in the app writes files, so this
  is fine today.

## 2. Prepare the database

1. Create a PostgreSQL 16 or newer database named `conceito_os`.
2. Create a read/write user for that database only, and a read-only user with SELECT rights.
3. Allow connections from your machine (for the first migration) and from Vercel,
   with TLS (`sslmode=require`). Managed providers document the options.

## 3. Create the Vercel project

1. Push the repository to GitHub (or another Git host Vercel supports).
2. In Vercel, click **Add New → Project** and import the repository.
3. Framework preset: **Other**. Leave the build and output settings empty.
   `vercel.json` already routes all requests to `api/index.py`.
4. Python version: the project was written for Python 3.12. Confirm the
   runtime version shown in the project settings.

## 4. Set the environment variables

In **Project → Settings → Environment Variables** (Production), add:

| Name | Value | Notes |
| --- | --- | --- |
| `DJANGO_SECRET_KEY` | a long random string | Generate: `python -c "import secrets; print(secrets.token_urlsafe(50))"` |
| `MFA_ENCRYPTION_KEY` | a Fernet key | Encrypts the authenticator secrets. Generate: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`. Keep it in the hosting settings and in a password manager; losing it locks MFA users out. |
| `DJANGO_DEBUG` | `False` | Never `True` in production. |
| `DJANGO_ALLOWED_HOSTS` | `your-project.vercel.app` | Add your custom domain too, comma separated. |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | `https://your-project.vercel.app` | Same host, with `https://`. |
| `DATABASE_URL_READWRITE` | `postgresql://USER:PASSWORD@HOST:5432/conceito_os?sslmode=require` | Mark as **Sensitive**. Percent-encode special characters in the password. |
| `DATABASE_URL_READONLY` | `postgresql://READONLY_USER:PASSWORD@HOST:5432/conceito_os?sslmode=require` | Optional. Mark as **Sensitive**. |
| `DB_CONN_MAX_AGE` | `0` | Keep at 0 on serverless. |
| `DB_CONNECT_TIMEOUT` | `5` | Seconds. |
| `DB_STATEMENT_TIMEOUT_MS` | `15000` | A query longer than this is stopped by the server. |
| `DB_PRIMARY_STICKY_SECONDS` | `5` | After a change, the same person reads from the primary for this long (PROPOSAL). |

Then trigger a new deployment (Deployments → Redeploy) so the variables apply.

## 5. Run the migrations (once, and after each schema change)

From your machine, with a virtual environment and the **production** variables
set in your shell (never commit them):

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
$env:DJANGO_SECRET_KEY = "<same key as Vercel>"
$env:MFA_ENCRYPTION_KEY = "<same key as Vercel>"
$env:DJANGO_DEBUG = "False"
$env:DATABASE_URL_READWRITE = "<read/write connection string>"
python manage.py migrate   # migrations run on the primary only
```

```bash
# macOS / Linux / Git Bash
source .venv/bin/activate
export DJANGO_SECRET_KEY="<same key as Vercel>" MFA_ENCRYPTION_KEY="<same key as Vercel>" DJANGO_DEBUG=False
export DATABASE_URL_READWRITE="<read/write connection string>"
python manage.py migrate   # migrations run on the primary only
```

Check the migration list with `python manage.py showmigrations`.

The sign-in attempt counters are stored in a table that `migrate` creates, so no extra
step is needed.

## 6. Create the first administrator

The administrator is created with a command, the same one used locally. It reads
`INITIAL_ADMIN_*` from the environment, so the password is never stored in the code.

1. Choose a strong password for the production administrator. Do not reuse the
   local development password.
2. Run once, from your machine, with the **production** database and SMTP settings
   in your shell (see step 5 for the pattern):

   ```powershell
   $env:INITIAL_ADMIN_EMAIL = "admin@conceito.com.br"
   $env:INITIAL_ADMIN_PASSWORD = "<the new strong password>"
   python manage.py create_initial_admin
   Remove-Item Env:INITIAL_ADMIN_PASSWORD
   ```

3. Sign in at `https://your-project.vercel.app/accounts/login/` with the email address.
4. Use `https://your-project.vercel.app/admin/` to add the organizations, teams
   and clients that are not yet in the app.

The command is safe to run again. Use `--reset-password` only to change the password.

## 6b. Configure the email provider (SMTP)

The welcome and password reset emails need an SMTP account from your email
provider (a transactional email service, or the company's mail server). Set these
variables in Vercel, the same way as step 4:

| Name | Example |
| --- | --- |
| `EMAIL_HOST` | the provider's SMTP host |
| `EMAIL_PORT` | `587` (STARTTLS, with `EMAIL_USE_TLS=True`) or `465` (with `EMAIL_USE_SSL=True`) |
| `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` | the SMTP credentials (mark the password as sensitive) |
| `DEFAULT_FROM_EMAIL` | `Conceito OS <no-reply@conceito.com.br>` (the domain must be verified with the provider) |
| `SITE_URL` | `https://your-project.vercel.app` (or your custom domain) |

Test it after deploying: request a password reset for the admin address and check
the inbox. Emails that fail to send are written to the Vercel function logs; they do
not stop an account from being created.
## 7. Check the deployment

- `https://your-project.vercel.app/accounts/login/` loads.
- Logging in as the owner shows the dashboard.
- `python manage.py check --deploy` (run with the production variables) only
  reports the optional HSTS preload and subdomain recommendations.

## 8. Troubleshooting

| Symptom | Likely cause |
| --- | --- |
| `SECRET_KEY must not be empty` | `DJANGO_SECRET_KEY` is missing in Vercel. |
| `MFA_ENCRYPTION_KEY is not set` | `MFA_ENCRYPTION_KEY` is missing in Vercel; add it, then redeploy. |
| `DisallowedHost` | Add the domain to `DJANGO_ALLOWED_HOSTS`. |
| CSRF error on forms | Add `https://<domain>` to `DJANGO_CSRF_TRUSTED_ORIGINS`. |
| `OperationalError: could not connect to server` | Host, port, TLS (`sslmode`) or firewall; the database must accept Vercel's connections. |
| Static files return 404 | Check that the `web/static/` folder is in the deployment. WhiteNoise serves it from the app folders. |
| `Table ... doesn't exist` | Migrations not run against this database (step 5). |
