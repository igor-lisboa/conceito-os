# Personal data in Conceito OS: types, bases and handling

Prepared for the legal review of decision D-17. Status: **draft, for lawyer review**.

Decided 2026-11-16 (product owner):
- Keep everything forever. Nothing is deleted from the database (DAT-007).
- When a person asks, or a contract ends, personal data is **anonymized**: names, emails and contact fields are replaced by an anonymous marker, and the record stays (DAT-011).
- MFA stays optional for everyone (answer 5B).

Still open: the **legal basis** for each type below. The options are listed for the lawyer to choose. The platform does not decide them.

Legal bases in Brazilian law (LGPD, art. 7): consent; legal or regulatory obligation; contract performance; legitimate interest; protection of credit; study by research bodies; exercise of rights; health; protection of life; public policy; the controller's own use. Options below use the bases that usually fit this kind of work.

## Data types

| # | Data | Where it lives | Who it is about | Suggested basis (lawyer to confirm) | Handling |
| --- | --- | --- | --- | --- | --- |
| 1 | Account: name, email, language, password (hashed) | accounts | Team members | Contract performance | Anonymize when access is removed and the person asks |
| 2 | Authenticator secret (encrypted at rest) | accounts | Team members | Contract performance (security) | Switched off on anonymization; kept encrypted |
| 3 | Team membership, role, client access | accounts, clients | Team members | Contract performance | Soft deleted; kept; the person is anonymized on request |
| 4 | Audit trail: who did what, when, and to what | core | Team members, client staff | Legal obligation or legitimate interest (accountability, SEC-007) | Append-only; the actor link points at the anonymized account |
| 5 | Sign-in attempt counters (email hash, address hash) | accounts | Anyone who tries to sign in | Legitimate interest (security) | Automatically expires after 15 minutes |
| 6 | Client contacts (names and emails of the client's team) | clients, portal | Client staff | Contract performance | Anonymize at contract end, on request |
| 7 | Brand briefing (business information, tone, audience) | clients | Client business; may name people | Contract performance | Anonymize person names at contract end; business content kept |
| 8 | Content: captions, scripts, media links, comments | production | Client and team, when named | Contract performance | Kept; mentions and author names anonymized with the person |
| 9 | Approvals (who approved, what, when) | production | Client and team staff | Contract performance; legal evidence of approval | Kept; the person is anonymized |
| 10 | Notifications (recipient, text, time) | notifications | Team and client staff | Contract performance | Kept with the records they point to |
| 11 | CRM leads: name, contact, notes | crm | Prospects who did not sign | Legitimate interest or consent (lawyer to choose) | Anonymize on request or when the prospect asks |
| 12 | Proposals: values, client name | crm | Prospects and clients | Contract performance; pre-contract steps at the person's request | Kept; the name is anonymized |
| 13 | Monthly metrics (values per platform) | reports | Client account (business data) | Contract performance | Business data; kept |
| 14 | Tasks: title, owner, due date | tasks | Team members | Contract performance | Kept; owner name anonymized with the person |
| 15 | Contracts, invoices, costs (Phase 2) | finance (planned) | Client and agency | Legal obligation (tax, accounting); contract performance | Kept as the law requires; personal fields anonymized |
| 16 | Social network connection tokens (Phase 2, encrypted) | integrations (planned) | Team members, through their accounts | Consent; contract performance | Revoked on disconnect; the token is removed from use, not from the audit trail |

## What the lawyer must decide, per row

- The basis in the table, or another one.
- Whether consent is needed, and how it is recorded (rows 6, 7, 11, 16).
- Any legal period that must be respected before anonymizing (rows 4, 9, 15).
- Whether anonymizing a name in a published or sent message is enough, or the message must also be recalled (row 10).

## Rules the platform already follows

- Data is separated by organization and by client (SEC-002, SEC-017).
- Passwords are stored as hashes; authenticator secrets are encrypted at rest (SEC-005).
- Audit rows cannot be changed or deleted (SEC-016).
- Nothing is sent to a third party without a recorded human approval (CLAUDE.md invariant).
