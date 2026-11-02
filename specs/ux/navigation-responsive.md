---
id: nav
status: draft
phase: MVP
version: 1.3
updated: 2026-11-02
---

# Navigation and responsiveness

## Platforms (approved decision)

- **NAV-001 Desktop**: primary experience; reference width ≥ 1024 px, prioritizing 1280–1440 px; sidebar and dense tables.
- **NAV-002 Mobile**: truly responsive (360–430 px), not a shrunk desktop.
- **NAV-003 Tablet**: NO dedicated experience, layouts or tests at this stage; if opened on a tablet, one of the responsive variants shows, with no specific optimization promised. **Do not build a separate tablet interface.**
- **NAV-004** Both allow: sign in, browse clients/tasks/content/calendar, approve/reject materials, receive alerts and follow indicators. Advanced strategy editing, bulk CRM, reports and settings prioritize desktop, but stay reachable on mobile through simplified flows when essential.
- **NAV-005** Browsers: current Chrome, Safari, Edge, Firefox; test Safari on iPhone and Chrome on Android.
- **NAV-006** Priorities: accessibility, keyboard, contrast, touch targets, offline/error states.

## Desktop (≥ 1024 px)

- Three-zone layout: persistent sidebar 220–260 px; top bar with global search, organization and client selector, notifications, help and account menu; fluid work area with content up to 1440 px.
- Sidebar (PROPOSAL unifying the two lists in the source, D-02): Home, CRM, Clients, Planning (strategy), Content, Production, Calendar, Metrics, Intelligence, Finance, Library, Administration (settings).
- Breadcrumbs on deep pages; tabs on the client page.
- Side panels for short edits; full screen for strategy creation and content editing.
- Clicking a number on the dashboard opens the module list already filtered.
- Never lose content when switching sections.
- **NAV-007** Unauthorized modules are hidden, and the server blocks them as well.

## Mobile (360–430 px)

- Compact top bar with organization/client context; notifications in the header.
- Bottom bar (PROPOSAL per source §18.1, D-03): Home · Clients · Calendar · Tasks · More ("Início · Clientes · Calendário · Tarefas · Mais"); other modules under More. The source §15.1 had "Alerts" as a tab instead; the proposal keeps alerts in the header.
- Client page as tabs/segments: Summary, Strategy, Content, Metrics, Files, Approvals.
- Kanban → list by selectable status; tables → cards; filters in a drawer; calendar as daily/weekly agenda.
- Post editor in steps: `Text → Media → Date/network → Review → Send for approval`.
- Large, accessible approval buttons; summarized charts with details on tap.
- Relevant actions require explicit confirmation.
- The restricted-access screen for delinquency is mobile-friendly.

## Client portal

Separate, simple environment: Home, Calendar, Approvals, Results, Files, Contact. No access to internal management, finances or other clients.

## Behavior rules

- **NAV-010** Filters reflected in the URL when possible.
- **NAV-011** Back preserves context; navigation keeps the selected client.
- **NAV-012** No unnecessary horizontal scrolling on desktop or mobile.
- **NAV-013** Forms, uploads, alerts and confirmations work by touch and keyboard.
- **NAV-014** Filter bars on the board, content list and calendar are collapsed by default and open when a filter is set (D-29). Confirmed (D-29): keeps phones free of a permanent filter block, and keeps the active filter visible.

## Main flow

```text
LOGIN
  └── DASHBOARD
        ├── CLIENTS → Client → Briefing → Strategy → Calendar → Content
        ├── PRODUCTION → Kanban → Detail → Internal review → Client approval
        ├── CALENDAR → Item → Preview → Scheduling/Publishing
        ├── CRM → Lead → Diagnosis → Proposal → Contract → Onboarding → Client
        ├── METRICS → Report → Learnings → Next planning
        ├── INTELLIGENCE → DNA / Lab / Radar / Pulse / Trends / Updates
        ├── FINANCE → Costs → Margins → Alerts
        └── SETTINGS → Team / Permissions / Integrations

CLIENT PORTAL (restricted access)
  └── Home → Approvals → Content detail → Approve or request changes
           → Calendar → Results → Files
```

## Acceptance criteria

- [ ] Login and dashboard work on desktop and mobile without unnecessary horizontal scrolling.
- [ ] Desktop Kanban has columns; mobile has lists filterable by stage, no horizontal dragging.
- [ ] A client approves/requests a revision on mobile in a few steps, with readable art/video and caption.
- [ ] Calendar: month/week on desktop; daily agenda and compact filters on mobile.
- [ ] Client context is kept while navigating and going back.
- [ ] Forms, uploads, alerts and confirmations work by touch and keyboard.

## Open decisions

- D-02 Desktop sidebar items. D-03 Mobile bottom bar.
