# Spec changelog

Format: `YYYY-MM-DD · file(s) · change · reason`. Newest first.

- 2026-11-01 · modules/notifications.md, modules/clients-briefing.md · NTF-001..004 and NTF-006 partly implemented (in-app and email for content review events; idempotent; visibility-scoped); client archiving (CLI-005) implemented; documented in docs/phase-1-decisions.md and docs/technical-debt.md · Phase 1 MVP consolidation
- 2026-11-01 · modules/auth-organization.md · AUTH-002 implemented: password recovery by email, welcome email on account creation (pt-BR), sign-in by email, `create_initial_admin` command; email is required and unique · product owner request (admin access, SMTP)
- 2026-11-01 · technical/non-functional.md, planning/risks-open-decisions.md · UI available in English (default) and pt-BR, selectable per browser; NFR-002 added for translation completeness · product owner request
- 2026-11-01 · technical/architecture.md · Decided stack (Django 5.2, MySQL, Vercel, WhiteNoise); added layering rules ARC-010..016 · hexagonal + DDD decision, see docs/architecture.md
- 2026-11-01 · technical/states-events.md · Replaced the non-existent `approved → published` manual fallback with the real flow (`scheduled → published`); documented the manual moves table · spec/code divergence found during review
- 2026-11-01 · planning/risks-open-decisions.md · Recorded decided items (MySQL, Django, architecture, hosting, frontend) · implementation start
- 2026-11-01 · modules/production-approval.md, modules/client-portal.md, modules/clients-briefing.md, modules/auth-organization.md · Status set to partially-implemented; Evidence lists the test modules · first implementation pass

- 2026-10-30 · all · Translated all specs and Claude instructions to English; renamed files/folders to English · request from Igor
- 2026-10-30 · all · Review pass: added `modules/auth-organization.md` (AUTH), `modules/notifications.md` (NTF), `technical/non-functional.md` (NFR); mapped business pipelines to technical states (content, lead); mapped use-case actors to roles; added per-client "client approval required" setting; added WCAG contrast estimates; aligned phase labels with D-01; new open decisions D-19..D-24 · consistency review
- 2026-10-30 · all · One-time prefix rename before any code references existed: EST→STR, IDV→BRD, IA→AI, TEL→SCR, ARQ→ARC, SEG→SEC, DAD→DAT, `est-ev`→EVT. Numbers unchanged · English naming, removed collision between strategy (EST) and states
- 2026-10-30 · all · Initial creation: specification v1.0 (Oct 2026) refined into modular files with requirement IDs · request from Beatriz/Igor
