# Acme Links (worked example) — the 7-step tutorial

> **Scope.** Everything in this directory is about the **Acme Links demo app**, the worked
> example shipped with this template. Your own project's setup lives in
> [`docs/SETUP.md`](../SETUP.md).


A linear, copy-along tutorial: build **Acme Links** (a link shortener with accounts) from an
empty repository to a governed, live-proven merge — the same way the framework builds itself.
Each step is its own `git checkout`-able checkpoint in the
[`acme-links`](https://github.com/lukasrepublic/acme-links) repo, and every prompt you'll run is
recorded verbatim in [`PROMPTS.md`](../../specs/features/acme-links/PROMPTS.md).

> **The one idea.** A green checkmark — "it compiled, the PR is ready" — does not mean the
> feature works. Foundry's contract journeys drive your *running* app at the seam your
> acceptance contract names, and the floor **refuses the merge** while they're red —
> `status ≠ functional`, proven by machine. Step 5 makes that visceral.

## What you build

A real app, not a toy: signed-in users create short links (`/r/<slug>` → a long URL) and see
per-link click counts on a dashboard; anyone can follow a short link. Auth + DB + UI — every
surface the gate cares about.

- **Stack:** Next.js (App Router) + TypeScript · Postgres + Drizzle · Better Auth (email+password)
  · Tailwind v4 + a design system built in Claude Design.
- **Atoms** (vertical slices, each authorized + gate-walked): `auth` · `create-link` ·
  `resolve-redirect` (the money shot) · `dashboard`.

## The steps

| Step | Title | Checkpoint |
|---|---|---|
| [1](step-1-scaffold.md) | Install + scaffold from the template | `step-1` |
| [2](step-2-specs.md) | Author specs + the spec review | — |
| [3](step-3-design.md) | Design the UI with Claude Design (two-surface audit) | — |
| [4](step-4-authorize.md) | Authorize the acceptance contracts | — |
| [5](step-5-money-shot.md) | **The money shot** — the floor blocks a broken seam, then admits the fix | `step-5` |
| [6](step-6-autonomous.md) | Kick off the autonomous buildout | `step-6` |
| [7](step-7-provenance.md) | Provenance + the citation graph | `step-7` |

## How to read it

Run it top to bottom. Every step shows: **the goal**, **what you run** (commands + the verbatim
prompts), **what to expect** (the checkpoint that proves it), and the tag to `git checkout` if you
want to jump in. The example specs the tutorial produces live under
[`specs/features/acme-links/`](../../specs/features/acme-links/) — read them alongside.

Prereqs: Node ≥ 22, Docker (for Postgres), a [Claude Code](https://claude.com/claude-code) session,
and a `claude.ai/design` login for step 3.

## See the whole journey first

If you'd rather read what actually happened before doing it yourself,
[**The full journey — how Acme Links was actually built**](BUILD-JOURNEY.md) is the build log:
every command and prompt in order, from empty workspace through requirements, audits,
authorization, buildout and security review, to the provenance pin — including the three security
Blocks caught before merge and the two defects found by *running* things that reading had missed.

## Reading the finished build instead

Every step's checkpoint is a tag in the [`acme-links`](https://github.com/lukasrepublic/acme-links)
repo, so you can read the destination before walking to it:

```bash
git clone https://github.com/lukasrepublic/acme-links && cd acme-links
git log --oneline --graph          # one merged PR per atom, behind the floor
git show step-5                    # the checkpoint where the stub was blocked, then fixed
cat .foundry/build-provenance.yaml # every atom pinned to its frozen contract
```

The stub-then-fix in step 5 is real history, not a screenshot: the first commit on that
branch shipped `GET /r/:slug → 200 'ok'` and CI refused it; the second made the same
check green.
