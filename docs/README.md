# Documentation index

Two kinds of document live here, and it is worth knowing which you are reading:

```
  ABOUT YOUR PROJECT                        ABOUT THE DEMO
  (use these to set up and run              (read these to learn the loop —
   your own workspace)                       none of it is your project)
  ────────────────────────────              ──────────────────────────────
  control-plane.md   ◀ start here           example-acme-links/
  SETUP.md                                    ├── README.md          the 7-step tutorial
  architecture/                               ├── BUILD-JOURNEY.md   how it was really built
                                              └── step-1 … step-7
```

## About your project

| Document | What it is |
|---|---|
| [**`control-plane.md`**](control-plane.md) | **The operating model — read this before running more than one repo.** This workspace is a *control plane* over your code repos: they live beside it as independent, gitignored sibling repos, and the factory dispatches into them. Covers the on-disk tree, the **session rule** (always start Claude Code at this root — and what silently breaks when you don't), building one atom across two repos, and day-two operations. |
| [`SETUP.md`](SETUP.md) | Anatomy of an initialized workspace + the setup runbook (greenfield and existing-repo), and identity isolation. |
| [`SETUP.md` → **Multi-repo control plane**](SETUP.md#multi-repo-control-plane--hosting-your-code-repos) | The **add-a-repo mechanics**: the `target_repo` → manifest → directory mapping, why siblings rather than submodules, and the runbook. The *why* and the operating rules are in `control-plane.md` above. |
| [`architecture/`](architecture/) | Your project's architecture docs and ADRs. Ships mostly empty — it is yours to fill. |
| [`../CLAUDE.md`](../CLAUDE.md) | Workspace governance: the floor that never relaxes, stage mode, conventions. |
| [`../WORKFLOW.md`](../WORKFLOW.md) | The SDLC orchestration — the phase pipeline and the artifact registry. |

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
