---
repo: ml-experiments
path: ~/projects/ship-cars-usa/ml-experiments
stack: Mixed — Jupyter notebooks + Python research code (per-folder)
domain: analytics
shape: top-level catalog (`automated-posting-research/`, `ml-research-template/`, `recommender-research/`)
last-synced-commit: ab0895c5c68cec602afd800cd6889cecbf4d5830
last-synced-date: 2026-05-12
maintainer: unknown
status: stale
---

# ml-experiments

## What it is
**A repository of notebooks and results from ML experiments and simulations** (per the one-line README). Each top-level subdirectory is a separate experiment with its own scope:

- **`automated-posting-research/`** — research underlying the `ml-bot-order` / `ml-bot-order-v2` automated-load-creation flow (which is now a real fleet service in `integrations`).
- **`recommender-research/`** — research underlying the recommendation pipeline (`load-recommender`, `ml-service-recommender`).
- **`ml-research-template/`** — a starter scaffold for new experiments (smaller than the standalone `ml-experiments-template` repo).

This is a **historical artifact repo**, not a deployed service. New experiments should use the standalone `ml-experiments-template` repo (DVC + GCS + dev containers) rather than adding new folders here.

Last commit 2025-10-10 — touched only by the Claude Code config sweep. Actual experiment content is older.

## How it fits

- **Not a runtime service.** Browsing-only / reproducibility-only.
- **Predates** at least two productionized fleet services: `ml-bot-order-v2` (from `automated-posting-research/`) and `load-recommender` + `ml-service-recommender` (from `recommender-research/`).

## Build / test / run
```
# Open notebooks in Jupyter Lab.
# Each subdirectory likely has its own README and dependency setup.
```

## Key abstractions

- `automated-posting-research/` — notebooks + scripts for the bot-order extraction flow.
- `recommender-research/` — notebooks + scripts for the recommender model.
- `ml-research-template/` — minimal scaffold (likely superseded by `ml-experiments-template` standalone repo).

## Don't-do-here / gotchas

- **Don't add new experiments here.** Use the `ml-experiments-template` repo for new work (DVC + GCS-backed, dev-container'd, reproducible). This repo is historical.
- **Notebooks may reference deprecated data sources / model artifacts.** Re-running an old notebook from this repo on current data can produce different results without warning.
- **No CI; no testing.** Treat any code here as exploratory unless someone explicitly says otherwise.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/ml-experiments-template.md` — the canonical template for new experiments.
- `~/projects/codebase-map/repos/ml-bot-order-v2.md` — productionized descendant of `automated-posting-research/`.
- `~/projects/codebase-map/repos/load-recommender.md` / `ml-service-recommender.md` — productionized descendants of `recommender-research/`.
- `~/projects/codebase-map/repos/ml-notebooks-archive.md` — sibling notebooks archive (presumably older).
- `~/projects/codebase-map/domains/analytics.md`.
