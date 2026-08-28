---
repo: trip-planner
path: ~/projects/ship-cars-usa/trip-planner
stack: Java/Quarkus 3.27.5
domain: operations
shape: multi-module (15 poms)
last-synced-commit: ffb50f6f0105de174e6224af7fdffdf33476dc90
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# trip-planner

## What it is
Quarkus 3.27.5 / Java 21 service that **orchestrates freight trip planning, load assignment, and route optimization**. Manages trip lifecycle (`TripStatus`: `ACTIVE → ARCHIVED → COMPLETED`); supports three load types (Posting, Order, Candidate); exposes REST CRUD + plan/route-optimization + stop rearrangement at `/api/v1/trips`. Bridges to the legacy CTMS Django system, reads user/company data from replicated PG, and emits domain events via Pub/Sub for downstream worker-services + db-syncer. Trip capacity is capped at **12 vehicles** (`TripConstants.MAX_NUMBER_OF_VEHICLES = 12`).

## How it fits
- Consumes API of: legacy **CTMS** (Django) via `CtmsClient` (`getOrder`/`getPosting`/`getNegotiations`) — impl `CtmsClientImpl` uses the shared `ship.cars.quarkus.extensions.webclient` `WebClientImpl` + `OidcClient`, reading `quarkus.rest-client.ctms-api.url`; **no `connect-timeout`/`read-timeout` configured** (see Don't-do-here). `location-provider` via `ship-cars-locationclient` 3.28.0 (`quarkus.rest-client.location-provider.url`, also no timeouts). `usermanagement-dtos` 2.7.0 for user shapes.
- Publishes events to: Pub/Sub via `PubSubMessagePublisherImpl` (`PubSubPublisherSync`, with **ordering key** header) — trip topic `trip-planner.pubsub.trip-topic` (`${TRIP_PLANNER_PUBSUB_TRIP_TOPIC}`) and notification topic `ship.cars.notification.topic`. JSON DTOs over Pub/Sub — no schema registry.
- Subscribes to: the **db-syncer** module consumes three subscriptions — `user-subscription-v2`, `company-subscription-v2`, `ctms-subscription` (`db-syncer/.../application.properties:1-3`) — to replicate user/company/CTMS data into local PG. **worker-services** consumes the trip topic for async processing.
- Owns data store: PostgreSQL primary (`quarkus.datasource.jdbc.url=${TRIP_PLANNER_POSTGRESQL_URI}`, blocking JDBC; default reactive datasource disabled) + **two secondary reactive datasources** `usermanagement` and `ctms`, both `reactive.max-size=10`, `health-exclude=true` (replicated read stores). `schema-management.strategy=none`; Flyway + Hibernate ORM with Panache.

## Build / test / run
```
./mvnw clean package -DskipTests
./mvnw quarkus:dev
# 15 poms: root + application, api-services, api-dtos, domain, domain-services,
#          commons, db-entities, db-migration, infra, infra-interfaces,
#          shared-services, worker-services, db-syncer, coverage-report
```

## Key abstractions
- `TripController` — `api-services/.../rest/controller/TripController.java:69` — `/api/v1/trips` CRUD + `/{trip-id}/plan` optimization + `/{trip-id}/postings|orders|candidate` load ops + `/count`.
- `TripFactory` / `Trip` — `domain-services/.../domain/trip/TripFactory.java`, `domain/.../trip/Trip.java` — trip construction + invariant enforcement; capacity `> 0 && <= MAX_NUMBER_OF_VEHICLES` (12) at `TripFactory.java:37-41`, `Trip.java:153`.
- `TripLoadOperationsService` — `domain-services/.../domain/trip/TripLoadOperationsService.java` — load-assignment business rules.
- `PlanGenerator` — `shared-services/.../services/PlanGenerator.java` — route planning + stop sequencing.
- `CtmsClient` / `CtmsClientImpl` — `infra-interfaces/.../ctms/CtmsClient.java`, `infra/.../ctms/CtmsClientImpl.java` — WebClient-based CTMS bridge (OIDC-authenticated).
- `MessagePublisher` / `PubSubMessagePublisherImpl` — `infra-interfaces/.../pubsub/MessagePublisher.java`, `infra/.../pubsub/publisher/impl/PubSubMessagePublisherImpl.java:26` — domain-event publishing with ordering keys.

## Don't-do-here / gotchas
- **`ctms-api` has neither `connect-timeout` nor `read-timeout`** — `application/.../application.properties:38-40` sets only `url`, `follow-redirects`, `max-redirects`. A slow CTMS hangs the trip-planning request path. The `location-provider` rest-client is likewise untimed. **Add both timeouts.** (Canonical anti-pattern: `~/projects/quarkus-rest-client-timeout-anti-pattern.md`.)
- **No transactional outbox for domain-event publishes** — `PubSubMessagePublisherImpl` publishes directly and only logs on failure; a publish-fail after a DB commit silently loses the event. Add an outbox or surface a retry/DLQ policy.
- **Data replicated via db-syncer from CTMS/user/company** — if the syncer lags, local user/company/CTMS reactive stores diverge from source; confirm the reconciliation rule.
- **Two reactive secondary datasources alongside the JDBC primary** — the connection-pool budget is split across two execution models; blocking-on-reactive bugs are harder to debug. Verify under load.
- **Trip capacity = 12 hardcoded** (`TripConstants.MAX_NUMBER_OF_VEHICLES`) — the 11→12→13 assignment edge is worth an explicit test.
- **PlanGenerator scheduling** — no `@Scheduled`+ShedLock observed; confirm plan generation is purely event/request-driven before assuming no multi-replica double-fire.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/posting-backend.md` — trips reference loads/orders.
- `~/projects/codebase-map/repos/loadboard-backend.md` — same legacy CTMS coordination boundary.
- `~/projects/codebase-map/repos/location-provider.md`.
- `~/projects/codebase-map/relations/rest-client-registry.md`.
- `~/projects/quarkus-rest-client-timeout-anti-pattern.md`.
- `~/projects/codebase-map/domains/operations.md`.


<!-- entities-begin -->
## Entities

Auto-generated by `scripts/cluster_entities.py`. Domain classes declared in this repo:

| Class | Kind | Module | Catalog canonical |
|---|---|---|---|
| `CompanyEntity` | jpa | `db-entities` | [Company](../domains/entities/Company.md) |
| `TripEntity` | jpa | `db-entities` | [Trip](../domains/entities/Trip.md) |
| `TripLoadEntity` | jpa | `db-entities` | [Load](../domains/entities/Load.md) |
| `TripSavedSearchUpdateEntity` | jpa | `db-entities` | SavedSearchUpdate |
| `UserEntity` | jpa | `db-entities` | [User](../domains/entities/User.md) |
| `GeoPointEntity` | embedded | `db-entities` | [GpsPosition](../domains/entities/GpsPosition.md) |
| `CityRangeFilter` | dto | `infra-interfaces` | CityRangeFilter |
| `CompanyVo` | dto | `domain` | CompanyVo |
| `CountDto` | dto | `api-dtos` | Count |
| `CreateTripDto` | dto | `api-dtos` | CreateTrip |
| `CreateTripLoadDto` | dto | `api-dtos` | CreateTripLoad |
| `CtmsDbOrderDto` | dto | `db-syncer` | CtmsDbOrder |
| `CtmsDbTripDto` | dto | `db-syncer` | CtmsDbTrip |
| `CtmsGeoPointDto` | dto | `infra-interfaces` | CtmsGeoPoint |
| `CtmsNegotiationDto` | dto | `infra-interfaces` | [Negotiation](../domains/entities/Negotiation.md) |
| `CtmsNegotiationMessageDto` | dto | `shared-services` | CtmsNegotiationMessage |
| `CtmsOfferMessageDto` | dto | `shared-services` | CtmsOfferMessage |
| `CtmsOrderDto` | dto | `infra-interfaces` | CtmsOrder |
| `CtmsOrderMessageDto` | dto | `shared-services` | CtmsOrderMessage |
| `CtmsPostingDto` | dto | `infra-interfaces` | [Posting](../domains/entities/Posting.md) |
| `CtmsPostingMessageDto` | dto | `shared-services` | CtmsPostingMessage |
| `CtmsResultsDto` | dto | `infra-interfaces` | CtmsResults |
| `CtmsTripMessageDto` | dto | `shared-services` | CtmsTripMessage |
| `CtmsVehicleDto` | dto | `infra-interfaces` | [Vehicle](../domains/entities/Vehicle.md) |
| `DateIntervalVo` | dto | `domain` | DateIntervalVo |
| `DateRangeDto` | dto | `api-dtos` | [DateRange](../domains/entities/DateRange.md) |
| `DbCompanyDto` | dto | `db-syncer` | [Company](../domains/entities/Company.md) |
| `DbUserDto` | dto | `db-syncer` | [User](../domains/entities/User.md) |
| `GeoPointDto` | dto | `api-dtos` | [GpsPosition](../domains/entities/GpsPosition.md) |
| `GeoPointVo` | dto | `domain` | GeoPointVo |
| `LegDto` | dto | `api-dtos` | Leg |
| `LegVo` | dto | `domain` | LegVo |
| `LoadAddedToTrip` | dto | `domain` | LoadAddedToTrip |
| `LoadCandidateDto` | dto | `api-dtos` | LoadCandidate |
| `LoadRemovedFromTrip` | dto | `domain` | LoadRemovedFromTrip |
| `LoadUpdateDto` | dto | `shared-services` | LoadUpdate |
| `LocationDto` | dto | `api-dtos` | [Location](../domains/entities/Location.md) |
| `LocationFilter` | dto | `infra-interfaces` | LocationFilter |
| `LocationVo` | dto | `domain` | LocationVo |
| `NegotiationUpdateDto` | dto | `shared-services` | NegotiationUpdate |
| `NegotiationVo` | dto | `domain` | NegotiationVo |
| `OfferDto` | dto | `infra-interfaces` | [Offer](../domains/entities/Offer.md) |
| `Plan` | dto | `shared-services` | Plan |
| `QueryParamsDto` | dto | `infra-interfaces` | QueryParams |
| `RangeDto` | dto | `api-dtos` | Range |
| `RearrangeStopVo` | dto | `domain` | RearrangeStopVo |
| `RouteDto` | dto | `api-dtos` | [Trip](../domains/entities/Trip.md) |
| `RouteOptimizationResult` | dto | `infra-interfaces` | RouteOptimizationResult |
| `RouteVo` | dto | `domain` | RouteVo |
| `SavedSearchDto` | dto | `infra-interfaces` | [SavedSearch](../domains/entities/SavedSearch.md) |
| `SavedSearchParametersVo` | dto | `domain` | SavedSearchParametersVo |
| `SavedSearchVo` | dto | `domain` | SavedSearchVo |
| `Slot` | dto | `shared-services` | Slot |
| `SlotDto` | dto | `api-dtos` | Slot |
| `Spot` | dto | `shared-services` | Spot |
| `SpotDto` | dto | `api-dtos` | Spot |
| `TimeMetaVo` | dto | `domain` | TimeMetaVo |
| `TransferTripDto` | dto | `api-dtos` | TransferTrip |
| `Trip` | dto | `domain` | [Trip](../domains/entities/Trip.md) |
| `TripArchived` | dto | `domain` | Archived |
| `TripCompleted` | dto | `domain` | Completed |
| `TripCreated` | dto | `domain` | Created |
| `TripDeleted` | dto | `domain` | Deleted |
| `TripDto` | dto | `api-dtos` | [Trip](../domains/entities/Trip.md) |
| `TripEmailNotificationSettingsChanged` | dto | `domain` | EmailNotificationSettingsChanged |
| `TripEmailSettingsDto` | dto | `api-dtos` | EmailSettings |
| `TripFilterParameters` | dto | `domain-services` | FilterParameters |
| `TripListDto` | dto | `api-dtos` | List |
| `TripLoadCandidate` | dto | `domain` | LoadCandidate |
| `TripLoadCandidateVo` | dto | `domain` | LoadCandidateVo |
| `TripLoadDto` | dto | `api-dtos` | [Load](../domains/entities/Load.md) |
| `TripLoadListDto` | dto | `api-dtos` | LoadList |
| `TripLoadOrder` | dto | `domain` | [Load](../domains/entities/Load.md) |
| `TripLoadOrderVo` | dto | `domain` | LoadOrderVo |
| `TripLoadPosting` | dto | `domain` | LoadPosting |
| `TripLoadPostingVo` | dto | `domain` | LoadPostingVo |
| `TripLoadUpdateEvent` | dto | `shared-services` | LoadUpdateEvent |
| `TripModified` | dto | `domain` | Modified |
| `TripPlan` | dto | `shared-services` | Plan |
| `TripPubSubDto` | dto | `api-dtos` | [Trip](../domains/entities/Trip.md) |
| `TripRenamed` | dto | `domain` | Renamed |
| `TripSocketNotificationData` | dto | `worker-services` | SocketNotificationData |
| `TripStop` | dto | `shared-services` | Stop |
| `TripStopDto` | dto | `api-dtos` | Stop |
| `TripStopReadDto` | dto | `api-dtos` | Stop |
| `TripStopsDto` | dto | `api-dtos` | Stops |
| `TripSyncDto` | dto | `api-dtos` | Sync |
| `TripSyncedEvent` | dto | `shared-services` | SyncedEvent |
| `TripUpdateDto` | dto | `shared-services` | Update |
| `TripUpdateEvent` | dto | `shared-services` | UpdateEvent |
| `TripUpdateVo` | dto | `domain` | UpdateVo |
| `UpdateTripDto` | dto | `api-dtos` | UpdateTrip |
| `UserDto` | dto | `api-dtos` | [User](../domains/entities/User.md) |
| `UserVo` | dto | `domain` | UserVo |
| `ValueDto` | dto | `api-dtos` | Value |
| `ValuesDto` | dto | `api-dtos` | Values |
| `VcgSpot` | dto | `shared-services` | VcgSpot |
| `RouteEntity` | other | `db-entities` | [Trip](../domains/entities/Trip.md) |
<!-- entities-end -->
