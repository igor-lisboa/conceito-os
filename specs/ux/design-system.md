---
id: dsg
status: draft
phase: MVP
version: 1.1
updated: 2026-10-30
---

# Conceito OS visual identity and design system

Derived from Conceito Co with a more technological character. Approved direction: sophisticated minimalism, generous whitespace, lilac and soft pink, graphite, rounded cards, clear hierarchy, discreet geometric symbols.

## Reference tokens

| Token | Value | Note |
| --- | --- | --- |
| `color.background` | `#F8F7FA` | off-white |
| `color.primary` | `#C9B8E9` | lilac |
| `color.accent` | `#E7D6DD` | nude pink |
| `color.neutral` | `#D9D9E0` | gray |
| `color.text` | `#1E1E24` | graphite |
| Heading font | Playfair Display | check license and performance |
| UI font | Montserrat | check license and legibility |
| Logo | `Conceito OS` + symbol derived from C/light | final vector pending |
| Theme | Light first; prepare dark mode | |

> Colors are suggestions from the visual specification, **not** a certified color sample of the artwork.

## Contrast check (estimated, verify with a tool)

| Foreground on background | Ratio | Verdict |
| --- | --- | --- |
| `text` on `background` | ≈ 15.5:1 | Passes AA/AAA for text |
| `text` on `primary` | ≈ 9:1 | Passes AA/AAA (graphite text on lilac buttons is fine) |
| `primary` on `background` | ≈ 1.7:1 | **Fails** text (4.5:1) and non-text UI (3:1) |
| `accent` / `neutral` on `background` | < 1.5:1 | **Fails**; decorative fills only |

Consequence: lilac, nude pink and gray are **fill colors**. They MUST NOT be used as text, icon, link, focus-ring or sole input-border colors on the light background.

## Requirements

- **DSG-001** Centralized tokens (color, typography, spacing, radius, shadow) in a single place; components never use loose values.
- **DSG-002** Dark mode is prepared from the tokens (light theme ships first; timing D-23).
- **DSG-003** WCAG 2.2 AA contrast verified for every text/background and UI-component/background pair (target level: [NFR-010](../technical/non-functional.md)).
- **DSG-004** Accessible components: keyboard, visible focus, adequate touch targets, interaction states (hover, focus, active, disabled, error).
- **DSG-005** Every screen has empty, loading, success, recoverable-error and forbidden states.
- **DSG-006** Final guide to produce: SVG logo, typography, spacing, components, tokens, states, contrast.
- **DSG-007** Images in the PDF are visual references, not UI code.
- **DSG-008** Add a darker "strong" variant of the primary color for links, focus rings, active states and borders, reaching ≥ 4.5:1 on `background`. Value chosen by the designer. PROPOSAL, follows from the contrast check.
- **DSG-009** Semantic status colors (success, warning, error, info) with accessible contrast, never conveying meaning by color alone. PROPOSAL.

## Visual reference

`Conceito_OS_Especificacao_Completa_Visual.pdf` (approved moodboard and wireframes) — not in this repository yet; suggested location `docs/references/`.

## Open decisions

- D-15 Font licensing and loading (both fonts are published under the SIL Open Font License on Google Fonts; confirm and decide self-hosting).
- D-14 Final logo vector.
- D-23 Dark mode timing.
