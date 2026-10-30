---
id: str
status: draft
phase: P2
version: 1.1
updated: 2026-10-30
---

# Diagnosis and strategy

## Goal

Produce versioned diagnoses and strategies with traceable evidence that feed the DNA and editorial generation.

## Requirements

- **STR-001** Initial analysis of the client's channels, brand, positioning, audience, offers and competitors.
- **STR-002** Every researched claim MUST carry evidence + source + date; facts are distinguished from hypotheses.
- **STR-003** A strategy contains goals and KPIs, value proposition, editorial pillars and per-network strategy (Instagram and TikTok handled separately).
- **STR-004** Version history and record of approvals (internal and client).
- **STR-005** An approved strategy enables generating a 30-day draft calendar ([CAL-010](calendar-seasonal.md)).
- **STR-006** The diagnosis MAY use SWOT/hypotheses; users can create hypotheses and edit the plan.
- **STR-007** Competitors and research sources live in `competitors`/`research_sources` with an observation date.
- **STR-008** An approved briefing creates a diagnosis task; an AI-generated preliminary diagnosis requires human review.

## Flow

Briefing → diagnosis (checklist + sources) → strategy (draft) → internal approval → client approval → published → enables calendar.

## Data

`strategies`, `strategy_versions`, `brand_dna`, `competitors`, `research_sources`.

## Screens

`/clientes/:id/estrategia`.

## Acceptance criteria

- [ ] A new version never overwrites the previous one.
- [ ] A claim without source/date cannot be marked as fact.
- [ ] The client only sees published versions.

## Evidence

—
