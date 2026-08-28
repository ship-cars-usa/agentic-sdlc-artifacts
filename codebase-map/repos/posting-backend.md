---
repo: posting-backend
path: ~/projects/ship-cars-usa/posting-backend
stack: Java/Spring Boot 3.2.12 (Java 21)
domain: listings-trade
shape: multi-module (4 poms)
last-synced-commit: 55b4bd1a07eb1cb386c879afc69a3fda9135a411
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# posting-backend

## What it is
Spring Boot 3.2.12 (Java 21) service — "LoadMate Posting Backend" — that manages the full **lifecycle of load legs** (transportation jobs) from creation to completion: load posting, carrier dispatching, and tracking across external loadboards and internal systems (`docs/BUSINESS_DOMAIN.md`). Core entity `LoadLeg`, statuses PENDING_POSTING → POSTED → DISPATCHED → COMPLETED (plus PENDING_CLAIM); types STANDARD, MANAGED_ORDER, DRIVEAWAY, CHASE_DRIVER. Multi-tenant via `impersonator`. **The Spring fleet's gold standard for outbox** — a real distributed-lock outbox (ShedLock + Sherlock) with retry, priority/starvation controls. Ships load data to legacy + v3 loadboards, integrates with `inventory-backend` for vehicles, consumes a wide Pub/Sub fan-in. **Temporal is now a hard dependency** (fail-fast if the `posting-dispatch` namespace is missing) driving a newer dispatch-event relay engine, dispatch-sheet PDFs, and bulk ops. New AI "Smart Load Assistant" via Gemini/Vertex. **Spring Boot, not Quarkus** despite `PROJECTS_INDEX.md`.

## How it fits
- Consumes API of: `inventory-backend`, `user-backend`, `attachment-backend`, `contract-pricing-backend`, `quote-manager-backend` (+ internal), `driveaway-backend`, `payment-backend`, `loadboard-backend` (legacy + v3), `location-history`, central-dispatch (external), `media-proxy`, `metadata`, file-storage, and Gemini/Vertex (Smart Load Assistant) — 13 REST client impls under `application/adapters/out/clients/`, all via `spring-commons.WebClientImpl`.
- Publishes events to: Pub/Sub `notification-state`, `posting-state`, `posting-v2-state`, `contacts-state`, `um-usage-record` (`application.properties:160-164`) — **all via the outbox**, 10 s tick, 225 s ShedLock max-lock-for.
- Subscribes to: Pub/Sub `user-state`, `company-state`, `loadboard-state`, `quote-state`, `posting-job-events`, `loadboard-v3-events`, `ml-bot-order` (`application.properties:153-159`) — consumers extending `spring-commons.PubSubConsumer`.
- Owns data store: PostgreSQL (JPA/Hibernate); outbox via `OutboxMessage` + `OutboxMessageService`; ehcache for Bucket4j rate limiting. **`integrators-data-bridge` reads this Postgres directly** (external; coordinate schema changes).

## Build / test / run
```
./mvnw clean package -DskipTests -Punit-tests-only
./mvnw -Pintegration-tests verify
# 4 poms / 3 modules: posting-app, posting-dtos, posting-enums
# Main HTTP port env-driven (server.port=7071 only in application-local); trusted-endpoints 7073
# Requires Temporal on :7233 + a `posting-dispatch` namespace (LITE-8008) — missing namespace fail-fasts startup
# Temporal task queues: create-report, bulk-update-loads, bulk-operations, loadleg-dispatch
```

## Key abstractions
- `OutboxMessageService` — `domain/service/outbox/OutboxMessageService.java` — core outbox processor; enforces `maxMessageRetries=5` at `:352` (`application.properties:288`).
- `OutboxPoller` — `application/adapters/in/chron/OutboxPoller.java:19-23` — `@Scheduled`+`@SchedulerLock` tick (lockAtMostFor PT225S) driving the outbox.
- `DispatchEventPoller` / `DispatchEventRelayService` — `application/adapters/in/chron/` + `domain/temporal/dispatch/relay/` — newer dispatch-event engine relaying into Temporal via signalWithStart.
- `ShipcarsLoadBoardClientImpl` — `application/adapters/out/clients/ShipcarsLoadBoardClientImpl.java:149-152` — legacy loadboard client; explicit timeouts connect PT60S / read PT150S.
- `V3LoadBoardClientImpl` — same package (`:101-104`) — v3 loadboard client; same four explicit timeouts.
- `LoadBoardClientUtil` — same package — shared retry/exception-classification helpers (the timeout-suppressing retry lists).
- Pub/Sub consumers (`application/adapters/in/pubsub/`): `UserStateConsumer`, `CompanyStateConsumer`, `LoadBoardStateConsumer`, `V3LoadboardStateConsumer`, `QuoteManagerStateConsumer`, `LoadLegPostingJobConsumer`, `MlBotOrderConsumer`.
- `SmartLoadAssistantController` + `assistant/GeminiLoadAssistantClient.java:61` — new Gemini/Vertex AI integration (client timeout 15 s).
- ~40 versioned controllers (G1–G6) under `application/adapters/in/web/rest/controller/`.

