"""Compile the .po translation catalogs into .mo files Django can load.

Why this script exists: Django's `compilemessages` needs the GNU gettext tools,
which are not installed by default on Windows. This script uses `polib`, a pure
Python library, so it works everywhere.

Usage (from the project root, with requirements-dev.txt installed):

    python scripts/compile_translations.py
"""

import sys
from pathlib import Path

import polib

LOCALE_DIR = Path(__file__).resolve().parent.parent / "locale"


def compile_all():
    catalogs = sorted(LOCALE_DIR.glob("*/LC_MESSAGES/django.po"))
    if not catalogs:
        print("No .po files found in", LOCALE_DIR)
        return 1

    for po_path in catalogs:
        catalog = polib.pofile(str(po_path))
        missing = [entry.msgid for entry in catalog.untranslated_entries()]
        catalog.save_as_mofile(str(po_path.with_suffix(".mo")))
        print(f"{po_path.relative_to(LOCALE_DIR.parent)}: {len(catalog)} entries, {len(missing)} untranslated")
        for msgid in missing:
            print(f"  untranslated: {msgid!r}")
    return 0


if __name__ == "__main__":
    sys.exit(compile_all())
