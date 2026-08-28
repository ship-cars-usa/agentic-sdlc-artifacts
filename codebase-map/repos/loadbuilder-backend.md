---
repo: loadbuilder-backend
path: ~/projects/ship-cars-usa/loadbuilder-backend
stack: Java/Spring Boot 3.2.12
domain: listings-trade
shape: multi-module (16 poms)
last-synced-commit: 11f4ca0f35f463e6e79f1ae29ba622527ae841ac
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# loadbuilder-backend

## What it is
Spring Boot 3.2.12 / Java 21 service that **builds and optimizes vehicle shipment loads**. Two deployables in one repo: **`api-app`** (`LoadBuilderApiApp`, runtime port 7065 — overrides the yaml default 8080) exposes REST for suggest/build/order/rate; **`worker-app`** (`LoadBuilderWorkerApp`) runs long-running async jobs from Pub/Sub. DDD: aggregate root `SuggestedLoadsJob` with a state machine, `{Entity}{Action}Event` domain events, repository pattern. **Unusual datastore**: persists all entity state (jobs, rates, loads, orders) to **Google Cloud Storage objects — now serialized as JSON via Jackson** (switched from raw Java serialization, commit `3f62206`), not PostgreSQL. Optimistic locking via a `version` field on `StorageEntity`. There is **no JPA/JDBC/Postgres/Flyway on the classpath at all** — a genuinely SQL-less service.

## How it fits
- Consumes API of: `posting-backend` (`postingService.internalBaseUrl` → `/internal/v4/standalone-load-legs/from-builder`), `inventory-backend` (`/api/inventory/v1/units`), `quote-manager-backend` (`quoteManagerService` — providers, booking-details, order-with-quote-selected), `notification-backend` (via `notification-client` 1.2.0 + notification pubsub topic), `attachment-backend` (`attachmentService.base-url`), `media-proxy` (`mediaproxy.client.base-uri`, using the `mediaproxy:spring-client` extension), `impersonator` (`impersonatorUrl`). Timeouts inherit `spring-commons.WebClientImpl` defaults; **no explicit per-client `connect-timeout`/`read-timeout` set here**. Dep versions (root `pom.xml`): posting 1.50.0, inventory 2.18.0, attachment-dtos 2.3.0, contract-pricing-dtos 1.3.0, notification-client 1.2.0, spring-commons 3.28.0.
- Publishes events to: Pub/Sub `config.gcp.pubsub.topics.worker` (API → Worker job-request), `config.gcp.pubsub.topics.notification` (notification events) — via `InfraPubSubPublisherImpl`.
- Subscribes to: Pub/Sub `config.gcp.pubsub.subscriptions.worker` (job consumers) + `config.gcp.pubsub.subscriptions.quoteManagerNotifications`.
- Owns data store: **Google Cloud Storage as primary store** — `config.storage.dbBucket=${CONFIG_DB_BUCKET}` (entity state) + `mediaBucket=${CONFIG_MEDIA_BUCKET}` (files), `config-external.yaml:49-51`. JSON blobs. Optimistic-locking via `version`. **No SQL.**

## Build / test / run
```
./mvnw clean package -DskipTests
./mvnw spring-boot:run -pl api-app       # port 7065 (actuator 17065)
./mvnw spring-boot:run -pl worker-app
# 16 poms (root + 15 modules): api-enums, domain, configs, db-entities, test-commons,
#   infra-interfaces, infra, shared-services, api-dtos, api-services, api-app,
#   worker-dtos, worker-services, worker-app, coverage-report
# (there is NO `commons` and NO `db-migration` module — old doc listed both wrongly)
```

