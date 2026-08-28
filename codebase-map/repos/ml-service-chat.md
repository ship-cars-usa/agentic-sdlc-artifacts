---
repo: ml-service-chat
path: ~/projects/ship-cars-usa/ml-service-chat
stack: Python 3.9 / FastAPI 0.95.2 / Tortoise ORM 0.19.3 / OpenAI 1.30.1 / LlamaIndex 0.10.23
domain: communication
shape: single-module
last-synced-commit: c46c75a2b43f1ee11809ca37be1f0f8f67b7820b
last-synced-date: 2026-05-12
maintainer: unknown
status: seed
---

# ml-service-chat

## What it is
ChatGPT-backed assistant API. Two routers under one FastAPI app:

- `/carrier/...` — agent-side chat (e.g. dispatcher tooling). Token + session model with **per-token rate limits** (`CARRIER_TOKENS` whitelist in `settings.py`, ~70 carriers with hardcoded `conversation_count_limit` and `question_count_limit`).
- `/customer/...` — customer-facing assistant ("Sofia"). Mirrors the carrier shape with a separate token set (`CUSTOMER_TOKENS`).

Backed by GPT-4o (`gpt-4o-2024-05-13`, `temperature=0`, `seed=23`) plus a LlamaIndex vector store on Postgres for retrieval. Tortoise ORM with **two separate logical apps** (`ml-service-chat` + `ml-service-customer-chat`) and **two Postgres connections**: `default`/`customer_default` both point at DB `ml_service_chat`, plus a `db-source` connection pointing at the `production` DB as user `rateengine`.

## How it fits
- **Called by:** `ml-ui-chat` (the Streamlit customer UI on `/chat/`) over REST, hitting `/customer/chat/conversation/{init,question,question/rate}`. Carrier callers are unknown from the catalog today; likely a Loadmate frontend module.
- **Consumes:**
  - **OpenAI API** (`openai==1.30.1`, key `OPENAI_API_KEY`, default `"SHOULD-BE-CHANGED"`). **Note:** the carrier_chatgpt / customer_chatgpt service modules call `openai.ChatCompletion.acreate(...)` — the legacy v0 API removed in `openai>=1.0`. Either there's a compatibility shim in the call chain or this code path is dead; worth confirming during the next deepening pass.
  - **`production` Postgres as user `rateengine`** via the `db-source` Tortoise connection. **This is a new shadow-caller edge**: ml-service-chat reads `rateengine`'s production data directly rather than through the rateengine REST API. Add to `relations/data-stores.md` cross-DB-reads list and draft an ADR-0003 contract.
- **Publishes events to:** none — REST-only, no Pub/Sub producer or consumer in the codebase.
- **Owns data store:** Postgres `ml_service_chat` (Tortoise, asyncpg, **pool 10/10**, `max_queries=50000`, `max_inactive_connection_lifetime=120s`).
  - Vector store: LlamaIndex `llama-index-vector-stores-postgres` 0.1.4.post1 — embeddings live in the same Postgres.
  - `customer_default` is a second connection to the same `DB_NAME` (`ml_service_chat`) with its own 10/10 pool. The two Tortoise apps share one physical DB unless `DB_HOST` / `DB_NAME` are overridden per-deploy. Worth verifying in helm.

## Build / test / run
```
pip install -r builder/files/requirements.txt
cd code
aerich init -t settings.TORTOISE_ORM
aerich upgrade        # applies migrations from code/migrations/{ml-service-chat,ml-service-customer-chat}/
OPENAI_API_KEY=… APP_ENVIRONMENT=development RUNTIME_SERVER_PORT=8087 \
RUNTIME_SERVER_LOG_LEVEL=info RUNTIME_SERVER_RELOAD_FILES=true python server.py
```

Docker: distroless `gcr.io/distroless/python3-debian11` final stage; uvicorn entrypoint via `server.py`.

## Key abstractions
- `code/api.py:app` — root FastAPI with two sub-routers (carrier_chat, customer_chat) plus monitoring.
- `services/ml/carrier_chat/api.py` + `services/ml/customer_chat/api.py` — per-audience routers, both gated by `Authenticator` (token+session middleware) and a `*RateLimitterMiddleware`.
- `services/ml/{carrier,customer}_chatgpt/service.py` — GPT-4o call sites; uses `tenacity==8.2.3` for retries and `async-lru` for in-process caches.
- `services/ml/customer_chatgpt/vector_store.py` — LlamaIndex Postgres vector store (RAG over conversation context).
- `middlewares/authentication.py` — header-driven token + session (`x-auth-token`, `x-session-id`); `authentication_only_paths=["/.../conversation/init"]` lets init skip session requirement.
- `middlewares/{carrier,customer}_rate_limitter.py` — counters live in DB, not Redis; check `utils.carrier_conversation_count` / `customer_conversation_count` for the SQL.
- `settings.CARRIER_TOKENS` / `CUSTOMER_TOKENS` — **~70+ hardcoded UUID tokens with embedded company IDs and limits**. Adding a carrier requires a code change and redeploy.

## Don't-do-here / gotchas
- **`openai==1.30.1` + legacy `openai.ChatCompletion.acreate` call site is incompatible.** The v0 module-level interface was removed in `openai>=1.0`. Either there's a vendored compatibility layer or this call path is dead. Verify the actual runtime path; do not assume it works.
- **Hardcoded carrier/customer token whitelist** in `settings.py` (70+ entries). Onboarding a new caller = PR + deploy, not config. Consider extracting to DB or external config once the pattern stabilizes.
- **`OPENAI_API_KEY` default literally `"SHOULD-BE-CHANGED"`** — same fleet pattern as `ml-service-listener` and `pusher`. Ensure prod env wiring is verified; a missing env var silently boots the service with an unusable key.
- **`db-source` shadow-caller edge** — direct read of `rateengine`'s `production` Postgres as the `rateengine` user. Subject to **ADR-0003** (cross-service DB read policy). Needs a versioned schema contract; ties to **ADR-0005** (rateengine EOL rewrite) — when rateengine moves off Django 2.1.7, this read path must move with it.
- **Python 3.9 / FastAPI 0.95.2 / uvicorn 0.22.0 are all behind current** (FastAPI is at 0.115+, uvicorn 0.30+, Python 3.9 reaches EOL Oct 2025). Not as severe as `lead-parser` or `rateengine`, but a future-quarter version-bump candidate.
- **No Pub/Sub** — this is a synchronous REST service. If you want async question handling (long-running RAG, model fallbacks), it requires new architecture, not a config change.
- **Tortoise ORM 0.19.3** is two minors behind (0.21.x current). Migration with `aerich` works, but newer Tortoise has incompatible config formats; budget time for any version bump.
- **`conversation_count_limit` and `question_count_limit` are enforced via DB counts** — heavy traffic can degrade the rate-limit check itself. If the limiter starts to be a hotspot, move counters to Redis with a TTL.

## Relevant ADRs / docs
- `~/projects/codebase-map/adr/0003-cross-service-db-read-policy.md` — covers the `rateengine` production-DB read.
- `~/projects/codebase-map/adr/0005-rateengine-eol-rewrite.md` — the `rateengine` migration this service's `db-source` depends on.
- `~/projects/codebase-map/repos/ml-ui-chat.md` — the customer-facing Streamlit caller.
- `~/projects/codebase-map/relations/data-stores.md` — Postgres pool table; this service adds two rows (or one with two logical apps).
- `~/projects/codebase-map/domains/communication.md`.
