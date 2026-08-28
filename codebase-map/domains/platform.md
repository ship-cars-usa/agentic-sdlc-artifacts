---
domain: platform
status: draft
owner-team: unknown
member-services: 54
last-reviewed: 2026-05-12
---

# Domain — platform

## Purpose
Shared libraries, common Quarkus / Spring extensions, the micro-frontend shell + shared FE component packages, the API gateway, media proxy, attachment storage, archival, the toolbox catch-all, the backoffice admin app, the BOM, and a small handful of services that don't slot into a vertical (CRM workflows, company-cleanup, cube/dataone — TBD).

## Member services (by sub-group)

### Java shared libraries / extensions / BOM
| Repo | Role |
|---|---|
| commons | shared Quarkus commons libraries (`Java/Maven` parent) |
| quarkus-commons | shared Quarkus commons libraries |
| spring-commons | shared Spring commons libraries |
| shipcars-quarkus-bom | BOM for Ship.Cars Quarkus apps |
| models-lib | shared Java models library |
| quarkus-auto-reflection | auto-reflection extension |
| quarkus-data-migration | data-migration extension |
| quarkus-extension-bootstrap | bootstrap extension |
| quarkus-extension-firestore-storage | Firestore storage extension |
| quarkus-extension-media-proxy | Media Proxy clients |
| quarkus-extension-persistence | persistence extension |
| quarkus-extension-webclient | web-client extension |
| quarkus-imperative-boilerplate | imperative-style boilerplate |
| quarkus-k8s-boilerplate | K8s template |
| quarkus-pubsub | Pub/Sub extension |
| quarkus-request-filter | request-filter extension |

### Micro-frontend shell + shared FE packages
| Repo | Role |
|---|---|
| public-root-app-frontend | public root single-spa orchestrator |
| public-common-frontend | public common frontend |
| ui-commons | common frontend components & architecture |
| ui-components-frontend-package | UI components library (Vite) |
| ctmslb-components-frontend-package | CTMS load board component library |
| carrier-packages-frontend | frontend monorepo (npm + Nx) |
| entities-frontend-package | frontend entities representation package |
| globals-frontend-package | globals frontend package |
| ctms-frontend | CTMS frontend |
| settings-frontend | settings frontend |
| gallery-frontend | gallery frontend |
| inspection-requirements-frontend | inspection requirements UI |
| documentation | Ship.cars documentation site |
| website | marketing website |
| platform-frontend | platform frontend |

### Edge / gateway / proxy
| Repo | Role | Stack |
|---|---|---|
| api-gateway | API gateway | Go |
| media-proxy | token-based media proxy | Go |
| webhook-relay | GitHub webhook signature validator/relay | Go |
| import-map-deployer | import map deployer (single-spa) | Go |
| logging-manager | K8s service log-level manager | Go |
| internal-api-docs | internal API docs | Node/JavaScript |
| internal-api-docs-controller | internal API docs controller | Go |
| api-documentation-builder | API documentation builder | Node/JavaScript |
| platform-backend | platform backend | Node/JavaScript |
| pubsub-exception-handler | undeliverable Pub/Sub messages | Java/Quarkus 3.20.2.2 |

### Backoffice (admin)
| Repo | Role |
|---|---|
| backoffice-backend | internal backoffice administration API |
| backoffice-frontend | backoffice frontend |
| backoffice-app-ARCHIVED | archived backoffice app |
| uship-backoffice-backend | uShip backoffice backend |
| uship-backoffice-frontend | uShip backoffice frontend |

### Other platform services (need triage)
| Repo | Role | Stack |
|---|---|---|
| attachment-backend | file attachments and media storage | Java/Quarkus 3.20.4 |
| archival-service | archival service | Java/Quarkus 3.15.2 |
| archiver | archiver service | Java/Quarkus 2.9.1.Final |
| archival-data-verification | cross-DB data consistency verifier | Go |
| metadata | metadata service | Java/Quarkus 3.20.2.2 |
| toolbox-service | catch-all utility service | Java/Quarkus 3.15.0 |
| crm-workflows | CRM workflows service | Java/Quarkus 3.27.0 |
| company-cleanup-utils | company data cleanup | Java/Quarkus 3.15.2 |
| cube | "Cube service" (purpose unclear from repo) | Java/Quarkus 3.27.0 |
| dataone | "Data One service" | Java/Quarkus 3.27.0 |

