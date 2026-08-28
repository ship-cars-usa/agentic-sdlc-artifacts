---
repo: integration-executor
path: ~/projects/ship-cars-usa/integration-executor
stack: Java 21 / Quarkus 3.27.5
domain: integrations
shape: multi-module (10 poms)
last-synced-commit: 1fb3bd2bee190077749f1d650b0064d5a8be9560
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# integration-executor

## What it is
Quarkus 3.27.5 / Java 21 **event-driven router and HTTP executor** for external logistics integrations. Seven per-platform executors: **Acertus, Ally, CarsArrive, EdiOrderful, RunBuggy, SuperDispatch, Webhook**. Stateless message consumer with a persistent retry table — receives `IntegrationMessageDto` on a Pub/Sub subscription (`IntegrationPubSubConsumer`), routes to the matching executor, and dispatches to the external platform. Stores failed requests in PG for backoff retry, and does EDI content-hash deduplication for Orderful. Publishes user-management events to the Logytext topic (Logytext is an outbound topic, not an executor). Its REST clients (`attachment`, `media-proxy`) carry explicit `connect-timeout`/`read-timeout` — fleet-rare.

## How it fits
- Consumes API of: `attachment-backend` via `AttachmentClient` (`@RegisterRestClient(configKey="attachment")`, **`connect-timeout=30000`, `read-timeout=60000`**, `application.properties:63-64`); a `media-proxy` REST client (**same 30s/60s timeouts**, `application.properties:114-115`); and the 7 external integration platforms via per-executor impls.
- Publishes events to: Pub/Sub `executor.pubsub.logytext-topic` (`application.properties:57`, user-management events).
- Subscribes to: Pub/Sub `executor.pubsub.subscription` (`application.properties:56`) — `IntegrationMessageDto` with `integrationType` (`IntegrationTypeEnum`) + payload, consumed by `IntegrationPubSubConsumer`.
- Owns data store: PostgreSQL — entities `IntegrationFailedRequest` (retry queue), `EdiOrderfulSentDocument` (EDI dedup via content hash), `Attachment`. Flyway migrations. Pool max-size not pinned in-repo (Quarkus defaults).

## Build / test / run
```
./mvnw clean install     # or ./build-dev.sh
./mvnw quarkus:dev
# 10 poms: root + configuration, api-dtos, db-entities, event-listener,
#          db-migration, resources, repositories, application, coverage-report
# Per-executor retry: executor.<platform>.retry-attempts=7, min 3000ms / max 10000ms backoff
# Retry sweep: executor.retry.batch-size=50, timeout-minutes=15,
#              keep-completed=180d, keep-failed=360d
```

