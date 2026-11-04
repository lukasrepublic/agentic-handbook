# WORKFLOW — how work moves through this workspace

**The default path is one page: [`OPERATING-MODEL.md`](OPERATING-MODEL.md).** One artifact per
change — a ticket with a runnable `Done means` — and the platform (branch protection + required
CI checks) is the gate. Read that page first; this file is the map of where things live and
what the opt-in spec lane adds when the operator chooses it.

## The default loop (ticket lane)

```
 ticket (What / Why / Done means / Paper allowed)
   → branch from main → build → local-green (foundry-test.sh)
   → one draft PR → ready when Done means passes → one review pass
   → merge on green → deploy on promote (tag or label)
   → close the ticket with the Done-means output
```

Assignment of the ticket is the authorization. Nothing else is authored for the change unless the
ticket's `Paper allowed` names it.

## The opt-in spec lane

A spec is **chosen by the operator, never by the agent**, for `security: true` work or a design too
large for one ticket. Only then do the spec-lane verbs apply, and only to that spec:

```
 phase          what happens                                     the verb
 0 INTAKE       fuzzy input → discovery → atomic spec            /foundry:intake
 1 SPEC-REVIEW  one pass, three fresh-context lenses             /foundry:spec-review
 2 AUTHORIZE    the operator's merge of the spec to main         /foundry:authorize
 3 BUILD        the spec decomposes into tickets; each ticket    the ticket lane above
                follows the default loop
```

Security review (a separate context) is part of the floor on auth / secrets / custody /
supply-chain paths whether or not a spec exists.

## Git discipline

Canonical source: the plugin's `context/branch-discipline.md`, enforced by the git-discipline hook.
Treat a paraphrase anywhere else as stale. In short: one ticket, one branch, one PR, from `main`;
local-green before the first push; draft until `Done means` passes; deploy on promote, not on
merge; branch protection is the merge gate (required checks on, `strict` off, no `--admin`); clean up
only after `origin/main` contains the merge (`scripts/foundry-worktree-gc.py --apply`); docs do
not go through a code repo's pipeline.

## What lives where

| Artifact | Location |
|---|---|
| the ticket (the unit of work) | the forge's issue tracker — `What / Why / Done means / Paper allowed` |
| the PR + its checks | the code repo; one PR per ticket, draft until local-green |
| the record of done | the closed ticket, carrying the `Done means` output |
| the CI template for a code repo | [`templates/ci.yml`](templates/ci.yml) (skips drafts, cancels superseded runs, deploys on promote) |
| the weekly metrics line | stdout of `foundry-delivery-metrics.py` — paper:code, PRs merged, lead time; not a report |
| an opt-in spec | `specs/features/<product>/<domain>/<capability>/feat-*.md` |
| architecture / ADRs | `docs/architecture/` |
| the operator registry (standing authorization) | `.claude/foundry-operators.json` |
| the repo manifest (multi-repo) | `.claude/foundry-project.json` `repos{}` — see [`docs/control-plane.md`](docs/control-plane.md) |

## Single-repo vs multi-repo

- **Single repo:** tickets and code in one place; the workspace holds the governance files.
- **Multi-repo:** this workspace is the control plane; each code repo is a gitignored sibling
  declared in `.claude/foundry-project.json` `repos{}`, with its own branch protection and CI.
  Full pattern: [`docs/control-plane.md`](docs/control-plane.md).

## Unsure what to do next?

Read [`OPERATING-MODEL.md`](OPERATING-MODEL.md). If the ticket has a runnable `Done means`, build
until it passes. If it does not, the next step is writing one — not a document about the change.
