---
repo: autoims-backend
path: ~/projects/ship-cars-usa/autoims-backend
stack: Java/Spring Boot 3.2.12, Java 21
domain: integrations
shape: multi-module (parent + 16 modules)
last-synced-commit: 47e2f94088776a60a7c0190fd2761ed1c6aaea17
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# autoims-backend

## What it is
Spring Boot 3.2.12 / Java 21 multi-module service (package `cars.ship.autoims`) that **bidirectionally syncs Ship.Cars inventory/order data with the external AutoIMS platform**. Two Spring Boot entrypoints share the code: `api-app` (`AutoImsApiApp`) exposes REST CRUD for units, options, and company sync config; `worker-app` (`AutoImsWorkerApp`) runs the ShedLock-guarded scheduled sync and the Pub/Sub-driven per-unit/per-load syncs, and now orchestrates sync jobs via **Temporal workflows** (`temporal-sdk` / `temporal-spring-boot-autoconfigure` in worker-services). The `infra` layer wraps outbound AutoIMS HTTP through a per-tenant `AutoImsWebClientFactory`. Re-domained to `integrations` — an external-platform shim, not billing.

## How it fits
- Consumes API of: external AutoIMS (per-tenant, API_KEY / BASIC_AUTH / SYSTEM_BASIC_AUTH, optional HTTP proxy — see `AutoImsWebClientFactory`); `inventory-backend` (`ship-cars-inventory` 2.17.0 dtos); `metadata` (`ship-cars-metadata` 0.12.0); `location-provider` (`ship-cars-location-provider-client` 3.28.0). Outbound goes through `spring-commons` `WebClientImpl`.
- Publishes events to: Pub/Sub topics `worker` (`CONFIG_GCP_PUBSUB_TOPICS_WORKER`) and `notification` (`CONFIG_GCP_PUBSUB_TOPICS_NOTIFICATION`).
- Subscribes to: Pub/Sub subscriptions `worker`, `inventory`, `posting`. Consumers in `worker-services/.../worker/application/sync/`: `InventoryUnitChangeConsumer`, `InventoryUnitUpdateConsumer`, `LoadInfoStateConsumer`, `BatchImportJobProcessedConsumer`; plus `SyncJobProcessedEventHandler`.
- Owns data store: PostgreSQL via `CONFIG_DB_JDBC_URL` (HikariCP `maximumPoolSize=10`, `maxLifetime=855000`, `connectionTimeout=30000`; comment: pool must stay under DB `max_connections=500`); Hibernate `ddl-auto: validate`; **Flyway disabled at boot** (`flyway.enabled=false`, runs as a separate migration job). Distributed locking via ShedLock (`shedlock-provider-jdbc-template`).

## Build / test / run
```
./mvnw clean package -DskipTests
./mvnw -Pintegration-tests verify
# Modules: api-app, api-services, api-dtos, api-enums, worker-app, worker-services,
#          worker-dtos, domain, shared-services, infra, infra-interfaces, configs,
#          db-entities, db-migration, autoims-mock, coverage-report
# Two runnable apps: AutoImsApiApp (api-app), AutoImsWorkerApp (worker-app)
```

## Key abstractions
- REST controllers (in `api-services/.../rest/`): `CompanyConfigController`, `UnitsController`, `OptionsController`, `SyncToAutoImsController`, `SyncFromAutoImsController`, `AppController` (health), `RootController`.
- `WorkerSyncFromAndToAutoIms` — `api-services/.../application/worker/WorkerSyncFromAndToAutoIms.java:63` — `@Scheduled(cron="${config.scheduler.syncCronExpression}")` **guarded by `@SchedulerLock(name="syncFromAndToAutoIms")`** (l.64); ShedLock enabled in `SchedulerLockConfig`.
- `AutoImsWebClientFactory` — `infra/.../autoims/impl/AutoImsWebClientFactory.java` — per-`AutoImsClientInfoDto` cached `WebClientImpl`; builds base URI, auth header (API_KEY / BASIC / SYSTEM_BASIC), and optional HTTP proxy. NOTE: it does **not** set explicit connect/response timeouts here — timeouts come from `spring-commons WebClientImpl` defaults.
- Pub/Sub consumers: `InventoryUnitChangeConsumer`, `InventoryUnitUpdateConsumer`, `LoadInfoStateConsumer`, `BatchImportJobProcessedConsumer` (worker-services).
- Temporal: `SyncToWorkflowImpl` + workflow/activity classes in `worker-services` — sync jobs run as Temporal workflows/activities (`SyncToActivityImpl`).
- `SecretResolverConfig` — `shared-services? config/SecretResolverConfig.java` — resolves secrets from a JSON file (`config.secrets.filePath`) via commons `SecretResolver`, else `SecretResolver.empty()` (new).
- `autoims-mock` module — in-repo AutoIMS stub; excluded from prod builds (`**/mock/**` exclusion in root pom, l.148).

