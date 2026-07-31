# Step 5 — The money shot: the floor blocks a broken seam, then admits the fix

**Goal.** Drive the `resolve-redirect` atom by hand. Ship the route as a `200 'ok'` **stub** — it
compiles, the PR looks merge-ready — and watch the contract's journey convict it against the
*running* app, turning the floor red so **the merge is refused**. Then fix it and watch the same
check admit the merge.

This is the whole thesis in one screen: **`status ≠ functional`, proven by machine.**

```
  the stub                                  the fix
  ────────                                  ───────
  compiles ✓  lints ✓  builds ✓             compiles ✓  lints ✓  builds ✓
  GET /r/canary7 → 200 "ok"                 GET /r/canary7 → 302 → the exact URL
        │                                         │
        ▼                                         ▼
  journey check: AC-RESOLVE-1 RED           journey check: AC-RESOLVE-1 GREEN
  the floor REFUSES the merge               the same floor ADMITS the merge
```

## You run

```bash
# Wire Foundry into the code repo; the atom's journey runs in CI as a floor check:
/foundry:init                # operator registry + project config
/foundry:mode-interactive    # you drive edit → verify → merge in one accountable context

# Bring up the app + an isolated dev DB, seed the canary the contract names:
make db-up                      # Postgres 16 on :5433, isolated from any system one
make db-push                    # create the schema

# link.user_id references user.id, so the owner row comes first:
psql "$DATABASE_URL" -c "INSERT INTO \"user\"(id,name,email) VALUES \
  ('seed-user','Seed','seed@acme.example') ON CONFLICT (id) DO NOTHING;"
psql "$DATABASE_URL" -c "INSERT INTO link(id,user_id,slug,target_url) VALUES \
  ('seed-link','seed-user','canary7','https://example.com/acme-canary-9f3');"
make dev &
```

The contract journeys seed this same canary themselves (`tests/journeys/resolve-redirect.spec.ts`),
so `make journeys` needs no manual setup — the psql above is for driving the seam by hand with
`curl`, which is what makes the block visceral the first time.

### 1 — ship the stub, run the journey → 🔴 RED

```ts
// src/app/r/[slug]/route.ts  (first pass — deliberately stubbed)
export async function GET() { return new Response("ok"); }
```

```bash
curl -s -o /dev/null -w '%{http_code} %{redirect_url}\n' http://localhost:3000/r/canary7
#   → 200    (the contract requires 302 + Location = …canary-9f3)
npx playwright test --grep AC-RESOLVE-1
#   AC-RESOLVE-1: RED  →  the journey check is red → the floor refuses the merge
```

Every conventional "is it ready?" signal is green — it compiles, serves, and the PR diff reads
plausibly. The journey is the only check that *drove the running app at the seam the contract
names*, and it is the one that's red.

### 2 — fix (real DB lookup + atomic clicks++ + 302), re-run → ✅ GREEN

```bash
curl -s -o /dev/null -w '%{http_code} %{redirect_url}\n' http://localhost:3000/r/canary7
#   → 302 https://example.com/acme-canary-9f3
npx playwright test --grep AC-RESOLVE-1
#   AC-RESOLVE-1: GREEN  →  the same check admits the merge
```

## What to expect

The stub **compiles and serves**, yet the merge is refused — because the journey named by the
frozen contract got `200` where it required `302 → <exact url>`. The fix turns it GREEN; you
merge. Later, `/foundry:certify-local` re-proves the same journeys against the whole deployed
release at once (step 6) — the release-level recheck of what the floor checked per-PR.

## Checkpoint

```bash
git checkout step-5   # resolve-redirect merged after RED → GREEN
```

**Next:** [Step 6 — the autonomous buildout](step-6-autonomous.md).
