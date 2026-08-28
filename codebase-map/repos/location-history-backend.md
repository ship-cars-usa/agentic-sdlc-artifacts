---
repo: location-history-backend
path: ~/projects/ship-cars-usa/location-history-backend
stack: Java/Quarkus 3.27.5
domain: operations
shape: multi-module (11 poms)
last-synced-commit: 764f7672606d088afb3380b24b86e080ddfb4efd
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# location-history-backend

## What it is
Quarkus 3.27.5 / Java 21 service that **owns driver + load location tracking and history** for active shipments. Ingests carrier-LB platform (TMS) location events via Pub/Sub, persists driver / load location state to PostgreSQL (using a custom Hibernate `UserType` over the Postgres `POINT`/`PGpoint` geometry), exposes REST APIs for location-history queries, and re-publishes location updates to two downstream Pub/Sub topics. Part of the operations domain; one of the PG sources `syncer` reads directly (shadow-caller edge under ADR-0003 — cross-repo claim, not enforced in this repo).

## How it fits
- Consumes API of: none. No outbound REST clients — a repo-wide grep for `@RegisterRestClient` / `connect-timeout` / `read-timeout` returns zero. Integrations are Pub/Sub (via the shared `ship.cars.quarkus.extensions.pubsub` extension) plus websocket notifications.
- Publishes events to: Pub/Sub **`carrierlb.events`** (config `locationhistory.config.carrierlb-topic`, e.g. `cars.ship.dev.carrierlb.events`) and **`lh-load-location-log.events`** (config `load-location-log-topic`, e.g. `cars.ship.dev.lh-load-location-log.events`), both via `PubSubPublisher` → `PubSubPublisherSync`. JSON DTOs over Pub/Sub — no schema registry. NOTE: `SocketNotificationsPublisher` does NOT publish to a Pub/Sub topic — it sends a websocket via `NotificationClient` (event `locationTrackingEvent`) and its only caller is currently commented out (`PlatformEventsListener.java:162`, pending SCP-9477), so it is effectively dormant. The `ship.cars.notification.topic=...cars.ship.dev.notification` property is unreferenced by the publishers.
- Subscribes to: Pub/Sub **only the `carrierlb.events` topic**, via subscription `carrier-tms-subscription` (`...carrierlb.events-location-history-...-sub`) consumed by `PlatformEventsListener`. It does NOT subscribe to `lh-load-location-log.events` (publish-only here). Consumers globally gated by `ship.cars.pubsub.consumers-enabled`.
- Owns data store: PostgreSQL. Tables: `driver_location_sharing_state`, `load_location_sharing_state`, `driver_locations`, `load_locations` / `load_location_logs`, `vehicles`. Custom `PointType` maps `org.postgresql.geometric.PGpoint`. `schema-management.strategy=none` (Flyway-managed).

## Build / test / run
```
./mvnw clean package -DskipTests
./mvnw quarkus:dev            # start-quarkus-dev.sh
# 11 poms: root + application, services, db-entities, db-migration, api-dtos,
#          commons, configuration, resources, repositories, coverage-report
```

## Key abstractions
- `PlatformEventsListener` — `services/.../services/listeners/PlatformEventsListener.java:31,47` — carrier-LB/TMS Pub/Sub subscriber (`PubSubConsumerBlocking`); applies incoming location to load/driver sharing state.
- `PubSubPublisher` — `services/.../services/publishers/PubSubPublisher.java:19,42` — publishes to carrierlb + lh-load-location-log topics (direct, no outbox).
- `SocketNotificationsPublisher` — `services/.../services/publishers/SocketNotificationsPublisher.java` — websocket push via `NotificationClient` (currently dormant, caller commented out).
- `DriverLocationSharingStateServiceImpl` — `services/.../services/impl/DriverLocationSharingStateServiceImpl.java` — driver sharing lifecycle + builds/publishes the Pub/Sub messages (`publishMessages` ~L183).
- `LoadLocationLogServiceImpl` / `LoadLocationSharingStateServiceImpl` — `services/.../services/impl/` — load/vehicle location-log reads; sharing-state updates + `expireOldLoads()`.
- `PointType` — `db-entities/.../entities/PointType.java:13` — custom Hibernate `UserType<PGpoint>`.
- REST resources — `resources/.../rest/` — v1 `DriverLocationResource` (`@Path("/driver")`, ingestion `POST /{driver_id}/locations`), `LocationHistoryResource` (`/history`, GET reads), `LoadLocationSharingStateResource` (`/load/state`), `ActionResource` (`/actions`, `POST /expire`); v2 `V2DriverLocationResource`/`V2LoadLocationResource`; `LocationHistoryInternalResource` (`/internal/history`). Base namespace `/location-history`.

