# Documentation index

Two kinds of document live here, and it is worth knowing which you are reading:

```
  ABOUT YOUR PROJECT                        ABOUT THE DEMO
  (use these to set up and run              (read these to learn the loop —
   your own workspace)                       none of it is your project)
  ────────────────────────────              ──────────────────────────────
  SETUP.md                                  example-acme-links/
  architecture/                               ├── README.md          the 7-step tutorial
                                              ├── BUILD-JOURNEY.md   how it was really built
                                              └── step-1 … step-7
```

## About your project

| Document | What it is |
|---|---|
| [`SETUP.md`](SETUP.md) | Anatomy of an initialized workspace + the setup runbook (greenfield and existing-repo), and identity isolation. |
| [`SETUP.md` → **Multi-repo control plane**](SETUP.md#multi-repo-control-plane--hosting-your-code-repos) | **How the nested-repo structure works and how to add one.** The workspace hosts your code repos as gitignored siblings — each an independent git repo the factory dispatches into. Diagram of the on-disk layout, the `target_repo` → manifest → directory mapping, why siblings rather than submodules, and the add-a-repo runbook. |
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
