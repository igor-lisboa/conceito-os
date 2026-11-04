---
id: onb
status: draft
phase: MVP basic / P2 (see D-01)
version: 1.1
updated: 2026-10-30
---

# Proposals, contracts, briefing and onboarding

## Goal

Turn a won lead into an operating client, with versioned documents and securely authorized access.

## Actors and permissions

Admin and commercial issue proposals/contracts; the manager runs onboarding; the end client fills in the briefing and only sees their own published documents.

## Requirements

- **ONB-001** Reusable proposal templates: short diagnosis, goals, deliverables, limits, pricing, terms, next steps.
- **ONB-002** Proposal PDF generation, versions and recording of sending/acceptance.
- **ONB-003** Parameterized contract templates; they MUST be reviewed by a legal professional before use. Taxes and clauses are parameterized and validated by qualified professionals.
- **ONB-004** Signature via in-house or external solution (D-07).
- **ONB-005** Briefing with conditional questions: goals, audience, tone of voice, competitors, products, channels, files. See [CLI](clients-briefing.md).
- **ONB-006** Configurable onboarding checklist: documents, OAuth authorizations, initial schedule.
- **ONB-007** The system MUST NOT ask for social network passwords in forms nor store them; access is via OAuth/secure flow.
- **ONB-008** An accepted proposal creates client, onboarding, folder and tasks **after confirming signature and commercial data** ([AUT-011](automations.md)).
- **ONB-009** A completed briefing creates a diagnosis task ([STR](diagnosis-strategy.md)).
- **ONB-010** Offboarding: on contract end, export the client's data and revoke integrations and portal access (journey step 11). PROPOSAL — the source mentions it only in the journey.

## Main flow

Proposal → acceptance → reviewed/signed contract → client created → checklist → briefing → channel authorizations → diagnosis.

## MVP vs P2 (pending D-01)

PROPOSAL: MVP = proposal from a simple template + PDF + acceptance record + onboarding checklist; P2 = contract templates, e-signature integration, conditional briefing logic.

## Data

`proposals`, `contracts`, `clients`, `tasks`, `assets`.

## Screens

`/proposals`, `/contracts`, `/onboarding`, `/clients/:id/briefing`.

## Exceptions

Acceptance with incomplete commercial data; OAuth authorization denied or expired; incomplete briefing (show gaps).

## Acceptance criteria

- [ ] A proposal produces a versioned PDF and records acceptance with date/actor.
- [ ] No field or flow collects a social network password.
- [ ] Onboarding only advances once mandatory checklist items are done.

## Open decisions

- D-01 MVP scope. D-07 Signature tool and legal templates.

## Evidence

—
