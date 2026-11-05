# Work with Foundry each day

The daily cycle for one operator: refine and mark Ready, start work, service blockers, verify, get
review and acceptance, deliver, stop and hand off. Two worked examples follow: a code task and a
document task, each taken to Done.

The states, eligibility, completion meanings and request rules are defined in
[`../../OPERATING-MODEL.md`](../../OPERATING-MODEL.md); this guide only shows how to act on them.
Checked against foundry `release/2.0.0` at `7681b90a`. One operating mode: a solo developer works this
way as a team of one.

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
   your own, unblocked, Ready tasks. The owned-queue verbs select for you: `scripts/foundry-ticket.py next` shows your next item,
   then `claim` (a lease that expires without a heartbeat; `claims.expires_after`, default 2h),
   `reconcile` (also the heartbeat) and `lead` (`acquire|renew|release|check`).

3. **Start the Command Deck** to run workers and inspect requests. Use `/foundry:command-deck start|status|stop|tick`.
   Without it, use the manual path in
   [diagnose-and-recover.md](diagnose-and-recover.md#operate-manually-without-command-deck).

4. **Service blockers first.** A request that blocks someone is acknowledged in GitHub and acted on
   before routine work. A non-blocker gets a visible target date, and a reschedule keeps the original
   target.

5. **Write the Design before the build.** The ticket carries `## Design` (components, what it reuses,
   the rule ids it cites), `## Security` (rule ids, or `none:` and why) and `## Surfaces` (one line per
   surface, or `n/a:` and why). On an architecture or security path, a declared trust boundary or a
   `size:L` ticket, `start` refuses without a Design that cites an existing rule id (`design-required`).
   Find the ids with `foundry_governance.py applicable --paths <path> ...`.

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/foundry_governance.py" applicable --paths src/auth/login.py
   ```

   Editing a CI path (workflows, CI scripts, test configs) is the operator's call per ticket:
   `foundry-ticket.py ci-allow <path>`. A performance or request-count budget is a command you run and
   report, not a required check.

6. **Start a task**, set its Status to In progress, then:

   ```bash
   python3 "$CLAUDE_PLUGIN_ROOT/scripts/foundry-ticket.py" start <issue-number>
   python3 "$CLAUDE_PLUGIN_ROOT/scripts/foundry-ticket.py" status
   ```

7. **Verify locally** before the first push:

   ```bash
   bash "$CLAUDE_PLUGIN_ROOT/scripts/foundry-test.sh"
   python3 "$CLAUDE_PLUGIN_ROOT/scripts/foundry-ticket.py" done
   ```

8. **Open one PR, seek review, deliver.** One review pass by someone other than the author, then merge
   on green (`/foundry:merge-when-green <pr-number>` only on your explicit say-so). Deploy on promote.

9. **Stop and hand off.** Leave a handoff comment on each unfinished issue naming the branch or PR,
   the evidence and the next action.

### The deck's report, STALL and pause

Each Command Deck tick ends with one four-block report: a first line (local date and time, how much is
done), then **Your decisions**, **Building now**, **Needs you** and **Ledger**. It is short on purpose
(`report.max_lines`, default 8) and names the coordination channel "the shared message log". A tick that
merged nothing and verified nothing prints `STALL:` and the reason; read that line first. The renderer
and the pause switch are `scripts/foundry_deck_report.py` (pending: lands with gv-13):

```text
pause   foundry_deck_report.py pause --until "<what must happen>" --reason "<why>"   (pending: lands with gv-13)
resume  foundry_deck_report.py resume                                              (pending: lands with gv-13)
state   foundry_deck_report.py state                                               (pending: lands with gv-13)
```

A paused deck starts no new fan-out until you resume it. Pause states what you are waiting for.

### Before and after every production change

A change to a live environment is stated first and reported after, in the shared message log. The
wrapper `scripts/foundry_prod_step.py` (pending: lands with gv-13) posts `PROD-BEFORE`, runs your command
after `--`, then posts `PROD-AFTER`, or runs your cleanup and posts `STOP` on failure. If the before
line cannot be posted, the command does not run. Approve each call; never persist an "always allow" for it.
Check the log for unpaired lines with `foundry_message_log.py audit`.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/foundry_message_log.py" audit
```

### Command shape in a session

Hooks refuse the shapes the permission layer cannot read ahead of time: no `cd` (use
`git -C <absolute-dir>` and absolute paths), `rm` only inside the session scratch directory, no packed
`bash -c` scripts or code heredocs (write the script to a file and run it by name), and no command that
reads a secret value. There is no off switch. The hooks are `hooks/foundry-shell-shape.py` and
`hooks/foundry-secret-read-guard.py`.

### Example A: a code task taken to Done

Issue #42 "Rate-limit the public API", owner `you`, Work type `code`:

```markdown
## What
Rate-limit the public API.
## Design
Components: src/api/middleware/**. Reuses: the existing token-bucket helper. Cites: <rule id>
## Security
none: no new credential or trust boundary
## Surfaces
api: new 429 response
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

Issue #57 "Runbook: restore the database", Work type `document`, accepting owner `owner-b`. There is no
Done-means command, and none is invented:

```markdown
## What
Write the restore runbook.
## Acceptance criteria
Accepted by @owner-b: docs/runbooks/restore.md, steps rehearsed once.
```

1. Ready, then In progress. You draft `docs/runbooks/restore.md` on a branch and open one PR.
2. You link the PR and the rehearsal evidence and set Status to Review. Worker verification is
   complete; acceptance is pending and the issue stays open.
3. `owner-b`, the named accepting owner, reads the revision in the PR and states acceptance on the issue.
4. After the merge, the issue is closed `completed` with the owner's acceptance and the merged revision
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
- Reading the leader-board (`/foundry:leader-board`), a read-only report.

## If it fails

- `done` or `foundry-test.sh` fails: the Stop hook keeps the session working; fix the cause. A dirty tree
  is refused before tests run, so commit first.
- A push or non-draft PR is refused: local-green is not recorded for the current HEAD; re-run
  `foundry-test.sh`.
- The queue shows nothing but GitHub is unreachable: report the failed check, do not call the inbox
  empty, and do not pick new work from a stale list.
- More at [diagnose-and-recover.md](diagnose-and-recover.md).
