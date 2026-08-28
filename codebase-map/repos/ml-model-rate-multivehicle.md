---
repo: ml-model-rate-multivehicle
path: ~/projects/ship-cars-usa/ml-model-rate-multivehicle
stack: Python / FastAPI / CatBoost / pydantic 1.x / Datadog (`ddtrace`)
domain: pricing-billing
shape: single-module
last-synced-commit: 6c30e6d6287e73716f09304166e913708cdbb10f
last-synced-date: 2026-05-12
maintainer: unknown
status: seed
---

# ml-model-rate-multivehicle

## What it is
**Multi-vehicle rate** ML inference service — sibling of `ml-model-rate` (single-vehicle) and the two confidence models. Predicts a carrier-pay rate for loads carrying **multiple vehicles**, where the request includes `vehicle_count`, `wholesize_y`, and a `carrier_pay_sum` baseline rather than the single-vehicle `weight/length/height` triple.

Launch date 2022-10-18 (per README). Same FastAPI / CatBoost / GCS-model-loading template as the rest of the `ml-model-*` family, but the **request shape differs**:

```json
{
  "request_id": "uuid",
  "distance": 397.21,
  "vehicle_count": 2,
  "pickup_lat": 37.776956,
  "pickup_lng": -122.215918,
  "delivery_lat": 34.103131,
  "delivery_lng": -118.416253,
  "first_available_date": "2022-09-24 10:56:24.045451+00:00",
  "wholesize_y": 4,
  "carrier_pay_sum": 745.30
}
```

Flat lat/lng + `vehicle_count` + `wholesize_y` (which appears to be a load-volume / trailer-utilization metric) + a baseline `carrier_pay_sum` to anchor the prediction.

## How it fits

- **Called by:** `ml-service-dispatcher` for multi-vehicle load paths.
- **Consumes (model artifacts):** **GCS bucket `production-rate-engine-model`** (same bucket as the family).
- **Publishes events to:** none.
- **Owns data store:** none.

Defaults to port 8084 (per `sample-request.txt`) — different from the confidence models on 8083 — but the file also mentions `localhost:8082`, suggesting dev-port confusion. **Verify the canonical local-dev port** before adding to docker-compose.

## Build / test / run
```
pip install -r builder/files/requirements.txt
cd code
APP_ENVIRONMENT=development RUNTIME_SERVER_PORT=8084 python server.py
```

## Key abstractions
Identical template to `ml-model-rate-confidence-absolute` — see that shadow for the canonical `code/api.py` / `PredictorWorker` shape. Differences:
- `dd_trace` `service_name` = `ml-model-rate-multivehicle`.
- Metric namer prefix = `ml.model.rate_multivehicle`.
- `code/models.py` request/response shapes match the multi-vehicle schema above.
- Feature transformation in `PredictorWorker.transform_request()` keys on `vehicle_count`, `wholesize_y`, `carrier_pay_sum`.

## Don't-do-here / gotchas

- **`wholesize_y` and `carrier_pay_sum` aren't self-documenting.** The training-data feature engineering picked these names; if a future feature wants to introduce a different multi-vehicle signal, expect the team's wiki or the model card to clarify. Coordinate with the data-science owner before renaming.
- **Request shape divergence from the other ml-model-* siblings** is a real footgun for the dispatcher. The single-vehicle / confidence models take `pickup.{lat,lng}` (nested); this service takes `pickup_lat` / `pickup_lng` (flat). Adding a uniform wrapper or aligning the schemas would prevent dispatcher-side mismatch bugs.
- **Same stale-stack story** as the rest of the ml-model-* family (`catboost==1.0.0`, `pydantic==1.10.x`, etc.).
- **Two ports referenced in `sample-request.txt`** (8082 and 8084) — almost certainly a copy-paste leftover. Confirm canonical port + remove the stale curl example.
- **`carrier_pay_sum` as a request feature** is a downstream of `rateengine` / `ml-model-rate`. So this service has an **implicit dependency on a prior prediction** before it can run. The dispatcher must invoke them in the correct order; a missing upstream prediction silently degrades the multi-vehicle prediction quality.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/ml-model-rate.md` — single-vehicle sibling.
- `~/projects/codebase-map/repos/ml-model-rate-confidence-absolute.md` — canonical template shadow.
- `~/projects/codebase-map/repos/ml-service-dispatcher.md` — upstream caller; coordinates the order of model calls.
- `~/projects/codebase-map/domains/pricing-billing.md`.
