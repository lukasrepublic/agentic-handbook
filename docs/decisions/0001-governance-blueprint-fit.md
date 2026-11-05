---
status: accepted
date: 2026-11-04
confirmation:
  check_id: FG-ARCH-005
---

# 0001: Governance blueprint for a documentation repository

**Status:** accepted · **Charter:** gv-19-dogfood

## Context

This repository is documentation, templates and a few shell and Python helper scripts. It has no manifest, lockfile,
container, infrastructure code or dependency list. `foundry_governance.py discover` found only a CI workflow, and
`select` ranked all eight shipped blueprints at score 0.00, below their thresholds. There is no `docs-site` blueprint.

## Decision

Selected `cli-tool` by explicit `--confirm` (recorded as an operator override of the detection threshold). It is the
least wrong shipped fit: no service, no UI, no data store, no cluster, and a small script surface.

## Honest note on fit

`cli-tool` is not a documentation blueprint. Its kits (architecture, conduct, contracts, delivery, exceptions, product,
quality, security, stack) are applied as the shipped set. Most rules there speak about code, releases and APIs, and mostly
do not bind a markdown repository. Declarations: ASVS level 1, data classification `public`, surface `workflows` only
(no `cli` surface is declared, because the helper scripts are internal tooling, not a product CLI).

Installed from the security kit: secret scan, SAST, scorecard and release attestation workflows. The semgrep and gitleaks
rule files are copied to `security-checks/` because the workflows reference them and `apply` does not install them.

A purpose-built docs-only blueprint would drop the non-binding rules and the release-attestation workflow. That is a
follow-up for the framework, not a change made here.

## Notes on the rendered rules

- Paths cited in `governance/rendered/*.md`, such as `governance/kits/**` and `scripts/foundry_governance.py`, resolve
  against the foundry plugin, not this repository.
- `cost.md` and `operations.md` are rendered even though the blueprint does not select those kits for this repository,
  because they carry floor rules (`FG-COST-001`, `FG-OPS-004`, `FG-OPS-005`), and floor rules are never filtered out.
- `.foundry/governance.lock` is tracked (re-included in `.gitignore`). `.foundry/governance-intake.json` is intake state
  and stays ignored.

## Confirmation

`FG-ARCH-005` (the ADR lint over `docs/decisions/**`).
