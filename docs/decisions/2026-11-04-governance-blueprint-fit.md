# Decision: governance blueprint for a documentation repository

**Date:** 2026-11-04 · **Charter:** gv-19-dogfood

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
