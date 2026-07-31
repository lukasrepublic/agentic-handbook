# Acme Links — Design System (Claude Design brief)

> Self-sufficient brief for Claude Design. Paste as the first message; the supporting files
> `acme-links-design-system.html` (the visual canary) and `theme.css` (the token definitions)
> are in the uploads tray — refer to them for the exact tokens and primitive composition.

## Goal

Produce a small, reusable **design system** for **Acme Links**, a link-shortener with
accounts. Deliver: design tokens + a primitive component kit, rendered as a single
self-contained reference page matching the uploaded `acme-links-design-system.html` baseline.
The system's first consumer is the signed-in **dashboard** (a link list with click counts).

## Brand & voice

Calm, precise, trustworthy, fast. A *demo brand* (the "Acme" convention) — favor clean
conventions over novelty. One filled primary action per view; generous whitespace;
restrained color; strong legibility. Copy is plain and direct ("Create a link", "No links
yet"), never jargon, never first-person-plural marketing.

## Foundations (tokens — defined in the uploaded `theme.css`)

- **Color.** Primary = Indigo `#4F46E5` (hover `#4338CA`, active `#3730A3`, soft `#EEF2FF`,
  text-on-primary white). Neutrals = a Slate scale 50→900 (surfaces, text, borders).
  Semantic = success `#059669`, danger `#DC2626`, warning `#D97706`. Surface roles
  (`bg / surface / surface-2 / border / text / text-muted`) re-map for dark mode.
- **Typography.** Inter (system-ui fallback). Scale: 12 / 14 / 16 / 18 / 20 / 24 / 30 / 36.
  Weights 400 / 500 / 600 / 700. Headings tight line-height; body 1.5.
- **Spacing.** 4px base ramp: 4 / 8 / 12 / 16 / 20 / 24 / 32 / 40 / 48 / 64.
- **Radius.** sm 6 / md 8 / lg 12 / full. **Elevation.** subtle, low-contrast shadows.
- **Dark mode** is a first-class token set (a `[data-theme="dark"]` surface remap), not an
  afterthought.

## Component kit (the primitives)

| Component | Variants | States | Notes |
|---|---|---|---|
| **Button** | primary / secondary / ghost / danger · sizes sm / md / lg | default · hover (darker) · focus (3px primary ring) · disabled (opacity .5, not-allowed) | One filled primary per view. `<button>` element; `aria-disabled` not `disabled`. |
| **Input** | default / error · with label + help/error text | default · focus (primary border + ring) · error (danger border) | Every input has an associated `<label>`; error text programmatically linked. |
| **Card** | header / body / footer | — | The container surface (forms, the dashboard table). |
| **Table** | header + rows | — | The dashboard link list: Short link (mono) · Destination · Clicks (badge) · Created. |
| **Badge** | neutral / primary / success · pill | — | Click-count chip. |
| **Empty state** | icon + title + body + action | — | Dashboard with zero links. Carries a `data-testid="empty-state"` marker. |
| **App shell** | top nav (logo · nav · account) + content | — | Signed-in chrome. |

## In context — the dashboard

Compose the kit into the signed-in dashboard: the app shell, an "Your links" header with a
primary **Create link** action, and a Card-wrapped Table listing the user's links with a
click-count Badge per row. Provide the empty-state for a user with zero links. (Match the
"04 Dashboard" section of the uploaded canary.)

## Accessibility contract (WCAG 2.1 AA)

- Text and primary actions meet AA contrast (verify indigo-on-white and on-dark).
- Every interactive element has a visible focus ring (`--ring`, 3px).
- All form inputs have associated labels; error text is programmatically associated.
- Targets are comfortable (≥ 40px tall on primary actions).

## Output & self-audit

Produce one self-contained HTML page + a CSS file using CSS custom properties for all tokens
(mirror the uploaded `theme.css` variable names so the result drops into the app). Show every
primitive and the dashboard composition in light mode (dark-mode token set defined).

**Then run Surface A of the Design Audit** (uploaded `DESIGN-AUDIT-PROMPT.md`) — the
*visual / subjective* lenses you are best placed to judge because you render: **visual hierarchy
& polish, brand & voice, rendered responsive (~390px and ~1280px), and visual consistency vs the
uploaded canary**. Classify each finding **Blocker / Risk / Confirmed**, apply fixes, and **loop
to convergence** — terminate by **rule (a)** (a pass with B0+R0) or **rule (e)** plateau (3
consecutive passes, zero Blockers, total B+R ≤ 3, non-increasing). Report the per-pass
convergence trend and verdict; **do not finish with open Blockers**. (A separate **native
conformance gate — Surface B** — verifies token conformance, WCAG contrast, ARIA/semantics, focus
rings, and target sizes in source; **both** surfaces must converge for design sign-off.)
