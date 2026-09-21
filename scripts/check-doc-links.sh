#!/usr/bin/env bash
# check-doc-links.sh — every relative link in tracked markdown resolves (handbook-docs-currency,
# AC-HDC-7). Bash + coreutils only, no interpreter dependency — mirrors the equivalent inline
# python step in .github/workflows/workspace-floor.yml ("Doc links resolve") so the same
# invariant is runnable locally, not just in CI.
#
# Usage: scripts/check-doc-links.sh
# Exit 0 and a one-line summary when every relative link resolves; exit 1 and the list of
# dead links (file -> target) otherwise.
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"

broken=()
file_count=0

while IFS= read -r doc; do
  [ -f "$doc" ] || continue
  file_count=$((file_count + 1))
  base_dir="$(dirname "$doc")"

  # Extract every markdown link target: [text](target) — grabs the inside of the parens.
  while IFS= read -r target; do
    [ -n "$target" ] || continue

    # Skip external / non-filesystem targets.
    case "$target" in
      http://*|https://*|mailto:*) continue ;;
    esac

    # Strip a trailing #fragment — fragments aren't filesystem paths.
    target="${target%%#*}"
    [ -n "$target" ] || continue

    resolved="$base_dir/$target"
    # Normalize (collapse ./ and ../) without requiring GNU realpath --relative-to.
    if [ ! -e "$resolved" ]; then
      broken+=("$doc -> $target")
    fi
  done < <(grep -oE '\]\([^)[:space:]]+\)' "$doc" 2>/dev/null | sed -E 's/^\]\((.*)\)$/\1/')
done < <(git ls-files '*.md')

if [ "${#broken[@]}" -gt 0 ]; then
  echo "broken links:"
  printf '%s\n' "${broken[@]}"
  exit 1
fi

echo "links OK across $file_count file(s)"
