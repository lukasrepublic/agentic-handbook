# Step 2 — Author specs + the spec review

**Goal.** Turn a plain-English idea into **atomic, machine-checkable specs** with frozen
acceptance contracts — then harden them with a fresh-context review before any code is written.

## You run

```bash
# Ingest the human-readable PRD → interactive discovery → atomic feat-*.md + acceptance-contract.yaml
/foundry:intake specs/features/acme-links/PRD.md
#   discovery resolves load-bearing decisions, e.g.:
#     slug scheme  → random base62, 7 chars, retry-on-collision
#     URL policy   → http/https only (reject javascript:/data:/file:)
#   → 4 vertical-slice atoms: auth · create-link · resolve-redirect · dashboard

# The single-pass review: deterministic pre-lints, then three fresh-context reviewer
# lenses (prior-art / steel-man+adversarial / per-AC rubric), one remediation round
/foundry:spec-review specs/features/acme-links/
```

## What to expect

- Four atoms, each a `feat-*.md` (stable AC-IDs in a delimited `<!-- normative -->` region) plus a
  sibling `acceptance-contract.yaml` whose **checkpoints** are the observable PASS criteria.
- The review reports categorized findings (Block / Risk / Nit). You remediate the Blocks and
  the Risks worth taking, in one round — a spec still contested after that is usually two
  atoms wearing one name; decompose it.

The crucial output is contracts that **witness real behavior, not just HTTP status**. For example,
the redirect checkpoint asserts `302` **and** `Location =` the exact target (a seeded canary) — so
a `200 'ok'` stub *or* a redirect to the wrong URL both fail.

Read the result: [`specs/features/acme-links/`](../../specs/features/acme-links/) — start with
[`resolve-redirect`](../../specs/features/acme-links/resolve-redirect/), the money-shot atom.

**Next:** [Step 3 — design the UI with Claude Design](step-3-design.md).
