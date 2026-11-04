---
id: met
status: draft
phase: MVP (manual entry) / P2 (imports and reports) — see D-01
version: 1.1
updated: 2026-11-01
---

# Metrics and reports

## Requirements

- **MET-001** Import data **only from authorized profiles** via API or an allowed connector; manual entry MAY exist and MUST be labeled as manual.
- **MET-002** Each metric records network, account, source, collection window, timestamp and availability.
- **MET-003** Missing data shows as `N/D`; NEVER a fictitious number presented as real. Demo data MUST be clearly labeled.
- **MET-004** Assess evolution, formats, goals and tests without implying causation that wasn't demonstrated.
- **MET-005** Monthly interpretive report, analytical text reviewable by a human, PDF export and history.
- **MET-006** Per-network metrics respect their differences (Instagram: reach, interactions, saves…; TikTok: views, engagement, retention… — when the API provides them).
- **MET-007** Charts, comparisons, filters (period, platform), visible sources and limitations; export.
- **MET-008** End of month: import metrics and draft the report; a human checks the numbers ([AUT-017](automations.md)).
- **MET-009** The end client only sees metrics for their own accounts.
- **MET-010** Re-importing the same window MUST NOT duplicate snapshots. PROPOSAL.

## MVP vs P2 (pending D-01)

The source MVP includes a "report with manual entry or clearly labeled demo data" while `/metrics` and `/reports` are P2. PROPOSAL: MVP = manual metric entry + simple report with sources and `N/D`; P2 = API imports, charts, interpretive report.

## Data

`platform_metrics`, `metric_snapshots`, `social_accounts`.

## Screens

`/metrics`, `/reports`.

## Acceptance criteria

- [ ] A report identifies source, dates and missing metrics.
- [ ] No fictitious number without a demo label.
- [ ] PDF export reproduces source and period.

## Open decisions

- D-01 MVP scope. D-25 Metrics actually available per account type in the Meta/TikTok APIs.

## Evidence

—
