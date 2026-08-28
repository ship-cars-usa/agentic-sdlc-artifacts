---
repo: api-gateway
path: ~/projects/ship-cars-usa/api-gateway
stack: Go 1.25 / Fiber v2 / go-redis / golang-jwt
domain: platform
shape: single-module
last-synced-commit: 0a8a4c5e0883c0a434403cac88d4d7357b542e78
last-synced-date: 2026-05-12
maintainer: unknown
status: seed
---

# api-gateway

## What it is
Go 1.25 / Fiber v2 **central reverse proxy and edge security gateway** for the fleet. All external traffic flows through this service. Enforces **JWT auth** (Keycloak-backed, RSA public-key verification), role-based RBAC, per-endpoint rate-limit families (Redis-backed sliding-window counters via MessagePack), header injection (`X-Forwarded-For`, `X-Context`, Datadog trace headers), and template-based route expansion (`{{.Env.LOADBOARD_FETCHER_URL}}/api/...`). 13 endpoint-config files in `config/` route to: cube, posting-v3, location-history, user, driveaway, company-documents, crm-workflow, bookmarks, rate-engine, saved-search-handler, public-tracking, plus a `legacy-tokens` directory and `rate-limits` directory. Distroless container. Prometheus metrics on a separate port; Datadog tracing.

## How it fits
- Consumes API of: every public-facing internal service (~13 upstreams via template-expanded URLs). **No upstream timeout configured** — see Don't-do-here.
- Publishes events to: none.
- Subscribes to: none.
- Owns data store: **Redis** (rate-limit counters via MessagePack; legacy-token cache). No persistent store; ephemeral state only.

## Build / test / run
```
go build ./...
go test ./...
./api-gateway   # main on :3000; Prometheus metrics on :3001
# Required env: REDIS_URL, KEYCLOAK_TOKEN_VERIFICATION_URL, and a URL env per upstream
```

## Key abstractions
- `Endpoint` — `model/endpoint.go:24-37` — YAML route definition: template URL, auth-mode (`none` / `authenticated` / `service-account`), permissions, rate-limit family, additional headers.
- `AuthContext` — `core/auth.go:17-22` — JWT claims (roles, email, token) + legacy auth fallback (query-param / header).
- `ProxyRequest` — `core/proxy.go` — request forwarding: template expansion + header injection + passthrough.
- `rateLimitManager` — `core/rate_limit_manager.go:10-28` — Redis sliding-window counters via MessagePack; pool-allocated for GC efficiency.
- `App` — `app/app.go:15-20` — Fiber + metrics + Datadog + Redis lifecycle.

## Don't-do-here / gotchas
- **No explicit HTTP-client timeout on proxy requests** — Fiber's underlying `fasthttp` defaults to no timeout. **An unresponsive upstream hangs the gateway indefinitely**, exhausting connection slots and silently amplifying outages. **Set a per-route timeout** — at minimum a fleet-wide default of e.g. 60 s, with per-route overrides.
- **Legacy auth fallback (`checkLegacyAuthentication`) is still active** — `?token=...` query-param + `x-api-key` header bypass modern JWT. Documented technical debt; track retirement.
- **Empty `nil` rate-limit family on an endpoint = no rate-limiting** — no default fallback. A misconfigured YAML can silently disable limits. Add a startup assertion: every public endpoint MUST declare a rate-limit family.
- **TODO markers around `user.Enrich()`, `CompanyTypeId`, `isOwner`** — flagged for v2 removal; the v1 path is still wired.
- **`X-Context` header is unvalidated JSON** — template expansion failures are logged, not surfaced to the client. Verify no PII or auth claims leak through the header.
- **Rate-limit counters live in Redis** — a Redis outage means rate-limit fail-open is the default (the counter increment errors, the proxy proceeds). Audit the failure-mode and decide whether fail-closed is preferable for sensitive endpoints.
- **No circuit breaker** between the gateway and any single upstream — a hot upstream taking down the gateway's connection pool affects every other upstream.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/keycloak.md` — JWT signing authority.
- `~/projects/codebase-map/repos/socket-server.md` — separate edge for WebSocket; not routed via this gateway.
- `~/projects/codebase-map/relations/service-graph.md` — every gateway upstream is also seeded.
- `~/projects/codebase-map/domains/platform.md`.
