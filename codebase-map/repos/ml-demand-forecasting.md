---
repo: ml-demand-forecasting
path: ~/projects/ship-cars-usa/ml-demand-forecasting
stack: Python 3.8+ / PyTorch 2.6 + CUDA 12.4 / TempoPFN (38M-param transformer)
domain: analytics
shape: single-module
last-synced-commit: a151c30f35f351da679e4743ecb2244d15a1079a
last-synced-date: 2026-05-12
maintainer: unknown
status: seed
---

# ml-demand-forecasting

## What it is
Python **batch ML pipeline** (not a service) for **quarterly demand forecasting**. Loads historical transportation metrics from a source production PG (rate-per-mile / PPM, loads-per-carrier / LPC, rejection-rate / RR), runs GPU-accelerated **TempoPFN** (38M-parameter transformer) inference, and writes 4-quarter-ahead predictions to a sink PG. Triggered on a schedule (cron / Argo); no REST surface, no Pub/Sub. The trained-model checkpoint lives in GCS; first run downloads it locally and caches.

## How it fits
- Consumes API of: source PG (read-only): `SOURCE_DB_{IP,USER,PASSWORD,NAME}`; GCS (model checkpoint).
- Publishes events to: none.
- Subscribes to: none.
- Owns data store: writes to sink PG tables `ppm_fc`, `lpc_fc`, `rr_fc` (prediction results; indexed by `(prediction_rundate, prediction_year, prediction_quarter)`); reads from **another service's PG** as the source (a shadow-caller pattern — see Don't-do-here). Model checkpoint in GCS bucket `shipcars-platform-dev-demand-forecasting`.

## Build / test / run
```
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python bin/run.py -c code/config.json    # scheduled batch entry point
pytest
```

## Key abstractions
- `Executor` — `code/executor.py` — orchestrates load → predict → store for PPM, LPC, RR.
- `load_model()` — `code/model.py` — fetches TempoPFN checkpoint from GCS into `code/tempopfn/models/` (cache).
- `price.load_data()` / `volume.load_data()` / `rejection.load_data()` — `code/data/*.py` — fetch historical data from source PG, filter, aggregate to quarterly.
- `predict()` — `code/model.py` — GPU inference.
- Connection helpers — `code/utils.py` — SQLAlchemy connection strings from env-var dicts.

## Don't-do-here / gotchas
- **Reads directly from a source production PG** — same shadow-caller pattern as `integrators-data-bridge` and `syncer`. Whichever upstream service owns `SOURCE_DB_*`, this pipeline has an undocumented contract on its schema. Add to `adr/0003-cross-service-db-read-policy.md` as a sanctioned edge.
- **No error recovery** — GCS download failure mid-run requires manual intervention. Add a checked retry + alert.
- **Hardcoded prediction-row index columns** (`["prediction_rundate", "prediction_year", "prediction_quarter"]`) — schema changes to the sink table break dedup masking. Pull the column list from config or model metadata.
- **GPU is assumed** — `torch.cuda.is_available()` is checked at startup; no CPU fallback. If the scheduled run lands on a non-GPU pod (config drift), the run dies.
- **Unbounded pandas memory** — entire historical dataset loaded into one DataFrame per metric. Long date ranges = OOM risk.
- **No DB-side uniqueness on sink** — dedup relies on in-process index masking; a second run in the same quarter appends duplicates if the masking misses. Add a unique constraint on `(prediction_rundate, prediction_year, prediction_quarter, metric_key)`.
- **Implicit env credentials** — `SOURCE_DB_PASSWORD` etc. assumed set; no startup assertion.
- **No model-version stamp** on prediction rows — operators can't tell which checkpoint produced which row. Persist `model_sha256` or `model_version` next to each row.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/bi-databricks-backend.md` — analytics-domain peer (different stack).
- `~/projects/codebase-map/repos/ai-dashboard-backend.md` — possible downstream consumer of the forecast tables.
- `~/projects/codebase-map/adr/0003-cross-service-db-read-policy.md` — relevant for the source-DB read pattern.
- `~/projects/codebase-map/domains/analytics.md`.
