# Acme Links — my dashboard  (feat-handbook-acme-links-dashboard)

> **Human-readable intent.** A signed-in user sees their own links with per-link click
> counts, rendered with the Acme Links design system. The design system's first consumer.
> Ownership isolation (U5) is the app's reason to exist, so it is verified by an attributable
> cross-tenant check that goes RED on a leaking implementation.

<!-- normative -->
## Acceptance criteria

- **AC-DASH-1**: An authenticated `GET /dashboard` returns HTTP 200 and lists exactly the
  current user's links, each with its current click count.
- **AC-DASH-2**: Ownership isolation — given two users A and B each owning distinct links, A's
  `GET /dashboard` contains A's links and **none** of B's links. A non-filtering (IDOR)
  implementation that returns all links must fail this criterion.
- **AC-DASH-3**: An unauthenticated `GET /dashboard` returns a **307** redirect to `/login`
  (the Next.js App Router `redirect()` status), enforced in the route handler; a
  CVE-2025-29927 middleware-bypass-shaped request without a valid session is still not served
  the dashboard.
- **AC-DASH-4**: A user with no links receives HTTP 200 with the defined empty-state (not an
  error or blank page).
- **AC-DASH-5**: User-controlled `targetUrl` and `slug` are output-encoded when rendered — a
  link whose target contains an HTML/JS payload renders inert (escaped), never executed
  (stored-XSS guard).
- **AC-DASH-6**: The dashboard is composed from the design-system tokens and components, not
  ad-hoc markup.
- **AC-DASH-7**: The link listing has a defined order (newest first) and is bounded
  (paginated / page-size limited) so a user with many links receives a bounded response.
<!-- /normative -->

## Design / notes

- First consumer of the design system (Tailwind v4 `@theme` tokens + shadcn-style components).
- Auth guard is handler-enforced; the atom is denied `src/lib/auth/**` and `src/middleware.ts`
  so it cannot repoint the auth gate (the enforcement stays in the auth atom's surface).
- Live-seam precondition: a two-user fixture (A and B, each with seeded links) is required to
  drive AC-DASH-2.
- [Design-asset: specs/features/acme-links/design/] — authored in the design step (step 3).
- [Doc: specs/features/acme-links/PRD.md §3].

## Changelog

- v1.0 Draft.
- v1.0 Draft — reviewed via `/foundry:spec-review` (three lenses, one remediation round).
  Remediated **full production-grade**: ownership isolation (AC-DASH-2) is now an **attributable
  cross-tenant check** (B's links visible to A must be 0; a no-`WHERE` leak goes RED) instead
  of a vacuous `count_gte:1`; added stored-XSS output-encoding (AC-DASH-5), handler-enforced
  auth guard incl. CVE-2025-29927 (AC-DASH-3), empty-state (AC-DASH-4), and ordering/pagination
  bound (AC-DASH-7); denied `src/lib/auth/**` + `src/middleware.ts` so the atom can't repoint
  the auth gate; stated the two-user fixture precondition.
