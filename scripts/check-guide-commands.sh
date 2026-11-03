#!/usr/bin/env bash
# check-guide-commands.sh — every command a guide names exists in the foundry tree it was
# written against. Bash + coreutils + grep only.
#
# Usage: scripts/check-guide-commands.sh <foundry-tree> [<guides-dir>]
#
# Checks every backticked `/foundry:<verb>` and every `scripts/foundry*` path in the guides
# directory (default: docs/guides/ in this repository), including the lines of fenced code blocks.
#   - a verb resolves when <foundry-tree>/skills/<verb>/ or <foundry-tree>/commands/<verb>.md exists;
#   - a path resolves when it is a file under <foundry-tree>;
#   - a token that does not resolve is accepted only when its line carries the label
#     `pending: lands with gn-NN` (the program atom that delivers it).
# Prints `resolved` or `pending` per token; exits 1 if any token is unresolved and unlabelled.
set -euo pipefail

if [ $# -lt 1 ] || [ $# -gt 2 ]; then
  echo "usage: $0 <foundry-tree> [<guides-dir>]" >&2
  exit 2
fi

tree="$1"
[ -d "$tree" ] || { echo "check-guide-commands: not a directory: $tree" >&2; exit 2; }

if [ $# -eq 2 ]; then
  guides="$2"
else
  guides="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/docs/guides"
fi
[ -d "$guides" ] || { echo "check-guide-commands: no guides directory: $guides" >&2; exit 2; }

resolved=0
pending=0
unresolved=0

# classify <file> <lineno> <token> <kind> <line>
classify() {
  local file="$1" lineno="$2" token="$3" kind="$4" line="$5" ok=0
  if [ "$kind" = verb ]; then
    local v="${token#/foundry:}"
    if [ -d "$tree/skills/$v" ] || [ -f "$tree/commands/$v.md" ]; then ok=1; fi
  else
    if [ -f "$tree/$token" ]; then ok=1; fi
  fi
  if [ "$ok" = 1 ]; then
    echo "resolved  $token  ($file:$lineno)"
    resolved=$((resolved + 1))
  elif printf '%s' "$line" | grep -Eq 'pending: lands with gn-[0-9]+'; then
    echo "pending   $token  ($file:$lineno)"
    pending=$((pending + 1))
  else
    echo "UNRESOLVED $token  ($file:$lineno) — absent from $tree and not labelled 'pending: lands with gn-NN'"
    unresolved=$((unresolved + 1))
  fi
}

while IFS= read -r file; do
  rel="${file#"$guides"/}"
  lineno=0
  infence=0
  while IFS= read -r line || [ -n "$line" ]; do
    lineno=$((lineno + 1))
    trimmed="${line#"${line%%[![:space:]]*}"}"
    case "$trimmed" in
      '```'*) infence=$((1 - infence)); continue ;;
    esac
    if [ "$infence" = 1 ]; then
      scan="$line"
    else
      # only the text inside backtick spans is scanned outside a fence
      scan="$(printf '%s' "$line" | grep -oE '`[^`]+`' || true)"
    fi
    [ -n "$scan" ] || continue
    while IFS= read -r tok; do
      [ -n "$tok" ] || continue
      classify "$rel" "$lineno" "$tok" verb "$line"
    done < <(printf '%s\n' "$scan" | grep -oE '/foundry:[a-z0-9][a-z0-9-]*' || true)
    while IFS= read -r tok; do
      [ -n "$tok" ] || continue
      tok="${tok%.}"
      classify "$rel" "$lineno" "$tok" path "$line"
    done < <(printf '%s\n' "$scan" | grep -oE 'scripts/foundry[A-Za-z0-9_./-]*' || true)
  done < "$file"
done < <(find "$guides" -type f -name '*.md' | sort)

echo "check-guide-commands: $resolved resolved, $pending pending, $unresolved unresolved"
[ "$unresolved" -eq 0 ]
