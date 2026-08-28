---
repo: ml-service-dispatcher
path: ~/projects/ship-cars-usa/ml-service-dispatcher
stack: Python 3.9+ / FastAPI + Uvicorn / Tortoise ORM / httpx
domain: analytics
shape: single-module
last-synced-commit: 274e1f712a7c49a39e9a3e63455e40a24dc6ba5a
last-synced-date: 2026-05-11
maintainer: unknown
status: seed
---

# ml-service-dispatcher

## What it is
Python / FastAPI **synchronous ML-prediction gateway**. Receives shipping-quote requests over REST, enriches them via DataOne (vehicle specs) + `location-provider`, dispatches to **multiple specialized ML model services** (rate, time-to-dispatch, two confidence scorers), and applies a chain of **business-logic modifiers** (surcharges, confidence adjustments, load adjustments, vehicle-price adjustments). Persists prediction inputs/outputs to PostgreSQL plus an Elasticsearch audit log. ~7.3k LOC; the largest of the ML trio. **Does not publish to Pub/Sub** — strictly request-response. `posting-backend`'s `ml-bot-order` consumption is therefore from a different source (not this service); worth confirming on the next pass.

## How it fits
- Consumes API of: `ml-model-rate` (`RateClient`), `RateMultivehicleClient`, `ConfidenceAbsoluteClient`, `ConfidencePercentageClient`, `TimeToDispatchClient` — all via `httpx` with `ML_SERVICE_TIMEOUT=20s`. `DATA_ONE_TIMEOUT_IN_SECONDS=30s` for vehicle-spec enrichment. **`httpx` limits: `max_connections=100`, `max_keepalive_connections=20`** — explicit pool sizing.
- Publishes events to: none (REST-response only).
- Subscribes to: none.
- Owns data store: PostgreSQL via Tortoise (`minsize=5, maxsize=5, max_queries=50k`). Tables: `client_response`, `fetched_vehicle` (DataOne cache), `calculated_route`, `location_details`, `model_prediction`, `rate_prediction_result`, `confidence_prediction_result`, `modificator_result`. Plus **Elasticsearch** for audit logs (`AUDIT_LOGGER_URL` / `_USER` / `_PASSWORD`). 30+ Aerich migrations.

## Build / test / run
```
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
pytest
# Routes: /predict/rate, /predict/time-to-dispatch, /vehicles/{years,makes,models}, /monitoring/*
```

## Key abstractions
- `services/ml/rate/service.py` + `client.py` — rate-prediction orchestrator + HTTP client to `ml-model-rate`.
- `services/ml/rate/confidence/{absolute,percentage}/` — dual confidence scorers (the RefactoringPlan flags ~800 LoC of dup here).
- `services/ml/modificators/` — `Surcharge`, `Confidence`, `Load`, `VehiclePrice` modifiers in a chain-of-responsibility.
- `services/dataone.py` — vehicle-spec enrichment; in-DB cache + CSV fallback for 40k+ vehicles.
- `services/audit_logger.py` — Elasticsearch event sink.
- `middlewares/tracking/` — Datadog APM via `ddtrace.auto`.

## Don't-do-here / gotchas
- **Test coverage <5%** (self-reported in `RefactoringPlan.md`). Critical: this is the entry point for pricing-related ML predictions.
- **`ML_SERVICE_TIMEOUT=20s` is a single shared knob** across 5 downstream models. If one model is slow, every prediction waits 20 s. Add per-client tunables; consider per-model SLOs.
- **No circuit breaker on DataOne or any model client** — `httpx` retries synchronously within the timeout. Under degraded downstream, the connection pool saturates; the explicit `max_connections=100` is the actual blast-radius limit.
- **Datadog auto-instrumentation** — `ddtrace.auto` is imported at module level. Agent outage silently drops spans (non-blocking, but observability disappears).
- **`fetched_vehicle` DB-cache + CSV fallback** — confirm the cache TTL and refresh policy; stale specs propagate into pricing.
- **No reconciliation between PG `model_prediction` and ES audit** — if one of the writes fails mid-request, observability and DB diverge.
- **Tortoise pool `maxsize=5`** — very tight for a prediction-gateway under burst; right-size after seeing pool-wait.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/rateengine.md` — the actual pricing engine; this dispatcher and rateengine likely overlap in scope. Worth a boundary-clarification note.
- `~/projects/codebase-map/repos/ml-service-recommender.md` — sibling.
- `~/projects/codebase-map/repos/ml-service-listener.md` — sibling.
- `~/projects/codebase-map/repos/location-provider.md`.
- `~/projects/codebase-map/domains/analytics.md`.
