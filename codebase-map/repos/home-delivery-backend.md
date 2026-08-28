---
repo: home-delivery-backend
path: ~/projects/ship-cars-usa/home-delivery-backend
stack: Node 13 / TypeScript 3.7 / Fastify 2.12 / fastify-swagger 2.5 / axios 0.19
domain: operations
shape: single-module
last-synced-commit: 72fe317ad3071f376d378e3c9a9d37253b8d9a61
last-synced-date: 2026-05-12
maintainer: unknown
status: seed
---

# home-delivery-backend

## What it is
A small Fastify proxy service that backs the **Home Delivery Widget** (`hdw.ship.cars`) — the embeddable car-hauling quote widget that runs on dealer websites. Listens on `:8090` and exposes 3 routes:

- `GET /api/health` → `'OK'`.
- `POST /api/transit` → forwards a `LoadMateTransitTimeRequest` to a dealer-context API and returns the `LoadMateTransitTimeResponse`.
- `POST /api/quote` → same shape but for quote rates.

The service multiplexes calls based on the `X-Context` request header. Each context (one per partnered dealer site — `henrybrownauto`, `westcoastautosales`, `dealersocket`, `ginspiredautomall`, `consumerfirstautogroup`, `dealersync`, `stmaryscdjr`, `pioneertrucks`, `mcs`, `autoworldofamerica`, `drivenautosales`, `carbingo`, `lexusoforland`, plus dev / qa / staging / prod variants of `quotemanager-*`) is mapped in `src/config.ts` to a target API URL + auth method (either a static token or a Keycloak token-exchange flow).

In practice the service has two backend modes:

1. **Direct-to-Montway** for the dealer-site contexts — each one hits `https://gateway.montway.com/` with a static bearer token unique to that dealer brand.
2. **Through `quote-manager-backend`** for the `quotemanager-{dev,staging,production}` contexts — uses Keycloak token-exchange (`urn:ietf:params:oauth:grant-type:token-exchange`) to mint a per-dealer JWT, then calls `quote-manager-backend`'s `/v1/providers/montway` route.

So this service is the public widget's API surface and a brand-token-to-Ship.Cars-context bridge.

## How it fits

- **Called by:** dealer websites embedding the Home Delivery Widget. CORS is constrained to a fixed list in `config.app.allowedOrigins` (33 dealer domains + the `hdw.ship.cars` / `hdw-qa.ship.cars` widget hosts + `localhost` variants).
- **Consumes API of:**
  - `https://gateway.montway.com/` — Montway's dealer-API gateway (legacy direct path).
  - `quote-manager-backend` via Keycloak token-exchange against `auth.ship.cars/auth/realms/master/protocol/openid-connect/token` (modern path; the `quotemanager-*` contexts).
- **Publishes events to:** none.
- **Owns data store:** none — stateless proxy.

## Build / test / run
```
npm install
npm run start:dev          # nodemon, hot-reload
npm run build              # rimraf + tsc
npm run start:prod         # node dist/index.js
npm test                   # jest
```

Docker: `node:13-slim` base; entrypoint `docker-entrypoint.sh`.

## Key abstractions

- `src/index.ts` — Fastify bootstrap, CORS registration, Swagger registration, route registration.
- `src/routes/index.ts` — 3 `RouteOptions` entries (health, transit, quote) with schema references.
- `src/controllers/mainController.ts` — `getTransitTime` and `createQuote` route handlers; the `getContext` / `getJwtTokenFromUser` / `getProxy` helpers that select-and-call the per-context backend.
- `src/controllers/converters.ts` — bidirectional shape conversion between the widget's wire format and LoadMate's API format (`convertToLoadMateQuoteRequest`, `convertFromLoadMateQuoteResponse`, transit-time variants).
- `src/controllers/interfaces.ts` — TypeScript shapes for both wire formats (`QuoteResponse`, `LoadMateQuoteResponse`, `QuoteRate`, `TransitTimeResponse`, `LoadMateTransitTimeResponse`).
- `src/config.ts` — `config.contexts: { [name]: Context }` mapping. Each `Context` is either `{ apiUrl, token }` (static token) or `{ apiUrl, client: { id, secret, authUrl, userEmail } }` (Keycloak token-exchange).
- `src/config/swagger.ts` — OpenAPI/Swagger UI exposed; useful for discovering the wire format.

## Don't-do-here / gotchas

- **P0 — production secrets committed to git in plaintext.** `src/config.ts` carries 13 production Montway bearer tokens (one per dealer brand: `henrybrownauto`, `westcoastauto`, `dealersocket`, …) plus the production `quote-manager-backend` Keycloak client secret (`f510dc89-f7c7-499a-9dca-4b7ba6f0161c`) and the dev / staging client secrets. Anyone with read access to the repo can hit Montway's gateway as any of those dealer brands and impersonate the `quote-manager-backend` admin client. The repo also embeds the dev / staging / prod `user-admin-client` Keycloak secret. These have not rotated in the file's history. Move to `gcp-secret-manager`-style external secret + per-env helm config.
- **Stack is multiple-major-versions stale.** Node 13 was non-LTS and EOL April 2020. Fastify 2.12 (current is 5+), axios 0.19 (current is 1+; many CVEs in 0.x), TypeScript 3.7 (current 5+), Jest 25 (current 29+). Any future feature work should pair with a stack bump or a rewrite.
- **The 33-domain CORS allowlist is fragile.** Adding a new dealer brand requires editing this file and redeploying. No data-driven source (e.g. fetching the list from `quote-manager-backend` on startup). New dealer onboarding pull-request shape is "add 2-3 origins + 1 context + 1 secret."
- **No timeout on outbound axios calls.** `Axios.create()` is used without a `timeout` option — a slow Montway gateway will hang the request indefinitely. Add a `timeout` default of 10-15 s.
- **The Keycloak token-exchange call hardcodes `userEmail: 'client_email'`** in the prod context — looks like a placeholder that escaped review. The dev context uses `test+shipper@ship.cars` and staging uses `test+staging+integration@ship.cars` (also test accounts in prod-cert paths). Worth confirming the prod placeholder is intentional or a config bug.
- **No structured logging beyond Fastify's defaults.** The custom `req` serializer captures `x-context` and `x-reference-id`, which is useful, but there's no MDC / trace ID propagation to the downstream Montway / quote-manager call. Incident debugging is "grep the logs by `x-context`."
- **`MAXIUMUM_PICKUP_WINDOW = 7`** (with a typo in the constant name) is the only domain constant in the controller. It's also hardcoded. If the business policy changes ("pickup window of 10 days for premium brands") this is a one-line code change, not a config.
- **No tests in `test/`** (per repo layout), so the `npm test` script is run-and-pass but proves nothing. Treat the service as effectively untested.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/quote-manager-backend.md` — the modern backend path; this service brokers Keycloak token-exchange into it.
- `~/projects/codebase-map/repos/socket-server-old.md` — separate fleet case of credentials-in-git; same fix recipe applies (`externalSecrets` + rotation).
- `~/projects/codebase-map/domains/operations.md`.
