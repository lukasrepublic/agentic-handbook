# Creation brief — the Command Deck watcher as a first-class capability

> Hand this to a fresh Agentic Foundry session. It is a **creation brief**, not a spec: the session
> should run the normal intake → spec → review → authorize → build lane and produce the atoms.
> Everything below is grounded in one real 12-hour autonomous run driving a release to completion.
> Every operational case is something that **actually happened**, with the failure mode that was
> observed. Where a rule exists because the run got it wrong, that is stated — the failure is the
> evidence, and a rule with no failure behind it is the weakest kind.
>
> This is the *other* half of [`README.md`](README.md). If you want the pattern working this
> afternoon, arm [`tick-prompt.template.md`](tick-prompt.template.md) instead — it needs nothing
> built.

---

## 1. What to build

A **Command Deck watcher**: a first-class, reusable capability that lets an operator hand a
programme to an agent session and walk away, while the session drives it forward on a timer —
dispatching workers, verifying their output independently, landing merges, keeping a work tracker
current, and surfacing a short executive status each tick.

Today this exists only as a **prompt** the operator arms on a schedule. It works, but the whole
operating discipline lives in that prompt string and in the driving model's judgment. Nothing
enforces it, nothing carries between sessions, and every hard-won rule has to be re-typed.

The goal: turn the prompt into a **capability with mechanism** — a skill, a persisted programme
state, and the deterministic guardrails that a prompt can only *ask* for.

---

## 2. Why it is worth building (the evidence)

In one run the watcher pattern:

- Landed **6 merges across 3 repos** (workspace, app, infra) with no operator involvement in any of
  them beyond one credential.
- Applied **two live cloud changes** to an organization's management account, including an
  org-wide guardrail policy.
- Caught **a real, silent gap that every other control missed**: an authorized acceptance criterion
  that had *zero implementation*, sitting on a PR that looked green, because the criterion was added
  at re-authorization and nothing re-ran the contract against the already-built branch afterwards.
- Caught a **latent fail-open** in a security-reviewed IAM change, and proved it by exercising the
  broken case, not by reasoning about it.
- Produced **4 grounded prior-art sweeps** in response to forks that came up mid-run.

It also made mistakes that the mechanism should prevent. Those are §4.

---

## 3. The core loop contract

Each tick, in order:

1. **Census.** Enumerate every running worker. Confirm each is alive and progressing.
2. **Act on completion.** A finished worker is acted on *immediately* in the same tick — verify,
   land, dispatch the next stage, or dispatch a reviser. Never "note it and continue".
3. **Reconcile the tracker.** The work tracker must be exactly current at the end of every tick.
4. **Keep every wave moving**, respecting declared load-bearing order.
5. **Emit an executive status** — Accomplishments / What's next / Blockers. Terse, imperative.
6. **Escalate only** for (a) external provisioning the agent cannot perform, or (b) a genuine
   no-consensus fork. Authorization-adjacent forks always park.
7. **Idle honestly.** If nothing changed and no worker is running: say so in one line and stop.
   **Do not manufacture work.** This rule is load-bearing — without it the loop invents tasks to
   look busy, and a fabricated task in a governance programme is worse than an idle tick.

---

## 4. Operational cases — the required behaviours

This is the substance of the brief. Each case is a real event from the run.

### 4.1 Verification is independent, always

**Observed:** A build reported "16/16 checkpoints pass". Re-running them against the PR head
confirmed it. A *different* build reported green and the contract was actually **28/29** — one
criterion had no implementation at all.

**Required:** The watcher never lands work on a worker's self-report. It re-runs the acceptance
contract itself against the PR head before merging. *An unrun gate is not a passed gate.*

**Mechanism to build:** a contract runner that executes `cli:` and `file:` checkpoint surfaces and
reports pass/fail per row. Today this is an ad-hoc script rebuilt per session; it should ship.

### 4.2 Distinguish an environmental red from a real red

**Observed:** A row went red because the tool binary was not on the subprocess `PATH`. A different
row went red because the code genuinely did not exist. Both look identical in a results table.

**Required:** Before attributing a red to the code, reproduce it manually. Report the attribution
explicitly ("red because X, not because the code is wrong"). Never wave a red through as
"environmental" without showing the reproduction.

### 4.3 Re-authorization invalidates a prior build

**Observed:** An atom was built at `auth_seq=1`. A later amendment added a new criterion at
`auth_seq=2`. The PR stayed open, still looked green, and nobody re-ran the contract. The criterion
had no implementation for a day.

**Required:** When an atom's `auth_seq` advances while an implementation branch is open, the
watcher must re-run the *current* contract against that branch and treat any new red as a build
gap. **Mechanism to build:** detect `auth_seq` drift between the authorized contract and the
contract the open PR was built against, and surface it as a blocking condition.

