---
domain: listings-trade
status: draft
owner-team: unknown
member-services: 16
last-reviewed: 2026-05-12
---

# Domain — listings-trade

## Purpose
Core marketplace surface: vehicle inventory, load posting, the loadboard (browse + match), recommendation, bookmarks, saved searches. The "what's available to ship and who can ship it" half of the business.

## Member services
| Repo | Role | Stack | Status |
|---|---|---|---|
| inventory-backend | vehicle inventory mgmt | Java/Spring Boot 3.2.12 | seed |
| inventory-frontend | inventory UI (v1 + v2 feature-flagged) | TS/React 18 / Webpack 5.104 / single-spa-react 6 / MUI 6.1 / axios 1.15 | seed |
| loadboard-backend | loadboard core API (3 PG datasources; Temporal) | Java/Quarkus 3.27.0 | seed |
| loadboard-frontend | loadboard UI (Redux + Normalizr + parcels + sockets + charts + DnD) | TS/React 18 / single-spa 5.9 / Webpack 5.75 / MUI 5.16 / axios 0.21 | seed |
| loadbuilder-backend | load building / packaging (GCS as primary store, no RDBMS) | Java/Spring Boot 3.2.12 | seed |
| posting-backend | post a load to the board (densest fanout node in domain) | Java/Spring Boot 3.2.12 | seed |
| posting-frontend | posting UI (with React Query + Unleash) | TS/React 18 / Webpack 5.105 / single-spa-react 6 / MUI 6.3 / axios 1.15 | seed |
| load-bookmark-backend | bookmark / pin loads | Java/Quarkus 3.27.0 | seed |
| load-bookmark-service | python-side bookmark service (etcd, P0 `eval()`) | Python 3.10 / FastAPI | seed |
| load-recommender | recommend loads to carriers | Java/Quarkus 3.27.0 | seed |
| ml-service-recommender | ML model serving for recommendations | Python / FastAPI | seed |
| saved-search-handler | persist + run saved searches (ES percolate pattern) | Java/Quarkus 3.27.0 | seed |
| cube | ES read-query microservice (re-domained `platform` → `listings-trade` 4.13) | Java/Quarkus 3.27.0 (28 poms / 13 modules) | seed |
| carrier-order-importer-frontend | carrier-order import flow (form-heavy MFE) | TS/React 18 / single-spa 5.9 / Webpack 5.75 / MUI 5.16 / axios 0.21 | seed |
| fe-exercise-inventory-api | **hiring artifact** — FE coding-challenge API | Node/TS / Express 5 / Mongoose 8 | seed |
| fe-exercise-inventory-ui | **hiring artifact** — FE coding-challenge README | Docs/Markdown | seed |

## Key flows

**Posting → loadboard → recommendation → match (full chain now confirmed across seeded shadows):**
1. User posts a load via `posting-frontend` → `posting-backend` writes to its `posting` PG (Hikari 20).
2. `posting-backend` publishes via its outbox to 4 topics (incl. `posting.v2` consumed by `pusher`, `loadboard` events consumed by `loadboard-backend`).
3. `loadboard-backend` ingests posting events into its primary PG + denormalized projections used by `loadboard-frontend`'s search.
4. `ml-service-recommender` publishes `cars.ship.prod.ml.recommender` → consumed by `load-recommender` → fans out via `notification-orchestrator`.
5. `cube` consumes `cube.search-posting-events` → indexes into Elasticsearch for the listings/search query layer.
6. `saved-search-handler` percolates new postings against saved user queries; matches trigger Pub/Sub fan-out for notification.
7. `load-bookmark-backend` (JVM API) and `load-bookmark-service` (Python etcd sidecar) jointly own the carrier-side bookmark state.

**Inbound-import (the "I have an order outside Ship.Cars, get it in" path):**
- `carrier-order-importer-frontend` (UI) → `command-executor` (Quarkus integrations service) → `impersonator` → `posting-backend`.
- External-platform webhooks (Acertus, CarsArrive, SuperDispatch, EDI Orderful) feed `command-executor` via Pub/Sub; same downstream path.

## Data stores

