# Upgrade and migrate an existing Foundry workspace

Two separate things happen to an older project: the plugin and managed files are refreshed
(installation), and selected active work is moved to GitHub with a recorded decision about which
system is authoritative (adoption, or cutover). Either can be finished while the other is still
pending, and the output must say which. A worked, per-item walk-through is in
[example-existing-project-migration.md](example-existing-project-migration.md).

Definitions: [`../../OPERATING-MODEL.md`](../../OPERATING-MODEL.md). Checked against foundry
`release/2.0.0` at `7681b90a`.

**What changes for you.** The upgrade re-runs governance intake: it applies the kit changes by pull
request and three-way merges them with your edits. Older releases had a mode switch; it is
gone. There is one mode and `github_scope` is part of setup. Four session rules now have hooks, so
commands you used to run may be refused (see [New command rules](#new-command-rules)).

## Starting conditions

- A workspace that already has the plugin enabled, with specs, contracts, release records or
  other history of its own.
- A clean working tree on a branch (commit or stash first). Mixed local plugin versions across
  operators are expected to be detected, not assumed away.
- Node 22 or newer.

## Actor and permissions

- **Project adoption owner**: decides dispositions, reconciles instructions, decides the cutover.
- **Each operator**: refreshes their own machine. The upgrade command acts only on the current
  workspace and the operator's own plugin scopes.

## Steps

1. **Preview without changing anything**, from inside the workspace:

   ```bash
   npx update-agentic-workspace --dry-run
   ```

   `--dry-run` plans and prints everything, writes nothing and runs no `claude` command. It reports
   installation and adoption separately and lists retired items.

2. **Inventory custom rules and active obligations.** Before applying anything, list your own
   instructions (workspace `CLAUDE.md`, hooks, permission rules) and the items still in flight:

   ```bash
   scripts/foundry_migrate.py inventory   # read-only
   ```

   The same list by hand: `git ls-files specs .foundry status-reports`, plus your open
   issues and branches. Retained history keeps its bytes; do not rewrite it to fit a new shape.

3. **Apply the supported mechanical update:**

   ```bash
   npx update-agentic-workspace
   ```

   It refreshes the marketplace, updates the plugin in every scope that enables it, and reconciles
   managed files and the permission floor without overwriting a file you edited. It writes
   `.foundry/upgrade-report.json` and ends by naming the next step. Stale retired files are listed
   and removed only under `--cleanup`; run `--dry-run --cleanup` first. `--legacy-maintenance` also
   runs the two history writers that the default skips.

4. **Open a new session and finish the judgement half:**

   ```text
   /foundry:post-upgrade
   ```

   It commits what the updater wrote, walks standing grants, a truth pass over your own prose, branch
   cleanup and verification, and opens one PR.

5. **Review the governance pull request.** After the plugin refresh the updater runs
   `foundry_governance.py upgrade`: it applies renamed rule ids to `governance/local/`, regenerates
   the kits' CI and hook snippets and merges them three-way against the snapshot of the old ones and
   your working file. Your edit survives, or the file gets inline conflict markers and the run exits
   with findings; a snippet you deleted stays deleted. It bumps `.foundry/governance.lock` and
   refuses a dirty tracked tree. An old `.foundry/stack-profile.lock` is absorbed into the governance
   lock once. A workspace with no lock gets intake instead: follow
   [adopt-an-existing-codebase.md](adopt-an-existing-codebase.md#steps).

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/foundry_governance.py" upgrade --pr
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/foundry_governance.py" check
   ```

6. **Add `github_scope`** if it is missing: run `/foundry:init`. The GitHub-backed verbs refuse with
   `github-scope-missing` until it is set. The mode-switch step of an earlier release no
   longer exists; nothing replaces it.

7. **Reconcile custom instructions** with the current working agreement. Where yours and
   [`OPERATING-MODEL.md`](../../OPERATING-MODEL.md) disagree, record the choice in writing in the PR;
   do not leave both live.

8. **Migrate selected active work, one item at a time**, with the preview-then-apply pair below,
   then record the authority cutover as a deliberate decision.

   ```bash
   scripts/foundry_migrate.py preview   # read-only
   scripts/foundry_migrate.py cutover   # --dry-run first, then --apply
   ```

9. **Verify and rerun.** Run the update again: it should change nothing and create no duplicate
   shared task. Check the versions each operator really loads (`/foundry:doctor`) rather than trusting
   a success line.

## New command rules

Hooks now refuse these shapes in a session. There is no off switch; the refusal message names the
allowed shape.

| Before | Now |
|---|---|
| `cd <dir>` then a command | `git -C <absolute-dir> ...`, or an absolute path |
| `rm` of any path | `rm` only inside the session scratch directory |
| `bash -c 'a; b'`, `python3 -` or a heredoc script | write the script to a file and run it by name |
| reading a secret value (a keychain, token or vault read, `.env`, `~/.ssh`) | never; configure names and let the tool read it. Add your own extra verbs or paths under `secrets` in `.foundry/operating-model.yaml` (add-only) |

The hooks are `hooks/foundry-shell-shape.py` and `hooks/foundry-secret-read-guard.py`; see also the
plugin's `docs/how-to/secrets-never-read.md`. Update your own scripts, aliases and saved prompts that
use the left column.

## Expected results

- Plugin and managed files are current in every scope; `/foundry:doctor` reports `DOCTOR-GREEN`.
- Retained historical specs, contracts and release records are byte-identical to before
  (compare `git diff --stat` and checksums if you want proof).
- Each migrated item is a GitHub issue with a link to its predecessor, and the old planning record
  is marked migrated. Unmigrated items are explicitly marked as such. Nothing reactivates an old
  backlog.
- An installation that succeeded while the GitHub setup or decisions are incomplete is reported as
  installed, adoption pending.

## Outstanding human decisions

- Which active items migrate now and which stay behind.
- The disposition of each custom rule and tool: keep, merge, or retire.
- The authority cutover: the moment GitHub, not the old records, is the plan. It is recorded, never
  inferred.
- Whether to run `--cleanup`.

## If it fails

- The updater stops part-way: re-run it. Every phase is idempotent; an edited file is kept, and the
  report says which phase finished.
- A session still loads the old plugin: check each scope's registration, then start a new session.
- The migration was interrupted: do not start it again from scratch; follow the partial-state steps in
  [diagnose-and-recover.md](diagnose-and-recover.md). Rollback is limited: history is never rewritten,
  so recovery means finishing or marking items, not erasing them.
