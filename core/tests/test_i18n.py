"""Language selection (English / Brazilian Portuguese)."""

from pathlib import Path

import polib
from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from django.utils import translation

from core.exceptions import DomainError
from core.http import translated_message
from production.domain.states import ContentState, ensure_transition

PO_FILE = Path(settings.LOCALE_PATHS[0]) / "pt_BR" / "LC_MESSAGES" / "django.po"
MO_FILE = PO_FILE.with_suffix(".mo")


class TranslationCatalogTests(TestCase):
    def test_every_entry_in_the_portuguese_catalog_is_translated(self):
        catalog = polib.pofile(str(PO_FILE))
        self.assertEqual([entry.msgid for entry in catalog.untranslated_entries()], [])

    def test_compiled_catalog_exists_and_matches_the_source(self):
        # A stale .mo would silently show old text. Recompile with scripts/compile_translations.py.
        self.assertTrue(MO_FILE.exists())
        self.assertGreaterEqual(MO_FILE.stat().st_mtime, PO_FILE.stat().st_mtime)


class LanguageSelectionTests(TestCase):
    def test_default_language_is_english(self):
        response = self.client.get(reverse("login"))
        self.assertContains(response, "Sign in")
        self.assertContains(response, 'lang="en"')

    def test_the_page_offers_both_languages(self):
        response = self.client.get(reverse("login"))
        self.assertContains(response, 'value="en"')
        self.assertContains(response, 'value="pt-br"')

    def test_choosing_portuguese_changes_the_interface(self):
        self.client.post(reverse("set_language"), {"language": "pt-br", "next": reverse("login")})

        response = self.client.get(reverse("login"))

        self.assertContains(response, "Entrar")
        self.assertContains(response, 'lang="pt-br"')
        self.assertNotContains(response, ">Sign in<")

    def test_choosing_english_again_switches_back(self):
        self.client.post(reverse("set_language"), {"language": "pt-br", "next": reverse("login")})
        self.client.post(reverse("set_language"), {"language": "en", "next": reverse("login")})

        response = self.client.get(reverse("login"))

        self.assertContains(response, "Sign in")

    def test_language_switch_only_redirects_to_safe_paths(self):
        response = self.client.post(
            reverse("set_language"), {"language": "pt-br", "next": "https://evil.example.com/"}
        )
        self.assertNotEqual(response.headers.get("Location"), "https://evil.example.com/")


class DomainMessageTranslationTests(TestCase):
    def test_business_rule_message_is_translated_with_its_labels(self):
        with self.assertRaises(DomainError) as context:
            ensure_transition(ContentState.PUBLISHED, ContentState.DRAFT)

        with translation.override("pt-br"):
            text = translated_message(context.exception)

        self.assertEqual(text, "Não é possível mudar de 'Publicado' para 'Rascunho'.")

    def test_the_same_message_stays_english_in_english(self):
        with self.assertRaises(DomainError) as context:
            ensure_transition(ContentState.PUBLISHED, ContentState.DRAFT)

        with translation.override("en"):
            text = translated_message(context.exception)

        self.assertEqual(text, "Cannot change from 'Published' to 'Draft'.")
