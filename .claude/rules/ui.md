---
paths:
  - "**/*.tsx"
  - "**/*.css"
  - "**/components/**"
---

# UI (when writing interface code)

Sources: `specs/ux/design-system.md`, `specs/ux/navigation-responsive.md`, `specs/ux/screens.md`, `specs/technical/non-functional.md`.

- Use centralized tokens; no loose colors or sizes. Target WCAG 2.2 AA. Lilac `#C9B8E9`, nude pink and gray are fills only: never text, icon, link, focus-ring or sole border color on the light background.
- Every screen: empty, loading, recoverable-error and forbidden states.
- Desktop (≥1024 px) primary and mobile (360–430 px) with its own layout: tables → cards, Kanban → list by stage, calendar → agenda, editor in steps, bottom bar. No tablet-specific layout.
- Keyboard, visible focus, adequate touch targets; no unnecessary horizontal scrolling.
- Filters in the URL; back preserves the client context; breadcrumbs on desktop.
- Hiding unauthorized modules is a convenience; the server blocks them.
- User-visible text is always translatable: `{% trans %}` in templates, `gettext` / `gettext_lazy` in Python. Never hard-code Portuguese or English in a template. Add the pt-BR entry to `locale/pt_BR/LC_MESSAGES/django.po` and run `python scripts/compile_translations.py`.
- Domain code (`production/domain/`) raises `DomainError` with an English message and parameters; it never imports `gettext`.
