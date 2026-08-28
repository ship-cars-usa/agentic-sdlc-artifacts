---
repo: ml-service-listener
path: ~/projects/ship-cars-usa/ml-service-listener
stack: Python 3.9+ / FastAPI + Uvicorn / Tortoise ORM
domain: analytics
shape: single-module
last-synced-commit: 121bc6d7fecff3eae78e96a6286c338ffd37728c
last-synced-date: 2026-05-11
maintainer: unknown
status: seed
---

# ml-service-listener

## What it is
Python / FastAPI service that **subscribes to two Pub/Sub topics for behavioral signals** and persists them to PostgreSQL for downstream model training and analytics. Consumes `cube.search-posting-events` (marketplace search/posting events) and `load-recommender.feedback-events` (user feedback on recommendations). Sister-service to `ml-service-dispatcher` (synchronous predictions) and `ml-service-recommender` (recommendation publishing). The pattern: behavior collection → DB → offline training → updated models. Pure event sink — no outbound Pub/Sub, no synchronous REST API beyond health checks.

## How it fits
- Consumes API of: `location-provider` (via `httpx` async client) for zip-code enrichment of search events. `ML_SERVICE_TIMEOUT` default 1.0 s; **no explicit connect/read timeout split**.
- Publishes events to: none (listener-only).
- Subscribes to: Pub/Sub `cube.search-posting-events` (`PUBSUBS_SEARCH_POSTING_EVENTS_SOURCE_SUBSCRIPTION_ID`); Pub/Sub `load-recommender.feedback-events` (`PUBSUBS_RECOMMENDATION_FEEDBACK_EVENTS_SOURCE_SUBSCRIPTION_ID`).
- Owns data store: PostgreSQL via **Tortoise ORM** (`minsize=10, maxsize=10, max_queries=50k, max_inactive_connection_lifetime=120s`).

## Build / test / run
```
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
pytest
# Liveness: /monitoring/liveness-check ; Readiness: /monitoring/readiness-check
```

## Key abstractions
- `services/pubsub/subscribers/SearchSubscriber` — parses + persists `cube.search-posting-events`.
- `services/pubsub/subscribers/FeedbackSubscriber` — parses + persists `load-recommender.feedback-events`. Both share a base parser with a re-publish hook.
- `services/location_provider.py` — async `httpx` client for zip-code enrichment.
- `services/audit_logger.py` — event-persistence layer.
- `models_persisted.py` — Tortoise models for the event tables.

## Don't-do-here / gotchas
- **`PUBSUBS_PROJECT_ID` defaults to `"SHOULD-BE-CHANGED"`** — startup will silently succeed but every Pub/Sub operation fails. Add a startup readiness assertion that the value isn't the sentinel.
- **No timeout on `location-provider` requests** — only the global 1.0 s `ML_SERVICE_TIMEOUT`. A slow `location-provider` blocks the event-processing path.
- **Silent ACK risk** — message is acked *after* `process_message()` returns. Whether unhandled exceptions cause an implicit nack is dependent on the Pub/Sub client's defaults plus the base parser's `try/except`. Confirm and document; ideally route to a DLQ.
- **Tortoise ORM `minsize=maxsize=10`** — fixed pool size; under burst, requests queue without backpressure. Right-size after observing wait metrics.
- **No outbound publish** — but `audit_logger.py`'s name suggests it could grow into one. If audit-stream needs to become reliable, add an outbox pattern.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/ml-service-recommender.md` — consumes the feedback events this service writes.
- `~/projects/codebase-map/repos/ml-service-dispatcher.md` — sibling.
- `~/projects/codebase-map/repos/load-recommender.md` — the upstream that emits `load-recommender.feedback-events`.
- `~/projects/codebase-map/repos/location-provider.md`.
- `~/projects/codebase-map/domains/analytics.md`.
