# Releases

`release.yaml` is the authoritative release manifest, and **this directory is where the factory
resolves it**: `.foundry/releases/<id>/release.yaml`, where `<id>` is an `[a-z0-9-]+` slug. A
manifest anywhere else is never found — the loader resolves the id strictly within this
directory and refuses any path that escapes it.

Companions alongside each `release.yaml`: `specs.txt`, `dependency-graph.md`, `release-notes.md`.

Generated lifecycle views live separately, under `specs/lifecycle/<state>/manifest.yaml` — those
are derived, never hand-edited.

**Atoms are authorized per-atom.** "Authorize the release once" is not a thing: each atom carries
its own frozen `acceptance-contract.yaml`, and `/foundry:authorize-release` records the operator
go-ahead for shipping a *wave* — it is not a substitute for the per-atom freeze.
