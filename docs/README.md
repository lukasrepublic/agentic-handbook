# Documentation index

Two kinds of document live here, and it is worth knowing which you are reading:

```
  ABOUT YOUR PROJECT                        ABOUT THE DEMO
  (use these to set up and run              (read these to learn the loop —
   your own workspace)                       none of it is your project)
  ────────────────────────────              ──────────────────────────────
  guides/            ◀ start here
  control-plane.md           example-acme-links/
  SETUP.md                                    ├── README.md          the 7-step tutorial
  architecture/                               ├── BUILD-JOURNEY.md   how it was really built
  command-deck-watcher/                       └── step-1 … step-7
```

## About your project

| Document | What it is |
|---|---|
| [**`../OPERATING-MODEL.md`**](../OPERATING-MODEL.md) | **The working agreement — read this first.** |
| [**`control-plane.md`**](control-plane.md) | **The control-plane guide — read this before running more than one repo.** This workspace is a *control plane* over your code repos: they live beside it as independent, gitignored sibling repos, and the factory dispatches into them. Covers the on-disk tree, the **session rule** (always start Claude Code at this root — and what silently breaks when you don't), building one atom across two repos, and day-two operations. |
| [**`guides/`**](guides/) | **The version-matched operating guides** (start with the one that matches your situation): [start a new project](guides/start-a-new-project.md), [adopt an existing codebase](guides/adopt-an-existing-codebase.md), [upgrade and migrate](guides/upgrade-and-migrate.md) (with a [worked migration](guides/example-existing-project-migration.md)), [join an existing team](guides/join-an-existing-team.md), [work each day](guides/work-each-day.md), [find and maintain knowledge](guides/find-and-maintain-knowledge.md), and [diagnose and recover](guides/diagnose-and-recover.md). They replace the legacy walk-throughs for new work; `SETUP.md` and the demo below are kept as they are. |
| [`github-planning-surface.md`](github-planning-surface.md) | The shared GitHub Project, its five-state Status field and four views, the issue and PR templates, labels, per-operator credentials and repository mapping. |
| [`SETUP.md`](SETUP.md) | Anatomy of an initialized workspace + the setup runbook (greenfield and existing-repo), and identity isolation. |
| [`SETUP.md` → **Multi-repo control plane**](SETUP.md#multi-repo-control-plane--hosting-your-code-repos) | The **add-a-repo mechanics**: the `target_repo` → manifest → directory mapping, why siblings rather than submodules, and the runbook. The *why* and the operating rules are in `control-plane.md` above. |
| [**`command-deck-watcher/`**](command-deck-watcher/) | **Run a programme unattended: reach for `/foundry:command-deck` first** (the plugin's `skills/command-deck/SKILL.md`) — it ships the watcher this directory once asked you to hand-build (`status \| stop \| restart \| tick \| prompt \| list`, capability preflight, the blocker schema, wave-state merging). This directory is now the historical design rationale the shipped verb was built from — the measured-learnings table (what the instrument said vs. what was actually true) is still genuinely useful reading. |
| [`architecture/`](architecture/) | Your project's architecture docs and ADRs. Ships mostly empty — it is yours to fill. |
| [`../CLAUDE.md`](../CLAUDE.md) | Workspace governance: the floor that never relaxes, stage mode, conventions. |
| [`../WORKFLOW.md`](../WORKFLOW.md) | Where things live — the opt-in spec lane and the artifact map. |
| [`../templates/ci.yml`](../templates/ci.yml) | The CI template a code repo copies: runs on ready-for-review PRs only, cancels superseded runs, deploys on promote (tag or label), never on merge. |

## About the demo (Acme Links)

**Acme Links is the worked example**, not part of your project. It is a small link shortener
built through the factory so the loop can be shown end to end rather than asserted.

| Document | What it is |
|---|---|
| [`example-acme-links/README.md`](example-acme-links/README.md) | The 7-step tutorial — do it yourself, each step a checkout-able checkpoint. |
| [`example-acme-links/BUILD-JOURNEY.md`](example-acme-links/BUILD-JOURNEY.md) | The build log — every command and prompt that actually produced the app, including the three security Blocks caught before merge and the defects that reading missed. |
| [`../specs/features/acme-links/`](../specs/features/acme-links/) | The example's specs, frozen contracts, design system, and every prompt verbatim. |

The demo's own code lives in a separate repository,
[`lukasrepublic/acme-links`](https://github.com/lukasrepublic/acme-links) — the multi-repo split
(workspace holds the *WHAT*, code repo holds the *HOW-built*) is itself part of what the example
demonstrates.

## The minimal example

If the full demo is more than you need, [`specs/features/example/api/ping/`](../specs/features/example/api/ping/)
is a single atom — one spec, one contract — showing the file shapes with nothing else attached.
