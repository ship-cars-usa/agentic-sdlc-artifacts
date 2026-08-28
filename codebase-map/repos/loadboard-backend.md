---
repo: loadboard-backend
path: ~/projects/ship-cars-usa/loadboard-backend
stack: Java/Quarkus 3.27.5
domain: listings-trade
shape: multi-module (12 poms)
last-synced-commit: f51207f7a68d3e1f754da610583627c0c0097a9c
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# loadboard-backend

## What it is
Quarkus 3.27.5 / Java 21 (project `0.2.29`) **write side** of the vehicle-transport loadboard marketplace: shippers post loads, carriers claim / dispatch / negotiate. **Three independent PostgreSQL databases**: `primary` (postings, vehicles, negotiations, attachments), `users` (synced from `user-backend`), `ctms` (synced from CTMS Django). **Temporal** (1.28.0) orchestrates async workflows (posting creation, dispatch, claim/negotiate). The read path here is single-posting-by-ID; loadboard search/browse is served out-of-band by `cube` (the CQRS read side over Elasticsearch).

## How it fits
- Consumes API of: `location-provider` (`quarkus.rest-client.location-provider.url`, `application.properties:82`), `media-proxy` (`quarkus.rest-client.media-proxy.url`, line 100), `attachment-backend` (`config.attachment.base-url`/`base-media-url`, lines 94-97), `dataone` (`config.dataone.*`, lines 89-91, vehicle-data lookups), Keycloak (OIDC client `quarkus.oidc-client.*`, lines 64-66). (Note: `metadata` is **not** an upstream — the old doc was wrong.)
- Publishes events to: Pub/Sub `loadboard-events-topic` (line 140), `loadboard-notifications-topic` (line 141), `temporal-workflows-events-topic` (`PUBSUB_LOADBOARD_JOB_EVENTS_TOPIC`, line 142) — all via `PubSubMessagePublisherImpl`; plus `ship.cars.notification.topic` (line 85) for negotiation/stale-posting emails (`NegotiationEmailServiceImpl`, `StalePostingsNotificationSenderServiceImpl`).
- Subscribes to: Pub/Sub `ctms-subscription` (line 137) — the **only** subscription consumed in local Java, by `LoadboardPubSubListener`. `user-subscription` (line 138) and `company-subscription` (line 139) are configured but consumed by the Ship.Cars pubsub/user-sync extension libraries, not local source.
- Owns data store: 3 PostgreSQL datasources with **asymmetric** pools — primary `max-size=${DB_MAX_POOL_SIZE:64}` (line 10), `users` `${DB_UM_MAX_POOL_SIZE:4}` (line 14), `ctms` `${DB_CTMS_MAX_POOL_SIZE:4}` (line 16). (The old doc's "3 × 16 = 48" was wrong.)

## Build / test / run
```
./start-quarkus-dev.sh [-x 8000] [-s]
./mvnw clean test
./mvnw clean verify
./build-native.sh                # or: ./mvnw clean install -Pnative -DskipTests
utils/docker-compose/docker-compose.sh up -d
# 12 poms (root + 11 modules): api-dtos, application, commons, configuration,
#   coverage-report, db-entities, db-syncer, db-migration, resources, services,
#   loadboard-backend-enums
```

## Key abstractions
- `PostingQueryController` — `resources/.../rest/PostingQueryController.java:31,41` — `GET /postings/{id}` → `PostingQueryService.getPosting`.
- `PostingController` — `resources/.../rest/PostingController.java:45-93` — `POST /{id}/claim` (instant booking), `/dispatch`, `/cancel`, `/offer`. Also `NegotiationsController` (`/{id}/accept`, `/cancel`, offer review-status), `AttachmentsController`, `PostingWorkflowsController`, and several `*InternalController`s.
- `PostingWorkflowsService` (+ `impl/PostingWorkflowsServiceImpl`) — `services/.../services/` — orchestrates Temporal workflows for instabook / dispatch.
- `PostingUtilsService` — `services/.../utils/PostingUtilsService.java` — **new (SCP-000, this HEAD)**: validation logic extracted out of `PostingWorkflowsServiceImpl` (see gotchas).
- `LoadboardPubSubListener` — `services/.../services/listeners/LoadboardPubSubListener.java` — `PubSubConsumerBlocking<CtmsMessageObjectDto>` on `ctmsSubscription`; routes by object type (posting/vehicle/negotiation/companylabel) to `PostingSyncService`, `NegotiationSyncService`, `VerifiedBySyncService`.
- `PostingEntity` / `NegotiationEntity` / `VehicleEntity` — `db-entities/.../entities/` — Envers-audited; `active` soft-delete, `allowInstantBooking`, `postedToCarriers` ManyToMany.
- `PostingQueryService` (+ impl) — read-path service; direct DB query.

## Don't-do-here / gotchas
- **No REST-client timeouts (P0).** `location-provider` / `media-proxy` set only `.url`, no `connect-timeout` / `read-timeout`. No `@Retry` / `@CircuitBreaker` / `@Timeout` / `@Fallback` anywhere in source — the async side relies on **Temporal** workflow retry config (`config.temporal.*.max-retries`, `workflow-run-timeout`, ~lines 348-361), not MicroProfile fault-tolerance. Synchronous `location-provider`/`media-proxy` outages cascade through unguarded.
- **Validation now lives in `PostingUtilsService`** (extracted from `PostingWorkflowsServiceImpl` in SCP-000): `validatePostedToCarriers`, `validateCompanyTypeCanMutatePostings`, `validateShipperLoadId`, `validatePostingIsCreatedByShipper`, `validateOwnerIsLb`, `validatePremiumPosting`, `isOwnedByLoadboard`. Add posting-mutation validations here, not back in the workflow service.
- **Read path is ID-only.** Loadboard browse/search is `cube`, not here — there's no pagination scaffolding to extend for bulk reads.
- **Pub/Sub consumer lacks outbox** — `LoadboardPubSubListener` calls sync services directly. CTMS is the truth source (eventual consistency expected), but write idempotency must be enforced inside each `*SyncService`.
- **Asymmetric datasource pools (64 / 4 / 4)** — the `users` and `ctms` pools are tiny; a burst of sync traffic can starve them well before the primary pool. Verify Postgres `max_connections` against replica count.
- **Temporal coupling is strong** — replacing/disabling Temporal would require rewriting posting-creation, dispatch, and claim flows.

## Relevant ADRs / docs
- `CLAUDE.md` + `docs/tech-project-overview.md` — Temporal orchestration, three-database split, instant-booking toggle (`config.loadboard.instant-booking.enabled-by-default`, line 105). (Note: the overview still says "Quarkus 3.27.0"; actual is 3.27.5.)
- `relations/rest-client-registry.md#loadboard-backend` — exact configKeys + URL profiles.
- `~/projects/codebase-map/repos/cube.md` — the loadboard **read** side (ES/CQRS); loadboard-backend is the write side.
- `~/projects/codebase-map/repos/posting-backend.md` — sibling; originates loadboard-bound events synced from CTMS.
- `~/projects/codebase-map/relations/media-url-flows.md` — **originates** the LBv3 attachment media-URL pipeline: uploads once to `attachment-backend`, then publishes `attachment.fileUrl` **verbatim** to `loadboard-events` (hop 1; `PostingPubSubDtoConverter`).


<!-- entities-begin -->
## Entities

Auto-generated by `scripts/cluster_entities.py`. Domain classes declared in this repo:

| Class | Kind | Module | Catalog canonical |
|---|---|---|---|
| `AttachmentEntity` | jpa | `db-entities` | [Attachment](../domains/entities/Attachment.md) |
| `CompanyEntity` | jpa | `db-entities` | [Company](../domains/entities/Company.md) |
| `NegotiationEntity` | jpa | `db-entities` | [Negotiation](../domains/entities/Negotiation.md) |
| `OfferEntity` | jpa | `db-entities` | [Offer](../domains/entities/Offer.md) |
| `PostingEntity` | jpa | `db-entities` | [Posting](../domains/entities/Posting.md) |
| `UserEntity` | jpa | `db-entities` | [User](../domains/entities/User.md) |
| `VehicleEntity` | jpa | `db-entities` | [Vehicle](../domains/entities/Vehicle.md) |
| `VerifiedByEntity` | jpa | `db-entities` | VerifiedBy |
| `AcceptNegotiation` | dto | `services` | AcceptNegotiation |
| `AcceptNegotiationDto` | dto | `services` | AcceptNegotiation |
| `AddRemoveResource` | dto | `services` | AddRemoveResource |
| `Attachment` | dto | `services` | [Attachment](../domains/entities/Attachment.md) |
| `AttachmentDto` | dto | `api-dtos` | [Attachment](../domains/entities/Attachment.md) |
| `AttachmentMetadata` | dto | `services` | AttachmentMetadata |
| `AttachmentMetadataDto` | dto | `api-dtos` | AttachmentMetadata |
| `AttachmentPubSubDto` | dto | `api-dtos` | [Attachment](../domains/entities/Attachment.md) |
| `AttachmentReadDto` | dto | `api-dtos` | [Attachment](../domains/entities/Attachment.md) |
| `AttachmentSyncDto` | dto | `db-syncer` | AttachmentSync |
| `CancelNegotiationData` | dto | `services` | CancelNegotiationData |
| `CarrierDispatchDto` | dto | `api-dtos` | CarrierDispatch |
| `ClaimPostingCtmsDto` | dto | `services` | ClaimPostingCtms |
| `ClaimPostingDto` | dto | `api-dtos` | ClaimPosting |
| `ClaimPostingWorkflowDto` | dto | `services` | ClaimPostingWorkflow |
| `Company` | dto | `services` | [Company](../domains/entities/Company.md) |
| `CompanyLabelSyncDto` | dto | `db-syncer` | CompanyLabelSync |
| `CompanySyncDto` | dto | `db-syncer` | CompanySync |
| `CreateOfferDto` | dto | `services` | CreateOffer |
| `CreatePostingDto` | dto | `services` | CreatePosting |
| `CtmsAddressLocationPubSubDto` | dto | `services` | CtmsAddressLocation |
| `CtmsAttachmentPubSubDto` | dto | `services` | [Attachment](../domains/entities/Attachment.md) |
| `CtmsImagePubSubDto` | dto | `services` | CtmsImage |
| `CtmsLoadBoardClientImpl` | dto | `services` | CtmsLoadBoardClientImpl |
| `CtmsMessageObjectDto` | dto | `services` | CtmsMessageObject |
| `CtmsNegotiationOfferDetailsDto` | dto | `services` | CtmsNegotiationOfferDetails |
| `CtmsNegotiationOfferDto` | dto | `services` | CtmsNegotiationOffer |
| `CtmsNegotiationPubSubDto` | dto | `services` | [Negotiation](../domains/entities/Negotiation.md) |
| `CtmsPostingDetailsPubSubDto` | dto | `services` | CtmsPostingDetails |
| `CtmsPostingIdsRequestDto` | dto | `services` | CtmsPostingIds |
| `CtmsPostingIdsResultDto` | dto | `services` | CtmsPostingIdsResult |
| `CtmsPostingPubSubDto` | dto | `services` | [Posting](../domains/entities/Posting.md) |
| `CtmsSpecificationPubSubDto` | dto | `services` | CtmsSpecification |
| `CtmsSpecificationsPubSubDto` | dto | `services` | CtmsSpecifications |
| `CtmsVehiclePubSubDto` | dto | `services` | [Vehicle](../domains/entities/Vehicle.md) |
| `Customer` | dto | `services` | [Company](../domains/entities/Company.md) |
| `CustomerDto` | dto | `api-dtos` | [Company](../domains/entities/Company.md) |
| `CustomerPubSubDto` | dto | `api-dtos` | [Company](../domains/entities/Company.md) |
| `CustomerReadDto` | dto | `api-dtos` | [Company](../domains/entities/Company.md) |
| `DateRange` | dto | `services` | [DateRange](../domains/entities/DateRange.md) |
| `DateRangeDto` | dto | `api-dtos` | [DateRange](../domains/entities/DateRange.md) |
| `DispatchPostingDto` | dto | `services` | DispatchPosting |
| `DispatchToCarrierData` | dto | `services` | DispatchToCarrierData |
| `DispatchToCarrierDto` | dto | `services` | DispatchToCarrier |
| `LocationDetails` | dto | `services` | LocationDetails |
| `LocationDetailsDto` | dto | `api-dtos` | LocationDetails |
| `LocationDetailsPubSubDto` | dto | `api-dtos` | LocationDetails |
| `LocationDetailsReadDto` | dto | `api-dtos` | LocationDetails |
| `LocationRequest` | dto | `services` | [Location](../domains/entities/Location.md) |
| `Negotiation` | dto | `services` | [Negotiation](../domains/entities/Negotiation.md) |
| `NegotiationCancelDto` | dto | `api-dtos` | NegotiationCancel |
| `NegotiationPubSubDto` | dto | `api-dtos` | [Negotiation](../domains/entities/Negotiation.md) |
| `NegotiationReadDto` | dto | `api-dtos` | [Negotiation](../domains/entities/Negotiation.md) |
| `NegotiationSyncDto` | dto | `db-syncer` | NegotiationSync |
| `Notification` | dto | `services` | Notification |
| `Offer` | dto | `services` | [Offer](../domains/entities/Offer.md) |
| `OfferDetailsDto` | dto | `api-dtos` | OfferDetails |
| `OfferDto` | dto | `api-dtos` | [Offer](../domains/entities/Offer.md) |
| `OfferPubSubDto` | dto | `api-dtos` | [Offer](../domains/entities/Offer.md) |
| `OfferReadDto` | dto | `api-dtos` | [Offer](../domains/entities/Offer.md) |
| `PaymentDetailsDto` | dto | `api-dtos` | PaymentDetails |
| `PaymentDetailsPubSubDto` | dto | `api-dtos` | PaymentDetails |
| `PaymentDetailsReadDto` | dto | `api-dtos` | PaymentDetails |
| `Posting` | dto | `services` | [Posting](../domains/entities/Posting.md) |
| `PostingDto` | dto | `api-dtos` | [Posting](../domains/entities/Posting.md) |
| `PostingInternalFilterDto` | dto | `api-dtos` | PostingInternalFilter |
| `PostingLocationResult` | dto | `services` | PostingLocationResult |
| `PostingOwnerDto` | dto | `api-dtos` | PostingOwner |
| `PostingPubSubDto` | dto | `api-dtos` | [Posting](../domains/entities/Posting.md) |
| `PostingPublicIds` | dto | `services` | PostingPublicIds |
| `PostingReadDto` | dto | `api-dtos` | [Posting](../domains/entities/Posting.md) |
| `PostingSyncDto` | dto | `db-syncer` | PostingSync |
| `PostingWorkflowOutDto` | dto | `services` | PostingWorkflowOut |
| `PubSubMessageDto` | dto | `api-dtos` | PubSubMessage |
| `PublicIdsToGenerateCount` | dto | `services` | IdsToGenerateCount |
| `RemoveFromLoadboardDto` | dto | `services` | RemoveFromLoadboard |
| `SpecificationDto` | dto | `db-syncer` | [VehicleSpecification](../domains/entities/VehicleSpecification.md) |
| `StalePostingNotificationDto` | dto | `services` | StalePostingNotification |
| `StalePostingsNotification` | dto | `services` | StalePostingsNotification |
| `TemporalWorkflowResultDto` | dto | `api-dtos` | TemporalWorkflowResult |
| `UpdatePostingDto` | dto | `services` | UpdatePosting |
| `User` | dto | `services` | [User](../domains/entities/User.md) |
| `UserSyncDto` | dto | `db-syncer` | UserSync |
| `V1VehicleSyncSpecificationDto` | dto | `db-syncer` | VehicleSyncSpecification |
| `V2VehicleSyncSpecificationDto` | dto | `db-syncer` | VehicleSyncSpecification |
| `Vehicle` | dto | `services` | [Vehicle](../domains/entities/Vehicle.md) |
| `VehicleDataRequestDto` | dto | `services` | VehicleData |
| `VehicleDimensionsResultDto` | dto | `services` | VehicleDimensionsResult |
| `VehicleDto` | dto | `api-dtos` | [Vehicle](../domains/entities/Vehicle.md) |
| `VehicleInfoDto` | dto | `services` | VehicleInfo |
| `VehiclePubSubDto` | dto | `api-dtos` | [Vehicle](../domains/entities/Vehicle.md) |
| `VehicleReadDto` | dto | `api-dtos` | [Vehicle](../domains/entities/Vehicle.md) |
| `VehicleSpecification` | dto | `services` | [VehicleSpecification](../domains/entities/VehicleSpecification.md) |
| `VehicleSpecificationDto` | dto | `services` | [VehicleSpecification](../domains/entities/VehicleSpecification.md) |
| `VehicleSpecificationPubSubDto` | dto | `api-dtos` | [VehicleSpecification](../domains/entities/VehicleSpecification.md) |
| `VehicleSpecificationReadDto` | dto | `api-dtos` | [VehicleSpecification](../domains/entities/VehicleSpecification.md) |
| `VehicleSyncDto` | dto | `db-syncer` | VehicleSync |
| `WorkflowEventPubSubDto` | dto | `api-dtos` | WorkflowEvent |
| `WorkflowResult` | dto | `services` | WorkflowResult |
<!-- entities-end -->
