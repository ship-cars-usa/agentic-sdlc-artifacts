---
repo: ml-notebooks-archive
path: ~/projects/ship-cars-usa/ml-notebooks-archive
stack: Jupyter notebooks (`.ipynb`)
domain: analytics
shape: flat dump of `[RE-NNN] *.ipynb` files
last-synced-commit: 39f8c840f1324431e79703a5478756813d1fee64
last-synced-date: 2026-05-12
maintainer: unknown
status: seed
---

# ml-notebooks-archive

## What it is
A **flat archive of historical Jupyter notebooks** — research artifacts tagged by Jira ticket (`[RE-647] Automated Posting.ipynb`, `[RE-741] Document Parser Testing.ipynb`, `[RE-752] Bot Order Testing.ipynb`, `[RE-815] Parse Gatepasses.ipynb`, `[RE-834] PPM Prediction.ipynb`, `[RE-834] Predictions.ipynb`, `[RE-834] Rejection Prediction.ipynb`, `[RE-834] Volume Prediction.ipynb`). The `[RE-NNN]` prefix maps each notebook to its originating Jira ticket.

The notebooks document the research underlying several productionized fleet ML services:
- `RE-647 Automated Posting` → fed into `ml-bot-order-v2`.
- `RE-741 Document Parser Testing` → fed into `ml-document-parser`.
- `RE-752 Bot Order Testing` → also `ml-bot-order` lineage.
- `RE-834 Predictions / PPM / Rejection / Volume` → likely fed into `ml-demand-forecasting` (which seeded in Phase 4.11).

Last commit 2026-01-30 (`Add files via upload`) — these are upload-from-elsewhere notebooks, not editable in-place work.

## How it fits

- **Read-only artifact repo.** Not a service.
- **Predates** the canonical experiment-template flow (`ml-experiments-template` + DVC + GCS). New experiments should go through that template, not here.

## Build / test / run
```
# Open in Jupyter / VS Code with the Python kernel.
# Each notebook is self-contained; dependencies must be installed by hand.
```

## Don't-do-here / gotchas

- **Don't add new notebooks here.** Use `ml-experiments-template` for new work.
- **Notebooks reference deprecated data sources.** Re-running an `[RE-834]` notebook against current `rateengine` data will produce different results — schemas have evolved.
- **No environment management** — each notebook may need its own `pip install` set; not versioned.
- **Archive-candidate** if the productionized descendants (`ml-bot-order-v2`, `ml-document-parser`, `ml-demand-forecasting`) carry enough institutional memory.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/ml-experiments.md` — sister "research notebooks" repo.
- `~/projects/codebase-map/repos/ml-experiments-template.md` — the canonical template for new ML experiments.
- `~/projects/codebase-map/repos/ml-bot-order-v2.md` — productionized descendant (RE-647).
- `~/projects/codebase-map/repos/ml-document-parser.md` — productionized descendant (RE-741).
- `~/projects/codebase-map/repos/ml-demand-forecasting.md` — productionized descendant (RE-834 family).
- `~/projects/codebase-map/relations/infrastructure-triage.md` — flag for archive on next refresh.
- `~/projects/codebase-map/domains/analytics.md`.
