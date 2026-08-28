---
repo: cube
path: ~/projects/ship-cars-usa/cube
stack: Java/Quarkus 3.27.0
domain: listings-trade
shape: multi-module (28 poms)
last-synced-commit: f53ac8487d9ce51e7c686816469f31afc00927e0
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# cube

## What it is
Quarkus 3.27.0 / Java 21 (project `0.6.17-SNAPSHOT`) **Elasticsearch CQRS read-query microservice** — `README.md:13` self-describes it as an "Elastic search read query microservice". This is the **read side** of CQRS: it serves loadboard-posting search, CTMS-orders read/aggregation, and Loadmate (LM) read surfaces from Elasticsearch. **`cube` does NOT write the ES indexes — `syncer` does**; cube only queries them. The single largest multi-module in the fleet (28 poms across the core / loadboard / loadmate / ctms-orders / db-sync / event-listener module trees). Domained `listings-trade` (its primary surface is loadboard search, not generic platform infrastructure).

## How it fits
- Consumes API of: `location-provider` (`quarkus.rest-client.location-provider.url`, `application.properties:78`), `media-proxy` (`quarkus.rest-client.media-proxy.url`, line 92). **Neither client sets `connect-timeout` / `read-timeout`** — same fleet pattern. No `@Retry`/`@CircuitBreaker`/`@Timeout` anywhere in source.
- Publishes events to: Pub/Sub `config.pubsub.search-posting-events-topic` = `${LOADBOARD_PUB_SUB_SEARCH_POSTING_EVENTS_TOPIC}` (env-driven; test topic literal `cube.loadboard.posting.events.search`), gated by `config.pubsub.is-search-posting-events-enabled` (default `true`, lines 97-99). Downstream consumer is `ml-service-listener` (assumed — verify in service-graph). Note: `saved-search-handler` does **not** consume this topic (it reads `ctms-subscription` + `loadboard-fetcher`).
- Subscribes to: **only** user-sync — `config.pubsub.user-subscription` = `${CUBE_BACKEND_PUBSUB_USER_SUBSCRIPTION}` (line 99), handled by `UserSyncConfig` + `UserManagementUserEventListenerImpl` via the Ship.Cars user-syncer extension. (There is **no** CTMS or Loadmate inbound Pub/Sub stream here — the old doc's claim was wrong; CTMS/LM data reaches cube as ES documents written by `syncer`.)
- Owns data store: **none authoritative — cube is a read service.** Reads Elasticsearch (client `co.elastic.clients` / `quarkus-elasticsearch-java-client`, configured purely by env `QUARKUS_ELASTICSEARCH_HOSTS`, not in `application.properties`). Backing PostgreSQL: default datasource (JDBC, `jdbc.max-size=16`, lines 8-9) + named `users` UM datasource (JDBC, no explicit max-size, lines 16-21). Redis: `max-pool-size=10000` / `max-pool-waiting=10000` (lines 41-43) — extreme-outlier pattern shared with `syncer` and `user-activity-tracker`.

## Build / test / run
```
./mvnw clean package -DskipTests
./start-quarkus-dev.sh   # or ./mvnw quarkus:dev
# 28 poms across the module trees: application, configuration, commons, coverage-report,
#   core (core-services, core-dtos, core-resources),
#   loadboard (loadboard-services, loadboard-commons, loadboard-client, loadboard-dtos),
#   loadmate (lm-services, lm-dtos, lm-resources),
#   ctms-orders (ctms-orders-services, ctms-orders-dtos, ctms-orders-resources, ctms-orders-client),
#   db-sync, event-listener, db-entities, db-repositories, db-migration
# ES via docker-compose (Elasticsearch 9.2.1); native supported.
```

## Key abstractions
- Loadboard posting read API — `loadboard/loadboard-services/.../rest/controller/v3/V3PostingsController.java` (`@Path` v3; `GET /{id}`, `/count`, active-negotiation-count). v1/v2/v4 variants + `V3PostingsWebController`, `V3PostingsInternalController`, `V4PostingsWebController`, `QueryController` exist alongside — the read surface is versioned v1→v4.
- CTMS orders read API — `ctms-orders/ctms-orders-resources/.../rest/OrdersController.java` (`GET /{id}/details`, `/count`, `/eta-status/count`) + `V2OrdersController`, `OrdersInternalController`, `OrdersExportController`, `SavedViewController`.
- Loadmate read API — `loadmate/lm-resources/.../rest/controller/{LoadListingController,DashboardController,ContactsController}.java`.
- `LHLogController` — `core/core-resources/.../rest/locationhistory/` — location-history reads; calls `location-provider`.
- Pub/Sub publish path — `loadboard/loadboard-commons/.../services/impl/PubSubMessagePublisherImpl.java:27-38` publishes to the search-posting-events topic; **triggered off the request thread** by `PostingEventsConsumerService` (a Vert.x `@ConsumeEvent(SEARCH_POSTING_EVENT)` bus consumer that skips default searches). DTO `SearchPostingEventPubSubDto` via `SearchPostingEventConverter`.
- `UserSyncConfig` — `db-sync/.../config/UserSyncConfig.java:44` — registers the user-subscription subscriber; feeds `ResyncService`.

## Don't-do-here / gotchas
- **`cube` reads ES; `syncer` writes ES.** Do not add index-write logic here — it will diverge from the syncer-owned write path. A stale/missing search result is almost always a `syncer` indexing issue, not a cube bug. See memory notes `syncer_orders_es_version_check` and `faster_payment_resync_null_trap`.
- **No REST-client timeouts** on `location-provider` / `media-proxy` — `application.properties` sets only `.url`. Same fleet pattern (`relations/rest-client-registry.md`).
- **Search-posting-events publish is decoupled from the HTTP request** (Vert.x event-bus consumer), so it does not block the caller — but there is **no transactional outbox**: an event-bus deliver + publish-fail silently drops the ML signal.
- **Redis pool `max-pool-waiting=10000`** — extreme outlier (with `syncer`, `user-activity-tracker`). Right-size against observed wait metrics.
- **Elasticsearch is on the read path** — query latency couples to ES cluster latency; no fallback to direct-PG read. ES config is env-only (`QUARKUS_ELASTICSEARCH_HOSTS`), not in `application.properties`.
- **Two JDBC datasources (default + `users`)** with separate pools — cross-datasource operations have no distributed-transaction guarantee.
- **Feature-flag-driven filtering** (premium-exclusivity, carrier-verification, company-filtering) — assumed still present but not re-verified this pass; confirm the offline fallback before relying on it.
- **28-pom multi-module** is unusually large; module boundaries should be reviewed for tightness.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/syncer.md` — **writes the ES indexes cube reads** (the CQRS write side) and shares the extreme Redis pool.
- `~/projects/codebase-map/repos/ml-service-listener.md` — assumed consumer of the search-posting-events topic.
- `~/projects/codebase-map/repos/loadboard-backend.md` — write side of loadboard postings (claim/dispatch/negotiate); cube is the read side.
- `~/projects/codebase-map/relations/rest-client-registry.md`.
- `~/projects/codebase-map/relations/media-url-flows.md` — relays CTMS media URLs **verbatim** (hop 4; `OrdersMediaUrlPostProcessor`), signs via the media-proxy client.
- `~/projects/codebase-map/domains/listings-trade.md`.
- Recent (SCP-15099, this HEAD): `faster_payment_enabled` now exposed in v1/v2 posting read DTOs (`loadboard/loadboard-dtos/.../out/v1/V1PostingReadDto.java:153`, `.../out/v2/PostingReadDto.java:157`) via `PostingReadDtoConverter.java:58` — the v3 controller serves the v2 DTO.


<!-- entities-begin -->
## Entities

Auto-generated by `scripts/cluster_entities.py`. Domain classes declared in this repo:

| Class | Kind | Module | Catalog canonical |
|---|---|---|---|
| `SavedViewsEntity` | jpa | `db-entities` | SavedViews |
| `UserEntity` | jpa | `db-entities` | [User](../domains/entities/User.md) |
| `ActivityLogDto` | dto | `ctms-orders` | [ActivityLog](../domains/entities/ActivityLog.md) |
| `AggregationRequestDto` | dto | `ctms-orders` | Aggregation |
| `AggregationResultDto` | dto | `ctms-orders` | AggregationResult |
| `AlongRouteFilter` | dto | `loadboard` | AlongRouteFilter |
| `AlongRouteLocationCoordinates` | dto | `loadboard` | AlongRouteLocationCoordinates |
| `AttachmentDto` | dto | `ctms-orders` | [Attachment](../domains/entities/Attachment.md) |
| `BodyFilterDto` | dto | `loadboard` | BodyFilter |
| `BooleanColumnFilterDto` | dto | `ctms-orders` | BooleanColumnFilter |
| `ByIdsFilter` | dto | `loadboard` | ByIdsFilter |
| `ByIdsFilter` | dto | `loadboard` | ByIdsFilter |
| `ByIdsFilterDto` | dto | `loadboard` | ByIdsFilter |
| `CityFilter` | dto | `loadboard` | CityFilter |
| `CityFilterDto` | dto | `loadboard` | CityFilter |
| `CityRangeFilterDto` | dto | `loadboard` | CityRangeFilter |
| `ColumnFilter` | dto | `ctms-orders` | ColumnFilter |
| `ColumnFilters` | dto | `ctms-orders` | ColumnFilters |
| `CompaniesResultDto` | dto | `loadboard` | CompaniesResult |
| `CompanyDto` | dto | `loadboard` | [Company](../domains/entities/Company.md) |
| `CompanyInfoReadDto` | dto | `loadboard` | CompanyInfo |
| `CompanySearchDto` | dto | `loadboard` | CompanySearch |
| `ContactFilter` | dto | `loadmate` | ContactFilter |
| `ContactSearchDto` | dto | `loadmate` | ContactSearch |
| `Coordinates` | dto | `loadboard` | [GpsPosition](../domains/entities/GpsPosition.md) |
| `CoordinatesDto` | dto | `core` | [GpsPosition](../domains/entities/GpsPosition.md) |
| `CtmsCustomFieldsDocumentDto` | dto | `ctms-orders` | CtmsCustomFieldsDocument |
| `CtmsOfferActivityLogReadDto` | dto | `loadboard` | CtmsOfferActivityLog |
| `CustomFieldFilter` | dto | `ctms-orders` | CustomFieldFilter |
| `DamageEntryDto` | dto | `ctms-orders` | DamageEntry |
| `DashboardLoadFilterDto` | dto | `loadmate` | DashboardLoadFilter |
| `DateColumnFilterDto` | dto | `ctms-orders` | DateColumnFilter |
| `DateFilter` | dto | `ctms-orders` | DateFilter |
| `EtaStatusCountsDto` | dto | `ctms-orders` | EtaStatusCounts |
| `ExtraObjectDto` | dto | `ctms-orders` | ExtraObject |
| `FieldSortOrder` | dto | `commons` | FieldSortOrder |
| `GeoPointDto` | dto | `ctms-orders` | [GpsPosition](../domains/entities/GpsPosition.md) |
| `GeoPointReadDto` | dto | `loadboard` | [GpsPosition](../domains/entities/GpsPosition.md) |
| `GeoPointReadDto` | dto | `core` | [GpsPosition](../domains/entities/GpsPosition.md) |
| `GeoServiceImpl` | dto | `loadboard` | GeoServiceImpl |
| `GridMonetizationRestriction` | dto | `ctms-orders` | GridMonetizationRestriction |
| `GroupPaginationDto` | dto | `ctms-orders` | GroupPagination |
| `ImageDto` | dto | `ctms-orders` | Image |
| `InspectionConfigurationDto` | dto | `ctms-orders` | InspectionConfiguration |
| `LabelDto` | dto | `loadboard` | Label |
| `LoadLegFilter` | dto | `loadmate` | LoadLegFilter |
| `LoadLegSearchDto` | dto | `loadmate` | LoadLegSearch |
| `LoadLocationLogReadDto` | dto | `core` | LoadLocationLog |
| `LocationDto` | dto | `core` | [Location](../domains/entities/Location.md) |
| `LocationFilter` | dto | `loadboard` | LocationFilter |
| `LocationFilterDto` | dto | `loadboard` | LocationFilter |
| `M22DamageDto` | dto | `ctms-orders` | M22Damage |
| `NegotiationReadDto` | dto | `loadboard` | [Negotiation](../domains/entities/Negotiation.md) |
| `NumericColumnFilterDto` | dto | `ctms-orders` | NumericColumnFilter |
| `NumericFilter` | dto | `ctms-orders` | NumericFilter |
| `OfferReadDto` | dto | `loadboard` | [Offer](../domains/entities/Offer.md) |
| `Order` | dto | `loadboard` | Order |
| `OrderDetailsBasicDto` | dto | `ctms-orders` | OrderDetailsBasic |
| `OrderDetailsDto` | dto | `ctms-orders` | OrderDetails |
| `OrderListDto` | dto | `ctms-orders` | OrderList |
| `OrdersBodyFilterDto` | dto | `ctms-orders` | OrdersBodyFilter |
| `OrdersCountDto` | dto | `ctms-orders` | OrdersCount |
| `OrdersCountResultDto` | dto | `ctms-orders` | OrdersCountResult |
| `OrdersFilter` | dto | `ctms-orders` | OrdersFilter |
| `OrdersGroupByDto` | dto | `ctms-orders` | OrdersGroupBy |
| `OrdersQueryFilterDto` | dto | `ctms-orders` | OrdersQueryFilter |
| `OrdersResultDto` | dto | `ctms-orders` | OrdersResult |
| `OrdersRowGroupDto` | dto | `ctms-orders` | OrdersRowGroup |
| `OrdersRowGroupingQuery` | dto | `ctms-orders` | OrdersRowGroupingQuery |
| `OrdersRowGroupingRequestDto` | dto | `ctms-orders` | OrdersRowGrouping |
| `OrdersRowGroupingResultDto` | dto | `ctms-orders` | OrdersRowGroupingResult |
| `OrdersSearchCriteria` | dto | `ctms-orders` | OrdersSearchCriteria |
| `Pageable` | dto | `loadmate` | Pageable |
| `PageableDto` | dto | `commons` | Pageable |
| `PostingReadDto` | dto | `loadboard` | [Posting](../domains/entities/Posting.md) |
| `PostingVehicleReadDto` | dto | `loadboard` | PostingVehicle |
| `PostingsCountDto` | dto | `loadboard` | PostingsCount |
| `PostingsFilter` | dto | `loadboard` | PostingsFilter |
| `PostingsFilterDto` | dto | `loadboard` | PostingsFilter |
| `PostingsResultDto` | dto | `loadboard` | PostingsResult |
| `PostingsWithActiveNegotiationsCountDto` | dto | `loadboard` | PostingsWithActiveNegotiationsCount |
| `QueryFilter` | dto | `loadboard` | QueryFilter |
| `QueryFilterDto` | dto | `loadboard` | QueryFilter |
| `RangeFilter` | dto | `loadboard` | RangeFilter |
| `RedisCacheServiceImpl` | dto | `commons` | RedisCacheServiceImpl |
| `Route` | dto | `loadboard` | [Trip](../domains/entities/Trip.md) |
| `SavedView` | dto | `ctms-orders` | SavedView |
| `SavedViewDto` | dto | `ctms-orders` | SavedView |
| `SavedViewRequestDto` | dto | `ctms-orders` | SavedView |
| `SavedViewTemplate` | dto | `ctms-orders` | SavedViewTemplate |
| `SavedViewsResultDto` | dto | `ctms-orders` | SavedViewsResult |
| `SearchPostingCriteriaDto` | dto | `loadboard` | SearchPostingCriteria |
| `SearchPostingEvent` | dto | `loadboard` | SearchPostingEvent |
| `SearchPostingEventPubSubDto` | dto | `loadboard` | SearchPostingEvent |
| `Shape` | dto | `loadboard` | Shape |
| `SpecificationDto` | dto | `ctms-orders` | [VehicleSpecification](../domains/entities/VehicleSpecification.md) |
| `SpecificationReadDto` | dto | `loadboard` | [VehicleSpecification](../domains/entities/VehicleSpecification.md) |
| `SpecificationsDto` | dto | `ctms-orders` | [VehicleSpecification](../domains/entities/VehicleSpecification.md) |
| `SpecificationsReadDto` | dto | `loadboard` | [VehicleSpecification](../domains/entities/VehicleSpecification.md) |
| `StringColumnFilterDto` | dto | `ctms-orders` | StringColumnFilter |
| `StringFilter` | dto | `ctms-orders` | StringFilter |
| `TripDto` | dto | `ctms-orders` | [Trip](../domains/entities/Trip.md) |
| `TripReadDto` | dto | `loadboard` | [Trip](../domains/entities/Trip.md) |
| `UserAppContext` | dto | `commons` | UserAppContext |
| `UserSyncDto` | dto | `db-sync` | UserSync |
| `V1BodyFilterDto` | dto | `loadboard` | BodyFilter |
| `V1NegotiationReadDto` | dto | `loadboard` | [Negotiation](../domains/entities/Negotiation.md) |
| `V1OfferReadDto` | dto | `loadboard` | [Offer](../domains/entities/Offer.md) |
| `V1PostingReadDto` | dto | `loadboard` | [Posting](../domains/entities/Posting.md) |
| `V1PostingsFilterDto` | dto | `loadboard` | PostingsFilter |
| `V1PostingsResultDto` | dto | `loadboard` | PostingsResult |
| `V1QueryFilterDto` | dto | `loadboard` | QueryFilter |
| `VehicleDto` | dto | `ctms-orders` | [Vehicle](../domains/entities/Vehicle.md) |
| `VehicleListDto` | dto | `ctms-orders` | VehicleList |
| `VehicleOperableSortOrder` | dto | `ctms-orders` | VehicleOperableSortOrder |
| `ExternallySyncedBaseEntity` | other | `db-entities` | lySyncedBase |
<!-- entities-end -->
