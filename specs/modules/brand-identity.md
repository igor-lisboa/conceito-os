---
id: brd
status: draft
phase: P2
version: 1.1
updated: 2026-10-30
---

# Profile diagnosis and visual identity redesign

## Goal

Analyze the client's digital presence and current identity and, when needed and contracted, propose a redesign aligned at once with the client's requests, the diagnosis and the brand strategy.

## Inputs

Briefing of preferences and constraints (keep/change/avoid); current logos and files; existing palette and typography; approved visual references; channels and existing posts; audience, positioning, competitors and goals; redesign budget and scope.

## Requirements

- **BRD-001** Collect an identity briefing with preferences, references and explicit limitations.
- **BRD-002** Audit the profile: bio, profile picture, highlights, covers, feed, visual coherence, hierarchy, legibility, accessibility, format fit, Instagram × TikTok consistency.
- **BRD-003** Analyze competitors' visual differentiation through allowed sources, with evidence and date.
- **BRD-004** Produce a current vs. proposed diagnosis, separating strengths, observed problems, hypotheses and changes requested by the client.
- **BRD-005** Recommend **keep, partially adjust or redesign**; MUST NOT push a rebrand when unnecessary.
- **BRD-006** Build a moodboard and 2–3 visual directions with rationale; propose palettes, type pairings, graphic language, photo treatment and a template system. Respect third-party marks and rights.
- **BRD-007** Show applied previews (profile picture, covers, feed, carousel, Reels/TikTok, Stories when relevant) for comments, comparison, change requests and explicit approval.
- **BRD-008** After approval, produce identity guide, tokens, templates and editable/exportable files **only if design tools are integrated**; keep versions and decision traceability.
- **BRD-009** Link the approved version to Conceito DNA and to the content generator.
- **BRD-010** AI produces proposals and previews only; final vector logos, professional identity and editable files require an in-house/integrated design pipeline and **human review**.

## Acceptance criteria

- [ ] No change is published without approval.
- [ ] The client sees requested vs. proposed changes, reasons, files and versions.
- [ ] The system records constraints, approvers, revisions and dates.

## Data

PROPOSAL: `brand_identity_versions` (or versions within `brand_dna`) — to be settled in the [data model](../technical/data-model.md).

## Screens

`/clients/:id/identity` (audit, change briefing, moodboards, before/after comparator, approval).

## Open decisions

- D-14 Design tool/pipeline for vectors and editable files.

## Evidence

—
