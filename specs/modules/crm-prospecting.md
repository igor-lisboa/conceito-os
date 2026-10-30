---
id: crm
status: draft
phase: MVP basic / P2 (see D-01)
version: 1.1
updated: 2026-10-30
---

# CRM and prospecting

## Goal

Manage leads from the first signal to won/lost, with traceable research and outreach that is always reviewed by a human.

## Actors and permissions

Owner/admin (yes); account manager (if permitted); others not by default. See [roles](../product/01-roles-permissions.md).

## Requirements

- **CRM-001** Pipeline: researched → qualified → approach approved → contacted → meeting → proposal → negotiation → won/lost. Mapped to technical states in [states-events](../technical/states-events.md#lead).
- **CRM-002** Search potential clients by niche, region and digital-presence signals, **only through allowed sources and methods** (D-13).
- **CRM-003** Each lead records the information source, lookup date, fit assessment, rationale and owner.
- **CRM-004** The system MAY generate personalized DM/email drafts from evidence; it MUST require human review before anything is sent.
- **CRM-005** The system MUST NOT send bulk campaigns/spam.
- **CRM-006** Interaction history, reminders and next steps per lead.
- **CRM-007** Opt-out/objection MUST be recorded and respected.
- **CRM-008** A lead with an accepted proposal MUST be convertible into a client that starts onboarding ([ONB](proposals-contracts-onboarding.md)).
- **CRM-009** No researched content without source and date.
- **CRM-010** Lost leads record a reason. PROPOSAL.
- **CRM-011** Duplicate detection by handle/email/domain when creating a lead. PROPOSAL.

## Main flow

New lead → research/qualification → approach (draft → approval) → contact → meeting → proposal → negotiation → won (creates client) or lost (with reason).

## MVP vs P2 (pending D-01)

The source roadmap puts a "basic CRM" in Phase 1 while the screen inventory marks `/crm` as P2. Until D-01 is decided, the PROPOSAL is: MVP = manual lead list + stages + interactions (CRM-001, 003, 006, 007, 008); P2 = research assistance and AI drafts (CRM-002, 004).

## Data

`leads`, `interactions`, `deals`, `proposals`, `research_sources`. See [data model](../technical/data-model.md).

## Screens

`/crm` (Kanban funnel), `/crm/leads/:id`. See [screens](../ux/screens.md).

## Exceptions

Source unavailable; duplicate lead; contact who opted out; draft generation failure (keep data).

## Acceptance criteria

- [ ] A lead cannot move to "contacted" without a recorded approved approach.
- [ ] Every researched fact shows source and date.
- [ ] A recorded opt-out blocks new contact.

## Out of scope

Automatic message sending; scraping that violates platform terms.

## Open decisions

- D-01 MVP scope.
- D-13 Which prospecting sources are actually allowed (platform terms, LGPD).

## Evidence

—
