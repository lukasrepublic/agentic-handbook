# Agentic workspace

Project-wide context loaded by every Claude Code session in this workspace. This repo is
the **workspace** — it holds the *WHAT* to build (the agentic SDLC artifacts) + the
governance around it. The **factory** (the *HOW*) is the **Agentic Foundry plugin**, wired
in here; the SDLC orchestration lives in `WORKFLOW.md`.

> Replace this section with your project's one-paragraph description (what it is, who it's
> for, the business model). Everything below is the reusable governance scaffold.

## Workspace ⟷ factory (the wiring)

- The factory is the `foundry` plugin (`lukasrepublic/agentic-foundry`), installed +
  wired into this workspace (plugin load + hooks + MCP). Its verbs are `/foundry:*`.
- The plugin's scripts read THIS workspace's corpus via `CLAUDE_PROJECT_DIR`
  (the specs, `.claude/foundry-operators.json`, the citation graph); the plugin's own
  files resolve via `${CLAUDE_PLUGIN_ROOT}`.
- `/foundry:doctor` must be `DOCTOR-GREEN` — it verifies the wiring is intact.

## Stage mode

**Operator-flipped governance posture.** Engineering provides the mechanism + the
relaxed-vs-strict rule sets; the operator declares which mode is active.

**Current mode:** `lean`

To change, edit the line above to `lean` or `scale` and commit. `lean` favors the direct
loop + lighter ceremony; `scale` enforces the full gates (deeper review, mandatory
architecture sign-off, enforcement-grade anti-patterns). Read the line per invocation.

### The both-modes floor (never relaxed by mode)

1. **Front-authorization** — an un-authorized spec never reaches `main` (no skip).
2. **The merge floor** — the platform's own enforcement (branch protection + required CI
   checks), honestly tiered; certification against the running release before acceptance.
3. **Security review** on auth / PII / payments / secrets / external-API surfaces.
4. **Typed contracts** at boundaries; **git discipline** (no force-push to `main`, PR-then-merge).

## Multi-repo control center (hosting infra + service repos)

This workspace can act as a **control center** that hosts the project's other repos — its
infrastructure (IaC) repo, service repos, any number of them — as **independent, gitignored
sibling subdirs** (the **meta-repo** pattern: gitignored siblings + a manifest, *not* git
submodules). The manifest is `.claude/foundry-project.json` `repos{}`: each hosted repo is one
entry keyed by a **`target_repo` dispatch key**, into which the factory dispatches workers (a
worker is redirected into the hosted repo's working tree; its merge floor is that repo's own).

- **Single-repo by default.** A fresh workspace seeds only the `workspace` self-entry → the
  doctor treats it as a single-repo adopter. You stay `DOCTOR-GREEN` until you add a hosted repo.
- **Add a hosted repo** when you clone one in — clone into the gitignored subdir, add its
  `repos.<key>` entry (`path`/`kind`/`role`), and dispatch by that key. Step-by-step:
  [`docs/SETUP.md`](docs/SETUP.md) → *Multi-repo control center*.
- **Why siblings, not submodules:** each hosted repo keeps a fully independent history; the
  control center is never coupled to a submodule commit pointer. (Rationale in SETUP.md.)

## Conventions

- **Specs** are atomic: `specs/features/<product>/<domain>/<capability>/feat-<…>.md`, each
  with stable AC-IDs + a delimited `<!-- normative -->` region (so the spec hash excludes
  cosmetic edits) + a sibling `acceptance-contract.yaml`. Templates ship with the foundry plugin
  (its `context/` kit — the canonical source; see `context/README.md`), not the workspace.
- **Citation grammar** — the `[Doc:]`/`[Atom:]` forms; the grammar ships in the foundry plugin's kit.
- **Releases** — `specs/releases/<…>/release.yaml` is the authoritative manifest; lifecycle
  views under `specs/lifecycle/` are generated, never hand-edited.
- **Git discipline** — branch per atom; PR-then-merge; the merge floor admits the merge.

## Implementation-merge autonomy (per-session)

A second axis governs how an implementation PR reaches `main`: **Regular** (operator
reviews the diff at the merge — the default) vs **Lean** (a separate-context reviewer +
auto-merge on a clean gate). Engaging Lean is the operator's segregation grant.

## Memory discipline (MEMORY.md index + load-limit)

Memory is a native Anthropic substrate — this is *convention*, not a bespoke store. Keep the
native memory healthy with three rules so recall does not silently degrade as the workspace
accumulates:

- **MEMORY.md is an index, not a store.** Keep **one short hook line per atom** in MEMORY.md;
  the full detail + `[[links]]` live in the atom's own topic file. Lines that cram full content
  bloat the index and crowd out other atoms.
- **Stay under the load limit.** MEMORY.md is loaded into context each session; an **over-limit
  file silently partial-loads** (it does not error) — the tail is dropped and recall quietly
  degrades. Keep MEMORY.md under the context **load limit**; when it approaches, prune hooks to
  their topic files rather than letting the index grow unbounded.
- **One line per atom — no orphans.** Every atom file has **exactly one index line** in
  MEMORY.md. An atom with no index line is invisible to recall even though its file exists; an
  atom with several index lines wastes the budget. Audit periodically: atoms ↔ index lines is a
  bijection.

## Not in this workspace

- Do not commit secrets or cloned product repos into the workspace.
- The factory machinery lives in the plugin, not here — don't re-implement `/foundry:*`
  verbs in the workspace; wire in the plugin.
