#!/usr/bin/env python3
"""
bootstrap_repo_md.py — generate a stub shadow doc for a single repo.

Usage:
    python3 bootstrap_repo_md.py <repo-name> [--force]

Reads ~/projects/ship-cars-usa/<repo>/ to extract:
  - stack (Quarkus / Spring / Node / Python / Go / unknown)
  - shape (single-module / multi-module by counting pom.xml files)
  - last-synced-commit (git rev-parse HEAD)

Writes ~/projects/codebase-map/repos/<repo>.md with status: stub.
Refuses to overwrite an existing file unless --force is passed.

Stdlib only.
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

PROJECTS_ROOT = Path.home() / "projects" / "ship-cars-usa"
MAP_REPOS = Path.home() / "projects" / "codebase-map" / "repos"


def detect_stack(repo: Path) -> str:
    pom = repo / "pom.xml"
    if pom.exists():
        try:
            text = pom.read_text(errors="replace")
            # Spring Boot first — its parent declaration is the strongest signal,
            # and a Spring service may pull a Quarkus-flavored client library.
            sb = re.search(r"<artifactId>spring-boot-starter-parent</artifactId>\s*<version>([^<]+)</", text)
            if sb:
                return f"Java/Spring Boot {sb.group(1)}"
            # Quarkus: require an artifactId starting with "quarkus-" (skips libs that
            # merely mention "quarkus" in their groupId).
            if re.search(r"<artifactId>quarkus-[\w-]+</artifactId>", text):
                m = re.search(r"<quarkus\.platform\.version>([^<]+)</", text)
                ver = f" {m.group(1)}" if m else ""
                return f"Java/Quarkus{ver}"
            if "spring-boot" in text.lower():
                return "Java/Spring Boot"
            return "Java/Maven"
        except Exception:
            return "Java/Maven (pom unparseable)"
    if (repo / "build.gradle").exists() or (repo / "build.gradle.kts").exists():
        return "Java/Gradle"
    if (repo / "package.json").exists():
        # Distinguish frontend (React/Vite) from Node-tooling
        try:
            pj = (repo / "package.json").read_text(errors="replace")
            if '"react"' in pj or '"single-spa"' in pj or '"vite"' in pj.lower():
                return "Node/Frontend (React/Vite)"
            if '"@types/node"' in pj or '"typescript"' in pj:
                return "Node/TypeScript"
            return "Node/JavaScript"
        except Exception:
            return "Node/JavaScript"
    if (repo / "pyproject.toml").exists() or (repo / "requirements.txt").exists():
        return "Python"
    if (repo / "go.mod").exists():
        return "Go"
    # Terraform live envs / modules — check recursively (capped via try)
    try:
        has_tf = any(repo.rglob("*.tf"))
    except Exception:
        has_tf = bool(list(repo.glob("*.tf")))
    try:
        has_terragrunt = any(repo.rglob("terragrunt.hcl"))
    except Exception:
        has_terragrunt = False
    if has_tf or has_terragrunt:
        if repo.name.startswith("devops-tf-live-") or "live" in repo.name:
            return "Terraform (live env)"
        if repo.name.startswith("devops-tf-module-"):
            return "Terraform (module)"
        return "Terraform"
    # Helm
    if (repo / "Chart.yaml").exists() or list(repo.glob("**/Chart.yaml")):
        return "Helm chart"
    # Mobile
    if (repo / "Podfile").exists() or (repo / "Podfile.lock").exists():
        return "iOS (Swift)"
    if (repo / "settings.gradle.kts").exists() or (repo / "build.gradle.kts").exists():
        return "Android (Gradle KTS)"
    # Chrome extension
    if (repo / "manifest.json").exists():
        return "Browser extension"
    # Docs/empty
    md_count = len(list(repo.glob("*.md")))
    file_count = sum(1 for _ in repo.iterdir() if _.is_file())
    if md_count > 0 and file_count <= md_count + 2:
        return "Docs/Markdown"
    if file_count == 0 and not any(repo.iterdir()):
        return "empty"
    return "unknown"


def detect_kind(stack: str) -> str:
    """High-level category for the body template."""
    if "Quarkus" in stack or "Spring" in stack or "Java" in stack:
        return "java"
    if "Frontend" in stack:
        return "frontend"
    if "Node" in stack:
        return "node"
    if stack == "Python":
        return "python"
    if stack == "Go":
        return "go"
    if stack.startswith("Terraform"):
        return "terraform"
    if "Helm" in stack:
        return "helm"
    if stack in ("iOS (Swift)", "Android (Gradle KTS)"):
        return "mobile"
    if stack == "Browser extension":
        return "browser-ext"
    if stack == "Docs/Markdown":
        return "docs"
    return "other"


def detect_shape(repo: Path) -> str:
    pom_count = sum(1 for _ in repo.rglob("pom.xml") if "/target/" not in str(_))
    if pom_count > 1:
        return f"multi-module ({pom_count} poms)"
    if pom_count == 1:
        return "single-module"
    return "n/a"


def git_head(repo: Path) -> str:
    try:
        out = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=5, check=True,
        )
        return out.stdout.strip()
    except Exception:
        return "unknown"


def extract_artifact_id(repo: Path) -> str | None:
    pom = repo / "pom.xml"
    if not pom.exists():
        return None
    try:
        ns = "{http://maven.apache.org/POM/4.0.0}"
        tree = ET.parse(pom)
        artifact = tree.getroot().find(f"{ns}artifactId")
        return artifact.text if artifact is not None else None
    except Exception:
        return None


BUILD_HINTS = {
    "java":        "mvn clean package\nmvn test\nmvn quarkus:dev   # if Quarkus\nmvn spring-boot:run  # if Spring Boot",
    "frontend":    "npm install\nnpm run dev\nnpm run build\nnpm test",
    "node":        "npm install\nnpm run start\nnpm test",
    "python":      "python3 -m venv .venv && source .venv/bin/activate\npip install -r requirements.txt   # or `pip install -e .` if pyproject.toml\npytest",
    "go":          "go build ./...\ngo test ./...\ngo run ./cmd/...",
    "terraform":   "terraform init\nterraform plan\nterraform apply   # don't run blindly — review plan",
    "helm":        "helm lint .\nhelm template . | less\nhelm install --dry-run --debug ...",
    "mobile":      "# iOS:    pod install && xcodebuild -workspace ... -scheme ... build\n# Android: ./gradlew assembleDebug && ./gradlew test",
    "browser-ext": "# Load unpacked from chrome://extensions/ during dev\n# Production: zip the folder and upload to Web Store",
    "docs":        "# Markdown only — no build step",
    "other":       "# Inspect repo manually for build/test commands",
}

KIND_NOTES = {
    "java":        "Maven artifactId: `{artifact}`.",
    "frontend":    "Frontend repo — likely a Single-SPA micro-frontend or Vite app.",
    "node":        "Node service / package — check `package.json` for entrypoint.",
    "python":      "Python service or ML pipeline.",
    "go":          "Go service.",
    "terraform":   "Terraform IaC — review `*.tf` and any `terragrunt.hcl` for module structure.",
    "helm":        "Helm chart — review `Chart.yaml` and `templates/`.",
    "mobile":      "Mobile app.",
    "browser-ext": "Browser extension (manifest.json present).",
    "docs":        "Docs / knowledge repo — content-only.",
    "other":       "Stack not auto-detected; inspect manually.",
}


def render(repo_name: str, repo: Path) -> str:
    stack = detect_stack(repo)
    shape = detect_shape(repo)
    head = git_head(repo)
    kind = detect_kind(stack)
    today = dt.date.today().isoformat()

    if kind == "java":
        artifact = extract_artifact_id(repo) or repo_name
        kind_note = KIND_NOTES["java"].format(artifact=artifact)
    else:
        kind_note = KIND_NOTES.get(kind, KIND_NOTES["other"])

    build_hint = BUILD_HINTS.get(kind, BUILD_HINTS["other"])

    return f"""---
