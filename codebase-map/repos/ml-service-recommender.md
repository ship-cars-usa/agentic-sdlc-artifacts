---
repo: ml-service-recommender
path: ~/projects/ship-cars-usa/ml-service-recommender
stack: Python 3.9+ / FastAPI + Uvicorn / Tortoise ORM
domain: listings-trade
shape: single-module
last-synced-commit: c5a969aef0ccb2a720ef96087a139800730963e7
last-synced-date: 2026-05-11
maintainer: unknown
status: stale
---

# ml-service-recommender

## What it is
Python / FastAPI **recommendation engine** for carrier-facing load suggestions. Consumes `cars.ship.prod.carrierlb.events-ml-recommender` (carrier behavior + load events), applies similarity-based + A/B-tested algorithms over two PostgreSQL stores (current preferences + historical recommendations), and **publishes formatted recommendations to `cars.ship.prod.ml.recommender`** — the topic consumed by `load-recommender`'s `ml-recommender-subscription`. Confirms the recommendation chain: **`ml-service-recommender` (this) → `load-recommender` → `notification-orchestrator` → user inbox/email**. Domain stays `listings-trade` because it serves load-matching, not generic analytics.

## How it fits
- Consumes API of: minimal direct HTTP — primarily its own subscribed topic. Test suite uses `requests` for integration.
- Publishes events to: Pub/Sub topic `cars.ship.prod.ml.recommender` (`PUBSUBS_LOADS_DESTINATION_TOPIC_ID`) — consumed by `load-recommender`.
- Subscribes to: Pub/Sub subscription `cars.ship.prod.carrierlb.events-ml-recommender` (`PUBSUBS_LOADS_SOURCE_SUBSCRIPTION_ID`).
- Owns data store: **two PostgreSQL databases** via Tortoise ORM —
  - `mlrecommender` primary (`minsize=10, maxsize=10`) — stats, predictions, A/B tracking, preferences.
  - `recommender` secondary via `db-recommendations` connection (`minsize=5, maxsize=5`) — historical recommendations + analytics.

## Build / test / run
```
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
pytest
# Routers: /api/ml/service/recommender/, /monitoring/{readiness,liveness}-check
```

## Key abstractions
- `services/ml/recommender/api.py` — main recommendation router + service.
- `services/ml/recommender/algorithms/` — `simple` and `similarity-based` implementations.
- `services/pubsub/` — subscriber + publisher (same pattern as `ml-service-listener`).
- `models_persisted.py` — Tortoise models for stats, A/B test tracking, preferences.
- `migrations/ml-recommender/` — 19+ migrations.

## Don't-do-here / gotchas
- **Hardcoded GCP project ID** `atlantean-field-175514` as the default for `PUBSUBS_LOADS_PROJECT_ID`. Non-prod environments depend on the env-var override; if it's missing, this publishes to prod's project. Fail-fast if the value is missing in non-prod.
- **Dual-database complexity** — two PG instances with separate credentials and migrations. Schema drift between them is plausible; document which fields live where.
- **No model-version field** on `model_prediction` table — migration 18 renamed a similarity column but didn't introduce a version stamp. Tracking which algorithm/version produced a recommendation requires migrating in a version column now.
- **Subscription/preference data is populated by the dispatcher** but has no foreign-key constraints to `posting-backend` or `user-backend`. Orphan rows accumulate.
- **Silent ACK pattern** — same as `ml-service-listener`. Exception inside `process_message()` may cause message loss without DLQ.
- **A/B-test buckets persisted in PG** — confirm whether bucket assignment is sticky across restarts (it should be).
- **Domain assignment is `listings-trade` not `analytics`** — load-recommendation is a marketplace function; analytics-domain peers are training/data-pipeline services. If a future split lands, this and `load-recommender` might move into a new `recommendations` domain.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/load-recommender.md` — primary consumer of the output topic.
- `~/projects/codebase-map/repos/ml-service-listener.md` — feeds upstream data via `load-recommender.feedback-events`.
- `~/projects/codebase-map/repos/ml-service-dispatcher.md` — sibling.
- `~/projects/codebase-map/domains/listings-trade.md`.