## Key abstractions
- `IntegrationPubSubConsumer` — `event-listener/.../listener/pubsub/IntegrationPubSubConsumer.java` — implements `PubSubAckReplyConsumerBlocking<IntegrationMessageDto>`; injects `@All List<IntegrationProcessor>` and routes by `integrationType`. (Old doc's `IntegrationMessageListener` name is outdated.)
- Per-platform executors — `event-listener/.../executors/{acertus,ally,carsarrive,ediorderful,runbuggy,superdispatch,webhook}/…Executor(Impl).java` — translate the standard DTO to each platform's wire format and dispatch.
- `EdiOrderfulDeduplicationService` — `event-listener/.../listener/services/EdiOrderfulDeduplicationService.java` — content-hash dedup; `@Scheduled(every="1h")` `cleanupOldRecords()` deletes via `deleteOlderThan(cutoff)` (`:89,:105-107`).
- `CronsController` — `resources/.../rest/CronsController.java` — `@Path("/crons")` with `POST /process-retries` and `POST /cleanup-old-requests`; external cron drives the retry sweep + failed-request cleanup (NEW REST surface).
- `IntegrationFailedRequest` — persistent retry queue entity (`db-entities/.../entities/`).
- `AttachmentClient` — `event-listener/.../clients/AttachmentClient.java:27` — `@RegisterRestClient(configKey="attachment")` with explicit timeouts (the right pattern).

## Don't-do-here / gotchas
- **Per-executor retry profiles now exist** — `executor.<platform>.retry-attempts/-min-backoff-ms/-max-backoff-ms` are declared separately for all 7 executors (`application.properties:66-95`), currently all set to 7 attempts / 3s–10s. (Old doc's "one schedule for all 7" gotcha is resolved structurally; values still identical, so per-platform SLA tuning is still available but unused.)
- **No `@CircuitBreaker`** on `AttachmentClient`/`media-proxy` despite the timeouts — under downstream slowness requests accumulate before retry sheds them.
- **PDF conversion timeout `pdf.conversion.process-timeout-seconds=30`** (`application.properties:52`, env `PDF_CONVERSION_PROCESS_TIMEOUT_SECONDS`) — a process-level hang propagates to consumers on the pod. `MediaProxyService`/`BolProcessingService` drive this path.
- **EDI dedup cleanup `@Scheduled` without ShedLock** — on multi-replica deploys the 1h cleanup double-fires; it deletes by `deleteOlderThan(cutoff)` (date range), so it is idempotent — low risk, but the retry sweep + cleanup-old-requests were moved to the external-cron `CronsController` while dedup cleanup stayed internal.
- **No message-backlog metric** — diagnosing backlog still needs Pub/Sub-side observability; consider a gauge on `IntegrationFailedRequest` row count.
- **Logytext topic is the only outbound async surface** — consumed by the `logytext` flavor of `integrations-backend`.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/integrations-backend.md` — the logytext flavor consumes from this service.
- `~/projects/codebase-map/repos/attachment-backend.md` — REST upstream (with timeouts).
- `~/projects/codebase-map/relations/rest-client-registry.md` — one of the few Quarkus clients with timeouts.
- `~/projects/codebase-map/domains/integrations.md`.
- `docs/BUSINESS_DOMAIN.md` in-repo — domain reference.


<!-- entities-begin -->
## Entities

Auto-generated by `scripts/cluster_entities.py`. Domain classes declared in this repo:

| Class | Kind | Module | Catalog canonical |
|---|---|---|---|
| `Attachment` | jpa | `db-entities` | [Attachment](../domains/entities/Attachment.md) |
| `EdiOrderfulSentDocument` | jpa | `db-entities` | EdiOrderfulSentDocument |
| `IntegrationFailedRequest` | jpa | `db-entities` | IntegrationFailed |
| `AcertusDeliveryInfo` | dto | `event-listener` | AcertusDeliveryInfo |
| `AcertusGpsInfo` | dto | `event-listener` | AcertusGpsInfo |
| `AcertusMessageDto` | dto | `api-dtos` | AcertusMessage |
| `AcertusPickupInfo` | dto | `event-listener` | AcertusPickupInfo |
| `AcertusSettingsDto` | dto | `api-dtos` | AcertusSettings |
| `AcertusStatusUpdateRequest` | dto | `event-listener` | AcertusStatusUpdate |
| `AcertusStatusUpdateRequestWrapper` | dto | `event-listener` | AcertusStatusUpdateRequestWrapper |
| `AllyAuthDto` | dto | `event-listener` | AllyAuth |
| `AllyErrorDto` | dto | `event-listener` | AllyError |
| `AllyMessageDto` | dto | `api-dtos` | AllyMessage |
| `AllySettingsDto` | dto | `api-dtos` | AllySettings |
| `AllyTransportStatusUpdateDto` | dto | `event-listener` | AllyTransportStatusUpdate |
| `AllyTransportStatusUpdateResponseDto` | dto | `event-listener` | AllyTransportStatusUpdate |
| `CarrierInfo` | dto | `event-listener` | CarrierInfo |
| `CarsArriveAcknowledgement` | dto | `event-listener` | CarsArriveAcknowledgement |
| `CarsArriveAttachment` | dto | `event-listener` | CarsArriveAttachment |
| `CarsArriveDelivery` | dto | `event-listener` | CarsArriveDelivery |
| `CarsArriveMessageDto` | dto | `api-dtos` | CarsArriveMessage |
| `CarsArrivePickup` | dto | `event-listener` | CarsArrivePickup |
| `CarsArriveSettingsDto` | dto | `api-dtos` | CarsArriveSettings |
| `CarsArriveUpdateLocation` | dto | `event-listener` | CarsArriveUpdateLocation |
| `Coordinates` | dto | `event-listener` | [GpsPosition](../domains/entities/GpsPosition.md) |
| `CoordinatesVo` | dto | `event-listener` | CoordinatesVo |
| `DamagesInfo` | dto | `event-listener` | DamagesInfo |
| `DeliveryInspection` | dto | `event-listener` | DeliveryInspection |
| `EdiOrderful214AT7Loop` | dto | `event-listener` | EdiOrderful214AT7Loop |
| `EdiOrderful214BeginningSegment` | dto | `event-listener` | EdiOrderful214BeginningSegment |
| `EdiOrderful214BusinessInstructionsAndReferenceNumber` | dto | `event-listener` | EdiOrderful214BusinessInstructionsAndReferenceNumber |
| `EdiOrderful214Contact` | dto | `event-listener` | EdiOrderful214Contact |
| `EdiOrderful214EquipmentLocation` | dto | `event-listener` | EdiOrderful214EquipmentLocation |
| `EdiOrderful214EquipmentOwnerAndType` | dto | `event-listener` | EdiOrderful214EquipmentOwnerAndType |
| `EdiOrderful214GeographicLocation` | dto | `event-listener` | EdiOrderful214GeographicLocation |
| `EdiOrderful214LXLoop` | dto | `event-listener` | EdiOrderful214LXLoop |
| `EdiOrderful214N1Loop` | dto | `event-listener` | EdiOrderful214N1Loop |
| `EdiOrderful214PartyIdentification` | dto | `event-listener` | EdiOrderful214PartyIdentification |
| `EdiOrderful214PartyLocation` | dto | `event-listener` | EdiOrderful214PartyLocation |
| `EdiOrderful214ShipmentStatusDetails` | dto | `event-listener` | EdiOrderful214ShipmentStatusDetails |
| `EdiOrderful214TransactionSetHeader` | dto | `event-listener` | EdiOrderful214TransactionSetHeader |
| `EdiOrderful214TransactionSetLineNumber` | dto | `event-listener` | EdiOrderful214TransactionSetLineNumber |
| `EdiOrderful214TransactionSetTrailer` | dto | `event-listener` | EdiOrderful214TransactionSetTrailer |
| `EdiOrderful214TransportationCarrierShipmentStatusDto` | dto | `event-listener` | EdiOrderful214TransportationCarrierShipmentStatus |
| `EdiOrderful928AutomotiveInspectionDetailDto` | dto | `event-listener` | EdiOrderful928AutomotiveInspectionDetail |
| `EdiOrderful928BeginningSegment` | dto | `event-listener` | EdiOrderful928BeginningSegment |
| `EdiOrderful928InspectionDetailSegment` | dto | `event-listener` | EdiOrderful928InspectionDetailSegment |
| `EdiOrderful928MotorVehicleControl` | dto | `event-listener` | EdiOrderful928MotorVehicleControl |
| `EdiOrderful928TransactionSetHeader` | dto | `event-listener` | EdiOrderful928TransactionSetHeader |
| `EdiOrderful928TransactionSetTrailer` | dto | `event-listener` | EdiOrderful928TransactionSetTrailer |
| `EdiOrderful928VCLoop` | dto | `event-listener` | EdiOrderful928VCLoop |
| `EdiOrderfulConvertRes` | dto | `event-listener` | EdiOrderfulConvertRes |
| `EdiOrderfulMessage` | dto | `event-listener` | EdiOrderfulMessage |
| `EdiOrderfulMessageDto` | dto | `api-dtos` | EdiOrderfulMessage |
| `EdiOrderfulParty` | dto | `event-listener` | EdiOrderfulParty |
| `EdiOrderfulSettingsDto` | dto | `api-dtos` | EdiOrderfulSettings |
| `EdiOrderfulTransactionRequest` | dto | `event-listener` | EdiOrderfulTransaction |
| `EdiOrderfulTransactionResponse` | dto | `event-listener` | EdiOrderfulTransaction |
| `EdiOrderfulTransactionType` | dto | `event-listener` | EdiOrderfulTransactionType |
| `Image` | dto | `event-listener` | Image |
| `IntegrationMessageDto` | dto | `api-dtos` | IntegrationMessage |
| `LoadAcknowledgement` | dto | `event-listener` | LoadAcknowledgement |
| `LoadLegToAcertusStatusUpdateConverter` | dto | `event-listener` | LoadLegToAcertusStatusUpdateConverter |
| `LoadLegToCarsArriveConverter` | dto | `event-listener` | LoadLegToCarsArriveConverter |
| `LoadLegToRunBuggyStatusUpdateConverter` | dto | `event-listener` | LoadLegToRunBuggyStatusUpdateConverter |
| `LoadLegToSuperDispatchStatusUpdateConverter` | dto | `event-listener` | LoadLegToSuperDispatchStatusUpdateConverter |
| `LoadUpdateLocation` | dto | `event-listener` | LoadUpdateLocation |
| `LoadVehiclesInfo` | dto | `event-listener` | LoadVehiclesInfo |
| `LoadVehiclesInfo` | dto | `event-listener` | LoadVehiclesInfo |
| `LogytextCompanyDto` | dto | `api-dtos` | LogytextCompany |
| `LogytextIntegrationMessageDto` | dto | `api-dtos` | LogytextIntegrationMessage |
| `LogytextUmEventDto` | dto | `api-dtos` | LogytextUm |
| `LogytextUserDto` | dto | `api-dtos` | LogytextUser |
| `PaymentInfo` | dto | `event-listener` | PaymentInfo |
| `PickupInspection` | dto | `event-listener` | PickupInspection |
| `RunBuggyActionDto` | dto | `event-listener` | RunBuggyAction |
| `RunBuggyEtaWindowDto` | dto | `event-listener` | RunBuggyEtaWindow |
| `RunBuggyInspectionTemplateInfo` | dto | `event-listener` | RunBuggyInspectionTemplateInfo |
| `RunBuggyMessageDto` | dto | `api-dtos` | RunBuggyMessage |
| `RunBuggySettingsDto` | dto | `api-dtos` | RunBuggySettings |
| `RunBuggyStatusUpdateDto` | dto | `event-listener` | RunBuggyStatusUpdate |
| `RunBuggyTransportOrderConverter` | dto | `event-listener` | RunBuggyTransportOrderConverter |
| `SuperDispatchAcceptRequest` | dto | `event-listener` | SuperDispatchAccept |
| `SuperDispatchAuthResponse` | dto | `event-listener` | SuperDispatchAuth |
| `SuperDispatchEtaUpdateRequest` | dto | `event-listener` | SuperDispatchEtaUpdate |
| `SuperDispatchExecutorImpl` | dto | `event-listener` | SuperDispatchExecutorImpl |
| `SuperDispatchMessageDto` | dto | `api-dtos` | SuperDispatchMessage |
| `SuperDispatchOrderPatchRequest` | dto | `event-listener` | SuperDispatchOrderPatch |
| `SuperDispatchSettingsDto` | dto | `api-dtos` | SuperDispatchSettings |
| `SuperDispatchStatusUpdateRequest` | dto | `event-listener` | SuperDispatchStatusUpdate |
| `VehicleInfo` | dto | `event-listener` | VehicleInfo |
| `VehicleInspectionDetails` | dto | `event-listener` | VehicleInspectionDetails |
| `WebhookMessageDataDto` | dto | `api-dtos` | WebhookMessageData |
| `WebhookMessageDto` | dto | `api-dtos` | WebhookMessage |
| `WebhookSettingsDto` | dto | `api-dtos` | WebhookSettings |
<!-- entities-end -->
