---
repo: ml-bot-order-v2
path: ~/projects/ship-cars-usa/ml-bot-order-v2
stack: Python 3.12 / FastAPI 0.128+ / Tortoise-ORM 0.25+ / LiteLLM (Gemini 2.5-flash)
domain: integrations
shape: single-module
last-synced-commit: 5c649d5cd0cc71f3076ff199a7309be582c23b28
last-synced-date: 2026-05-12
maintainer: unknown
status: seed
---

# ml-bot-order-v2

## What it is
Python 3.12 / FastAPI / Tortoise-ORM service that **uses LLMs (Gemini 2.5-flash primary; 2.0-flash fallback via LiteLLM Router) to extract structured order / shipping data from unstructured text** (emails, SMS, attached documents) and publish a normalized **v2 `ContractMessage`** to Pub/Sub for downstream consumers. **Confirms the source of the `ml-bot-order` topic consumed by `posting-backend`**: this v2 service publishes to `oib-outbound-lm` (LM-flavored) and `oib-outbound-sf` (Salesforce-flavored). Ships with comprehensive in-repo docs (`ARCHITECTURE.md`, `AGENTS.md`, `LESSONS.md`, `STATE.md`) — the **best-documented service in the fleet**. **Re-domained `pricing-billing` → `integrations` on 2026-05-12** — this is unstructured-text-to-structured-DTO extraction, not pricing.

Sibling repo `ml-bot-order` (the older v1) still exists and is co-deployed; their boundary is "v1 = legacy text-only path, v2 = active development with multimodal attachments + the modernized stack". Plan a v1 retirement once v2 reaches parity.

## How it fits
- Consumes API of: LLM provider via LiteLLM (Gemini 2.5-flash primary, 2.0-flash fallback; **60 s timeout** at Router + per-request). `attachment-backend` for signed URLs + form upload (`httpx.AsyncClient`, **10 s per-request timeout**, **100 max connections / 20 keepalive**) — fleet-good explicit pool sizing.
- Publishes events to: Pub/Sub `oib-outbound-lm` (default) + `oib-outbound-sf` (env-overridable). Payload: `ContractMessage` (v2 contract envelope — extraction items + recipients + raw content + destination routing). Publisher workers=1; in-process queue max=10 000.
- Subscribes to: Pub/Sub `oib-inbound-lm` + `oib-inbound-sf` (`InboundIngestMessage`).
- Owns data store: PostgreSQL via Tortoise-ORM / asyncpg. Tables: `incoming_requests` + `incoming_requests_raw`, `ingest_requests_log`, `extraction_results`, `attachment_records`, `pubsub_events_log`. Idempotency: `UNIQUE(request_id, codename, status) ON CONFLICT DO NOTHING`.

## Build / test / run
```
uv sync                        # uv is the package manager
uv run uvicorn code.main:app --host 0.0.0.0 --port 8000
uv run pytest                  # 95%+ coverage convention per the project's testing skill
# REST: POST /api/v1/ingest/{destination}, GET /health
```

## Key abstractions
- `OutboundQueueService` — `code/services/outbound/service.py` — in-process queue decouples REST from Pub/Sub publish; prevents API latency from network I/O.
- `OutboundPublisher` — `code/services/pubsub/publishers/outbound.py` — wraps Pub/Sub client; routes by destination attribute.
- `ContractMessage` schema — `code/schemas/pubsub.py` — v2 contract envelope.
- `AuditMiddleware` + `AuditService` — `code/core/middlewares/audit.py`, `code/services/audit.py` — non-blocking audit logging; `MemoryObjectStream` + background task; batches on 50 events or 2 s.
- `IngestRequestLog` model — `code/models/logs.py` — per-request idempotency tracking.

## Don't-do-here / gotchas
- **Idempotency is per `(request_id, codename, status)`** — a duplicate REST POST with the same `request_id` is safely no-op. But the **upstream caller must generate stable `request_id`s**, otherwise dedup is bypassed.
- **In-process outbound queue max=10 000** — under sustained spike, `send_nowait()` errors; no backpressure handling visible at the REST boundary.
- **Pub/Sub inbound auto-acks after callback** — `ingest_requests_log` captures the attempt, but a partial-failure during processing means the message is acked while the log row may not be committed. Add idempotency guards before the publish, not just the ack.
- **LLM timeout chain is 60 s end-to-end** — if upstream caller's HTTP timeout is shorter, the caller gives up but the LLM call continues and eventually emits to Pub/Sub. Document this divergence or pass a deadline.
- **Two outbound topics from one service** (`-lm`, `-sf`) — `posting-backend` subscribes to `-lm` (LM-flavored). The `-sf` topic implies a separate Salesforce-flavored consumer; confirm who owns that.
- **Dual-deployment with `ml-bot-order` (v1)** — both run; coordinate retirement. Until then, every shape change to the contract must be backward-compatible.
- **Tortoise-ORM connection pool not explicitly tuned** in visible config — relies on asyncpg defaults. Right-size after observing wait metrics.

## Relevant ADRs / docs
- `~/projects/ship-cars-usa/ml-bot-order-v2/ARCHITECTURE.md` — in-repo design doc (the actual source of truth).
- `~/projects/ship-cars-usa/ml-bot-order-v2/LESSONS.md` — postmortem notes worth carrying into peer services.
- `~/projects/codebase-map/repos/ml-bot-order.md` — v1 sibling (stub).
- `~/projects/codebase-map/repos/posting-backend.md` — consumes `oib-outbound-lm` as `ml-bot-order` subscription.
- `~/projects/codebase-map/repos/attachment-backend.md` — REST upstream.
- `~/projects/codebase-map/domains/integrations.md`.
