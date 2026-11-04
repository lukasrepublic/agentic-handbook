# Example: migrating one active item of an existing project

> **Prerequisite: team mode.** The shared Project and GitHub issue migration below apply only in team mode. Enable it first with `/foundry:team-mode enable` (script `scripts/foundry_operating_mode.py enable-team`). Single-operator mode is the default and needs none of it; see "Operating modes" in [`../../OPERATING-MODEL.md`](../../OPERATING-MODEL.md).

A worked walk-through of [upgrade-and-migrate.md](upgrade-and-migrate.md) for one in-flight item.
The project, names and numbers are invented. The five per-item steps are those of the migration
procedure; each step shows the migration command (`scripts/foundry_migrate.py`) and, where useful, the plain
git equivalent.

The item: an old planning record `specs/features/api/rate-limit/feat-rate-limit.md` (owner Sam,
priority high, depends on the gateway change, promised outcome "public API is rate limited",
evidence: a draft branch `rate-limit` and a passing unit test run).

## Starting conditions

- The mechanical update has been applied and `/foundry:post-upgrade` has finished; installation is
  done and adoption is pending. The workspace is in single-operator mode, the 2.0 default.
- Team mode has been enabled as the separate step below (it is not part of the upgrade).
- The shared Project exists and the planning repository is `acme/handbook`.

## Actor and permissions

- **Project adoption owner (Lukas)**: runs the migration and records the cutover.
- **Item owner (Sam)**: confirms the item's facts. Sam's own `gh` login is used for anything Sam owns.

## Steps

### Before step 0: enable team mode (explicit, separate from the upgrade)

The 2.0 upgrade lands the workspace in single-operator mode. Team mode is a deliberate second step
by the Project adoption owner, taken only after the upgrade and `/foundry:post-upgrade` are done:

```bash
/foundry:team-mode enable
```

It requires plugin 2.0.0 or later, a configured `github_scope` and a capability check of at least
`partial`. It is reversible: `/foundry:team-mode disable` returns to single-operator mode and keeps
all history. Shared cutover happens once; each operator then does their own setup.

### 0. Inventory: custom rules, active obligations, retained history

```bash
scripts/foundry_migrate.py inventory   # read-only
git ls-files specs .foundry status-reports | wc -l
```

The inventory reports three groups for this project:

| Group | Found | Disposition |
|---|---|---|
| Custom rules | A `CLAUDE.md` paragraph "no deploys on Fridays"; a hook `.claude/hooks/no-friday.sh` | Keep both; the rule is merged into the working agreement in the PR |
| Active obligations | The rate-limit item; an unresolved security follow-up on its spec | Rate-limit migrates now; the follow-up becomes a linked issue |
| Retained history | 41 frozen specs and contracts, 12 release records | Read-only; not converted |

Record the bytes of retained history before and prove they did not change:

```bash
git ls-files specs/features .foundry/releases | xargs sha256sum > "$TMPDIR/history.before"
```

### 1. Identify owner, priority, dependencies, outcome, evidence

From the old record: owner Sam, priority high, blocked by the gateway change, outcome "public API is
rate limited", evidence branch `rate-limit` and its test run. Sam confirms each in a comment.

### 2. Create the issue and link its knowledge, branch and PR

```bash
gh issue create --repo acme/handbook --title "Rate-limit the public API" --assignee sam \
  --body-file rate-limit-issue.md
gh issue comment <n> --body 'Context: docs/architecture/api.md; branch rate-limit; predecessor specs/features/api/rate-limit/feat-rate-limit.md'
```

The body follows the task form: What, Why, Done means (`npx playwright test tests/rate-limit.spec.ts`),
Context.

### 3. Reconcile actual progress with the board, not the old status

The old record says "in progress"; the branch has no PR and the gateway change is not done. On the
Project the item is set to Backlog with the gateway issue as its "blocked by", and moves to Ready only
when the planning owner decides. A stale local status was not imported.

### 4. Mark the old record migrated and link its successor

Add one line to the top of the old record's planning region: `Migrated to acme/handbook#<n>`.
This is the only edit, and it is an annotation on an active planning record. Retained history (frozen
specs, release records) receives no such edit.

### 5. Confirm owner and a second engineer both understand it from GitHub

Sam and a colleague each open the issue with no other context and state, in a comment, what the
outcome, blocker and next action are. Disagreement means the issue is not yet complete.

### Cutover

```bash
scripts/foundry_migrate.py cutover   # team mode only; --dry-run first, then --apply
```

Until the command ships, the adoption owner records the decision as a comment on the planning
issue, "Cutover: GitHub is the plan for <items> from <date>; the old records are reference."

### Rerun

```bash
npx update-agentic-workspace
```

Expected: no file changed, no duplicate issue created for the item (the issue is found through its
predecessor link), and the checksum comparison below is empty.

```bash
git ls-files specs/features .foundry/releases | xargs sha256sum > "$TMPDIR/history.after"
diff "$TMPDIR/history.before" "$TMPDIR/history.after"
```

An empty diff shows the retained bytes did not move.

### Recovery

The run stopped after step 2 (the issue exists, the old record is not yet marked). Do not create the
issue again. Search for it through the predecessor link, finish steps 3 to 5, and mark the old record.
Items not yet reached stay marked unmigrated. Nothing reactivates the old backlog for the migrated item.
More in [diagnose-and-recover.md](diagnose-and-recover.md).

## Expected results

- One issue for the item, with owner, priority, blocker, Context links, branch and predecessor.
- The old record carries a single `Migrated to` line; every retained-history file is byte-identical.
- The Project, not the old record, shows the item's true state; a rerun changes nothing.
- A second engineer understood the item from GitHub alone.

## Outstanding human decisions

- Whether the remaining 14 active items migrate now or later (each marked either way).
- The recorded authority cutover, and its date.
- Whether the custom Friday rule stays as a hook or moves into the working agreement.

## If it fails

- A duplicate issue appeared: close it as `duplicate` of the first, never delete.
- The rerun changed a retained file: stop, restore it from Git (`git checkout -- <path>`), and report on the
  planning repository before continuing.
- The old record cannot be edited: leave a comment on the new issue naming the predecessor instead.