| Service | Store | Notes |
|---|---|---|
| `posting-backend` | `posting` PG (Hikari 20) | densest both-directions node in the domain |
| `loadboard-backend` | 3 PGs (`loadboard` primary + `users` replica + `ctms` replica), all 20 | Temporal-orchestrated workflows; ID-only read path (search lives in `cube`/ES) |
| `inventory-backend` | `inventory` PG (Hikari 20, Envers audit) | read directly by `integrators-data-bridge` (shadow caller) |
| `loadbuilder-backend` | **GCS as primary store** (serialized Java + JSON, version-field optimistic-locking) | only Spring service in fleet without RDBMS |
| `load-bookmark-backend` | `loadbookmark` PG (**Hikari 4 prod / 16 dev** — outlier) | JVM bookmark API |
| `load-bookmark-service` | `etcd` (key prefix per carrier+load_id) | Python sidecar; **P0 `eval()` on bookmark values** |
| `load-recommender` | `loadrecommender` PG (16) + `usermanagement` PG replica (reactive 10) | ML-recommendation persistence |
| `ml-service-recommender` | `mlrecommender` PG + `recommender` PG (Tortoise 10/5) | Python FastAPI |
| `saved-search-handler` | `savedsearch` PG (3 datasources: main + users + ctms) + Elasticsearch percolate index (size=10000 hardcoded) | percolate pattern |
| `cube` | `cube` PG + `usermanagement` PG (16 main); Elasticsearch read-query backend | the "Elasticsearch read query microservice" |
| Frontends + hiring artifacts | none (browser-only) | |

## Cross-cutting concerns

- **3 of the 4 Java backends are Spring Boot, not Quarkus** (`posting-backend`, `inventory-backend`, `loadbuilder-backend`) — `PROJECTS_INDEX.md` miscategorizes. `loadboard-backend` + 6 supporting services are Quarkus.
- **Two single-spa MFE generations coexist:**
  - **Modern** (single-spa-react 6.0.2, webpack 5.104+, axios 1.15, MUI 6.x): `posting-frontend`, `inventory-frontend`. Same generation as `user-frontend`.
  - **Older** (single-spa 5.9, webpack 5.75, axios 0.21.1, MUI 5.16): `loadboard-frontend`, `carrier-order-importer-frontend`. Same generation as `trip-planner-frontend`, `chat-frontend`.
  - When the parent Loadmate shell upgrades to single-spa v6 fully, the older MFEs need coordinated bumps.
- **`axios 0.21.1` CVEs** affect 2 MFEs in this domain (`loadboard-frontend`, `carrier-order-importer-frontend`). Bump priority.
- **`posting-backend` is the densest both-directions node** in the listings-trade subgraph: 12+ outbound REST + 7 Pub/Sub subscriptions + 4 outbox-published topics. Single biggest blast-radius callee in the domain.
- **`integrators-data-bridge` directly reads `posting-backend` + `inventory-backend` Postgres** — sanctioned cross-DB reads with draft ADR-0003 contracts; schema migrations upstream silently break the bridge.

## Open questions / known gaps
- ~~Three "interview exercise" repos~~ — resolved (Phase 4.20): `fe-exercise-inventory-api` + `fe-exercise-inventory-ui` are explicit **hiring artifacts**, not production code. Recommended re-domain to `infrastructure` (or removal from the domain entirely) on the next triage refresh.
- ~~`ml-service-recommender` vs `load-recommender`~~ — resolved (Phase 4.10): `ml-service-recommender` (Python) publishes `cars.ship.prod.ml.recommender` topic; `load-recommender` (Quarkus) consumes that topic and fans out via `notification-orchestrator`. They're a pipeline, not peers.
- **`carrier-order-importer-frontend` Node 18 dependency** — Node 18 reaches EOL April 2025; coordinate with backend services on their Node version.
- **Modern vs. older single-spa generation drift** is a real maintenance gap. Plan for a coordinated migration of the 2 older MFEs.

## Related ADRs
- `~/projects/codebase-map/adr/0003-cross-service-db-read-policy.md` — applies to `integrators-data-bridge` reads of `posting-backend` and `inventory-backend` PGs.
- `~/projects/quarkus-rest-client-timeout-anti-pattern.md` — relevant for the Quarkus backends in this domain.

## Coverage
**16 of 16 shadows are `seed`** — listings-trade is **catalog-complete** as of 2026-05-12 (Phase 4.20). Two of the seeds are explicit hiring artifacts; 14 cover production code. All 4 Java backends and all 4 single-spa MFEs in the domain now have seed-quality shadow docs.
