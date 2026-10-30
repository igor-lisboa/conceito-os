---
id: cli
status: draft
phase: MVP
version: 1.1
updated: 2026-10-30
---

# Clients, brands and briefing

## Goal

A structured record and history for each client (brand), isolated per organization and per client.

## Requirements

- **CLI-001** Create a client with brand, plan, channels, status and owners.
- **CLI-002** Client page with tabs: Summary, Briefing, Identity, Strategy, Content, Metrics, Files (plus Approvals on mobile).
- **CLI-003** Briefing organized in sections, with save draft, attachments, versions, missing-data indicators and correction requests.
- **CLI-004** Invite authorized users (team, freelancer, end client) with scope and expiry ([AUTH-011](auth-organization.md)).
- **CLI-005** Archive a client with explicit confirmation; never delete silently.
- **CLI-006** Creating a client creates an isolated space and an initial checklist (UC-01).
- **CLI-007** File library per brand with search and permissions; private upload and short-lived URLs.
- **CLI-008** Change history of the client record (audit).
- **CLI-009** List with search and filters; filters kept in the URL.
- **CLI-010** Per-client setting **"client approval required"** (default: on), used by the content state machine ([EVT](../technical/states-events.md)). PROPOSAL, D-21.

## Data

`clients`, `social_accounts`, `assets`, `brand_dna`, `memberships`.

## Screens

`/clientes`, `/clientes/:id/resumo`, `/clientes/:id/briefing`, `/biblioteca`.

## Exceptions

Duplicate client name; briefing with missing required sections (show gaps, allow draft); upload failure (keep the rest of the form).

## Acceptance criteria

- [ ] Briefing creates a structured record with files and history.
- [ ] A user only lists clients they are assigned to.
- [ ] A private file cannot be opened without a valid signed URL.
- [ ] Archiving asks for confirmation and keeps all data.

## Open decisions

- D-21 Client approval required: per client, per content type, or both.

## Evidence

—