## Key flows
TBD. Platform services are typically called by every vertical above; flows here are best documented in each consumer's domain rollup.

## Data stores
- `attachment-backend`: GCS (`shipcars-platform-dev-media`, env-overridable) + Postgres metadata (Hikari `max-size=16`).
- `metadata`: `metadata` PG (`max-size=16` dev). Ships an in-repo `spring-client` module that Spring consumers compile against — major-version renames here silently break Spring downstreams.
- `dataone`: `dataone` PG (Hikari **`max-size=4`** — pool-size outlier given **8 inbound REST edges**) + Caffeine `1400 h` TTL cache.
- `media-proxy`: opaque-token gateway, proxies to GCS via service account; no per-route HTTP timeout.
- `archival-service` / `archiver`: source DBs + an archival store (BigQuery? GCS? — confirm).
- `loadbuilder-backend`: **GCS as primary store** (serialized Java + JSON, optimistic locking via version field) — the only Spring service in the fleet without an RDBMS.

## Cross-cutting concerns

- **`commons:libs` is the fleet's framework-neutral nucleus** after the 2024 Quarkus/Spring split. ~50+ Java services compile against it. Public API stability is load-bearing.
- **`quarkus-pubsub` (29 consumers), `quarkus-extension-persistence` (14 consumers), `quarkus-extension-webclient` (9 consumers), `quarkus-notification-client` (40+ consumers)** are the four fleet-cross-cutting Quarkus extensions. Together they shape the fleet's resilience defaults — see compile-time-edges table in `relations/service-graph.md`.
- **The fleet's REST-client timeout gap is structural, not configurational**: ~30 Quarkus services use MicroProfile's `@RegisterRestClient` (silent-by-default on timeouts; 33 of 36 declarations missing timeouts per `rest-client-registry.md`). The other 9 use this domain's `quarkus-extension-webclient.WebClientImpl` which has `DEFAULT_CONFIG` baseline timeouts. The fix isn't "configure timeouts" — it's "decide the canonical path."
- **The fleet's Pub/Sub retry/DLQ posture is GCP-side, not in-code**: `quarkus-pubsub` NACKs on exception and lets GCP redeliver. Every prod subscription needs `Maximum delivery attempts` + a `Dead letter topic` set in Terraform — verifying that's universal across the ~29 Quarkus consumers is an audit worth running.
- **The pool-size outliers (`notification-backend` 5, `dataone` 4, `public-tracking-backend` 5, `load-bookmark-backend` 4 prod, `location-history-backend` 4, `location-provider` 4, `autoims-backend` 10, `driveaway-backend` 10) are per-repo `application.properties`** — *not* inherited from `quarkus-extension-persistence` or any other shared library. Confirmed in the depth pass. The fleet-wide pool-size right-sizing is a many-line PR sweep, not a one-liner.
- **`archiver` is on Quarkus 2.9.1.Final** (2022) — well behind the 3.20+/3.27+ majority. EOL upgrade candidate.
- **The boundary between `platform` and `infrastructure` is fuzzy** — Go services like `media-proxy`, `api-gateway`, `webhook-relay` could go either way. They're here because they participate in the request path.
- **The single-spa shell + 5+ shared FE packages are central** — a bad release here breaks every micro-frontend simultaneously.

