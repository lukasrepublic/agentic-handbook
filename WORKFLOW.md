# WORKFLOW — the agentic SDLC

How work moves through this workspace, phase by phase. The **phases are the factory's
verbs** (the Foundry plugin); this doc is the **orchestration + the artifact registry** —
what each phase consumes/produces and where it lives in the workspace.

## The pipeline

```
 phase            what happens                                   the verb / mechanism
 ─────            ────────────                                   ────────────────────
 0 INTAKE         fuzzy input → discovery → atomic spec          /foundry:intake
 1 SPEC-REVIEW    pre-lints + three fresh-context lenses,        /foundry:spec-review
                  one remediation round                          (mandatory; both-modes floor)
 2 AUTHORIZE      freeze + sign the acceptance contract;         /foundry:authorize ·
                  re-freeze a living, already-authorized spec    /foundry:amend
                  without an operator step unless it widens a
                  boundary. The **charter lane** — a one-page
                  Goal/AC/Done-when/Escalate-when unit, no
                  hash-freeze ceremony — is the DEFAULT lane
                  under `noninteractive`/`interactive` posture;
                  this factory lane is the non-default path for
                  a `factory`-mode release.                     (front gate; NO skip)
 3 SHAPE          bundle atoms into a release manifest           /foundry:release
 4 IMPLEMENT      build the atom against the frozen contract     /foundry:dispatch |
                  or charter. Autonomous drivers:                mode-interactive ·
                  `/foundry:mode-autonomous` drives one           /foundry:mode-autonomous ·
                  authorized release's atoms through              /foundry:command-deck
                  implementation now (per-wave fan-out);
                  `/foundry:command-deck` arms a recurring
                  watcher over a whole programme instead
                  (status|stop|restart|tick|prompt).
 5 FLOOR          your branch protection + CI admit the merge;   the merge floor ·
                  `/foundry:merge-when-green` replaces a         /foundry:merge-when-green
                  hand-rolled sleep-then-poll loop around one    (platform-enforced, honestly
                  PR's checks.                                   tiered; plugin docs/merge-floor.md)
 6 CERTIFY        deploy the release once, run every atom's      /foundry:certify-local
                  real journeys against that instance
 7 SIGN-OFF       the operator tests and accepts — a recorded    /foundry:release accept
                  practice note, never a machine gate
 8 CLOSEOUT       learnings + deploy observation                 /foundry:learn-distill ·
                                                                 /foundry:deploy-status
```

Two hard gates (**authorize**, **the floor**), one honest tail (**certify**, **sign-off**).
Phase 2 is the boundary between "intent" and "authorized instruction set" — nothing past it
is built without it.

## Git discipline — one worktree/branch per atom, one PR per release to `main`

Restated here from the plugin's `context/branch-discipline.md` (the canonical source — treat a
paraphrase found anywhere else, including an older copy of this section, as stale):

1. **One worktree, one branch, per atom** — `atom/<id>`, cut from the release's own
   `release/<version>` integration branch (created from `main` at `/foundry:intake`'s last
   step), never from `main` directly and never shared by two atoms.
2. **Local-green before the first push** — the atom's full local suite + `foundry-doctor.py`
   pass before the first `git push`; one push per atom, never a work-in-progress push.
