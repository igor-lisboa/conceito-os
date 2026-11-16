"""Text colours meet WCAG AA contrast (4.5:1) in both themes (DSG-002, NFR-010, D-23).

The colours are read from web/static/css/app.css, so the test follows the stylesheet.
"""

import re
from pathlib import Path

from django.test import SimpleTestCase

CSS = Path(__file__).resolve().parents[3] / "web" / "static" / "css" / "app.css"

# Text that sits on each surface (what the stylesheet puts there).
TEXT_PAIRS = [
    ("text", "background"),
    ("text", "surface"),
    ("text", "primary"),  # top bar and buttons
    ("text", "accent"),
    ("text", "neutral"),  # secondary buttons
    ("link", "background"),
    ("link", "surface"),
    ("danger", "background"),
    ("danger", "surface"),
    ("muted", "background"),
    ("muted", "surface"),
    ("muted", "soft"),
    ("link", "soft"),
    ("on-strong", "strong"),
]


def _channel(value):
    value = value / 255
    return value / 12.92 if value <= 0.03928 else ((value + 0.055) / 1.055) ** 2.4


def luminance(hex_colour):
    hex_colour = hex_colour.lstrip("#")
    r, g, b = (int(hex_colour[i:i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * _channel(r) + 0.7152 * _channel(g) + 0.0722 * _channel(b)


def contrast(a, b):
    high, low = sorted((luminance(a), luminance(b)), reverse=True)
    return (high + 0.05) / (low + 0.05)


def tokens(block):
    return dict(re.findall(r"--color-([a-z-]+):\s*(#[0-9a-fA-F]{6});", block))


def block_after(css, selector):
    start = css.index(selector)
    return css[start:css.index("}", start)]


class ThemeContrastTests(SimpleTestCase):
    def setUp(self):
        self.css = CSS.read_text(encoding="utf-8")

    def check(self, palette, theme):
        failures = []
        for text, surface in TEXT_PAIRS:
            ratio = contrast(palette[text], palette[surface])
            if ratio < 4.5:
                failures.append(f"{theme}: {text} on {surface} is {ratio:.2f}:1")
        self.assertEqual(failures, [])

    def test_light_theme_meets_aa(self):
        self.check(tokens(block_after(self.css, ":root {")), "light")

    def test_dark_theme_meets_aa(self):
        self.check(tokens(block_after(self.css, ':root[data-theme="dark"]')), "dark")

    def test_input_borders_have_non_text_contrast_in_both_themes(self):
        for selector in (":root {", ':root[data-theme="dark"]'):
            palette = tokens(block_after(self.css, selector))
            for surface in ("surface", "background"):
                self.assertGreaterEqual(contrast(palette["input-border"], palette[surface]), 3)

    def test_the_dark_theme_is_used_when_the_system_asks_for_it(self):
        self.assertIn('@media (prefers-color-scheme: dark)', self.css)
        self.assertIn(':root:not([data-theme="light"])', self.css)

    def test_the_stylesheet_has_no_hard_coded_white_surfaces(self):
        self.assertNotIn("#fff;", self.css)
