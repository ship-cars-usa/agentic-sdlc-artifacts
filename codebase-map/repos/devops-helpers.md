---
repo: devops-helpers
path: ~/projects/ship-cars-usa/devops-helpers
stack: Mixed (mostly shell / bash / markdown helpers; auto-classified as Docs because of the .md content)
domain: infrastructure
shape: helper-scripts + docs (34 files)
last-synced-commit: 6ff262a070f7e82060e524914265b8684d95c600
last-synced-date: 2026-05-12
maintainer: unknown
status: stale
---

# devops-helpers

## What it is
**DevOps helper-scripts repo** — shell / bash utilities for common operational tasks. Companion to `devops-docs` (docs only). The helpers here are runnable scripts that the docs reference.

Last commit 2026-03-30 — actively maintained.

## How it fits

- **Reference scripts** for the DevOps team. Cluster operations, debugging, common workflows.
- **Pairs with:** `devops-docs` (the documentation side).

## Build / test / run
```
# Per-script — usually shell-script invocation with documented args.
```

## Don't-do-here / gotchas

- **Operator-run scripts.** Verify which cluster context is active before running anything that touches K8s.
- **Confirm script provenance** before running — these are often shared via Slack and may get copied into the repo without thorough review.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/devops-docs.md` — paired documentation.
- `~/projects/codebase-map/domains/infrastructure.md`.