## Don't-do-here / gotchas
- **`quarkus.datasource.jdbc.max-size=4` in prod (16 in dev)** — extreme-outlier pool, no `%prod` override in the committed properties (prod uses base `=4`). Same pattern flagged for `public-tracking-backend` / `load-bookmark-backend`; add to the right-sizing sweep in `data-stores.md`.
- **No transactional outbox** — `PubSubPublisher` publishes directly. A DB-commit-then-publish-fail silently loses the downstream location event (carrierlb / lh-load-location-log consumers stay stale).
- **Ingestion is NOT the `/api/location_tracking/history` endpoint** — that JWT self-only driver-app path lives in `platform-backend` (Django). This service's ingestion is `POST /location-history/driver/{driver_id}/locations`. No `@RolesAllowed` / `@Authenticated` / JWT-self check exists anywhere in `src/main` — authz is assumed to be enforced upstream (gateway / network); confirm before treating any endpoint as protected.
- **v2 `updateDriverLocationHistory` is a stub** (`V2DriverLocationResource.java:197` — `// TODO: implement it`). Don't rely on the v2 history-write path.
- **Custom `PointType`** ties this service to PostgreSQL/PGpoint; a DB-engine migration would require rewriting the type.
- **Deprecated leftovers still present** — `LoadDeprecated` (a `@RegisterForReflection` `@Deprecated(forRemoval=true)` POJO, not a JPA entity) plus `*ServiceDeprecated` interfaces. Flag for removal.
- **Pub/Sub message contract is the de-facto API** — no outbound REST means an upstream carrier-LB schema change can silently break consumption; treat the DTO contract as a versioned interface.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/syncer.md` — direct reader of this PG (cross-repo edge).
- `~/projects/codebase-map/relations/db-contracts/syncer--multi-source.md` — contract draft.
- `~/projects/codebase-map/relations/media-url-flows.md` / `location-ingestion` memory — GPS ingestion is driver-app-only via platform-backend; this service re-publishes to carrierlb.events + lh-load-location-log.events.
- `~/projects/codebase-map/domains/operations.md`.


<!-- entities-begin -->
## Entities

Auto-generated by `scripts/cluster_entities.py`. Domain classes declared in this repo:

| Class | Kind | Module | Catalog canonical |
|---|---|---|---|
| `DriverLocationSharingStateEntity` | jpa | `db-entities` | DriverLocationSharingState |
| `DriverLocationsEntity` | jpa | `db-entities` | DriverLocations |
| `LoadLocationLogEntity` | jpa | `db-entities` | LoadLocationLog |
| `LoadLocationSharingStateEntity` | jpa | `db-entities` | LoadLocationSharingState |
| `VehicleEntity` | jpa | `db-entities` | [Vehicle](../domains/entities/Vehicle.md) |
| `CoordinatesDto` | dto | `api-dtos` | [GpsPosition](../domains/entities/GpsPosition.md) |
| `DriverIdsRequestDto` | dto | `api-dtos` | DriverIds |
| `DriverLocationDto` | dto | `api-dtos` | DriverLocation |
| `DriverLocationRequestDto` | dto | `api-dtos` | DriverLocation |
| `DriverLocationSharingStateDto` | dto | `api-dtos` | DriverLocationSharingState |
| `EventDto` | dto | `api-dtos` | — |
| `GetLocationSharingStatesDto` | dto | `api-dtos` | GetLocationSharingStates |
| `LoadDeprecated` | dto | `db-entities` | LoadDeprecated |
| `LoadLocationLogMsgPubSubDto` | dto | `api-dtos` | LoadLocationLogMsg |
| `LoadLocationSharingState` | dto | `api-dtos` | LoadLocationSharingState |
| `LoadLocationSharingStateDto` | dto | `api-dtos` | LoadLocationSharingState |
| `LoadWithVehiclesLocationDto` | dto | `api-dtos` | LoadWithVehiclesLocation |
| `LocationDto` | dto | `api-dtos` | [Location](../domains/entities/Location.md) |
| `LocationResponseDto` | dto | `api-dtos` | [Location](../domains/entities/Location.md) |
| `MessageDto` | dto | `api-dtos` | [Message](../domains/entities/Message.md) |
| `SocketEventMessageDto` | dto | `api-dtos` | SocketEventMessage |
| `V2LocationDto` | dto | `api-dtos` | [Location](../domains/entities/Location.md) |
| `VehicleLocationGroupDto` | dto | `api-dtos` | VehicleLocationGroup |
<!-- entities-end -->
