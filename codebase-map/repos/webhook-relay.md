---
repo: webhook-relay
path: ~/projects/ship-cars-usa/webhook-relay
stack: Go (net/http stdlib + uber/zap)
domain: integrations
shape: single-module
last-synced-commit: 70b44ec59e47378c851a3ed4401c9c8347fe0422
last-synced-date: 2026-05-11
maintainer: unknown
status: seed
---

# webhook-relay

## What it is
Tiny Go (stdlib `net/http` + `uber/zap`) **stateless webhook gateway** that validates inbound GitHub webhook HMAC-SHA256 signatures, applies a GitHub IP whitelist (auto-refreshed hourly from GitHub's published ranges), and forwards each webhook to N configured downstream endpoints with the same signature. Path-based routing via `config.json` loaded at startup. Implements per-endpoint exponential-backoff retry inside the request. **Re-domained from `platform` to `integrations`** on 2026-05-11 — it's a third-party (GitHub) inbound integration gateway.

## How it fits
- Consumes API of: external GitHub Webhook IP ranges API (`https://api.github.com/meta`, hourly refresh) for the IP whitelist.
- Publishes events to: forwards inbound HTTPs to N configured downstream endpoints (URLs in `config.json`).
- Subscribes to: none — pure HTTP relay.
- Owns data store: none (stateless). Config from `/app/config/config.json` loaded at startup; no hot reload.

## Build / test / run
```
go build ./...
go test ./...
./webhook-relay   # listens on $PORT (default 8080); metrics on configured port; /health bypasses IP filter
```

## Key abstractions
- `handlers/webhooks.go` — POST handler: HMAC-SHA256 validation → forwarding service.
- `services/forwarding.go` — exponential-backoff retry to each downstream endpoint (sequential).
- `middleware/ipfilter/` — GitHub IP-range whitelist; hourly background refresh.
- `utils/signature.go` — HMAC-SHA256 verify + sign.
- `config/config.go` — JSON config loader (endpoints, paths, routing).

## Don't-do-here / gotchas
- **Sequential forwarding to N downstreams** — if one endpoint is slow, all subsequent ones wait. Fan out concurrently with bounded parallelism.
- **No persistent retry queue** — if a downstream endpoint stays down past the in-process backoff window, the webhook is dropped. GitHub will redeliver on its own schedule, but the gap is real. Consider a small SQLite or Redis-backed DLQ.
- **Config reload requires restart** — adding a new downstream is a redeploy.
- **No circuit breaker** — under sustained downstream failure, retries keep firing per request; combined with sequential forwarding, this can starve other webhooks.
- **IP-whitelist refresh race** — during the hourly refresh, requests at the boundary can be denied/allowed inconsistently. Acceptable but worth documenting.
- **CORS / Origin unverified** beyond the IP whitelist — GitHub publishes the IPs, so the IP filter is the authoritative trust boundary. Any other webhook source (Stripe, etc.) won't work without code change.
- **No request-ID propagation** — generates a UUID per request; doesn't forward `X-GitHub-Delivery`. Correlating with GitHub's delivery log requires log-level grepping.
- **No signed-config validation** — `config.json` URLs are not validated; a misconfig could turn this into an internal-network scanner via webhook forwarding.

## Relevant ADRs / docs
- `~/projects/codebase-map/domains/integrations.md`.
