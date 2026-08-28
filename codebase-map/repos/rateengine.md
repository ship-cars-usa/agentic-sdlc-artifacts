---
repo: rateengine
path: ~/projects/ship-cars-usa/rateengine
stack: Python/Django 2.1.7 + DRF 3.8.2 (both EOL)
domain: pricing-billing
shape: single-module
last-synced-commit: 43fabc987eed29ca4615bfcf0b5798840a3854f0
last-synced-date: 2026-05-11
maintainer: unknown
status: seed
---

# rateengine

## What it is
Python / **Django 2.1.7** / **DRF 3.8.2** service running on Gunicorn that **computes carrier-pay quotes** for auto-transport using pre-trained ML models (scikit-learn, LightGBM, CatBoost). Input: vehicle list + pickup/delivery ZIP + coordinates + enclosed flag + date. Output: `RatingResult` with base carrier pay, enclosed premium, vehicle-type adjustments, and variant prices. Versioned model branches (`analysisV3`, `analysisV4`) coexist. Heavy-traffic; called by `posting-backend` (`rateengine` REST client) and likely `quote-manager-backend` and `contract-pricing-backend`. **This is the actual pricing engine** — `quote-manager-backend` is a state façade in front of it, `contract-pricing-backend` handles per-customer contract pricing. The three together are the fleet's pricing stack.

## How it fits
- Consumes API of: external **central-dispatch** (`app/external/central_dispatch.py` via `requests.Session()`); possibly other carrier-facing systems. **Default `requests` timeout is infinite** — see Don't-do-here.
- Publishes events to: none observed (no Kafka/Pub/Sub integration; possibly Celery tasks for downstream propagation but not confirmed).
- Subscribes to: none observed.
- Owns data store: PostgreSQL (psycopg2-binary), Django ORM. Redis (django-redis) for caching + session. **Elasticsearch** (full-text indexing — possibly for quote audit trail; verify whether it's load-bearing). ML models loaded **in-memory at startup** (sklearn pickle + numpy-backed); blue/green is required for model updates.

## Build / test / run
```
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver  # dev
gunicorn config.wsgi -b 0.0.0.0:8000  # prod
pytest
```

## Key abstractions
- `Facade` — `app/rating/facade.py` — builds `PredictionRequest`s, invokes `MLFacade.predict()`, applies `Calculator` adjustments, returns `RatingResult`.
- `MLFacade` — `app/ml/...` — wraps scikit-learn / LightGBM / CatBoost models; routes by analysis version.
- `Calculator` — `app/rating/adjustment.py` — business-rule adjustments (multi-vehicle surcharge, special routing, enclosed premium).
- `QuoteViewSet` (+ sibling DRF ViewSets `StarRatingViewSet`, `UpsellViewSet`, `VehicleViewSet`, `MarketViewSet`) — `app/viewsets.py` — DRF surface with token auth.
- `CentralDispatchSession` — `app/external/central_dispatch.py` — external carrier-dispatch HTTP integration.

## Don't-do-here / gotchas (CRITICAL flags)
- **Django 2.1.7 and DRF 3.8.2 are both long-EOL** (Django 2.1 lost security support in April 2020). Six years of unpatched CVEs in the auth stack, request parser, ORM, and middleware. **This is the second-biggest lifecycle flag in the fleet after `lead-parser`.** Upgrade path: Django 4.2 LTS (or 5.x) — non-trivial because of ORM and middleware API changes.
- **Python 3.6+ supported per setup** — Python 3.6 itself is EOL (Dec 2021). Confirm the deployed runtime; ideally Python 3.11+.
- **`requests.Session()` with no timeout** — default is infinite. A slow central-dispatch hangs the request thread, exhausts the gunicorn worker pool, and surfaces as a service outage. **Add `timeout=(connect=5, read=30)` everywhere `requests` is used.**
- **ML models in-memory** — startup is slow (model load) and memory footprint is large. Blue/green deploys are required for model updates; rolling restarts will briefly serve from the old model + new model concurrently.
- **No request rate limiting visible** beyond DRF throttle defaults — confirm `app/throttles.py` config; an unauthenticated load test can saturate this service.
- **54+ migration files** in `app/migrations/` — schema drift risk if anyone runs `makemigrations` against a stale local DB.
- **Token-only auth** for inter-service calls; no mTLS, no OAuth. Token rotation is a coordinated event across all callers.
- **Elasticsearch on the request path** — if quote ingestion writes to ES synchronously, ES outages mask as quote failures. Confirm async / fire-and-forget.
- **Pricing is the most critical correctness surface in the fleet** and it currently runs on EOL framework versions — schedule this work.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/quote-manager-backend.md` — state facade in front of this engine.
- `~/projects/codebase-map/repos/contract-pricing-backend.md` — per-customer-contract pricing layer.
- `~/projects/codebase-map/repos/posting-backend.md` — primary inbound caller via `rateengine` REST client.
- `~/projects/codebase-map/domains/pricing-billing.md`.
