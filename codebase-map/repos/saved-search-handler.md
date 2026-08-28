---
repo: saved-search-handler
path: ~/projects/ship-cars-usa/saved-search-handler
stack: Java/Quarkus 3.27.5
domain: listings-trade
shape: multi-module (10 poms)
last-synced-commit: 991c608434e3799f05df711cb01fc836608544db
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# saved-search-handler

## What it is
Quarkus 3.27.5 / Java 21 service (groupId `ship.cars.search`, version `1.0.1`) that **matches incoming loadboard postings against user-saved search filters** using Elasticsearch **percolate** queries (reverse-index: the saved queries are indexed, each new posting is matched against them). Buffers `post_to_loadboard` load events into an in-memory queue, batch-runs percolate, then emits per-user email notifications. Sister to `load-recommender` — same notification surface, different source (user-defined filters here vs. ML there); the two got parallel `preferred_carrier` fixes (SCP-15132 / SCP-15133). (The sisterhood is a fleet fact, not stated in this repo's own docs.)

## How it fits
- Consumes API of: **`loadboard-fetcher`** (NOT `loadboard-backend` — the old doc was wrong) via `LoadboardFetcherSyncServiceImpl.java:33-35`, calling `/api/loadboard/v2/query` (`RequestConfig.java:37`); URL from `loadboard-fetcher.base-url`/`.port` (`application.properties:93-94`). Outbound HTTP uses the Ship.Cars `WebClientImpl` extension — **no `quarkus.rest-client.*` and no connect/read timeout configured** (no MP REST clients in this repo).
- Publishes events to: Pub/Sub `ship.cars.notification.topic` = `${NOTIFICATIONS_TOPIC}` (email dispatch, via the notification extension), `sent-emails-topic` (via `NotificationServiceImpl.java:398`), `sync-topic` (saved-search ES-index state, via `EsSavedSearchSyncServiceImpl.java:71`).
- Subscribes to: Pub/Sub `ctms-subscription` (load + `companylabel` events → `CtmsPubSubAckReplyConsumer`), `user-subscription-v2` (→ `UserPubSubListener`), `company-subscription` (→ `CompanyPubSubListener`, via `db-syncer`).
- Owns data store: three PostgreSQL datasources — default/main, `users`, `ctms` (`application.properties:11-22`, **no `max-size` pool sizing set**); **Elasticsearch** for percolate queries (`es.query-size=10000` hardcoded, line 75; ES URL env-driven).

## Build / test / run
```
./mvnw clean package -DskipTests
./mvnw quarkus:dev
# 10 poms (root + 9 modules): configuration, db-entities, api-services, application,
#   coverage-report, db-migration, api-dtos, commons, db-syncer
```

## Key abstractions
- `SavedSearchServiceImpl` — `api-services/.../services/impl/SavedSearchServiceImpl.java` — transactional CRUD over saved searches; validation.
- `CtmsPubSubAckReplyConsumer` — `api-services/.../infra/CtmsPubSubAckReplyConsumer.java` — consumes `ctms-subscription` (line 45); routes `post_to_loadboard` load events to `LoadEventProcessor.addEventForProcessing` (line 80) and `companylabel` events to the preferred_carrier gate (see gotchas).
- `LoadEventProcessor` — `api-services/.../services/impl/LoadEventProcessor.java` — internal queue of load events; flusher runs the percolate batch.
- `EsSearchServiceImpl` / `EsSavedSearchSyncServiceImpl` — `api-services/.../services/impl/` — Elasticsearch percolate execution + saved-search index-sync.
- `NotificationServiceImpl` — `api-services/.../services/impl/NotificationServiceImpl.java` — private-load notification gate (line 220) + publishes to `sent-emails-topic`.
- `SavedSearchNotificationSenderImpl` — `api-services/.../services/impl/` — builds/sends the matched-user notifications.

## Don't-do-here / gotchas
- **preferred_carrier vs. verified naming trap (SCP-15132, this HEAD).** Private-load notifications now gate on the company label **`preferred_carrier`**, not `verified`. Two sites: label-ingestion `CtmsPubSubAckReplyConsumer.java` (constant `PREFERRED_CARRIER_KEY="preferred_carrier"` line 35; `preferredCarrier` check line 113; `setVerifiedBy` line 117) and the notification gate `NotificationServiceImpl.java:217-220` (`if (!isPreferredCarrier && !isInPostedToCarriers) { skip }`). The table (`shipper_verified_carriers`), entity (`ShipperVerifiedCarrierEntity`), and methods (`isCarrierVerifiedByShipper`/`setVerifiedBy`) still carry legacy "verified" names but hold the **preferred_carrier** relation (see code comment `CtmsPubSubAckReplyConsumer.java:115-116`). SQL sync `db-syncer/.../fetch-shipper-verified-carriers.sql` now filters `(l.labels ->> 'preferred_carrier')::boolean IS TRUE`. Ties to memory note `scp14054_preferred_carrier_label_mismatch` — this is the fix side.
- **Talks to `loadboard-fetcher`, not `loadboard-backend`.** Don't route saved-search parameter fetches at loadboard-backend.
- **Elasticsearch `query-size=10000` hardcoded** (`application.properties:75`) — memory pressure if one load matches a wide population; no pagination/overflow handling.
- **Three datasources with no configured `max-size`** — pools fall back to defaults; watch all three under load.
- **No REST-client timeouts** on the loadboard-fetcher call (same fleet pattern; `relations/rest-client-registry.md`).
- **Prod Pub/Sub subscription names are pure `${ENV}` with no fallback** — a missing env var yields an empty subscription binding, not a build error. Only the `%test` profile has literal defaults.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/loadboard-fetcher.md` — actual saved-search parameter source (query API).
- `~/projects/codebase-map/repos/load-recommender.md` — sister service (ML-driven; got the parallel SCP-15133 preferred_carrier fix).
- `~/projects/codebase-map/repos/notification-orchestrator.md` — email-channel sink.
- `~/projects/codebase-map/domains/listings-trade.md`.


<!-- entities-begin -->
## Entities

Auto-generated by `scripts/cluster_entities.py`. Domain classes declared in this repo:

| Class | Kind | Module | Catalog canonical |
|---|---|---|---|
| `CompanyEntity` | jpa | `db-entities` | [Company](../domains/entities/Company.md) |
| `SavedSearchEntity` | jpa | `db-entities` | [SavedSearch](../domains/entities/SavedSearch.md) |
| `ShipperVerifiedCarrierEntity` | jpa | `db-entities` | ShipperVerifiedCarrier |
| `UserEntity` | jpa | `db-entities` | [User](../domains/entities/User.md) |
| `CityFilter` | dto | `api-dtos` | CityFilter |
| `CityRangeFilter` | dto | `api-dtos` | CityRangeFilter |
| `CompanyLabelDto` | dto | `api-dtos` | CompanyLabel |
| `CompanyLabelSyncDto` | dto | `db-syncer` | CompanyLabelSync |
| `ConstantScoreQuery` | dto | `api-dtos` | ConstantScoreQuery |
| `EsPercolateQueryResponse` | dto | `api-dtos` | EsPercolateQuery |
| `EsQueryModel` | dto | `api-dtos` | EsQuery |
| `Fields` | dto | `api-dtos` | Fields |
| `Filter` | dto | `api-dtos` | [Filter](../domains/entities/Filter.md) |
| `Hit` | dto | `api-dtos` | Hit |
| `HitsData` | dto | `api-dtos` | HitsData |
| `LoadEvent` | dto | `api-services` | LoadEvent |
| `PercolateQuery` | dto | `api-dtos` | PercolateQuery |
| `Query` | dto | `api-dtos` | Query |
| `SavedSearch` | dto | `commons` | [SavedSearch](../domains/entities/SavedSearch.md) |
| `SavedSearchDto` | dto | `api-dtos` | [SavedSearch](../domains/entities/SavedSearch.md) |
| `SavedSearchListDto` | dto | `api-dtos` | SavedSearchList |
| `SavedSearchMatch` | dto | `api-services` | SavedSearchMatch |
| `SavedSearchSyncDto` | dto | `api-dtos` | SavedSearchSync |
| `SavedSearchesCountDto` | dto | `api-dtos` | SavedSearchesCount |
| `SearchDocument` | dto | `api-services` | SearchDocument |
| `SentEmailDto` | dto | `api-dtos` | SentEmail |
| `SyncSavedSearchCommand` | dto | `api-services` | SyncSavedSearchCommand |
| `TotalHitsData` | dto | `api-dtos` | TotalHitsData |
| `UmDbCompanyDto` | dto | `db-syncer` | UmDbCompany |
| `UmDbUserDto` | dto | `db-syncer` | UmDbUser |
| `User` | dto | `commons` | [User](../domains/entities/User.md) |
<!-- entities-end -->
