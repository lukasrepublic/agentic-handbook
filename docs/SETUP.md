# SETUP — adopter anatomy + the setup runbook

The concrete, file-by-file companion to the conceptual model in the plugin's
[`docs/architecture.md`](https://github.com/lukasrepublic/agentic-foundry/blob/main/docs/architecture.md).
That doc explains *why* a project is two components; this one answers the practical
questions: **what does an initialized workspace look like on disk, where does each file
come from, and what is the exact sequence from "Use this template" to `DOCTOR-GREEN`.**

> **The two components, in one line.** This repo (a *handbook*) is the **workspace** — the
> *WHAT* to build; you own it and evolve it. The **Foundry plugin** is the **factory** — the
> *HOW*; you *install + wire* it and it stays generic and versioned. They meet at the
> **wiring contract**: `${CLAUDE_PLUGIN_ROOT}` (the factory's own files) ↔
> `CLAUDE_PROJECT_DIR` (this workspace's corpus).

---

## 1. Anatomy of an initialized adopter

What a wired, `DOCTOR-GREEN` workspace contains, annotated by **where each file comes
from** — the thing that's otherwise only learnable by reverse-engineering an existing repo.

**Legend**
`[T]` ships in this **template** ·
`[P]` provided by the **plugin** (not in your repo — resolves under `${CLAUDE_PLUGIN_ROOT}`) ·
`[B]` written by the **pre-session bootstrap** (`npx create-agentic-workspace`, §3) ·
`[I]` created/edited by **`/foundry:init`** ·
`[Y]` **yours** to fill in ·
`[G]` **gitignored** runtime/transient

> **`[B]` vs `[I]` is the distinction that changed.** `/foundry:init` no longer writes the
> permission floor or the plugin/marketplace enablement — it **verifies and reports** them. A model
> editing its own confinement is denied by the harness classifier, so those writes happen before a
> session exists. See §3.

```
<project>-handbook/
├── CLAUDE.md                          [T→Y]  governance scaffold; put YOUR project on top
├── WORKFLOW.md                        [T]    SDLC orchestration + artifact registry
├── README.md                          [T]    template readme (retarget to your project when ready)
├── .claude/
│   ├── settings.json                  [B]    THE WIRING: the permission floor + enabledPlugins/extraKnownMarketplaces
│   │                                         (+ the template's hooks). Written by the pre-session bootstrap (§3);
│   │                                         /foundry:init VERIFIES it and never writes it.
│   ├── foundry-operators.json         [T→I]  operator registry — replace op_example with your real operator id(s)
│   ├── settings.local.json            [I,G]  machine-local resolved paths (e.g. absolute gh config dir)
│   └── logs/                          [G]    session logs
├── .foundry/
│   ├── README.md                      [T]    explains the dir (runtime state; generated, mostly gitignored)
│   ├── build-provenance.yaml          [—]    NOT here — this is emitted in the CODE repo at PR time (pins this repo's commit)
│   └── security-audit.jsonl           [G]    fail-closed audit trail
├── context/                           [T]    pointer README only — the authoring kit (spec/contract
│   └── README.md                      [T]      templates, citation grammar, glossary) ships in the
│                                              PLUGIN's context/ kit [P] and stays version-locked to it
├── specs/
│   ├── features/
│   │   ├── example/api/ping/          [T]    minimal worked atom (spec + acceptance-contract.yaml)
│   │   ├── acme-links/                [T]    the DEMO's specs (the 7-step tutorial builds this; delete when done)
│   │   └── <your-product>/…           [Y]    YOUR atomic specs: <product>/<domain>/<capability>/feat-*.md (+ contract)
│   ├── releases/                      [T→Y]  release manifests (release.yaml)
│   └── lifecycle/                     [G/—]  generated lifecycle views — never hand-edited
├── docs/
│   ├── README.md                      [T]    index: which docs are YOURS vs the demo's
│   ├── architecture/                  [T→Y]  your ADRs / architecture docs
│   ├── example-acme-links/            [T]    the DEMO's docs — 7-step tutorial + the build log
│   │                                         (delete with specs/features/acme-links/ when done)
│   └── SETUP.md                       [T]    this file
├── status-reports/                    [T→Y]  executive status reports
└── .gitignore                         [T]    ignores __pycache__, the audit trail, logs, lifecycle scratch

—— provided by the PLUGIN (installed; NOT committed into your repo) ——
[P] /foundry:*  skills + engineer agents          (intake · spec-review · authorize · dispatch · certify-local · doctor · …)
[P] hooks/hooks.json   → composes into your PreToolUse/SessionStart/… events (git-discipline, cloud-CLI
                         exec guard, worktree write containment, session-learnings capture)
[P] .mcp.json          → the foundry-graph MCP (citation graph with O(1) backlinks)
[P] scripts/ + schema/ → the gate scripts + JSON schemas, reached via ${CLAUDE_PLUGIN_ROOT}
```

The crux of that last block: **none of the factory machinery lives in your repo.** The
plugin contributes the verbs and reads your nouns. `${CLAUDE_PLUGIN_ROOT}` points at the
factory's files; `CLAUDE_PROJECT_DIR` points at this workspace. Upgrading the factory =
bumping the plugin version; your specs and governance are untouched.

### Optional: identity isolation (multi-account operators)

If you run more than one GitHub account on one machine, this template **ships** a per-project
`gh` identity jail (UL-0007) so the wrong account can never push or open a PR from this repo.
It is **opt-in and dormant by default** — single-account adopters are unaffected:

```
.claude/hooks/gh-account-guard.sh        [T]  PreToolUse(Bash) guard: blocks gh when GH_CONFIG_DIR ≠ the account
                                              declared in the NEAREST .claude/gh-identity (walking up from cwd —
                                              so a nested repo with a different account is enforced as ITS account)
.claude/hooks/gh-identity-bootstrap.sh   [T]  one-time: provision ~/.config/gh-<account> with INLINE token storage
                                              (--insecure-storage) — from the keyring if present, else an isolated
                                              browser login; proves the jail with `gh api user`
.claude/hooks/gh-account-guard.selftest.sh [T] hermetic proof of the guard (AC-GHID-1..5)
.envrc                                   [T]  direnv: exports GH_CONFIG_DIR (from .claude/gh-identity) + FOUNDRY_OPERATOR
.claude/settings.json (hooks)            [T]  wires the PreToolUse guard (dormant until you declare an identity)
.claude/gh-identity                      [Y]  YOU create this — one line, your account handle (activates the jail)
.claude/settings.local.json              [Y,G] machine-local resolved GH_CONFIG_DIR (gitignored)
```

**To activate** (only if you have >1 account):

```bash
echo <account> > .claude/gh-identity                 # declare the repo-owning account
.claude/hooks/gh-identity-bootstrap.sh <account>     # provision ~/.config/gh-<account> (inline token)
#  → prints "OK: …/.config/gh-<account> resolves to <account>"   (this gh api user proof IS the contract)
direnv allow                                         # exports GH_CONFIG_DIR for terminal sessions
```

Also set `GH_CONFIG_DIR=$HOME/.config/gh-<account>` in the gitignored `.claude/settings.local.json`
env so **Claude Code** sessions (not just the terminal) inherit the jail. The moment
`.claude/gh-identity` exists, any `gh` command under the wrong/unset `GH_CONFIG_DIR` is **blocked
fail-loud**. Single account? Do nothing — the guard stays dormant.

> **The keyring trap (why `--insecure-storage`).** On a keyring-backed machine, `gh auth login`
> stores the token in the **shared OS keyring** and *ignores* `GH_CONFIG_DIR` for storage — so a
> later `GH_CONFIG_DIR=… gh api user` resolves through the keyring to the *globally-active*
> account and the jail is **illusory**. `gh-identity-bootstrap.sh` therefore logs in with
> `--insecure-storage`, writing the token **inline** into `~/.config/gh-<account>/hosts.yml`.
> Prove the jail with **`gh api user`** (a real resolve), never `gh auth status` (it can read the
> keyring and lie).

> **The second layer — git transport (SSH host alias).** `gh` identity controls the API
> (PR/issue/admin); it does **not** control `git push`, which authenticates by **SSH key**. Pushing
> via a bare `git@github.com:…` URL uses your *default* key regardless of the gh jail. Give each
> account its own SSH host alias and use it in every remote:
>
> ```sshconfig
> # ~/.ssh/config
> Host <account>-github
>   HostName ssh.github.com
>   Port 443
>   IdentityFile ~/.ssh/<account>-ed25519
>   IdentitiesOnly yes
> ```
> ```bash
> git remote set-url origin git@<account>-github:<owner>/<repo>.git   # NOT git@github.com:…
> ssh -T git@<account>-github                                         # expect: "Hi <account>!"
> ```

---

## 2. The wiring — three native seams + the data-flow crux

The plugin plugs into the workspace through **native Claude Code mechanisms** — no bespoke
glue:

| Seam | How it wires |
|---|---|
| **Plugin load** | `.claude/settings.json` → `enabledPlugins: { "foundry@agentic-foundry": true }` makes `/foundry:*` skills, agents, and the MCP available in this repo's sessions. |
| **Hooks** | the plugin's `hooks/hooks.json` composes (additively, deduped) into your `PreToolUse`/`SessionStart`/`PostToolUse` events — the git-discipline guard and learnings capture fire because the plugin's hooks are wired into *your* tool events. |
| **MCP** | the plugin's `.mcp.json` merges in the `foundry-graph` retrieval source. |
| **Data flow** | `${CLAUDE_PLUGIN_ROOT}` = the factory's own files (gate scripts, schemas); `CLAUDE_PROJECT_DIR` = **this workspace** (specs, the operator registry, the graph corpus). The factory's scripts read this workspace's artifacts. |

That last row is integrity-critical, so it is self-verified: `/foundry:doctor`'s five probes
check the wiring (manifest, hooks, skills, profile lock, operator registry) in under a second.

---

## 3. Before your first session — the pre-session bootstrap

**The Claude Code session is a step, not the starting point.** This is the one part of setup that
cannot happen inside a session, and the reason is structural rather than stylistic: a model editing
its own confinement is denied by the harness classifier. So `/foundry:init` **can never scaffold its
own permission floor** — the floor has to exist before a session does, written in your own terminal.

```bash
npx create-agentic-workspace
```

The wizard walks name/dir → greenfield-vs-existing → git/GitHub identity → stage mode → the
permission conversation, previews every file **and** every capability it will declare before writing
a byte, then writes and stops. It **declares, never grants**: it never runs `claude`, never accepts
the workspace trust dialog, and never pre-grants anything. The platform's trust dialog — which lists
exactly the rules it wrote — is the consent ceremony.

What it owns, and `/foundry:init` therefore does not:

| Artifact | Owner |
|---|---|
| `.claude/settings.json` — the three-tier permission floor | **pre-session CLI** |
| `extraKnownMarketplaces` + `enabledPlugins` (plugin/marketplace enablement) | **pre-session CLI** |
| Git commit-identity isolation (`--gh-account`, the `includeIf` wiring) | **pre-session CLI** |
| Status line / native Bash sandbox settings | *no shipped writer* — init reports only |

**Already have a workspace?** You do not need to re-onboard. `/foundry:init` still **verifies and
reports** on all of the above — it simply never writes them. A finding tells you which artifact is
missing and who owns the write.

Then continue at §4 or §5 below, and open your session at the end of it — not the beginning.

---

## 4. Setup runbook — greenfield (start from this template)

> **direnv users:** the template ships an `.envrc` (it exports identity variables when you
> opt into the gh jail). direnv will prompt `blocked` on first entry — `direnv allow` when
> you're ready, or ignore it; nothing below depends on it until the identity section.

> **First merge from a Claude Code session:** the plugin's git-discipline guard admits
> `gh pr merge` only on live all-green checks — and a fresh workspace has **no CI yet**, so
> it fail-closes. Either wire a first CI check before your first PR, or run that first
> merge yourself in your own terminal. This is the guard working as designed.

**The whole journey, end to end.** Steps 0–2 run in **your own terminal**; the session opens at
step 3. Nothing here needs a Claude Code session until it says so.

```bash
# ── 0. THE PERMISSION FLOOR — in your own terminal, before any session (§3) ──────────────
#    Writes .claude/settings.json (the three-tier floor), the marketplace + plugin
#    declarations, the git commit-identity wiring, and a seven-file workspace seed.
#    It previews every file AND every capability before writing a byte, then stops.
npx create-agentic-workspace
cd <project>-handbook

# ── 1. START FROM THIS TEMPLATE (optional — step 0 can also seed a fresh workspace) ──────
#    GitHub UI → "Use this template" → <project>-handbook, or:
gh repo create <you>/<project>-handbook --template lukasrepublic/agentic-handbook --public --clone
cd <project>-handbook

# ── 2. INSTALL THE FACTORY (the Foundry plugin) ──────────────────────────────────────────
#    Pin the marketplace to a release tag — an unpinned add resolves the default branch.
claude plugin marketplace add lukasrepublic/agentic-foundry#v1.2.0
claude plugin install foundry@agentic-foundry

#    Register yourself: edit .claude/foundry-operators.json → replace op_example with your
#    operator id + GitHub handle. (/foundry:init will also seed this if you skip it.)
```

Now open the session — **this is where the Claude Code part begins**:

```
# ── 3. ACCEPT THE TRUST DIALOG ───────────────────────────────────────────────────────────
claude
   → Claude Code shows the workspace trust dialog, listing exactly the `allow` rules
     step 0 declared. THIS is the consent ceremony: the rules take effect only once you
     accept it. `deny`/`ask` rules apply immediately (restrict-only is un-gated).

# ── 4. INITIALIZE ────────────────────────────────────────────────────────────────────────
/foundry:init
   → WRITES:    the operator registry (.claude/foundry-operators.json), the stack-profile
                lock (.foundry/stack-profile.lock, opt-in), and the .gitignore managed block.
   → VERIFIES:  the permission floor, plugin/marketplace enablement, git commit identity,
                the status line and the native Bash sandbox — it reports findings on these
                and never writes them. A finding names the artifact and who owns the write.

# ── 5. PROVE THE WIRING ──────────────────────────────────────────────────────────────────
/foundry:doctor          # must print DOCTOR-GREEN before the workspace is "live"
   → its permission-floor probe compares your written floor against the INSTALLED plugin's
     own copy of the map — the one check that did not travel through npm.

# ── 6. APPLY YOUR MERGE FLOOR ────────────────────────────────────────────────────────────
   the plugin's scripts/foundry_tier_preflight.py reports your honest tier from
   post-apply evidence (branch protection + required checks). Tier A enforces
   server-side; Tier B reports only. Claim only the tier you actually have.
```

> **Cross-account or private template — local-seed instead of `--template`.** "Use this template"
> and `gh repo create --template` require the **creating account to be able to read the template
> repo**. If your template is private and owned by a *different* account or org than the new repo's
> owner (a multi-account setup), that call 403s and there is no cross-account template clone. Seed
> from a local copy instead — tracked files only, no `.git`, no machine-local cruft:
>
> ```bash
> # from a checkout of the template (the account that owns it):
> git archive --format=tar HEAD | (mkdir -p /tmp/seed && tar -x -C /tmp/seed)
> cd /tmp/seed && git init -q && git add -A && git commit -qm "seed from <template>"
>
> # create the EMPTY repo via the OWNING account's gh token (no --template):
> GH_CONFIG_DIR=$HOME/.config/gh-<account> gh repo create <owner>/<project>-handbook --private
>
> # push via the account's SSH host alias (see Identity isolation), NOT a github.com URL:
> git remote add origin git@<account>-github:<owner>/<project>-handbook.git && git push -u origin main
> ```
>
> Then continue at step 2 (install the factory) in the new repo.

Replace the placeholder paragraph at the top of `CLAUDE.md` with your project's description,
and you're ready to author your first atom (see [Next](#5-next)).

> **One-command bootstrap.** The plugin ships `scripts/foundry-bootstrap.sh`, which collapses
> steps 1–4 (scaffold → plugin install → optional identity jail → init → doctor). The steps
> above are the same sequence, unrolled — use whichever you prefer.

## 5. Setup runbook — existing repo (already have one)

You don't have to start from the template. The order is the same: **the floor first, in your own
terminal; the session second.**

```bash
# in your own terminal, at the repo root — scaffolds into an existing tree, never clobbering:
npx create-agentic-workspace --dir . --existing
```

It creates only what is **absent**. A managed file that already exists and differs is reported
`drifted` and **left byte-identical** — never overwritten, never merged. Then, in a session:

```
/foundry:init    # WRITES the operator registry, the stack-profile lock, the .gitignore block
                 # VERIFIES (never writes) the permission floor, plugin/marketplace enablement,
                 #   git identity, status line, sandbox — reporting a finding for each gap
/foundry:doctor  # must print DOCTOR-GREEN, then apply your merge floor (tier preflight)
```

The pre-session bootstrap does the **wiring**; `/foundry:init` **verifies** it and seeds the
governance artifacts; the template provides the **workspace structure**. Three jobs — see
architecture.md §3.

---

## Multi-repo control plane — hosting your code repos

This workspace can be a **control plane** that hosts the project's *other* repos — its
infrastructure (IaC) repo, service repos, any number — and drives the factory into each.

> **This section is the add-a-repo mechanics.** The operating model — the session rule, building
> one atom across two repos, day-two operations, and the symptom→cause table for when things look
> wrong — is in **[`control-plane.md`](control-plane.md)**. Read that first if you are setting up
> a multi-repo project; come back here for the runbook.

### What it looks like on disk

**Three git repositories, one directory tree.** That is the whole idea, and it is the part prose
keeps failing to convey:

```
<project>-handbook/                      ◀── git repo #1 — the workspace. YOU commit this one.
│
├── CLAUDE.md · WORKFLOW.md                  governance + the SDLC pipeline
├── .claude/
│   ├── settings.json                        the wiring (enabledPlugins → the factory)
│   ├── foundry-operators.json               who is allowed to authorize
│   └── foundry-project.json   ◀── THE MANIFEST. repos{} maps a dispatch key → a path below.
├── specs/features/<product>/…               the WHAT: feat-*.md + acceptance-contract.yaml
├── docs/ · status-reports/
├── .gitignore                 ◀── every hosted repo below is listed here, root-anchored (/infra/)
│
├── acme-links/                          ◀── git repo #2 — GITIGNORED. Not a submodule.
│   ├── .git/                                its own history, branches, PRs, CI, merge floor
│   ├── src/…                                the HOW-built: the actual application code
│   └── .foundry/build-provenance.yaml       pins the repo-#1 commit it was authorized against
│
└── infra/                               ◀── git repo #3 — GITIGNORED. Same deal.
    ├── .git/
    └── terraform/… or k8s/…
```

Read the boundaries, because they are what make this work:

- **`git status` in the workspace never shows anything from `acme-links/` or `infra/`.** They are
  root-anchored gitignore entries. The control plane cannot accidentally commit your app.
- **Each hosted repo keeps a fully independent history** — its own PRs, its own CI, its own
  branch protection. The workspace is never pinned to a submodule commit pointer.
- **The link runs the other way.** Rather than the workspace tracking the code, each built atom
  writes `.foundry/build-provenance.yaml` *in the code repo*, pinning the workspace commit whose
  frozen contract authorized it. Traceability without coupling.
- **The factory is not in this tree at all.** The plugin installs under `~/.claude/plugins/…` and
  resolves via `${CLAUDE_PLUGIN_ROOT}`; it reads your corpus via `CLAUDE_PROJECT_DIR`. Upgrading
  the factory touches nothing above.

The manifest is what ties a spec to a directory:

```jsonc
// .claude/foundry-project.json
"repos": {
  "workspace":  { "path": ".",           "kind": "workspace" },
  "app":        { "path": "acme-links",  "kind": "single-app", "boot_command": "make dev" },
  "infra":      { "path": "infra",       "kind": "infra-repo" }
}
```

```
   acceptance-contract.yaml            .claude/foundry-project.json         on disk
   ───────────────────────             ───────────────────────────         ───────
   target_repo: app          ─────►    repos.app.path = "acme-links"  ─────►  ./acme-links/
```

A contract with **no** `target_repo` is workspace-targeted — the single-repo default. A contract
naming a `target_repo` key follows two distinct dispositions, and they must not be confused:

- **Key absent** → the scope grounds against the control plane itself, where the target repo's
  files do not exist, so it `matches ZERO paths` under the venue root. Authorization **refuses**,
  by design. (That is not hypothetical — it caught four contracts here whose `target_repo` was
  missing entirely, so every path in them matched zero files.)
- **Key present but unresolvable** (misspelled, or a repo not yet cloned) → there is no venue
  root to ground against, so authorization `degrades rather than refuses`: five grounding floors —
  surface⊆scope, doctor-row baseline, system-grounding, `allowed_paths` grounding, and
  checkpoint-locator grounding — each print a `warn: … degraded` / `SKIPPED` line and are
  skipped, and the contract still freezes and still increments `auth_seq`.

**Nothing catches the second case before authorize time by itself.**
`feat-foundry-control-plane-preflight` — was specified, not shipped, at spec-authoring time
(2026-08-01/02); it has since shipped as `/foundry:doctor`'s sixth probe in agentic-foundry
v1.1.0 (2026-08-02). It is an operator-invoked doctor check, not an authorization gate: it
convicts a dangling `repos{}` path when an operator runs `/foundry:doctor`, keeps that
command's `--session-start` fail-open contract, and does not change the authorize-time
five-floor degradation above. Read the `warn:` lines in the authorize dry-run before you
confirm — register only repos you have already cloned. This coverage on the degraded path
is a practice, not a control: no gate, hook or CI job asserts either happened.

**The pattern (and why this one).** This is the **meta-repo** pattern: the hosted repos live as
**independent, gitignored sibling subdirs**, named by a **manifest** — here,
`.claude/foundry-project.json` `repos{}` (the *same* manifest the factory's multi-repo dispatch
already reads; there is **no second artifact**). We deliberately do **not** use **git
submodules**: submodules couple the control plane to a pinned submodule commit, require manual
`git submodule update`, and entangle histories — the wrong fit for a hub of *fully independent*
repos. Gitignored siblings + a manifest keeps each hosted repo's history its own. (This is the
established lightweight multi-repo convention, e.g. the `meta` tool.)

**A fresh template is single-repo.** The seeded `repos{}` carries only the `workspace` self-entry
(`path: "."`), which is the single-repo default: a contract with no `target_repo` is
workspace-targeted, and there is nothing to configure until you clone a second repo in.

> **Add hosted repos only once cloned — never as dangling entries, and check your spelling.**
> `/foundry:doctor`'s sixth probe (`feat-foundry-control-plane-preflight`, shipped in
> agentic-foundry v1.1.0) now catches a dangling `repos{}` entry: run `/foundry:doctor` after
> every manifest edit and a dangling entry turns `DOCTOR-RED`, naming the offending key. It is an
> operator-invoked check, not an authorization gate — it only fires when you actually run
> doctor, and `--session-start` fails open (a warning only, the session still continues).
>
> The cost still lands at authorization if you skip that step. When a contract's `target_repo`
> does not resolve to a real directory — a typo, or a repo you have not cloned yet —
> `/foundry:authorize` cannot establish a venue root, and **five grounding floors degrade to
> warnings and the freeze proceeds anyway**: the surface⊆scope check, the doctor-row baseline
> check, the system-grounding floor, the `allowed_paths` reality-grounding check, and
> checkpoint-locator grounding. Each prints a `warn: … degraded` / `SKIPPED` line, so the
> information is on screen — but a typo and a not-yet-cloned repo look identical, and the
> contract still freezes and still increments `auth_seq`.
>
> **Read the `warn:` lines in the authorize dry-run before you confirm.** If you did not expect a
> degrade, you have a manifest defect, not a missing checkout. Doing both — running doctor after
> every edit, reading the `warn:` lines before every freeze — is a practice, not a control: no
> gate, hook or CI job asserts either happened.

### Add a hosted repo (runbook)

1. **Clone it into a root-anchored, gitignored subdir.** Add the dir to `.gitignore` under the
   *hosted repos* section (root-anchored with a leading slash so the control plane never tracks
   it), then clone:
   ```bash
   #  .gitignore →  /infra/
   git clone git@github.com:<you>/<project>-infra.git infra
   ```
2. **Register it in the manifest** — add one `repos.<key>` entry. The **key is the `target_repo`
   dispatch key**; the shape is exactly what the resolver reads (`repos.<key>.path`). Not every
   field you can record here is read by shipped code — see `control-plane.md` →
   *What the manifest fields actually do* for which of the seven fields are and are not:
   ```json
   "repos": {
     "workspace": { "path": ".", "kind": "workspace", "role": "the control plane" },
     "infra":     { "path": "infra", "kind": "infra-repo", "role": "the project's IaC (OpenTofu/Kubernetes)" }
   }
   ```
   With the cloned dir present on disk, the path resolves and `/foundry:doctor` stays
   `DOCTOR-GREEN`. That green attests the wiring, not the registration — the doctor's checks
   never used to read `repos{}` at all, and even now, its sixth probe only checks that the path
   resolves; it does not check the key name a contract will actually reference, or any other
   field. See the callout above for the full mechanism and its tier.
3. **Provenance rides the dispatch — nothing to pin at clone time.** The cross-repo
   `.foundry/build-provenance.yaml` marker (pinning the workspace commit an atom was authorized
   against) is authored as part of the dispatched atom's PR, per the provenance convention the
   plugin documents. It appears when the first atom is dispatched into that repo.

Now dispatch a spec whose acceptance-contract sets `target_repo: infra`: the factory redirects the
worker into the `infra/` working tree, and that repo's own merge floor admits the PR.

---

## 6. Next

- **Author + authorize your first atom** → the plugin's
  [`QUICKSTART.md`](https://github.com/lukasrepublic/agentic-foundry/blob/main/docs/QUICKSTART.md)
  (zero → your first governed merge in about ten minutes).
- **Learn the whole loop by building a real app** → [the Acme Links tutorial](example-acme-links/README.md),
  or read [how that app was actually built](example-acme-links/BUILD-JOURNEY.md).
- **The conceptual model** (workspace ⟷ factory, the WHAT/HOW split) →
  [architecture.md](https://github.com/lukasrepublic/agentic-foundry/blob/main/docs/architecture.md).

The loop, once wired:

```
/foundry:intake → /foundry:spec-review → /foundry:authorize → /foundry:dispatch
      → the merge floor (your CI + branch protection) → /foundry:certify-local → your sign-off
```
