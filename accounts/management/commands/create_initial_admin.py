"""Create the first administrator, or update an existing one. Safe to run again.

The password is never written in the code. It comes from the environment (or the
--password option), so it stays in your local .env file or in the hosting settings.

    python manage.py create_initial_admin

What it does:
- creates the user if the email is new, as a superuser that can open /admin/;
- if the user exists, makes sure the superuser flags are on (the password is only
  changed with --reset-password);
- creates the organization (default "Conceito Co") and makes the user its owner.
"""

import os

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from accounts.models import Membership, Organization
from accounts.roles import Role

User = get_user_model()


class Command(BaseCommand):
    help = "Create or update the first administrator (reads INITIAL_ADMIN_* variables)."

    def add_arguments(self, parser):
        parser.add_argument("--email", default=os.environ.get("INITIAL_ADMIN_EMAIL"))
        parser.add_argument("--password", default=os.environ.get("INITIAL_ADMIN_PASSWORD"))
        parser.add_argument("--name", default=os.environ.get("INITIAL_ADMIN_NAME", "Administrator"))
        parser.add_argument("--organization", default=os.environ.get("INITIAL_ADMIN_ORGANIZATION", "Conceito Co"))
        parser.add_argument(
            "--reset-password",
            action="store_true",
            help="Also set the password again if the user already exists.",
        )

    def handle(self, *args, **options):
        email = (options["email"] or "").strip().lower()
        password = options["password"] or ""
        if not email or not password:
            raise CommandError(
                "Set INITIAL_ADMIN_EMAIL and INITIAL_ADMIN_PASSWORD (in .env) or pass --email and --password."
            )

        with transaction.atomic():
            user = User.objects.filter(email__iexact=email).first()
            if user is None:
                self._validate(password)
                user = User.objects.create_superuser(
                    username=email,
                    email=email,
                    password=password,
                    first_name=options["name"],
                )
                self.stdout.write(self.style.SUCCESS(f"Created administrator {email}."))
            else:
                user.is_active = True
                user.is_staff = True
                user.is_superuser = True
                if options["reset_password"]:
                    self._validate(password)
                    user.set_password(password)
                    self.stdout.write("Password updated.")
                user.save()
                self.stdout.write(f"Administrator {email} already exists; flags updated.")

            organization, _ = Organization.objects.get_or_create(name=options["organization"])
            Membership.objects.get_or_create(
                user=user,
                organization=organization,
                defaults={"role": Role.OWNER.value},
            )
        self.stdout.write(f"Owner of organization '{organization.name}'.")

    def _validate(self, password):
        try:
            validate_password(password)
        except ValidationError as error:
            raise CommandError("Password rejected: " + " ".join(error.messages)) from error
