# Acme Links — Design System (brief)

> **The WHAT of the design system.** Authored in the workspace (dogfood), synced to the
> `claude.ai/design` project **"Acme Links — Design System"** via `DesignSync` / `/design-sync`,
> and first consumed by the Acme Links dashboard (`feat-handbook-acme-links-dashboard`). The
> token core is framework-agnostic (CSS custom properties) so it is reusable by any future
> app; the in-app styling layer wires the tokens through Tailwind v4 `@theme` + shadcn-style
> owned components.

## 1. Brand & voice

Acme Links is a small, trustworthy, modern link-shortener. The UI should feel **calm,
precise, and fast** — confident primary actions, generous whitespace, restrained color,
strong legibility. It is a *demo brand* (the "Acme" convention), so the system favors
clean conventions over novelty.

## 2. Foundations (tokens)

Tokens live as **CSS custom properties** (`theme.css`, `:root` + `[data-theme="dark"]`).
In-app they are projected through Tailwind v4 `@theme`.

- **Color**
  - *Primary* — Indigo: `--color-primary` `#4F46E5` (hover `#4338CA`, active `#3730A3`),
    on-primary `#FFFFFF`.
  - *Neutral* — Slate scale `--color-slate-50…900` (surfaces, text, borders).
  - *Semantic* — success `#059669` (emerald), danger `#DC2626` (red), warning `#D97706`
    (amber), info = primary.
  - *Surface roles* — `--color-bg`, `--color-surface`, `--color-surface-2`, `--color-border`,
    `--color-text`, `--color-text-muted` (re-mapped in dark mode).
- **Typography** — Inter (system-ui fallback). Modular scale: `xs 12 / sm 14 / base 16 /
  lg 18 / xl 20 / 2xl 24 / 3xl 30 / 4xl 36`. Weights 400/500/600/700. Line-heights tight
  for headings, 1.5 for body.
- **Spacing** — 4px base ramp: `1=4 2=8 3=12 4=16 5=20 6=24 8=32 10=40 12=48 16=64`.
- **Radius** — `sm 6 / md 8 / lg 12 / full 9999`.
- **Elevation** — `shadow-sm / shadow / shadow-md` (subtle, low-contrast).

## 3. Component inventory (the kit)

Owned, shadcn-style (Radix primitives in-app). Synced as preview cards (`@dsCard`).

| Component | Variants | Notes |
|---|---|---|
| **Button** | primary / secondary / ghost / danger · sizes sm/md/lg · disabled | Primary = the only filled action per view |
| **Input** | default / focus / error · with label + help/error text | Used in auth + create-link forms |
| **Card** | default / with header+footer | The dashboard's container surface |
| **Table** | header + rows · empty | The dashboard link list (slug · target · clicks · created) |
| **Badge** | neutral / primary / success · pill | Click-count chip |
| **Empty state** | icon + title + body + action | Dashboard with zero links (AC-DASH-4) |
| **App shell** | top nav + content | Signed-in chrome (logo, nav, account) |

## 4. Accessibility floor

- Contrast ≥ WCAG AA for text and primary actions (verify indigo-on-white / on-dark).
- Visible focus ring (`--ring`) on all interactive elements.
- All form inputs have associated labels; error text is programmatically linked.
- Dark mode is a first-class token set, not an afterthought.

## 5. Sync & consumption

- **Project:** `claude.ai/design` → "Acme Links — Design System" (created via
  `DesignSync create_project`; reused thereafter, synced one component at a time).
- **Local library:** `specs/features/acme-links/design/library/` (this dir) —
  `theme.css` + `foundations/*.html` + `components/*.html`, each preview marked with
  `<!-- @dsCard group="…" -->`.
- **In-app (downstream, `acme-links/src/design-system/`):** the same tokens as Tailwind v4
  `@theme` + shadcn-style React components; the dashboard atom imports them.

## Changelog

- v1.0 Draft — initial design brief + foundations; synced to Claude Design (step 3 of the tutorial).
