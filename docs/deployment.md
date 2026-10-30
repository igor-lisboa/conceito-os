# Deployment (Vercel + MySQL)

The app runs on Vercel as a Python serverless function. Vercel routes every
request to `api/index.py`, which exposes the Django WSGI app. Static files are
served by WhiteNoise from the app folders, so no separate build step is needed.

The database is a **MySQL server that you provide**. Vercel cannot host it, and
the function must be able to reach it over the network (use a managed MySQL
service).

## 1. Things to know before you start

- **Migrations are not run by Vercel.** Run them once from your machine against
  the production database, then deploy. Running them on every request would be
  wrong, and the build step has no database access.
- **No file uploads yet.** Vercel's filesystem is read-only except `/tmp`, and it
  is erased between requests. Media is stored as URLs until a storage decision
  is made (see `specs/planning/risks-open-decisions.md`).
- **Serverless database connections.** Each cold start opens new connections.
  Keep `DJANGO_CONN_MAX_AGE=0` and use a MySQL service with a connection proxy
  or a generous connection limit.
- **`/tmp` is the only writable path.** Nothing in the app writes files, so this
  is fine today.

## 2. Prepare the database

1. Create a MySQL 8 database named `conceito_os` with charset `utf8mb4`.
2. Create a user that can access that database only.
3. Allow connections from your machine (for the first migration) and from Vercel.
   Managed providers document the IP ranges or a secure connection option.

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
| `DJANGO_DEBUG` | `False` | Never `True` in production. |
| `DJANGO_ALLOWED_HOSTS` | `your-project.vercel.app` | Add your custom domain too, comma separated. |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | `https://your-project.vercel.app` | Same host, with `https://`. |
| `MYSQL_DATABASE` | `conceito_os` | |
| `MYSQL_USER` | the database user | |
| `MYSQL_PASSWORD` | the database password | Mark as **Sensitive**. |
| `MYSQL_HOST` | the MySQL host | Not `127.0.0.1`. |
| `MYSQL_PORT` | `3306` | |
| `DJANGO_CONN_MAX_AGE` | `0` | Keep at 0 on serverless. |

Then trigger a new deployment (Deployments → Redeploy) so the variables apply.

## 5. Run the migrations (once, and after each schema change)

From your machine, with a virtual environment and the **production** variables
set in your shell (never commit them):

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
$env:DJANGO_SECRET_KEY = "<same key as Vercel>"
$env:DJANGO_DEBUG = "False"
$env:MYSQL_HOST = "<host>"
$env:MYSQL_USER = "<user>"
$env:MYSQL_PASSWORD = "<password>"
python manage.py migrate
```

```bash
# macOS / Linux / Git Bash
source .venv/bin/activate
export DJANGO_SECRET_KEY="<same key as Vercel>" DJANGO_DEBUG=False
export MYSQL_HOST="<host>" MYSQL_USER="<user>" MYSQL_PASSWORD="<password>"
python manage.py migrate
```

Check the migration list with `python manage.py showmigrations`.

## 6. Create the first owner

Use the Django admin, which is read only for content but full for organizations,
users, memberships and clients:

```powershell
python manage.py createsuperuser
```

Then open `https://your-project.vercel.app/admin/` and:

1. Create the **Organization** (agency).
2. Create the **User** (Beatriz), then add a **Membership** with role *Proprietária / admin*.
3. Create the clients and the memberships of the team. For account managers,
   creatives, freelancers and client users, add **Client access** rows on each
   client page so they can see the right brands.

## 7. Check the deployment

- `https://your-project.vercel.app/accounts/login/` loads.
- Logging in as the owner shows the dashboard.
- `python manage.py check --deploy` (run with the production variables) only
  reports the optional HSTS preload and subdomain recommendations.

## 8. Troubleshooting

| Symptom | Likely cause |
| --- | --- |
| `SECRET_KEY must not be empty` | `DJANGO_SECRET_KEY` is missing in Vercel. |
| `DisallowedHost` | Add the domain to `DJANGO_ALLOWED_HOSTS`. |
| CSRF error on forms | Add `https://<domain>` to `DJANGO_CSRF_TRUSTED_ORIGINS`. |
| `OperationalError: Can't connect to MySQL` | Host, port or firewall; the database must accept Vercel's connections. |
| Static files return 404 | Check that the `static/` folder is in the deployment. WhiteNoise serves it from the app folders. |
| `Table ... doesn't exist` | Migrations not run against this database (step 5). |
