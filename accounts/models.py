from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from core.choices import translated_choices

from .roles import Role


class User(AbstractUser):
    """The login account. A person can belong to several organizations (see Membership).

    Email is required and unique: people sign in with it and reset their password through it.
    """

    email = models.EmailField("email address", unique=True)

    REQUIRED_FIELDS = ["email"]

    def save(self, *args, **kwargs):
        # Store emails in lowercase. Uniqueness then means the same thing on every
        # database: MySQL ignores case in unique checks by default, SQLite does not.
        if self.email:
            self.email = self.email.lower()
        super().save(*args, **kwargs)


class Organization(models.Model):
    """A company using the platform (an agency). All business data belongs to one organization."""

    name = models.CharField(max_length=120)
    timezone = models.CharField(max_length=60, default="America/Sao_Paulo")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Membership(models.Model):
    """Links a user to an organization with one role inside it."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="memberships")
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="memberships")
    role = models.CharField(max_length=20, choices=translated_choices(Role))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(fields=["user", "organization"], name="unique_membership_per_org"),
        ]

    def __str__(self):
        return f"{self.user} @ {self.organization} ({Role(self.role).label})"
