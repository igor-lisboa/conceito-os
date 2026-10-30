# Conceito OS — instructions for Claude

Web platform for social media professionals and agencies (Conceito Co), conceived and directed by **Beatriz** (product owner). The repository currently contains **specs only**; there is no code yet.

## Core rule: spec-driven

**Everything in this project is based on [`specs/`](specs/README.md).** The specs are the source of truth.

1. **Read before acting.** Before planning, writing code or answering questions about product behavior, read the module spec (index in `specs/README.md`) and the cross-cutting ones: `product/01-roles-permissions.md`, `technical/security-privacy.md`, `technical/states-events.md`, `technical/data-model.md`.
2. **Keep them current.** Any change to behavior, rules, permissions, states, entities, screens or phase scope updates the spec **in the same piece of work**. Follow `specs/PROCESS.md` (including its consistency checklist) and log it in `specs/CHANGELOG.md`.
3. **Don't invent.** Don't create requirements, integrations, numbers, deadlines or business decisions that don't come from Beatriz or the specs. Suggestions go in marked `PROPOSAL`. Items in `specs/planning/risks-open-decisions.md` are not yours to decide: present options with a recommendation and ask.
4. **Spec vs request/code divergence.** Point it out explicitly, ask which one is right, then fix the other. Never resolve it silently.
5. **Honest status.** Mark `implemented` / `[x]` only with evidence (code + passing test) recorded in the spec's "Evidence" section.
6. **Traceability.** Cite requirement IDs (`CRM-004`, `BIL-010`…) in commits, tests and PRs. IDs are never reused or renumbered.

## Product invariants (never violate)

- Data segregated by `organization_id`; authorization by organization, user and client, **always enforced on the backend**. Hiding in the UI is not enough. No IDOR via ID swapping.
- No secrets in the browser; network tokens encrypted; **never** ask for or store social network passwords.
- AI is an explainable copilot. **Nothing is published, sent to third parties or contracted without a recorded human approval.** No spam or bulk messaging.
- No fictitious number shown as real; missing data = `N/D`; demo data always labeled.
- Researched claims carry source + date; fact ≠ hypothesis; correlation ≠ causation.
- Integration/publishing failures are never hidden and never delete content being edited.
- Non-payment never deletes data. A social media client's late payment ≠ a SaaS subscriber's delinquency (financial contexts A and B are separate).
- Every screen has empty, loading, success, recoverable-error and forbidden states.
- Platforms: desktop primary + truly responsive mobile. **No dedicated tablet experience.**

## Conventions

- **Language**: specs, code, identifiers and commit messages in English. Product UI copy in Brazilian Portuguese (pt-BR); user-facing routes stay in pt-BR (`/clientes`). Reply to the user in the language they write in.
- **Stack** suggested but not decided (`specs/technical/architecture.md`): Next.js, TypeScript, React, Tailwind, PostgreSQL/Supabase. Confirm before scaffolding the project.
- **Phases**: MVP → P2 → P3 → P4. Don't build later-phase features without being asked.
- **Design**: tokens and identity in `specs/ux/design-system.md`. The brand lilac/pink/gray fail contrast as text; use them as fills only.

## Commands

- `/spec-check` — audit spec consistency (links, IDs, status, open decisions).
- `/spec-sync` — after a change, update specs, checklist and changelog.
- `/spec-new` — create a new module spec from the template.

Detailed rules: `.claude/rules/`.
