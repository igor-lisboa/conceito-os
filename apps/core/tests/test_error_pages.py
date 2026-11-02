"""Error pages are translated like the rest of the interface (TD-S1, NFR-002)."""

from django.template.loader import render_to_string
from django.test import TestCase
from django.urls import reverse
from django.utils import translation


class NotFoundPageTests(TestCase):
    def test_unknown_page_shows_the_branded_404_in_english(self):
        response = self.client.get("/this-page-does-not-exist/")

        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "404.html")
        self.assertContains(response, "Page not found", status_code=404)
        self.assertContains(response, 'lang="en"', status_code=404)

    def test_unknown_page_shows_the_branded_404_in_portuguese(self):
        self.client.post(reverse("set_language"), {"language": "pt-br", "next": reverse("login")})

        response = self.client.get("/this-page-does-not-exist/")

        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "Página não encontrada", status_code=404)
        self.assertContains(response, "Voltar ao início", status_code=404)
        self.assertNotContains(response, "Page not found", status_code=404)


class ForbiddenPageTests(TestCase):
    def test_403_template_is_translated(self):
        with translation.override("pt-br"):
            html = render_to_string("403.html")

        self.assertIn("Acesso negado", html)
        self.assertNotIn("Access denied", html)

    def test_403_template_is_translated_in_english(self):
        with translation.override("en"):
            html = render_to_string("403.html")

        self.assertIn("Access denied", html)


class ServerErrorPageTests(TestCase):
    def test_500_template_renders_without_request_context(self):
        # A server error can happen before any request context exists.
        with translation.override("pt-br"):
            html = render_to_string("500.html")

        self.assertIn("Algo deu errado", html)
        self.assertIn('lang="pt-br"', html)
        self.assertIn('href="/static/', html)
