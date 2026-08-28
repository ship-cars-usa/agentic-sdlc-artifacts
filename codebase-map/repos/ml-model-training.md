---
repo: ml-model-training
path: ~/projects/ship-cars-usa/ml-model-training
stack: Python / MySQL client (`libmysqlclient-dev`) / GCS / Jenkins (CI) / packaged as installable (`pip install -e .`)
domain: analytics
shape: scripts-and-packages (data fetch → transform → train → upload to GCS)
last-synced-commit: de44177e7d48db3770e872f70e1526bdbb32bd8d
last-synced-date: 2026-05-12
maintainer: unknown
status: seed
---

# ml-model-training

## What it is
The **model training pipeline** that produces the artifacts loaded at startup by the `ml-model-*` family (`ml-model-rate`, `ml-model-rate-confidence-absolute`, `ml-model-rate-confidence-percentage`, `ml-model-rate-multivehicle`). Per the README:

> Contains a set of scripts that download data, transform it, train a model and upload the model on Google Cloud Storage.

The entry point is `bin/run-all` — it sequences the data → transform → train → upload steps. Different model variants live in separate submodules:

- `confidencemodeltraining/` — trains the rate-confidence models.
- `correctionmodeltraining/` — trains a correction-factor model (likely feeds the `correction_factor` field in `ml-model-rate-confidence-absolute`'s request shape).

Driven by **Jenkins** in CI (per the `Jenkinsfile` at the root). The Jenkins job is the canonical "retrain a model" trigger; results land in `production-rate-engine-model` GCS bucket where the inference services load them at startup.

## How it fits

- **Consumes:**
  - **`rateengine`'s MySQL database** (per the `libmysqlclient-dev` apt-get install instruction + the `RATE_ENGINE_PASSWORD` env var) — direct read of the production data to assemble training datasets. **Adds to the cross-service direct-DB-read count.**
  - **Google Cloud credentials** via `GOOGLE_APPLICATION_CREDENTIALS` — for GCS access.
- **Writes to:**
  - **GCS bucket `production-rate-engine-model`** — model artifacts that the `ml-model-*` services load at startup.
- **Publishes events to:** none.
- **Owns data store:** the GCS model-artifact bucket (jointly owned with the inference services that read it).

## Build / test / run
```
sudo apt-get install libmysqlclient-dev
pip install -r requirements.txt
pip install -e .

RATE_ENGINE_PASSWORD=...
GOOGLE_APPLICATION_CREDENTIALS=...
bin/run-all
```

CI: `Jenkinsfile` orchestrates retraining + upload.

## Key abstractions

- `bin/run-all` — top-level orchestration script.
- `confidencemodeltraining/` — module for the confidence models.
- `correctionmodeltraining/` — module for the correction-factor model.
- `config.json` — training config (hyperparameters, data ranges, model targets).
- `builder/` — build / dependency setup.
- `deploy/` — deploy helpers (presumably for the Jenkins-side model push).
- `Dockerfile` + `Dockerfile-test` — runtime + test images.
- `Jenkinsfile` — CI pipeline definition.

## Don't-do-here / gotchas

- **Reads `rateengine`'s MySQL DB directly using `RATE_ENGINE_PASSWORD`.** Same shadow-caller pattern as `ml-pricing-app` (MONTWAY + RATE_ENGINE PG reads) — adds to the **15-edge cross-service direct-DB-read** count from `relations/data-stores.md`. Needs an ADR-0003 contract draft. Will need to migrate when `rateengine` is rewritten per ADR-0005.
- **Models loaded by inference services at startup, not per-prediction.** Pushing a new model to GCS does **not** propagate until the consuming service is restarted. Coordinate with the inference services on when to roll pods after a model push.
- **Jenkins-driven retraining cadence is not visible from this repo.** Whether retraining is daily / weekly / on-demand is in the Jenkins config, not here. Worth confirming on incident-followups.
- **Multiple model variants in one repo** — confidence + correction + presumably rate-base. Adding a new model means another `*modeltraining/` submodule + Jenkins-side variant.
- **Stack is old enough to require `libmysqlclient-dev`** (the C extension; `pymysql` would be pure-Python). Confirm whether the prod CI image carries this dep.
- **`config.json` carries hyperparameters.** Changing them changes the model behavior; treat any commit touching `config.json` as a model-behavior change, not just config drift.
- **Last commit was a Claude-config-only sweep (2025-10-10).** Pipeline content is older; behavior should be stable but worth verifying it still runs cleanly on current data.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/ml-model-rate.md` / `ml-model-rate-confidence-absolute.md` / `ml-model-rate-confidence-percentage.md` / `ml-model-rate-multivehicle.md` — consume the artifacts this pipeline produces.
- `~/projects/codebase-map/repos/rateengine.md` — source of the MySQL data this pipeline reads.
- `~/projects/codebase-map/repos/ml-service-dispatcher.md` — synchronous gateway in front of the inference services.
- `~/projects/codebase-map/adr/0003-cross-service-db-read-policy.md` — applies to the `rateengine`-MySQL read.
- `~/projects/codebase-map/adr/0005-rateengine-eol-rewrite.md` — the rateengine migration this pipeline depends on.
- `~/projects/codebase-map/relations/data-stores.md` — cross-service direct-DB-read catalog.
- `~/projects/codebase-map/domains/analytics.md`.
