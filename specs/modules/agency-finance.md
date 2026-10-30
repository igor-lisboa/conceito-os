---
id: fin
status: draft
phase: P2
version: 1.1
updated: 2026-10-30
---

# Agency finance

Context A. Not to be confused with [SaaS billing](saas-billing.md).

## Requirements

- **FIN-001** Service contracts, installments, receipts, costs, freelancers and hours per client.
- **FIN-002** Estimated margin per client; alerts for low profitability and for extra revisions beyond scope.
- **FIN-003** Record receipt/cost, reconcile, filter overdue items; financial record per client.
- **FIN-004** Taxes and contract rules are parameterized and validated by qualified professionals.
- **FIN-005** A **social media client's** late payment raises an alert/contract control; it MUST NOT automatically block the portal without an explicit contract rule and an agency decision.
- **FIN-006** A contract nearing expiry creates a renewal task; external messages only after approval.
- **FIN-007** Internal financial data (margins, costs, prices) NEVER visible to end clients or freelancers.
- **FIN-008** Pulse links hours/costs to commercial results only when the data supports it.
- **FIN-009** Currency BRL; amounts stored as integer cents (or exact decimal), never floating point. PROPOSAL.

## Data

`contracts`, `agency_invoices` (see D-11), `costs`, `time_entries`.

## Screens

`/financeiro`.

## Acceptance criteria

- [ ] Margin is computed from recorded revenue, hours and costs.
- [ ] A role without permission cannot read amounts via the API.

## Evidence

—
