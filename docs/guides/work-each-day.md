# Work with Foundry each day

> **Prerequisite: team mode.** The Project queue, operator inbox and requests below apply only in team mode. Enable it first with `/foundry:team-mode enable` (script `scripts/foundry_operating_mode.py enable-team`; pending: lands with gn-17). Single-operator mode is the default and needs none of it; see "Operating modes" in [`../../OPERATING-MODEL.md`](../../OPERATING-MODEL.md).

The daily cycle for one operator: refine and mark Ready, start work, service blockers, verify, get
review and acceptance, deliver, stop and hand off. Two worked examples follow: a code task and a
document task, each taken to Done.

The states, eligibility, completion meanings and request rules are defined in
[`../../OPERATING-MODEL.md`](../../OPERATING-MODEL.md); this guide only shows how to act on them.
Checked against the foundry base tree `origin/atom/subtract`; the release pin is pending: lands with gn-06.

## Starting conditions

- You are set up ([start-a-new-project.md](start-a-new-project.md) or
  [join-an-existing-team.md](join-an-existing-team.md)) and your session is at the workspace root.
- At most two started, unfinished outcomes are yours (the pilot capacity), unless an expedited
  exception is visible on the issue.

## Actor and permissions

- **Planning owner**: refines Backlog and moves a task to Ready. Agents may draft Backlog items; they
  never decide what is Ready.
- **Owner (assignee)**: starts, verifies, requests review, delivers.
- **Accepting human**: the owner, or the named accepting owner for a document outcome. A request
  recipient answers their own requests.

## Steps

1. **See your queue.** Your personal Project view, or:

   ```bash
   gh issue list --assignee @me --state open
   gh issue list --label request --assignee @me --state open
   gh pr list --search "review-requested:@me"
   ```

2. **Resume before starting.** Finish In progress and Review follow-up first; pick new work only from
   your own, unblocked, Ready tasks. Until the owned-queue verbs ship you select by reading the list above.
   The owned-queue verbs `scripts/foundry-ticket.py next` (then `claim`, `reconcile`, `lead`) are pending: lands with gn-08.

3. **Start the Command Deck** to run workers and inspect requests. `/foundry:command-deck` is pending: lands with gn-10.
   Without it, use the manual path in
   [diagnose-and-recover.md](diagnose-and-recover.md#operate-manually-without-command-deck).

4. **Service blockers first.** A request that blocks someone is acknowledged in GitHub and acted on
   before routine work. A non-blocker gets a visible target date, and a reschedule keeps the original
   target.

5. **Start a task**, set its Status to In progress, then:

   ```bash
   python3 "$CLAUDE_PLUGIN_ROOT/scripts/foundry-ticket.py" start <issue-number>
   python3 "$CLAUDE_PLUGIN_ROOT/scripts/foundry-ticket.py" status
   ```

6. **Verify locally** before the first push:

   ```bash
   bash "$CLAUDE_PLUGIN_ROOT/scripts/foundry-test.sh"
   python3 "$CLAUDE_PLUGIN_ROOT/scripts/foundry-ticket.py" done
   ```

7. **Open one PR, seek review, deliver.** One review pass by someone other than the author, then merge
   on green (`/foundry:merge-when-green <pr-number>` only on your explicit say-so). Deploy on promote.

8. **Stop and hand off.** Leave a handoff comment on each unfinished issue naming the branch or PR,
   the evidence and the next action.

### Example A: a code task taken to Done

Issue #42 "Rate-limit the public API", owner `you`, Work type `code`:

```markdown
## What
Rate-limit the public API.
## Done means
npx playwright test tests/rate-limit.spec.ts
```

1. The planning owner sets #42 to Ready. You set In progress and run the `foundry-ticket.py start 42` step.
2. `/foundry:dispatch 42` builds it on a branch; `foundry-test.sh` records local-green for HEAD.
3. You open the PR (`Refs #42`); required checks and one review pass run; Status becomes Review.
4. Merge on green. The merge integrates the change; it is not acceptance.
5. You run the Done-means command yourself against the merged code and confirm the behaviour,
   then close #42 as `completed` with the PR and CI run linked. Status is Done.

### Example B: a document task accepted by its named owner

Issue #57 "Runbook: restore the database", Work type `document`, accepting owner `sam`. There is no
Done-means command, and none is invented:

```markdown
## What
Write the restore runbook.
## Acceptance criteria
Accepted by @sam: docs/runbooks/restore.md, steps rehearsed once.
```

1. Ready, then In progress. You draft `docs/runbooks/restore.md` on a branch and open one PR.
2. You link the PR and the rehearsal evidence and set Status to Review. Worker verification is
   complete; acceptance is pending and the issue stays open.
3. Sam, the named accepting owner, reads the revision in the PR and states acceptance on the issue.
4. After the merge, the issue is closed `completed` with Sam's acceptance and the merged revision
   linked. Status is Done. The accepting person's decision, not a command, made it Done.

## Expected results

- Your queue shows no stale In progress items; blockers are acknowledged in GitHub.
- Every Done issue has its accepting actor and evidence linked; a green check never stood in for a
  human decision.
- Anything unfinished carries a handoff comment another engineer can act on.

## Outstanding human decisions

- Which tasks are Ready and in what priority order.
- Acceptance of each outcome, by the named human.
- Any expedited exception to the capacity limit, approved visibly.
- Release sign-off, a practice and not a machine check.
- Reading the leader-board (`/foundry:leader-board`) is pending: lands with gn-15.

## If it fails

- `done` or `foundry-test.sh` fails: the Stop hook keeps the session working; fix the cause. A dirty tree
  is refused before tests run, so commit first.
- A push or non-draft PR is refused: local-green is not recorded for the current HEAD; re-run
  `foundry-test.sh`.
- The queue shows nothing but GitHub is unreachable: report the failed check, do not call the inbox
  empty, and do not pick new work from a stale list.
- More at [diagnose-and-recover.md](diagnose-and-recover.md).
