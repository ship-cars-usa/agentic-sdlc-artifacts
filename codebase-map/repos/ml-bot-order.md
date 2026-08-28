---
repo: ml-bot-order
path: ~/projects/ship-cars-usa/ml-bot-order
stack: Python 3.11 / FastAPI / Tortoise-ORM 0.25 / google-genai (legacy)
domain: integrations
shape: single-module
last-synced-commit: e8b2f92df91e87e556bd1a08947c17c378100e94
last-synced-date: 2026-05-12
maintainer: unknown
status: seed
---

# ml-bot-order

## What it is
**v1** of the bot-order extraction service — Python 3.11 / FastAPI / Tortoise-ORM. **Sister to `ml-bot-order-v2`** (the v2 active development line). Receives SMS + email payloads, calls **Google Gemini directly via the older `google-genai` SDK** (not LiteLLM), extracts vehicle / route / timing fields, and posts drafts directly to `posting-backend` via REST (through `impersonator`). **v1 does NOT publish to a Pub/Sub topic** — `posting-backend`'s `ml-bot-order` subscription is fed by **v2** (`oib-outbound-lm`), not this service. v1 is therefore the "legacy text-only, REST-write" flavor; v2 is the "multimodal + Pub/Sub-mediated" flavor. **Re-domained `pricing-billing` → `integrations` on 2026-05-12** to match v2. Per the v2 shadow, **retire v1 once v2 reaches parity**.

## How it fits
- Consumes API of: company-settings service, vehicle-lookup service, `posting-backend` (via `impersonator`), Elasticsearch index `lm-contacts` (address resolution). `httpx.AsyncClient` with `timeout=20s`, `max_connections=10`, `keepalive=5` — **explicit pool sizing**, but Elasticsearch client has no per-request timeout.
- Publishes events to: **none observed**. The `ml-bot-order` Pub/Sub topic consumed by `posting-backend` is supplied by `ml-bot-order-v2`, not this service.
- Subscribes to: Pub/Sub `sms-events` subscription via `SMSSubscriber`.
- Owns data store: PostgreSQL via Tortoise-ORM (`minsize=10 / maxsize=10 / inactive_lifetime=120s`). Tables: `sms_request`, `sms_request_contact`, `email_request`, `email_request_contact`, `incoming_event_log` (20+ status states from `NEW` → `DECODED` → `VALIDATED` → `CREATED_DRAFT_POSTING` / `FAILED_*`), `ai_response_poc`, `posting_response_poc`. Elasticsearch `lm-contacts` for address lookup.

## Build / test / run
```
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn code.api:app --host 0.0.0.0 --port 8000
pytest
# REST: /api/ml/service/botordy/, /monitoring/{liveness,readiness}-check
```

## Key abstractions
- `BotOrdyService` — `code/services/ml/botordy/service.py` — orchestrates SMS/email parse → AI call → enrichment → posting-draft creation.
- `GeminiClient` — `code/services/ml/botordy/clients_ai/gemini/gemini.py` — wraps the legacy `google-genai` SDK; `timeout=15s`, `temperature=0`, `seed=5` for reproducibility.
- `SMSEventParser` — `code/services/pubsub/parsers/sms.py` — Pub/Sub callback; logs to `IncomingEventLog`; deserializes + validates + delegates.
- `IncomingEventLog` model — `code/services/ml/botordy/models_persisted.py` — explicit 20-state lifecycle.
- `http_client` — `code/http_client.py` — shared `httpx.AsyncClient` for outbound.

## Don't-do-here / gotchas
- **Uses the legacy `google-genai` SDK**, not LiteLLM. Migration to multi-provider routing (or fallbacks like v2's Gemini 2.0-flash) requires a code change. The SDK itself is deprecated/aged; verify Google's support timeline.
- **Pub/Sub auto-ack on callback** — `SMSEventParser` acks after delegation; if posting-API fails mid-request, ack still succeeds. **No idempotency guard** (unlike v2's `UNIQUE(request_id, codename, status)`).
- **No timeout on Elasticsearch lookup** — `AsyncElasticsearch` client is used without a per-request timeout; long queries block the event loop.
- **No published topic** — anything that expects to consume `ml-bot-order` from this service will get nothing. If you find a consumer subscribed to a topic produced by *this* service, fix the consumer or this service.
- **Tortoise pool `minsize=maxsize=10`** — same fixed-pool pattern as `ml-service-listener`. Under burst, requests queue without backpressure.
- **Hardcoded posting endpoint** + `GENERATIVE_MODEL_NAME` env-var-only model selection. Model rollback requires env-var + redeploy.
- **Datadog auto-instrumented** — agent outage silently drops spans.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/ml-bot-order-v2.md` — successor; **the v1-retirement plan lives there**.
- `~/projects/codebase-map/repos/posting-backend.md` — downstream sink.
- `~/projects/codebase-map/repos/impersonator.md` — auth flow.
- `~/projects/codebase-map/domains/integrations.md`.
