---
id: pro
status: partially-implemented
phase: MVP
version: 1.1
updated: 2026-10-30
---

# Production, content and approval

## Requirements

- **PRO-001** Production stages shown to users: `idea → planned → script → production → internal review → client approval → scheduled → published → analyzed`. They map onto the fixed technical content states in [states-events](../technical/states-events.md#content). Whether agencies can rename/add stages is D-19.
- **PRO-002** A content item has briefing, artwork/file, script, full caption, hashtags, CTA, date/channel and versions.
- **PRO-003** Editor with autosave, attachments, per-network preview and "send to review". On mobile, steps: `Text → Media → Date/network → Review → Send for approval`.
- **PRO-004** Versions, revision count, comments (with mentions), owners and due dates.
- **PRO-005** Production Kanban: move cards according to rules and permissions; comment; log time; flag blockers. On mobile, a list filterable by stage (no horizontal dragging).
- **PRO-006** Preview of images, carousels and videos, and the full caption text.
- **PRO-007** Client approval: approve, or request changes with a comment; the decision returns to the editor with history.
- **PRO-008** Auditable approval history **per publication**, tied to the exact approved version.
- **PRO-009** Automatic publishing NEVER happens without the required approval.
- **PRO-010** A rejection creates a new version without losing the previous one.
- **PRO-011** Edit conflicts are detected and handled without losing content.
- **PRO-012** Scope, copy and guideline (DNA) check before sending for approval (AI-assisted, human-approved; P2+).
- **PRO-013** Editing a piece after it was approved invalidates that approval and returns it to review. PROPOSAL — follows from PRO-008.
- **PRO-014** If the client's "client approval required" setting is off ([CLI-010](clients-briefing.md)), internal approval is sufficient, and the record says so.

## Data

`content_items`, `content_versions`, `assets`, `approvals`, `tasks`, `comments`, `time_entries`.

## Screens

`/producao`, `/conteudos/:id`, `/aprovacoes`.

## Acceptance criteria

- [ ] Kanban changes state with permission checks and an audit trail.
- [ ] Content has briefing, artwork, script, caption, CTA and versions.
- [ ] A piece only reaches "scheduled" with a recorded approval of its current version.
- [ ] Notifications are not duplicated.

## Open decisions

- D-19 Configurable stages vs fixed states.
- D-21 Client approval required: per client / per content.

## Evidence

- Domain rules: `production/tests/domain/test_content.py`, `test_states.py`
- Use cases and permissions: `production/tests/application/test_content_service.py
- Persistence round-trip: `production/tests/adapters/test_django_repository.py
- Screens: `production/tests/test_views.py`, read side: `production/tests/test_queries.py`
