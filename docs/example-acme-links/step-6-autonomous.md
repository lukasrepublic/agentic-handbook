# Step 6 — Kick off the autonomous buildout

**Goal.** With the specs authorized and the design signed off, drive the remaining three atoms —
`auth`, `create-link`, `dashboard` — to merge **hands-off**. Each is implemented in its own
worktree and merged on green floor checks, with no per-atom operator turn.

## You run

```bash
/foundry:mode-autonomous   # one wave per atom: implement → PR → green floor checks → merge
#   the three atoms are a dependency chain (auth → create-link → dashboard), so they build in order.
```

Each atom's journeys drive its contract's surfaces against the running app — e.g. the auth flow:

```bash
curl -s -c jar -X POST localhost:3000/signup -d '{"email":"a@x.io","password":"hunter2pass"}'  # → 200 + session
curl -s -b jar -o /dev/null -w '%{http_code}' localhost:3000/api/me                            # → 200
# …invalid login → 401, duplicate signup → 409, logout → /api/me 401, password stored hashed.
```

## What to expect

- All three atoms merge on green journeys: auth (signup/login/logout + `/api/me`), create-link
  (CSPRNG slug, http(s)-only validation), dashboard (ownership isolation — user A sees *none* of B's
  links — XSS output-encoding, empty-state, design-system UI).
- **The gate earns its keep again.** During the dashboard build the journey reveals the contract
  over-specified the auth-gate redirect as `302`, but Next's `redirect()` returns `307`. That's a
  real spec-vs-reality gap — so you correct the spec and **re-authorize**:

  ```bash
  /foundry:authorize --reauth-after-impl   # auth_seq=2, supersedes the prior; journeys GREEN → merge
  ```

## Checkpoint

```bash
git checkout step-6   # auth + create-link + dashboard merged; the full app builds
# then: /foundry:certify-local acme-v1 — deploy once, all four atoms' journeys against ONE instance
```

**Next:** [Step 7 — provenance + the citation graph](step-7-provenance.md).