3. **The atom's PR targets the release branch, not `main`** — `gh pr create --base
   release/<version>` whenever the release manifest names an `integration_branch`.
   `/foundry:merge-when-green` refuses a PR whose base is `main` in that case (remediation:
   `gh pr edit <n> --base release/<version>`).
4. **`main` receives ONE PR per release** — `release/<version>` → `main`, once every atom has
   landed on the release branch, so a per-merge deploy trigger on an adopter's app repo fires
   once per release, not once per atom. **Hotfixes are the one exception:** `hotfix/<id>` →
   `main` directly, stated in the hotfix PR's own body.
5. **Delete after `origin` contains the merge, never before** — a premature delete closes the
   PR instead of merging it. `git worktree remove`, then `git branch -d`, then `git push origin
   --delete <branch>`.
6. **The release branch itself is deleted the same way**, after its own PR to `main` merges and
   the release's tag exists.

The codified cleanup sweep for rules 5/6 is `scripts/foundry-worktree-gc.py --dry-run` (always
first — read-only) then `--apply` (deletes only the `merged` class, by real git ancestry). Full
detail + the worked adopter example: the plugin's `docs/how-to/branching-and-cleanup.md`.

## Artifact registry (what lives where)

| Phase | Artifact | Location (in this workspace) |
|---|---|---|
| 0 | atomic spec (human-readable) | `specs/features/<product>/<domain>/<capability>/feat-*.md` |
| 0–1 | LLM-friendly functional spec (AC-IDs, normative region) | same file (the `<!-- normative -->` region) |
| 1 | review evidence | `.foundry/` (runtime, gitignored) — the review is content-bound to the spec's hash |
| 2 | frozen acceptance contract | `…/acceptance-contract.yaml` (operator-signed `authorized:` block) |
| 3 | release manifest | `.foundry/releases/<id>/release.yaml` (`<id>` is an `[a-z0-9-]+` slug — the factory resolves this exact path; a manifest anywhere else is never found). Companions alongside it: `specs.txt`, `dependency-graph.md`, `release-notes.md`. Optional field `integration_branch` names the release's own branch (e.g. `release/1.16.0`) — consumed by `/foundry:merge-when-green`'s base-branch refusal and the cut-release R→R2→tag flow. |
| 3–4 | wave state (what one wave learned) | `.foundry/releases/<id>/state.yaml` — `decisions`/`artifacts`/`open_risks`/`amendments_needed` lists plus the optional scalar `next_action`, read FIRST by the next wave's `/foundry:intake` so it does not re-ask what is already known. `next_action` REPLACES on write, never accumulates; the four lists are merged, never overwritten. |
| 4 | the PR + its checks | the code repo (the PR body carries `Spec: <path>` — the spec-link) |
| 4 | build-provenance | in the **code repo** (`.foundry/build-provenance.yaml`, pins this workspace's commit) |
| 4 | per-atom done-when evidence | `.foundry/evidence/<atom>.json` — one `met` row per `done_when` locator (`{"locator", "status": "met", "evidence": "<captured output>", "at": "<UTC>"}`), written before an atom's task is marked complete; a team session's completion hook refuses a missing/stale/unmet record. |
| 4 | idle-nudge ledger | `.foundry/idle-nudges.jsonl` — caps at three keep-working nudges per atom before a command-deck tick surfaces a blocker instead of nudging a fourth time. |
| 6 | certification evidence | per-atom pass/fail from the journey runner's own output |
| 7 | the operator's acceptance | the release manifest (a practice note) |
| — | architecture / ADRs | `docs/architecture/` |
| 7–8 | learnings / status | `status-reports/`, the distill corpus |

> **Atoms are authorized per-atom — "authorize the release once" is not a thing.** Each atom carries
> its own frozen `acceptance-contract.yaml` from phase 2. `/foundry:authorize-release` records the
> operator go-ahead for shipping a *wave*; it is not a substitute for the per-atom freeze.

## The WHAT ladder (refinement of intent)

1. **Human-readable spec** — intent a human writes + reads (requirements, ACs in prose).
2. **LLM-friendly functional spec** — the same atom made deterministic: stable AC-IDs, a
   delimited normative region, design-asset citations — the precise *instruction set* for the agent.
3. **Frozen acceptance contract** — content-hashed observable checkpoints, operator-signed:
   the binding definition of done that certification verifies against the running app.

## Single-repo vs multi-repo

- **Single repo:** specs + code together; the contract sits beside the spec.
- **Multi-repo:** this workspace holds the specs/contracts; each code repo's
  `.foundry/build-provenance.yaml` pins the workspace commit it was authorized against.
  Hosted repos are **gitignored sibling subdirs** declared in `.claude/foundry-project.json`
  `repos{}`; the contract's `target_repo:` (hash-covered) names where the code lands. Full
  pattern: the plugin's `docs/how-to/multi-repo-control-plane.md`.

## Unsure what to do next?

Consult this file, then the factory's verb reference (the plugin's
`docs/VERBS-QUICK-REF.md`). The never-relaxed floor — front-authorization, the merge floor,
security review on sensitive surfaces, typed contracts + git discipline — holds in every
mode; ceremony above it scales with the work.
