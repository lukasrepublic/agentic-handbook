# The Command Deck watcher

A single prompt, re-fired on a schedule, treating a release manifest as a work queue. Each firing is
a **tick**: re-measure state from disk, dispatch what the dependency graph has unblocked, verify
what finished, land what passes, report in a fixed shape. Hand it one authorized programme and walk
away.

You can arm it **today**, on this workspace, with no capability built at all. Everything it needs
ships here.

| file | what it is |
|---|---|
| [`tick-prompt.template.md`](tick-prompt.template.md) | **the runnable half** — fill in the placeholders, arm it on a schedule |
| [`../../scripts/command-deck-status.py`](../../scripts/command-deck-status.py) | the measurement script the tick runs. No model in the loop |
| [`state.example.yaml`](state.example.yaml) | the programme state file the script reads — copy it to `command-deck/<programme-id>/state.yaml` |
| [`creation-brief.md`](creation-brief.md) | **the other half** — a creation brief for building the watcher as a first-class capability, if you would rather have mechanism than a prompt |

Compiled from measured runs, not from recollection: one 17-hour unattended run driving a 16-atom
infrastructure release across three repositories, a prior 12-hour run recorded as the brief's
sixteen operational cases, and several hundred topic files of accumulated session learnings.

---

## 1. The finding that shapes it

The dominant failure of an autonomous loop is **not** that the agent does the wrong thing. It is
that **the agent measures, and the measurement is confidently wrong.** Roughly **35 of ~60**
portable learnings mined from prior runs are instances of this single shape:

| the instrument said | what was actually true |
|---|---|
| "does not exist" | the tree was stale |
| "check passed" | the check had not concluded |
| "floor cleared" | the floor was silently skipped |
| "here is the data" | it was a permission denial |
| "0 findings" | the population was empty |
| "measured OK" | the measurement had expired |
| `0` | the value was `null` |
| *(nothing, exit 0)* | the command ran in the wrong directory |

Which yields the single most valuable rule in the template:

> **Every instrument you rely on must be able to distinguish "I looked and found nothing" from
> "I could not look" — and if it cannot, it is not an instrument.**

That is why §0b is the longest section of the prompt, and why the shipped measurement script
refuses rather than printing a zero.

---

## 2. How it is armed

The agent holds **no** state between ticks — it re-derives it every time from files a script can
read. An agent that trusts its previous tick accumulates drift; one that re-measures cannot.

Three pieces:

1. **A scheduler.** In Claude Code, `CronCreate` with a five-field expression. Two properties bite:
   jobs are **session-only** (nothing on disk — so real state must live in files, never in the job),
   and recurring jobs **auto-expire after 7 days**. Pick an off-minute: `3,13,23,33,43,53` beats
   `*/10`, which lands every user on the same instant.
2. **A measurement script.** `scripts/command-deck-status.py`. Reads the manifest and a state file,
   shells out to `git`, prints completion, **its denominator**, the **commit it measured**, and
   elapsed. **No model in the loop.**
3. **The prompt.** [`tick-prompt.template.md`](tick-prompt.template.md).

### The shape that works, and the one that does not

Measured across the sessions where this pattern actually drove releases:

- **The watcher is the operator's own main session, woken by a recurring cron job.** It therefore
  *has* the operator's authority by construction and never has to be handed it.
- **It is never a subagent.** Packaging operator authority into a prompt and delegating it to an
  `Agent` is the exact shape a permission classifier is built to refuse — and refusing it is
  correct. Subagents are dispatched *by* the tick, as narrow implementers and reviewers with
  explicit "do not commit / do not authorize / do not merge" briefs.
- **It is never a background shell loop.** No `tick.py`, no `while true`. The tick is a wake-up of
  the main session, not a process.
- **The scheduling permission comes from the operator**, once, via `/permissions`. Self-granting is
  blocked, correctly, and the loop should surface the denial as its single blocker rather than
  route around it.
- **Editing the prompt is `CronDelete` then `CronCreate`.** Rewriting the standing prompt every time
  the deck learns a rule is why the prompt gets good — the first working one was 12 lines, the last
  was 60 lines of scar tissue.

---

## 3. What earned its place — measured