## Don't-do-here / gotchas
- **`@Version` optimistic locking is INERT.** `domain/model/common/BaseEntity.java:37` annotates `lastModified` with `@Version`, but the import at `:17` is `org.springframework.data.annotation.Version` (Spring Data), not `jakarta.persistence.Version` — Hibernate ignores it. Correctness rests on narrow-write patterns, not optimistic locks.
- **Lost-update races are a live risk (HEAD `55b4bd1a` fixed one).** The `LocationResolverMessageHandler` used to `save(loadLeg)` after long geocoding calls, rewriting every column from a stale snapshot and silently reverting a status another tx had promoted (POSTED → PENDING_POSTING). The fix adds a narrow `LoadLegRepositoryImpl.saveRoutes(...)` (merge routes only) rather than re-enabling `@Version`. When writing back an aggregate read before a slow call, save only what you changed. ITs: `LoadLegStaleWriteIT`, `LocationResolverMessageHandlerIT`.
- **Loadboard clients suppress retry-on-timeout** — `LoadBoardClientUtil.RETRY_EXCEPTION_CLASS_NAMES_WITHOUT_TIMEOUT` (`:56-59`) filters "timeout" class names out of the retry set; applied at `ShipcarsLoadBoardClientImpl.java:407`. Under loadboard slowness a timeout is propagated, not retried (intentional). New curated lists `CREATE_LOAD_RETRY_*` / `CONNECTION_CLOSED_*` (`:61-83`).
- **Only 4 of 13 REST clients pin timeouts** (both loadboard clients + Attachment upload PT180S + Gemini 15 s). The other 9 (Payment, Inventory, UserManagement, QuoteManager(+Internal), Driveaway, FileStorage, CentralDispatch, ContractPricing, LocationHistory) inherit WebClient defaults.
- **Outbox lock window 225 s** (= loadboard read-timeout 150 s × 1.5, `:276-280`) with `maxMessageRetries=5` — a publish hung >225 s orphans the group for another instance; treat "stuck outbox" alerts as poison-message indicators. Outbox now has priority/starvation controls (`lowPriorityMaxDeferral` PT15M, `maxPromotedGroups`, `:293-300`).
- **`integrators-data-bridge` reads this Postgres directly** — schema changes here can silently break the bridge.
- **HikariCP `maximumPoolSize: 20`** (`application.properties:348`) — fleet-norm; scale if outbox + Temporal activity spike.

## Relevant ADRs / docs
- `docs/BUSINESS_DOMAIN.md` — LoadLeg lifecycle / status model.
- `application.properties:267-300` — outbox config (lock window, retries, priority/starvation).
- `application.properties:246-250, 220-223` — loadboard client timeouts.
- `application.properties:510-574` — Temporal (posting-dispatch namespace, workers).
- `~/projects/codebase-map/repos/loadboard-backend.md`, `inventory-backend.md`, `spring-commons.md`.


<!-- entities-begin -->
## Entities

Auto-generated by `scripts/cluster_entities.py`. Domain classes declared in this repo:

