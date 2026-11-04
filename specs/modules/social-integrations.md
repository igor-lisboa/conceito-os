---
id: int
status: draft
phase: P2
version: 1.1
updated: 2026-11-04
---

# Integrations: Instagram and TikTok

| Aspect | Instagram | TikTok |
| --- | --- | --- |
| Content | Feed, carousel, Reels, Stories as supported | Native video, formats and trends |
| Metrics | Reach, interactions, saves etc., if the API provides them | Views, engagement, retention etc., if the API provides them |
| Publishing | Per approved types and permissions | Per Content Posting API, review and permissions |
| Competitors | Only allowed public data | Only allowed public sources |
| Strategy | Relationship, authority, discovery | Discovery, retention, native language |

## Requirements

- **INT-001** Integration via OAuth, official Meta and TikTok connectors, minimum scopes.
- **INT-002** Requires app registration, platform review, secure token renewal, quotas, tests and maintenance.
- **INT-003** Tokens encrypted (`oauth_tokens`); revocation supported; automatic renewal with an alert on failure.
- **INT-004** **Manual fallback** when publishing or a metric isn't available via API.
- **INT-005** Publishing: validate approval, permissions, format and channel; record attempts, failures and confirmation with external ID.
- **INT-006** Publishing failure: controlled retry, log and alert; NEVER hide the error nor mark it as published.
- **INT-007** An expired integration shows a warning and guides reconnection without losing content.
- **INT-008** APIs change; capabilities per account/type are detected and displayed, not assumed.
- **INT-009** A network abstraction allows adding other networks later.
- **INT-010** Manual fallback publishing: the user marks a piece as published manually, optionally with the post URL; the record states it was manual. PROPOSAL. *Partly implemented 2026-11-04: `publish_method` is recorded as `manual` on every publication and shown on the piece; the network publishing itself is TD-20.*

## Data

`connectors`, `oauth_tokens`, `social_accounts`.

## Open decisions

- D-25 App approval, supported account types, publishing and metrics limits.

## Evidence

—
