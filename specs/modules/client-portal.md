---
id: por
status: partially-implemented
phase: MVP (approvals) / P2 (rest)
version: 1.1
updated: 2026-11-01
---

# Client portal

An application inside the same product, in a separate and simple environment.

## Requirements

- **POR-001** Access only to the brands and work the client is authorized for.
- **POR-002** Sections: Home, Calendar, Approvals, Results, Files, Contact. MVP: Approvals (plus the minimum Home to reach them); the rest in P2.
- **POR-003** Approve or request changes with a comment; decision history; see art/video, full caption, channel and date.
- **POR-004** Fill in the briefing; see approved strategy, calendar and authorized reports.
- **POR-005** Configurable notifications ([NTF](notifications.md)).
- **POR-006** MUST NOT reveal internal margins, other clients' data or confidential pricing; no access to internal management or finances.
- **POR-007** Approval on mobile in a few steps, with large buttons and readable content.
- **POR-008** A client only sees their own pieces; changing an ID in the URL exposes nothing else.
- **POR-009** A client's late payment MUST NOT block the portal without an explicit contract rule and an agency decision ([FIN-005](agency-finance.md)).
- **POR-010** A portal user may approve on behalf of more than one brand only if invited to each. PROPOSAL.

## Screens

`/portal` — Home → Approvals → Content detail → Approve / request changes → Calendar → Results → Files.

## Acceptance criteria

- [ ] A client sees only their pieces, approves or requests changes, and comments.
- [ ] The decision returns to the editor with history.
- [ ] Approval works end to end on a 360 px wide screen.

## Evidence

- Portal screens and hidden internal data: `apps/portal/tests/test_views.py`
