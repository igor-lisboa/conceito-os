---
id: cal
status: draft
phase: MVP (calendar) / P2 (seasonal and assisted generation)
version: 1.1
updated: 2026-10-30
---

# Editorial calendar and seasonality

## Requirements

### Calendar (MVP)

- **CAL-001** Month/week/list/Kanban views, filtered by client, network, campaign, state, owner and date; filters kept in the URL.
- **CAL-002** On mobile: daily/weekly agenda and compact filters.
- **CAL-003** Drag to change date MUST validate rules (e.g. can't move an approved piece without re-approval if the date is part of what was approved — PROPOSAL); the change updates the related task.
- **CAL-004** Duplicate a piece and open the editor from the calendar.
- **CAL-005** Each entry contains: goal, audience, pillar, format, hook, script/copy, CTA, date, media and status.
- **CAL-006** 30/60/90-day planning per client, platform, format, owner and campaign.
- **CAL-011** Timezone per agency; publishing date/time per channel. Dates are stored in UTC and shown in the agency timezone.

### Seasonal and assisted generation (P2)

- **CAL-007** Database of Brazilian dates: fixed, movable and industry-specific, each with source and year.
- **CAL-008** Dates selected by relevance to the client profile; MUST NOT insert holidays indiscriminately.
- **CAL-009** Configurable lead time for planning, shooting, design, review and approval.
- **CAL-010** An approved strategy generates a **draft** 30-day calendar; it requires editorial and capacity review before use.

## Data

`calendar_entries`, `campaigns`, `seasonal_events`, `content_items`.

## Screens

`/calendario`, `/sazonal`.

## Acceptance criteria

- [ ] Calendar creates and filters content by client, channel, state and date.
- [ ] Desktop shows month/week; mobile shows a daily agenda.
- [ ] Each seasonal date shows source and year.
- [ ] A generated calendar is never used without a recorded human approval.

## Open decisions

- D-26 Whether a date change after client approval requires re-approval.

## Evidence

—
