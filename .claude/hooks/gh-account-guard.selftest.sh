#!/usr/bin/env bash
# Selftest for gh-account-guard.sh — proves AC-GHID-1..5 (UL-0007). Hermetic: temp dirs only,
# no network, no real gh. Drives the REAL guard with synthesized PreToolUse JSON + checks exit codes.
HERE="$(cd "$(dirname "$0")" && pwd)"
GUARD="$HERE/gh-account-guard.sh"
ok=1
emit(){ if eval "$2"; then echo "  $1: PASS"; else echo "  $1: FAIL"; ok=0; fi; }
ghjson(){ printf '{"tool_input":{"command":"%s"}}' "$1"; }
# run_guard <cwd> <GH_CONFIG_DIR> <command> → prints the guard's exit code
run_guard(){ ( cd "$1" && printf '%s' "$(ghjson "$3")" | GH_CONFIG_DIR="$2" CLAUDE_PROJECT_DIR="$1" bash "$GUARD" >/dev/null 2>&1; echo $? ); }

echo "gh-account-guard self-test:"

# AC-GHID-1: the convention files ship together (guard + bootstrap + .envrc).
emit "AC-GHID-1 files-shipped" '[ -f "$HERE/gh-account-guard.sh" ] && [ -f "$HERE/gh-identity-bootstrap.sh" ] && [ -f "$HERE/../../.envrc" ]'

tmp="$(mktemp -d)"
mkdir -p "$tmp/umb/.claude";        echo "acctA" > "$tmp/umb/.claude/gh-identity"
mkdir -p "$tmp/umb/nested/.claude"; echo "acctB" > "$tmp/umb/nested/.claude/gh-identity"
mkdir -p "$tmp/bare"   # no .claude/gh-identity → opt-in dormant

# AC-GHID-2: gh under wrong GH_CONFIG_DIR → BLOCK (exit 2); correct → allow (0); non-gh → allow (0).
emit "AC-GHID-2 fail-loud-on-mismatch" '
  [ "$(run_guard "$tmp/umb" "$HOME/.config/gh-wrong" "gh pr create")" = 2 ] &&
  [ "$(run_guard "$tmp/umb" "$HOME/.config/gh-acctA" "gh pr create")" = 0 ] &&
  [ "$(run_guard "$tmp/umb" "" "echo hello && git push")" = 0 ]'

# AC-GHID-3: per-project isolation — distinct accounts each pass under their own ~/.config/gh-<acct>.
emit "AC-GHID-3 per-project-isolation" '
  [ "$(run_guard "$tmp/umb" "$HOME/.config/gh-acctA" "gh api user")" = 0 ] &&
  [ "$(run_guard "$tmp/umb/nested" "$HOME/.config/gh-acctB" "gh api user")" = 0 ]'

# AC-GHID-4: cwd-aware nested — from the nested cwd the NESTED account (B) is enforced, the
# umbrella account (A) is BLOCKED; from the umbrella cwd, A is enforced.
emit "AC-GHID-4 cwd-aware-nested" '
  [ "$(run_guard "$tmp/umb/nested" "$HOME/.config/gh-acctB" "gh pr create")" = 0 ] &&
  [ "$(run_guard "$tmp/umb/nested" "$HOME/.config/gh-acctA" "gh pr create")" = 2 ] &&
  [ "$(run_guard "$tmp/umb" "$HOME/.config/gh-acctA" "gh pr create")" = 0 ]'

# AC-GHID-5: opt-in default — no declared identity → guard dormant, gh allowed (single-account
# adopters unaffected).
emit "AC-GHID-5 opt-in-dormant-when-undeclared" '[ "$(run_guard "$tmp/bare" "$HOME/.config/gh-anything" "gh pr create")" = 0 ]'

rm -rf "$tmp"
if [ "$ok" = 1 ]; then echo "GH-IDENTITY-SELFTEST-GREEN"; else echo "GH-IDENTITY-SELFTEST-RED"; exit 1; fi
