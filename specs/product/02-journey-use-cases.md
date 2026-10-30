---
id: uc
status: draft
phase: all
version: 1.1
updated: 2026-10-30
---

# End-to-end journey and use cases

## Journey

1. A lead is detected or added manually to the CRM.
2. Research and qualification with sources; a personalized approach is suggested.
3. Meeting, proposal, negotiation and recording of the decision.
4. Contract reviewed and signed (in-house or external solution).
5. Onboarding: briefing, files, authorizations and goals.
6. DNA + diagnosis + competitors + strategy + KPIs approved.
7. Seasonal planning + 30-day calendar.
8. Creation of artwork, videos, scripts and captions; internal and client review.
9. Scheduling/publishing through an allowed connector or a manual flow.
10. Metrics, report, recommendations and new experiments.
11. Renewal, repricing or offboarding with data export and access revocation.

## Use cases

Actors are job functions; see the [role mapping](01-roles-permissions.md#job-functions--roles-proposal-d-20).

| ID | Actor | Use case | Main flow and outcome | Module |
| --- | --- | --- | --- | --- |
| UC-01 | Admin | Create agency/client | Registers entity, owners, plan and channels; creates an isolated space and initial checklist | [AUTH](../modules/auth-organization.md), [CLI](../modules/clients-briefing.md) |
| UC-02 | Commercial | Qualify lead | Records source, reviews public signals, sets stage, drafts approach for review | [CRM](../modules/crm-prospecting.md) |
| UC-03 | Admin/commercial | Issue proposal | Picks package, scope and pricing, generates PDF, records sending/acceptance | [ONB](../modules/proposals-contracts-onboarding.md) |
| UC-04 | Manager | Onboarding | Sends briefing, requests files, collects approvals, sets up authorized channels | [ONB](../modules/proposals-contracts-onboarding.md) |
| UC-05 | Strategist | Build diagnosis | Uses briefing, verifiable research and connected channels; records sources and recommendations | [STR](../modules/diagnosis-strategy.md) |
| UC-06 | Strategist | Plan 30 days | Picks goal, platform, volume and seasonality; AI drafts; a person approves the calendar | [CAL](../modules/calendar-seasonal.md) |
| UC-07 | Creative | Produce content | Opens task, reads briefing, attaches art/video, caption, CTA, requests review | [PRO](../modules/production-approval.md) |
| UC-08 | End client | Approve piece | Sees preview, caption, channel and date; approves or requests changes with a comment; history saved | [POR](../modules/client-portal.md) |
| UC-09 | Manager | Publish/schedule | Checks approval, permissions, format and channel; schedules via integration or guides manual posting | [INT](../modules/social-integrations.md) |
| UC-10 | Analyst | Monthly report | Imports allowed metrics, shows source/period, summarizes results and hypotheses | [MET](../modules/metrics-reports.md) |
| UC-11 | Strategist | Adapt a global trend | Filters by country/network, assesses DNA fit, generates a testable script, records evidence | [AI](../modules/ai-intelligence.md) |
| UC-12 | Admin | Assess profitability | Crosses revenue, hours and costs; flags margin and scope limits | [FIN](../modules/agency-finance.md) |
| UC-13 | Admin | Manage access | Invites/revokes members, sets client scope, reviews audit log | [AUTH](../modules/auth-organization.md) |
| UC-14 | Authorized user | Get alerted | Receives a relevant alert (task, approval, trend, update) with origin and link | [NTF](../modules/notifications.md) |
| UC-15 | Strategist/designer | Redesign identity | Reviews profile and references, collects desired changes, recommends keep/adjust/redo, prepares previews and guide; client approves before adoption | [BRD](../modules/brand-identity.md) |

## Mandatory exceptions (all journeys)

Authentication failure, unauthorized client, expired integration, missing data, rejection with a new version, edit conflict, publishing failure.

- **UC-EXC-001** The system MUST show clear feedback, preserve drafts and offer a retry when safe.
- **UC-EXC-002** An integration error MUST NOT delete content being edited nor be shown as a completed publication.

## Reference end-to-end paths

1. `CRM → Lead → Quick diagnosis → Proposal → Acceptance → Client → Onboarding → Briefing → Strategy → Calendar → Production → Approval → Scheduling → Report`
2. `Clients → Client X → Identity → Initial assessment → Preferences → Visual proposal → Comparator → Approval → Brand library`
3. `Intelligence → Trends → International trend → Client fit → Lab experiment → Script → Calendar → Result`
4. `Administration → Subscriptions → Overdue invoice → Notices → Grace period → Partial suspension → Payment confirmed → Reactivation + audit`
