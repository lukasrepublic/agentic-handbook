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
 2 AUTHORIZE      freeze + sign the acceptance contract          /foundry:authorize
                                                                 (front gate; NO skip)
 3 SHAPE          bundle atoms into a release manifest           /foundry:release
 4 IMPLEMENT      build the atom against the frozen contract     /foundry:dispatch |
                                                                 mode-interactive
 5 FLOOR          your branch protection + CI admit the merge    the merge floor
                                                                 (platform-enforced, honestly
                                                                 tiered; plugin docs/merge-floor.md)
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

## Artifact registry (what lives where)

| Phase | Artifact | Location (in this workspace) |
|---|---|---|
| 0 | atomic spec (human-readable) | `specs/features/<product>/<domain>/<capability>/feat-*.md` |
| 0–1 | LLM-friendly functional spec (AC-IDs, normative region) | same file (the `<!-- normative -->` region) |
| 1 | review evidence | `.foundry/` (runtime, gitignored) — the review is content-bound to the spec's hash |
| 2 | frozen acceptance contract | `…/acceptance-contract.yaml` (operator-signed `authorized:` block) |
| 3 | release manifest | `specs/releases/<…>/release.yaml` |
| — | lifecycle views (generated) | `specs/lifecycle/<state>/manifest.yaml` — never hand-edited |
| 4 | the PR + its checks | the code repo (the PR body carries `Spec: <path>` — the spec-link) |
| 4 | build-provenance | in the **code repo** (`.foundry/build-provenance.yaml`, pins this workspace's commit) |
| 6 | certification evidence | per-atom pass/fail from the journey runner's own output |
| 7 | the operator's acceptance | the release manifest (a practice note) |
| — | architecture / ADRs | `docs/architecture/` |
| 7–8 | learnings / status | `status-reports/`, the distill corpus |

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
  pattern: the plugin's `docs/how-to/multi-repo-control-center.md`.

## Unsure what to do next?

Consult this file, then the factory's verb reference (the plugin's
`docs/VERBS-QUICK-REF.md`). The never-relaxed floor — front-authorization, the merge floor,
security review on sensitive surfaces, typed contracts + git discipline — holds in every
mode; ceremony above it scales with the work.
