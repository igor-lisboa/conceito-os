# Process: keeping the specs alive

## Rules

1. **Spec first.** Any change to behavior, business rule, permission, state, entity, screen or phase scope starts with (or at the latest ends in the same piece of work with) a spec update.
2. **Single source of truth.** Each rule lives in exactly one file; others link to it. Don't duplicate text.
3. **Honest status.** Mark `implemented` only with evidence: code + passing test. Record the evidence (test path / PR / commit) in the module's "Evidence" section.
4. **Stable IDs.** Requirements are `<PREFIX>-NNN`; code, tests and commits reference the ID. Never renumber.
5. **Conflicts.** If code and spec diverge, ask the product owner (Beatriz) which one is right, fix the other, and log it in the CHANGELOG.
6. **Open decisions** are not decided by Claude: record them, propose options with a recommendation, and wait.
7. **No invention.** Don't add requirements, integrations, numbers or deadlines that don't come from the product owner. Suggestions go in marked as `PROPOSAL`.

## Change workflow

1. Find the affected specs (index in [README.md](README.md)); also check permissions, states, data model and screens.
2. Edit the specs: text, IDs, acceptance criteria, `updated` and `version` in the front matter.
3. Implement and test against the acceptance criteria.
4. Update `status` and "Evidence".
5. Add a line to [CHANGELOG.md](CHANGELOG.md).

## Consistency checklist (before calling it done)

- [ ] New state/transition → [states-events.md](technical/states-events.md)
- [ ] New table/field → [data-model.md](technical/data-model.md) (with `organization_id`)
- [ ] New permissioned action → [01-roles-permissions.md](product/01-roles-permissions.md)
- [ ] New screen/route → [screens.md](ux/screens.md) and navigation, with empty/loading/error/forbidden states
- [ ] Phase scope change → [roadmap.md](planning/roadmap.md)
- [ ] Unresolved question → [risks-open-decisions.md](planning/risks-open-decisions.md)
- [ ] Internal links work; no duplicated IDs

## Standard front matter

```yaml
---
id: <prefix>
status: draft
phase: MVP | P2 | P3 | P4
version: 1.0
updated: YYYY-MM-DD
---
```
