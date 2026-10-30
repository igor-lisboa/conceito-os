"""Sign-in by email, password recovery, welcome email and the first administrator."""

import re
from unittest import mock

from django.core import mail
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

from accounts.models import Membership, Organization, User
from accounts.roles import Role


class EmailSignInTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("ana", email="ana@conceito.com.br", password="Senha-Forte-2026!")

    def test_signs_in_with_the_email_address(self):
        self.assertTrue(self.client.login(username="ana@conceito.com.br", password="Senha-Forte-2026!"))

    def test_email_is_case_insensitive(self):
        self.assertTrue(self.client.login(username="ANA@Conceito.com.br", password="Senha-Forte-2026!"))

    def test_username_still_works(self):
        self.assertTrue(self.client.login(username="ana", password="Senha-Forte-2026!"))

    def test_wrong_password_is_refused(self):
        self.assertFalse(self.client.login(username="ana@conceito.com.br", password="errada"))

    def test_login_page_asks_for_email(self):
        response = self.client.get(reverse("login"))
        self.assertContains(response, 'name="username"')
        self.assertContains(response, "Email")

    def test_two_accounts_cannot_share_an_email(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            User.objects.create_user("outra", email="ANA@conceito.com.br", password="x")


class PasswordRecoveryTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("bia", email="bia@conceito.com.br", password="Antiga-Senha-2026!")

    def reset_link_from_outbox(self):
        body = mail.outbox[0].body
        match = re.search(r"(/accounts/password/reset/[^/\s]+/[^/\s]+/)", body)
        self.assertIsNotNone(match, "the email must contain the reset link")
        return match.group(1)

    def test_request_sends_one_email_with_a_link(self):
        response = self.client.post(reverse("password_reset"), {"email": "bia@conceito.com.br"})

        self.assertRedirects(response, reverse("password_reset_done"))
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["bia@conceito.com.br"])
        self.reset_link_from_outbox()

    def test_unknown_email_gets_the_same_answer_and_no_email(self):
        # Same redirect for unknown emails, so the form cannot be used to discover accounts.
        response = self.client.post(reverse("password_reset"), {"email": "ninguem@conceito.com.br"})

        self.assertRedirects(response, reverse("password_reset_done"))
        self.assertEqual(mail.outbox, [])

    def test_the_link_sets_a_new_password_that_then_works(self):
        self.client.post(reverse("password_reset"), {"email": "bia@conceito.com.br"})
        link = self.reset_link_from_outbox()

        landing = self.client.get(link, follow=True)
        final_url = landing.redirect_chain[-1][0]
        self.client.post(
            final_url,
            {"new_password1": "Nova-Senha-2026!", "new_password2": "Nova-Senha-2026!"},
        )

        self.assertFalse(self.client.login(username="bia@conceito.com.br", password="Antiga-Senha-2026!"))
        self.assertTrue(self.client.login(username="bia@conceito.com.br", password="Nova-Senha-2026!"))

    def test_a_used_link_cannot_be_used_again(self):
        self.client.post(reverse("password_reset"), {"email": "bia@conceito.com.br"})
        link = self.reset_link_from_outbox()
        final_url = self.client.get(link, follow=True).redirect_chain[-1][0]
        self.client.post(final_url, {"new_password1": "Nova-Senha-2026!", "new_password2": "Nova-Senha-2026!"})

        response = self.client.get(link)

        self.assertContains(response, "invalid or has already been used")


class WelcomeEmailTests(TestCase):
    def test_new_user_with_email_receives_a_welcome_after_commit(self):
        with self.captureOnCommitCallbacks(execute=True):
            User.objects.create_user("carla", email="carla@conceito.com.br", password="x")

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Bem-vindo ao Conceito OS")
        self.assertIn("/accounts/login/", mail.outbox[0].body)

    def test_welcome_is_not_sent_when_the_transaction_rolls_back(self):
        with self.captureOnCommitCallbacks(execute=True):
            with self.assertRaises(RuntimeError), transaction.atomic():
                User.objects.create_user("dani", email="dani@conceito.com.br", password="x")
                raise RuntimeError("something failed after the insert")

        self.assertEqual(mail.outbox, [])

    def test_updating_an_existing_user_sends_nothing(self):
        user = User.objects.create_user("eva", email="eva@conceito.com.br", password="x")
        mail.outbox.clear()
        with self.captureOnCommitCallbacks(execute=True):
            user.first_name = "Eva"
            user.save()

        self.assertEqual(mail.outbox, [])

    def test_a_failing_mail_server_does_not_break_creating_the_account(self):
        with mock.patch("accounts.emails.send_mail", side_effect=OSError("smtp down")):
            with self.assertLogs("accounts.emails", level="ERROR") as logs:
                with self.captureOnCommitCallbacks(execute=True):
                    user = User.objects.create_user("fabi", email="fabi@conceito.com.br", password="x")

        self.assertTrue(User.objects.filter(pk=user.pk).exists())
        self.assertIn("Could not send the welcome email", logs.output[0])


class CreateInitialAdminTests(TestCase):
    EMAIL = "admin@conceito.com.br"
    PASSWORD = "Conceito@2026"

    def run_command(self, **options):
        call_command(
            "create_initial_admin",
            email=options.pop("email", self.EMAIL),
            password=options.pop("password", self.PASSWORD),
            stdout=_Silent(),
            **options,
        )

    def test_creates_a_superuser_who_owns_the_default_organization(self):
        self.run_command()

        admin = User.objects.get(email=self.EMAIL)
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.check_password(self.PASSWORD))
        membership = Membership.objects.get(user=admin)
        self.assertEqual(membership.role, Role.OWNER.value)
        self.assertEqual(membership.organization.name, "Conceito Co")

    def test_running_it_twice_changes_nothing_extra(self):
        self.run_command()
        self.run_command()

        self.assertEqual(User.objects.filter(email=self.EMAIL).count(), 1)
        self.assertEqual(Membership.objects.filter(user__email=self.EMAIL).count(), 1)
        self.assertEqual(Organization.objects.filter(name="Conceito Co").count(), 1)

    def test_the_password_is_not_changed_without_the_reset_flag(self):
        self.run_command()
        self.run_command(password="Outra-Senha-2026!")

        self.assertTrue(User.objects.get(email=self.EMAIL).check_password(self.PASSWORD))

    def test_reset_flag_updates_the_password(self):
        self.run_command()
        self.run_command(password="Outra-Senha-2026!", reset_password=True)

        self.assertTrue(User.objects.get(email=self.EMAIL).check_password("Outra-Senha-2026!"))

    def test_weak_password_is_rejected_for_a_new_admin(self):
        with self.assertRaises(CommandError):
            self.run_command(password="123")
        self.assertFalse(User.objects.filter(email=self.EMAIL).exists())

    def test_missing_settings_stop_with_a_clear_message(self):
        with self.assertRaises(CommandError):
            self.run_command(email="", password="")


class _Silent:
    """Stand-in for stdout so the command output does not clutter the test log."""

    def write(self, text):
        return None
