---
repo: sc-reusable-workflows
path: ~/projects/ship-cars-usa/sc-reusable-workflows
stack: GitHub Actions reusable workflows / docs / scripts
domain: infrastructure
shape: workflows + scripts + docs (16 files)
last-synced-commit: 78ed06bbadca1359f3e2ba8516964254f0021b0d
last-synced-date: 2026-05-12
maintainer: unknown
status: stale
---

# sc-reusable-workflows

## What it is
**`sc-reusable-workflows`** — Ship.Cars's shared **GitHub Actions reusable workflows** + supporting `docs/runbooks/` and `scripts/`. Reusable workflows are GitHub Actions' mechanism for sharing CI/CD logic across multiple repos (one definition, called from many `.github/workflows/*.yml` files via `uses: ship-cars-usa/sc-reusable-workflows/.github/workflows/X.yml@vN`).

Last commit 2026-04-28.

## How it fits

- **Consumed by:** every repo in `ship-cars-usa/` org that has `.github/workflows/*.yml` calling a reusable workflow from this repo.
- **Companion to:** `automation` (the fleet's Jenkins-driven test framework — different CI surface).

## Build / test / run
```
# Workflows are invoked by GitHub Actions; no local "build."
# Test changes via a workflow_dispatch trigger in a downstream repo.
```

## Don't-do-here / gotchas

- **Breaking changes here cascade to every consuming repo's CI.** Use semver tags (e.g. `@v1`, `@v2`) and add tests before publishing a new major.
- **Reusable workflows can carry secrets** — verify the `permissions:` block to avoid leaking tokens to less-trusted callers.
- **`docs/runbooks/`** — operational runbooks for the workflows themselves.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/automation.md` — Jenkins-side counterpart for test automation.
- `~/projects/codebase-map/domains/infrastructure.md`.