## Key abstractions
- `StorageClientImpl` — `infra/.../infra/storage/impl/StorageClientImpl.java` — GCS read/write (real `com.google.cloud.storage` SDK) with optimistic locking + retry-on-transient. Interface `StorageClient` in `infra-interfaces`.
- `StorageEntity` base — `infra-interfaces/.../infra/storage/dtos/StorageEntity.java` — `version` field + key sanitization. `db-entities` holds ~18 `*DbEntity`/`*DbEmbedded` GCS storage models (LoadsDbEntity, RatesDbEntity, ActiveJobDbEntity, JobStatusDbEntity, …).
- REST controllers — `api-services/.../rest/{SuggestLoads,BuildLoads,OrdersCreation,Rates}Controller.java` (+ `AppController`, `CronsController`, `RootController`).
- `domain/` — aggregates, VOs, domain events (no infra deps).
- Worker consumers — `worker-services/.../worker/application/`: `rates/RatesJobMsgConsumerImpl` (worker sub), `order/OrdersCreationMsgConsumerImpl` (worker sub), `rates/QuoteManagerNotificationMsgConsumer` (quoteManagerNotifications sub), `health/WorkerPubSubPingJobConsumer`.
- `InfraPubSubPublisherImpl` — `infra/.../pubsub/impl/` — publishes domain events to the worker/notification topics.

