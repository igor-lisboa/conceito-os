---
id: nav
status: draft
phase: MVP
version: 1.4
updated: 2026-11-16
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

## Current application shell and public entry (2026-11-16)

Requested by Igor: simplify the crowded navigation, use a single theme icon,
improve account/logout and the mobile bottom bar, and add a public introduction
with separate paths for existing users and prospective clients.

- **NAV-015** The public root `/` introduces existing capabilities, labels its
  product preview as illustrative, and offers two paths: existing access goes to
  `/accounts/login/` (or the workspace for signed-in visitors); prospective clients
  go to `/contact/`. The authenticated dashboard moves to `/dashboard/` and retains
  the `home` route name, login requirement and client-to-portal redirect.
- **NAV-016** The public contact form asks for name, email, brand/company, interest
  and project context. Required fields, email, choice and length limits are
  validated on the server. Valid answers produce an encoded `mailto:` draft for
  the existing `CONTACT_EMAIL`. The visitor opens their mail app and reviews/sends
  the draft. Show a direct address and the answers as a fallback. No account,
  lead, database record or outgoing server email is created by this flow.
- **NAV-017** Desktop navigation groups currently implemented modules in a
  persistent sidebar (workspace, planning and owner administration). CRM visibility
  follows the per-person capability. Client users see only portal destinations.
  The top bar contains section context, notifications, a single sun/moon theme
  button and an account menu containing account, security, language and POST logout.
  The theme button has an accessible action label and remembers the choice.
- **NAV-018** Below 1024 px, a fixed bottom bar uses icons, text labels and an active
  state: Home, Clients, Calendar, Tasks, More. The client variant uses Approvals,
  Calendar, Files, Contact, More. More opens the full navigation drawer; Escape,
  close and backdrop dismiss it, focus stays inside while open and returns to the
  opener when dismissed. The bottom bar is hidden on desktop and public pages.

This implements the currently available module subset; it does not introduce the
future sidebar destinations proposed above or resolve their full scope (D-02).

## Evidence

- `apps/core/tests/test_public_site.py`: public entry, Portuguese text, protected
  dashboard, existing sign-in/logout, portal isolation, active entries, CRM grant,
  contact validation, CSRF, URL encoding, escaping and absence of outgoing email.
- `apps/core/tests/test_theme_toggle.py`, `test_theme_contrast.py`, `test_i18n.py`:
  theme controls, existing contrast pairs and language selection/catalog.

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
