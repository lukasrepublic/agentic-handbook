# Upgrade and migrate an existing Foundry workspace

> **Prerequisite: team mode.** Moving active work to GitHub (adoption and cutover) is a team-mode step. The upgrade itself lands in single-operator mode. Enable it first with `/foundry:team-mode enable` (script `scripts/foundry_operating_mode.py enable-team`). Single-operator mode is the default and needs none of it; see "Operating modes" in [`../../OPERATING-MODEL.md`](../../OPERATING-MODEL.md).

Two separate things happen to an older project: the plugin and managed files are refreshed
(installation), and selected active work is moved to GitHub with a recorded decision about which
system is authoritative (adoption, or cutover). Either can be finished while the other is still
pending, and the output must say which. A worked, per-item walk-through is in
[example-existing-project-migration.md](example-existing-project-migration.md).

Definitions: [`../../OPERATING-MODEL.md`](../../OPERATING-MODEL.md). Checked against the foundry
base tree `origin/atom/subtract`. Supported source and target release numbers are pending: lands with gn-06; this guide names none.

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

   `--dry-run` plans and prints everything, writes nothing and runs no `claude` command. The
   installation-versus-adoption report and the quarantine of retired items are pending: lands with gn-13.

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
   and removed only under `--cleanup`; run `--dry-run --cleanup` first. A mode that keeps the
   previous workflow lane (`--legacy-maintenance`) is pending: lands with gn-13.

4. **Open a new session and finish the judgement half:**

   ```text
   /foundry:post-upgrade
   ```

   It commits what the updater wrote, walks standing grants, a truth pass over your own prose, branch
   cleanup and verification, and opens one PR.

5. **Reconcile custom instructions** with the current working agreement. Where yours and
   [`OPERATING-MODEL.md`](../../OPERATING-MODEL.md) disagree, record the choice in writing in the PR;
   do not leave both live.

6. **Migrate selected active work, one item at a time**, with the preview-then-apply pair below,
   then record the authority cutover as a deliberate decision.

   ```bash
   scripts/foundry_migrate.py preview   # read-only
   scripts/foundry_migrate.py cutover   # team mode only; --dry-run first, then --apply
   ```

7. **Verify and rerun.** Run the update again: it should change nothing and create no duplicate
   shared task. Check the versions each operator really loads (`/foundry:doctor`) rather than trusting
   a success line.

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
