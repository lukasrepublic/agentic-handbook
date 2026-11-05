# WORKFLOW — how work moves through this workspace

**The working agreement is one page: [`OPERATING-MODEL.md`](OPERATING-MODEL.md).** GitHub owns
planning, and the platform (branch protection + required CI checks) is the gate. Read that page
first; this file is the map of where things live and what the opt-in spec lane adds when the
operator chooses it.

## The default loop (ticket lane)

```
 task (What / Why / Owner / Target repo key / Acceptance criteria / Done means / Context)
   → branch from main → build → local-green (foundry-test.sh)
   → one draft PR → ready when Done means passes → one review pass
   → merge on green → deploy on promote (tag or label)
   → accept and close with evidence, per Completion meanings in OPERATING-MODEL.md
```

States, ownership and what counts as done are defined in `OPERATING-MODEL.md` only. There is one
operating mode: a solo developer follows the same loop as a team, as a team of one. Each ticket also
carries `## Design`, `## Security` and `## Surfaces` sections
([Governance](OPERATING-MODEL.md#governance)).

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
| the task (the unit of work) | a GitHub issue from the task form — What / Why / Owner / Target repo key / Acceptance criteria / Done means / Context |
| the PR + its checks | the code repo; one PR per ticket, draft until local-green |
| the record of done | the issue closed as `completed` with the accepting actor and evidence linked (Completion meanings in `OPERATING-MODEL.md`); a passing Done-means run is verification, not acceptance |
| the governance (policy, lock, your own rules, exceptions, baselines) | `.foundry/operating-model.yaml`, `.foundry/governance.lock`, `governance/local/` — meaning in [Governance](OPERATING-MODEL.md#governance); how to set up in [`docs/guides/adopt-an-existing-codebase.md`](docs/guides/adopt-an-existing-codebase.md) |
| the shared message log (what sessions do, find and need; production changes) | the branch `foundry/messages` and one issue per topic — see [`docs/guides/join-an-existing-team.md`](docs/guides/join-an-existing-team.md) |
| the CI template for a code repo | [`templates/ci.yml`](templates/ci.yml) (skips drafts, cancels superseded runs, deploys on promote) |
| the weekly metrics line | stdout of `foundry-delivery-metrics.py` — paper:code, PRs merged, lead time; not a report |
| an opt-in spec | `specs/features/<product>/<domain>/<capability>/feat-*.md` |
| architecture / ADRs | `docs/architecture/` |
| the operator registry (login ↔ operator id) | `.claude/foundry-operators.json` |
| the repo manifest (multi-repo) | `.claude/foundry-project.json` `repos{}` — see [`docs/control-plane.md`](docs/control-plane.md) |

## Single-repo vs multi-repo

- **Single repo:** tickets and code in one place; the workspace holds the governance files.
- **Multi-repo:** this workspace is the control plane; each code repo is a gitignored sibling
  declared in `.claude/foundry-project.json` `repos{}`, with its own branch protection and CI.
  Full pattern: [`docs/control-plane.md`](docs/control-plane.md).

## Guides

[Start a project](docs/guides/start-a-new-project.md) ·
[adopt a codebase](docs/guides/adopt-an-existing-codebase.md) ·
[work each day](docs/guides/work-each-day.md) ·
[join a team](docs/guides/join-an-existing-team.md) ·
[upgrade](docs/guides/upgrade-and-migrate.md) ·
[diagnose and recover](docs/guides/diagnose-and-recover.md)

## Unsure what to do next?

Read [`OPERATING-MODEL.md`](OPERATING-MODEL.md).
