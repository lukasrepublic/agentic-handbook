# Acme Links — resolve & redirect  (feat-handbook-acme-links-resolve-redirect)

> **Human-readable intent.** Anyone (no account) visiting a short link `/r/<slug>` is sent to
> the original URL. This is the app's core value and its tightest seam: a real DB lookup that
> 302-redirects to the **exact** stored target. Deliberately the atom that carries the
> tutorial's broken-seam money shot — a `200 'ok'` stub that the contract journey catches —
> strengthened so the checkpoint also catches a redirect to the *wrong* target.

<!-- normative -->
## Acceptance criteria

- **AC-RESOLVE-1**: `GET /r/<slug>` for an existing slug responds HTTP **302** with a
  `Location` header **exactly equal** to that link's stored target URL.
- **AC-RESOLVE-2**: The resolver applies a read-side scheme guard (defense-in-depth, not
  trusting the write-side alone): if a stored target is not an absolute `http(s)` URL, it
  responds HTTP 404 rather than emitting a dangerous-scheme `Location`.
- **AC-RESOLVE-3**: Each successful `GET /r/<slug>` increments that link's stored click count
  by exactly 1, atomically — concurrent resolves do not lose updates (DB-level atomic
  increment, not read-modify-write).
- **AC-RESOLVE-4**: `GET /r/<slug>` for a slug that does not exist responds HTTP 404.
- **AC-RESOLVE-5**: The `slug` path parameter is constrained to the base62 charset; a
  malformed, oversized, or path-traversal-shaped slug responds HTTP 404 with no server error
  (no 500 / DB-error leak).
- **AC-RESOLVE-6**: The surface is unauthenticated and performs no write other than the click
  increment; the 302 response carries `Cache-Control: no-store` (no poisoned-redirect
  caching).
<!-- /normative -->

## Design / notes

- No authentication required (public surface). The slug→target lookup + atomic `clicks++`
  reads/writes the `link` table (Drizzle) — hence `src/db/**` is in scope (the GREEN fix needs it).
- **Broken-seam (tutorial step 5).** The first implementation pass ships `GET /r/:slug`
  returning a hardcoded `200 'ok'` stub; `AC-RESOLVE-1`'s checkpoint (302 + exact `Location`)
  is the one the floor blocks on, then the fix (real lookup + 302) turns it GREEN.
- Read-side scheme guard (AC-RESOLVE-2) pairs with the create-link atom's write-side scheme guard.
- [Doc: specs/features/acme-links/PRD.md §4.2].

## Changelog

- v1.0 Draft.
- v1.0 Draft — reviewed via `/foundry:spec-review` (three lenses, one remediation round).
  Remediated **full production-grade**: the money-shot checkpoint now asserts the **exact
  `Location` target** via a seeded canary (AC-RESOLVE-1), so an open-redirect / wrong-target
  stub also fails; added a read-side scheme guard (AC-RESOLVE-2), atomic click increment
  (AC-RESOLVE-3), slug-charset/traversal handling (AC-RESOLVE-5), and cache-header /
  side-effect constraints (AC-RESOLVE-6); **added `src/db/**` to `allowed_paths`** so the real
  lookup+write fix is in-scope.
