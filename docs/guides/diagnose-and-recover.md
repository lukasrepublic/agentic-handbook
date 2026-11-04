# Diagnose and recover

> **Prerequisite: team mode.** The inbox, Project and Command Deck checks below apply only to a team-mode workspace. Enable it first with `/foundry:team-mode enable` (script `scripts/foundry_operating_mode.py enable-team`). Single-operator mode is the default and needs none of it; see "Operating modes" in [`../../OPERATING-MODEL.md`](../../OPERATING-MODEL.md).

What to check, and what to do next, when something is off: the wrong workspace or version, stale
instructions, missing GitHub access, a partial inbox, duplicate leads, an interrupted migration,
uncommitted work, or no Command Deck. It ends with a manual way to run the shared workflow using
GitHub and existing commands only.

Definitions: [`../../OPERATING-MODEL.md`](../../OPERATING-MODEL.md). Checked against the foundry base
tree `origin/atom/subtract`; the release pin is pending: lands with gn-06.

## Starting conditions

- Something above has gone wrong, and you can open a terminal in the workspace.
- Preserve first: do not delete branches, reset, or clean the tree until you know what is
  uncommitted.

## Actor and permissions

- **The affected operator** diagnoses and recovers their own machine and their own tasks.
- **The project adoption owner** decides anything shared: cutover state, which lead owns a request,
  access grants.

## Steps

1. **Start with the doctor, from the workspace root:**

   ```text
   /foundry:doctor
   ```

   ```bash
   pwd
   git rev-parse --show-toplevel
   git status --short
   ```

   A session started inside a hosted repository, not the workspace root, is the most common cause.

2. **Triage by symptom.**

   | Symptom | Check | Next action |
   |---|---|---|
   | Wrong workspace or version | `pwd`; `claude plugin list`; compare with a colleague's version in the planning repo | Restart at the workspace root; update your own scope; open a new session |
   | Preserved stale instructions | `git log -3 -- CLAUDE.md .claude/` and the upgrade report `.foundry/upgrade-report.json` | Reconcile against [`../../OPERATING-MODEL.md`](../../OPERATING-MODEL.md); record the choice in a PR |
   | Missing GitHub access | `gh auth status`; `gh project list --owner <owner>` | Run `gh auth refresh -s read:project -s project` yourself; ask the owner for membership |
   | Partial inbox (a source unreadable) | `gh issue list --assignee @me`; `gh pr list --search "review-requested:@me"` | Report which source failed; do not call the inbox empty and pick no new routine work |
   | Duplicate leads | `gh issue list --label request --state open` and compare owners | The adoption owner names one; the others stop and comment |
   | Interrupted migration | `git status`; list issues carrying a predecessor link | Finish or mark items; see the next section |
   | Uncommitted work | `git status --short`; `git stash list` | Commit to a branch and push after `foundry-test.sh`; never discard |

3. **Interrupted upgrade or migration.** Do not restart from scratch. Re-run the updater (it is
   idempotent and keeps edited files):

   ```bash
   npx update-agentic-workspace --dry-run
   npx update-agentic-workspace
   ```

   Then identify, per active item, whether its issue exists and whether the old record is marked
   migrated. Items already moved stay in GitHub; unmigrated items stay marked as such. The partial
   state report of the migration command is pending: lands with gn-14 (`scripts/foundry_migrate.py preview`).

4. **Rollback limits.** The upgrade never rewrites retained history, and the migration records a
   decision in GitHub. You can stop, pin a plugin scope back by hand, or leave items unmigrated; you cannot
   erase what was recorded, and nothing here claims a full automated rollback.

### Operate manually without Command Deck

Until the deck is available (`/foundry:command-deck` is pending: lands with gn-10), run the shared
workflow with GitHub and existing commands. Everything below is visible to colleagues.

1. **Queue.** Your owned, Ready, unblocked work:

   ```bash
   gh issue list --assignee @me --state open
   gh project item-list <project-number> --owner <owner> --format json
   ```

   Select a new task only if it is yours, Ready, unblocked and within capacity.

2. **Requests.** Find what others need from you, and what you need from them:

   ```bash
   gh issue list --label request --assignee @me --state open
   gh issue list --label request --author @me --state open
   gh issue view <request-number> --comments
   ```

   Acknowledge a blocker at once by commenting on the issue and tell the operator; resolve it only when
   the dependency is really satisfied. Use the structured comment from the working agreement
   (`foundry-deck`, events `ack`, `blocker_ack`, `resolved`).

3. **Handoff.** On stopping, preserve uncommitted work on a branch, then comment on the issue:

   ```bash
   gh issue comment <issue-number> --body 'Handoff: branch <name>, PR <url>, evidence <url>, next: <action>'
   ```

4. **Evidence.** Link what another operator can open: the PR, the CI run, the document revision.

   ```bash
   gh pr checks <pr-number>
   gh run list --branch <branch> --limit 5
   python3 "$CLAUDE_PLUGIN_ROOT/scripts/foundry-ticket.py" status
   ```

5. **Continue.** Run `bash "$CLAUDE_PLUGIN_ROOT/scripts/foundry-test.sh"`, push once, open one PR, and
   follow [work-each-day.md](work-each-day.md). Acceptance of a document outcome remains the named
   human's decision.

## Expected results

- You know which of the failures above you have, and the state of each affected task is visible in
  GitHub.
- No work was lost: uncommitted changes are on a branch, and migrated items have one planning home.
- A colleague can pick up from your handoff comment alone.

## Outstanding human decisions

- Who the single lead is when leads are duplicated.
- Whether to finish or stop a paused migration, and when to record cutover.
- Any degraded-operation policy for an unreadable inbox source: until one is approved, new routine
  dispatch pauses.
- Access grants, which the owner gives and the operator never works around.

## If it fails

- The doctor stays red after you fix the cause: read its failing line, fix that one thing, run it again.
- You cannot tell what state the migration is in: stop, snapshot with `git status` and `git log`, and
  ask the adoption owner on the planning repository; do not delete issues or branches to tidy up.
- Branch cleanup: only `python3 "$CLAUDE_PLUGIN_ROOT/scripts/foundry-worktree-gc.py" --dry-run --repo <dir>`,
  and apply only the merged class it lists.
