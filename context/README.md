# Context — templates live in the foundry plugin

The spec-authoring templates (spec template, acceptance-contract template, citation grammar, glossary)
are **not** kept here. Their **canonical source of truth is the foundry plugin's own context kit**, shipped
with the plugin and updated via `claude plugin update` — the plugin is a self-contained ecosystem.

Find them at `${CLAUDE_PLUGIN_ROOT}/context/` (e.g. the version-pinned plugin cache
`…/plugins/cache/agentic-foundry/foundry/<version>/context/`):

- `feat-spec-template.md` — the atomic spec template (Requirement/Invariant + EARS + prior-art + normative region)
- `acceptance-contract-template.yaml` — the sibling acceptance contract
- `charter-template.md` — the one-page unit of work for the charter lane (Goal / Acceptance
  criteria / Done when / Escalate when / Scope / Amendments), the DEFAULT lane under
  `noninteractive`/`interactive` posture — no hash-freeze ceremony, committed as its own record
- `branch-discipline.md` — the canonical worktree/branch rules (one worktree per atom, atom PRs
  target the release branch, one PR per release to `main`), cited by reference from
  `/foundry:mode-autonomous`, `/foundry:command-deck`, and `/foundry:dispatch` rather than
  copied into each
- the citation grammar and the Foundry methodology glossary

The `spec-author` / `spec-reviewer` agents and the `extract-spec` / `intake` skills read the kit from the
plugin directly, so a workspace does not carry its own copy.