| Class | Kind | Module | Catalog canonical |
|---|---|---|---|
| `AccountingLineItemEntity` | jpa | `posting-app` | AccountingLineItem |
| `ActivityLog` | jpa | `posting-app` | [ActivityLog](../domains/entities/ActivityLog.md) |
| `AtgDriverCodeViewLog` | jpa | `posting-app` | AtgDriverCodeViewLog |
| `Attachment` | jpa | `posting-app` | [Attachment](../domains/entities/Attachment.md) |
| `Carrier` | jpa | `posting-app` | [Company](../domains/entities/Company.md) |
| `CarrierOffer` | jpa | `posting-app` | [Offer](../domains/entities/Offer.md) |
| `CentralDispatchCredentialsEntity` | jpa | `posting-app` | CentralDispatchCredentials |
| `Company` | jpa | `posting-app` | [Company](../domains/entities/Company.md) |
| `CompanySettingsEntity` | jpa | `posting-app` | CompanySettings |
| `Contact` | jpa | `posting-app` | [Contact](../domains/entities/Contact.md) |
| `DateDetail` | jpa | `posting-app` | [DateDetail](../domains/entities/DateDetail.md) |
| `DefaultContactsExclusions` | jpa | `posting-app` | DefaultContactsExclusions |
| `Driveaway` | jpa | `posting-app` | Driveaway |
| `DriveawayDriver` | jpa | `posting-app` | [Driver](../domains/entities/Driver.md) |
| `Driver` | jpa | `posting-app` | [Driver](../domains/entities/Driver.md) |
| `Load` | jpa | `posting-app` | [Load](../domains/entities/Load.md) |
| `LoadLeg` | jpa | `posting-app` | [Load](../domains/entities/Load.md) |
| `LoadLegPostingJob` | jpa | `posting-app` | LoadLegPostingJob |
| `Location` | jpa | `posting-app` | [Location](../domains/entities/Location.md) |
| `ManagedOrder` | jpa | `posting-app` | ManagedOrder |
| `OutboxMessage` | jpa | `posting-app` | OutboxMessage |
| `Payment` | jpa | `posting-app` | [Transaction](../domains/entities/Transaction.md) |
| `PaymentDetailsEntity` | jpa | `posting-app` | PaymentDetails |
| `PublicLinkInfo` | jpa | `posting-app` | LinkInfo |
| `ReportingLog` | jpa | `posting-app` | ReportingLog |
| `ReportingTemplate` | jpa | `posting-app` | ReportingTemplate |
| `Route` | jpa | `posting-app` | [Trip](../domains/entities/Trip.md) |
| `ShippingItem` | jpa | `posting-app` | ShippingItem |
| `StatusHistoryEntity` | jpa | `posting-app` | StatusHistory |
| `SupportedAccountingLineItemEntity` | jpa | `posting-app` | SupportedAccountingLineItem |
| `UserAccount` | jpa | `posting-app` | [User](../domains/entities/User.md) |
| `Vehicle` | jpa | `posting-app` | [Vehicle](../domains/entities/Vehicle.md) |
| `DefaultContactsExclusionsId` | embedded | `posting-app` | DefaultContactsExclusionsId |
| `AcceptOffer` | dto | `posting-app` | AcceptOffer |
| `AcceptOfferPayloadDto` | dto | `posting-dtos` | AcceptOfferPayload |
| `AccountingLineItemDto` | dto | `posting-dtos` | AccountingLineItem |
| `AccountingLineItemUpdateDto` | dto | `posting-dtos` | AccountingLineItemUpdate |
| `AccountingLineItemsSearchDto` | dto | `posting-dtos` | AccountingLineItemsSearch |
| `ActivityLogDto` | dto | `posting-dtos` | [ActivityLog](../domains/entities/ActivityLog.md) |
| `ActivityLogPagedDto` | dto | `posting-dtos` | ActivityLogPaged |
| `AdditionalVehicleInfoDto` | dto | `posting-dtos` | AdditionalVehicleInfo |
| `ArchiveCompanyLoadLegsVo` | dto | `posting-app` | ArchiveCompanyLoadLegsVo |
| `ArchivePayloadDto` | dto | `posting-dtos` | ArchivePayload |
| `AtgDriverCodeDto` | dto | `posting-dtos` | AtgDriverCode |
| `AttachmentDto` | dto | `posting-app` | [Attachment](../domains/entities/Attachment.md) |
| `AttachmentDto` | dto | `posting-dtos` | [Attachment](../domains/entities/Attachment.md) |
| `AttachmentEventPubSubDto` | dto | `posting-app` | AttachmentEvent |
| `AttachmentLoadboardStatePubSubDto` | dto | `posting-app` | AttachmentLoadboardState |
| `AttachmentMetadataCtmsPubSubDto` | dto | `posting-app` | AttachmentMetadataCtms |
| `AttachmentMetadataDto` | dto | `posting-dtos` | AttachmentMetadata |
| `AttachmentPubSubDto` | dto | `posting-app` | [Attachment](../domains/entities/Attachment.md) |
| `AttachmentsMetadataEmbedded` | dto | `posting-app` | AttachmentsMetadata |
| `BaseAttachmentDto` | dto | `posting-dtos` | BaseAttachment |
| `BaseMessageVo` | dto | `posting-app` | BaseMessageVo |
| `BasicDateDetailDto` | dto | `posting-dtos` | BasicDateDetail |
| `BroadcastReportResultInDto` | dto | `posting-app` | BroadcastReportResultIn |
| `CancelOrderDto` | dto | `posting-app` | CancelOrder |
| `CarrierDirectDispatchDto` | dto | `posting-dtos` | CarrierDirectDispatch |
| `CarrierDto` | dto | `posting-dtos` | [Company](../domains/entities/Company.md) |
| `CarrierInfoDto` | dto | `posting-app` | CarrierInfo |
| `CarrierOfferDto` | dto | `posting-app` | [Offer](../domains/entities/Offer.md) |
| `CarrierOfferDto` | dto | `posting-dtos` | [Offer](../domains/entities/Offer.md) |
| `CarrierPagedDto` | dto | `posting-dtos` | CarrierPaged |
| `CentralDispatchCredentialsDto` | dto | `posting-dtos` | CentralDispatchCredentials |
| `CentralDispatchLoadAndHeadersDto` | dto | `posting-app` | CentralDispatchLoadAndHeaders |
| `CentralDispatchLoadDto` | dto | `posting-app` | CentralDispatchLoad |
| `CentralDispatchLocationDto` | dto | `posting-app` | CentralDispatchLocation |
| `CentralDispatchMarketPlaceDto` | dto | `posting-app` | CentralDispatchMarketPlace |
| `CentralDispatchPaymentDetailsDto` | dto | `posting-app` | CentralDispatchPaymentDetails |
| `CentralDispatchPaymentDto` | dto | `posting-app` | CentralDispatchPayment |
| `CentralDispatchStopDto` | dto | `posting-app` | CentralDispatchStop |
| `CentralDispatchV1LoadDto` | dto | `posting-app` | CentralDispatchV1Load |
| `CentralDispatchV1VehicleDto` | dto | `posting-app` | CentralDispatchV1Vehicle |
| `CentralDispatchVehicleDto` | dto | `posting-app` | CentralDispatchVehicle |
| `ChaseDriverLoadLegDto` | dto | `posting-dtos` | ChaseDriverLoadLeg |
| `CommonVehicleDto` | dto | `posting-dtos` | CommonVehicle |
| `CompanyCreatedEvent` | dto | `posting-app` | CompanyCreatedEvent |
| `CompanyDto` | dto | `posting-dtos` | [Company](../domains/entities/Company.md) |
| `CompanyEventPubSubDto` | dto | `posting-app` | CompanyEvent |
| `CompanyLoadboardDto` | dto | `posting-app` | CompanyLoadboard |
| `CompanySettingsDto` | dto | `posting-dtos` | CompanySettings |
| `ContactDetailsDto` | dto | `posting-dtos` | ContactDetails |
| `ContactDto` | dto | `posting-dtos` | [Contact](../domains/entities/Contact.md) |
| `ContactInformationVo` | dto | `posting-app` | ContactInformationVo |
| `ContactMsgPubSubDto` | dto | `posting-dtos` | ContactMsg |
| `ContactSearchFilter` | dto | `posting-app` | ContactSearchFilter |
| `ContactSearchFilterByNameDto` | dto | `posting-dtos` | ContactSearchFilterByName |
| `ContactSearchFilterDto` | dto | `posting-dtos` | ContactSearchFilter |
| `ContactSummaryDto` | dto | `posting-dtos` | ContactSummary |
| `ContactUpdateDto` | dto | `posting-dtos` | ContactUpdate |
| `ContactsPagedDto` | dto | `posting-dtos` | ContactsPaged |
| `ContactsSummaryPagedDto` | dto | `posting-dtos` | ContactsSummaryPaged |
| `ContractDto` | dto | `posting-dtos` | Contract |
| `ContractPricingCalculationDto` | dto | `posting-dtos` | ContractPricingCalculation |
| `ContractPricingDto` | dto | `posting-dtos` | ContractPricing |
| `ContractPricingPaymentEmbedded` | dto | `posting-app` | ContractPricingPayment |
| `ContractUpdateDto` | dto | `posting-dtos` | ContractUpdate |
| `ConvertDraftLoadDto` | dto | `posting-dtos` | ConvertDraftLoad |
| `CoordinatesDto` | dto | `posting-dtos` | [GpsPosition](../domains/entities/GpsPosition.md) |
| `CoordinatesVO` | dto | `posting-app` | CoordinatesVO |
| `CreateAttachmentResponseDto` | dto | `posting-app` | CreateAttachment |
| `CreateReportInDto` | dto | `posting-app` | CreateReportIn |
| `CreateReportOutDto` | dto | `posting-app` | CreateReportOut |
| `CreateReportWorkflowImpl` | dto | `posting-app` | CreateReportWorkflowImpl |
| `CreateReportingLogInDto` | dto | `posting-app` | CreateReportingLogIn |
| `CsvContactDto` | dto | `posting-dtos` | CsvContact |
| `DashboardFilter` | dto | `posting-app` | DashboardFilter |
| `DashboardLoadLegDto` | dto | `posting-dtos` | DashboardLoadLeg |
| `DashboardLoadLegPagedDto` | dto | `posting-dtos` | DashboardLoadLegPaged |
| `DashboardLoadStatusFilterDto` | dto | `posting-dtos` | DashboardLoadStatusFilter |
| `DashboardLoadStatusInformationDto` | dto | `posting-dtos` | DashboardLoadStatusInformation |
| `DateDetailDto` | dto | `posting-dtos` | [DateDetail](../domains/entities/DateDetail.md) |
| `DateDetailUpdateDto` | dto | `posting-dtos` | DateDetailUpdate |
| `DateDetailVo` | dto | `posting-app` | DateDetailVo |
| `DateDetailsPubSubDto` | dto | `posting-app` | DateDetails |
| `DateFields` | dto | `posting-app` | DateFields |
| `DateRangeDto` | dto | `posting-dtos` | [DateRange](../domains/entities/DateRange.md) |
| `DeleteAttachmentPayload` | dto | `posting-app` | DeleteAttachmentPayload |
| `DispatchPayloadDto` | dto | `posting-dtos` | DispatchPayload |
| `DispatchSheetData` | dto | `posting-app` | DispatchSheetData |
| `DomainsValidatorImpl` | dto | `posting-app` | DomainsValidatorImpl |
| `DriveawayDirectDispatchDto` | dto | `posting-dtos` | DriveawayDirectDispatch |
| `DriveawayDriverDto` | dto | `posting-dtos` | [Driver](../domains/entities/Driver.md) |
| `DriveawayDto` | dto | `posting-dtos` | Driveaway |
| `DriveawayItemOperationDto` | dto | `posting-dtos` | DriveawayItemOperation |
| `DriveawayLoadLegDto` | dto | `posting-dtos` | DriveawayLoadLeg |
| `DriveawayLoadOperationDto` | dto | `posting-dtos` | DriveawayLoadOperation |
| `DriverDto` | dto | `posting-dtos` | [Driver](../domains/entities/Driver.md) |
| `DropdownItemDto` | dto | `posting-dtos` | DropdownItem |
| `DropdownsDto` | dto | `posting-dtos` | Dropdowns |
| `EntityId` | dto | `posting-app` | EntityId |
| `ExternalDriveawayDriverDto` | dto | `posting-app` | [Driver](../domains/entities/Driver.md) |
| `FieldDto` | dto | `posting-dtos` | Field |
| `FileContent` | dto | `posting-app` | [FileContent](../domains/entities/FileContent.md) |
| `FullLoadLegDto` | dto | `posting-dtos` | FullLoadLeg |
| `FullLoadLegPagedDto` | dto | `posting-dtos` | FullLoadLegPaged |
| `GatepassInformation` | dto | `posting-app` | GatepassInformation |
| `InventoryItemVehicleDto` | dto | `posting-dtos` | InventoryItemVehicle |
| `InventoryLoadDto` | dto | `posting-dtos` | InventoryLoad |
| `InventoryLoadPagedDto` | dto | `posting-dtos` | InventoryLoadPaged |
| `InventorySearchFilter` | dto | `posting-app` | InventorySearchFilter |
| `InventoryUnitsLoadWrapper` | dto | `posting-app` | InventoryUnitsLoadWrapper |
| `LineItemCalculationDto` | dto | `posting-dtos` | LineItemCalculation |
| `LineItemEmbedded` | dto | `posting-app` | LineItem |
| `LiveUpdateData` | dto | `posting-app` | LiveUpdateData |
| `LoadBaseDto` | dto | `posting-dtos` | LoadBase |
| `LoadBoardStateInfoPubSubDto` | dto | `posting-app` | LoadBoardStateInfo |
| `LoadBuilderDto` | dto | `posting-dtos` | LoadBuilder |
| `LoadBuilderUnitDto` | dto | `posting-dtos` | LoadBuilderUnit |
| `LoadBuildingResponseData` | dto | `posting-dtos` | LoadBuildingResponseData |
| `LoadDto` | dto | `posting-app` | [Load](../domains/entities/Load.md) |
| `LoadDto` | dto | `posting-dtos` | [Load](../domains/entities/Load.md) |
| `LoadLegBaseDetailsDto` | dto | `posting-dtos` | LoadLegBaseDetails |
| `LoadLegConfigVo` | dto | `posting-app` | LoadLegConfigVo |
| `LoadLegEventPubSubDto` | dto | `posting-app` | LoadLegEvent |
| `LoadLegExpandedBaseDto` | dto | `posting-dtos` | LoadLegExpandedBase |
| `LoadLegGroupCountWrapperDto` | dto | `posting-dtos` | LoadLegGroupCountWrapper |
| `LoadLegGroupInformationDto` | dto | `posting-dtos` | LoadLegGroupInformation |
| `LoadLegInventorySearchDto` | dto | `posting-dtos` | LoadLegInventorySearch |
| `LoadLegLoadboardStatePubSubDto` | dto | `posting-app` | LoadLegLoadboardState |
| `LoadLegMsgPubSubDto` | dto | `posting-dtos` | LoadLegMsg |
| `LoadLegPubSubDto` | dto | `posting-app` | [Load](../domains/entities/Load.md) |
| `LoadLegStateAspect` | dto | `posting-app` | LoadLegStateAspect |
| `LoadLegStatusPubSubDto` | dto | `posting-dtos` | LoadLegStatus |
| `LoadLegUpdateBaseDto` | dto | `posting-dtos` | LoadLegUpdateBase |
| `LoadLegUpdateVo` | dto | `posting-app` | LoadLegUpdateVo |
| `LoadUpdateDto` | dto | `posting-dtos` | LoadUpdate |
| `LoadboardLoad` | dto | `posting-app` | LoadboardLoad |
| `LoadboardSetupDto` | dto | `posting-app` | LoadboardSetup |
| `LoadboardVehicle` | dto | `posting-app` | LoadboardVehicle |
| `LoadboardVehicleDto` | dto | `posting-app` | LoadboardVehicle |
| `LoadboardVehiclePubSubDto` | dto | `posting-app` | LoadboardVehicle |
| `LocationCoordinatesPubSubDto` | dto | `posting-app` | LocationCoordinates |
| `LocationDto` | dto | `posting-dtos` | [Location](../domains/entities/Location.md) |
| `LocationEventPubSubDto` | dto | `posting-app` | LocationEvent |
| `LocationPubSubDto` | dto | `posting-app` | [Location](../domains/entities/Location.md) |
| `LocationStatePubSubDto` | dto | `posting-app` | LocationState |
| `LocationUpdateDto` | dto | `posting-dtos` | LocationUpdate |
| `LocationVo` | dto | `posting-app` | LocationVo |
| `LocationWithCoordinatesDto` | dto | `posting-dtos` | LocationWithCoordinates |
| `M22DamageDto` | dto | `posting-dtos` | M22Damage |
| `M22DamageEmbedded` | dto | `posting-app` | M22Damage |
| `M22DamagePubSubDto` | dto | `posting-app` | M22Damage |
| `ManagedOrderDto` | dto | `posting-dtos` | ManagedOrder |
| `ManagedOrderFacadeImpl` | dto | `posting-app` | ManagedOrderFacadeImpl |
| `ManagedOrderLoadLegDto` | dto | `posting-dtos` | ManagedOrderLoadLeg |
| `ManagedOrderUpdate` | dto | `posting-app` | ManagedOrderUpdate |
| `ManagedOrderUpdateDto` | dto | `posting-dtos` | ManagedOrderUpdate |
| `ManagedOrderVehicleUpdate` | dto | `posting-app` | ManagedOrderVehicleUpdate |
| `ManagedOrderVehicleUpdateDto` | dto | `posting-dtos` | ManagedOrderVehicleUpdate |
| `MediaProxyReplacer` | dto | `posting-app` | MediaProxyReplacer |
| `MediaProxyTransformer` | dto | `posting-app` | MediaProxyTransformer |
| `MergeInventoryUnitsDto` | dto | `posting-dtos` | MergeInventoryUnits |
| `MlBotContactDto` | dto | `posting-dtos` | MlBotContact |
| `MlBotDateDetailsDto` | dto | `posting-dtos` | MlBotDateDetails |
| `MlBotExtractionDto` | dto | `posting-dtos` | MlBotExtraction |
| `MlBotFieldsDto` | dto | `posting-dtos` | MlBotFields |
| `MlBotFileDto` | dto | `posting-dtos` | MlBotFile |
| `MlBotLocationDto` | dto | `posting-dtos` | MlBotLocation |
| `MlBotMessageDataDto` | dto | `posting-dtos` | MlBotMessageData |
| `MlBotMessagePubSubDto` | dto | `posting-dtos` | MlBotMessage |
| `MlBotPickupDeliveryDto` | dto | `posting-dtos` | MlBotPickupDelivery |
| `MlBotRawBodyDto` | dto | `posting-dtos` | MlBotRawBody |
| `MlBotRawDto` | dto | `posting-dtos` | MlBotRaw |
| `MlBotRecipientsDto` | dto | `posting-dtos` | MlBotRecipients |
| `MlBotVehicleDto` | dto | `posting-dtos` | MlBotVehicle |
| `NegotiationEventPubSubDto` | dto | `posting-app` | NegotiationEvent |
| `NegotiationLoadboardStatePubSubDto` | dto | `posting-app` | NegotiationLoadboardState |
| `NegotiationPubSubDto` | dto | `posting-app` | [Negotiation](../domains/entities/Negotiation.md) |
| `OfferDetailsPubSubDto` | dto | `posting-app` | OfferDetails |
| `OfferPubSubDto` | dto | `posting-app` | [Offer](../domains/entities/Offer.md) |
| `OperationDto` | dto | `posting-dtos` | Operation |
| `OrderContactDto` | dto | `posting-dtos` | OrderContact |
| `OrderContactLocationDto` | dto | `posting-dtos` | OrderContactLocation |
| `OrderInfoDto` | dto | `posting-dtos` | OrderInfo |
| `OrderResponseDto` | dto | `posting-dtos` | Order |
| `OrderUpdateVo` | dto | `posting-app` | OrderUpdateVo |
| `OrderVehicleInfoDto` | dto | `posting-dtos` | OrderVehicleInfo |
| `OutboxMessageGroup` | dto | `posting-app` | OutboxMessageGroup |
| `OutboxPayload` | dto | `posting-app` | OutboxPayload |
| `PaymentDto` | dto | `posting-dtos` | [Transaction](../domains/entities/Transaction.md) |
| `PaymentInformationDto` | dto | `posting-dtos` | PaymentInformation |
| `PaymentInformationEmbedded` | dto | `posting-app` | PaymentInformation |
| `PaymentUpdateDto` | dto | `posting-dtos` | PaymentUpdate |
| `PaymentVo` | dto | `posting-app` | PaymentVo |
| `PickupDeliveryLocationDto` | dto | `posting-dtos` | PickupDeliveryLocation |
| `PickupDeliveryLocationVo` | dto | `posting-app` | PickupDeliveryLocationVo |
| `PongDto` | dto | `posting-dtos` | Pong |
| `PossibleDuplicatesDto` | dto | `posting-dtos` | PossibleDuplicates |
| `PostConfigDto` | dto | `posting-app` | PostConfig |
| `PostLoadResponseDto` | dto | `posting-app` | PostLoad |
| `PostPayloadDto` | dto | `posting-dtos` | PostPayload |
| `PostingDto` | dto | `posting-app` | [Posting](../domains/entities/Posting.md) |
| `PostingJob` | dto | `posting-app` | Job |
| `ProviderPropertiesUpdateDto` | dto | `posting-dtos` | ProviderPropertiesUpdate |
| `PubSubActionDataDto` | dto | `posting-dtos` | PubSubActionData |
| `PublicLinkInfoDto` | dto | `posting-dtos` | LinkInfo |
| `PublicLinkMessageVO` | dto | `posting-app` | LinkMessageVO |
| `QuoteManagerUpdateEventPubSubDto` | dto | `posting-app` | QuoteManagerUpdateEvent |
| `Rate` | dto | `posting-app` | Rate |
| `RateDto` | dto | `posting-dtos` | Rate |
| `RateInformation` | dto | `posting-app` | RateInformation |
| `RateInformationDto` | dto | `posting-dtos` | RateInformation |
| `RateInformationRouteDto` | dto | `posting-dtos` | RateInformationRoute |
| `ReAssignDriveawayDriverPayloadDto` | dto | `posting-dtos` | ReAssignDriveawayDriverPayload |
| `ReportCsvVo` | dto | `posting-app` | ReportCsvVo |
| `ReportDto` | dto | `posting-dtos` | Report |
| `ReportFilterDto` | dto | `posting-dtos` | ReportFilter |
| `ReportSchedulingDto` | dto | `posting-dtos` | ReportScheduling |
| `ReportSchedulingEmbedded` | dto | `posting-app` | ReportScheduling |
| `ReportVo` | dto | `posting-app` | ReportVo |
| `ReportingLogDto` | dto | `posting-dtos` | ReportingLog |
| `ReportingLogPagedDto` | dto | `posting-dtos` | ReportingLogPaged |
| `ReportingServiceImpl` | dto | `posting-app` | ReportingServiceImpl |
| `ReportingTemplateDto` | dto | `posting-dtos` | ReportingTemplate |
| `ReportingUpdateMessageVo` | dto | `posting-app` | ReportingUpdateMessageVo |
| `RouteDto` | dto | `posting-dtos` | [Trip](../domains/entities/Trip.md) |
| `RouteUpdateDto` | dto | `posting-dtos` | RouteUpdate |
| `SearchFilter` | dto | `posting-app` | SearchFilter |
| `SendReportEmailInDto` | dto | `posting-app` | SendReportEmailIn |
| `ShippingItemAutoImsOutboxPayload` | dto | `posting-app` | ShippingItemAutoImsOutboxPayload |
| `ShippingItemBaseDto` | dto | `posting-dtos` | ShippingItemBase |
| `ShippingItemBaseUpdateDto` | dto | `posting-dtos` | ShippingItemBaseUpdate |
| `ShippingItemBulkStatusUpdateDto` | dto | `posting-dtos` | ShippingItemBulkStatusUpdate |
| `ShippingItemPatchDto` | dto | `posting-dtos` | ShippingItemPatch |
| `ShippingItemWithDriverDto` | dto | `posting-dtos` | ShippingItemWithDriver |
| `StandaloneLoadLegSearchDto` | dto | `posting-dtos` | StandaloneLoadLegSearch |
| `StandardLoadLegDto` | dto | `posting-dtos` | StandardLoadLeg |
| `SupportedAccountingLineItemDto` | dto | `posting-dtos` | SupportedAccountingLineItem |
| `SupportedAccountingLineItemsPagedDto` | dto | `posting-dtos` | SupportedAccountingLineItemsPaged |
| `UndispatchMetadataEmbedded` | dto | `posting-app` | UndispatchMetadata |
| `UndispatchPayloadDto` | dto | `posting-dtos` | UndispatchPayload |
| `UndispatchReasonDto` | dto | `posting-dtos` | UndispatchReason |
| `User` | dto | `posting-app` | [User](../domains/entities/User.md) |
| `UserAccountDto` | dto | `posting-dtos` | [User](../domains/entities/User.md) |
| `UserAccountLoadboardDto` | dto | `posting-app` | UserAccountLoadboard |
| `UserAccountPagedDto` | dto | `posting-dtos` | UserAccountPaged |
| `UserDto` | dto | `posting-dtos` | [User](../domains/entities/User.md) |
| `UserEventPubSubDto` | dto | `posting-app` | UserEvent |
| `V1AccountingLineItemPubSubDto` | dto | `posting-dtos` | AccountingLineItem |
| `V1AttachmentPubSubDto` | dto | `posting-dtos` | [Attachment](../domains/entities/Attachment.md) |
| `V1CarrierOfferPubSubDto` | dto | `posting-dtos` | [Offer](../domains/entities/Offer.md) |
| `V1CarrierPubSubDto` | dto | `posting-dtos` | [Company](../domains/entities/Company.md) |
| `V1ContactPubSubDto` | dto | `posting-dtos` | [Contact](../domains/entities/Contact.md) |
| `V1ContractPubSubDto` | dto | `posting-dtos` | Contract |
| `V1DateDetailDto` | dto | `posting-dtos` | [DateDetail](../domains/entities/DateDetail.md) |
| `V1DateDetailPubSubDto` | dto | `posting-dtos` | [DateDetail](../domains/entities/DateDetail.md) |
| `V1DateRestrictionDto` | dto | `posting-dtos` | DateRestriction |
| `V1DirectDispatchDto` | dto | `posting-dtos` | DirectDispatch |
| `V1DriveawayDriverPubSubDto` | dto | `posting-dtos` | [Driver](../domains/entities/Driver.md) |
| `V1DriveawayPubSubDto` | dto | `posting-dtos` | Driveaway |
| `V1DriverPubSubDto` | dto | `posting-dtos` | [Driver](../domains/entities/Driver.md) |
| `V1LoadLegEventDto` | dto | `posting-dtos` | [Load](../domains/entities/Load.md) |
| `V1LoadLegMsgPubSubDto` | dto | `posting-dtos` | LoadLegMsg |
| `V1LoadLegPubSubDto` | dto | `posting-dtos` | [Load](../domains/entities/Load.md) |
| `V1LoadLegStatusPubSubDto` | dto | `posting-dtos` | LoadLegStatus |
| `V1LoadLegSyncPubSubDto` | dto | `posting-dtos` | LoadLegSync |
| `V1LoadPubSubDto` | dto | `posting-dtos` | [Load](../domains/entities/Load.md) |
| `V1LocationPubSubDto` | dto | `posting-dtos` | [Location](../domains/entities/Location.md) |
| `V1LocationWithCoordinatesPubSubDto` | dto | `posting-dtos` | LocationWithCoordinates |
| `V1OperationalTypeDto` | dto | `posting-dtos` | OperationalType |
| `V1PagedResponseDto` | dto | `posting-dtos` | Paged |
| `V1PagingCriteria` | dto | `posting-app` | PagingCriteria |
| `V1PaymentDto` | dto | `posting-dtos` | [Transaction](../domains/entities/Transaction.md) |
| `V1PaymentMethodDto` | dto | `posting-dtos` | PaymentMethod |
| `V1PaymentPubSubDto` | dto | `posting-dtos` | [Transaction](../domains/entities/Transaction.md) |
| `V1PaymentTermsBeginTypeDto` | dto | `posting-dtos` | PaymentTermsBeginType |
| `V1PaymentTermsTypeDto` | dto | `posting-dtos` | PaymentTermsType |
| `V1PaymentTransactionTypeDto` | dto | `posting-dtos` | PaymentTransactionType |
| `V1PaymentTypeDto` | dto | `posting-dtos` | PaymentType |
| `V1PublicLinkInfoPubSubDto` | dto | `posting-dtos` | LinkInfo |
| `V1RateInformationDto` | dto | `posting-dtos` | RateInformation |
| `V1RouteDto` | dto | `posting-dtos` | [Trip](../domains/entities/Trip.md) |
| `V1RoutePubSubDto` | dto | `posting-dtos` | [Trip](../domains/entities/Trip.md) |
| `V1SearchFilter` | dto | `posting-app` | SearchFilter |
| `V1ShippingItemDto` | dto | `posting-dtos` | ShippingItem |
| `V1ShippingItemPubSubDto` | dto | `posting-dtos` | ShippingItem |
| `V1SortCriteria` | dto | `posting-app` | SortCriteria |
| `V1SortDto` | dto | `posting-dtos` | Sort |
| `V1StandaloneLoadLegBaseDto` | dto | `posting-dtos` | StandaloneLoadLegBase |
| `V1StandaloneLoadLegBasePagedDto` | dto | `posting-dtos` | StandaloneLoadLegBasePaged |
| `V1StandaloneLoadLegDto` | dto | `posting-dtos` | StandaloneLoadLeg |
| `V1UserAccountPubSubDto` | dto | `posting-dtos` | [User](../domains/entities/User.md) |
| `V1VehicleDto` | dto | `posting-dtos` | [Vehicle](../domains/entities/Vehicle.md) |
| `V1VehiclePubSubDto` | dto | `posting-dtos` | [Vehicle](../domains/entities/Vehicle.md) |
| `V2ActivityLogPagedDto` | dto | `posting-dtos` | ActivityLogPaged |
| `V2CarriePagedDto` | dto | `posting-dtos` | CarriePaged |
| `V2CarrierDirectDispatchDto` | dto | `posting-dtos` | CarrierDirectDispatch |
| `V2ContactsPagedDto` | dto | `posting-dtos` | ContactsPaged |
| `V2DriveawayDirectDispatchDto` | dto | `posting-dtos` | DriveawayDirectDispatch |
| `V2InventoryLoadPagedDto` | dto | `posting-dtos` | InventoryLoadPaged |
| `V2LoadLegStatusCountDto` | dto | `posting-dtos` | LoadLegStatusCount |
| `V2LoadLegStatusCountWrapperDto` | dto | `posting-dtos` | LoadLegStatusCountWrapper |
| `V2RouteDto` | dto | `posting-dtos` | [Trip](../domains/entities/Trip.md) |
| `V2StandaloneLoadLegBaseDto` | dto | `posting-dtos` | StandaloneLoadLegBase |
| `V2StandaloneLoadLegBasePagedDto` | dto | `posting-dtos` | StandaloneLoadLegBasePaged |
| `V2StandaloneLoadLegDto` | dto | `posting-dtos` | StandaloneLoadLeg |
| `V2StandaloneLoadLegPagedDto` | dto | `posting-dtos` | StandaloneLoadLegPaged |
| `V3ActivityLogDto` | dto | `posting-dtos` | [ActivityLog](../domains/entities/ActivityLog.md) |
| `V3ActivityLogPagedDto` | dto | `posting-dtos` | ActivityLogPaged |
| `V3CarrierDirectDispatchDto` | dto | `posting-dtos` | CarrierDirectDispatch |
| `V3ContactSearchFilterDto` | dto | `posting-dtos` | ContactSearchFilter |
| `V3DashboardLoadLegDto` | dto | `posting-dtos` | DashboardLoadLeg |
| `V3DashboardLoadLegPagedDto` | dto | `posting-dtos` | DashboardLoadLegPaged |
| `V3DriveawayDirectDispatchDto` | dto | `posting-dtos` | DriveawayDirectDispatch |
| `V3DriveawayLoadLegDto` | dto | `posting-dtos` | DriveawayLoadLeg |
| `V3FullLoadLegDto` | dto | `posting-dtos` | FullLoadLeg |
| `V3FullLoadLegPagedDto` | dto | `posting-dtos` | FullLoadLegPaged |
| `V3LoadLegExpandedBaseDto` | dto | `posting-dtos` | LoadLegExpandedBase |
| `V3ManagedOrderLoadLegDto` | dto | `posting-dtos` | ManagedOrderLoadLeg |
| `V3PubSubObjectDto` | dto | `posting-app` | PubSubObject |
| `V3ReportDto` | dto | `posting-dtos` | Report |
| `V3ReportTemplateDto` | dto | `posting-dtos` | ReportTemplate |
| `V3ReportTemplateFilterDto` | dto | `posting-dtos` | ReportTemplateFilter |
| `V3ShippingItemDto` | dto | `posting-dtos` | ShippingItem |
| `V3StandardLoadLegDto` | dto | `posting-dtos` | StandardLoadLeg |
| `V4DeliveryInvoiceDto` | dto | `posting-dtos` | DeliveryInvoice |
| `V4InvoiceDataDto` | dto | `posting-dtos` | InvoiceData |
| `V4ManagedOrderUpdateDto` | dto | `posting-dtos` | ManagedOrderUpdate |
| `V4ManagedOrderVehicleUpdateDto` | dto | `posting-dtos` | ManagedOrderVehicleUpdate |
| `VehicleChangeEventPubSubDto` | dto | `posting-app` | VehicleChangeEvent |
| `VehicleChangeEventValuesPubSubDto` | dto | `posting-app` | VehicleChangeEventValues |
| `VehicleDto` | dto | `posting-dtos` | [Vehicle](../domains/entities/Vehicle.md) |
| `VehicleIdDetailsPubSubDto` | dto | `posting-app` | VehicleIdDetails |
| `VehicleInformation` | dto | `posting-app` | VehicleInformation |
| `VehicleInformationDto` | dto | `posting-dtos` | VehicleInformation |
| `VehicleLoadboardStatePubSubDto` | dto | `posting-app` | VehicleLoadboardState |
| `VehicleLoadboardStateValuesPubSubDto` | dto | `posting-app` | VehicleLoadboardStateValues |
| `VehicleLoadboardStatusChangePubSubDto` | dto | `posting-app` | VehicleLoadboardStatusChange |
| `VehiclePatchDto` | dto | `posting-dtos` | VehiclePatch |
| `VehiclePubSubDto` | dto | `posting-app` | [Vehicle](../domains/entities/Vehicle.md) |
| `VehicleRevisionPubSubDto` | dto | `posting-app` | VehicleRevision |
| `VehicleRevisionValuesPubSubDto` | dto | `posting-app` | VehicleRevisionValues |
| `VehicleUpdateDto` | dto | `posting-dtos` | VehicleUpdate |
| `VehicleValuePubSubDto` | dto | `posting-app` | VehicleValue |
<!-- entities-end -->
