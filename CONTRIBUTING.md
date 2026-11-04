# Contributing

This is a **workspace template**. Two kinds of contribution:

## Improving the template (this repo)
Make the scaffold more useful for everyone: better generic `CLAUDE.md`/`WORKFLOW.md`,
a sharper worked example (spec templates ship with the foundry plugin's kit, not here).
Keep it **generic** — no
project-specific or business content. Issues + PRs welcome.

## Using it for your project (after "Use this template")
- Replace the placeholder description in `CLAUDE.md` with your project.
- Install + wire the factory: `claude plugin install foundry@agentic-foundry`; register
  operators in `.claude/foundry-operators.json`; run `/foundry:doctor` → green.
- Follow `OPERATING-MODEL.md`: one ticket with a runnable `Done means` per change; branch →
  build → local-green → one draft PR → merge on green → deploy on promote → close with the output.
- The non-negotiable floor: branch protection + required CI checks, security review on
  auth / secrets / custody / supply-chain surfaces, no force-push, the operator's own walkthrough.

Code of Conduct: [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