repo: {repo_name}
path: ~/projects/ship-cars-usa/{repo_name}
stack: {stack}
domain: unassigned
shape: {shape}
last-synced-commit: {head}
last-synced-date: {today}
maintainer: unknown
status: stub
---

# {repo_name}

## What it is
Stub. {kind_note} Replace this paragraph with what the repo actually does after reading it. Mark assumptions explicitly; do not fabricate.

## How it fits
- Consumes API of: unknown
- Publishes events to: unknown
- Owns data store: unknown
- Owns no data; pure orchestrator: unknown

## Build / test / run
```
{build_hint}
```

## Key abstractions
- TODO

## Don't-do-here / gotchas
- TODO

## Relevant ADRs / docs
- TODO
"""


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("repo_name", help="Folder name under ~/projects/ship-cars-usa/")
    p.add_argument("--force", action="store_true", help="Overwrite existing shadow doc")
    args = p.parse_args()

    repo = PROJECTS_ROOT / args.repo_name
    if not repo.is_dir():
        print(f"ERROR: not a directory: {repo}", file=sys.stderr)
        return 2

    out = MAP_REPOS / f"{args.repo_name}.md"
    if out.exists() and not args.force:
        print(f"SKIP: {out} already exists (use --force to overwrite)")
        return 0

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(args.repo_name, repo))
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
