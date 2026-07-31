# Acme Links — Prompt Library

> **Every prompt used to build Acme Links, per step, copy-paste-able.** This is the canonical
> source for the tutorial's per-step "Prompts used" blocks (PRD §4.1) and satisfies success
> criterion S5 ("no claims, only checks; every prompt recorded verbatim"). Some "prompts" are
> committed artifacts (a brief, an audit prompt) — those are referenced by path; the rest are
> captured verbatim here.

---

## Step 2 — Author specs + adversarial audit

**`/foundry:intake`** — input = the human PRD (`PRD.md`); interactive discovery resolved two
load-bearing decisions:
```
/foundry:intake specs/features/acme-links/PRD.md
# discovery answers:
#  - slug scheme: random base62, 7 chars, retry-on-collision
#  - URL validation: http/https only (reject javascript:/data:/file: after normalization)
# → produces 4 atomic feat-*.md + acceptance-contract.yaml (auth, create-link, resolve-redirect, dashboard)
```

**`/foundry:spec-review`** — the single-pass review (pre-lints + three fresh-context lenses), over the 4 atoms:
```
/foundry:spec-review specs/features/acme-links/   # auth · create-link · resolve-redirect · dashboard
# three lenses (prior-art / steel-man+adversarial / per-AC rubric) → one remediation round
# remediate: full production-grade (contracts witness real behavior, not just HTTP status)
```

---

## Step 3 — Design (Claude Design)

**The brief (paste into Claude Design as the first message):** the self-sufficient, citation-free
brief — `design/brief-claude-design.md` (the file *is* the prompt; paste it verbatim).

**Surface B — native conformance audit (run here):** `design/DESIGN-AUDIT-PROMPT.md` (the
two-surface gate), executed as the `acme-design-audit` workflow over `design/library/`.

**Surface A — Claude Design visual audit (paste into the project chat):** ⭐ the reusable prompt —
```
You are running SURFACE A of the Acme Links design audit — the visual / subjective adversarial loop. Work against the design system in this project: the canary `acme-links-design-system.html`, `theme.css`, and the component cards. Render it and judge it as a critical design reviewer and a brand owner would. Be adversarial: assume it's not good enough until proven otherwise.

LENSES (sweep all, every pass — these are the ones that need a rendered eye; the source-conformance lenses are handled by a separate native gate, don't duplicate them):
- A1 · Visual hierarchy & polish — emphasis, balance, rhythm, density, alignment, optical spacing; does each screen read in the right order; is it genuinely elegant or just "fine".
- A2 · Brand & voice — aesthetic restraint (exactly one filled primary action per view; semantic color only for state, never decoration); copy plain and direct ("Create a link", "No links yet"), no jargon, no marketing-plural.
- A3 · Rendered responsive — at ~390px and ~1280px the *rendered* layout holds: no overflow, awkward wrap, cramped tap targets, or broken composition.
- A4 · Visual consistency vs the canary baseline — every component and the dashboard composition look like they belong to one system.

LOOP:
- Run passes p1, p2, … Each pass is a fresh adversarial visual sweep across A1–A4.
- For every finding emit: severity · lens · location · the concrete fix. Severity = BLOCKER (ships visibly broken / off-brand-critical) or RISK (real quality concern, not ship-blocking). Track CONFIRMED = previously-raised findings you've now resolved.
- Apply the fixes to the design (update the canary + theme.css / components), then recount.
- Report the per-pass convergence trend, e.g. "p1: B3+R5=8 → p2: B1+R3=4 → …".

TERMINATE (judge by trend, never grind for a fake zero):
- Rule (a) Convergence: a pass with 0 Blockers AND 0 Risks → DONE.
- Rule (e) Plateau (this is a multi-component design system, so it has a legitimately non-zero fixed point): 0 Blockers AND residual Risks non-increasing across 3 consecutive passes AND every residual explicitly triaged (fixed, or accepted with a one-line rationale) → DONE.
- Hard cap 5 passes. NEVER finish with an open Blocker.

OUTPUT when done:
1. The converged design (updated canary + CSS + components, tokens intact — keep using the theme.css custom-property names).
2. The per-pass convergence trend line.
3. A residual ledger: each accepted Risk + its one-line rationale.
4. Verdict: CONVERGED (rule a) | PLATEAU (rule e). State it explicitly.
```

---

