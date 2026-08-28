---
repo: ml-model-rate-confidence-absolute
path: ~/projects/ship-cars-usa/ml-model-rate-confidence-absolute
stack: Python / FastAPI 0.115 / CatBoost 1.0.0 / pydantic 1.10 / uvicorn / Datadog (`ddtrace`)
domain: pricing-billing
shape: single-module
last-synced-commit: 529547fe643202c4f38e017172e9fb355345dfe3
last-synced-date: 2026-05-12
maintainer: unknown
status: seed
---

# ml-model-rate-confidence-absolute

## What it is
**Confidence-absolute** ML inference service — one of the four sibling `ml-model-*` services that sit beneath `ml-service-dispatcher` and produce per-load model predictions for the pricing flow. Given a load's pickup/delivery + vehicle + a previously predicted price (from `ml-model-rate` or `rateengine`), this service returns an **absolute-value confidence score** indicating how trustworthy the predicted price is.

Launch date 2022-10-14 (per README). Templated identically to `ml-model-rate` (seeded Phase 4.12) and the two sibling confidence/multivehicle models:

- `code/api.py` — FastAPI app with `/predict`, `/predict-freezed` (date-frozen variant for testing), `/monitoring/liveness-check`, `/monitoring/readiness-check`.
- `code/ml/predictor.py` (PredictorWorker class) — loads the latest CatBoost model from GCS (`production-rate-engine-model` bucket, `latest_production_model.json` config), transforms request features, calls `.predict()`.
- `code/models.py` — pydantic v1 request/response models.
- `code/middlewares/tracking/` — Datadog metrics middleware (per-route counters/timings).
- `code/server.py` — uvicorn entry.
- `code/settings.py` — env-driven config; `APP_ROOT_PATH=/api/ml/model/rate-confidence-absolute`.

Same anti-staleness recipe as `ml-model-rate`: model artifacts are loaded from GCS at startup; **redeploying does NOT pick up a new model** — the model registry is updated separately, and pods need to be rolled to load the new artifact.

## How it fits

- **Called by:** `ml-service-dispatcher` (the synchronous ML-prediction gateway seeded in Phase 4.10). The dispatcher's `httpx` clients call this service's `/predict` endpoint with a `PredictionRequest`.
- **Consumes API of:** none — pure inference service.
- **Consumes (model artifacts):** **GCS bucket `production-rate-engine-model`** (same bucket as `ml-model-rate` and the confidence/multivehicle siblings). Model registry config in `latest_production_model.json`.
- **Publishes events to:** none.
- **Owns data store:** none — in-memory model + Datadog metrics.

## Build / test / run
```
pip install -r builder/files/requirements.txt
cd code
APP_ENVIRONMENT=development \
  RUNTIME_SERVER_PORT=8083 \
  RUNTIME_SERVER_LOG_LEVEL=info \
  python server.py
```
Sample request available at `sample-request.txt`. Defaults to port 8083 for local dev.

## Key abstractions

- `code/api.py:app` — FastAPI app; ORJSON response class.
- `code/api.py:predict()` + `predict_freezed()` — main inference endpoints.
- `code/api.py:liveness_check()` — runs a `stub_data.request` through `process_request` to verify the model loads + predicts. Failure = 503.
- `code/ml/predictor.py:PredictorWorker` — loads CatBoost model from GCS, runs feature transformation, predicts.
- `code/middlewares/tracking/` — Datadog `TrackingMiddleware` with `MetricNamerDefault(prefix="ml.model.rate_confidence_absolute")`.
- `code/stub_data.py` — canned request used by liveness check.

## Request shape (per sample-request.txt)
```json
{
  "request_id": "uuid",
  "pickup": {"lat": 37.776956, "lng": -122.215918},
  "delivery": {"lat": 34.103131, "lng": -118.416253},
  "vehicle": {"weight": 3032.0, "length": 172.9, "height": 50.1},
  "distance": 397.21,
  "is_enclosed": false,
  "is_running": true,
  "is_classic": false,
  "first_available_date": "2022-09-23T00:00:00Z",
  "predicted_price": 384.75,
  "correction_factor": 0.99
}
```
Same shape as `ml-model-rate-confidence-percentage` — the two services accept identical requests and differ only in the model artifact + how the output is interpreted.

## Don't-do-here / gotchas

- **Stale stack.** Pinned to `catboost==1.0.0` (Sep 2021 — current is 1.2+), `fastapi==0.115.12` (current 0.115), `pydantic==1.10.16` (v1 — deprecated; v2 is current), `numpy==1.26.2`. The black target-version line still lists `py36, py37, py38` even though the service runs on a newer Python (per the parent ml-model-rate seed; Python version varies by Dockerfile).
- **`pydantic==1.10`** is on the deprecated v1 line. Migrating to v2 is non-trivial because feature transformation likely uses `.dict()` / `.json()` patterns that changed in v2.
- **Model loaded at startup, not per-request.** Pod restart is required after a model registry update. **Verify the deployment recipe rolls pods after a model push.**
- **Datadog `ddtrace.auto` patches the global tracer at import time** — be careful that the import order in `api.py` (`import ddtrace.auto  # noqa: F401` is the first line) is preserved; refactoring imports can break tracing silently.
- **`hardcoded GCS bucket `production-rate-engine-model`** in `settings.py` with prefix `prod` vs `<env>`. Make sure non-prod environments have the right subfolder populated; a non-prod pod will silently fail to load a model if the prefix doesn't resolve.
- **No retry / backoff on model-load failure at startup.** If GCS is slow or temporarily unreachable when the pod boots, the pod fails liveness and gets restarted by Kubernetes — eventually catching up, but adding to deploy duration during regional GCS issues.
- **No `/predict` rate limiting.** Caller (`ml-service-dispatcher`) controls concurrency via its `max_connections=100` setting. A misconfigured caller can saturate this service.
- **`is_classic`, `is_running`, `correction_factor` are feature inputs** that must align with the trained model's expected feature set. Adding a model with different features requires a coordinated request-shape change + dispatcher update.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/ml-model-rate.md` — sibling service (rate prediction); same template + same GCS bucket.
- `~/projects/codebase-map/repos/ml-model-rate-confidence-percentage.md` — sibling confidence model; identical request shape, different output interpretation.
- `~/projects/codebase-map/repos/ml-model-rate-multivehicle.md` — sibling rate model for multi-vehicle loads; different request shape.
- `~/projects/codebase-map/repos/ml-service-dispatcher.md` — upstream caller; coordinates which model to call for which prediction.
- `~/projects/codebase-map/repos/rateengine.md` — produces the `predicted_price` input to this model.
- `~/projects/codebase-map/domains/pricing-billing.md`.
