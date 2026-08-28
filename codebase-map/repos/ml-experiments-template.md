---
repo: ml-experiments-template
path: ~/projects/ship-cars-usa/ml-experiments-template
stack: Python / VS Code Dev Containers / DVC (Data Version Control) / GCS-backed shared storage
domain: analytics
shape: clone-and-rename template repo
last-synced-commit: ac40095a04fc40e202075fda9be8e50ad5b7d1bf
last-synced-date: 2026-05-12
maintainer: unknown
status: seed
---

# ml-experiments-template

## What it is
**Production-ready template for ML experimentation** — the canonical clone-and-rename scaffold for any new ML experiment / training pipeline. Standardizes the team's experiment workflow on:

- **VS Code Dev Containers** — every team member runs the experiment in the same containerized env (reproducibility).
- **DVC (Data Version Control)** — tracks data, models, and experiments alongside git, with backing store on shared **GCS** (`gs://ship-cars-ml-experiments/ml-experiments-template`).
- **Reproducible pipelines** — anyone on the team can run an experiment end-to-end from a clean clone.
- **Local editing + containerized execution** — edit locally, run inside the dev container.

This is the **ML side** of the fleet's "template repos" — same posture as `quarkus-imperative-boilerplate` and `quarkus-k8s-boilerplate` for Quarkus services. Sister repo to `ml-experiments` (which holds actual past experiments rather than the template).

## How it fits

- **Not a runtime service.** Template only.
- **DVC remote:** `gs://ship-cars-ml-experiments/ml-experiments-template` (per the README) — shared across team members.
- **Influence:** new ML experiments / training pipelines should clone this rather than `ml-experiments` directly.

## Build / test / run
```
# Open in VS Code Dev Container (the recommended workflow).
# Inside the container:
dvc init
dvc pull           # fetch tracked data/models from GCS
python main.py     # run the pipeline
dvc add data/      # version a new dataset
dvc push           # publish to GCS
```

## Key abstractions

- `main.py` — pipeline entry.
- `src/` — experiment source.
- `data/` — DVC-tracked datasets (the actual files live in GCS via DVC).
- `models/` — DVC-tracked model artifacts.
- `experiments/` — per-experiment scripts / configs.
- `metrics/` — metric outputs (loss curves, validation scores).
- `scripts/` — helper scripts.
- `pyproject.toml` — Python deps.
- `.devcontainer/` (implied) — VS Code dev-container config.

## Don't-do-here / gotchas

- **DVC GCS remote is shared.** A `dvc push` from one experiment-clone can overwrite another team member's data version unless paths are namespaced per-experiment. Coordinate cloning conventions.
- **Dev Container is the supported workflow.** Local Python venv works but isn't tested; consistency depends on the container.
- **Template-only.** Don't deploy this repo. Clone, rename, fill in.
- **Recent commit `Add safety checks for dvc` (2026-02-12)** suggests the team has been hitting DVC operational footguns. Read the latest README before running.
- **Pairs with `ml-experiments`** for browsing past results; this repo is just the skeleton.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/ml-experiments.md` — sister repo containing actual experiment results.
- `~/projects/codebase-map/repos/ml-lib-extraction.md` — example of a "graduated" ML library that may have started here.
- `~/projects/codebase-map/repos/quarkus-imperative-boilerplate.md` — Quarkus-side template counterpart.
- `~/projects/codebase-map/domains/analytics.md`.
