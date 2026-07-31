#!/usr/bin/env bash
# Bootstrap an ISOLATED gh config dir for a GitHub account. Enables per-project identity
# isolation: each account gets its own ~/.config/gh-<account>, so handbook projects using
# different accounts never collide. (UL-0007)
#
# Usage:
#   .claude/hooks/gh-identity-bootstrap.sh [account]
# account defaults to the handle in .claude/gh-identity. Two paths:
#   (a) the account is already in the global gh keyring (gh auth login once, ever) → seed the
#       isolated dir from that token, NO browser;
#   (b) it is NOT in the keyring → open an isolated browser login directly into the dir, so the
#       account need never pollute the global keyring at all.
#
# CRITICAL (the keyring trap): both paths use `--insecure-storage` so the token is written
# INLINE into $dir/hosts.yml. WITHOUT it, gh stores the token back into the SHARED OS keyring
# (it ignores GH_CONFIG_DIR for *storage* when a keyring is available), so a later
# `GH_CONFIG_DIR=$dir gh api user` resolves THROUGH the keyring to the globally-active account —
# the isolation is illusory and you silently run gh as the wrong identity. The proof below uses
# `gh api user` (a real keyring-bypassing resolve), NOT `gh auth status`.
set -u
umask 077   # security-review hardening: ensure gh writes $dir/hosts.yml as 0600 (not just the 0700 dir)
acct="${1:-$(tr -d '[:space:]' < "$(dirname "$0")/../gh-identity" 2>/dev/null || true)}"
[ -n "${acct:-}" ] || { echo "usage: $0 <github-account>  (or create .claude/gh-identity)" >&2; exit 2; }

dir="$HOME/.config/gh-$acct"
mkdir -p "$dir"; chmod 700 "$dir"
tok="$(gh auth token --user "$acct" -h github.com 2>/dev/null || true)"
if [ -n "$tok" ]; then
  # (a) seed from the keyring token — inline, never back to the shared keyring.
  printf '%s' "$tok" | GH_CONFIG_DIR="$dir" gh auth login -h github.com --with-token --insecure-storage
else
  # (b) not in the keyring: isolated browser login straight into $dir (inline storage).
  echo "INFO: '$acct' is not in gh's keyring — opening an isolated browser login into $dir." >&2
  echo "      Authenticate in the browser AS $acct; gh will print 'saved in plain text' (= inline)." >&2
  GH_CONFIG_DIR="$dir" gh auth login -h github.com --git-protocol ssh --insecure-storage \
    || { echo "ERROR: isolated login for '$acct' failed." >&2; exit 1; }
fi
# PROOF the jail is real: resolve the identity THROUGH $dir (bypasses any keyring fallback).
who="$(GH_CONFIG_DIR="$dir" gh api user -q .login 2>/dev/null || true)"
if [ "$who" = "$acct" ]; then
  echo "OK: $dir resolves to $who"
else
  echo "WARN: $dir resolved to '${who:-<none>}', expected '$acct' — isolation NOT sound. If gh wrote to" >&2
  echo "      the shared keyring, re-run; ensure your gh supports --insecure-storage." >&2
  exit 1
fi