## Don't-do-here / gotchas
- **GCS-as-database means no relational queries.** Listings/filtering require app-level prefix-scan + in-memory filter — anything beyond key-prefix lookup is O(N). No secondary index.
- **No row-level locking**, only optimistic `version` checks. Concurrent updates race; the loser must re-fetch and retry.
- **JSON-serialization coupling** — domain-model field renames can break deserialization of objects already in GCS. `JacksonConfig`/`JobKeyModule` give some backward compatibility, but forward/backward compat still needs explicit testing.
- **`db-entities` is NOT vestigial** — it holds the live GCS storage models. (Old doc called it empty; corrected.) `db-migration` does not exist.
- **No ShedLock.** (Old doc claimed ShedLock is in play — it is not.) There are two plain `@Scheduled` jobs with no distributed locking: `api-services/.../worker/WorkerPingService.java:31` (PT30S) and `worker-services/.../build/ProcessBuildLoadsStatusUpdatesEventHandler.java:56` (PT15S). If more than one instance runs, these double-fire.
- **REST-client timeouts inherited from `spring-commons.WebClientImpl`** — same fleet pattern; no per-client overrides here.
- **Pub/Sub message ordering not guaranteed** — worker job-state transitions need idempotency + replay-tolerance.
- **Dual-app deploy** — every release moves both `api-app` and `worker-app`; version-skew makes API↔Worker message-schema compatibility the failure mode.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/posting-backend.md` — load-creation downstream.
- `~/projects/codebase-map/repos/inventory-backend.md` — unit lookup.
- `~/projects/codebase-map/repos/quote-manager-backend.md` — rate + order endpoints.
- `~/projects/codebase-map/repos/spring-commons.md` — shared WebClient/PubSub.
- `~/projects/codebase-map/relations/data-stores.md` — fleet-unique GCS-as-database row.
- `~/projects/codebase-map/domains/listings-trade.md`.
- Recent (LITE-8295, this HEAD): per-contact `pickupNotes`/`deliveryNotes` free-text fields added to `AddressInfoDbEmbedded` and mapped through `worker-services/.../build/LoadCreateDtoConverter.java` + `suggest/ProcessLoadSuggestServiceImpl.java`.


<!-- entities-begin -->
## Entities

Auto-generated by `scripts/cluster_entities.py`. Domain classes declared in this repo:

| Class | Kind | Module | Catalog canonical |
|---|---|---|---|
| `AddressInfoDbEmbedded` | dto | `db-entities` | AddressInfoDb |
| `ContactDto` | dto | `infra-interfaces` | [Contact](../domains/entities/Contact.md) |
| `CsvRowDto` | dto | `api-dtos` | CsvRow |
| `CsvRowPersisted` | dto | `domain` | CsvRowPersisted |
| `FileContentDto` | dto | `infra-interfaces` | [FileContent](../domains/entities/FileContent.md) |
| `GatepassDto` | dto | `infra-interfaces` | Gatepass |
| `InventoryItemDto` | dto | `api-dtos` | InventoryItem |
| `InventoryUnitDbEmbedded` | dto | `db-entities` | InventoryUnitDb |
| `InventoryUnitRatesProcessing` | dto | `domain` | InventoryUnitRatesProcessing |
| `InventoryUnitRatesProcessingDbEntity` | dto | `db-entities` | InventoryUnitRatesProcessing |
| `InventoryUnitRatesResolveFailedEvent` | dto | `domain` | InventoryUnitRatesResolveFailedEvent |
| `InventoryUnitRatesResolvedEvent` | dto | `domain` | InventoryUnitRatesResolvedEvent |
| `InventoryUnitsOrderProcessing` | dto | `domain` | InventoryUnitsOrderProcessing |
| `InventoryWorkerConfig` | dto | `worker-services` | InventoryWorkerConfig |
| `JobIdentityDto` | dto | `api-dtos` | JobIdentity |
| `JobKey` | dto | `db-entities` | JobKey |
| `JobStatusDto` | dto | `api-dtos` | JobStatus |
| `LoadBuilderConfig` | dto | `shared-services` | LoadBuilderConfig |
| `LoadsSuggestedWebSocketMsgDto` | dto | `worker-dtos` | LoadsSuggestedWebSocketMsg |
| `ManagedServiceProviderDto` | dto | `infra-interfaces` | ManagedServiceProvider |
| `OrderDto` | dto | `infra-interfaces` | Order |
| `OrdersCreationDoneSendEmailEvent` | dto | `domain` | OrdersCreationDoneSendEmailEvent |
| `OrdersCreationDto` | dto | `api-dtos` | OrdersCreation |
| `OrdersCreationJob` | dto | `domain` | OrdersCreationJob |
| `OrdersCreationJobDto` | dto | `api-dtos` | OrdersCreationJob |
| `OrdersCreationJobMsgDto` | dto | `worker-dtos` | OrdersCreationJobMsg |
| `OrdersCreationJobProcessedEvent` | dto | `domain` | OrdersCreationJobProcessedEvent |
| `OrdersCreationResponseDto` | dto | `infra-interfaces` | OrdersCreation |
| `OrdersCreationResultDto` | dto | `api-dtos` | OrdersCreationResult |
| `OrdersCreationResultStorage` | dto | `shared-services` | OrdersCreationResultStorage |
| `OrdersCreationUnitProcessingFailedEvent` | dto | `domain` | OrdersCreationUnitProcessingFailedEvent |
| `OrdersCreationUnitProcessingStartedEvent` | dto | `domain` | OrdersCreationUnitProcessingStartedEvent |
| `OrdersCreationWebSocketMsgDto` | dto | `worker-dtos` | OrdersCreationWebSocketMsg |
| `PingJobMsgDto` | dto | `worker-dtos` | PingJobMsg |
| `PongDto` | dto | `infra-interfaces` | Pong |
| `PricingInfoDto` | dto | `api-dtos` | PricingInfo |
| `ProviderResponseDto` | dto | `infra` | Provider |
| `ProvidersPayloadDto` | dto | `infra` | ProvidersPayload |
| `QuoteDetails` | dto | `infra-interfaces` | QuoteDetails |
| `QuoteDto` | dto | `infra` | [Quote](../domains/entities/Quote.md) |
| `QuoteListDto` | dto | `infra` | QuoteList |
| `QuoteRateDto` | dto | `infra-interfaces` | QuoteRate |
| `QuoteRequestDto` | dto | `infra-interfaces` | [Quote](../domains/entities/Quote.md) |
| `QuoteVO` | dto | `infra-interfaces` | QuoteVO |
| `QuoteVehicleDto` | dto | `infra-interfaces` | QuoteVehicle |
| `QuotesReceivedNotificationDto` | dto | `infra-interfaces` | QuotesReceivedNotification |
| `RateDbEmbedded` | dto | `db-entities` | RateDb |
| `RateDto` | dto | `api-dtos` | Rate |
| `RatesFetchedWebSocketMsgDto` | dto | `worker-dtos` | RatesFetchedWebSocketMsg |
| `RatesJob` | dto | `domain` | RatesJob |
| `RatesJobDto` | dto | `api-dtos` | RatesJob |
| `RatesJobFailedWebSocketMsgDto` | dto | `worker-dtos` | RatesJobFailedWebSocketMsg |
| `RatesJobMsgDto` | dto | `worker-dtos` | RatesJobMsg |
| `RatesJobProcessedEvent` | dto | `domain` | RatesJobProcessedEvent |
| `RatesProcessedEvent` | dto | `domain` | RatesProcessedEvent |
| `RatesProcessingEvent` | dto | `domain` | RatesProcessingEvent |
| `RatesRequestDto` | dto | `api-dtos` | Rates |
| `RatesRequestedEvent` | dto | `domain` | RatesRequestedEvent |
| `RatesScheduledEvent` | dto | `domain` | RatesScheduledEvent |
| `SelectedPaymentInfo` | dto | `domain` | SelectedPaymentInfo |
| `SuggestedLoadDto` | dto | `api-dtos` | SuggestedLoad |
| `SuggestedLoadJobStatusDto` | dto | `api-dtos` | SuggestedLoadJobStatus |
| `SuggestedLoadSettingsDto` | dto | `api-dtos` | SuggestedLoadSettings |
| `SuggestedLoadsJob` | dto | `domain` | SuggestedLoadsJob |
| `SuggestedLoadsJobMsgDto` | dto | `worker-dtos` | SuggestedLoadsJobMsg |
| `SuggestedLoadsJobProcessedEvent` | dto | `domain` | SuggestedLoadsJobProcessedEvent |
| `SuggestedLoadsJobProcessingStartedEvent` | dto | `domain` | SuggestedLoadsJobProcessingStartedEvent |
| `SuggestedLoadsJobReadyForProcessingEvent` | dto | `domain` | SuggestedLoadsJobReadyForProcessingEvent |
| `SuggestedUnitDto` | dto | `api-dtos` | SuggestedUnit |
| `TimeMetaDto` | dto | `api-dtos` | TimeMeta |
| `TimeoutService` | dto | `shared-services` | TimeoutService |
| `TimeoutServiceUnit` | dto | `domain` | TimeoutServiceUnit |
| `UnitsAddedToLoadDto` | dto | `infra` | UnitsAddedToLoad |
| `UnitsFilterDto` | dto | `api-dtos` | UnitsFilter |
| `UnitsLockDto` | dto | `infra` | UnitsLock |
| `UnitsUnlockDto` | dto | `infra` | UnitsUnlock |
| `User` | dto | `domain` | [User](../domains/entities/User.md) |
| `VehicleDto` | dto | `infra-interfaces` | [Vehicle](../domains/entities/Vehicle.md) |
| `WorkerPubSubHealth` | dto | `worker-services` | WorkerPubSubHealth |
| `ActiveJobDbEntity` | other | `db-entities` | ActiveJob |
| `BuildLoadsJobStatusDbEntity` | other | `db-entities` | BuildLoadsJobStatus |
| `JobStatusDbEntity` | other | `db-entities` | JobStatus |
| `JobStatusWithExtraUserInfoDBEntity` | other | `db-entities` | JobStatusWithExtraUserInfoDB |
| `LoadDbEntity` | other | `db-entities` | [Load](../domains/entities/Load.md) |
| `LoadsDbEntity` | other | `db-entities` | Loads |
| `OrdersCreationResultDbEntity` | other | `db-entities` | OrdersCreationResult |
| `QuoteManagerProcessIdToRatesJobIdDbEntity` | other | `db-entities` | QuoteManagerProcessIdToRatesJobId |
| `RatesDbEntity` | other | `db-entities` | Rates |
| `RatesJobDbEntity` | other | `db-entities` | RatesJob |
| `TimeoutDbEntity` | other | `db-entities` | Timeout |
<!-- entities-end -->