## Step 4 — Authorize

**`/foundry:authorize`** — front-authorization gate; per-atom operator confirmation, then freeze:
```
/foundry:authorize   # auth · create-link · resolve-redirect · dashboard
# operator=op_lukas, mode=regular → freezes spec_sha256 + contract_sha256 per atom (auth_seq=1)
```

---

## Step 1 — Install + scaffold

Clone the template, wire the factory, confirm green, then scaffold the app:
```
# from agentic-handbook (the workspace template) — install the factory
claude plugin marketplace add lukasrepublic/agentic-foundry
claude plugin install foundry@agentic-foundry
/foundry:doctor                      # → DOCTOR-GREEN

# scaffold the app repo (Next.js App Router + Drizzle + Better Auth + the design system)
cp .env.example .env                 # set DATABASE_URL + BETTER_AUTH_SECRET
make install                         # npm install
make db-push                         # create the schema in the dev DB
make dev                             # http://localhost:3000  (the app-exercise binding)
```
The 4 atoms' routes are NOT built here — they ship as gate-walked checkpoints (steps 5–6).

## Step 5 — Operator-driven build → the money shot

Wire the gate into the code repo, then drive the `resolve-redirect` atom by hand:
```
/foundry:init               # app-exercise binding (make dev; api->http, ui->chrome, test->runner)
/foundry:mode-interactive   # the operator drives edit → verify → merge in one context

# bring up the app + an isolated dev DB
make db-up                                        # Postgres 16 on :5433
make db-push                                      # create the schema
# seed the canary the contract names (the owner row first — link.user_id is a FK):
psql "$DATABASE_URL" -c "INSERT INTO \"user\"(id,name,email) VALUES \
  ('seed-user','Seed','seed@acme.example') ON CONFLICT (id) DO NOTHING;"
psql "$DATABASE_URL" -c "INSERT INTO link(id,user_id,slug,target_url) VALUES \
  ('seed-link','seed-user','canary7','https://example.com/acme-canary-9f3');"

# 1) ship the STUB (GET /r/:slug -> 200 'ok'), boot, run the contract journey:
make dev &
curl -s -o /dev/null -w '%{http_code} %{redirect_url}\n' http://localhost:3000/r/canary7
#   -> 200  (expected 302 + Location=…canary-9f3)  => AC-RESOLVE-1 RED => merge BLOCKED

# 2) FIX (real DB lookup + atomic clicks++ + 302), re-run the walk:
curl -s -o /dev/null -w '%{http_code} %{redirect_url}\n' http://localhost:3000/r/canary7
#   -> 302 https://example.com/acme-canary-9f3  => AC-RESOLVE-1 GREEN => gate ALLOWS => merge
```

## Step 6 — Autonomous buildout

Drive the remaining authorized atoms to merge, hands-off (dependency order, not parallel):
```
/foundry:mode-autonomous    # wave per atom: implement → PR → green floor checks → merge
# wave 1 auth → wave 2 create-link → wave 3 dashboard (each branch → walk → merge to main)

# the journeys = drive the running app at each contract surface, e.g. auth:
curl -s -c jar -X POST localhost:3000/signup -d '{"email":..,"password":..}'   # → 200 + session
curl -s -b jar -o /dev/null -w '%{http_code}' localhost:3000/api/me            # → 200
```
If the walk reveals the contract was over-specified (it caught dashboard's redirect = 307, not
302), correct the spec + contract and re-authorize:
```
/foundry:authorize --reauth-after-impl   # auth_seq=2, supersedes; re-walk → GREEN → merge
```

## Step 7 — Provenance + citation graph

Pin the merged code back to the authorized contracts, and materialize the citation graph:
```
cat acme-links/.foundry/build-provenance.yaml   # the PR authored this, per the convention:
#   each atom → foundry_authorized_against: agentic-workspace@<commit>, spec_sha256, contract_sha256
#   (dashboard carries auth_seq=2 — the reauth-after-impl 302→307 correction)

/foundry:report-citation-graph   # builds .foundry/graph.json (materialized backlinks) + serves it via MCP
# query "what cites the PRD?" → all 4 atom specs (the [Doc: …PRD.md] backlinks)
```
That closes the loop: the WHAT (frozen, authorized specs) ↔ the HOW-built (merged, walked code),
cross-repo-pinned and citation-indexed.