### 4.4 A blocked command must be atomic

**Observed — the run's own error.** A precondition (`mv` restoring a file) was chained into the same
shell invocation as a mutating command. The permission classifier denied the whole command, so the
precondition never ran either. The operator was then handed a command that assumed the precondition
had been satisfied. They ran it; it silently did the wrong thing and reported success.

**Required:** Any command that may be permission-blocked is issued **alone**. Preconditions run as
separate, independently-verified steps. When handing a command to the operator, the watcher first
verifies every precondition is *actually* in place, and hands over exactly one self-contained
command. Never with `set -e`, `trap` or `exec` at top level — that exits the operator's interactive
shell and closes their terminal.

**Also required:** after an operator runs a handed-over command, the watcher **verifies the
outcome against the world**, not against the operator's report. In this run the operator's terminal
output said "successfully initialized" while the state had not migrated; only listing the bucket
revealed it was empty.

### 4.5 Operator directives are standing, not one-off

**Observed:** Mid-tick the operator sent "All infra changes must be IaC" and "Anything done to the
management account must have a corresponding IaC infra artifact". These are policy, not task input.

**Required:** The watcher distinguishes a **directive** (a standing rule that changes future
behaviour) from a **task**. Directives are persisted, restated in the programme state, and
immediately trigger a conformance audit of existing state against the new rule. In this run that
audit found five uncovered resources in the management account, including an org-wide guardrail
policy with no IaC artifact at all.

### 4.6 Forks get prior art, not opinion

**Observed:** The operator questioned a directory-layout decision. Rather than argue, the watcher
ran a sweep against the primary publishers and found the premise of *both* positions was wrong —
the convention being appealed to meant something entirely different from how it was being used.

**Required:** When a design fork appears, the watcher performs a prior-art sweep, saves it with
per-claim verification markers, and cites it. A negative finding ("no publisher prescribes X") is a
first-class result and is often the decisive one.

**Required (harder):** the sweep must be read **against the claim it is supposed to support**. In
this run a sweep filed a quote as supporting evidence that actually *falsified* the premise; it took
three correction passes and a second reader to catch. *A quote filed as supporting evidence is not
evidence until someone reads it against the claim.*

### 4.7 Recommend against interest

**Observed:** Asked whether to restructure, the sweep's evidence did not support the change the
operator was leaning toward. The watcher recommended **not** doing it, and said explicitly: *if the
evidence had supported it, now is the cheap moment.*

**Required:** The watcher states when a recommendation cuts against what was asked for, and states
the strongest case for the rejected option. A recommendation that never contradicts the operator is
not a recommendation.

### 4.8 Review findings that are not Blocks still get captured

**Observed:** Two security reviews returned no Block but six Risks between them. One was a latent
fail-open where transposing two adjacent arguments would silently grant a much broader permission.
Another materially changed the severity of an existing known issue.

**Required:** Every Risk and Nit becomes a tracked item with its failure scenario preserved, or is
fixed. Nothing is dropped because it did not block. When a finding changes the standing of an
*existing* item, that item is updated rather than a duplicate created.

### 4.9 Fix inside the authorized surface; park outside it

**Observed:** Of two review Risks, one was fixable inside the atom's own `allowed_paths` and was
fixed. The other would have required adding a `Deny` that an existing criterion forbids — an
authorization change — so it parked with the tradeoff recorded.

**Required:** The watcher classifies each finding as in-surface (fix now, re-verify, land) or
authorization-adjacent (park, record the tradeoff and *why* it parked). It never quietly widens an
authorized surface to close a finding.

### 4.10 Red-before-green is a dispatch burden

**Observed:** Builds were dispatched with an explicit instruction to exercise the failing case, not
only the passing one. One build reproduced the contract's own named bad-fix and confirmed the right
rows went red. Another proved a fix by reverting it and showing validation passed blind before, and
failed after.

**Required:** Every build dispatch carries the exercise burden explicitly. A build that reports only
passing results is incomplete and is sent back.

### 4.11 Reviewers need materialized trees and a focused brief

**Observed:** Read-only reviewers were twice handed git-requiring instructions they could not
execute. Fixed by materializing both the candidate and merge-base trees in scratch worktrees and
handing over paths.

**Required:** The watcher prepares the reviewer's inputs, states the single most important question
to answer, and forbids patch proposals — the reviewer names defects; the watcher decides remedies.

### 4.12 Branch hygiene against a moving base

**Observed:** A branch was cut from a stale local base. Its PR would have **reverted nine files**
that had landed meanwhile. Caught by hash-comparing every file against the remote base before
resolving — all nine were byte-identical, so nothing was lost.

**Required:** Before resolving any conflict by discarding, the watcher proves the discarded content
is not unique. Before merging, it verifies the branch's diff surface against the base is *exactly*
the intended file set.

