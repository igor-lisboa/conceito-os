---
id: ai
status: draft
phase: P2 (DNA) / P3 (other engines)
version: 1.1
updated: 2026-10-30
---

# Artificial intelligence — six engines

## General rules

- **AI-001** AI is an explainable copilot; external actions require human approval.
- **AI-002** Data is isolated per client; knowledge retrieval is per client; no leakage across clients or tenants.
- **AI-003** Provider-agnostic layer; cost per task, usage limits and logs.
- **AI-004** **Minimum output format**: recommendation; client/goal; sources/date; confidence/limitations; rationale; adaptation; effort; who approves; test and later result.
- **AI-005** Agent architecture: an orchestrator plus specialized functions (strategy, creation, research, trends, metrics, commercial, documentation). Each agent has scoped tools, data and budget, with controls and logs.
- **AI-006** Never promise virality, nor detecting international trends before they reach Brazil.
- **AI-007** AI-generated content is labeled as AI-generated until a human edits/approves it. PROPOSAL.

## Engines

### Conceito DNA — brand strategic memory (P2)

- **AI-010** History of tone of voice, positioning, guidelines, approved decisions, campaigns, constraints, feedback and tests.
- **AI-011** Recommendations are justified with the relevant records.

### Conceito Lab — experimentation (P3)

- **AI-020** Hypothesis → audience/variable → content → period → KPI → analysis criterion → evidence/results → learning.
- **AI-021** Distinguish correlation from causation; no virality guarantees.

### Conceito Radar — competitors and opportunities (P3)

- **AI-030** Authorized public sources; comparative positioning; saturated themes; opportunities and differentiation, with date, source and rationale.

### Conceito Pulse — operations and results (P3)

- **AI-040** Hours per client, revisions, delays, team load, costs and margin; commercial correlation only when the data supports it.

### Conceito Trends — global trends (P3)

- **AI-050** Authorized sources from Brazil, US, Europe, Latin America and other markets; formats, audio when licensed, narratives, themes.
- **AI-051** Evidence-based classification: `emerging | growing | established | declining`.
- **AI-052** Cross-check with each client's DNA and resources; propose adaptations; record tests.
- **AI-053** Pipeline: legal/authorized collection → deduplication → source/date/country/network → classification → DNA fit → recommendation → review → experiment → analysis.

### Conceito Updates — platform news (P3)

- **AI-060** Monitor official Instagram and TikTok sources; record publication, region, gradual rollout, impact and actions.
- **AI-061** Separate `confirmed`, `testing`, `rumor`. Critical alerts per event; daily/weekly digests ([NTF-008](notifications.md)).

## Data

`brand_dna`, `experiments`, `trend_signals`, `platform_updates`, `research_sources`, `executions`.

## Screens

`/inteligencia/dna|lab|radar|pulse|trends|updates`.

## Open decisions

- D-06 AI providers and budget per task. D-13 Trend sources and licenses.

## Evidence

—
