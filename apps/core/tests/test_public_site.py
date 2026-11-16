"""Public introduction and email inquiry (NAV-015, NAV-016, SCR-030)."""

from urllib.parse import parse_qs, urlsplit

from django.core import mail
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from apps.accounts.models import User
from apps.accounts.roles import Role
from apps.core.testing import make_membership, make_organization, make_owner


class PublicSiteTests(TestCase):
    def test_visitors_get_a_landing_page_with_two_entry_paths(self):
        response = self.client.get("/")
        self.assertContains(response, 'id="get-started"')
        self.assertContains(response, 'href="' + reverse("login") + '"')
        self.assertContains(response, 'href="' + reverse("contact") + '"')
        self.assertContains(response, "Illustrative example")
        self.assertNotContains(response, 'class="sidebar"')

    def test_dashboard_still_requires_sign_in(self):
        response = self.client.get(reverse("home"))
        self.assertRedirects(response, reverse("login") + "?next=" + reverse("home"))

    def test_portuguese_landing_is_translated(self):
        response = self.client.get("/", HTTP_ACCEPT_LANGUAGE="pt-BR")
        self.assertContains(response, "Menos ruído.")
        self.assertContains(response, "Mais espaço para criar.")
        self.assertContains(response, "Quero ser cliente")
        self.assertNotContains(response, "More room to create.")

    def test_public_page_stays_public_for_members(self):
        owner = make_owner(make_organization())
        self.client.force_login(owner.user)
        response = self.client.get(reverse("landing"))
        self.assertContains(response, "Open workspace")
        self.assertNotContains(response, 'class="sidebar"')


class InquiryTests(TestCase):
    def setUp(self):
        self.data = {
            "name": "João & Ana", "email": "joao@example.com", "company": "Criação & Cia",
            "interest": "content", "message": "Conteúdo com café?\nSim, #ideias & planejamento.",
        }

    @override_settings(CONTACT_EMAIL="commercial@example.com")
    def test_valid_answers_prepare_a_draft_for_the_configured_recipient(self):
        users_before = User.objects.count()
        response = self.client.post(reverse("contact"), self.data)
        self.assertEqual(response.status_code, 200)
        parsed = urlsplit(response.context["mailto"])
        self.assertEqual(parsed.scheme, "mailto")
        self.assertEqual(parsed.path, "commercial@example.com")
        query = parse_qs(parsed.query)
        self.assertEqual(set(query), {"subject", "body"})
        self.assertIn(self.data["company"], query["subject"][0])
        for field in ("name", "email", "company", "message"):
            self.assertIn(self.data[field], query["body"][0])
        self.assertIn("Content planning and production", query["body"][0])
        self.assertEqual(User.objects.count(), users_before)
        self.assertEqual(len(mail.outbox), 0)
        self.assertContains(response, "No email has been sent yet.")

    def test_invalid_answers_keep_the_values_and_show_errors(self):
        response = self.client.post(reverse("contact"), {**self.data, "email": "invalid", "message": ""})
        self.assertFormError(response.context["form"], "email", "Enter a valid email address.")
        self.assertFormError(response.context["form"], "message", "This field is required.")
        self.assertNotIn("mailto", response.context)
        self.assertEqual(response.context["form"]["company"].value(), self.data["company"])

    def test_invalid_interest_and_oversized_message_are_rejected(self):
        response = self.client.post(reverse("contact"), {
            **self.data, "interest": "injected", "message": "x" * 2001,
        })
        self.assertIn("interest", response.context["form"].errors)
        self.assertIn("message", response.context["form"].errors)
        self.assertNotIn("mailto", response.context)

    def test_user_text_cannot_inject_email_query_parameters_or_html(self):
        self.data["company"] = "<script>alert(1)</script>&bcc=other@example.com"
        response = self.client.post(reverse("contact"), self.data)
        self.assertEqual(set(parse_qs(urlsplit(response.context["mailto"]).query)), {"subject", "body"})
        self.assertNotContains(response, "<script>alert(1)</script>")
        self.assertContains(response, "&lt;script&gt;")

    def test_portuguese_email_uses_translated_labels_and_interest(self):
        response = self.client.post(reverse("contact"), self.data, HTTP_ACCEPT_LANGUAGE="pt-BR")
        query = parse_qs(urlsplit(response.context["mailto"]).query)
        self.assertIn("Seu nome: João & Ana", query["body"][0])
        self.assertIn("Planejamento e produção de conteúdo", query["body"][0])
        self.assertContains(response, "Sua apresentação está pronta.")

    def test_public_form_requires_csrf(self):
        response = Client(enforce_csrf_checks=True).post(reverse("contact"), self.data)
        self.assertEqual(response.status_code, 403)


class NavigationTests(TestCase):
    def setUp(self):
        self.organization = make_organization()
        self.owner = make_owner(self.organization)

    def test_report_has_one_current_desktop_entry_and_a_post_logout(self):
        self.client.force_login(self.owner.user)
        response = self.client.get(reverse("report"))
        self.assertContains(response, 'aria-current="page"', count=1)
        self.assertContains(response, 'method="post" action="' + reverse("logout") + '"')
        self.assertContains(response, 'class="bottom-nav"')
        self.assertContains(response, 'id="theme-toggle"')

    def test_calendar_has_no_duplicate_current_content_entry(self):
        self.client.force_login(self.owner.user)
        response = self.client.get(reverse("content_calendar"))
        active = [i for g in response.context["navigation_groups"] for i in g["items"] if i["active"]]
        self.assertEqual([i["url"] for i in active], [reverse("content_calendar")])

    def test_client_menu_keeps_internal_tools_hidden_and_portal_redirect(self):
        member = make_membership(self.organization, Role.CLIENT)
        self.client.force_login(member.user)
        self.assertRedirects(self.client.get(reverse("home")), reverse("portal_list"))
        response = self.client.get(reverse("portal_calendar"))
        self.assertContains(response, "Client space")
        for route in ("team_list", "audit_log", "lead_board", "client_list", "report"):
            self.assertNotContains(response, 'href="' + reverse(route) + '"')
        active = [i for g in response.context["navigation_groups"] for i in g["items"] if i["active"]]
        self.assertEqual([i["url"] for i in active], [reverse("portal_calendar")])

    def test_crm_menu_respects_the_per_person_grant(self):
        manager = make_membership(self.organization, Role.ACCOUNT_MANAGER)
        self.client.force_login(manager.user)
        response = self.client.get(reverse("home"))
        self.assertNotContains(response, 'href="' + reverse("lead_board") + '"')
        self.assertNotContains(response, 'href="' + reverse("team_list") + '"')
        manager.crm_access = True
        manager.save(update_fields=["crm_access"])
        response = self.client.get(reverse("home"))
        self.assertContains(response, 'href="' + reverse("lead_board") + '"')

    def test_sign_in_still_lands_in_dashboard_and_logout_ends_session(self):
        response = self.client.post(reverse("login"), {
            "username": self.owner.user.email, "password": "senha-de-teste-123",
        })
        self.assertRedirects(response, reverse("home"))
        self.assertEqual(self.client.get(reverse("logout")).status_code, 405)
        self.assertRedirects(self.client.post(reverse("logout")), reverse("login"))
        self.assertRedirects(self.client.get(reverse("home")), reverse("login") + "?next=" + reverse("home"))
