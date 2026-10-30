---
name: i18n-sync
description: Keep the Portuguese (pt-BR) translations complete after any change to text the user sees. Use when templates, forms, messages or emails were added or changed, or when the user asks about translations.
---

# Translation sync

The interface is in English (default) and pt-BR. English is the source text (`msgid`). Portuguese lives in `web/locale/pt_BR/LC_MESSAGES/django.po`, compiled to `django.mo`.

## Rules that caused real bugs before

- The `msgid` must match the source text exactly, including punctuation and capital letters.
- Placeholders in `blocktrans` become `%(name)s` in the msgid.
- A template string written as `{% trans "1. Install ..." %}` must include the number in the msgid.
- Never edit `django.mo` by hand. Recompile.
- If the `.po` is saved and the `.mo` is not recompiled, the test `test_compiled_catalog_exists_and_matches_the_source` fails.

## Steps

1. Find text that has no entry. Run `./.venv/Scripts/python.exe scripts/add_translations.py`. It reports template strings without an entry and adds the ones listed in its table.

2. For each reported string, write the Portuguese translation. Add it to the table in `scripts/add_translations.py` (the `NEW_PHASE1_FINAL` block or a new block), keeping the English text as key. Then run the script again.

3. Python strings (`gettext("...")`, `gettext_lazy`, `DomainError("...")`) are not scanned. Search for them and add entries the same way:
   `grep -rn 'gettext' apps --include=*.py`

4. Compile: `./.venv/Scripts/python.exe scripts/compile_translations.py`. It must print "0 untranslated".

5. Run the i18n tests: `./.venv/Scripts/python.exe manage.py test apps.core.tests.test_i18n --settings=config.settings.test`

6. Quick visual check by language: start the server (`./.venv/Scripts/python.exe manage.py runserver 127.0.0.1:8080`), then open the page with the cookie `django_language=pt-br` (or use the language switch) and look for English leftovers.

## Report

Entries added, untranslated count after compiling, tests result. List any string you were unsure how to translate, so the product owner can review it.
