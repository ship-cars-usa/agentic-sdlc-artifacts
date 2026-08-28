---
repo: media-proxy
path: ~/projects/ship-cars-usa/media-proxy
stack: Go
domain: platform
shape: n/a
last-synced-commit: d3243b2e7847455d1a38a3a92b6172950cf6f257
last-synced-date: 2026-05-08
maintainer: unknown
status: seed
---

# media-proxy

## What it is
Go service (Go 1.26) that proxies media requests to Google Cloud Storage with token-based authorization. Three independent HTTP servers in one process: public proxy (`:9771`) for client downloads, internal API (`:9773`) for backend key issuance / revocation, and a Prometheus metrics endpoint (`:9740`). Validates **opaque** tokens against Redis (no JWT signing observed), applies wildcard scope-based access control, and streams objects directly from GCS. Companion library: `quarkus-extension-media-proxy` (separate repo, the consumer-side client).

## How it fits
- Consumes API of: **Google Cloud Storage** via `cloud.google.com/go/storage v1.62.1` with service-account credentials. Exports tracing/metrics to Datadog (`dd-trace-go v2.7.2`).
- Publishes events to: none observed.
- Subscribes to: none observed.
- Owns data store: **Redis** (`go-redis v9.18.0`) for ephemeral keys (TTL ≤ 24 h, `k-` prefix) and **PostgreSQL** (`jackc/pgx v5`) for long-lived keys (TTL > 24 h, `d-` prefix; backed by Redis cache at 80% TTL).

## Build / test / run
```
make test                # all tests (Makefile:25)
make test-unit           # skip integration (Makefile:30)
make test-coverage       # with coverage (Makefile:37)
make build               # bin/media-proxy (Makefile:46)
make run                 # docker-compose up redis + postgres, then run (Makefile:49)
docker build -t media-proxy:latest .
```

## Key abstractions
- `handler/public_proxy.go:PublicProxyHandler` — validates token, checks scope/whitelist, streams from GCS.
- `handler/internal_api.go:CreateKeyHandler` — `POST /api/v1/keys`; issues opaque tokens with TTL/scope/metadata. Critical: `string.Clone()` at line ~63 prevents Fiber buffer-reuse bugs (a foot-gun if removed).
- `service/key_manager.go:KeyManager` — token lifecycle. Generates `k-` (ephemeral, Redis-only) vs `d-` (durable, PG + Redis cache) at the 24 h boundary (`file:574-590`); refreshes the Redis cache at 80% TTL (`file:251`).
- `service/key_manager.go:ValidateKey` — Redis lookup with PG fallback for durable keys; expiry checked at `file:265-292`.
- `service/gcs_storage.go` — GCS object streamer with generation support and metadata headers (Content-Type, Cache-Control, size).
- `handler/whitelist.go` — glob-pattern matching for anonymous-allowed paths.
- `model/key.go:Key.CanAccess()` — wildcard scope match (e.g. `/media/company_123/*`).
- `service/config.go:Config` — env loader: `MAX_TTL_SECONDS`, `DEFAULT_TTL_SECONDS`, `SERVICE_TOKEN_SIGNING_KEY`, `ADMIN_TOKEN`, `GCS_BUCKET`, `REDIS_ADDR`, `TRUSTED_ISSUERS`.

## Don't-do-here / gotchas
- **No HMAC / JWT signature on tokens.** Tokens are opaque keys validated only by Redis presence — there is no signature check (`main.go` shows no signing wiring). If a consumer expected signed URLs, this is *not* implemented. Treat the Redis store as the security boundary; if Redis is shared / leaks, every issued token is at risk.
- **No per-route HTTP timeout on the public proxy.** Fiber v3.1.0 server has no `IdleTimeout`/`ReadTimeout`/`WriteTimeout` configured for the public proxy. GCS fetch is synchronous — slow GCS responses block media-proxy goroutines (`handler/public_proxy.go:43` `fetchAndStreamObject`). This is exactly the blocking path that fails `chat-backend.DiscussionController.getDiscussion()` per the fleet review; the call needs a timeout on the *caller* side and a server-side deadline here.
- **Cache stampede possible** — concurrent cache misses race to GCS without request coalescing. The 24 h TTL cap (`service/key_manager.go:216-219`) limits long-tail damage but doesn't prevent thundering herd on cold cache.
- **No `context.WithTimeout` in fetch path** — `fetchObjectFromStorage` (`file:101`) gets context from the tracer span only.
- **Auth split** — public proxy requires token-or-whitelist (`file:65-73`); internal API requires Bearer service token (middleware); admin operations use a separate `ADMIN_TOKEN` env var.
- **Keys stored in Redis as JSON plaintext** (`service/key_manager.go:198`). No mention of Redis TLS in pom/Dockerfile. GCS credentials loaded from a service-account file (`README:88`).

## Relevant ADRs / docs
- `README.md` — Architecture (line 5–23), Configuration (line 71–102), Security Considerations (line 194–202).
- `CLAUDE.md` — three-tier endpoint structure, Redis TTL strategy, scope validation.
- `~/projects/quarkus-fleet-review-2026-05-07.md#4-chat-backend` — caller-side gotcha when this service is slow.
- `quarkus-extension-media-proxy` (separate repo, in `platform` domain) — the consumer-side library.
- `~/projects/codebase-map/relations/media-url-flows.md` — **literal GCS lookup** of the media path (hop 5; `gcs_storage.go` → `OBJECT_NOT_FOUND` on a wrong path). Not a URL fix site — a bad path is assembled upstream in `syncer`.
