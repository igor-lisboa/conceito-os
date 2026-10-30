---
description: Create a new module spec from the template
argument-hint: "<module-name> <PREFIX> <phase>"
---

Create the module spec: $ARGUMENTS

1. Copy `specs/_templates/module.md` to `specs/modules/<name>.md` and fill the front matter (`id`, `phase`, `version: 0.1`, `updated` = today, `status: draft`).
2. Check that the prefix doesn't collide with an existing one (search for `PREFIX-` in `specs/`).
3. Ask the user for any content that can't be derived from existing specs; don't invent requirements.
4. Add the file to the index in `specs/README.md`, update screens/states/data model if applicable, and log it in `specs/CHANGELOG.md`.
