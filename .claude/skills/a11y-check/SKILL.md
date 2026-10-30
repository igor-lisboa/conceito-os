---
name: a11y-check
description: Check the Conceito OS templates and styles for accessibility problems (WCAG 2.2 AA) that can be found in code: labels, names, alt text, table headers, focus, contrast tokens, language and landmarks. Use before a release, after changing templates, or for the accessibility task (TD-36).
---

# Accessibility check (code level)

This finds problems in the code. It does not replace a test with a screen reader or a keyboard-only walk-through, which a person must do. Say so in the report.

## Steps

1. **Page language and title.** Every template extends `web/templates/base.html`. Check it has `lang="{{ CURRENT_LANGUAGE }}"`, a `<title>` block, a skip link to `#conteudo`, and `<main id="conteudo">`.

2. **Form fields have labels.** Search the templates for `<input`, `<select`, `<textarea`. Each must have a `<label for=...>`, be wrapped in a label, or have `aria-label`. Django's `{{ form.as_p }}` renders labels, so check the custom HTML ones (search `grep -rn "<input\|<select\|<textarea" web/templates`).

3. **Buttons and links have a name.** Search for `<button` and `<a` with no text inside, and for icon-only buttons. Icon-only buttons need `aria-label` (see `task_list.html` for the pattern).

4. **Images.** Search for `<img`. Each needs `alt`. Decorative images use `alt=""`.

5. **Tables.** Each `<table>` needs a `<thead>` with `<th>`, and the list page should have an accessible name (`aria-label` or a caption) when it is the only heading.

6. **Status is not only colour.** The `.state-badge` and the N/D cells carry text. Check no state is shown only by colour (search for `class="...-error"` or `color` used alone).

7. **Focus and keyboard.** `app.css` must keep a `:focus-visible` outline. Check no `outline: none` without a replacement.

8. **Contrast of colour tokens.** Read `specs/ux/design-system.md` (table "Contrast check"). In `web/static/css/app.css`, text colours must be `--color-text` or `--color-link` on light backgrounds. The primary lilac (`--color-primary`) must not be used as text colour on the light background.

9. **Live messages.** The message list uses `role="status"`. Errors that need attention should be announced; check the forms that show errors inline.

10. **Target size on phones.** Buttons have `min-height: 44px` in `app.css`. Check new controls follow it.

## Report

A list of findings with file and line, grouped by WCAG principle (perceivable, operable, understandable, robust). Then the manual checks that remain: keyboard-only walk through of the main flows, a screen reader pass, and zoom to 200%. Do not mark TD-36 as done from this skill alone.