## Open questions / known gaps
- ~~`commons` (Java/Maven) vs. `quarkus-commons` — what's in each?~~ — **resolved** (Phase 4.15): `commons` is framework-neutral (Error codes, retry primitives, MDC keys, DTOs, Datadog/Temporal helpers); `quarkus-commons` is Quarkus-specific (OTel/MDC bridge, structured JSON); `spring-commons` is Spring-specific (`WebClientImpl`, `GlobalExceptionHandler`, `PubSubConsumer` template). 2024 split documented in `commons/README.md`.
- ~~`cube` and `dataone` — names give nothing away.~~ — **resolved**: `cube` is the fleet's ES-read-query microservice (re-domained to `listings-trade` in Phase 4.13); `dataone` is a local vehicle catalog with Caffeine `1400 h` cache + 8 inbound REST edges.
- `crm-workflows` — sounds like it should be a vertical (some kind of sales/CRM domain) but there's no such grouping. May warrant carving out.
- Multiple boilerplate repos — `quarkus-imperative-boilerplate`, `quarkus-k8s-boilerplate`. Fleet may benefit from one canonical boilerplate.
- **Open seam:** `quarkus-extension-webclient` (9 consumers, safe-by-default) vs. `@RegisterRestClient` (~30 consumers, silent-by-default). The fleet hasn't decided which is canonical. The decision drives the REST-client-timeout remediation path.
- **Audit gap:** which prod Pub/Sub subscriptions have `Maximum delivery attempts` + `Dead letter topic` configured? Without that, a perpetually-throwing consumer is an infinite-redelivery condition.

## Related ADRs
- `~/projects/codebase-map/adr/0003-cross-service-db-read-policy.md` — applies to several platform-adjacent shadow callers.
- `~/projects/quarkus-fleet-review-2026-05-07.md` — fleet review touching platform-shared concerns.
- `~/projects/quarkus-rest-client-timeout-anti-pattern.md` — anti-pattern write-up; `quarkus-extension-webclient` is its structural fix.

## Coverage
**21 of 54 shadows are `seed`** as of 2026-05-12 (was 0 at last review, 5 at Phase 4.13, 11 after Phase 4.15, 13 after Phase 4.16, 17 after Phase 4.23, **21 after Phase 4.25**). Newly added in Phase 4.25:

- **`quarkus-data-migration`** — runtime data-migration framework complementing Flyway with Java-typed migrations against the JPA layer (`DataMigration` interface, `DataMigrationVersionEntity` for tracking). **No active fleet consumers detected** — may be intended for future use or imported transitively.
- **`quarkus-extension-firestore-storage`** — `StorageClient` with versioned CRUD + optimistic concurrency + TTL auto-deletion over Firestore. 1 confirmed consumer (`command-executor`). Versioned 3.20.2.3-SNAPSHOT (behind fleet HEAD).
- **`quarkus-extension-bootstrap`** — **template repo** for scaffolding new Ship.Cars Quarkus extensions. Not consumed at runtime; explains the shared "multi-module (runtime + deployment + coverage-report)" layout across all the other extensions.
- **`quarkus-k8s-boilerplate`** — **lightweight single-module** service template. Counterpart to `quarkus-imperative-boilerplate`'s 9-module heavy template. For 5-20-endpoint services, serverless / native-first.

**Quarkus-extension catalog is now COMPLETE**: 14 of 14 Ship.Cars Quarkus extensions / commons / templates are at seed. Full list: `commons`, `quarkus-commons`, `spring-commons`, `shipcars-quarkus-bom`, `models-lib`, `quarkus-notification-client`, `quarkus-pubsub`, `quarkus-extension-persistence`, `quarkus-extension-webclient`, `quarkus-extension-media-proxy`, `quarkus-locationprovider-client`, `quarkus-user-syncer`, `quarkus-auto-reflection`, `quarkus-request-filter`, `quarkus-data-migration`, `quarkus-extension-firestore-storage`, `quarkus-imperative-boilerplate`, `quarkus-k8s-boilerplate`, `quarkus-extension-bootstrap`.

After **Phase 4.26 added 8 shell + FE-package seeds**, coverage was 29/54. **Phase 4.27 added 14 more** (7 remaining frontends + 7 Go/Node services), bringing platform coverage to **43 of 54**:

**Newly seeded frontends (7):**
- **`platform-frontend`** — `@ship-cars/root-config` — the **Loadmate-app single-spa root config**. Contains in-repo parcels (`src/CTMS`, `src/ContractPricing`, `src/ExecutiveDashboard`, `src/Conversations`, `src/DriverChat`) that have **dual-existence with standalone MFE repos** (`contract-pricing-frontend`, `executive-dashboard-frontend`, `chat-frontend`). Active dev path (PR #1835).
- **`ctms-frontend`** — older single-spa-5 MFE with **`@mui/x-data-grid-premium 8.23`** (the only fleet repo using the paid MUI X Premium tier).
- **`settings-frontend`**, **`gallery-frontend`**, **`inspection-requirements-frontend`** — older single-spa-5 MFEs. `gallery-frontend` consumes `media-proxy` access keys; `inspection-requirements-frontend` drives ePOD app behavior.
- **`documentation`** — 3.5-years-stale Grunt-based static-docs site for `docs.ship.cars`. **Archive-candidate.**
- **`website`** — 3.5-years-stale Gatsby 2.x marketing site for `ship.cars`. **Archive-candidate.**

**Newly seeded backends / services (7):**
- **`platform-backend`** — Django+Daphne **Python 3.6** monolith (the original Ship.Cars Loadmate backend). **PR #2780** (highest in catalog) — still actively maintained despite being the migration source for the entire microservice fleet. **Third EOL Python/Spring service alongside `lead-parser` (Spring 2.1.4) and `rateengine` (Django 2.1.7) — but receives the most active commits.**
- **`import-map-deployer`** — Go CLI for managing single-spa import maps; SPOF for fleet-wide MFE deploys.
- **`logging-manager`** — Go service brokering runtime logger-level changes across Spring + Quarkus services.
- **`archival-data-verification`** — Go service comparing source / target DB records during archival migrations. Pairs with `archiver` + `archival-service`.
- **`api-documentation-builder`** — Node tool that combines per-service swagger files + publishes to Readme.com via `rdme`.
- **`internal-api-docs`** — tiny Node Express + swagger-ui-express server consuming `api-documentation-builder`'s output.
- **`internal-api-docs-controller`** — 3-year-stale Go K8s controller watching configmaps for dynamic API-doc paths. **Archive-candidate** if no longer running.

**Phase 4.28 closed the final 11 platform stubs — platform coverage 43 → 54 of 54 (catalog-complete).** Newly seeded in 4.28:

**Backoffice cohort (5):**
- **`backoffice-backend`** (NestJS + TypeORM 0.3) + **`backoffice-frontend`** (**Vite 6 + React 19.2 + pnpm 10** — fleet's newest React major) — the modern Ship.Cars BackOffice. Standalone deployment, separate auth.
- **`uship-backoffice-backend`** (NestJS + TypeORM 0.3) + **`uship-backoffice-frontend`** (**CRA 5 + craco-less + React 18.2** — older stack) — uShip-specific BackOffice sibling. **Stack drift between the two BackOffice fronts** (modern Vite 6 vs deprecated CRA 5).
- **`backoffice-app-ARCHIVED`** — **archived** Python Flask 2.3 predecessor (last commit 2023-07-17).

**Small Quarkus services (6):**
- **`crm-workflows`** (Quarkus 3.27.0) — syncs operational data to **Freshsales CRM**.
- **`company-cleanup-utils`** (Quarkus 3.15.2) — cleans test data across dev/qa/staging.
- **`archival-service`** (Quarkus 3.15.2) — modern data-archival mover; pairs with `archival-data-verification` (Go).
- **`toolbox-service`** (Quarkus 3.15.0) — catch-all for "utility services too small to warrant their own service."
- **`archiver`** (Quarkus 2.9.1.Final — **fleet's oldest active Quarkus**) — legacy archival service; **P1 lifecycle item** alongside `lead-parser`, `rateengine`, `platform-backend`, `notification-orchestrator`. No BOM import. 3-year-stale.
- **`pubsub-exception-handler`** (Quarkus 3.20.2.2) — fleet-wide **DLQ-message capture service** storing undeliverable Pub/Sub messages in Postgres for analysis.

**Platform domain is now catalog-complete: 54 of 54 shadows at seed.**
