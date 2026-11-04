# The operating model — one page

**One artifact per change: a ticket with a runnable "Done means". The platform is the gate.**

Why this page replaces a spec-first pipeline: measured on two adopter workspaces over 60 days, the
default path produced 1.5 to 8 lines of paper (specs, contracts, manifests, reports) per line of
shipped code; one app repo took 890 pull requests in 56 days, each a 32-minute CI run, and every
merge deployed to staging. The paper did not make the code better. The check does.

## The unit of work is a ticket

A GitHub issue (or your forge's equivalent), one screen at most:

```
## What
Repoint beta DNS to the new load balancer.
## Why
The old one is being decommissioned Friday.
## Done means
```
dig +short beta.example.test | grep -q 203.0.113.10 && curl -fsS https://beta.example.test/healthz
```
## Paper allowed
docs/runbooks/dns.md
```

- **`Done means` is a command, not a sentence.** The agent runs it before it stops, the reviewer
  runs it, and the operator runs it for sign-off. If it cannot be written as a command, the ticket
  is not ready.
- **`Paper allowed`** lists the documents this change may touch. Nothing else under `specs/`,
  `docs/`, `status-reports/`, `charters/` or `.foundry/` is written for this ticket; the plugin's
  paper guard refuses it.
- **Assignment is the authorization.** The operator's standing grant is recorded once in
  `.claude/foundry-operators.json` (`standing_authorization: true`), never re-asked per change.

Start it in the session: `python3 "$CLAUDE_PLUGIN_ROOT/scripts/foundry-ticket.py" start <issue>`.

## The loop

1. **Branch** from `main`: `git switch -c <ticket>-<slug>`. One ticket, one branch, one PR.
2. **Build** on the branch. Commit as often as you like; nothing on a branch runs CI.
3. **Local-green** before the first push: `bash "$CLAUDE_PLUGIN_ROOT/scripts/foundry-test.sh"`
   runs the repository's own test command and `Done means` until both pass. In a container this is
   the real stack, not a mock. The git-discipline hook refuses the push until this has passed for
   `HEAD`. CI confirms; it does not discover.
4. **One draft PR** per ticket. CI does not run on drafts (see [`templates/ci.yml`](templates/ci.yml)).
5. **Ready when `Done means` passes.** Mark the PR ready for review; CI runs once.
6. **One review pass** by a reviewer that is not the author — correctness and requirement gaps,
   one round. The security reviewer joins on auth / secrets / custody / supply-chain paths.
7. **Merge on green.** Branch protection with required checks decides; no `--admin`, ever.
8. **Deploy on promote**, not on merge: a `v*` tag or a `deploy/<env>` label builds the image and
   writes back to GitOps. A merge to `main` is integration, not a release.
9. **Close the ticket with the `Done means` output.** That is the record. Then delete the branch —
   after `origin/main` contains the merge, never before.

## The floor (never relaxed)

- Branch protection + required CI checks on `main`; PR-then-merge; no force-push.
- Security review, in a separate context, on any auth / secrets / custody / supply-chain change.
- The leak guard on anything public.
- The operator's own walkthrough before a release is called delivered.

## What is deliberately absent

No acceptance contracts, hash freezes, per-change authorization, audit ledgers, spec-review
rounds, release manifests, wave-state files, provenance markers, status reports, charters or
watcher ticks on the default path. Each of them was built to make an agent trustworthy; measured,
each produced paper that the operator read instead of code the operator ran.

## When a spec is still used

A spec is **opt-in and chosen by the operator**, never by the agent, in two cases:

- the ticket carries `security: true` (auth, secrets, custody, supply chain), or
- the design is too large for one ticket's `Done means` and needs to be agreed before it is built.

Then the spec lives under `specs/features/…`, and the spec-lane verbs (`/foundry:intake`,
`/foundry:spec-review`, `/foundry:authorize`) apply to that spec only. The tickets it decomposes
into still follow the loop above. Everything else ships without one.

## The agent's conduct

- **Do not stop on reversible work.** The Stop hook runs `Done means`; while it fails the session
  continues (three refusals, then it may end with the ticket still open and the failure named).
- **Do not ask what prior art plus sensible defaults can answer.** Ask only on an irreversible,
  security or authorization-adjacent fork, and name the exact decision.
- **Proposing governance machinery is a defect.** A new hook, gate, ledger, sign-off, status
  report, "commentary PR" or programme is not an improvement; the ticket and its check are the only
  artifacts the agent creates unasked.
- **Measure, don't report.** `python3 "$CLAUDE_PLUGIN_ROOT/scripts/foundry-delivery-metrics.py"`
  prints one line per repo per week: paper:code, PRs merged, lead time. If paper:code rises above
  0.3 in a workspace, the next ticket is "delete paper", not "write more".

## Where the rest lives

- Branch and PR rules, enforced by the git-discipline hook: the plugin's `context/branch-discipline.md`.
- The CI template for a code repo (skips drafts, cancels superseded runs, deploys on promote):
  [`templates/ci.yml`](templates/ci.yml).
- The workspace layout and the multi-repo control plane: [`README.md`](README.md),
  [`docs/control-plane.md`](docs/control-plane.md).
