# Adversarial Design Audit — the two-surface gate (formal step)

> **Standard.** A design is signed off only when it converges on **both** surfaces. The two
> are complementary, not redundant: Claude Design judges what must be **seen**; the native
> audit verifies what must be **proven in source**. Both share one protocol
> (Blocker/Risk/Confirmed, loop to convergence). This is the design-side peer of
> `/foundry:spec-review`.

## Surface A — Claude Design (the visual / subjective loop)

Run **in the claude.ai/design project chat**, during the generative iteration, against the
*rendered* design + the uploaded `acme-links-design-system.html` canary. Claude Design renders,
so it owns the lenses that need an eye:

- **A1 · Visual hierarchy & polish** — emphasis, balance, rhythm, density; does the screen read
  in the right order; is it elegant.
- **A2 · Brand & voice** — aesthetic restraint (one filled primary action; semantic color only
  for state); copy tone plain and direct, no jargon/marketing-plural.
- **A3 · Rendered responsive** — at ~390px and ~1280px the *rendered* layout holds: no visual
  overflow, awkward wrap, or broken composition.
- **A4 · Visual consistency vs canary** — the produced screens look like they belong to the
  uploaded baseline.

## Surface B — Native conformance gate (the committed, verifiable loop)

Run **here as a workflow** against the source files (`theme.css` + component/canary HTML).
Source-verifiable, deterministic, and it lands **real diffs in git**. Owns the lenses that must
be proven, not perceived:

- **B1 · Token conformance** — every color/spacing/radius/type value resolves to a `theme.css`
  token; no literal hex/px/rem outside the token definitions.
- **B2 · Accessibility-as-code (WCAG 2.1 AA)** — contrast computed from the actual tokens
  (≥4.5:1 text, ≥3:1 large/UI); visible focus ring on every interactive element; label↔control
  association; `aria-*` for state; semantic elements; target ≥40px (≥44px coarse-pointer);
  state not conveyed by color alone.
- **B3 · State coverage (in source)** — default/hover/focus/active/disabled/error/empty/loading
  defined where applicable.
- **B4 · Structural consistency** — spacing on the 4px ramp; radii/type-scale adherence; no
  structural drift across components.
- *(Optional)* render the canary via the `chrome-devtools` MCP and screenshot it, so the native
  gate also *sees* the result — narrowing the gap to Surface A.

## Shared protocol (both surfaces)

- Classify every finding **Blocker** (ships broken/inaccessible/off-brand-critical) /
  **Risk** (quality/consistency concern) / **Confirmed** (previously-raised, now resolved).
- **Loop**: each pass is a fresh adversarial sweep; apply fixes; recount. Report the per-pass
  convergence trend (`p1: B3+R5=8 → p2: B1+R3=4 → …`).
- **Terminate** by **rule (a)** (a pass with B0+R0) or **rule (e)** plateau. *Plateau is
  calibrated to the surface:* a single **spec** plateaus at total `B+R ≤ 3`, but a
  **multi-component design system** has a higher legitimate fixed point — its plateau is
  **zero Blockers** + residual Risks non-increasing across K=3 passes + **every residual
  explicitly triaged** (fixed, or accepted-with-rationale in a ledger). Never accept a plateau
  with open Blockers. Hard cap 5 passes (raise deliberately only to close out Blockers).
  *(Empirical note: the v1 Acme Links run plateaued at ~17 Risks under the spec-sized `≤3`
  bound — ~2 minor risks/component — which is why this calibration exists.)*
- **Never** finish a surface with open Blockers; never grind for a fake zero past plateau.

## Sign-off

Design is **APPROVED** only when **both** surfaces report `CONVERGED (rule a)` or
`PLATEAU (rule e)` with **zero open Blockers**. Record each surface's verdict + trend. Surface
B's converged diffs are committed; Surface A's converged design is synced back via DesignSync.
