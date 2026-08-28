---
repo: company-documents
path: ~/projects/ship-cars-usa/company-documents
stack: Python 3.8+ / FastAPI 0.74 / SQLAlchemy (sync) / psycopg2 / GCS
domain: analytics
shape: single-module
last-synced-commit: 54d57c6d3370b6426f020db8ab8a2b9ea1790d08
last-synced-date: 2026-05-12
maintainer: unknown
status: seed
---

# company-documents

## What it is
Python / FastAPI **document-storage and lifecycle service** for company-scoped documents (insurance certificates, operating authority, agreements, etc.). Stores files in GCS, tracks metadata + versions in PostgreSQL (SQLAlchemy, **synchronous**), publishes lifecycle notifications (created / updated / deleted) to Pub/Sub for downstream consumers (websocket relay, audit). Dual-route surface: separate shipper- and carrier-document routes with role-based access. Domain is `analytics` by convention, but functionally this is closer to **`platform`** (a shared storage + notification service); revisit on next domain pass.

## How it fits
- Consumes API of: media-proxy (`app/media_proxy.py`, **`requests` sync client with 25 s timeout** — fleet-rare timeout-clean). No async HTTP client (`httpx` not in use).
- Publishes events to: Pub/Sub `projects/atlantean-field-175514/topics/cars.ship.qa.notification` (shared with `ml-document-parser` — and hardcoded the same way). Message format `NotificationMessage` (event name + data + receivers, `type=websocket`). Batch: 5 max msgs, 1 s max latency.
- Subscribes to: not observed.
- Owns data store: PostgreSQL via SQLAlchemy (sync, psycopg2). GCS for file blobs. Schema in Alembic migrations: `documents`, `document_versions`, `document_requests` (inferred from routes; not fully surveyed in this pass).

## Build / test / run
```
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn main:app --host 0.0.0.0 --port 8000
pytest
# REST: POST/GET/PUT /api/documents (shipper); separate carrier routes
```

## Key abstractions
- `emit_message()` — `pubsub/__init__.py` — synchronous wrapper around `PublisherClient.publish()`; sends notifications.
- Shipper document routes — `api/routes/shipper_document_route.py` — REST CRUD; emits events on mutation.
- Carrier document routes — `api/routes/carrier_document_route.py` — same shape, carrier scope.
- Media proxy — `app/media_proxy.py` — `requests` HTTP call (25 s timeout) to fetch/process media.
- Settings — `app/settings.py` — Pub/Sub topic + GCS bucket + DB connection.
- Database — `database/database.py` — SQLAlchemy engine + Alembic.

## Don't-do-here / gotchas
- **Synchronous `emit_message()` inside async FastAPI handlers** — blocks the event loop if Pub/Sub stalls; will cause request timeouts and async concurrency collapse under any Pub/Sub latency spike. **Move to the Google Pub/Sub async client or run in a thread pool.**
- **Synchronous SQLAlchemy in FastAPI** — every DB call goes through the default thread-pool executor; high concurrency → thread-pool exhaustion → tail-latency degradation. Migrate to SQLAlchemy 2.x async or wrap explicitly.
- **Pub/Sub topic hardcoded to `cars.ship.qa.notification`** — same issue as `ml-document-parser`; production deploys publish to a QA-named topic unless env-overridden. Verify.
- **`requests` library is sync** in an async framework — the 25 s `media-proxy` timeout is good, but the sync call still blocks the thread for that long.
- **No idempotency on Pub/Sub events** — request retries publish duplicates; consumers must dedupe.
- **Batch latency = 1 s** — events may delay up to a second before publish; if a client waits on a synchronous "document created" notification, that latency is visible.
- **GCS credentials assumed in env** (no explicit credential-path fallback) — startup will fail unpredictably if the env-var path is unset or stale.
- **Two route trees with role-based access** — verify the auth-decorator is applied consistently; missing it on one route in either tree is a cross-tenant data risk.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/ml-document-parser.md` — shares the hardcoded-QA-topic pattern; sibling.
- `~/projects/codebase-map/repos/attachment-backend.md` — fleet-wide file-storage peer; partial scope overlap worth a boundary note.
- `~/projects/codebase-map/repos/media-proxy.md` — REST upstream (25 s timeout, fleet-rare).
- `~/projects/codebase-map/domains/analytics.md` (likely belongs in `platform` on a future domain pass).
