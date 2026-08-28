#!/usr/bin/env python3
"""
drift_check.py — compare each shadow doc's last-synced-commit to the
current git HEAD of the corresponding repo.

Usage:
    python3 drift_check.py <repo-name>          # check one
    python3 drift_check.py --all                 # check every shadow
    python3 drift_check.py --all --mark-stale    # also rewrite frontmatter status: stale on drift
    python3 drift_check.py --event-catalog       # diff regenerated vs committed event-catalog.md

Exit code:
    0 = no drift
    1 = drift detected on at least one shadow / catalog
    2 = invocation error

Stdlib only.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

PROJECTS_ROOT = Path.home() / "projects" / "ship-cars-usa"
MAP_ROOT = Path.home() / "projects" / "codebase-map"
MAP_REPOS = MAP_ROOT / "repos"
EVENT_CATALOG = MAP_ROOT / "relations" / "event-catalog.md"
EVENT_SCHEMAS_DIR = MAP_ROOT / "relations" / "event-schemas"
GEN_SCRIPT = MAP_ROOT / "scripts" / "gen_event_catalog.py"
GEN_SCHEMAS_SCRIPT = MAP_ROOT / "scripts" / "gen_event_schemas.py"

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def parse_frontmatter(text: str) -> dict[str, str]:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    out: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            out[k.strip()] = v.strip()
    return out


def replace_frontmatter_field(text: str, key: str, value: str) -> str:
    def repl(match: re.Match[str]) -> str:
        body = match.group(1)
        new_lines: list[str] = []
        replaced = False
        for line in body.splitlines():
            if line.startswith(f"{key}:"):
                new_lines.append(f"{key}: {value}")
                replaced = True
            else:
                new_lines.append(line)
        if not replaced:
            new_lines.append(f"{key}: {value}")
        return "---\n" + "\n".join(new_lines) + "\n---\n"
    return FRONTMATTER_RE.sub(repl, text, count=1)


def git_head(repo: Path) -> str | None:
    try:
        out = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=5, check=True,
        )
        return out.stdout.strip()
    except Exception:
        return None


def check_one(shadow: Path, mark_stale: bool) -> bool:
    text = shadow.read_text()
    fm = parse_frontmatter(text)
    repo_name = fm.get("repo")
    recorded = fm.get("last-synced-commit")
    if not repo_name or not recorded:
        print(f"[malformed]   {shadow.name}: missing repo/last-synced-commit")
        return True
    repo = PROJECTS_ROOT / repo_name
    if not repo.is_dir():
        print(f"[missing]     {shadow.name}: repo path {repo} does not exist")
        return True
    actual = git_head(repo)
    if recorded == "unknown" and actual is None:
        # Recorded as not-a-git-checkout and still not-a-git-checkout — no drift to report.
        return False
    if actual is None:
        print(f"[git-fail]    {shadow.name}: could not read HEAD of {repo} (recorded={recorded[:12] if recorded != 'unknown' else 'unknown'})")
        return True
    if recorded == "unknown" and actual is not None:
        print(f"[promoted]    {shadow.name}: was 'unknown', repo now has HEAD {actual[:12]} — re-run bootstrap to update")
        return True
    if actual == recorded:
        return False
    print(f"[DRIFT]       {shadow.name}: shadow={recorded[:12]} HEAD={actual[:12]}")
    if mark_stale and fm.get("status") != "stale":
        new = replace_frontmatter_field(text, "status", "stale")
        shadow.write_text(new)
        print(f"              -> marked status: stale")
    return True


_DATE_LINE_RE = re.compile(r"^last-generated-date:\s*\d{4}-\d{2}-\d{2}\s*$", re.MULTILINE)


def _normalize_catalog(text: str) -> str:
    """Strip the auto-changing `last-generated-date` frontmatter field so the
       diff reflects actual content drift, not the regeneration timestamp."""
    return _DATE_LINE_RE.sub("last-generated-date: <stripped>", text)


def check_event_schemas() -> bool:
    """Regenerate the per-topic schema files into a temp directory and compare
       file-by-file against the committed copies (normalizing the per-file
       last-generated-date)."""
    import difflib
    import tempfile

    if not EVENT_SCHEMAS_DIR.is_dir():
        print(f"[missing]     event-schemas/: {EVENT_SCHEMAS_DIR} not found; "
              f"run gen_event_schemas.py first")
        return True
    if not GEN_SCHEMAS_SCRIPT.exists():
        print(f"[missing]     gen_event_schemas.py: {GEN_SCHEMAS_SCRIPT} not found")
        return True

    # The generator writes directly to relations/event-schemas/. We can't
    # cleanly redirect it without modifying the script, so we snapshot the
    # current directory, regenerate, diff, and restore.
    committed: dict[str, str] = {}
    for md in EVENT_SCHEMAS_DIR.glob("*.md"):
        committed[md.name] = _DATE_LINE_RE.sub(
            "last-generated-date: <stripped>", md.read_text())

    try:
        out = subprocess.run(
            ["python3", str(GEN_SCHEMAS_SCRIPT)],
            capture_output=True, text=True, timeout=600, check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"[gen-fail]    event-schemas/: generator failed:\n{e.stderr}")
        # Restore committed copies before returning.
        for name, body in committed.items():
            (EVENT_SCHEMAS_DIR / name).write_text(body)
        return True
    except subprocess.TimeoutExpired:
        print("[gen-fail]    event-schemas/: generator timed out (>10 min)")
        return True

    drifted_files: list[str] = []
    extra_files: list[str] = []
    fresh: dict[str, str] = {}
    for md in EVENT_SCHEMAS_DIR.glob("*.md"):
        text = _DATE_LINE_RE.sub("last-generated-date: <stripped>", md.read_text())
        fresh[md.name] = text
        if md.name not in committed:
            extra_files.append(md.name)
        elif committed[md.name] != text:
            drifted_files.append(md.name)
    missing_files = [n for n in committed if n not in fresh]

    if not drifted_files and not extra_files and not missing_files:
        print(f"[clean]       event-schemas/ ({len(fresh)} files)")
        return False

    print(f"[DRIFT]       event-schemas/: {len(drifted_files)} changed, "
          f"{len(extra_files)} new, {len(missing_files)} removed")
    for name in drifted_files[:5]:
        diff = list(difflib.unified_diff(
            committed[name].splitlines(keepends=True),
            fresh[name].splitlines(keepends=True),
            fromfile=f"committed/{name}", tofile=f"regenerated/{name}", n=1,
        ))
        sys.stdout.write("".join(diff[:40]))
        if len(diff) > 40:
            print(f"  ... ({len(diff) - 40} more lines)")
    for name in extra_files[:10]:
        print(f"  [new]      {name}")
    for name in missing_files[:10]:
        print(f"  [removed]  {name}")
    return True


def check_event_catalog() -> bool:
    """Re-run the generator to a buffer and diff against the committed catalog.
       Returns True on drift, False on clean."""
    import difflib
    if not EVENT_CATALOG.exists():
        print(f"[missing]     event-catalog.md: {EVENT_CATALOG} not found; "
              f"run gen_event_catalog.py first")
        return True
    if not GEN_SCRIPT.exists():
        print(f"[missing]     gen_event_catalog.py: {GEN_SCRIPT} not found")
        return True
    try:
        out = subprocess.run(
            ["python3", str(GEN_SCRIPT), "--dry-run"],
            capture_output=True, text=True, timeout=300, check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"[gen-fail]    event-catalog.md: generator failed:\n{e.stderr}")
        return True
    except subprocess.TimeoutExpired:
        print("[gen-fail]    event-catalog.md: generator timed out (>5 min)")
        return True

    fresh = _normalize_catalog(out.stdout)
    committed = _normalize_catalog(EVENT_CATALOG.read_text())
    if fresh == committed:
        print("[clean]       event-catalog.md")
        return False
    diff = list(difflib.unified_diff(
        committed.splitlines(keepends=True),
        fresh.splitlines(keepends=True),
        fromfile="committed/event-catalog.md",
        tofile="regenerated/event-catalog.md",
        n=2,
    ))
    print(f"[DRIFT]       event-catalog.md: {len(diff)} diff line(s) — regenerate to refresh")
    sys.stdout.write("".join(diff[:120]))
    if len(diff) > 120:
        print(f"... ({len(diff) - 120} more diff lines suppressed)", file=sys.stdout)
    return True


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("repo_name", nargs="?", help="One repo to check; omit with --all")
    p.add_argument("--all", action="store_true", help="Check every shadow")
    p.add_argument("--mark-stale", action="store_true", help="Rewrite status: stale on drift")
    p.add_argument("--event-catalog", action="store_true",
                   help="Diff regenerated event-catalog.md against the committed file")
    p.add_argument("--event-schemas", action="store_true",
                   help="Diff regenerated event-schemas/*.md files against the committed copies")
    args = p.parse_args()

    if args.event_catalog:
        if args.repo_name or args.all or args.mark_stale or args.event_schemas:
            p.error("--event-catalog cannot be combined with other modes")
            return 2
        return 1 if check_event_catalog() else 0

    if args.event_schemas:
        if args.repo_name or args.all or args.mark_stale:
            p.error("--event-schemas cannot be combined with other modes")
            return 2
        return 1 if check_event_schemas() else 0

    if args.all == bool(args.repo_name):
        p.error("provide one of: <repo-name>, --all, --event-catalog, --event-schemas")
        return 2

    if args.repo_name:
        shadows = [MAP_REPOS / f"{args.repo_name}.md"]
        if not shadows[0].exists():
            print(f"ERROR: no shadow at {shadows[0]}", file=sys.stderr)
            return 2
    else:
        shadows = sorted(p for p in MAP_REPOS.glob("*.md") if not p.name.startswith("_"))

    drifted = 0
    for s in shadows:
        if check_one(s, args.mark_stale):
            drifted += 1

    total = len(shadows)
    clean = total - drifted
    print(f"\nchecked {total} shadow(s): {clean} clean, {drifted} drifted")
    return 1 if drifted else 0


if __name__ == "__main__":
    sys.exit(main())