| rule | what it caught | count |
|---|---|---|
| Verify every worker report by execution | a defect in **every** atom; workers reported green, independent re-runs disagreed, and both were right for reasons that were the finding | 11 |
| Print the denominator | turned "no findings" into a checkable claim; one sweep looked systemic at 12 hits and was a singleton, another was the reverse | 4,617 rows |
| Census before action | idle capacity repeatedly — including two items never dependency-blocked at all, just missing their specs | 2 |
| Hunt the gate that exits 0 and evaluates nothing | named in the prompt, so it was hunted rather than stumbled on | 6 |
| Never trust a cached number | a measurement against a checkout 175 commits stale — the exact error a worker had been corrected for hours earlier | 2 |
| Blockers are operator-actionable only | kept a five-item escalation list honest across 40+ ticks | 5 |

**The strongest single line:** *"Agents without a shell have no measurements: their counts, their
'0 findings' and their claimed defeating inputs are estimates until you run them."* Every
non-executing agent produces confident, well-formatted, unverified numbers. Treating those as
estimates is the difference between a loop that compounds error and one that removes it.

### Four gaps a long run exposed, all closed in the template

- **No termination condition** — the programme finished and the watcher kept firing; eight identical
  ticks before it was stopped by hand. → §7.
- **Directory pinning too weak** — the prompt said `cd` at the start of every call and it *still*
  went wrong twice. Once silently: the script was absent from the wrong directory, the error went to
  stderr, and **the command exited 0 with no output** — precisely the defect class the same prompt
  warns about elsewhere. → §0b, and the shipped script's `--self-test`.
- **No shared-machine clause** — concurrent sessions collided over a shared append-only ledger
  twice, each rebuild silently dropping the other's rows. → §4 SHARED MACHINE.
- **Anchoring reviewers** — telling a reviewer to "treat this as settled so we do not diverge"
  destroyed the independence it was dispatched for. It reversed a *correct* finding and reported the
  coordinator's own error back as confirmed. → §4 WORKERS.

---

## 4. Setup checklist

1. **Create the state file.** Copy [`state.example.yaml`](state.example.yaml) to
   `command-deck/<programme-id>/state.yaml` and fill in one entry per manifest atom. This survives
   the session; the cron job does not.
2. **Run the measurement script** and read every line of its output:
   ```bash
   python3 scripts/command-deck-status.py <programme-id>
   ```
3. **Break it on purpose** — this is not optional, it is the instrument test:
   ```bash
   python3 scripts/command-deck-status.py <programme-id> --self-test
   ```
   It re-runs itself from a directory that is not the workspace and asserts it refuses loudly
   instead of printing nothing and exiting 0. A silent empty tick is otherwise waiting for you
   somewhere in the run.
4. **Fill §4 of the prompt properly.** Start from the generic clusters, then add every
   project-specific trap a worker has already hit twice. This is where the loop's real quality
   lives.
5. **Arm the cron on an off-minute.** 10 minutes suits sub-hour work units; longer units want 20–30.
   Remember the 7-day auto-expiry and the session-only lifetime.
6. **Watch the first three ticks, then leave it.** If the first three are honest about what is idle,
   the rest will be. If tick one manufactures work, §6 is not strong enough yet.

---

## 5. Why §5 of the prompt is deliberately stale

Counter-intuitive and load-bearing. The state snapshot in the prompt goes stale within the hour —
but it carries *"re-measure, do not trust this line"*, which turns it into a **decoy that trains the
habit**. Over one long run it stated 10 merged for seven hours while the truth reached 16, and the
instruction caught it on every single tick. Do not "fix" it by keeping it current; that removes the
training signal and replaces it with a number the agent will start trusting.

---

## 6. Deliberately omitted, so it is not re-derived

The learnings sweep surfaced several clusters that look tempting and were left out on purpose:

- **Checkpoint-authoring taxonomies** (non-discriminating oracles, non-terminating regex,
  doc-satisfies-control, unscoped counts). Genuinely portable, but they belong in a
  spec/contract-authoring prompt, not a tick loop.
- **Shell-in-YAML quoting traps** (`printf` newline mangling, `sed` bracket negation, the zsh
  `$VAR[` subscript, control characters in YAML surfaces, nested `zsh -c` quoting). Collapsed into
  the one §0b clause about instruments that under-scan silently.
- **Frozen-contract amendment mechanics** and `allowed_paths` scope-grant semantics. Excellent
  rules, but they presuppose a particular freeze/re-authorization model.
- **Artifact-production conventions** (diagram verification, output locations, version literals).
  Portable in spirit; none is a tick-loop failure.
- **Project records naming specific infrastructure.** Not portable by construction — that is what
  `{{PROJECT-SPECIFIC}}` is for.

One near-miss worth reconsidering if this ever grows an *evidence decay* section: *losing an
environment costs latency evidence, not safety evidence — leak, ordering and shape claims are almost
always statically re-derivable.*
