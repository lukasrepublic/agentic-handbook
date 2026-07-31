# Acme Links — accounts & sessions  (feat-handbook-acme-links-auth)

> **Human-readable intent.** A visitor can create an account and sign in so their links are
> private to them. Email + password, session-based (Better Auth), no OAuth, no external
> service. Protected surfaces require a valid session, enforced in the route handler — not
> middleware-only (CVE-2025-29927). This atom owns a minimal auth-required probe surface
> `GET /api/me` (returns the current user) so session establishment and handler-enforcement
> are witnessable without borrowing another atom's route.

<!-- normative -->
## Acceptance criteria

- **AC-AUTH-1**: `POST /signup` with a unique `{email, password}` returns HTTP 200, creates
  exactly one user, and establishes an authenticated session — witnessed by a follow-on
  `GET /api/me` using the returned session returning HTTP 200 with that user's identity.
- **AC-AUTH-2**: The persisted credential is a one-way password hash (argon2id / bcrypt /
  scrypt format) — never equal to the submitted plaintext.
- **AC-AUTH-3**: `POST /signup` with an already-registered email returns HTTP 409 and creates
  no additional user.
- **AC-AUTH-4**: `POST /login` with credentials matching an existing user returns HTTP 200
  and establishes an authenticated session (witnessed by a follow-on `GET /api/me` → 200).
- **AC-AUTH-5**: `POST /login` with invalid credentials returns HTTP 401, establishes no
  session, and returns a response uniform across "no such account" vs "wrong password" (no
  account-enumeration oracle).
- **AC-AUTH-6**: `POST /logout` returns HTTP 200 and invalidates the session server-side — a
  follow-on `GET /api/me` reusing the pre-logout session returns HTTP 401.
- **AC-AUTH-7**: An auth-required surface (`GET /api/me`) without a valid session returns HTTP
  401, enforced in the route handler; a request carrying the CVE-2025-29927 middleware-bypass
  shape (spoofed `x-middleware-subrequest` header) without a valid session still returns 401.
- **AC-AUTH-8**: The session cookie is `HttpOnly`, `Secure`, `SameSite=Lax` (or stricter),
  carries a bounded TTL, and is rotated on login.
- **AC-AUTH-9**: Repeated failed `POST /login` / `POST /signup` beyond a defined threshold per
  window are rate-limited with HTTP 429 (Better Auth ships no built-in rate limiting).
<!-- /normative -->

## Design / notes

- Better Auth (email+password, Drizzle adapter). User/session schema in `src/db`.
- Auth atom owns `src/app/api/me/**` (the probe) and `src/app/(auth)/**`; it is denied the
  `links`/`r` routes (cross-atom isolation).
- Schema-authority residual: `src/db/**` holds the single Drizzle schema shared by atoms;
  table ownership is by atom convention (auth → user/session; create-link → link).
- [Doc: specs/features/acme-links/PRD.md §5].

## Changelog

- v1.0 Draft.
- v1.0 Draft — reviewed via `/foundry:spec-review` (three lenses, one remediation round).
  Remediated **full production-grade**: positive checkpoints now witness session establishment
  via follow-on `GET /api/me`; added negative-branch ACs (AC-AUTH-3 409, AC-AUTH-5 401 + no
  enumeration oracle, AC-AUTH-6 logout-invalidation); added password-hash (AC-AUTH-2),
  CVE-2025-29927 handler-enforcement (AC-AUTH-7), cookie-hardening (AC-AUTH-8), and
  rate-limiting (AC-AUTH-9); introduced the auth-owned `/api/me` probe to remove the
  cross-atom `/api/links` surface borrow. Residual (bounded): single shared Drizzle schema dir
  — table ownership by convention, not by glob.