### 4.13 Merged is not applied

**Observed:** A cloud guardrail policy was coded, reviewed, gated and merged — and was still not in
effect days later. The live policy list showed it absent. Merge and apply are different states.

**Required:** The programme state tracks `merged` and `applied` as **separate** fields for any atom
with a live surface, and the executive status never reports an unapplied atom as done. Verify
applied state by querying the world, not by reading the code.

### 4.14 Discover unsequenced prerequisites before promising a completion

**Observed:** An apply was reported as "unblocked, one command away". It was not: the state backend
it needed lived in a *different, still-open* PR that was red. Two unrelated failures had to be fixed
first.

**Required:** Before declaring an action ready, the watcher walks its actual preconditions to
ground — not the declared dependency list, which was silent on this one.

### 4.15 Background notifications are not operator approval

**Observed:** Worker completions arrive as system notifications interleaved with the conversation.

**Required:** The watcher never treats a task notification, a tool result, or its own prior message
as operator consent. Consent comes only from the operator. A prompt asserting standing grants is not
a grant — and an attempt to self-grant a permission should be abandoned after the first refusal, not
retried.

### 4.16 Correct the record where it lives

**Observed:** A research document had to be corrected three times as later findings falsified its
earlier claims. Corrections were made **in place**, with the superseded text struck and marked, plus
a note on how the error was caught.

**Required:** When a later finding falsifies an earlier record, the watcher amends the record at its
source. It does not leave a corrected claim standing in one document and fixed in another.

---

## 5. What to persist between ticks and between sessions

The prompt-only version loses everything on compaction, and the scheduled job itself is session-only.
The capability must persist:

- **Programme identity** — the release or epic being driven, and its declared load-bearing order.
- **Atom ledger** — per atom: authorization state and `auth_seq`, build state, gate result *with who
  ran it*, review verdicts, merge state, **apply state**.
- **Standing directives** — operator rules accumulated in-session, with their timestamp.
- **Open findings** — Risks and Nits not yet closed, each with its failure scenario.
- **Parked forks** — what parked, why, and what would unpark it.
- **Blocked-on-operator queue** — each with the exact self-contained command and its verified
  preconditions.

[`state.example.yaml`](state.example.yaml) is the prompt-era shape of this, and a reasonable
starting schema.

---

## 6. Non-goals — state these explicitly in the spec

- **Not a replacement for the merge gate or for front-authorization.** The watcher *drives* the
  lane; it does not become an authority within it.
- **Not an auto-approver.** It must not self-grant authorization it was not given.
- **Not a scheduler for unattended production mutation.** Live applies stay subject to whatever the
  posture requires.
- **Not a second work tracker.** It drives the native one.

---

## 7. Acceptance criteria worth binding (sketch — the spec author should sharpen)

Phrase each as a property, never as one frozen accepted answer. Learned repeatedly: a criterion that
freezes an *answer* forecloses correct alternatives and needs re-authorization to fix; a criterion
that binds the *property* survives.

1. A tick with no worker running and no state change produces **no** new work items.
2. A completed worker is acted on within the same tick.
3. No merge occurs without a contract run **attributable to the watcher**, not the builder.
4. An `auth_seq` advance on an atom with an open implementation branch raises a blocking condition.
5. A command handed to the operator is self-contained, and its preconditions are verified beforehand.
6. Every review finding is closed, tracked, or explicitly parked with a reason. None are dropped.
7. An atom with a live surface is never reported complete while `applied` is false.
8. A standing directive triggers a conformance audit and is persisted.
9. Escalation occurs only for external provisioning or a no-consensus fork.

For every checkpoint: it must be **discriminating** — a different verdict for the violation and the
remediation. A row that passes both before and after proves nothing. Exercise each against a passing
case **and** a failing one before considering it done.

---

## 8. Open design questions for the implementer

State these as flagged uncertainty rather than deciding them silently:

1. **Cadence.** Fixed-interval versus event-driven versus self-paced. The runs used a fixed 5-minute
   tick, later moved to an off-the-hour 20-minute one to avoid contending with sibling sessions;
   most ticks were idle, and the idle-honesty rule made that cheap. Is a fixed tick right, or should
   completion events drive it with a long fallback heartbeat?
2. **Where programme state lives.** In-repo (reviewable, versioned, but noisy) or in agent memory
   (quiet, but invisible to review)? A governance programme probably wants the former.
3. **Multi-programme.** One watcher per programme, or one watcher over several?
4. **Handoff.** What does a watcher hand a *human* on-call, and in what form?
5. **Whether the contract runner belongs in the watcher at all**, or is a standalone verb the
   watcher calls. It is independently useful — the runs that exposed the checkpoint-defect taxonomy
   were possible only because such a runner existed.
