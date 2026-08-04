# The control plane — running a project made of several repositories

Most real projects are not one repository. They are an app, a service or two, and the
infrastructure that runs them — each with its own history, its own CI, its own release cadence.

This workspace is the **control plane** for that. Your specifications live here. Your code lives
in its own repositories, hosted inside this tree as gitignored siblings. The factory reads the
specs from here and dispatches work *into* each code repo, where that repo's own merge floor
decides what lands.

> **The one rule that trips everyone up:** you run Claude from **this** directory, never from
> inside a hosted repo. [Why, and what breaks if you don't →](#the-session-rule-always-start-from-the-control-plane)

---

## 1. What it looks like on disk

**Three git repositories, one directory tree:**

```
acme-handbook/                           ◀── git repo #1 — the control plane. YOU commit this.
│
├── CLAUDE.md · WORKFLOW.md                  governance + the SDLC pipeline
├── .claude/
│   ├── settings.json                        the wiring: enabledPlugins → the factory
│   ├── foundry-operators.json               who is allowed to authorize
│   └── foundry-project.json   ◀── THE MANIFEST. repos{} maps a dispatch key → a path below.
├── specs/
│   └── features/<product>/…                 the WHAT: feat-*.md + acceptance-contract.yaml
├── docs/ · status-reports/
├── .gitignore                 ◀── every hosted repo below is listed here, root-anchored
│
├── api/                                 ◀── git repo #2 — GITIGNORED. Not a submodule.
│   ├── .git/                                its own history, branches, PRs, CI, merge floor
│   ├── src/…                                the HOW-built
│   └── .foundry/build-provenance.yaml       pins the repo-#1 commit that authorized each atom
│
├── web/                                 ◀── git repo #3 — GITIGNORED.
│   └── .git/ · src/…
│
└── infra/                               ◀── git repo #4 — GITIGNORED.
    └── .git/ · terraform/…
```

The boundaries are the whole design:

| | |
|---|---|
| **`git status` here never shows your code** | Hosted repos are root-anchored gitignore entries. The control plane cannot accidentally commit your app. |
| **Each repo keeps an independent history** | No submodule pointer, no `git submodule update`, no entangled histories. Clone one on its own and it is a completely normal repo. |
| **The link runs code → specs, not specs → code** | Each built atom writes `.foundry/build-provenance.yaml` *in the code repo*, pinning the control-plane commit whose frozen contract authorized it. Traceability without coupling. |
| **The factory is not in this tree** | The plugin installs under `~/.claude/plugins/…` and resolves via `${CLAUDE_PLUGIN_ROOT}`. Upgrading it changes nothing above. |

### Why gitignored siblings instead of git submodules

Submodules pin the parent to a specific child commit, need explicit `git submodule update`, and
entangle the histories. For a hub of genuinely independent repos that is the wrong coupling —
you would be committing a pointer bump in the control plane every time any service moved. The
lightweight **meta-repo** convention (independent clones named by a manifest) keeps each repo's
history entirely its own, and the manifest is a file you already have.

---

## 2. The session rule: always start from the control plane

**Open Claude Code in the control-plane directory. Not in `api/`. Not in `infra/`. Ever.**

```bash
cd ~/work/acme-handbook     # ✅ the control plane — the factory is live here
claude

cd ~/work/acme-handbook/api # ❌ a hosted repo — you get a plain session with no factory
claude
```

This is not style. Claude Code resolves everything from the session's project directory
(`CLAUDE_PROJECT_DIR`, falling back to the working directory), and every piece of the factory
lives at the control-plane root:

| What the factory needs | Where it lives | If you start in `api/` |
|---|---|---|
| Operator registry | `.claude/foundry-operators.json` | **Missing** → authorization fails closed; nothing can be frozen. |
| The repo manifest | `.claude/foundry-project.json` → `repos{}` | **Missing** → `target_repo` resolves to nothing; dispatch has no venue. |
| Your specs + contracts | `specs/features/…` | **Not there** — the code repo holds code, not the WHAT. |
| Workspace governance + hooks | `CLAUDE.md`, `.claude/hooks/` | **Not applied** — your workspace's own guards do not fire. |

**Whether the `/foundry:*` verbs themselves appear depends on where the plugin was enabled**, and
both outcomes are bad in different ways:

- **Enabled per-project** (`<the control plane>/.claude/settings.json`): the plugin does not load
  in `api/` at all. No verbs. The session fails by *absence* — nothing errors, the commands are
  simply missing.
- **Enabled user-wide** (`~/.claude/settings.json`, which is where `claude plugin install` puts it
  by default): the verbs **do** load in `api/` — pointed at the wrong root. This is the more
  dangerous case, because the factory *looks* available while the corpus, the operator registry
  and the manifest it governs are all absent. You can start working and discover nothing was
  governed.

Either way, a session started inside a hosted repo is not "the factory with a narrower view." It is
a session **with none of your governance**, and it will let an agent write code that no frozen
contract authorized.

> **Nothing detects this today.** A preflight check is specified
> (`feat-foundry-control-plane-preflight`) and will convict the user-wide case, where the doctor is
> reachable. Until it ships, the rule above is the only defence.

**You still work on code in the hosted repos** — the factory dispatches workers into those
working trees for you, and each repo's own PR and merge floor govern what lands. You just drive
it all from one session, at the top.

### The everyday shape

```
  one Claude session, opened at the control plane
        │
        ├── read/write specs           →  ./specs/…                (repo #1, you commit)
        ├── /foundry:authorize         →  freezes a contract       (repo #1, PR + merge)
        ├── /foundry:dispatch          →  worker enters ./api/     (repo #2, its own branch)
        │                                 …or ./infra/            (repo #4)
        └── each PR faces THAT repo's merge floor, not this one's
```

---

## 3. Setting up a multi-repo project, step by step

Starting from nothing. Substitute your own names throughout.

### Step 1 — create the control plane

```bash
# GitHub UI → "Use this template" on agentic-handbook → acme-handbook
git clone git@github.com:<you>/acme-handbook.git
cd acme-handbook
```

Everything from here happens **in this directory**.

### Step 2 — install the factory and declare yourself

```bash
claude plugin marketplace add lukasrepublic/agentic-foundry#v1.2.0
claude plugin install foundry@agentic-foundry
```

Edit `.claude/foundry-operators.json` — replace the example with your real id. This is
load-bearing, not paperwork: every frozen contract names an `operator_id`, and the freeze
fail-closes if the id does not resolve here.

```json
{
  "schema_version": 1,
  "operators": {
    "op_you": { "name": "Your Name", "github": "your-handle", "added_at": "2026-07-31" }
  }
}
```

Commit it — it must resolve at the pinned commit, by anyone, later.

### Step 3 — confirm the wiring before adding anything

```bash
claude          # from acme-handbook/
/foundry:doctor # → DOCTOR-GREEN
```

A fresh template is **single-repo**: the seeded `repos{}` has only the `workspace` self-entry, and
that is a valid, green state.

**Do not add manifest entries for repos you have not cloned yet.** A dangling entry is not caught
by anything today — the doctor's five checks do not read `repos{}` — and it does not fail loudly
later either: it makes `/foundry:authorize` skip five of its grounding floors with a printed
warning and freeze the contract anyway (§4). A check that convicts a dangling entry is queued as
`feat-foundry-control-plane-preflight`; until it ships, adding entries only for repos that exist
is the defence.

### Step 4 — bring in your first code repo

Two edits and a clone, in this order.

**(a) Gitignore it first**, root-anchored, so the control plane can never track it:

```gitignore
# ── hosted repos (independent git repos; the control plane never tracks them) ──
/api/
```

**(b) Clone it into that path:**

```bash
git clone git@github.com:<you>/acme-api.git api
```

**(c) Register it** in `.claude/foundry-project.json`. The key is the **dispatch key** a contract
will name:

```jsonc
"repos": {
  "workspace": { "path": ".",    "kind": "workspace",  "role": "the control plane" },
  "api":       { "path": "api",  "kind": "single-app", "package_manager": "npm",
                 "boot_command": "make dev", "ci_install": "npm ci",
                 "datastores": ["postgres"] }
}
```

`boot_command` is **declarative metadata today** — it records how this repo is booted, and the
schema accepts it, but no shipped code reads it. The recipe `/foundry:certify-local` actually
boots comes from the **active stack profile's** `app_exercise_binding.boot`, not from here. Record
it anyway so the manifest documents the repo honestly, but do not expect it to drive anything.

```bash
/foundry:doctor   # → DOCTOR-GREEN, now as a multi-repo control plane
```

### Step 5 — repeat for every other repo

```gitignore
/web/
/infra/
```

```bash
git clone git@github.com:<you>/acme-web.git   web
git clone git@github.com:<you>/acme-infra.git infra
```

```jsonc
"web":   { "path": "web",   "kind": "single-app", "boot_command": "npm run dev" },
"infra": { "path": "infra", "kind": "infra-repo", "role": "OpenTofu + Kubernetes" }
```

Re-run `/foundry:doctor` after each. Registering repos one at a time means a typo is obvious
immediately rather than three repos later.

### Step 6 — give each code repo a merge floor

The control plane does **not** enforce your code repos' merges — each repo does, with its own CI
and branch protection. Per repo:

1. A CI workflow that builds and runs the contract journeys.
2. Branch protection on `main` requiring that check, with force-pushes and deletions off.
3. Confirm the required check name matches the job's reported context **exactly** — a required
   check that never reports blocks every merge permanently.

Tier each repo honestly; a protected control plane confers nothing on an unprotected service repo.

---

## 4. Shipping your first atom across two repos

The loop, with the multi-repo parts called out. All of it from the one session at the top.

```
/foundry:intake            state the capability in prose → an atomic spec + contract
/foundry:spec-review       three fresh-context lenses → one remediation round
        │
        │   ← you now edit the contract to name its venue:
        │       target_repo: api
        │       scope.allowed_paths: ["src/routes/**", "src/db/**"]
        ▼
/foundry:authorize         the operator signs; spec_sha256 + contract_sha256 freeze
        │                  (this is a PR in the CONTROL PLANE; merging it IS the authorization)
        ▼
/foundry:dispatch          a worker enters ./api/, on its own branch, confined to allowed_paths
        ▼
   the api repo's merge floor    build + the contract journeys against the RUNNING app
        │                        red → the merge is refused. That is the point.
        ▼
   merge in ./api/          the PR carries .foundry/build-provenance.yaml pinning this
                            control plane's commit — the cross-repo audit trail
```

Two rules that keep this honest:

- **One atom, one target repo.** A change spanning `api` and `infra` is *two* atoms with an
  explicit dependency, not one atom with two venues. It keeps each scope groundable and each
  merge floor meaningful.
- **`scope.allowed_paths` grounds against the target repo**, not the control plane. The two ways
  to get this wrong fail in **opposite** directions, which is worth knowing before it happens:
  - **`target_repo` absent** → the paths ground against the control plane, where `src/` does not
    exist, so the scope matches nothing — and a scope that matches nothing constrains nothing.
    Authorization **refuses this, by design**: *"matches ZERO paths under the venue root"*.
  - **`target_repo` present but unresolvable** (misspelled, or not cloned) → there is no venue
    root to ground against, so authorization **degrades rather than refuses**. Five floors —
    surface⊆scope, doctor-row baseline, system-grounding, `allowed_paths` grounding, and
    checkpoint-locator grounding — each print a `warn: … degraded` / `SKIPPED` line and are
    skipped, and the contract still freezes and still increments `auth_seq`.

  The rationale for the second is sound (never wedge a freeze on a checkout you simply have not
  made yet), but it means **a typo and a not-yet-cloned repo look identical**. Read the `warn:`
  lines in the authorize dry-run before you confirm; an unexpected degrade is a manifest defect.

---

## 5. Day-two operations

**Adding a repo later** — same three moves as Step 4, in the same order: gitignore, clone,
register, then `/foundry:doctor`.

**Removing one** — delete the `repos{}` entry, remove the gitignore line, delete the directory.
Specs that named it stay valid history; they simply cannot be dispatched until the key resolves
again.

**Going from single-repo to multi-repo** — nothing to migrate. Add the first hosted repo and
existing workspace-targeted contracts keep working unchanged; a contract with no `target_repo` is
workspace-targeted by definition.

**Someone joining the project** — they clone the control plane, install the plugin, add
themselves to the operator registry, then clone each hosted repo into the paths the manifest
already names. The manifest *is* the onboarding document.

**Upgrading the factory** — `claude plugin update foundry@agentic-foundry`. Your specs,
manifest, and hosted repos are untouched; the plugin is not in your tree.

---

## 6. When something is wrong

| Symptom | Cause |
|---|---|
| No `/foundry:*` verbs | Session started in a hosted repo, or the plugin is not installed. `cd` to the control plane. |
| `DOCTOR-RED`, operator registry | `.claude/foundry-operators.json` still has `op_example`, or the id in a contract is not a key in it. |
| A `repos{}` entry points at nothing | **The doctor will not tell you** — its five checks never read `repos{}`. The symptom appears at authorize time as `warn: … degraded` lines (see the row below). |
| Authorize prints *"matches ZERO paths under the venue root"* | `target_repo` is **absent**, so the scope grounded against the control plane, where `src/` does not exist. Add the key. This one fails closed. |
| Authorize prints several `warn: … degraded` / `SKIPPED` lines | `target_repo` is **present but unresolvable** — misspelled, or the repo is not cloned. Five grounding floors were skipped and the freeze proceeded anyway. Fix the manifest and re-authorize. |
| The control plane wants to commit your app's files | The gitignore entry is missing or not root-anchored. Use `/api/`, not `api/`. |
| Journeys cannot reach the app | The **stack profile's** `app_exercise_binding.boot` is what certification boots — not `boot_command`. See the certification how-to. |

---

## Related

- [`SETUP.md`](SETUP.md) — full file-by-file anatomy, identity isolation for multi-account
  operators, and the existing-repo (`/foundry:init`) path.
- [`example-acme-links/`](example-acme-links/README.md) — the worked example, which is itself a
  two-repo build: specs in the control plane, code in its own repo.
- [`../WORKFLOW.md`](../WORKFLOW.md) — the phase pipeline and artifact registry.
