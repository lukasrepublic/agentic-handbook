# Agentic Handbook — workspace template

A starter **workspace** for an agentic software project. Click **"Use this template"** to
create your project's workspace, then wire in the [**Agentic Foundry**](https://github.com/lukasrepublic/agentic-foundry)
plugin (the factory).

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

## Layout

```
specs/features/<product>/<domain>/<capability>/   atomic specs + acceptance-contract.yaml
specs/releases/ · specs/lifecycle/                release manifests + lifecycle views
context/                                          spec templates + the citation grammar + glossary
docs/architecture/                                architecture docs + ADRs
status-reports/                                   executive status reports
.claude/foundry-operators.json                    operator registry (the factory reads this)
CLAUDE.md · WORKFLOW.md                            workspace governance + the SDLC orchestration
```

## License

[MIT](LICENSE).
