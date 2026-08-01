# Agentic Handbook — workspace template

A starter **workspace** for an agentic software project — and the **control plane** for however
many code repositories that project has. Click **"Use this template"** to create your project's
workspace, then wire in the [**Agentic Foundry**](https://github.com/lukasrepublic/agentic-foundry)
plugin (the factory).

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

## Setup (after "Use this template")

> Full file-by-file anatomy of an initialized workspace + the complete runbook:
> **[`docs/SETUP.md`](docs/SETUP.md)**. The short version:

1. **Install the factory** (the Foundry plugin):
   ```bash
   claude plugin marketplace add lukasrepublic/agentic-foundry
   claude plugin install foundry@agentic-foundry
   ```
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
│   └── releases/ · lifecycle/               release manifests + generated lifecycle views
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
self-entry, a contract with no `target_repo` is workspace-targeted, and `/foundry:doctor` stays
green. Add hosted repos when you have them: **[`docs/SETUP.md` → Multi-repo control plane](docs/SETUP.md#multi-repo-control-plane--hosting-your-code-repos)**.

## License

[MIT](LICENSE).
