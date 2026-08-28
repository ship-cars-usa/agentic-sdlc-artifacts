---
repo: inventory-backend
path: ~/projects/ship-cars-usa/inventory-backend
stack: Java/Spring Boot 3.2.12 (Java 21)
domain: listings-trade
shape: multi-module (18 poms)
last-synced-commit: bff6db45d1c72d8e6f40708ec5bc63a138d6abcb
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# inventory-backend

## What it is
Spring Boot 3.2.12 (Java 21) vehicle-inventory unit management (v2.19.0-SNAPSHOT). REST CRUD for inventory units plus CSV import/export, batch update/import, unit locking, gate-pass downloads, and auto-generated IMS notes. Integrates with `posting-backend` (load assignment) and the loadboard posting flow; company-scoped calls go through `impersonator`. Heavy async flows (CSV import/export, batch ops, gate-pass) run on **Temporal** workers (5 task queues), but the service **also uses ShedLock + `@Scheduled` + `@Async`** for lighter periodic/async work (e.g. expiring unit locks) — it is not Temporal-only. Postgres + Hibernate Envers auditing. **Spring Boot, not Quarkus** despite `PROJECTS_INDEX.md`.

## How it fits
- Consumes API of: `posting-backend`, `contract-pricing-backend`, `user-backend`, carrier-search, `attachment-backend`, `dataone` (with retry + reactive `.block(Duration)` timeout), `location-provider`, `media-proxy` — all via `spring-commons.WebClientImpl`; company-scoped via the `impersonator` prefix.
- Publishes events to: Pub/Sub topics `notification` and `events` (declared `config-external.yaml:51-54`; used in `NotificationClientConfig` and `shared-services/.../events/EventsService.java:39`).
- Subscribes to: **None.** Publishes only; no inbound Pub/Sub adapter / subscriber in main source. Confirmed still true.
- Owns data store: PostgreSQL + Hibernate Envers audit; Flyway migrations in `db-migration`. Temporal task queues: `<env>.inventory.queue.{csv-import, csv-export, batch-import, batch-update, gatepass-download}` (`config-external.yaml:56-103`). **`integrators-data-bridge` reads this Postgres directly** (external; coordinate schema changes).

## Build / test / run
```
./build-project.sh          # run before PRs (per CLAUDE.md)
./mvnw clean package -DskipTests
./mvnw test -Dunit-tests-only
./mvnw -Pintegration-tests verify
# 18 poms. Modules incl: api-app, api-services, worker-app, worker-services,
#   shared-services, domain, infra, infra-interfaces, db-entities, db-migration, configs, *-dtos, *-enums
# App server.port=8080 (config-commons.yaml:96); 7085/15085 in README are Docker host mappings
# Requires Temporal frontend (CONFIG_TEMPORAL_FRONTEND, default :7233)
```

## Key abstractions
- `V1UnitsController` — `api-services/.../rest/v1/V1UnitsController.java` — inventory-unit CRUD/query REST endpoints. Siblings in `rest/v1/`: `V1BatchUpdateController`, `V1BatchImportController`, `V1UploadCsvController`, `V1ExportCsvController`, `V1UserSettingsController`, `V1PingController`.
- `UnitsQueryService` — `shared-services/.../repos/units/UnitsQueryService.java` — unit read/query.
- `PostingClientImpl` — `infra/.../posting/impl/PostingClientImpl.java:60-67` — outbound to `posting-backend`; **no timeouts**.
- `DataOneFetcherImpl` — `infra/.../dataone/impl/DataOneFetcherImpl.java:58-69` — the one client WITH bounds: retry + reactive `.block(Duration)` (`dataone.timeout-seconds-per-item:10`).
- `InfraPubSubPublisherImpl` — `infra/.../pubsub/impl/InfraPubSubPublisherImpl.java` — Pub/Sub publish wrapper.
- `SchedulerLockConfig` — `shared-services/.../config/SchedulerLockConfig.java` — `@EnableSchedulerLock` + `JdbcTemplateLockProvider` (ShedLock IS present).
- `UnitLockSchedulerImpl` — `api-services/.../unitlock/impl/UnitLockSchedulerImpl.java:17-21` — `@Scheduled` + `@SchedulerLock` cleanup of expired locks.
- Temporal workflows (`shared-services`/`worker-services` `.../temporal/`): `CsvImportWorkflow`, `CsvExportWorkflow`, `BatchImportWorkflow`, `BatchUpdateWorkflow`, `GatePassDownloadWorkflow` (+ monitor/schedule).

