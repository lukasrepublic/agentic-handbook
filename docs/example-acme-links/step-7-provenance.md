# Step 7 — Provenance + the citation graph

**Goal.** Close the loop. Pin the merged code back to the exact authorized contracts, and
materialize the citation graph so you can ask "what cites this?".

## You run

```bash
# Each merged atom's PR carried its cross-repo pin, authored per the provenance
# convention the plugin documents — inspect it:
cat acme-links/.foundry/build-provenance.yaml

# Build the citation graph (materialized backlinks) + serve it via the foundry-graph MCP:
/foundry:report-citation-graph
```

## What to expect

`build-provenance.yaml` records, per atom, the cross-repo pin:

```yaml
authorizations:
  - spec_ref: specs/features/acme-links/resolve-redirect/feat-…-resolve-redirect.md
    foundry_authorized_against: agentic-workspace@<commit>
    spec_sha256:     <…>
    contract_sha256: <…>
    auth_seq: 1
  # dashboard carries auth_seq: 2, supersedes: <…>  — the step-6 reauth-after-impl correction
```

The citation graph answers queries like "**what cites the PRD?**" → all four atom specs (the
`[Doc: …PRD.md]` backlinks, materialized into an O(1) reverse index).

That's the WHAT ↔ HOW-built loop, closed: **frozen, authorized specs** ⇄ **merged, certified code**,
cross-repo-pinned and citation-indexed — checkable by anyone, instantly.

## Checkpoint

```bash
git checkout step-7   # provenance pinned; the flagship is complete
```

## You're done

You built a real app from an empty repo to a governed, live-proven merge — and the gate blocked a
broken seam, caught an over-specified contract, and drove a re-authorization along the way. That's
the framework working *as you'd use it on your own project*. The prompts you ran are all in
[`PROMPTS.md`](../../specs/features/acme-links/PROMPTS.md).
