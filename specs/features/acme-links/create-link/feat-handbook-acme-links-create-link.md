# Acme Links — create short link  (feat-handbook-acme-links-create-link)

> **Human-readable intent.** A signed-in user submits a long URL and receives a short slug
> they can share. The slug is unique, unguessable, and owned by that user. The write-side is
> the first line of defense for the public redirect surface, so URL validation is strict.

<!-- normative -->
## Acceptance criteria

- **AC-CREATE-1**: An authenticated `POST /api/links` with body `{url}` that is a valid
  absolute `http(s)` URL returns HTTP 201 with `{slug, shortUrl}`, persists a link owned by
  the current user, where `slug` matches `^[A-Za-z0-9]{7}$` and `shortUrl` =
  `<BASE_URL>/r/<slug>`.
- **AC-CREATE-2**: An unauthenticated `POST /api/links` returns HTTP 401 and creates no link.
- **AC-CREATE-3**: `POST /api/links` whose `url` is missing, unparseable, or — after
  normalization (scheme lower-cased, surrounding whitespace trimmed, control characters
  stripped) — is not an `http(s)` scheme (e.g. `javascript:`, `data:`, `file:`, `mailto:`,
  ` Javascript:`, `java\tscript:`) returns HTTP 400 and creates no link.
- **AC-CREATE-4**: `POST /api/links` whose `url` exceeds the maximum stored length (2048
  characters) returns HTTP 400 and creates no link (stored-redirect DoS guard).
- **AC-CREATE-5**: Each persisted `slug` is unique across all links; a generation collision is
  retried so the persisted slug never duplicates an existing one.
- **AC-CREATE-6**: Slugs are generated from a cryptographically-secure RNG (not a sequential
  or otherwise predictable source), so they are not enumerable.
- **AC-CREATE-7**: Creation is not deduplicated — submitting the same URL twice yields two
  links with distinct slugs (stated to remove ambiguity).
<!-- /normative -->

## Design / notes

- Slug: CSPRNG base62, length 7, retry-on-collision (unique constraint on `link.slug`).
- URL policy: normalize then accept only absolute `http(s)`; this is the write-side guard for
  the public resolve surface (defense-in-depth paired with the resolve atom's read-side scheme guard).
- [Doc: specs/features/acme-links/PRD.md §2.2].

## Changelog

- v1.0 Draft.
- v1.0 Draft — reviewed via `/foundry:spec-review` (three lenses, one remediation round).
  Remediated **full production-grade**: defined `shortUrl` format (AC-CREATE-1); added scheme
  normalization so case/whitespace/control-char bypasses are rejected (AC-CREATE-3); added a
  URL length bound (AC-CREATE-4); made the uniqueness checkpoint non-vacuous (AC-CREATE-5,
  witnessed across many slugs); added slug-unguessability (AC-CREATE-6) and an explicit
  no-dedup statement (AC-CREATE-7).
