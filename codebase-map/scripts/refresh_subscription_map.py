#!/usr/bin/env python3
"""
refresh_subscription_map.py — rebuild event-catalog.subscriptions.tsv from gcloud.

Usage:
    python3 refresh_subscription_map.py [--project <gcp-project>] [--dry-run]

Requires:
  - `gcloud` on PATH and authenticated (`gcloud auth application-default login`).
  - A project either passed via --project or set in `gcloud config get-value project`.

What it does:
  1. Runs `gcloud pubsub subscriptions list --format=json` for the project.
  2. For each subscription, extracts (subscription_name, topic_name).
  3. Cross-references the names against env-var conventions seen in the fleet's
     Python services (e.g., `FOO_SUBSCRIPTION` env var typically resolves to a
     subscription named `foo-subscription` or `pubsub-foo-subscription`).
  4. Writes the TSV. Preserves comment header from the existing file.

NOT part of the auto-run path. Run manually when subscriptions change.

Stdlib only.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

TSV = Path.home() / "projects" / "codebase-map" / "relations" / "event-catalog.subscriptions.tsv"


def _gcloud_list(project: str | None) -> list[dict]:
    cmd = ["gcloud", "pubsub", "subscriptions", "list", "--format=json"]
    if project:
        cmd += ["--project", project]
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if out.returncode != 0:
        print(f"ERROR: gcloud failed: {out.stderr.strip()}", file=sys.stderr)
        return []
    try:
        return json.loads(out.stdout)
    except json.JSONDecodeError as e:
        print(f"ERROR: could not parse gcloud output: {e}", file=sys.stderr)
        return []


def _short(resource_path: str) -> str:
    # "projects/ship-cars/subscriptions/foo-sub" -> "foo-sub"
    return resource_path.rsplit("/", 1)[-1]


def _read_header(path: Path) -> list[str]:
    """Preserve the leading `# ...` header lines from the existing TSV."""
    if not path.exists():
        return []
    header: list[str] = []
    for line in path.read_text().splitlines():
        if line.startswith("#") or not line.strip():
            header.append(line)
        else:
            break
    return header


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project", help="GCP project; defaults to gcloud config")
    p.add_argument("--dry-run", action="store_true",
                   help="Print proposed TSV to stdout; do not write the file.")
    args = p.parse_args()

    subs = _gcloud_list(args.project)
    if not subs:
        return 1

    header = _read_header(TSV)
    today = subprocess.run(["date", "+%Y-%m-%d"], capture_output=True, text=True).stdout.strip()
    source_tag = f"gcloud-{today}"

    rows: list[tuple[str, str, str]] = []
    for s in subs:
        sub_name = _short(s.get("name", ""))
        topic_path = s.get("topic", "")
        topic_name = _short(topic_path) if topic_path else ""
        if not sub_name or not topic_name or topic_name == "_deleted-topic_":
            continue
        rows.append((sub_name, topic_name, source_tag))

    rows.sort()

    out_lines = list(header)
    if not header or not header[-1].startswith("#"):
        out_lines.append("# subscription_env_var\ttopic_name\tsource")
    out_lines.append("")
    for sub, topic, src in rows:
        out_lines.append(f"{sub}\t{topic}\t{src}")

    text = "\n".join(out_lines) + "\n"

    if args.dry_run:
        sys.stdout.write(text)
        print(f"\n[dry-run] {len(rows)} subscription rows", file=sys.stderr)
        return 0

    TSV.write_text(text)
    print(f"wrote {TSV} ({len(rows)} rows from project={args.project or 'default'})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
