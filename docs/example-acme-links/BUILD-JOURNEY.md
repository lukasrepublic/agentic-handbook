# Acme Links (worked example) — the full build journey

> **Scope.** This is the build log of the **Acme Links demo app** — the worked example this
> template ships to teach the loop. It is *not* the development history of the Agentic Foundry
> framework or of this workspace template. The app it produced lives at
> [`lukasrepublic/acme-links`](https://github.com/lukasrepublic/acme-links).


This is the **build log**, not a brochure. Every command, prompt, and artifact below is the one
that produced [`lukasrepublic/acme-links`](https://github.com/lukasrepublic/acme-links) — a
working link shortener with accounts — starting from an empty workspace and ending at a merged,
gate-proven, provenance-pinned app.

Read the [7-step tutorial](README.md) if you want to *do* it. Read this if you want to
see **exactly what happened**, including the parts that went wrong: three security Blocks caught
before merge, one contract that had to be re-frozen, and one test of mine that passed in CI while
being broken for users.

> **A note on honesty.** Where the recorded journey differs from the idealized one, this document
> says so. Sections marked **⟦as-built⟧** describe what was actually run in the session that
> produced the merged code; sections marked **⟦from the corpus⟧** describe work done in earlier
> sessions whose prompts were recorded at the time in
> [`PROMPTS.md`](../../specs/features/acme-links/PROMPTS.md). Nothing here is reconstructed from
> memory — it is all recoverable from git history, PR comments, and the frozen contracts.

---

## The shape of the whole thing

```
  HUMAN                        FACTORY                          MACHINE-CHECKED
  ─────                        ───────                          ───────────────

  ① workspace setup ─────────► /foundry:doctor ───────────────► DOCTOR-GREEN
        │                                                             │
  ② config: repos map ───────► target_repo: app ──────────────► paths ground
        │                                                             │
  ③ PRD.md  (the human WHAT)                                          │
        │                                                             │
        ▼                                                             │
  ④ /foundry:intake ─────────► 4 atomic specs + contracts             │
        │                       auth · create-link ·                  │
        │                       resolve-redirect · dashboard          │
        ▼                                                             │
  ⑤ /foundry:spec-review ────► 3 fresh-context lenses ────────► specs hardened
        │                       one remediation round                 │
        ▼                                                             │
  ⑥ design (Claude Design) ──► two-surface audit ─────────────► tokens + components
        │                                                             │
        ▼                                                             │
  ⑦ /foundry:authorize ──────► spec_sha256 + contract_sha256 ──► FROZEN
        │                       (the operator signs)                  │
        ▼                                                             │
  ⑧ implement, atom by atom ─► branch → PR                            │
        │                                                             ▼
        │                       ┌──────────────────────────────────────────┐
        │                       │  THE MERGE FLOOR                         │
        ├──► security review ──►│  build + typecheck                       │
        │    (separate context) │  contract journeys vs the RUNNING app    │
        │                       │  → red blocks the merge. no exceptions.  │
        │                       └──────────────────────────────────────────┘
        ▼                                                             │
  ⑨ merge ◄───────────────────────────────────────────────── green ──┘
        │
        ▼
  ⑩ .foundry/build-provenance.yaml ──► every atom pinned to its frozen contract
```

The single idea the whole apparatus serves: **a green checkmark is not evidence the feature
works.** Compilation, type-checking, and a plausible diff all pass on a route that returns the
wrong thing. Only a check that drives the *running* app at the seam the contract names can tell
you otherwise — and step ⑧ below is that claim being demonstrated rather than asserted.

---

## ① Workspace setup ⟦as-built⟧

The workspace is the *WHAT* (specs, contracts, governance). The factory is the *HOW* (the Foundry
plugin). They are separate on purpose: you own your requirements, you install the machinery.

```bash
# 1. Create the workspace from the template
#    GitHub UI → "Use this template" → <project>-handbook
git clone https://github.com/<you>/<project>-handbook && cd <project>-handbook

# 2. Install the factory
claude plugin marketplace add lukasrepublic/agentic-foundry#v1.2.1
claude plugin install foundry@agentic-foundry

# 3. Register yourself as the operator
#    edit .claude/foundry-operators.json — replace op_example with your id + GitHub handle
```

```json
{
  "schema_version": 1,
  "operators": {
    "op_lukas": { "name": "Lukas Sliwka", "github": "lukasrepublic", "added_at": "2026-06-01" }
  }
}
```

That registry is **load-bearing, not paperwork**: every `authorized:` block names an
`operator_id`, and the freeze fail-closes if the id does not resolve here. It is committed so the
identity can be resolved at the pinned commit, by anyone, later.

```bash
/foundry:doctor        # → DOCTOR-GREEN
```

Five structural checks — manifest parses, hook scripts exist, skill frontmatter is valid, the
stack-profile lock resolves, the operator registry resolves. **Measured on a clean machine: about
three minutes from clone to `DOCTOR-GREEN`.**

`DOCTOR-GREEN` means the wiring is intact. It does **not** mean your merges are safe — that is the
CI floor's job, and doctor says so itself.

---

## ② Config — teaching the workspace where the code lives ⟦as-built⟧

Acme Links is a **separate repo** from the workspace that specifies it. That is the multi-repo
pattern most real projects need, and the one this build demonstrates:

```
agentic-handbook/          the WHAT — specs, contracts, this document
└── specs/features/acme-links/…

acme-links/                the HOW-built — the actual app
└── src/… .foundry/build-provenance.yaml
```

The link between them is one entry in `.claude/foundry-project.json`:

```json
"repos": {
  "app": {
    "path": "acme-links",
    "kind": "single-app",
    "package_manager": "npm",
    "boot_command": "make dev",
    "ci_install": "npm ci",
    "datastores": ["postgres"]
  }
}
```

`boot_command` records how this repo boots. Note honestly: no shipped code reads that field today
— `/foundry:certify-local` resolves its boot recipe from the active **stack profile's**
`app_exercise_binding.boot`. The field documents the repo; it does not yet drive it.

Each contract then names its venue:

```yaml
target_repo: app        # the acme-links code repo (repos.app in the workspace manifest)
```

**This line was missing for a month and nobody noticed.** When the contracts were finally
re-frozen (§⑩), the authorization gate refused them:

```
FAIL (fail-closed): scope.allowed_paths entry 'src/lib/auth/**': matches ZERO paths
under the venue root and is not named by any of the atom's own checkpoint surfaces
```

Without `target_repo`, the scope grounded against the *workspace* — where `src/lib/auth/` does not
exist — so every path in every contract matched nothing. A scope that matches nothing constrains
nothing. The gate caught it; a human reading the same YAML had not.

---

## ③ Human requirements — the PRD ⟦from the corpus⟧

The journey starts with a human writing what they want in prose. Not user stories in a tracker,
not a ticket — a document with intent, trade-offs, and an explicit statement of what is *not*
being built.

📄 [`specs/features/acme-links/PRD.md`](../../specs/features/acme-links/PRD.md)

The load-bearing parts:

**The app**, in one line: *"A signed-in user creates short links (`acme.example/<slug>` → a long
URL) and sees per-link click counts on a dashboard; anyone visiting the short link is
redirected."*

**Why this app** — and this is the part that matters for a teaching artifact: *"It exercises every
surface the gate cares about with the smallest honest footprint: authentication, a database, and a
UI. The core value lives in one tight seam — the redirect resolve — which is trivial to stub and
visceral when the gate catches the stub."*

**Explicitly out of scope**: custom slugs, expiry, edit/delete, analytics beyond a counter,
password reset, OAuth, teams. *"The app must feel real, not be feature-complete."*

**Resolved decisions, with reasons** (O1–O7) — Next.js + TypeScript for reach; Postgres via
Drizzle for one language end-to-end; Better Auth because Lucia is deprecated and Auth.js is
OAuth-centric; four vertical slices rather than horizontal layers.

**A security note the PRD insists on teaching rather than hiding:** Better Auth ships no rate
limiting, and CVE-2025-29927 showed that middleware-only session checks in Next.js are bypassable.
Both facts became acceptance criteria (AC-AUTH-9 and AC-AUTH-7) instead of footnotes.

---

## ④ LLM requirements — intake turns prose into atoms ⟦from the corpus⟧

A PRD is not buildable. It has no stable identifiers, no measurable criteria, and no way to tell
whether it has been satisfied. `/foundry:intake` refines it into **atomic specs**: one capability
each, stable AC-IDs, a delimited normative region, and a sibling acceptance contract.

**The prompt, verbatim:**

```
/foundry:intake specs/features/acme-links/PRD.md
```

Discovery is interactive — it asks about the decisions it cannot infer, and the answers given were:

```
- slug scheme: random base62, 7 chars, retry-on-collision
- URL validation: http/https only (reject javascript:/data:/file: after normalization)
```

**Out came four atoms**, split as vertical slices (each one shippable end-to-end) rather than
horizontal layers (which cannot be demonstrated individually):

| Atom | Owns | AC count |
|---|---|---|
| `auth` | signup/login/logout, `GET /api/me` | 9 |
| `create-link` | `POST /api/links` | 7 |
| `resolve-redirect` | `GET /r/:slug` — **the seam** | 6 |
| `dashboard` | `GET /dashboard` | 7 |

Each atom is a pair of files:

```
specs/features/acme-links/resolve-redirect/
├── feat-handbook-acme-links-resolve-redirect.md   the WHAT (normative ACs)
└── acceptance-contract.yaml                        the CHECK (executable checkpoints)
```

The spec states the requirement in prose that a human can argue with:

```markdown
<!-- normative -->
- **AC-RESOLVE-1**: `GET /r/<slug>` for an existing slug responds HTTP **302** with a
  `Location` header **exactly equal** to that link's stored target URL.
- **AC-RESOLVE-3**: Each successful `GET /r/<slug>` increments that link's stored click count
  by exactly 1, atomically — concurrent resolves do not lose updates.
<!-- /normative -->
```

The `<!-- normative -->` fence is what gets hashed. Edit the changelog, fix a typo in the intro,
reword the design notes — the hash does not move. Change what the app must *do*, and it does.
That is the difference between a document under version control and a **requirement under
governance**.

The contract states the same thing as something a machine can run:

```yaml
scope:
  allowed_paths:  ["src/app/r/**", "src/lib/links/**", "src/db/**"]
  denied_paths:   ["src/app/(auth)/**", "src/app/api/links/**", "src/design-system/**"]
checkpoints:
  - ac_id: AC-RESOLVE-1
    surface: "api:/r/:slug"
    locator: "GET /r/<seeded canary slug> → HTTP 302 with Location EXACTLY equal to
              the seeded target https://example.com/acme-canary-9f3"
    expect: { op: matches, value: 'https://example\.com/acme-canary-9f3', baseline: pre-change }
```

Two things to notice, because they are the whole design:

- **`baseline: pre-change`** means this checkpoint must be **red before the fix and green after**.
  A test that passes on an empty implementation proves nothing; this one is required to prove it
  can fail.
- **`scope`** is a blast radius. The resolve atom may touch the redirect route and the database
  layer; it is *denied* the auth routes and the design system. An implementer that wanders is
  caught by the diff, not by a reviewer's attention span.

---

## ⑤ Audit — three fresh-context lenses ⟦from the corpus⟧

Specs are reviewed before they are frozen, because the cheapest place to fix a requirement is
before any code depends on it.

```
/foundry:spec-review specs/features/acme-links/
```

The review runs deterministic pre-lints first (size ceiling, reference closure — zero token cost,
so they run before anything expensive), then dispatches **three separate agents with fresh
context**, one question each:

```
   ┌─ prior art ─────────► "is this the approach the industry actually builds,
   │                        or a bespoke re-invention of a solved problem?"
   ├─ steel-man +        ─► "assume the design is right: where is it under-specified?
   │  adversarial           assume an adversary: where does it fail open?"
   └─ per-AC rubric ─────► completeness / clarity / measurability, scored once (advisory)
```

Separate contexts matter: an agent that just wrote a spec is the worst possible reviewer of it.

**What the review changed** — recorded in each spec's changelog, and substantial:

| Before | After | Why |
|---|---|---|
| `AC-RESOLVE-1`: "responds 302" | "302 **with `Location` exactly equal** to the stored target" | A redirect to the *wrong* place also returns 302. The original passed on an open-redirect bug. |
| `AC-DASH-2`: `count_gte: 1` | "B's slugs visible in A's dashboard **== 0**" | "At least one link appears" passes on an implementation that leaks *every* user's links. |
| — | `AC-AUTH-5`: 401 **uniform** across unknown-user vs wrong-password | Otherwise the error message is an account-enumeration oracle. |
| — | `AC-CREATE-3`: reject non-http(s) **after normalization** | ` Javascript:` and `java\tscript:` bypass a naive prefix check. |
| — | `AC-RESOLVE-3`: atomic increment, "not read-modify-write" | Concurrent resolves silently lose clicks. |

That table is the argument for the review step. Every "after" is a checkpoint that a real
implementation can fail; several of the "before"s were **vacuous** — assertions that no plausible
bug could have violated.

---

## ⑥ Design — before any UI exists ⟦from the corpus⟧

The dashboard is a real screen, so it gets designed before it is built, and the design is an
artifact under the same governance as everything else.

📁 [`specs/features/acme-links/design/`](../../specs/features/acme-links/design/) — the brief, the
token spec, per-component specs, and a rendered canary page.

The design system is **tokens first** (CSS custom properties projected through Tailwind v4's
`@theme`) and **owned components** second (shadcn-style: copied in, not imported from a
dependency). Framework-agnostic core, so it outlives the app that first consumes it.

The design goes through a **two-surface audit** — the design-side peer of `/foundry:spec-review`:

```
  SURFACE A (in Claude Design)          SURFACE B (native, here)
  ──────────────────────────────        ────────────────────────────
  visual hierarchy & polish             token conformance
  brand & voice                         WCAG contrast ratios
  rendered responsive @390 / @1280      ARIA + semantics
  consistency vs the canary             target sizes
        │                                       │
        └──────────► both converge, ────────────┘
                     zero open Blockers → APPROVED
```

The full Surface-A prompt is recorded verbatim in
[`PROMPTS.md`](../../specs/features/acme-links/PROMPTS.md#step-3--design-claude-design). What that
audit produced is visible in the shipped token file — for example:

```css
--color-danger-badge-text: var(--color-danger-hover);
/* #b91c1c — AA-safe danger text on danger-soft; raw #dc2626 is only 4.41:1 there */
```

A contrast ratio measured, found wanting by 0.09, and fixed with the reason recorded next to the
value. That is what "the design is real, not decoration" means in practice.

---

## ⑦ Authorize — the freeze ⟦as-built⟧

Nothing is built until the operator signs. This is the **front-authorization floor**, and it has
no skip.

```bash
/foundry:authorize specs/features/acme-links/auth/…
```

The verb runs **dry first** and prints exactly what is being signed — the scope, and every
checkpoint in full:

```
operator=op_lukas  mode=regular
  spec_ref: specs/features/acme-links/auth/feat-handbook-acme-links-auth.md
  target_repo: 'app'  (PRODUCT-REPO dispatch — code lands here, gate-bound to this repo)
  scope.allowed_paths: ['src/app/(auth)/**', 'src/app/api/me/**', 'src/lib/auth/**', 'src/db/**']
  scope.denied_paths : ['src/app/r/**', 'src/app/api/links/**', 'src/design-system/**']
  checkpoints (the live-seam PASS criteria you are signing):
    - [AC-AUTH-1] api:/api/me @ POST /signup {unique email,password} then GET /api/me
                  with returned session → 200 with that user's identity
    …
DRY RUN — no write. After operator confirmation, re-run with --yes.
```

On confirmation it writes a signed trailer into the contract:

```yaml
# === FOUNDRY-AUTHORIZED-TRAILER (excluded from contract_sha256) ===
authorized:
  operator_id: op_lukas
  authorized_at: 2026-07-31T…Z
  auth_seq: 2
  supersedes: 928be1f07a3989228c6ac18ce9c077b7bec662b137920a040b68e743b15fff44
  spec_sha256: 904bfea09118a247284c5263a3118697eb2150836e954b4e74b14b7f564ee9c2
  contract_sha256: 66a919fb037714f0869712d1f70b73b1592299d54d83e75ea2ae58bc40f94f0d
  merge_autonomy_mode: regular
```

**Why the hashes are the point.** `spec_sha256` covers the normative region only; `contract_sha256`
covers the contract above the sentinel (so the trailer can be appended without invalidating
itself). Together they answer a question that is otherwise unanswerable after the fact: *was this
code built against the requirements that were actually approved, or against ones edited
afterwards?*

**And approval is a merge, not a mood.** The frozen contract is a tracked file. It reaches `main`
through a pull request, which means GitHub's own machinery — CODEOWNERS, required reviews,
"an author cannot approve their own PR" — gates it. Foundry deliberately does **not** reimplement
any of that.

---

## ⑧ Buildout ⟦as-built⟧

### 8.1 The money shot — the floor blocks a broken seam

The `resolve-redirect` atom was built by hand, deliberately, so the block could be *witnessed*.

**Pass one: an honestly incomplete implementation.**

```ts
// src/app/r/[slug]/route.ts  (first pass)
export async function GET() {
  return new Response("ok");
}
```

The route exists. `next build` compiles. TypeScript is clean. The PR diff reads plausibly. Every
conventional "is it ready?" signal is green.

**The contract journey drives the running app instead of the source:**

```bash
curl -s -o /dev/null -w '%{http_code} %{redirect_url}\n' http://localhost:3000/r/canary7
#   → 200                          (the contract requires 302 → …canary-9f3)
```

CI, on commit [`22cd12a`](https://github.com/lukasrepublic/acme-links/commit/22cd12a):

```
✘ AC-RESOLVE-1: GET /r/canary7 → 302 with Location EXACTLY the stored target
    Expected: 302
    Received: 200
6 failed
```

**The merge is refused.** Not by a reviewer noticing — by a machine that drove the seam the
contract named and got the wrong answer.

**Pass two: the real implementation.**

```ts
const rows = await db.select({ id: link.id, targetUrl: link.targetUrl })
  .from(link).where(eq(link.slug, slug)).limit(1);
if (!found) return notFound();
const target = safeTarget(found.targetUrl);        // AC-RESOLVE-2 read-side scheme guard
if (target === null) return notFound();
await db.update(link)                              // AC-RESOLVE-3 atomic, not read-modify-write
  .set({ clicks: sql`${link.clicks} + 1` }).where(eq(link.id, found.id));
return new Response(null, { status: 302,
  headers: { Location: target, "Cache-Control": "no-store" } });   // AC-RESOLVE-1, -6
```

Same check, same floor, commit [`ae456f2`](https://github.com/lukasrepublic/acme-links/commit/ae456f2):

```
✓ AC-RESOLVE-1  ✓ AC-RESOLVE-2  ✓ AC-RESOLVE-3  ✓ AC-RESOLVE-4  ✓ AC-RESOLVE-5  ✓ AC-RESOLVE-6
6 passed → merged as 2d4f131
```

Both runs are in the repository's Actions history. `git show step-5` puts them in your hands.

### 8.2 The remaining three atoms

`auth` → `create-link` → `dashboard`, in dependency order, one branch and one PR each. Each was
implemented against its frozen contract, journeys written per AC-ID, and pushed to the same floor.

```
PR #2  auth          9 ACs → 9 journeys + 2 security regressions
PR #3  create-link   7 ACs → 6 journeys + 2 security regressions
PR #4  dashboard     7 ACs → 7 journeys + 2 security regressions
```

---

## ⑨ Security review — where the real defects were caught ⟦as-built⟧

Every atom touching auth, credentials, or a public surface gets a **separate-context adversarial
review of the diff** before merge. Not the agent that wrote the code, reviewing its own work.

The review is dispatched with an explicit threat model and named lenses — the prompt shape used
for the `auth` atom:

```
Security-review the auth atom of the acme-links app. This is PR #2's diff — the complete set
of NEW files: [files listed]

The authorized contract (AC-AUTH-1..9) requires: [contract restated]

Review lenses: credential handling, session fixation/rotation, cookie flags, CSRF exposure of
the custom POST endpoints (JSON + form-encoded accepted — assess SameSite=Lax coverage and any
state-changing GET), enumeration side channels, rate-limit bypass (x-forwarded-for
spoofability), open-redirect on the GET redirects, secrets hygiene, dependency risk.

This is a PUBLIC exhibit/tutorial repo for a demo app, threat model: internet-reachable demo;
teaching honesty matters — a finding that the tutorial should DISCLOSE is as valuable as one
to fix.

Emit categorized findings: Block (must fix before merge) / Risk / Nit. For each: file:line,
the concrete attack or failure, and the minimal fix.
```

**It found three Blocks. All three would have shipped in a public exhibit.**

### Block 1 — login CSRF (PR #2)

The handlers call Better Auth's server API directly. Its CSRF protection is **router-level**, not
endpoint-level — so calling the API directly skips it. Combined with accepting form-encoded
bodies (the un-preflighted "simple request" shape), `evil.com` could auto-submit a POST to
`/login` carrying the **attacker's** credentials.

No victim cookie is needed, so `SameSite=Lax` does not block it — and Lax *does* then send the
planted session on the victim's next top-level navigation. The victim ends up silently signed
into the attacker's account, and every link they shorten lands in the attacker's dashboard.

```ts
export function isCrossSiteRequest(req: Request): boolean {
  const fetchSite = req.headers.get("sec-fetch-site");
  if (fetchSite && fetchSite !== "same-origin" && fetchSite !== "none") return true;
  const origin = req.headers.get("origin");
  if (origin && origin !== appOrigin()) return true;
  return false;
}
```

### Block 2 — a rate limiter one header defeated (PR #2)

The limiter keyed on `x-forwarded-for` with no trusted proxy in front. A client sets that header
to anything it likes, so rotating it bought an unbounded number of password guesses.

**The contract's own AC-AUTH-9 journey passed** — because Playwright does not send the header.
The control read as protection and was not. The key is now the identity alone; `x-forwarded-for`
is consulted only when the deployment declares `TRUST_PROXY=1`.

### Block 3 — validated one string, stored another (PR #3)

```ts
const url = new URL(cleaned);                       // parsed — and then thrown away
if (url.protocol !== "http:" && …) return null;
return cleaned;                                     // the RAW input is what gets stored
```

The URL was validated in its *parsed* form and stored in its *raw* form — and the stored string is
what the resolver later emits as a `Location` header. `U+010A`/`U+010D` (CR/LF with a high byte
attached) survive the control-character strip, parse fine, and would have been percent-encoded by
the canonical form. Node's header validator catches it today, so the visible outcome is a hard 500
on every resolve of that link — one framework detail away from response splitting.

The fix is one line, and it closes the whole class: `return url.href`, then re-check the length
bound (percent-encoding can grow the string past the limit that was measured on the input).

### Findings that were disclosed instead of fixed

An exhibit that hides its limits teaches the wrong lesson. These are in the repo's README:

- **A `409` on duplicate signup is an enumeration oracle.** Kept, because the contract specifies
  it and it makes the tutorial legible. The production answer is generic-200 plus a confirmation
  email; that is stated rather than silently implied.
- **The app is an open redirector by construction.** Accounted honestly: this is *not* SSRF — the
  server never dereferences the target, so a link-local address reaches the *clicker's* browser,
  not the app's credentials. A write-time host blocklist is bypassed by any attacker-controlled
  name that resolves to a private address, so it would be mitigation posing as prevention.

### A finding that was filed, not fixed

The dashboard review found that `link.user_id` has no index — Postgres does not auto-index foreign
keys, so every dashboard render is a full table scan. **The fix needs `src/db/schema.ts`, which
that atom's frozen contract does not allow.** So it was filed as a follow-up and the PR merged
without it.

That is the floor working. The alternative — quietly widening the scope because the fix is small
and obviously correct — is exactly how "authorized scope" becomes decoration.

---

## ⑩ The merge floor, and what it actually runs ⟦as-built⟧

```yaml
# .github/workflows/ci.yml
services:
  postgres: { image: postgres:16, … }
steps:
  - run: npm ci
  - run: npm run typecheck
  - run: npm run db:push          # a real schema
  - run: npm run build            # a real production build
  - run: npm run journeys         # the contract journeys vs the RUNNING app
```

The journeys are named by AC-ID, so a red check names the requirement it violated:

```
✓ AC-AUTH-1: signup creates one user and establishes a session, witnessed by /api/me
✓ AC-AUTH-7: /api/me without a session → 401, spoofed middleware-bypass header included
✓ AC-CREATE-5 + AC-CREATE-6: 100 created slugs are pairwise-distinct 7-char base62
✓ AC-DASH-2: ownership isolation — zero of B's slugs appear in A's dashboard
✓ AC-RESOLVE-3: 100 concurrent resolves increment the click count by exactly 100 (atomic)
36 passed
```

**One more defect, and it was mine.** After merging, a full suite run against the *same* database
failed: a seeded slug was a fixed literal, so the journey passed once and then violated a unique
constraint forever after. CI never saw it — CI gets a fresh database every run.

Green in CI while broken for anyone running it twice is the precise failure this entire project
argues against, so it was fixed in [PR #5](https://github.com/lukasrepublic/acme-links/pull/5) and
proven with two consecutive full suites against one database.

---

## ⑪ Provenance — closing the loop ⟦as-built⟧

The last step pins the merged code back to the exact contracts it was authorized against:

📄 [`acme-links/.foundry/build-provenance.yaml`](https://github.com/lukasrepublic/acme-links/blob/main/.foundry/build-provenance.yaml)

```yaml
workspace: lukasrepublic/agentic-handbook
foundry_authorized_against: agentic-handbook@96bf3b256250eb8b9ff9bb9ed6f9470a1d521cfd

authorizations:
  - atom: resolve-redirect
    spec_sha256: 1549ec319ca886f5238d574e0ca30bf932499ef87710d7af547e2d0ece6bc419
    contract_sha256: 5d9788dd9644599cd08ef85347da72391c805c79eba699b03f2d5eb6c247a5ba
    auth_seq: 2
    merged_pr: 1
```

### The pin was written by recomputing, not by copying — and that caught something

Rather than transcribe the hashes out of the contract trailers, they were **recomputed** with the
factory's own hashing functions and compared. The result:

| Corpus | `spec_sha256` | `contract_sha256` |
|---|---|---|
| the authorizing workspace copy | 4/4 verified | **4/4 verified** |
| the published handbook copy | 4/4 verified | **0/4 verified** |

**Cause:** when the specs were mirrored into the public handbook, one line changed — `spec_ref:`
was rewritten to match the new repo's paths. That line lives inside the hashed contract-proper
region, so the published copies no longer hashed to the trailers they carried. No acceptance
criterion, checkpoint, or scope had drifted — the diff was exactly one path string per file.

**Why it mattered anyway:** this document invites you to verify those hashes. On the public copy,
that check *failed*. A claim the reader cannot verify is the one defect this exhibit exists to
refute, so the mirrors were re-frozen (`auth_seq` 2/2/2/3) and the missing `target_repo` from §②
fixed at the same time.

**Verify it yourself** — the point of the file is that this works:

```bash
git clone https://github.com/lukasrepublic/agentic-handbook && cd agentic-handbook
git checkout 96bf3b256250eb8b9ff9bb9ed6f9470a1d521cfd
python3 - <<'EOF'
import sys; sys.path.insert(0, "<plugin>/scripts")
import foundry_contract as fc
print(fc.spec_sha256("specs/features/acme-links/auth/feat-handbook-acme-links-auth.md"))
print(fc.contract_sha256("specs/features/acme-links/auth/acceptance-contract.yaml"))
EOF
# must print the values recorded in build-provenance.yaml
```

---

## What the journey actually cost, and what it caught

| | |
|---|---|
| Atoms specified, authorized, built, merged | 4 |
| Acceptance criteria | 29 |
| Contract journeys, named by AC-ID | 36 |
| Pull requests, each through the floor | 6 |
| **Security Blocks caught before merge** | **3** |
| Review findings, as reported per PR | #2: 2 Blocks · 9 Risks · 5 Nits — #3: 1 Block · 4 Risks · 3 Nits — #4: 0 Blocks · 3 Risks · 3 Nits |
| Risks disclosed in the README rather than fixed | 4 |
| Findings filed because the fix was out of authorized scope | 2 |
| Defects the *gate* caught that review had not | 2 (the 200-stub; the rerun-breaking journey) |
| Defects *recomputation* caught that reading had not | 2 (the mirror freeze; the missing `target_repo`) |

The pattern worth taking away: **every defect in that last block was invisible to reading and
visible to running.** The stub compiled and type-checked. The rate limiter looked correct and had
a passing test. The contracts looked authorized and carried real-looking hashes. Each one was
caught by something that *executed* — a journey against a live app, a hash recomputed from bytes,
a scope grounded against a real filesystem.

That is the entire thesis, and it is why the checks are where they are.

---

## Replay it yourself

```bash
# read the destination first
git clone https://github.com/lukasrepublic/acme-links && cd acme-links
git log --oneline --graph          # one merged PR per atom, each behind the floor
git show step-5                    # the stub blocked, then the fix admitted
cat .foundry/build-provenance.yaml # every atom pinned to its frozen contract

# then walk it
make install && make db-up && make db-push
make build && make journeys        # 36/36
```

Then do it on your own project: [the 7-step tutorial](README.md) ·
[every prompt, verbatim](../../specs/features/acme-links/PROMPTS.md) ·
[workspace setup](../SETUP.md)
