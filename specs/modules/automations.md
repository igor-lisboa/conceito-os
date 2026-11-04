---
id: aut
status: draft
phase: P3
version: 1.1
updated: 2026-10-30
---

# Automations

## General requirements

- **AUT-001** Every automation has a trigger, an action and, where stated, a human safeguard.
- **AUT-002** Executions record actor, timestamps, version, rationale and external ID; states in [states-events](../technical/states-events.md#automated-execution).
- **AUT-003** Idempotent jobs with controlled retries, dead-letter queue and observability.
- **AUT-004** `/automations` screen: rules, triggers, frequency, permissions and logs.
- **AUT-005** An automation never publishes, does external prospecting outreach nor issues contracts without human approval.

Some triggers below (e.g. AUT-016 publishing failure) are needed before P3; those individual flows are delivered with their modules, and P3 adds the user-configurable automation layer.

## Catalog

| ID | Trigger | Action | Safeguard |
| --- | --- | --- | --- |
| AUT-010 | New lead | Record, qualify, create next step | Outreach requires human review |
| AUT-011 | Proposal accepted | Create client, onboarding, folder and tasks | Confirm signature and commercial data |
| AUT-012 | Briefing completed | Generate preliminary diagnosis | Review of information and strategy |
| AUT-013 | Strategy approved | Generate 30-day draft calendar | Editorial and capacity review |
| AUT-014 | Content ready | Check scope, copy and guidelines | Internal and client approval |
| AUT-015 | Client approves | Send to scheduling queue | Confirm connection and permissions |
| AUT-016 | Publishing fails | Controlled retry, log and alert | Never hide the error |
| AUT-017 | End of month | Import metrics and draft report | Check the numbers |
| AUT-018 | Trend detected | Cross with DNA, score, suggest test | Source, license and relevance |
| AUT-019 | Network update | Alert team and possibly affected clients | Confirm information and availability |
| AUT-020 | Contract near expiry | Create renewal task | External message only after approval |

## Data

`automations`, `executions`, `notifications`.

## Open decisions

- D-05 n8n for peripheral integrations vs own queue; cost per automation.

## Evidence

—
