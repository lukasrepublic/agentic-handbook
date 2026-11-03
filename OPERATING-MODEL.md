# The operating model — one page

**GitHub owns the plan. One accountable human per task, a runnable "Done means", and the platform as the gate.**

Why one page: measured on two adopter workspaces over 60 days, the default spec-first path produced
1.5 to 8 lines of paper (specs, contracts, manifests, reports) per line of shipped code, and the paper
did not make the code better. So planning, ownership, priority and dependencies live in GitHub Issues
and Projects, where every engineer can see and change them; the workspace keeps instructions and
code. Where this page says "pilot default", the value is a starting point the team may change in
writing, not a rule of the platform.

On a user-owned repository, issue types and custom issue fields are not available (they are
organization features), so a pilot there uses labels and Project fields. The meanings below do not
change with the mechanism.

## The five states

Each executable task is one issue. Its state is the Project `Status` field.

| State | Meaning |
|---|---|
| Backlog | A candidate outcome, not approved for execution. Refinement happens here. |
| Ready | The planning owner has set priority, owner, dependencies and adequate acceptance criteria. |
| In progress | The owner's deck has started the task and recorded its execution reference (branch or draft PR). |
| Review | The work awaits the required review or acceptance. |
| Done | The stated outcome has been accepted, with evidence appropriate to its type. |

