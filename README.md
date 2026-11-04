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

Your governance lives here. Your code lives in its own repos, hosted inside this one as gitignored
siblings — see [Layout](#layout--one-workspace-n-repos).

## The operating model — one page

> **One artifact per change: a ticket with a runnable "Done means". The platform is the gate.**

The whole model is [**`OPERATING-MODEL.md`**](OPERATING-MODEL.md): the ticket template, the loop
(branch → build → local-green → one draft PR → merge on green → deploy on promote → close with
the check's output), the floor that never relaxes, what is deliberately absent, and when a spec is
still used (operator-chosen: `security: true`, or a design too large for one ticket).

- **This repo (the workspace)** holds the governance: the operator registry, the repo manifest,
  the CI template, and the opt-in specs when the operator asks for one.
- **The Foundry plugin (the factory)** brings the tooling that makes the model hold without
  ceremony: `foundry-ticket.py`, `foundry-test.sh` (local-green before push), the paper guard, the
  Stop hook that runs `Done means`, the git-discipline hook, and the security-review lane.

Full plugin model: the plugin's [`docs/architecture.md`](https://github.com/lukasrepublic/agentic-foundry/blob/main/docs/architecture.md).

## Learn the spec lane — the Acme Links worked example

**Acme Links is the demo, not your project.** It is a small link shortener (accounts, a database,
a dashboard) built from an empty repo to a live-proven merge, so the loop is shown rather than
asserted. It exercises the **opt-in spec lane** end to end (the app has auth, so the operator chose
specs); your day-to-day changes take the ticket lane in `OPERATING-MODEL.md` instead. The gate
blocks a deliberately broken seam along the way, which is what makes `status ≠ functional` visceral.

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

1. **Install the factory** (the Foundry plugin):
   ```bash
   claude plugin install foundry@agentic-foundry
   ```
   > **You do not add the marketplace by hand, and this page names no version on purpose.**
   > Step 0 already declared the marketplace in `.claude/settings.json`, **pinned to an exact
   > release** with `autoUpdate: false`. That pin travels with the published CLI — a release bumps
   > the plugin, the CLI's own version moves with it (enforced, not remembered), and `npx` resolves
   > the current one. The version therefore lives in the artifact, not in this prose, which is why
   > this page cannot go stale the way it did three releases running.
   >
   > Adopting into a workspace that already exists, so step 0 did not run? Then you do need the
   > add, and it is in [`docs/SETUP.md`](docs/SETUP.md) — also unpinned, for the same reason:
   > `claude plugin install` resolves the current release on its own.
   >
   > Already wired in from an earlier release? `npx update-agentic-workspace`, run from inside
   > the workspace, brings the marketplace, the plugin, and the managed-file floor current in
   > one command — see [`docs/SETUP.md`](docs/SETUP.md).

**Then open the session** (`claude`) and accept the trust dialog — it lists exactly the `allow`
rules step 0 declared. Declaring is not granting; accepting the dialog is what grants them.

2. **Register operators:** edit `.claude/foundry-operators.json` (replace `op_example`; the
   standing authorization recorded there is what makes ticket assignment the authorization).
3. **Apply branch protection** on each code repo's `main` (required checks on, no force-push) and
   copy [`templates/ci.yml`](templates/ci.yml) into it — see `/foundry:init` and the plugin's
   `docs/merge-floor.md`.
4. **Verify the wiring:** `/foundry:doctor` → `DOCTOR-GREEN`.

## The loop

```
ticket → branch → build → local-green → one draft PR → ready when Done means passes
      → one review pass → merge on green → deploy on promote → close with the Done-means output
```

One gate (branch protection + CI), one check (`Done means`), one operator walkthrough per release.
The one-page model: [`OPERATING-MODEL.md`](OPERATING-MODEL.md); where things live: [`WORKFLOW.md`](WORKFLOW.md).

## Layout — one workspace, N repos

**This workspace is a control plane.** Your specs live here; your *code* lives in its own
repositories, which sit inside this tree as **gitignored siblings** — each one an independent git
repo with its own history, PRs, CI and merge floor. The factory dispatches work *into* them.

```
<project>-handbook/                      ◀── git repo #1 — the workspace. YOU commit this one.
│
├── OPERATING-MODEL.md · WORKFLOW.md         the one-page model + where things live
├── CLAUDE.md                                governance loaded into every session
├── .claude/
│   ├── settings.json                        the wiring (enabledPlugins → the factory)
│   ├── foundry-operators.json               the operators and their standing authorization
│   └── foundry-project.json   ◀── THE MANIFEST. repos{} maps a dispatch key → a path below.
├── templates/ci.yml                         the CI template each code repo copies
├── specs/features/<product>/…               opt-in specs (operator-chosen; security or large design)
├── docs/
├── .gitignore                 ◀── every hosted repo below is listed here, root-anchored (/api/)
│
├── api/                                 ◀── git repo #2 — GITIGNORED. Not a submodule.
│   ├── .git/                                its own history, branches, PRs, CI, branch protection
│   └── src/…                                your application code
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
- **The record of a change is its closed ticket** (with the `Done means` output) and the merged
  PR in the code repo — traceability without a file to keep in sync.
- **The factory is not in this tree.** The plugin installs under `~/.claude/plugins/…`; upgrading
  it touches nothing above.

A ticket reaches a repo by naming its manifest key:

```
   the ticket                          .claude/foundry-project.json          on disk
   ──────────                          ───────────────────────────          ───────
   repo: api                 ─────►    repos.api.path = "api"        ─────►   ./api/
```

**Starting with one repo?** That is the default — a fresh template seeds only the `workspace`
self-entry, and a ticket that names no repo is workspace-targeted. Nothing to configure until you
add a second repo.

> **Running more than one repo? Read [`docs/control-plane.md`](docs/control-plane.md) first.**
> It is the guide to operating this workspace as a control plane: the on-disk layout, the
> **session rule** (always start Claude Code at this root, never inside a hosted repo — and what
> silently breaks if you don't), the add-a-repo runbook, and day-two operations. The
> add-a-repo mechanics alone are in
> [`docs/SETUP.md`](docs/SETUP.md#multi-repo-control-plane--hosting-your-code-repos).

## License

[MIT](LICENSE).
