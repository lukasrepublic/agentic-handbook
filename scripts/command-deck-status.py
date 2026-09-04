#!/usr/bin/env python3
"""command-deck-status — the Command Deck watcher's measurement instrument.

Pure measurement. NO MODEL IN THE LOOP: the same inputs always produce the same output, and the
tick prompt is forbidden from quoting a number this script did not print.

The one property that matters, and the reason it is a script rather than a paragraph of prompt:

    EVERY RESULT MUST DISTINGUISH "I LOOKED AND FOUND NOTHING" FROM "I COULD NOT LOOK".

So this script never prints a plausible zero. When it cannot measure it REFUSES — a loud line on
stdout naming exactly what was missing, and a non-zero exit. When it can measure but part of the
population is undecidable, it prints that part as UNMEASURED, in words, beside the count.

Usage
-----
    python3 scripts/command-deck-status.py <programme-id> [--json]
    python3 scripts/command-deck-status.py <programme-id> --self-test

    --state PATH   state file (default: command-deck/<programme-id>/state.yaml)
    --root PATH    workspace root (default: $CLAUDE_PROJECT_DIR, else the current directory)
    --json         machine-readable; the same measurement, no prose
    --self-test    drive the instrument against a case whose answer is already known: run it from
                   a directory that is not the workspace and prove it refuses loudly instead of
                   printing nothing and exiting 0. Run this BEFORE arming the watcher.

Exit codes
----------
    0   measured. Warnings, if any, are printed in words and are part of the measurement.
    2   REFUSED — could not measure. Never confuse this with "nothing to report".

Docs: docs/command-deck-watcher/README.md
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

STAGES = ("unbuilt", "dispatched", "pr-open", "merged", "applied", "parked", "blocked")
DONE_WITHOUT_LIVE_SURFACE = ("merged", "applied")
STALE_BLOCKER_HOURS = 24


def refuse(msg: str, *detail: str) -> "NoReturn":  # noqa: F821
    """Fail the way an instrument must: loudly, on stdout, naming what was missing."""
    print(f"REFUSED — cannot measure: {msg}")
    for line in detail:
        print(f"  {line}")
    print("  (exit 2. This is NOT an empty result; nothing was measured.)")
    sys.exit(2)


def now_utc() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def parse_ts(value, field: str):
    if value in (None, ""):
        return None
    try:
        return dt.datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        refuse(f"{field} is not an ISO-8601 timestamp", f"got: {value!r}")


def fmt_delta(delta: dt.timedelta) -> str:
    total = int(delta.total_seconds())
    d, rem = divmod(total, 86400)
    h, rem = divmod(rem, 3600)
    m = rem // 60
    return f"{d}d {h:02d}h {m:02d}m"


def git(root: Path, *args: str) -> tuple[int, str, str]:
    proc = subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, text=True
    )
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def load_yaml(path: Path, what: str):
    try:
        import yaml  # noqa: PLC0415
    except ImportError:
        refuse(
            "PyYAML is not installed, so the manifest cannot be PARSED",
            "membership and status are derived from parsed fields, never from a grep — a grep",
            "matches the comment documenting a removal as readily as the removal itself.",
            "fix: python3 -m pip install pyyaml",
        )
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        refuse(f"{what} could not be read", f"{path}: {exc}")
    try:
        return yaml.safe_load(text)
    except Exception as exc:  # noqa: BLE001 — any parse failure is a refusal
        refuse(f"{what} is not parseable YAML", f"{path}: {exc}")


# ── measurement ──────────────────────────────────────────────────────────────────────────────


def resolve_root(explicit: str | None) -> Path:
    root = Path(explicit or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()).resolve()
    marker = root / ".claude" / "foundry-project.json"
    if not marker.is_file():
        refuse(
            "this is not an Agentic Foundry workspace root",
            f"looked in: {root}",
            f"expected:  {marker}",
            "A command run from the wrong directory otherwise fails SILENTLY with exit 0 and no",
            "output. Start every tick call with an absolute `cd <workspace> &&`.",
        )
    return root


def measure_git(root: Path) -> dict:
    rc, head, err = git(root, "rev-parse", "HEAD")
    if rc != 0:
        refuse("git could not resolve HEAD", f"{root}: {err or 'no stderr'}")
    rc, porcelain, _ = git(root, "status", "--porcelain")
    dirty = bool(porcelain.strip()) if rc == 0 else None

    rc, behind, _ = git(root, "rev-list", "--count", "HEAD..@{upstream}")
    # No upstream, or a base never fetched: UNMEASURED. A stale tree fakes ABSENCE, so an
    # unmeasurable distance from the base must never render as 0.
    behind_count = int(behind) if rc == 0 and behind.isdigit() else None

    rc, upstream, _ = git(root, "rev-parse", "--abbrev-ref", "@{upstream}")
    return {
        "head": head,
        "dirty": dirty,
        "behind": behind_count,
        "upstream": upstream if rc == 0 else None,
    }


def load_manifest(root: Path, programme: str) -> tuple[Path, list]:
    manifest = root / ".foundry" / "releases" / programme / "release.yaml"
    if not manifest.is_file():
        releases_dir = root / ".foundry" / "releases"
        found = (
            sorted(p.name for p in releases_dir.iterdir() if p.is_dir())
            if releases_dir.is_dir()
            else []
        )
        refuse(
            f"no release manifest for programme {programme!r}",
            f"expected: {manifest}",
            f"releases present: {', '.join(found) if found else '(none — the directory is empty or absent)'}",
        )
    data = load_yaml(manifest, "the release manifest") or {}
    atoms = data.get("atoms")
    if not isinstance(atoms, list) or not atoms:
        refuse(
            "the manifest declares no atoms[]",
            f"{manifest}",
            "A denominator of 0 is indistinguishable from a programme with nothing in it, so it",
            "is refused rather than printed.",
        )
    ids = []
    for i, atom in enumerate(atoms):
        if not isinstance(atom, dict) or not atom.get("id"):
            refuse(f"manifest atom #{i} has no id", f"{manifest}")
        ids.append(str(atom["id"]))
    return manifest, ids


def load_state(path: Path) -> dict:
    if not path.is_file():
        refuse(
            "the programme state file does not exist",
            f"expected: {path}",
            "Create it from docs/command-deck-watcher/state.example.yaml. It holds what cannot be",
            "re-derived (apply state, directives, findings, operator blockers) and it — not the",
            "scheduled job, which is session-only — is what survives a restart.",
        )
    data = load_yaml(path, "the programme state file") or {}
    if not isinstance(data.get("atoms"), list):
        refuse("the state file has no atoms[] list", f"{path}")
    return data


def corpus_coverage(root: Path) -> tuple[list[str], str | None]:
    """Specs referenced by NO release manifest.

    §7 of the tick prompt: prove the denominator covers the corpus. One programme read
    226/226 - 100% for six consecutive ticks while three authorized items sat outside every
    manifest.  Returns (unreferenced_specs, undecidable_reason).
    """
    specs_dir = root / "specs" / "features"
    if not specs_dir.is_dir():
        return [], "specs/features/ does not exist"
    releases = root / ".foundry" / "releases"
    if not releases.is_dir():
        return [], ".foundry/releases/ does not exist"

    referenced: set[str] = set()
    for manifest in sorted(releases.glob("*/release.yaml")):
        data = load_yaml(manifest, f"manifest {manifest.name}") or {}
        for atom in data.get("atoms") or []:
            if isinstance(atom, dict) and atom.get("spec_ref"):
                referenced.add(str(atom["spec_ref"]).lstrip("./"))

    unreferenced = [
        str(p.relative_to(root))
        for p in sorted(specs_dir.rglob("feat-*.md"))
        if str(p.relative_to(root)) not in referenced
    ]
    return unreferenced, None


def measure(root: Path, programme: str, state_path: Path) -> dict:
    manifest_path, manifest_ids = load_manifest(root, programme)
    state = load_state(state_path)
    gitinfo = measure_git(root)

    entries = {}
    bad_stage = []
    for atom in state["atoms"]:
        if not isinstance(atom, dict) or not atom.get("id"):
            refuse("a state atom entry has no id", f"{state_path}")
        stage = atom.get("stage")
        if stage not in STAGES:
            bad_stage.append(f"{atom['id']}: {stage!r}")
        entries[str(atom["id"])] = atom
    if bad_stage:
        refuse(
            "a state atom has an unrecognised stage",
            *bad_stage,
            f"valid stages: {', '.join(STAGES)}",
        )

    unmeasured = [i for i in manifest_ids if i not in entries]
    outside = [i for i in entries if i not in manifest_ids]

    counts = {s: 0 for s in STAGES}
    done, not_done_because_unapplied = [], []
    for atom_id in manifest_ids:
        entry = entries.get(atom_id)
        if entry is None:
            continue
        stage = entry["stage"]
        counts[stage] += 1
        live = bool(entry.get("live_surface"))
        if live:
            if stage == "applied":
                done.append(atom_id)
            elif stage == "merged":
                not_done_because_unapplied.append(atom_id)
        elif stage in DONE_WITHOUT_LIVE_SURFACE:
            done.append(atom_id)

    auth_drift = [
        f"{a['id']}: authorized at auth_seq {a.get('auth_seq')}, branch built against "
        f"{a.get('built_against')}"
        for a in entries.values()
        if a.get("stage") in ("pr-open", "dispatched")
        and a.get("auth_seq") is not None
        and a.get("built_against") is not None
        and a["auth_seq"] != a["built_against"]
    ]

    started = parse_ts(state.get("started_at"), "started_at")
    now = now_utc()
    elapsed = (now - started) if started else None
    rate = forecast = None
    if elapsed and elapsed.total_seconds() > 0 and done:
        rate = len(done) / (elapsed.total_seconds() / 86400)
        remaining = len(manifest_ids) - len(done)
        if rate > 0 and remaining > 0:
            forecast = now + dt.timedelta(days=remaining / rate)

    blockers = []
    for b in state.get("operator_blockers") or []:
        measured_at = parse_ts(b.get("measured_at"), "operator_blockers[].measured_at")
        age_h = (now - measured_at).total_seconds() / 3600 if measured_at else None
        blockers.append(
            {
                "id": b.get("id", "(unnamed)"),
                "what": b.get("what", ""),
                "measured_at": b.get("measured_at"),
                "stale": age_h is None or age_h > STALE_BLOCKER_HOURS,
                "preconditions_verified": bool(b.get("preconditions_verified")),
            }
        )

    unreferenced_specs, corpus_undecidable = corpus_coverage(root)

    return {
        "programme": programme,
        "measured_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "git": gitinfo,
        "manifest": str(manifest_path.relative_to(root)),
        "state_file": str(state_path.relative_to(root)) if state_path.is_relative_to(root) else str(state_path),
        "total": len(manifest_ids),
        "done": len(done),
        "done_ids": done,
        "stages": counts,
        "merged_not_applied": not_done_because_unapplied,
        "unmeasured": unmeasured,
        "outside_denominator": outside,
        "auth_seq_drift": auth_drift,
        "started_at": state.get("started_at"),
        "elapsed_seconds": int(elapsed.total_seconds()) if elapsed else None,
        "rate_per_day": round(rate, 2) if rate else None,
        "forecast": forecast.strftime("%Y-%m-%dT%H:%M:%SZ") if forecast else None,
        "operator_blockers": blockers,
        "unreferenced_specs": unreferenced_specs,
        "corpus_undecidable": corpus_undecidable,
        "open_findings": len(
            [f for f in (state.get("findings") or []) if f.get("disposition") != "closed"]
        ),
        "directives": len(state.get("directives") or []),
    }


# ── rendering ────────────────────────────────────────────────────────────────────────────────


def render(m: dict) -> None:
    g = m["git"]
    dirty = "dirty" if g["dirty"] else ("clean" if g["dirty"] is False else "UNMEASURED")
    if g["behind"] is None:
        behind = f"distance from base UNMEASURED (no upstream for HEAD{'' if g['upstream'] else ''})"
    else:
        behind = f"{g['behind']} commit(s) behind {g['upstream']}"

    pct = (m["done"] / m["total"] * 100) if m["total"] else 0.0

    print(f"COMMAND DECK STATUS — {m['programme']}")
    print(f"  measured    {m['measured_at']} @ {g['head'][:12]} ({dirty}) · {behind}")
    print(f"  denominator {m['manifest']}  ({m['total']} atoms)")
    print(f"  state       {m['state_file']}")
    print()
    print(f"  COMPLETION  {m['done']}/{m['total']}  ({pct:.1f}%)")
    nonzero = " · ".join(f"{k} {v}" for k, v in m["stages"].items() if v)
    print(f"  stages      {nonzero or '(every stage zero — see UNMEASURED below)'}")

    if m["merged_not_applied"]:
        print(
            f"  MERGED NOT APPLIED  {len(m['merged_not_applied'])} — not done, not counted: "
            + ", ".join(m["merged_not_applied"])
        )
    if m["unmeasured"]:
        print(
            f"  UNMEASURED  {len(m['unmeasured'])} manifest atom(s) with no state entry: "
            + ", ".join(m["unmeasured"])
        )
    if m["outside_denominator"]:
        print(
            f"  OUTSIDE THE DENOMINATOR  {len(m['outside_denominator'])} state entr(ies) absent "
            "from the manifest: " + ", ".join(m["outside_denominator"])
        )
    if m["auth_seq_drift"]:
        print(f"  AUTH_SEQ DRIFT  {len(m['auth_seq_drift'])} — re-run the CURRENT contract:")
        for line in m["auth_seq_drift"]:
            print(f"    - {line}")
    if m["corpus_undecidable"]:
        print(f"  CORPUS COVERAGE  UNMEASURED — {m['corpus_undecidable']}")
    elif m["unreferenced_specs"]:
        print(
            f"  CORPUS COVERAGE  {len(m['unreferenced_specs'])} spec(s) referenced by NO release "
            "manifest:"
        )
        for path in m["unreferenced_specs"][:10]:
            print(f"    - {path}")
        if len(m["unreferenced_specs"]) > 10:
            print(f"    … and {len(m['unreferenced_specs']) - 10} more")

    print()
    if m["elapsed_seconds"] is None:
        print("  elapsed     UNMEASURABLE — state file has no started_at")
    else:
        print(
            f"  elapsed     {fmt_delta(dt.timedelta(seconds=m['elapsed_seconds']))} "
            f"since {m['started_at']}"
        )
    if m["forecast"]:
        print(f"  forecast    {m['forecast']} at {m['rate_per_day']} atoms/day")
    else:
        print("  forecast    UNMEASURABLE — no completions yet, or nothing remaining")

    print()
    print(f"  open findings {m['open_findings']} · standing directives {m['directives']}")
    if m["operator_blockers"]:
        print(f"  operator blockers ({len(m['operator_blockers'])}) — re-derive each, every tick:")
        for b in m["operator_blockers"]:
            flags = []
            if b["stale"]:
                flags.append(f"STALE (>{STALE_BLOCKER_HOURS}h or unstamped)")
            if not b["preconditions_verified"]:
                flags.append("PRECONDITIONS UNVERIFIED")
            suffix = f"  [{'; '.join(flags)}]" if flags else ""
            print(f"    - {b['id']}: {b['what']}  measured {b['measured_at']}{suffix}")
    else:
        print("  operator blockers  None")


# ── the instrument test ──────────────────────────────────────────────────────────────────────


def self_test(argv: list[str]) -> int:
    """Drive this instrument against a case whose answer is already known.

    A broken instrument does not fail — it reassures. Two invocations from a directory that is not
    the workspace, one absolute and one relative, because they fail differently and only one of
    them is fixable inside this script.
    """
    script = Path(__file__).resolve()
    passed = True
    with tempfile.TemporaryDirectory() as tmp:
        print("SELF-TEST — running the instrument from a directory that is not the workspace")
        print(f"  cwd: {tmp}\n")

        proc = subprocess.run(
            [sys.executable, str(script), *argv],
            cwd=tmp,
            capture_output=True,
            text=True,
            env={**os.environ, "CLAUDE_PROJECT_DIR": tmp},
        )
        loud = proc.returncode != 0 and "REFUSED" in proc.stdout
        print(f"  [1] absolute path, wrong cwd → exit {proc.returncode}, "
              f"{len(proc.stdout.splitlines())} line(s) on stdout")
        print(f"      {'PASS' if loud else 'FAIL'} — must exit non-zero AND print REFUSED on stdout")
        if not loud:
            passed = False
            print("      stdout was:\n" + (proc.stdout or "(empty)"))

        rel = subprocess.run(
            [sys.executable, "scripts/command-deck-status.py", *argv],
            cwd=tmp,
            capture_output=True,
            text=True,
        )
        silent = rel.returncode != 0 and not rel.stdout.strip()
        print(f"\n  [2] RELATIVE path, wrong cwd → exit {rel.returncode}, "
              f"{len(rel.stdout.splitlines())} line(s) on stdout")
        print(f"      {'HAZARD CONFIRMED' if silent else 'unexpected'} — the interpreter cannot "
              "find the script, so")
        print("      NOTHING reaches stdout. No script can fix this from the inside: it is why")
        print("      every tick call must start with an absolute `cd <workspace> &&`, and why an")
        print("      empty result is an INSTRUMENT FAILURE until proven otherwise.")

    print(f"\nSELF-TEST {'PASS' if passed else 'FAIL'}")
    return 0 if passed else 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Deterministic programme measurement for the Command Deck watcher tick.",
        epilog="Refuses (exit 2) rather than printing a plausible zero. See "
               "docs/command-deck-watcher/README.md",
    )
    parser.add_argument("programme", help="programme id — the <id> in .foundry/releases/<id>/")
    parser.add_argument("--state", help="state file (default: command-deck/<programme>/state.yaml)")
    parser.add_argument("--root", help="workspace root (default: $CLAUDE_PROJECT_DIR, else cwd)")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="prove the instrument refuses loudly from the wrong directory",
    )
    args = parser.parse_args()

    if args.self_test:
        return self_test([args.programme] + (["--state", args.state] if args.state else []))

    root = resolve_root(args.root)
    state_path = Path(args.state) if args.state else root / "command-deck" / args.programme / "state.yaml"
    if not state_path.is_absolute():
        state_path = (root / state_path).resolve()

    m = measure(root, args.programme, state_path)
    if args.json:
        print(json.dumps(m, indent=2, sort_keys=True))
    else:
        render(m)
    return 0


if __name__ == "__main__":
    sys.exit(main())
