---
id: scr
status: draft
phase: all
version: 1.1
updated: 2026-10-30
---

# Screen inventory and behavior

**Convention (SCR-001):** every page implements empty, loading, success, recoverable-error and forbidden states. Actions that change sensitive data are audited. Filters live in the URL when possible. Breadcrumbs on desktop. Back preserves context. On mobile: step-by-step flows and reduced menus. Cards without a real action are not enough.

Routes are user-facing and stay in pt-BR, as in the source spec.

## Inventory

| Route | Main elements and actions | Phase |
| --- | --- | --- |
| `/login`, `/recuperar-senha` | Sign in, password reset, session protection, accept invitation; failure never reveals whether an account exists | MVP |
| `/inicio` | KPIs, pending items, due dates, shortcuts; a card opens a filtered list | MVP |
| `/clientes` | List, filters, search, add, archive with confirmation | MVP |
| `/clientes/:id/resumo` | Brand, owners, plan, status, links, invite authorized users | MVP |
| `/clientes/:id/briefing` | Sectioned form, attachments, versions, gaps | MVP |
| `/clientes/:id/identidade` | Visual audit, change briefing, moodboards, proposals, before/after comparator, approval | P2 |
| `/clientes/:id/estrategia` | Goals, positioning, DNA, pillars, competitors, approvals | P2 |
| `/calendario` | Month/week/list, channels, clients, status; drag date with validation | MVP |
| `/conteudos/:id` | Preview, caption, hashtags, CTA, date, revisions, autosave | MVP |
| `/producao` | Kanban with owners, due dates, files, comments, time logging | MVP |
| `/aprovacoes` | Review queue, decisions, versions, history | MVP |
| `/crm` | Kanban funnel, source, next actions, filters | MVP basic / P2 (D-01) |
| `/crm/leads/:id` | Commercial diagnosis, history, approach, proposal | MVP basic / P2 (D-01) |
| `/propostas` | Templates, packages, PDF, versions, acceptance | MVP basic / P2 (D-01) |
| `/contratos` | Templates, filling, history, link to client | P2 |
| `/onboarding` | Checklist templates, pending items, triggers | P2 |
| `/sazonal` | Dates, segments, selection and preparation | P2 |
| `/metricas` | Network, period, series, source, export, connect account | MVP manual / P2 (D-01) |
| `/relatorios` | Preview, reviewable text, export, history | MVP simple / P2 (D-01) |
| `/financeiro` | Contracts, expenses, hours, margin, alerts | P2 |
| `/biblioteca` | Files and templates per brand, search, permissions | P2 |
| `/inteligencia/dna` | Strategic memory, sources, decisions | P2 |
| `/inteligencia/lab` | Hypotheses, experiments, indicators, learnings | P3 |
| `/inteligencia/radar` | Competitors and opportunities with sources | P3 |
| `/inteligencia/pulse` | Client health, results, capacity, profitability | P3 |
| `/inteligencia/trends` | Trends by country/network, evidence, fit, ideas | P3 |
| `/inteligencia/updates` | Official updates, filters, impact, alerts | P3 |
| `/automacoes` | Rules, triggers, frequency, permissions, logs | P3 |
| `/configuracoes` | Team, roles, integrations, plans, identity, logs, webhooks | MVP / P2 |
| `/portal` | Client space: approvals, calendar, reports | MVP (approval) / P2 (rest) |
| SaaS billing (route TBD) | Active, paying, trial, delinquent, suspended, MRR, invoices; resend charge, authorized exception | P4 |
| Restricted access (route TBD) | Subscription status, invoice, pay, update method, export; returns after webhook confirms | P4 |

Note: the client library lives both as the client's Files tab (MVP, [CLI-007](../modules/clients-briefing.md)) and as the cross-client `/biblioteca` (P2).

## Behavior and destination per screen

| Screen | Actions | Destination / output |
| --- | --- | --- |
| Login | Sign in, recover password, accept invitation, sign out | `/inicio` or authorized portal |
| Dashboard | Filter by period, open indicators, prioritize pending items | Filtered module list |
| CRM | Create, qualify, record contact, create opportunity and proposal | Lead → record → proposal → onboarding |
| Clients | Search, filter, create, archive | Client page with tabs |
| Briefing/onboarding | Create invitation, save draft, request corrections, finish | Approved briefing triggers diagnosis |
| Diagnosis/identity | Analyze, justify proposal, compare before/after, send version | Approval → versioned brand guide and library |
| Strategy | Create hypothesis, edit plan, send for approval | Approved strategy enables editorial generation |
| Calendar | Drag (validated), filter, duplicate, open editor | Detail; change updates task |
| Editor | Autosave, attach, per-network preview, send to review | Internal review → client approval → publishing |
| Kanban | Move by rules, comment, log time, flag blocker | Opens editor/task |
| Portal | Approve, request changes with comments, fill briefing | Decision returns to editor; no internal costs |
| Metrics | Connect account, refresh, generate report | Exportable reports, no invented data |
| Radar/Trends/Updates | Save opportunity, filter, request per-client assessment | Becomes Lab hypothesis or calendar topic |
| Agency finance | Record receipt/cost, reconcile, filter overdue | Client financial record |
| SaaS billing | Filter, view history, resend charge, apply exception | Subscription detail + audit |
| Restricted access | Pay, update method, export | Dashboard after webhook |
| Administration | Invite/revoke, webhooks, policies, audit | Back to origin with confirmation |

## Cross-cutting features (SCR-010)

Permission-aware global search; in-app/email notifications; comments with mentions; change logs; attachments and media previews; saved filters; template duplication; import/export; version history; segmented seasonal calendar; quality checklists; accessibility; contextual help; notification preferences; agency timezone; publishing date/time per channel.

## Reference screens in the PDF

Dashboard, Clients, Client page (Overview, DNA, Strategy, Profiles, Competitors, Files, Metrics), Calendar, Content editor, Approval portal, Metrics, CRM, Trends, Updates, Finance, Administration.
