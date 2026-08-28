---
repo: ml-model-rate-confidence-percentage
path: ~/projects/ship-cars-usa/ml-model-rate-confidence-percentage
stack: Python / FastAPI / CatBoost / pydantic 1.x / Datadog (`ddtrace`)
domain: pricing-billing
shape: single-module
last-synced-commit: 5deda36af80266c7c4f9b39c5f9f030e7baca61c
last-synced-date: 2026-05-12
maintainer: unknown
status: seed
---

# ml-model-rate-confidence-percentage

## What it is
**Confidence-percentage** sibling of `ml-model-rate-confidence-absolute` — returns a percentage-encoded confidence score for a previously-predicted price. Same FastAPI / CatBoost template, same GCS-model-loading recipe, **same request shape** as the absolute variant (per the side-by-side `sample-request.txt` files).

Launch date 2022-11-28 (per README). The two confidence models presumably serve different downstream needs — one returns a raw absolute confidence value, the other normalizes it into a 0-100% range. Caller (`ml-service-dispatcher`) decides which to invoke per the use case.

Last commit 2025-10-22 (`Fix datetime.utcnow warning` — minor cleanup; the Python `datetime.utcnow()` deprecation in 3.12+).

## How it fits

- **Called by:** `ml-service-dispatcher` (`/predict`).
- **Consumes (model artifacts):** **GCS bucket `production-rate-engine-model`** with `latest_production_model.json` config — same bucket as the rest of the `ml-model-*` family.
- **Publishes events to:** none.
- **Owns data store:** none.

## Build / test / run
```
pip install -r builder/files/requirements.txt
cd code
APP_ENVIRONMENT=development \
  RUNTIME_SERVER_PORT=8083 \
  python server.py
```
Defaults to port 8083 for local dev (per the `sample-request.txt`). **Note** — port collides with `ml-model-rate-confidence-absolute`'s default; in production each service runs in its own pod / port, but local-dev runs of both at once need port overrides.

## Key abstractions

Identical to `ml-model-rate-confidence-absolute` — see that shadow for the canonical `code/api.py` / `PredictorWorker` / Datadog middleware shape. The only structural differences are:
- `dd_trace` `service_name` = `ml-model-rate-confidence-percentage`.
- `MetricNamerDefault(prefix="ml.model.rate_confidence_percentage")`.
- `APP_ROOT_PATH` defaults to `/api/ml/model/rate-confidence-percentage`.
- A different model artifact in GCS (same bucket, different `latest_production_model.json`-pointed model name).
- `redeploy/` directory present (not in the absolute variant) — possibly a stale leftover from a manual redeploy iteration; verify before removing.

## Don't-do-here / gotchas

- **Same stale-stack story as `ml-model-rate-confidence-absolute`** — `catboost==1.0.0`, `pydantic==1.10.x`, Python 3.6/3.7/3.8 target in black config. Bump pricing-side ML models together to keep deploy parity.
- **`datetime.utcnow()` deprecation fix landed recently (2025-10-22).** If the other ml-model siblings haven't gotten the same fix, they'll emit deprecation warnings on Python 3.12+; consider a coordinated commit.
- **`/predict` request shape is identical to the absolute variant** — risk of dispatcher misrouting (sending a request meant for one to the other) is real. Verify the dispatcher's `RateConfidenceAbsoluteClient` vs `RateConfidencePercentageClient` selection logic when adding new caller paths.
- **`redeploy/` directory** — undocumented. Possibly a scripts-leftover. Don't assume it's a deployment surface without checking helm + CI.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/ml-model-rate-confidence-absolute.md` — sibling with the canonical template description.
- `~/projects/codebase-map/repos/ml-model-rate.md` — same template; rate prediction.
- `~/projects/codebase-map/repos/ml-service-dispatcher.md` — upstream caller.
- `~/projects/codebase-map/domains/pricing-billing.md`.
