---
repo: ml-document-parser
path: ~/projects/ship-cars-usa/ml-document-parser
stack: Python 3.8+ / FastAPI 0.74 / Tortoise-ORM / asyncpg
domain: analytics
shape: single-module
last-synced-commit: 2b613791debd937f9aaa603b1ba47146407b239e
last-synced-date: 2026-05-12
maintainer: unknown
status: stale
---

# ml-document-parser

## What it is
Python / FastAPI **document-parsing web service**. Exposes a REST surface to accept dispatch sheets and other structured documents, extracts fields via pluggable parsers (the heavy lifting likely lives in a peer library — `ml-lib-extraction` — not in this repo), persists results to PostgreSQL, and publishes a generic notification to Pub/Sub. Datadog APM + Prometheus metrics wired in. Distinct from `ml-bot-order-v2` (which uses an LLM on free-form text) and `attachment-backend` (which stores files but doesn't parse them) — this one is the **structured-document-to-fields** extractor.

## How it fits
- Consumes API of: not observed in this repo's code — likely depends on `ml-lib-extraction` (peer library) for the actual parsing. No outbound `httpx` / `@RegisterRestClient` in grep.
- Publishes events to: Pub/Sub `projects/atlantean-field-175514/topics/cars.ship.qa.notification` (hardcoded in settings — see Don't-do-here).
- Subscribes to: not observed.
- Owns data store: PostgreSQL via Tortoise-ORM with **lazy connection init** (fires on first request, not at startup); pool `min=10 / max=10 / inactive_lifetime=120s`. 3 Aerich migrations: `0_init`, `1_client_response`, `2_document_parser`.

## Build / test / run
```
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn code.api:app --host 0.0.0.0 --port 8000
pytest
# REST: /api/v1/parse* (exact routes in code/services/ml/parser); /monitoring/{readiness,liveness}-check
```

## Key abstractions
- `app` — `code/api.py` — FastAPI instance with `app_startup()` / `app_shutdown()` lifespan hooks.
- Parser service — `code/services/ml/parser/...` — pluggable parser registry (concrete implementations not surveyed in this pass).
- Audit logger — `code/services/audit_logger.py` — structured logging with request context.
- Settings — `code/settings.py` — Pydantic `BaseSettings`; Tortoise + Pub/Sub topic config.
- Monitoring router — `routers/monitoring.py` — health/readiness/liveness.

## Don't-do-here / gotchas
- **Pub/Sub topic is hardcoded to `cars.ship.qa.notification`** in settings; no env override visible. **Production deploys publish to the QA topic** unless overridden via Pydantic `Settings` env-var convention. Verify the deploy manifest.
- **Lazy DB init** — `Tortoise.init()` runs on first request, not in the FastAPI startup hook. Cold-start request floods can exhaust the 10-connection pool while async init is in flight. Move to eager init via `lifespan`.
- **Pool `inactive_connection_lifetime=120 s`** is very short — idle connections drop after 2 minutes; first request after idle pays reconnect latency. Tune up.
- **Sync code in FastAPI** is a fleet risk for Python services; verify the parser pluggables don't block the event loop (`/code/services/ml/parser` not deep-read in this pass).
- **No outbound HTTP client visible** — but if the parser delegates to a remote ML model, that call site needs a timeout. Confirm.
- **`ddtrace` auto-instrumented** — agent outage silently drops spans.
- **No DLQ / retry on Pub/Sub publish failure** — failure path swallows.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/ml-bot-order-v2.md` — sibling parser, LLM-based, different surface.
- `~/projects/codebase-map/repos/attachment-backend.md` — likely upstream (files probably arrive via attachment IDs).
- `~/projects/codebase-map/domains/analytics.md`.
