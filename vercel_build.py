"""Build step for Vercel: run the database migrations before a production deploy.

Vercel runs this command after it installs the dependencies and before it publishes the
app (vercel.json, buildCommand). Rules:

- Only production builds migrate (VERCEL_ENV=production). Preview builds never touch
  the production database.
- Set RUN_MIGRATIONS=0 in the Vercel project to skip migrations for a production build.
- If a migration fails, this script exits non-zero, the build fails, and the new version is
  not published. The previous version keeps serving requests.
- Migrations must be backward compatible with the version that is still running while
  the build happens (add columns first, remove them in a later release).
"""

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def should_migrate(environ):
    if environ.get("VERCEL_ENV") != "production":
        return False
    return environ.get("RUN_MIGRATIONS", "1").strip() != "0"


def main(environ=os.environ):
    if not should_migrate(environ):
        print("vercel_build: migrations skipped (not a production build, or RUN_MIGRATIONS=0).")
        return 0
    print("vercel_build: running migrations on the production database...")
    result = subprocess.run([sys.executable, "manage.py", "migrate", "--noinput"], cwd=ROOT)
    if result.returncode != 0:
        print("vercel_build: migrations FAILED. The deployment is stopped; the previous version keeps running.")
    else:
        print("vercel_build: migrations finished.")
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
