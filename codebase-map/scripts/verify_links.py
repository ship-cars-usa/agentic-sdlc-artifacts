#!/usr/bin/env python3
"""
verify_links.py — lint pass over all shadow docs.

Checks:
  1. Required frontmatter keys present.
  2. `path:` field resolves to an existing directory.
  3. `repo:` field matches the filename stem.
  4. No duplicate `repo:` values across shadows.
  5. `_index.md` (if present) lists exactly the set of shadow files.
  6. Markdown links of the form ~/projects/<...> resolve.
  7. Status is one of {seed, stub, verified, stale}.

Exit code: 0 on success, 1 on any failure.
Stdlib only.
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

MAP_ROOT = Path.home() / "projects" / "codebase-map"
MAP_REPOS = MAP_ROOT / "repos"
RELATIONS = MAP_ROOT / "relations"
EVENT_CATALOG = RELATIONS / "event-catalog.md"
PROJECTS_ROOT = Path.home() / "projects"
SHIP_CARS = PROJECTS_ROOT / "ship-cars-usa"

REQUIRED_FIELDS = {
    "repo", "path", "stack", "domain", "shape",
    "last-synced-commit", "last-synced-date", "maintainer", "status",
}
VALID_STATUS = {"seed", "stub", "verified", "stale"}

EVENT_CATALOG_REQUIRED_FRONTMATTER = {
    "name", "description", "generator", "last-generated-date", "status",
}
EVENT_CATALOG_VALID_ROW_STATUS = {"resolved", "symbolic", "partial", "unresolved"}

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
TILDE_LINK_RE = re.compile(r"~/projects/[^\s)`]+")
EVENT_ROW_RE = re.compile(r"^\|\s*(?P<topic>[^|]+?)\s*\|"
                          r"\s*(?P<producers>[^|]*?)\s*\|"
                          r"\s*(?P<consumers>[^|]*?)\s*\|"
                          r"\s*(?P<tier>[^|]*?)\s*\|"
                          r"\s*(?P<sub>[^|]*?)\s*\|"
                          r"\s*(?P<schema_ver>[^|]*?)\s*\|"
                          r"\s*(?P<schema_src>[^|]*?)\s*\|"
                          r"\s*(?P<row_status>[^|]+?)\s*\|"
                          r"\s*(?P<evidence>[^|]*?)\s*\|\s*$")

EVENT_SCHEMA_REQUIRED_FRONTMATTER = {
    "topic", "tier", "schema-source", "last-generated-date", "status",
}
EVENT_SCHEMA_VALID_SOURCES = {"lombok-data", "java-record", "pydantic", "partial", "none"}
EVENT_SCHEMAS_DIR = MAP_ROOT / "relations" / "event-schemas"


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


def expand(p: str) -> Path:
    return Path(os.path.expanduser(p))


def verify_event_catalog(errors: list[str]) -> None:
    """Lint the Tier 1 event catalog at relations/event-catalog.md."""
    if not EVENT_CATALOG.exists():
        return  # Optional artifact; absence is not an error.
    text = EVENT_CATALOG.read_text()
    prefix = "event-catalog.md:"
    fm = parse_frontmatter(text)
    missing = EVENT_CATALOG_REQUIRED_FRONTMATTER - fm.keys()
    if missing:
        errors.append(f"{prefix} missing frontmatter fields: {sorted(missing)}")
    if fm.get("status") and fm["status"] not in {"seed", "stub", "verified", "stale"}:
        errors.append(f"{prefix} invalid frontmatter status `{fm['status']}`")

    body = text.split("---\n", 2)[-1] if text.startswith("---\n") else text
    # Skip header/legend lines; only check rows starting with a topic cell.
    seen_topics: set[str] = set()
    for lineno, line in enumerate(body.splitlines(), start=1):
        if not line.startswith("| "):
            continue
        if line.startswith("| Topic ") or set(line.strip()) <= {"|", "-", " "}:
            continue
        m = EVENT_ROW_RE.match(line)
        if not m:
            errors.append(f"{prefix} body L{lineno}: row doesn't parse as 9-column table")
            continue
        row_status = m.group("row_status").strip()
        if row_status not in EVENT_CATALOG_VALID_ROW_STATUS:
            errors.append(
                f"{prefix} body L{lineno}: invalid Status `{row_status}` "
                f"(must be one of {sorted(EVENT_CATALOG_VALID_ROW_STATUS)})")
        tier = m.group("tier").strip()
        if tier not in {"carrier", "fleet"}:
            errors.append(f"{prefix} body L{lineno}: invalid Tier `{tier}`")
        topic_cell = m.group("topic").strip()
        if topic_cell in seen_topics:
            errors.append(f"{prefix} body L{lineno}: duplicate topic row `{topic_cell}`")
        seen_topics.add(topic_cell)

        # Validate evidence pointer if it looks like a path:line reference.
        evidence = m.group("evidence").strip()
        if evidence and evidence.startswith("service-graph.md:L"):
            # Pointer into the sibling relations file. Confirm the file exists.
            if not (RELATIONS / "service-graph.md").is_file():
                errors.append(f"{prefix} body L{lineno}: evidence cites missing "
                              f"service-graph.md")
        elif "/" in evidence and ":" not in evidence and evidence:
            # Repo-relative path; first segment should be a real repo.
            repo = evidence.split("/", 1)[0]
            if not (SHIP_CARS / repo).is_dir():
                errors.append(f"{prefix} body L{lineno}: evidence cites unknown "
                              f"repo `{repo}`")


def verify_event_schemas(errors: list[str]) -> None:
    """Lint the per-topic schema sidecar at relations/event-schemas/*.md."""
    if not EVENT_SCHEMAS_DIR.is_dir():
        return
    # Cross-reference: every per-topic file's `topic:` must match a catalog row.
    catalog_topics: set[str] = set()
    if EVENT_CATALOG.exists():
        cat_body = EVENT_CATALOG.read_text()
        for line in cat_body.splitlines():
            if not line.startswith("| "):
                continue
            m = EVENT_ROW_RE.match(line)
            if not m:
                continue
            t = m.group("topic").strip().strip("`")
            # Strip presentation prefixes like _(prose)_ / _(unresolved)_.
            t = re.sub(r"^_\([\w-]+\)_\s+", "", t)
            catalog_topics.add(t)

    for md in EVENT_SCHEMAS_DIR.glob("*.md"):
        if md.name.startswith("_"):
            continue
        prefix = f"event-schemas/{md.name}:"
        text = md.read_text(errors="replace")
        fm = parse_frontmatter(text)
        missing = EVENT_SCHEMA_REQUIRED_FRONTMATTER - fm.keys()
        if missing:
            errors.append(f"{prefix} missing frontmatter fields: {sorted(missing)}")
            continue
        topic = fm["topic"]
        if catalog_topics and topic not in catalog_topics:
            errors.append(f"{prefix} `topic: {topic}` does not match any event-catalog row")
        source = fm.get("schema-source", "").strip("~ ")
        if source and source not in EVENT_SCHEMA_VALID_SOURCES:
            errors.append(f"{prefix} invalid schema-source `{source}` "
                          f"(allowed: {sorted(EVENT_SCHEMA_VALID_SOURCES)})")
        dto_file = fm.get("canonical-dto-file", "").strip()
        if dto_file and dto_file != "~":
            if not expand(dto_file.lstrip("~/").replace("~/", "")).is_file() \
                    and not expand(dto_file).is_file():
                errors.append(f"{prefix} canonical-dto-file does not resolve: {dto_file}")


def main() -> int:
    errors: list[str] = []
    shadows = sorted(p for p in MAP_REPOS.glob("*.md") if not p.name.startswith("_"))
    seen_repos: dict[str, str] = {}

    for s in shadows:
        text = s.read_text()
        fm = parse_frontmatter(text)
        prefix = f"{s.name}:"

        missing = REQUIRED_FIELDS - fm.keys()
        if missing:
            errors.append(f"{prefix} missing frontmatter fields: {sorted(missing)}")
            continue

        if fm["repo"] != s.stem:
            errors.append(f"{prefix} `repo: {fm['repo']}` does not match filename stem `{s.stem}`")

        if fm["repo"] in seen_repos:
            errors.append(f"{prefix} duplicate `repo:` (also in {seen_repos[fm['repo']]})")
        seen_repos[fm["repo"]] = s.name

        path = expand(fm["path"])
        if not path.is_dir():
            errors.append(f"{prefix} `path:` does not exist: {path}")

        if fm["status"] not in VALID_STATUS:
            errors.append(f"{prefix} invalid status `{fm['status']}` (must be one of {sorted(VALID_STATUS)})")

        for link in TILDE_LINK_RE.findall(text):
            target_str = link.split("#")[0].rstrip(".,;:")
            target = expand(target_str)
            if not target.exists():
                errors.append(f"{prefix} broken link to nonexistent path: {target_str}")

    index = MAP_REPOS / "_index.md"
    if index.exists():
        listed = set(re.findall(r"\((?:\./)?([\w.-]+)\.md\)", index.read_text()))
        actual = {s.stem for s in shadows}
        only_in_index = listed - actual
        only_on_disk = actual - listed
        if only_in_index:
            errors.append(f"_index.md: lists shadows that don't exist: {sorted(only_in_index)}")
        if only_on_disk:
            errors.append(f"_index.md: missing shadows that do exist: {sorted(only_on_disk)}")

    verify_event_catalog(errors)
    verify_event_schemas(errors)

    if errors:
        for e in errors:
            print(f"FAIL  {e}")
        print(f"\n{len(errors)} error(s) across {len(shadows)} shadow(s) + event-catalog")
        return 1
    print(f"OK    {len(shadows)} shadow(s) + event-catalog verified clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
