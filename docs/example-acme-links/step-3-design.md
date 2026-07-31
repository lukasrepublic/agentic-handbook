# Step 3 — Design the UI with Claude Design (the two-surface audit)

**Goal.** Build a small, reusable **design system** in Claude Design — tokens + components — and
sign it off with a formal audit *before* any screen is built on it. The dashboard (step 6) is its
first consumer.

## You run

```bash
# Create the design-system project + sync the local component library (incremental, one at a time)
/design-sync               # DesignSync: create_project "Acme Links — Design System" → push tokens + components
```

Then run the **two-surface design review** (the design-side peer of `/foundry:spec-review`) — see
[`DESIGN-AUDIT-PROMPT.md`](../../specs/features/acme-links/design/DESIGN-AUDIT-PROMPT.md):

- **Surface A — Claude Design (visual):** paste the Surface-A prompt into the project chat. It
  judges what must be *seen* — hierarchy, polish, brand/voice, rendered responsive — and loops to
  convergence (Blocker/Risk/Confirmed; rule-a or plateau).
- **Surface B — native conformance gate:** run the audit as a workflow over the source. It verifies
  what must be *proven* — token conformance, WCAG contrast, ARIA/semantics, target sizes — lands
  real diffs, and can screenshot the canary via the `chrome-devtools` MCP to *see* the result too.

## What to expect

- A `claude.ai/design` project holding the canary (`acme-links-design-system.html`), the token core
  (`theme.css`), and component cards (button, input, card, table, badge, empty-state, shell).
- Sign-off requires **both** surfaces to converge with **zero open Blockers**, recorded in
  [`DESIGN-AUDIT-LEDGER.md`](../../specs/features/acme-links/design/DESIGN-AUDIT-LEDGER.md).
- A real lesson: Surface B *will* catch the generator over-reaching (e.g. inventing an un-specced
  component) — that's the conformance gate doing its job.

> **Gotcha (brand font).** Claude Design's design-system project wants the brand font *self-hosted*
> in the project and registered via its **Upload-fonts** UI — a CDN `<link>` isn't enough, and
> `DesignSync` can't populate the font registry. Vendor the `.woff2` + `@font-face`, then upload
> the files through the pane.

**Next:** [Step 4 — authorize the acceptance contracts](step-4-authorize.md).
