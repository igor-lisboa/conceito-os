"""The internal contracts in docs/api-contracts.md match the code (TD-49).

Covers the content state transitions and the notification kinds. The audit actions
are listed by hand and are not checked here.
"""

import re
from pathlib import Path

from django.test import SimpleTestCase

from apps.notifications.models import KIND_MESSAGES
from apps.production.domain.states import ALLOWED_TRANSITIONS

DOC = Path(__file__).resolve().parents[3] / "docs" / "api-contracts.md"


def section(text, title):
    """The text under a level-2 heading, up to the next one."""
    parts = re.split(r"^## ", text, flags=re.MULTILINE)
    for part in parts:
        if part.startswith(title + "\n"):
            return part
    raise AssertionError(f"Section not found in docs/api-contracts.md: {title}")


class InternalContractsTests(SimpleTestCase):
    def setUp(self):
        self.text = DOC.read_text(encoding="utf-8")

    def test_content_transitions_match_the_code(self):
        rows = re.findall(r"^\| `([a-z_]+)` \| `([a-z_]+)` \|$", section(self.text, "Content states"), re.MULTILINE)
        documented = {(source, target) for source, target in rows}

        in_code = {
            (source.value, target.value) for source, targets in ALLOWED_TRANSITIONS.items() for target in targets
        }

        self.assertEqual(documented, in_code)

    def test_notification_kinds_match_the_code(self):
        rows = re.findall(r"^\| `([a-z_]+)` \|", section(self.text, "Notification kinds"), re.MULTILINE)

        self.assertEqual(sorted(rows), sorted(KIND_MESSAGES))