## Don't-do-here / gotchas
- **REST-client timeouts are scoped, not universal.** `PostingClientImpl` and `ContractPricingClientImpl` / `UserManagementClientImpl` / `CarrierSearchClientImpl` set **no** connect/read timeout (WebClient defaults). Exceptions: `DataOneFetcherImpl` (retry + `.block(Duration)`) and `AttachmentClientImpl` (upload-completion polling timeout, `config-external.yaml:6`). Don't assume everything is timeout-less; don't assume anything is bounded either — check the specific client.
- **`@Version` optimistic locking here is CORRECT (rare in the Spring fleet).** `db-entities/.../commons/BaseDbEntity.java:46` uses `jakarta.persistence.Version` on `long entityVersion` (import at `:9`) — the active JPA import, not the inert `org.springframework.data.annotation.Version` that sibling Spring services use. CLAUDE.md also documents `EntityManager.lock(OPTIMISTIC_FORCE_INCREMENT)` for collection-only updates.
- **`integrators-data-bridge` reads this Postgres directly** — no API contract, no schema-change hook. Renaming/migrating a column without coordinating breaks the bridge silently.
- **No inbound Pub/Sub / no inventory-mutation topic for consumers.** Reactors either poll the API or read via integrators-data-bridge — both fragile. A canonical `inventory-state` topic would help.
- **Mixed async models.** Temporal for the heavy import/export/gatepass workflows; ShedLock + `@Scheduled` + `@Async` (`AsyncThreadPoolsConfig`, several event handlers) for lighter work. Ensure both Temporal failure metrics AND `@Async` uncaught-exception handling are wired to alerting.
- **HikariCP `maximumPoolSize: 20`** (`config-db.yaml:20`, default) — fleet-norm; watch under concurrent posting + Temporal activity.

## Relevant ADRs / docs
- `docs/tech-project-overview.md` — module breakdown + architecture.
- `config-external.yaml:56-110` — Temporal task queues + connection.
- `infra/.../posting/impl/PostingClientImpl.java` — primary outbound integration point.
- `~/projects/codebase-map/repos/posting-backend.md` — counterpart in the listings-trade flow.
- `~/projects/codebase-map/repos/integrators-data-bridge.md` — direct-Postgres-reader; coordinate schema changes.


<!-- entities-begin -->
## Entities

Auto-generated by `scripts/cluster_entities.py`. Domain classes declared in this repo:

| Class | Kind | Module | Catalog canonical |
|---|---|---|---|
| `AutoImsNoteDbEntity` | jpa | `db-entities` | Note |
| `InventoryUnitDbEntity` | jpa | `db-entities` | [Vehicle](../domains/entities/Vehicle.md) |
| `UnitLockDbEntity` | jpa | `db-entities` | Lock |
| `UserSettingsDbEntity` | jpa | `db-entities` | UserSettings |
| `AddressInfoDbEmbedded` | embedded | `db-entities` | AddressInfoDb |
| `AddressInfo` | dto | `domain` | AddressInfo |
| `AddressInfoDto` | dto | `inventory-dtos` | AddressInfo |
| `AddressInfoValue` | dto | `domain` | AddressInfoValue |
| `AutoImsNoteDto` | dto | `inventory-dtos` | Note |
| `BatchDeleteUnitsDto` | dto | `inventory-dtos` | BatchDeleteUnits |
| `BatchImportDto` | dto | `worker-dtos` | BatchImport |
| `BatchImportJobDto` | dto | `inventory-dtos` | BatchImportJob |
| `BatchImportJobIdentityDto` | dto | `inventory-dtos` | BatchImportJobIdentity |
| `BatchImportReportDto` | dto | `inventory-dtos` | BatchImportReport |
| `BatchImportWorkflowInDto` | dto | `worker-dtos` | BatchImportWorkflowIn |
| `BatchImportWorkflowOutDto` | dto | `worker-dtos` | BatchImportWorkflowOut |
| `BatchImportedEvent` | dto | `worker-dtos` | BatchImportedEvent |
| `BatchImportedWebSocketMsgDto` | dto | `worker-dtos` | BatchImportedWebSocketMsg |
| `BatchSummaryReportDto` | dto | `inventory-dtos` | BatchSummaryReport |
| `BatchUpdateDto` | dto | `worker-dtos` | BatchUpdate |
| `BatchUpdateJobDto` | dto | `inventory-dtos` | BatchUpdateJob |
| `BatchUpdateJobIdentityDto` | dto | `inventory-dtos` | BatchUpdateJobIdentity |
| `BatchUpdateProcessedEvent` | dto | `domain` | BatchUpdateProcessedEvent |
| `BatchUpdateProcessingStartedEvent` | dto | `domain` | BatchUpdateProcessingStartedEvent |
| `BatchUpdateReadyForProcessingEvent` | dto | `domain` | BatchUpdateReadyForProcessingEvent |
| `BatchUpdateReportDto` | dto | `inventory-dtos` | BatchUpdateReport |
| `BatchUpdateReportRowDto` | dto | `inventory-dtos` | BatchUpdateReportRow |
| `BatchUpdateWorkflowInDto` | dto | `worker-dtos` | BatchUpdateWorkflowIn |
| `BatchUpdateWorkflowOutDto` | dto | `worker-dtos` | BatchUpdateWorkflowOut |
| `BatchUpdatedEvent` | dto | `worker-dtos` | BatchUpdatedEvent |
| `BatchUpdatedWebSocketMsgDto` | dto | `worker-dtos` | BatchUpdatedWebSocketMsg |
| `CleanupStorageActivityInDto` | dto | `worker-dtos` | CleanupStorageActivityIn |
| `CleanupStorageInDto` | dto | `worker-dtos` | CleanupStorageIn |
| `ContractPricingDetailsDto` | dto | `inventory-dtos` | ContractPricingDetails |
| `ContractPricingDetailsEmbedded` | dto | `db-entities` | ContractPricingDetails |
| `ContractPricingResolverService` | dto | `shared-services` | ContractPricingResolverService |
| `CreateAutoImsNoteDto` | dto | `inventory-dtos` | CreateAutoImsNote |
| `CsvContactDto` | dto | `inventory-dtos` | CsvContact |
| `CsvContactsDto` | dto | `inventory-dtos` | CsvContacts |
| `CsvExportJobDto` | dto | `inventory-dtos` | CsvExportJob |
| `CsvExportJobIdentityDto` | dto | `inventory-dtos` | CsvExportJobIdentity |
| `CsvExportWorkflowInDto` | dto | `worker-dtos` | CsvExportWorkflowIn |
| `CsvExportWorkflowOutDto` | dto | `worker-dtos` | CsvExportWorkflowOut |
| `CsvExportedEvent` | dto | `worker-dtos` | CsvExportedEvent |
| `CsvExportedWebSocketMsgDto` | dto | `worker-dtos` | CsvExportedWebSocketMsg |
| `CsvImportJobDto` | dto | `inventory-dtos` | CsvImportJob |
| `CsvImportJobIdentityDto` | dto | `inventory-dtos` | CsvImportJobIdentity |
| `CsvImportWorkflowInDto` | dto | `worker-dtos` | CsvImportWorkflowIn |
| `CsvImportWorkflowOutDto` | dto | `worker-dtos` | CsvImportWorkflowOut |
| `CsvImportedEvent` | dto | `worker-dtos` | CsvImportedEvent |
| `CsvImportedWebSocketMsgDto` | dto | `worker-dtos` | CsvImportedWebSocketMsg |
| `CustomerDto` | dto | `inventory-dtos` | [Company](../domains/entities/Company.md) |
| `CustomerInfo` | dto | `domain` | CustomerInfo |
| `CustomerJsonEntity` | dto | `db-entities` | CustomerJson |
| `CustomerResult` | dto | `db-entities` | CustomerResult |
| `CustomerValue` | dto | `domain` | CustomerValue |
| `DateRangeDto` | dto | `inventory-dtos` | [DateRange](../domains/entities/DateRange.md) |
| `DownloadGatePassStatusUpdatedWebSocketMsgDto` | dto | `worker-dtos` | DownloadGatePassStatusUpdatedWebSocketMsg |
| `EmailMessageDto` | dto | `infra-interfaces` | EmailMessage |
| `ExportCsvInDto` | dto | `worker-dtos` | ExportCsvIn |
| `ExportCsvOutDto` | dto | `worker-dtos` | ExportCsvOut |
| `ExportDataDto` | dto | `inventory-dtos` | ExportData |
| `FileIdToUrl` | dto | `infra-interfaces` | FileIdToUrl |
| `FileInfoDto` | dto | `infra-interfaces` | FileInfo |
| `GatePassDownloadFailedEvent` | dto | `domain` | GatePassDownloadFailedEvent |
| `GatePassDownloadInDto` | dto | `worker-dtos` | GatePassDownloadIn |
| `GatePassDownloadScheduleInDto` | dto | `worker-dtos` | GatePassDownloadScheduleIn |
| `GatePassDownloadStartedEvent` | dto | `domain` | GatePassDownloadStartedEvent |
| `GatePassDownloadStatus` | dto | `domain` | GatePassDownloadStatus |
| `GatePassDownloadedEvent` | dto | `domain` | GatePassDownloadedEvent |
| `ImportContactsValidatorInDto` | dto | `worker-services` | ImportContactsValidatorIn |
| `ImportLocationDto` | dto | `inventory-dtos` | ImportLocation |
| `ImportReportInDto` | dto | `worker-dtos` | ImportReportIn |
| `ImportReportOutDto` | dto | `worker-dtos` | ImportReportOut |
| `ImportReportRowDto` | dto | `inventory-dtos` | ImportReportRow |
| `ImportSliceInDto` | dto | `worker-dtos` | ImportSliceIn |
| `ImportSliceOutDto` | dto | `worker-dtos` | ImportSliceOut |
| `ImportUnitStatusDto` | dto | `worker-dtos` | ImportUnitStatus |
| `ImportUnitsStatusDto` | dto | `worker-dtos` | ImportUnitsStatus |
| `InventoryApiConfig` | dto | `api-services` | ApiConfig |
| `InventoryConfig` | dto | `shared-services` | Config |
| `InventoryEventDto` | dto | `inventory-dtos` | Inventory |
| `InventoryFilterDto` | dto | `inventory-dtos` | [Filter](../domains/entities/Filter.md) |
| `InventoryUnitCreateDto` | dto | `inventory-dtos` | UnitCreate |
| `InventoryUnitDto` | dto | `inventory-dtos` | [Vehicle](../domains/entities/Vehicle.md) |
| `InventoryUnitImportCsvDto` | dto | `inventory-dtos` | UnitImportCsv |
| `InventoryUnitImportExportDto` | dto | `inventory-dtos` | UnitImportExport |
| `InventoryUnitStatus` | dto | `domain` | UnitStatus |
| `InventoryUnitUpdate` | dto | `domain` | UnitUpdate |
| `InventoryUnitUpdateDto` | dto | `inventory-dtos` | UnitUpdate |
| `InventoryUnitUpdatedEvent` | dto | `domain` | UnitUpdatedEvent |
| `InventoryUnitsImportDto` | dto | `inventory-dtos` | UnitsImport |
| `InventoryUnitsUpdateDto` | dto | `inventory-dtos` | UnitsUpdate |
| `InventoryWorkerConfig` | dto | `worker-services` | WorkerConfig |
| `LineItemDto` | dto | `inventory-dtos` | LineItem |
| `LineItemEmbedded` | dto | `db-entities` | LineItem |
| `ListInventoryUnitsDto` | dto | `inventory-dtos` | ListInventoryUnits |
| `LocationDto` | dto | `inventory-dtos` | [Location](../domains/entities/Location.md) |
| `LocationJsonEntity` | dto | `db-entities` | LocationJson |
| `LocationResult` | dto | `db-entities` | LocationResult |
| `LocationValue` | dto | `domain` | LocationValue |
| `MileageResolveInDto` | dto | `worker-services` | MileageResolveIn |
| `NewUnitsImportedWebSocketMsgDto` | dto | `worker-dtos` | NewUnitsImportedWebSocketMsg |
| `PongDto` | dto | `inventory-dtos` | Pong |
| `ReadCsvInDto` | dto | `worker-dtos` | ReadCsvIn |
| `ReadCsvOutDto` | dto | `worker-dtos` | ReadCsvOut |
| `ScheduleCsvUploadCommand` | dto | `api-services` | ScheduleCsvUploadCommand |
| `SortingColumns` | dto | `domain` | SortingColumns |
| `SystemAutoImsNoteAddedEvent` | dto | `domain` | SystemAutoImsNoteAddedEvent |
| `TimeMetaDto` | dto | `inventory-dtos` | TimeMeta |
| `UnitAddedToLoadEvent` | dto | `domain` | UnitAddedToLoadEvent |
| `UnitLock` | dto | `domain` | Lock |
| `UnitPutOnHoldEvent` | dto | `domain` | UnitPutOnHoldEvent |
| `UnitReleasedOnHoldEvent` | dto | `domain` | UnitReleasedOnHoldEvent |
| `UnitRemovedFromLoadEvent` | dto | `domain` | UnitRemovedFromLoadEvent |
| `UnitUpdateContactsValue` | dto | `domain` | UnitUpdateContactsValue |
| `UnitUpdateValue` | dto | `domain` | UnitUpdateValue |
| `UnitWithCompanyId` | dto | `shared-services` | UnitWithCompanyId |
| `UnitsAddedToLoadDto` | dto | `inventory-dtos` | UnitsAddedToLoad |
| `UnitsFilterProperties` | dto | `shared-services` | UnitsFilterProperties |
| `UnitsLockDto` | dto | `inventory-dtos` | UnitsLock |
| `UnitsPutOnHoldDto` | dto | `inventory-dtos` | UnitsPutOnHold |
| `UnitsReleaseOnHoldDto` | dto | `inventory-dtos` | UnitsReleaseOnHold |
| `UnitsRemovedFromLoadDto` | dto | `inventory-dtos` | UnitsRemovedFromLoad |
| `UnitsUnlockDto` | dto | `inventory-dtos` | UnitsUnlock |
| `UnitsUpdatedWebSocketMsgDto` | dto | `worker-dtos` | UnitsUpdatedWebSocketMsg |
| `UnitsUpdatedWebSocketMsgDto` | dto | `worker-dtos` | UnitsUpdatedWebSocketMsg |
| `UnitsWithContractDetails` | dto | `shared-services` | UnitsWithContractDetails |
| `UpdateReportInDto` | dto | `worker-dtos` | UpdateReportIn |
| `UpdateReportOutDto` | dto | `worker-dtos` | UpdateReportOut |
| `UpdateSliceInDto` | dto | `worker-dtos` | UpdateSliceIn |
| `UpdateSliceOutDto` | dto | `worker-dtos` | UpdateSliceOut |
| `UpdateUnitInDto` | dto | `worker-dtos` | UpdateUnitIn |
| `UpdateUnitStatusDto` | dto | `worker-dtos` | UpdateUnitStatus |
| `UpdateUnitsStatusDto` | dto | `worker-dtos` | UpdateUnitsStatus |
| `UpdateUserSettingsDto` | dto | `inventory-dtos` | UpdateUserSettings |
| `UploadReportDto` | dto | `inventory-dtos` | UploadReport |
| `User` | dto | `domain` | [User](../domains/entities/User.md) |
| `UserSettings` | dto | `domain` | UserSettings |
| `UserSettingsDto` | dto | `inventory-dtos` | UserSettings |
| `UserSettingsJsonEntity` | dto | `db-entities` | UserSettingsJson |
| `ValidatedUnitDtoToVinToYmmValidItemsConverter` | dto | `worker-services` | ValidatedUnitDtoToVinToYmmValidItemsConverter |
| `VehicleInfo` | dto | `domain` | VehicleInfo |
| `VehicleInfoDto` | dto | `infra-interfaces` | VehicleInfo |
| `VehicleInfoNotFoundDto` | dto | `infra-interfaces` | VehicleInfoNotFound |
| `VehicleSpecificationDto` | dto | `infra-interfaces` | [VehicleSpecification](../domains/entities/VehicleSpecification.md) |
| `VehicleVin` | dto | `domain` | VehicleVin |
| `VinToYmmValidItem` | dto | `domain` | VinToYmmValidItem |
| `VinToYmmValidItems` | dto | `domain` | VinToYmmValidItems |
| `VisibleColumns` | dto | `domain` | VisibleColumns |
| `YearMakeModel` | dto | `domain` | YearMake |
<!-- entities-end -->
