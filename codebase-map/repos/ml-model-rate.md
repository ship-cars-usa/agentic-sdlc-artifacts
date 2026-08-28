---
repo: ml-model-rate
path: ~/projects/ship-cars-usa/ml-model-rate
stack: Python 3.6-3.9 / FastAPI / LightGBM 3.2.1
domain: pricing-billing
shape: single-module
last-synced-commit: d85d7d531c3ee4852ba87c6d7bac1ac8fd638582
last-synced-date: 2026-05-12
maintainer: unknown
status: seed
---

# ml-model-rate

## What it is
Python / FastAPI **stateless inference service** that predicts shipping rates using a pre-trained **LightGBM 3.2.1** regressor + a lightweight correction model. **One of the model services called by `ml-service-dispatcher`** via REST (`/predict`). Loads its model artifacts from a GCS bucket at startup and serves predictions in-memory — there is no database. Sister services likely exist for time-to-dispatch, confidence-absolute, confidence-percentage, and rate-multivehicle (per `ml-service-dispatcher`'s seed).

## How it fits
- Consumes API of: Google Cloud Storage (`production-rate-engine-model` bucket) at startup for `latest_production_model.json` + pickle artifacts.
- Publishes events to: none.
- Subscribes to: none.
- Owns data store: **none**. Models loaded in-memory at startup via `PredictorWorker`.

## Build / test / run
```
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn code.api:app --host 0.0.0.0 --port 8000
pytest
# REST: POST /api/ml/model/rate/predict, POST /predict-freezed
# Health: /monitoring/{liveness,readiness}-check (liveness runs a stub prediction)
```

## Key abstractions
- `PredictorWorker` — `code/ml/predictor.py` — wraps LightGBM + correction model; implements `__await__` for async init at startup.
- `Predictor` — `code/ml/predictor.py:Predictor` — loads pickle artifacts; `predict(features)` for inference.
- `PredictionRequest` / `PredictionResponse` — `code/models.py` — Pydantic schemas defining the dispatcher contract.
- `TrackingMiddleware` + `MetricNamerDefault` — `code/middlewares/tracking/` — Datadog instrumentation.

## Don't-do-here / gotchas
- **Model versioning via hardcoded pickle filenames** — `prod_fapi_model_light_gbm_regressor_v4_2025-02-15_2025-08-15_1755147698.pkl`, `correction_model_2025_02_06.pkl`. GCS config points to `latest_production_model.json` but the Python code's filenames are baked in. **A/B testing or rollback requires a code change + redeploy.** Add a `model_version` field to responses; load filenames from config.
- **Hardcoded user-email feature mapping** — a list of ~5 emails (`admin@mdg.bg`, `test+carrier@ship.cars`, ...) is mapped to `feature_value=1`; everyone else gets `0`. This is feature-engineering-as-code; new emails or feature splits require code redeploy. Move to a config or a feature store.
- **LightGBM 3.2.1 is from 2021**. Pinned for reproducibility, but several bug-fix releases exist; verify nothing material is missing.
- **`numpy` version skew between `pyproject.toml` (1.26.2) and `requirements.txt` (1.19.1)**. The build that ships is whichever the Dockerfile uses; verify.
- **Python 3.6 support listed** — 3.6 is EOL since Dec 2021. Confirm the runtime is at least 3.9+.
- **`POST /predict` accepts an unbounded list** of `PredictionRequest` — no max-items check. Potential resource-exhaustion vector if exposed broadly.
- **Liveness probe runs a stub prediction** — operationally OK, but a slow inference path will fail the liveness check before the readiness path notices. Verify the probe's tolerance.
- **No outbound HTTP except GCS-at-startup** — request-path is in-memory only; clean separation of concerns.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/ml-service-dispatcher.md` — primary inbound caller via the `RateClient` HTTP client.
- `~/projects/codebase-map/repos/rateengine.md` — the Django service that wraps ML predictions with business-rule adjustments.
- `~/projects/codebase-map/adr/0005-rateengine-eol-rewrite.md` — the rewrite proposal that affects how this service is called.
- `~/projects/codebase-map/domains/pricing-billing.md`.