A blocker is a relationship, not a sixth state: see [Operator requests and blockers](#operator-requests-and-blockers).
Cancelled or duplicate work is closed but is not Done; see [Completion meanings](#completion-meanings).
Agents may draft and organise Backlog items and supporting documents. They do not decide what is Ready.

## Ownership and Ready

- **Each executable task has exactly one accountable human owner**, recorded as its single assignee.
  The owner is accountable for the result, not necessarily the one who types the code.
- **Only the planning owner moves a task to Ready.** Ownership plus Ready is the assignment. Ready is
  a scoped development instruction under existing permissions, not an expansion of infrastructure
  access or release authority. Moving a task back to Backlog records that the instruction is withdrawn;
  a comment or a routine state change does not.
- A task records: the intended result, why it matters, the owner, priority, dependencies, acceptance
  criteria, the target repository or document, and links to relevant context. One screen:

```
## What
Repoint beta DNS to the new load balancer.
## Why
The old one is being decommissioned Friday.
## Done means
dig +short beta.example.test | grep -q 203.0.113.10 && curl -fsS https://beta.example.test/healthz
## Context
Runbook: docs/runbooks/dns.md
```

- **One document per decision.** Architecture, security and operations knowledge is linked from the
  work and has one current version: a Git file or an issue artifact, never both maintained in parallel.
  Executable things (code, tests, infrastructure, CI) stay in Git. Agent scratch work stays local.

## Eligibility and capacity

An operator or deck selects new work only when the task is:

1. **owned** by that operator (never unassigned, never another operator's);
2. in **Ready**;
3. **unblocked** (`is:blocked` finds the rest);
4. **in the configured scope** (repositories or projects the operator named);
5. supported by **adequate acceptance criteria and repository or document context**.

The deck resumes known, still-authorised owned work before it picks new work, and rechecks ownership
and readiness before starting. In-progress work and Review follow-up continue without returning to
Ready. It does not claim unassigned tasks, take over a colleague's, or reprioritise the backlog.

**Capacity (pilot default): two started, unfinished outcomes per operator**, counting Review and
blocked work. Moving a task to Review does not free a slot; cancelled and duplicate work leaves the
count once its disposition is recorded. An **expedited** exception is allowed only if it is visible
on the issue: a label and a one-line comment naming who approved it and why. It is never a silent
increase of the limit.

## Completion meanings

Five things are kept distinct: **worker verification** (the checks and the Done-means command pass),
**outcome acceptance** (the owner or named accepting human accepts the stated outcome), **merge**,
**deployment**, and **release sign-off**. Each GitHub signal below carries exactly one meaning.

| Signal | Means | Does not mean |
|---|---|---|
| Issue open | The outcome is not yet accepted. This includes Review while a human decision or a deployment is outstanding. | Anything about merge. |
| Issue closed, `completed` | The outcome was accepted at its agreed scope; the accepting actor and evidence are recorded. | Deployment or release sign-off, unless that was the scope. |
| Issue closed, `not_planned` | Cancelled. Not accepted, no throughput. | Done. |
| Issue closed, `duplicate` | Duplicate of a linked issue. Not accepted, no throughput. | Done. |
| Reopen | A quality event on an accepted outcome. | New throughput; later reacceptance does not count again. |
| Project status Review | Worker verification is complete; review or acceptance is pending. | Accepted. |
| Project status Done | Outcome accepted; matches `completed`. | A cancelled or duplicate closure. |
| PR merge | The change is integrated. | Acceptance, deployment, or release. |
| Deployment record | The change runs in the named environment, with verification evidence linked. | Release sign-off. |
| Release sign-off | The operator's own walkthrough, the last step of delivery. A human practice; no check claims it ran. | Anything a CI job can show. |

Rules that follow:

- If a human decision or a deployment promise is outstanding, the issue stays **open in Review**
  after checks pass. Close-on-merge (a closing keyword in the PR) is used **only where the merge
  satisfies the outcome's agreed scope**; configure Project automation so it cannot mark an
  outstanding decision accepted.
- When an implementation and a release have different acceptance scopes, they are separate issues;
  the release issue stays open until integration, environment verification and the operator's
  walkthrough are done.
- Review readiness links evidence another operator can open: the PR, the CI run, the accepted document
  revision, or the environment observation. A local path or a worker's "passed" is not evidence.

## Operator requests and blockers

A request is an action, review, decision or approval that one operator needs from another. Receiving a
request grants no permission to run arbitrary instructions, and an approval request is never answered
by the deck on the human's behalf.

- **Route it through a recipient-owned issue or PR** that already represents the action; otherwise
  open a small request issue **assigned to the target** and link it to the requester's task. The
  requester keeps their own task. Keep the source (comment, review request) identifiable so a repeated
  scan does not create a duplicate. An informational mention is not a task.
- **A blocker is the native blocked-by dependency**: the requester's task is "blocked by" the request
  issue. The request is a blocker from the moment it is both blocking and targeted at that operator.
- **Blockers are immediate.** The recipient's deck acknowledges in GitHub, alerts its operator at once
  (even if agents can fix it alone), states the exact need and the affected work, and starts permitted
  resolution ahead of routine work. A request is resolved when the dependency is actually satisfied,
  not when it is read, acknowledged or an agent started.
- **Non-blockers** are acknowledged and given a visible target date or iteration in the operator's
  ordered queue. A reschedule is recorded; **the original target is preserved**. If the request later
  blocks someone, it becomes a blocker, needs a fresh blocker acknowledgement and alert, and shows as
  unacknowledged until that happens.
- **Order competing blockers by affected-work impact, then priority, then age** (pilot default). This
  orders execution only; it never delays the alert. A **dependency cycle** or conflicting priorities
  escalates to the planning owner.
- **Handoff.** On stop or reassignment the deck stops dispatching under the old assignment, preserves
  uncommitted work, and records the current task, branch or PR, evidence and next action in the issue
  before reporting handoff complete. Later results from stopped workers are checked against current
  ownership before anything is reported done. If GitHub is unreachable, report the failed check, do
  not call the inbox empty, and do not pick new work from a stale queue.

## Metrics conventions

Events come from native GitHub records first. Where native history lacks the event, record it as a
structured comment on the existing issue, one line of JSON in an HTML marker:

```
<!-- foundry-deck: {"v":1,"event":"ack","idempotency_key":"<unique>","target":"<login or issue>","blocking":false,"at":"<UTC time>","by":"<login>","evidence":["<url>"]} -->
```

The comment is a log line, not a second backlog or approval ledger. The `idempotency_key` keeps a
repeated scan from writing it twice.

| Event | Source |
|---|---|
| Ready | Project `Status` change to Ready (or the `ready` label). The first one counts; going back to Backlog does not reset it. |
| Start | Project `Status` to In progress, with the connected branch or draft PR. First start counts; pauses and ownership changes do not reset it. |
| Acceptance | Issue closed with `completed` (or Status Done), with the accepting actor and an evidence link. Merge alone counts only where it satisfies the agreed scope. |
| Request and commitment | The request issue and its blocked-by link (native). Target and any later schedule change: `foundry-deck` event `scheduled` (a later change: `rescheduled`, carrying `original_target`). |
| Request acknowledgement | `foundry-deck` event `ack` on the request. |
| Blocker acknowledgement | `foundry-deck` event `blocker_ack`, at or after the request became blocking and targeted. An earlier `ack` does not count. |
| Verified resolution | `foundry-deck` event `resolved` with evidence that the dependency is satisfied; a read notification or automated reply does not. |
| Assignment intervals | Native assigned and unassigned timeline events. |
| Handoff | `foundry-deck` event `handoff` naming the next owner and evidence. |
| Review readiness | `foundry-deck` event `review_ready` with the PR and CI-run links; `accepted` records the accepting actor and evidence where closure alone is not the scope. |
| Cancellation, duplicate, reopen, reacceptance | Native closed (`not_planned`, `duplicate`) and reopened events; reacceptance is distinct from first acceptance. |

- **Work types**: `code | architecture | security | operations | document`, as a label or Project field.
- **Identity**: a GitHub login maps to an operator id through the `github` field of
  `.claude/foundry-operators.json`. Attribute completion to the assignee at the time of the event,
  not today's assignee or a bot's authorship; consumption belongs to whoever consumed it.
- **Reading reports** (`/foundry:leader-board`): they show scope, window, sample sizes and coverage
  gaps; missing history is "unavailable", not zero. Throughput and token counts are never personnel
  scores. Use the report to find team bottlenecks and trends, then look at the contributing tasks.
- **Weekly improvement review** (lightweight, pilot): look at review effort, interruptions, manual
  coordination, confidence and rework next to the report, check the intended customer or operational
  result, and pick one concrete workflow improvement to try. The operator names who convenes it.
  It is not surveillance and not a ranking.

## Done means and acceptance

`Done means` is a command, not a sentence, for work a command can check. The agent runs it before it
stops, the reviewer runs it, the operator runs it for sign-off. **A passing Done-means command is
worker verification, not human acceptance.** Where acceptance needs a human decision, the work waits
in Review for that decision; a green run does not stand in for it.

**A document outcome** (a decision record, a runbook, a security assessment) may omit the command. It
names an **accepting owner** and the reviewable result (document and revision); that owner's
acceptance is the Done event. Operations work links its rehearsal or environment evidence.

## The loop

1. **Branch** from `main`: one task, one branch, one PR.
2. **Build.** Commit as often as you like; nothing on a branch runs CI.
3. **Local-green** before the first push: `bash "$CLAUDE_PLUGIN_ROOT/scripts/foundry-test.sh"` runs the
   repository's tests and `Done means` until both pass. CI confirms; it does not discover.
4. **One draft PR** per task; CI does not run on drafts (see [`templates/ci.yml`](templates/ci.yml)).
5. **Ready for review** when `Done means` passes; CI runs once.
6. **One review pass** by someone who is not the author. Security review in a separate context on
   auth / secrets / custody / supply-chain paths.
7. **Merge on green.** Branch protection with required checks decides; no admin bypass, ever.
8. **Deploy on promote**, not on merge: a `v*` tag or a `deploy/<env>` label. A merge is integration.
9. **Accept and close** with the evidence linked, per [Completion meanings](#completion-meanings).
   Delete the branch only after `origin/main` contains the merge.

## The floor (never relaxed)

- Branch protection and required CI checks on `main`; PR-then-merge; no force-push.
- Security review, in a separate context, on any auth / secrets / custody / supply-chain change.
- The leak guard on anything public.
- The operator's own walkthrough before a release is called delivered.

## The agent's conduct

- Do not stop on reversible work; do not ask what prior art and sensible defaults can answer. Ask only
  on an irreversible, security or authorization-adjacent fork, and name the exact decision.
- Proposing governance machinery is a defect: a new gate, ledger or programme is not an improvement.
- Measure, do not report: `foundry-delivery-metrics.py` prints one line per repo per week.

Where the rest lives: branch rules in the plugin's `context/branch-discipline.md`; the CI template in
[`templates/ci.yml`](templates/ci.yml); workspace layout in [`README.md`](README.md) and
[`docs/control-plane.md`](docs/control-plane.md).
