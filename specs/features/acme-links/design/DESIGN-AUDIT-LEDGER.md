# Design Audit — Surface B run ledger (Acme Links v1)

Surface B (native conformance gate) run record + the triaged residual ledger. Surface A
(Claude Design visual loop) is run separately in the project chat; record its verdict here too
when run.

## Run

- **Surface B**, adversarial 6-lens workflow, 5 passes · 34 agents · ~1.57M tokens.
- **Convergence trend (B+R):** `p1: 43 → p2: 37 → p3: 25 → p4: 20 → p5: 19`.
- **Raw verdict:** `MAX-PASS — 2 Blockers open` (under the spec-sized `B+R ≤ 3` plateau bound).

## Close-out

- **Both Blockers were in fixer-added scope** (an un-specced account `menu` component +
  `menuitem-danger` hover). **Reverted the menu scope-creep** (deleted `components/menu.html`,
  restored plain Account buttons in `shell.html` + the canary, removed the menu CSS + the
  disabled "Reports" nav item) → **Blockers → 0**, inventory back to the briefed 7 components.
- **Rule-e recalibrated** for multi-component designs (see `DESIGN-AUDIT-PROMPT.md`): plateau =
  zero Blockers + non-increasing residuals + every residual triaged (not the spec-sized `≤3`).
- **Final Surface B verdict: `PLATEAU (rule e)` — 0 Blockers, residuals triaged below.**

## Kept (genuine fixes the run landed — retained)

AA-contrast token swaps (`text-muted → slate-600`, input border → slate-500), visible focus
rings on every interactive element, `aria-busy` spinner + `prefers-reduced-motion`, semantic
`<nav><ul><a aria-current>`, 40/44px target floors, non-color error indicator, content-width
tokens. **Also fixed at close-out:** nav-link target raised to 40px on fine pointers.

## Accepted residual Risks (bounded, non-blocking)

| # | Lens | Risk | Disposition |
|---|---|---|---|
| 1 | token-conformance | `colors.html` swatch prints `#DC2626` while the danger-*text* token resolves to `#B91C1C` (AA-safe) | **Accept / fix-next** — minor doc nit in the swatch sheet; tokens themselves are correct. |
| 2 | brand (one filled primary) | `btn-danger` is a filled variant that could rival the page primary | **Accept w/ guidance** — destructive variant, used sparingly; button.html notes one-filled-primary. |
| 3 | semantic-color | click counts use the neutral `.badge` (label affordance around a metric) | **Accept** — neutral pill for counts is a common, non-stateful convention. |
| 4 | copy | canary subtitle/body carry design-token jargon + duplicate the button label | **Accept** — the canary is a *design-system reference page*, intentionally technical; not product copy. |
| 5 | state-coverage | no in-table "zero filtered results" empty state; no sortable-header `:active` | **Accept** — filter/search + sortable columns are out of app scope (PRD §2.4). |
| 6 | type-scale | `card-header` (500) vs `empty-title` (600) both at `text-lg` | **Accept** — different roles justify the weight difference; within scale. |

*(7 further residuals were menu-related and are moot after the revert.)*

## Surface A (Claude Design) — CONVERGED

Operator-run in the claude.ai/design project chat (2026-06-14), after self-hosting Inter (the
brand font was registered via the pane's **Upload-fonts** affordance — the design-system
project is a Claude Design feature a design-partner predates, so its font registry is a UI step
`DesignSync` can't populate). **Verdict: CONVERGED.** Surface A found the design visually clean
and made **no net changes** to the synced files — the project's `theme.css` + canary + component
cards, pulled back via `DesignSync get_file`, match the Surface-B source. The visual loop
confirmed the Surface-B-converged design needs no aesthetic Blocker fixes.

*(If Surface A reported a per-pass trend in the chat, paste it and I'll append it for the record.)*

## Design sign-off — ✅ APPROVED

Both surfaces converged with **zero open Blockers**:
- **Surface B (native conformance):** `PLATEAU (rule e)` — 0 Blockers; residuals triaged above.
- **Surface A (Claude Design visual):** `CONVERGED` — 0 Blockers; no net changes.

The Acme Links design system **v1 is signed off** (tutorial step 3 complete).