## Don't-do-here / gotchas
- **ShedLock IS now in place** (was flagged missing in the previous shadow — corrected): the cron is `@SchedulerLock`-guarded, so multi-replica `worker-app` will not double-fire `syncFromAndToAutoIms`. When adding new `@Scheduled` methods, add `@SchedulerLock` too.
- **AutoImsWebClientFactory sets NO explicit timeouts** — despite the previous shadow's claim, the factory only configures base URI/auth/proxy. Outbound AutoIMS calls inherit `WebClientImpl` defaults; verify those are bounded before trusting them under a slow AutoIMS endpoint.
- **Flyway disabled at boot, runs as a K8s job** — app pods can start against an un-migrated schema; `ddl-auto: validate` then crash-loops. Enforce job→app ordering. Recent migrations V54/V55/V56 add indexes on `sync_jobs` (company/synctype/created, inventory_job_id) and `autoims_units` (company/active/last-updated).
- **HikariCP `maximumPoolSize=10`** across both apps — tight; right-size after pool-wait metrics.
- **Auth header value is logged (masked to 3 chars)** in `AutoImsWebClientFactory.buildAuthHeader` — verify `hideString` masking is sufficient given the committed-secrets/secrets-in-logs fleet history.
- **Temporal now in the worker path** — sync-job orchestration depends on a reachable Temporal service; account for that in the worker's health/failure model.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/inventory-backend.md` — primary domain peer.
- `~/projects/codebase-map/repos/location-provider.md`.
- `~/projects/codebase-map/relations/rest-client-registry.md` — note the correction: this service does NOT set WebClient timeouts in its factory.
- `~/projects/codebase-map/domains/integrations.md`.


<!-- entities-begin -->
## Entities

Auto-generated by `scripts/cluster_entities.py`. Domain classes declared in this repo:

