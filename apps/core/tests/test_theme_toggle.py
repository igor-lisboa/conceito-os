"""Light and dark switch, skip link and readable form controls (DSG-002, DSG-004, WCAG 2.4.1)."""

from pathlib import Path

from django.test import SimpleTestCase, TestCase
from django.urls import reverse

CSS = Path(__file__).resolve().parents[3] / "web" / "static" / "css" / "app.css"


class ThemeToggleTests(TestCase):
    def test_the_switch_is_on_every_page_with_its_state(self):
        response = self.client.get(reverse("login"))
        self.assertContains(response, 'id="theme-toggle"')
        self.assertContains(response, 'aria-pressed="false"')

    def test_the_skip_link_points_to_the_content(self):
        response = self.client.get(reverse("login"))
        self.assertContains(response, 'class="skip-link" href="#conteudo"')


class StylesheetTests(SimpleTestCase):
    def setUp(self):
        self.css = CSS.read_text(encoding="utf-8")

    def test_the_skip_link_is_hidden_until_focused(self):
        self.assertIn(".skip-link {", self.css)
        self.assertIn("top: -60px", self.css)
        self.assertIn(".skip-link:focus", self.css)

    def test_form_controls_have_a_text_colour_of_their_own(self):
        block = self.css[self.css.index("input, select, textarea {"):]
        self.assertIn("color: var(--color-text)", block[:200])
