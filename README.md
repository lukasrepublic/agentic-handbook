# Agentic Handbook — workspace template

A starter **workspace** for an agentic software project — and the **control plane** for however
many code repositories that project has. Start it with one command, in your own terminal:

```bash
npx create-agentic-workspace
```

That is **step 0**, and it runs *before* any Claude session — because it writes the permission
floor, and a Claude session may not write its own confinement. It previews every file and every
capability before writing a byte, then stops. Full sequence:
[**`docs/SETUP.md`**](docs/SETUP.md).

You can also click **"Use this template"** to start from this repo's contents — but that is the
*optional* route, and it does **not** give you the permission floor. Step 0 does, and step 0 can
seed a fresh workspace on its own.

Your specs live here. Your code lives in its own repos, hosted inside this one as gitignored
siblings, and the factory dispatches work into each — see [Layout](#layout--one-workspace-n-repos).

## The model: Workspace (WHAT) + Factory (HOW)

> **This workspace holds the _WHAT_ to build. The Foundry plugin determines _HOW_ it
> gets built. The plugin is wired _into_ this workspace.**

- **This repo (the workspace)** holds the **agentic SDLC artifacts** — the instruction
  set of *what* to build — plus the governance, corpus, and orchestration around it.
- **The Foundry plugin (the factory)** brings the *verbs*: the process + trust model +
  the honestly-tiered merge floor that turn that instruction set into merged code. Generic, versioned,
  shared — **wired into** this workspace.

Full model: the plugin's [`docs/architecture.md`](https://github.com/lukasrepublic/agentic-foundry/blob/main/docs/architecture.md).

## The WHAT ladder (what lives here)

Intent is progressively refined, in this workspace, into a machine-executable instruction set:

```
human-readable specs            ← intent (PRDs, user stories) — specs/features/.../feat-*.md
        │
LLM-friendly functional specs   ← deterministic atomic specs with stable AC-IDs + designs
   + designs
        │
frozen acceptance contracts     ← content-hashed, operator-signed — acceptance-contract.yaml
```

See the minimal worked example in
[`specs/features/example/api/ping/`](specs/features/example/api/ping/).

## Learn the loop — the Acme Links worked example

**Acme Links is the demo, not your project.** It is a small link shortener (accounts, a database,
a dashboard) built through the factory from an empty repo to a governed, live-proven merge, so the
loop is shown rather than asserted. The gate blocks a deliberately broken seam along the way,
which is what makes `status ≠ functional` visceral.

Two ways in — do it, or read what happened:

→ **[The 7-step tutorial](docs/example-acme-links/README.md)** — copy-along, each step a
`git checkout`-able checkpoint.
→ **[The build journey](docs/example-acme-links/BUILD-JOURNEY.md)** — the actual build log: every
command and prompt, the three security Blocks caught before merge, and the defects that reading
missed and running found.

The example's specs live in [`specs/features/acme-links/`](specs/features/acme-links/), every
prompt is in [`PROMPTS.md`](specs/features/acme-links/PROMPTS.md), and its code is a separate repo:
[`lukasrepublic/acme-links`](https://github.com/lukasrepublic/acme-links).

Everything under `docs/example-acme-links/` and `specs/features/acme-links/` is the demo; delete
both when you no longer need them. What is *yours* is described in
[`docs/README.md`](docs/README.md).

## Setup

> Full file-by-file anatomy of an initialized workspace + the complete runbook:
> **[`docs/SETUP.md`](docs/SETUP.md)**. The short version:

**In your own terminal, before any session:**

0. **Write the permission floor and seed the workspace:**
   ```bash
   npx create-agentic-workspace
   cd <project>-handbook
   ```
   This is the only step that cannot happen inside a Claude session — it writes
   `.claude/settings.json`, and a model editing its own confinement is refused. It also wires the
   git commit identity and scaffolds the workspace seed.

1. **Install the factory** (the Foundry plugin) — **pinned to a release tag.** An unpinned
   `marketplace add` resolves the default branch, which is a moving target:
   ```bash
   claude plugin marketplace add lukasrepublic/agentic-foundry#v1.2.1
   claude plugin install foundry@agentic-foundry
   ```

**Then open the session** (`claude`) and accept the trust dialog — it lists exactly the `allow`
rules step 0 declared. Declaring is not granting; accepting the dialog is what grants them.

2. **Register operators:** edit `.claude/foundry-operators.json` (replace `op_example`).
3. **Declare your boot recipe** (how certification deploys the release once, locally)
   and apply branch protection — see `/foundry:init` and the plugin's `docs/merge-floor.md`.
4. **Verify the wiring:** `/foundry:doctor` → `DOCTOR-GREEN`.

## The loop

```
/foundry:intake → /foundry:spec-review → /foundry:authorize → /foundry:dispatch
      → the merge floor (your CI + branch protection) → /foundry:certify-local → your sign-off
```

Two hard gates (authorize, the floor), one honest tail (certify, sign-off). The full
orchestration + artifact registry: [`WORKFLOW.md`](WORKFLOW.md).

## Layout — one workspace, N repos

**This workspace is a control plane.** Your specs live here; your *code* lives in its own
repositories, which sit inside this tree as **gitignored siblings** — each one an independent git
repo with its own history, PRs, CI and merge floor. The factory dispatches work *into* them.

```
<project>-handbook/                      ◀── git repo #1 — the workspace. YOU commit this one.
│
├── CLAUDE.md · WORKFLOW.md                  governance + the SDLC pipeline
├── .claude/
│   ├── settings.json                        the wiring (enabledPlugins → the factory)
│   ├── foundry-operators.json               who is allowed to authorize
│   └── foundry-project.json   ◀── THE MANIFEST. repos{} maps a dispatch key → a path below.
├── specs/
│   ├── features/<product>/…                 the WHAT: feat-*.md + acceptance-contract.yaml
│   └── lifecycle/                           generated lifecycle views (never hand-edited)
├── .foundry/releases/<id>/release.yaml      the authoritative release manifest
├── docs/ · status-reports/ · context/
├── .gitignore                 ◀── every hosted repo below is listed here, root-anchored (/api/)
│
├── api/                                 ◀── git repo #2 — GITIGNORED. Not a submodule.
│   ├── .git/                                its own history, branches, PRs, CI, merge floor
│   ├── src/…                                the HOW-built: your application code
│   └── .foundry/build-provenance.yaml       pins the repo-#1 commit that authorized this atom
│
└── infra/                               ◀── git repo #3 — GITIGNORED. Same deal.
    ├── .git/
    └── terraform/… or k8s/…
```

Three git repositories, one directory tree. The boundaries are the point:

- **`git status` here never shows anything from `api/` or `infra/`** — root-anchored gitignore
  entries, so the control plane cannot accidentally commit your app.
- **Each hosted repo keeps a fully independent history.** No submodule pointer, no entangled
  histories, no `git submodule update`.
- **The link runs the other way.** Each built atom writes `.foundry/build-provenance.yaml` *in the
  code repo*, pinning the workspace commit whose frozen contract authorized it — traceability
  without coupling.
- **The factory is not in this tree.** The plugin installs under `~/.claude/plugins/…`; upgrading
  it touches nothing above.

A spec reaches a repo by naming its manifest key:

```
   acceptance-contract.yaml            .claude/foundry-project.json          on disk
   ───────────────────────             ───────────────────────────          ───────
   target_repo: api          ─────►    repos.api.path = "api"        ─────►   ./api/
```

**Starting with one repo?** That is the default — a fresh template seeds only the `workspace`
self-entry, and a contract with no `target_repo` is workspace-targeted. Nothing to configure
until you add a second repo.

> **Running more than one repo? Read [`docs/control-plane.md`](docs/control-plane.md) first.**
> It is the guide to operating this workspace as a control plane: the on-disk layout, the
> **session rule** (always start Claude Code at this root, never inside a hosted repo — and what
> silently breaks if you don't), the add-a-repo runbook, and day-two operations. The
> add-a-repo mechanics alone are in
> [`docs/SETUP.md`](docs/SETUP.md#multi-repo-control-plane--hosting-your-code-repos).

## License

[MIT](LICENSE).
