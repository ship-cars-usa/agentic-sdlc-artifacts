---
repo: impersonator
path: ~/projects/ship-cars-usa/impersonator
stack: Go
domain: identity
shape: n/a
last-synced-commit: 92256802ef2331e47faf0349d57189762b5cf73c
last-synced-date: 2026-05-08
maintainer: unknown
status: seed
---

# impersonator

## What it is
Go service (Go 1.23.0) that issues scoped Keycloak access tokens for company- or user-level impersonation. Receives `GET /:companyId/*` or `GET /:userId/*`, fetches/refreshes the corresponding Keycloak access token from a Redis-backed cache, and proxies the request to the backend API gateway with that token as `Bearer` auth. Used by support flows. Caller seen in fleet review: `contract-pricing-backend` via `ImpersonatorClient` — *no caller-side timeout*. **No audit log of impersonations.**

## How it fits
- Consumes API of: **Keycloak** for `urn:ietf:params:oauth:grant-type:token-exchange` and refresh-token grants (`service/keycloak.go:50-99`); **`user-backend`** for email lookup — both `company-owner-api` and `user-api` symbolic names resolve to `user-backend` (`config.go:9-11` defaults to `localhost:17011/internal/v2/{companies,users}/...`; verified against `user-backend.V2InternalCompanyController` at `/internal/v2/companies/{companyId}/owner` and `V2InternalUserAccountController` at `/internal/v2/users/{userId}`). There is no separate `company-owner-backend` repo.
- Publishes events to: none observed.
- Subscribes to: none observed.
- Owns data store: **Redis** (`gomodule/redigo v1.9.2`) for access-token cache, keyed by `company::<id>` / `user::<id>` (`service/keycloak.go:139`).

## Build / test / run
```
go mod download
docker build -t impersonator:latest .                 # multi-stage Alpine + distroless (Dockerfile:1-30)
go run main.go                                         # local
# Ports: :3000 main app (main.go:23), :3001 metrics (main.go:24)
```

## Key abstractions
- `handler/handler.go:CompanyImpersonateHandler` / `UserImpersonateHandler` — receive impersonation requests; call `Auth` to get a token; proxy via `Proxy` (file:23-31).
- `service/auth.go:Auth.GetAccessTokenByCompanyId` / `GetAccessTokenByUserId` — orchestrate cache check → Keycloak refresh → user-email lookup → fresh token issuance (file:26-78).
- `service/keycloak.go:KeyCloak` — Keycloak client. Token-exchange + refresh-token grants. Caches the response with `TTL = RefreshExpiresAt - now - 10 s` (file:123-130). Caching is **asynchronous** (`go k.cacheAccessToken`, line 216) — race window where the next request can miss the cache.
- `service/keycloak.go:CheckAccessTokenValidity` — if access token expired but refresh isn't, calls refresh; if both expired, returns nil to trigger fresh exchange (file:75-99).
- `service/redis.go:Redis` — wrapper for Set/Get/Del + JSON marshal.
- `service/user.go:User` — looks up user/company email by ID (`auth.go:40, 67`).
- `service/proxy.go:Proxy.ProxyRequest` — forwards request to `API_GATEWAY_BASE_URL` with the Bearer token attached.

## Don't-do-here / gotchas
- **NO `http.Client.Timeout`** — `service/keycloak.go:48`: `keyCloakClient = &http.Client{}` with no `Timeout` set. Keycloak requests can hang **indefinitely**. Combined with the caller-side missing timeout in `contract-pricing-backend.ImpersonatorClient`, slow-Keycloak fully stalls the support path.
- **No audit trail of impersonations** — impersonation events are not recorded anywhere (no DB write, no audit topic). For SOC2 / SOX / GDPR purposes this is a compliance gap.
- **TTL not capped** — Keycloak access-token TTL is calculated as `expiresIn - 30 s` (`keycloak.go:211-213`); refresh-token TTL same. If Keycloak ever issues a year-long token, this service will cache it for a year.
- **Cache stampede on miss** — multiple goroutines requesting the same company/user simultaneously all hit Keycloak (no distributed lock). The async cache-write means the first request can return before the cache is populated.
- **No `context.WithTimeout`** on Keycloak / user-API / company-API RPCs. Datadog tracer only wraps; it doesn't enforce deadlines.
- **Email lookup latency** — synchronous calls to user-api / company-owner-api with no timeout (`auth.go:40, 67`). If those services are slow, the impersonation handler blocks.
- **No scope validation at issue time** — token-exchange specifies `requested_subject=email` (`keycloak.go:57`); whatever scopes Keycloak puts on the resulting token are not audited or restricted by this service.
- **Redis** — `REDIS_URL` is the only env var (`config.go:8`); TLS / auth not visible. Verify deployment configuration.

## Relevant ADRs / docs
- `CLAUDE.md` — minimal; no ADRs.
- `app/app.go` — Fiber server setup, metrics on `:3001`.
- `service/config.go` — required env vars (Keycloak URL, client id/secret, Redis URL, API endpoints).
- `~/projects/quarkus-fleet-review-2026-05-07.md#5-contract-pricing-backend` — the caller-side gap on `ImpersonatorClient`.
