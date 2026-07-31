# PRD — Acme Links: the Agentic Foundry flagship sample app + how-to series

> **Status:** DRAFT (human-readable intent). This is the *WHAT* — the top of the WHAT
> ladder. It is the input to `/foundry:intake`, which (with `/foundry:spec-author` +
> `/foundry:spec-review`) refines it into atomic `feat-*.md` specs + a frozen
> `acceptance-contract.yaml`. Co-authored with the operator; not yet authorized.
> **"Acme Links"** is a deliberately-fictional demo brand (the industry-standard "Acme"
> convention) — it signals "this is the example," not a real product.
>
> **Where this is built (the dogfood model).** Authored and dogfooded here in
> `agentic-workspace` — the private control-plane that is itself shaped as a clone of the
> `agentic-handbook` template (so we live the adopter's experience). The *publishable*
> result then flows **downstream** to the public products: `agentic-handbook` (the template)
> and `lukasrepublic/acme-links` (the example code repo). §6's repo layout describes that
> downstream end-state; during the build, the WHAT lives at
> `agentic-workspace/specs/features/acme-links/`.

---

## 1. Why this exists

Per `STRATEGY-path-to-number-1.md §3.1`, the single highest-leverage asset on the path to
\#1 is **not a claim — it's a teachable, reproducible build**. Acme Links is that build: a
small but *genuine* application (real auth, real DB, a **designed** UI) a newcomer follows
from an empty repository to a governed, live-proven merge. The tutorial's **money shot is
the gate blocking a deliberately broken seam**, making `status ≠ functional` visceral in a
way no prose can.

Three things ship from this PRD:
1. **The app — Acme Links.** A link-shortener with accounts. Built in a separate, pinned code
   repo (`lukasrepublic/acme-links`), exactly the multi-repo pattern an adopter uses.
2. **A reusable design system — built with Claude Design.** Tokens + components authored as
   a *WHAT* artifact alongside the Acme Links specs, synced to a `claude.ai/design` project,
   and **first consumed by Acme Links's own signed-in dashboard.** Reusable in any future
   work; the dashboard is just the first consumer.
3. **The how-to series.** A linear, copy-along, 7-step tutorial; each step is its own
   `git checkout`-able committed checkpoint **and carries the verbatim prompts used.** Lives
   in `agentic-handbook/docs/`. It teaches the full arc — *spec → design → authorize →
   operator-driven build → kick off automated buildout → provenance* — including how to work
   with Claude Design and how to drive both the interactive and the autonomous postures.

---

## 2. The app — Acme Links

**One-liner.** A signed-in user creates short links (`acme.example/<slug>` → a long URL) and
sees per-link click counts on a dashboard; anyone visiting the short link is redirected.

**Why this app.** It exercises *every surface the gate cares about* with the smallest
honest footprint: authentication (only my links are mine), a database (slugs + clicks
persist), and a UI (the dashboard). The core value lives in **one tight seam** — the
redirect resolve — which is trivial to stub and visceral when the gate catches the stub.

### 2.1 User stories

- **U1 — Sign up / sign in.** As a visitor I can create an account and log in, so my links
  are private to me.
- **U2 — Create a short link.** As a signed-in user I paste a long URL and get back a short
  slug I can share.
- **U3 — Follow a short link.** As anyone (no account), visiting `/r/<slug>` redirects me to
  the original URL.
- **U4 — See my links + clicks.** As a signed-in user my dashboard lists my links with a
  click count per link.
- **U5 — Only my links.** As a signed-in user I never see or manage another user's links.

### 2.2 Surfaces

| Surface | Auth | Behavior |
|---|---|---|
| `POST /api/links` | required | Body `{url}` → creates a slug for the current user, returns `{slug, shortUrl}`. Rejects invalid URLs (400) and anonymous callers (401). |
| `GET /r/:slug` | none | **The seam.** Looks up the slug in the DB; on hit, increments the click count and **302-redirects** to the original URL; on miss, 404. |
| `GET /dashboard` | required | Renders the current user's links + click counts. **First consumer of the design system.** |
| `POST /signup`, `POST /login`, `POST /logout` | n/a | Session-based auth (Better Auth, email+password). |
| `GET /api/me` | required | Returns the current user. The auth atom's handler-enforced probe surface — witnesses session establishment + CVE-2025-29927 enforcement without borrowing another atom's route. |

### 2.3 Data model (minimal)

- **User** — `id`, `email` (unique), `passwordHash`, `createdAt`. (Managed by Better Auth's
  schema; extended only as needed.)
- **Link** — `id`, `userId` (FK), `slug` (unique), `targetUrl`, `clicks` (int, default 0),
  `createdAt`.

Schema + migrations are defined in **Drizzle** (TypeScript schema, `drizzle-kit` migrations).

### 2.4 Explicitly out of scope (keep the tutorial tight)

Custom slugs, link expiry, edit/delete, analytics beyond a click counter, password reset,
OAuth, teams. The app must feel real, not be feature-complete. *(Per the **full
production-grade** audit remediation, the specs **do** include production hardening that the
gate enforces: rate-limiting on auth (AC-AUTH-9), URL length bounds (AC-CREATE-4), stored-XSS
output-encoding (AC-DASH-5), open-redirect guards on both the write and read sides
(AC-CREATE-3 / AC-RESOLVE-2), and atomic click counting (AC-RESOLVE-3).)*

---

## 3. The design system (built with Claude Design)

**What it is.** A small but real, **reusable** design system — design tokens (color, type,
spacing, radius, elevation) + a handful of components (button, input, card, table,
nav/shell, empty-state) — authored and iterated **in Claude Design** (`claude.ai/design`)
and kept in sync with a local component library via the `DesignSync` tool + `/design-sync`
skill (incrementally, one component at a time — never a wholesale replace).

**Styling approach (O5).** Tokens live as **CSS custom properties** exposed through
**Tailwind v4's `@theme`** directive — CSS is the single source of truth, and the tokens
stay framework-agnostic/reusable regardless of the consuming layer. Components follow the
**shadcn/ui model** (owned, copy-in components on Radix primitives) — accessible, fully
owned in-repo, and a conceptual match to `/design-sync`'s "own your components, one at a
time" philosophy.

**Project (O6).** A fresh, dedicated `claude.ai/design` project — **"Acme Links — Design
System"** (created via `DesignSync create_project`). Fresh-not-reused because the flagship
*builds* the design system and the tutorial must show the reader's own `create_project` path.

**Two facets, two homes (this is deliberate).**
- **The WHAT** — the design brief, the tokens spec, the per-component specs, and the pointer
  to the `claude.ai/design` project — lives in the handbook **with the Acme Links specs**
  (`specs/features/acme-links/design/`). It flows through the same ladder as any other spec:
  intake → spec-author → audit → authorize.
- **The compiled code** — the token CSS (`@theme`) + the shadcn-style React components the app
  imports — is produced during buildout in the app repo
  (`acme-links/src/design-system/`), synced from the Claude Design project.

**First consumer.** Acme Links's signed-in **`/dashboard`** is the first surface built on the
design system — proving the system works against a real screen, not a swatch sheet. Because
the system is a standalone artifact (tokens + components, not app-specific markup), it is
reusable by any future app; the dashboard is simply consumer #1.

---

## 4. The how-to series (the 7-step tutorial)

A linear, copy-along tutorial. Each step ends at a committed checkpoint in the
`acme-links` repo (tagged `step-1` … `step-7`) that a reader can `git checkout`, **and each
step records the verbatim prompts used** (see §4.1). Each step maps to the real foundry verbs
an adopter runs.

| Step | Title | Foundry / tool verb(s) | The checkpoint proves |
|---|---|---|---|
| **1** | Install + scaffold from template | clone `agentic-handbook` template → `claude plugin install foundry` → `/foundry:doctor` | The factory is wired; `DOCTOR-GREEN`. `/ping` proves the wiring. Scaffold = Next.js + Drizzle schema + design tokens (the "sprint-0" foundation, not an atom). |
| **2** | Author specs + the spec review | `/foundry:intake` (+ the spec-author persona) → `/foundry:spec-review` | Fuzzy intent becomes 4 atomic vertical-slice specs — `auth`, `create-link`, **`resolve-redirect`**, `dashboard` — hardened by the three-lens review. |
| **3** | Design the UI with Claude Design | `DesignSync` (`create_project` + sync) + `/design-sync`; design specs authored like any WHAT | A reusable design system (Tailwind v4 `@theme` tokens + shadcn-style components) lives in the "Acme Links — Design System" project and as authored specs; the dashboard's look is designed *before* it's built. Includes the **two-surface design-audit gate** (`DESIGN-AUDIT-PROMPT.md`) — **Surface A** in Claude Design (visual/subjective: hierarchy, polish, brand, rendered responsive) + **Surface B** native here (objective conformance: token/WCAG/ARIA/semantics/targets, committed diffs, optional `chrome-devtools` screenshots). Both Blocker/Risk/Confirmed, looped to convergence/plateau; APPROVED only when both converge with zero open Blockers. The design-side peer of `/foundry:spec-review`. |
| **4** | Authorize specs + design | `/foundry:authorize` (or `/foundry:authorize-release` for the batch) | The operator signs every contract; `spec_sha256` + `contract_sha256` freeze. An un-authorized spec/design never reaches `main`. |
| **5** | 🔴 Operator-driven command-center → the floor BLOCKS → fix → merge | `/foundry:mode-interactive`; the contract journeys as floor checks | **The money shot.** The operator drives the `resolve-redirect` atom by hand. The first pass ships `GET /r/:slug` as a `200 'ok'` stub → the contract journey expects `302` → **RED → merge REFUSED**. The operator wires the real DB lookup + `302` → **GREEN** → merge. `status ≠ functional`, proven and fixed in one accountable context. |
| **6** | Kick off the fully automated buildout | `/foundry:mode-autonomous` | With specs + design authorized, the operator launches the autonomous driver; the remaining atoms (`auth`, `create-link`, **`dashboard` consuming the design system**) build → walk → merge with no per-atom turn. |
| **7** | Provenance + citation graph | the build-provenance convention, `/foundry:report-citation-graph` | Each merged atom carries `.foundry/build-provenance.yaml` pinning the workspace commit; the citation graph answers "what cites this contract / this design token?". |

### 4.1 Every prompt, captured (a hard requirement)

Every step ends with a **"Prompts used"** block containing the *verbatim* prompts the
operator issued (foundry verbs, Claude Design briefs, fix instructions), copy-paste-able.
Rationale: the guide's promise is **reproducibility** — a reader must be able to replay the
exact inputs, and an adopter learns most from seeing the real prompts that produced each
artifact. This satisfies the "no claims, only checks" bar (§7, S5). The canonical source for
these blocks is the **prompt library** at `PROMPTS.md` (every prompt, per step, verbatim).

### 4.2 The deliberately-broken seam (step 5 — the money shot)

- **The contract is correct.** The authorized `acceptance-contract.yaml` checkpoint for the
  redirect seam expects: `GET /r/:slug` → **HTTP 302** with `Location` = the original URL.
- **The first implementation is honestly incomplete.** The `GET /r/:slug` handler returns a
  hardcoded `new Response('ok')` (HTTP 200) — the route exists, the app compiles, the PR is
  "ready", `status` says merge-ready. The trap every team falls into: *a green checkmark that
  doesn't mean the feature works.*
- **The contract journey catches it.** It drives the *real running app* at the seam the
  contract names, sees `200 'ok'` where it required `302 → <url>`, and goes **RED**. The
  merge is **blocked** by a machine-derived PASS that was never earned — not by a human
  noticing.
- **The fix is the payoff.** The operator replaces the stub with a real DB lookup +
  `clicks++` + `302`. The walk re-runs GREEN, and the *same* gate that blocked now authorizes
  the merge. RED→GREEN, visible and reproducible.

> Placing this in the **operator-driven** step (5) is deliberate: the human *witnesses* the
> block and the fix. Step 6 then shows the autonomous driver handling the rest — so the
> reader sees both postures and understands the gate guards both equally.

---

## 5. Tech stack (decisions O3–O5)

- **Next.js (App Router) + TypeScript** front-to-back — broadest reach, one language, one
  runtime, simplest clean-room repro.
- **Postgres** via **Drizzle** — TS-native schema + `drizzle-kit` migrations (no codegen step;
  keeps the whole stack in one language).
- **Better Auth** — type-safe, self-hosted **email+password sessions** (no OAuth, no external
  service), Drizzle adapter. Type-safety reinforces the "typed contracts at boundaries" floor.
- **Design system** — Tailwind v4 `@theme` tokens (CSS custom properties) + shadcn/ui-style
  owned components (Radix), authored in Claude Design and synced via `DesignSync`.
- **`make dev`** is the boot recipe (what certification and the journeys run against).

> **Security note (for the step-5 / security-review surface).** Two current realities to
> *teach, not hide*: (1) Better Auth ships **no rate limiting** on auth routes — the
> security review flags brute-force exposure; (2) **CVE-2025-29927** showed Next.js
> middleware-only session checks are bypassable — enforce auth in the route handler, not just
> middleware. Auth touches the security-review floor, so these belong in the guide.

---

## 6. Repo layout & the multi-repo pin

```
agentic-workspace/              (PRIVATE — operator's orchestration plane; dogfoods all of this)
└── agentic-handbook/           (the WHAT — public template an adopter clones)
    ├── specs/features/acme-links/
    │   ├── …/feat-*.md                       ← atomic app specs (from intake, step 2)
    │   ├── …/acceptance-contract.yaml        ← frozen at authorize (step 4)
    │   └── design/                           ← the design system WHAT: brief, tokens spec,
    │                                            component specs, claude.ai/design project ref
    └── docs/sample-app/                       ← this PRD + the 7-step how-to series (+ prompts)

claude.ai/design  →  "Acme Links — Design System"   (the live, synced design system project)

lukasrepublic/acme-links        (the CODE — separate repo; what a reader builds; PRIVATE → public at launch)
    ├── src/app/…  src/db/ (drizzle)  Makefile
    ├── src/design-system/                     ← compiled @theme tokens + shadcn-style components (synced)
    └── .foundry/build-provenance.yaml         ← pins the workspace commit (step 7)
```

The handbook stays **WHAT-only** (like the existing `/ping` example — spec + contract, no
app code): the design system's *brief/specs* live there with the Acme Links specs, while the
*compiled* tokens + components live in the app repo. App code is addressed cross-repo via the
build-provenance pin. This is deliberate: the docs *teach* the multi-repo + WHAT/HOW split,
so the flagship build must *demonstrate* it.

---

## 7. Success criteria (for the tutorial itself, not just the app)

- **S1 — Clean-room reproducible.** An external newcomer, starting from an empty machine,
  reproduces every step to a GREEN merge using only the published docs + the recorded
  prompts. (Gate on publish — and the gate on going public per O7.)
- **S2 — Every step is a real checkpoint.** Each `step-N` tag builds and is `git
  checkout`-able; the reader can resume at any step.
- **S3 — The gate actually blocks.** The step-5 broken-seam checkpoint produces a genuine RED
  merge floor (not a simulated/screenshotted one) — runnable by the reader.
- **S4 — The fix actually merges.** The fix produces a genuine GREEN gate + a real merge to
  `main`, with a real `build-provenance.yaml`.
- **S5 — No claims, only checks.** Nothing in the docs asserts a capability the reader can't
  verify locally within the same step; **every prompt is recorded verbatim.**
- **S6 — Design is real, not decoration.** The dashboard renders from the design system that
  was authored in Claude Design; the system is shown to be reusable (tokens/components are
  app-agnostic), with the dashboard as the demonstrated first consumer.
- **S7 — Both build postures shown.** The guide demonstrates the operator-driven
  command-center (interactive) AND a hands-off automated buildout (autonomous), with the
  same gate guarding both.

---

## 8. Resolved decisions (O1–O7)

All seven open decisions are settled (research-rooted; see commit/discussion history):

- **O1 — App name → "Acme Links."** Industry-standard fictional demo brand ("Acme"
  convention); avoids the trademark/collision problem of "Sniplink" (4+ live products) and
  signals "this is the example."
- **O2 — Atomization → 4 vertical slices** (`auth`, `create-link`, `resolve-redirect`,
  `dashboard`) on a step-1 scaffold foundation. Vertical-slice + INVEST best practice;
  `resolve-redirect` carries the step-5 broken seam, `dashboard` is the design-system
  consumer built in the autonomous wave.
- **O3 — Auth → Better Auth.** Modern, type-safe, self-hosted email+password sessions; the
  2026 best practice (Lucia is deprecated; Auth.js is OAuth-centric/maintenance-mode).
- **O4 — ORM → Drizzle.** TS-native schema + migrations; tightens "one language end-to-end."
  (Prisma was the teaching-readability runner-up; operator chose Drizzle.)
- **O5 — Styling → Tailwind v4 `@theme` tokens + shadcn/ui-style owned components.** Token
  core stays framework-agnostic/reusable; copy-own components mirror `/design-sync`.
- **O6 — Design project → create fresh** "Acme Links — Design System" (reproducible; matches
  the reader's `create_project` path).
- **O7 — Repo → `lukasrepublic/acme-links`; private → public at launch**, gated on the
  operator + the design-partner proof-of-use + a formal release strategy (per CLAUDE.md + GTM §8).

### Still open (design-step outputs, not blocking)

- Concrete token values (palette, type scale, spacing ramp) — produced in the Claude Design
  step.
- Final component inventory beyond the core set — confirmed during `/design-sync`.
```