| Class | Kind | Module | Catalog canonical |
|---|---|---|---|
| `AutoImsNoteDbEntity` | jpa | `db-entities` | Note |
| `AutoImsUnitDbEntity` | jpa | `db-entities` | [Vehicle](../domains/entities/Vehicle.md) |
| `CompanyConfigDbEntity` | jpa | `db-entities` | [CompanyConfig](../domains/entities/CompanyConfig.md) |
| `SyncJobDbEntity` | jpa | `db-entities` | SyncJob |
| `SyncJobUnitDbEntity` | jpa | `db-entities` | SyncJobUnit |
| `AddressInfoDbEmbedded` | embedded | `db-entities` | AddressInfoDb |
| `AddressInfoUpdateValue` | dto | `domain` | AddressInfoUpdateValue |
| `AutoImsClientConfig` | dto | `infra` | ClientConfig |
| `AutoImsClientInfoDto` | dto | `infra-interfaces` | ClientInfo |
| `AutoImsConfig` | dto | `shared-services` | Config |
| `AutoImsFilterDto` | dto | `api-dtos` | [Filter](../domains/entities/Filter.md) |
| `AutoImsInventoryDto` | dto | `infra-interfaces` | Inventory |
| `AutoImsInventoryListDto` | dto | `infra-interfaces` | InventoryList |
| `AutoImsInventoryNoteDto` | dto | `infra-interfaces` | InventoryNote |
| `AutoImsLocationInfoDto` | dto | `infra-interfaces` | LocationInfo |
| `AutoImsNoteDto` | dto | `api-dtos` | Note |
| `AutoImsNoteValue` | dto | `domain` | NoteValue |
| `AutoImsResponseDto` | dto | `infra-interfaces` | AutoIms |
| `AutoImsTransportUpdateDto` | dto | `infra-interfaces` | TransportUpdate |
| `AutoImsTransportUpdateRequestDto` | dto | `infra-interfaces` | TransportUpdate |
| `AutoImsTransportUpdateResponseDto` | dto | `infra-interfaces` | TransportUpdate |
| `AutoImsUnitDto` | dto | `api-dtos` | [Vehicle](../domains/entities/Vehicle.md) |
| `AutoImsUnitUpdate` | dto | `domain` | UnitUpdate |
| `AutoImsUnitUpdateDto` | dto | `api-dtos` | UnitUpdate |
| `AutoImsUnitUpdateValue` | dto | `domain` | UnitUpdateValue |
| `AutoImsUnitUpdatedEvent` | dto | `domain` | UnitUpdatedEvent |
| `AutoImsVinMessageDto` | dto | `infra-interfaces` | VinMessage |
| `AutoImsWorkerConfig` | dto | `worker-services` | WorkerConfig |
| `CompanyConfigDto` | dto | `api-dtos` | [CompanyConfig](../domains/entities/CompanyConfig.md) |
| `CompanyConfigNotesJsonEntity` | dto | `db-entities` | CompanyConfigNotesJson |
| `CompanyConfigSyncFromDto` | dto | `api-dtos` | CompanyConfigSyncFrom |
| `CompanyConfigSyncFromNotesDto` | dto | `api-dtos` | CompanyConfigSyncFromNotes |
| `CompanyConfigSyncFromUpdateDto` | dto | `api-dtos` | CompanyConfigSyncFromUpdate |
| `CompanyConfigSyncToDto` | dto | `api-dtos` | CompanyConfigSyncTo |
| `CompanyConfigSyncToTransportDto` | dto | `api-dtos` | CompanyConfigSyncToTransport |
| `CompanyConfigSyncToUpdateDto` | dto | `api-dtos` | CompanyConfigSyncToUpdate |
| `CompanyConfigTransportJsonEntity` | dto | `db-entities` | CompanyConfigTransportJson |
| `CompanyConfigUpdateDto` | dto | `api-dtos` | CompanyConfigUpdate |
| `CompanyConfigUpdateSyncTimesDto` | dto | `api-dtos` | CompanyConfigUpdateSyncTimes |
| `FetchUnitsForUpdateInDto` | dto | `shared-services` | FetchUnitsForUpdateIn |
| `FetchUnitsForUpdateOutDto` | dto | `shared-services` | FetchUnitsForUpdateOut |
| `InventoryMemoryStore` | dto | `autoims-mock` | InventoryMemoryStore |
| `ListAutoImsUnitsDto` | dto | `api-dtos` | ListAutoImsUnits |
| `LocationDto` | dto | `autoims-mock` | [Location](../domains/entities/Location.md) |
| `NoteResponseDto` | dto | `autoims-mock` | Note |
| `OptionDto` | dto | `api-dtos` | Option |
| `SyncJob` | dto | `domain` | SyncJob |
| `SyncJobCompletedWebSocketMsgDto` | dto | `worker-dtos` | SyncJobCompletedWebSocketMsg |
| `SyncJobDto` | dto | `api-dtos` | SyncJob |
| `SyncJobIdentityDto` | dto | `api-dtos` | SyncJobIdentity |
| `SyncJobMsgDto` | dto | `worker-dtos` | SyncJobMsg |
| `SyncJobProcessedEvent` | dto | `domain` | SyncJobProcessedEvent |
| `SyncJobProcessingStartedEvent` | dto | `domain` | SyncJobProcessingStartedEvent |
| `SyncJobReadyForProcessingEvent` | dto | `domain` | SyncJobReadyForProcessingEvent |
| `SyncJobUnit` | dto | `domain` | SyncJobUnit |
| `SyncJobUnitProcessedEvent` | dto | `domain` | SyncJobUnitProcessedEvent |
| `SyncJobUnitProcessingStartedEvent` | dto | `domain` | SyncJobUnitProcessingStartedEvent |
| `SyncJobUnitReadyForProcessingEvent` | dto | `domain` | SyncJobUnitReadyForProcessingEvent |
| `SyncSummaryReportDto` | dto | `api-dtos` | SyncSummaryReport |
| `SyncToActivityInDto` | dto | `shared-services` | SyncToActivityIn |
| `SyncToAutoImsServiceImpl` | dto | `shared-services` | SyncToAutoImsServiceImpl |
| `SyncToAutoImsServiceResponse` | dto | `shared-services` | SyncToAutoImsService |
| `SyncToWorkflowInDto` | dto | `shared-services` | SyncToWorkflowIn |
| `SyncToWorkflowOutDto` | dto | `shared-services` | SyncToWorkflowOut |
| `TimeMetaDto` | dto | `api-dtos` | TimeMeta |
| `TransportInfoJsonEntity` | dto | `db-entities` | TransportInfoJson |
| `TransportInfoUpdateValue` | dto | `domain` | TransportInfoUpdateValue |
| `TransportUpdateDto` | dto | `autoims-mock` | TransportUpdate |
| `TransportUpdateResponseDto` | dto | `autoims-mock` | TransportUpdate |
| `TransportUpdatesDto` | dto | `autoims-mock` | TransportUpdates |
| `UnitsFilterProperties` | dto | `api-services` | UnitsFilterProperties |
| `UpdateLastSuccessfulSyncActivityInDto` | dto | `shared-services` | UpdateLastSuccessfulSyncActivityIn |
| `UpdateLastSyncActivityInDto` | dto | `shared-services` | UpdateLastSyncActivityIn |
| `User` | dto | `domain` | [User](../domains/entities/User.md) |
| `VehicleController` | dto | `autoims-mock` | VehicleController |
| `VehicleFormatResponseDto` | dto | `autoims-mock` | VehicleFormat |
| `VehicleResponseDto` | dto | `autoims-mock` | [Vehicle](../domains/entities/Vehicle.md) |
| `VehicleResponseErrorDto` | dto | `autoims-mock` | VehicleResponseError |
| `VehicleVin` | dto | `domain` | VehicleVin |
| `VehiclesResponseDto` | dto | `autoims-mock` | Vehicles |
| `VinMessageDto` | dto | `autoims-mock` | VinMessage |
| `YearMakeModel` | dto | `domain` | YearMake |
<!-- entities-end -->
