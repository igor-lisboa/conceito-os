---
description: Audit spec consistency (links, IDs, status, open decisions)
---

Audit `specs/` and report problems without fixing anything yet:

1. Broken relative links and files missing from the index in `specs/README.md`.
2. Missing/incomplete front matter; `updated` older than the latest CHANGELOG entry for that file.
3. Duplicated requirement IDs or suspicious gaps; prefixes that don't match the file.
4. Specs with `status: implemented*` and no filled "Evidence" section; `[x]` checkboxes without evidence.
5. States, entities or routes mentioned in modules but missing from `technical/states-events.md`, `technical/data-model.md` or `ux/screens.md`.
6. Contradictions between files (phase, permission, state name). Quote both passages for each.
7. `D-NN` references that don't exist in `planning/risks-open-decisions.md`, and decisions there that no spec references.
8. Text that is not in English (UI labels quoted in pt-BR are allowed).

Output: a list grouped by severity with `file:line` and proposed fixes. Ask before applying them.
