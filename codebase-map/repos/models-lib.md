---
repo: models-lib
path: ~/projects/ship-cars-usa/models-lib
stack: Java 21 / Maven multi-module (5 modules) — `ship.cars.models-lib:models-lib` 1.150.0-SNAPSHOT (Lombok 1.18.36, Jackson 2.17.3)
domain: platform
shape: multi-module
last-synced-commit: a4bd21335eafc6d33a53a23ecf20b46345f9096e
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# models-lib

## What it is
The fleet's **shared Java DTO library** — the wire-format types that flow across service boundaries (REST DTOs, Pub/Sub event DTOs, Elasticsearch index documents). Five modules:

- **`data-models`** — flat catalog of ~35 entity DTOs (`PostingDto`, `LoadDto`, `CompanyDto`, `VehicleDto`, `OfferDto`, `TripDto`, `InvoiceDto`, `MessageDto`, `SocketMessageDto`, `PubsubMessageDto`, …). These are the *base* business-domain shapes.
- **`api-dtos`** — REST API DTOs grouped by consuming service (`savedsearchhandler`, `tripplanner`, `loadbookmark`, `locationhistory`, `integrationexecutor`, `syncer`, `keycloak`) plus a `common` package. The package layout reflects which downstream owns the wire contract.
- **`read-models`** — read-optimized variants (`PostingVehicleReadDto`, `TripReadDto`, `CompanyInfoReadDto`, `OfferDetailsReadDto`, `SpecificationsReadDto`, `LoadLocationSharingStateReadDto`, …) plus an `Indexable` marker. **This is the "ES document" tier** — what `syncer`, `cube`, and `saved-search-handler` actually index.
- **`converters`** — bidirectional converters organized by feature (`loadbookmark`, `posting`, `datatoread`, `utils`). The pipeline that turns `data-models` → `read-models` for indexing.
- **`ml-dtos`** — separate package root (`cars.ship.ml.rateengine.dtos`) for `rateengine` request/response DTOs (`RequestQuoteDto`, `RequestVehicleDto`, `RequestLocationDto`, `RateDto`, `ConfidenceDto`). The Java-side contract for talking to `rateengine`'s Python service.

Versioned **independently** of the Quarkus BOM at `1.150.0-SNAPSHOT` (HEAD) — the version number reflects DTO-shape evolution, not Quarkus releases. Compiles on Java 21; DTOs are Lombok 1.18.36 POJOs serialized with Jackson 2.17.3.

## How it fits

- **Compile-time consumers (17 fleet repos):** `crm-workflows`, `cube`, `fraud-detector`, `integrations-backend`, `invoices`, `load-bookmark-backend`, `load-recommender`, `loadboard-backend`, `location-history-backend`, `payment-backend`, `public-tracking-backend`, `pusher`, `saved-search-handler`, `syncer`, `trip-planner`, plus 2 test-automation repos.
- **Highest-leverage consumers** are the ES-indexing pipeline (`syncer` → `read-models` → ES; `cube` reads ES; `saved-search-handler` reads + percolates). These pull `data-models` + `read-models` + `converters` together.
- **`rateengine` interface** is owned by `ml-dtos` — `payment-backend`, `quote-manager-backend`, `uship-quotes` all reach for these types when talking to rate APIs. When ADR-0005 rewrites `rateengine`, these DTOs are part of the interface contract that has to remain compatible through the cutover (or get bumped to a v2 namespace).
- **Consumes API of:** none.
- **Publishes events to:** none — this is a library; topics that carry these DTOs are defined by the producer services.
- **Owns data store:** none.

## Build / test / run
```
./mvnw clean install -DskipTests        # publishes to local Maven repo
./mvnw test
./build-project.sh
./deploy-project.sh
```

Consumers typically import the whole multi-module hierarchy by depending on individual sub-artifacts:
```xml
<dependency>
  <groupId>ship.cars.models-lib</groupId>
  <artifactId>data-models</artifactId>
  <version>${models-lib.version}</version>
</dependency>
<dependency>
  <groupId>ship.cars.models-lib</groupId>
  <artifactId>read-models</artifactId>
  <version>${models-lib.version}</version>
</dependency>
<dependency>
  <groupId>ship.cars.models-lib</groupId>
  <artifactId>converters</artifactId>
  <version>${models-lib.version}</version>
</dependency>
```

The README mentions a **client-side git hook enforcing Jira-ticket-prefixed commit messages** (`LITE-111` format, or `Merge ...`).

## Key abstractions

- **`PostingDto`, `LoadDto`, `CompanyDto`, `VehicleDto`, `OfferDto`, `TripDto`, `InvoiceDto`** — the seven most-referenced business-domain DTOs. These are the names that show up in nearly every Pub/Sub payload and REST response across the fleet.
- **`PubsubMessageDto`** + **`MessageDto`** + **`SocketMessageDto`** — the canonical envelope types for Pub/Sub events and Socket.IO push messages. The `cars.ship.notification.topic` payload is some shape derived from these.
- **`Indexable` (in `read-models`)** — marker interface for "this DTO is destined for an Elasticsearch index." `syncer`'s bulk-write path keys off this.
- **`*ReadDto` types** — denormalized views of `*Dto` types. The split exists so that the ES indexer doesn't include write-side fields (timestamps, internal status flags) and so callers can evolve the write-side schema without changing the read-side without coordinating a converter update.
- **`converters/datatoread/`** — the data-DTO → read-DTO converters. **This is where the indexing pipeline coupling lives.** A new field added to `LoadDto` that should be searchable requires a parallel addition to `LoadReadDto` (or equivalent) and a converter update. Forgetting either link silently drops the field from ES.
- **`converters/posting/`**, **`converters/loadbookmark/`** — per-feature converter packages (e.g. domain DTO ↔ bookmark DTO ↔ ES doc).
- **`api-dtos/<consumer>/`** — DTOs scoped to a specific consumer. The `keycloak` package is the Keycloak event-payload shape; `tripplanner` is Trip Planner's REST contract; etc. Cleaner separation than putting everything in `data-models`.
- **`ml-dtos/cars.ship.ml.rateengine.dtos.{in,out}/`** — directional split for rateengine. `in/RequestQuoteDto` is what we send; `out/RateDto` + `ConfidenceDto` is what we receive.

## Don't-do-here / gotchas

- **17 services have a compile-time dependency.** A breaking DTO change (renamed field, added required field, removed type, changed nullability via annotations) **forces a fleet-wide recompile-and-redeploy of all 17 consumers**. Treat field names, type signatures, and `@JsonProperty` names as semi-versioned: deprecate first, remove in a later major.
- **`data-models` field renames are doubly costly** because they propagate through `converters` to `read-models`, then through `syncer` into Elasticsearch documents. A renamed field that was indexable means a reindex, not just a recompile.
- **`read-models` and `data-models` must evolve together.** Adding a field to `data-models` without updating the corresponding `*ReadDto` + converter means the field will silently not be indexed — no compile error, no runtime exception, the field just doesn't show up in search results.
- **`ml-dtos` is the contract for `rateengine`.** ADR-0005 plans a Python 3.12 + FastAPI rewrite of `rateengine`; the rewrite must either preserve this Java-side DTO shape on the wire OR introduce a v2 namespace. Don't change `RequestQuoteDto` / `RateDto` field names lightly — `payment-backend`, `quote-manager-backend`, `uship-quotes` are all readers of this shape.
- **Independent versioning (`1.150.0-SNAPSHOT` at HEAD)** means a service can be on Quarkus 3.27.0 / `shipcars-quarkus-bom` 3.27.1-SNAPSHOT but on `models-lib` 1.140.0. Each consumer picks its `${models-lib.version}` separately. This usually doesn't matter because DTOs are append-mostly, but it means **the "current shape" of a DTO depends on which models-lib version each consumer is pinned to**. When investigating a wire-format question across services, check each consumer's `${models-lib.version}` before assuming they agree.
- **`PubsubMessageDto` shape is the Pub/Sub canonical envelope.** Per `quarkus-pubsub`'s `PubSubMessageConverter`, the envelope shape is what serializes; any service publishing or consuming Pub/Sub events transitively depends on this shape's stability.
- **The `keycloak` package under `api-dtos/`** mirrors Keycloak event-payload shapes. Updates to Keycloak (the bundled `keycloak` repo on KC 26.0.5) can require coordinated DTO updates here, because consuming services (`fraud-detector`, `pusher`) parse events via these types.
- **No runtime behavior** — pure POJOs (Lombok-style getters/setters). No validation annotations on most types means the **contract is by-convention, not enforced**. If you want enforcement, add `jakarta.validation` annotations to the DTO and verify both the producer and consumer trigger validation.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/commons.md` — `cars.ship.commons.dtos.*` (e.g. `UserContextDto`, `IDResponseDto`, `PageDto`) live there, **not** here. The two libraries together form the fleet's DTO surface: `commons` for framework-neutral primitives, `models-lib` for business-domain types.
- `~/projects/codebase-map/repos/quarkus-pubsub.md` — `PubSubMessageConverter` serializes types from this repo.
- `~/projects/codebase-map/adr/0005-rateengine-eol-rewrite.md` — `ml-dtos` is the Java-side contract that the rewrite must honor (or version-bump).
- `~/projects/codebase-map/repos/syncer.md` / `cube.md` / `saved-search-handler.md` — the ES-indexing pipeline that consumes `read-models` + `converters`.
- `~/projects/codebase-map/domains/platform.md`.


<!-- entities-begin -->
## Entities

Auto-generated by `scripts/cluster_entities.py`. Domain classes declared in this repo:

| Class | Kind | Module | Catalog canonical |
|---|---|---|---|
| `AccountingLineItemReadDto` | dto | `read-models` | AccountingLineItem |
| `ActivityLogDto` | dto | `data-models` | [ActivityLog](../domains/entities/ActivityLog.md) |
| `ActivityLogReadDto` | dto | `read-models` | [ActivityLog](../domains/entities/ActivityLog.md) |
| `AddressLocationDto` | dto | `api-dtos` | AddressLocation |
| `AddressLocationDto` | dto | `data-models` | AddressLocation |
| `AttachmentDto` | dto | `data-models` | [Attachment](../domains/entities/Attachment.md) |
| `AttachmentReadDto` | dto | `read-models` | [Attachment](../domains/entities/Attachment.md) |
| `AttachmentReadDto` | dto | `read-models` | [Attachment](../domains/entities/Attachment.md) |
| `BasicDateDetailReadDto` | dto | `read-models` | BasicDateDetail |
| `BookmarkChangeDto` | dto | `api-dtos` | BookmarkChange |
| `BookmarkDto` | dto | `api-dtos` | Bookmark |
| `CarrierOfferReadDto` | dto | `read-models` | [Offer](../domains/entities/Offer.md) |
| `CarrierReadDto` | dto | `read-models` | [Company](../domains/entities/Company.md) |
| `CityStateDto` | dto | `api-dtos` | CityState |
| `CompanyBillingDto` | dto | `data-models` | CompanyBilling |
| `CompanyBillingReadDto` | dto | `read-models` | CompanyBilling |
| `CompanyDto` | dto | `data-models` | [Company](../domains/entities/Company.md) |
| `CompanyInfoDto` | dto | `data-models` | CompanyInfo |
| `CompanyInfoReadDto` | dto | `read-models` | CompanyInfo |
| `CompanyLabelDto` | dto | `data-models` | CompanyLabel |
| `CompanyReadDto` | dto | `read-models` | [Company](../domains/entities/Company.md) |
| `CompanyReadDto` | dto | `read-models` | [Company](../domains/entities/Company.md) |
| `CompanyVerifiedByReadDto` | dto | `read-models` | CompanyVerifiedBy |
| `ConfidenceDto` | dto | `ml-dtos` | Confidence |
| `ContactEsReadDto` | dto | `read-models` | ContactEs |
| `ContactReadDto` | dto | `read-models` | [Contact](../domains/entities/Contact.md) |
| `ContextDto` | dto | `api-dtos` | Context |
| `ContractPricingCalculationReadDto` | dto | `read-models` | ContractPricingCalculation |
| `ContractPricingReadDto` | dto | `read-models` | ContractPricing |
| `ContractReadDto` | dto | `read-models` | Contract |
| `CoordinatesDto` | dto | `api-dtos` | [GpsPosition](../domains/entities/GpsPosition.md) |
| `CountDto` | dto | `api-dtos` | Count |
| `CreateLoadCandidateDto` | dto | `api-dtos` | CreateLoadCandidate |
| `CreateTripDto` | dto | `api-dtos` | CreateTrip |
| `CreateTripLoadDto` | dto | `api-dtos` | CreateTripLoad |
| `CtmsActivityLogReadDto` | dto | `read-models` | CtmsActivityLog |
| `CtmsAttachmentReadDto` | dto | `read-models` | [Attachment](../domains/entities/Attachment.md) |
| `CtmsCompanyReadDto` | dto | `read-models` | CtmsCompany |
| `CtmsDamageEntryReadDto` | dto | `read-models` | CtmsDamageEntry |
| `CtmsLoadReadDto` | dto | `read-models` | CtmsLoad |
| `CtmsNegotiationReadDto` | dto | `read-models` | [Negotiation](../domains/entities/Negotiation.md) |
| `CtmsOfferActivityLogReadDto` | dto | `read-models` | CtmsOfferActivityLog |
| `CtmsOfferReadDto` | dto | `read-models` | CtmsOffer |
| `CtmsPostingReadDto` | dto | `read-models` | [Posting](../domains/entities/Posting.md) |
| `CtmsVehicleReadDto` | dto | `read-models` | [Vehicle](../domains/entities/Vehicle.md) |
| `DamageEntryDto` | dto | `data-models` | DamageEntry |
| `DamageEntryReadDto` | dto | `read-models` | DamageEntry |
| `DateDetailReadDto` | dto | `read-models` | [DateDetail](../domains/entities/DateDetail.md) |
| `DateRangeDto` | dto | `api-dtos` | [DateRange](../domains/entities/DateRange.md) |
| `DateRangeDto` | dto | `data-models` | [DateRange](../domains/entities/DateRange.md) |
| `DateRangeReadDto` | dto | `read-models` | [DateRange](../domains/entities/DateRange.md) |
| `DriveawayDriverReadDto` | dto | `read-models` | [Driver](../domains/entities/Driver.md) |
| `DriveawayReadDto` | dto | `read-models` | Driveaway |
| `DriverLocationSharingStateDto` | dto | `api-dtos` | DriverLocationSharingState |
| `DriverReadDto` | dto | `read-models` | [Driver](../domains/entities/Driver.md) |
| `EmailStatusDto` | dto | `data-models` | EmailStatus |
| `EventDto` | dto | `data-models` | — |
| `ExtraObjectDto` | dto | `data-models` | ExtraObject |
| `ExtraObjectReadDto` | dto | `read-models` | ExtraObject |
| `FullLoadLegReadDto` | dto | `read-models` | FullLoadLeg |
| `GeoPointDto` | dto | `api-dtos` | [GpsPosition](../domains/entities/GpsPosition.md) |
| `GeoPointReadDto` | dto | `read-models` | [GpsPosition](../domains/entities/GpsPosition.md) |
| `ImageDto` | dto | `data-models` | Image |
| `ImageReadDto` | dto | `read-models` | Image |
| `InspectionConfigurationCustomPhotosDto` | dto | `data-models` | InspectionConfigurationCustomPhotos |
| `InspectionConfigurationCustomPhotosReadDto` | dto | `read-models` | InspectionConfigurationCustomPhotos |
| `InspectionConfigurationDto` | dto | `data-models` | InspectionConfiguration |
| `InspectionConfigurationReadDto` | dto | `read-models` | InspectionConfiguration |
| `InvoiceDto` | dto | `data-models` | Invoice |
| `InvoiceRevisionDto` | dto | `data-models` | InvoiceRevision |
| `InvoiceServiceDataDto` | dto | `data-models` | InvoiceServiceData |
| `InvoiceServiceDto` | dto | `data-models` | InvoiceService |
| `KeyCloakEventDto` | dto | `api-dtos` | KeyCloak |
| `KeyCloakUserDto` | dto | `api-dtos` | KeyCloakUser |
| `LegDto` | dto | `api-dtos` | Leg |
| `LineItemCalculationReadDto` | dto | `read-models` | LineItemCalculation |
| `LoadDto` | dto | `data-models` | [Load](../domains/entities/Load.md) |
| `LoadLegStatusStateReadDto` | dto | `read-models` | LoadLegStatusState |
| `LoadLocationLogReadDto` | dto | `read-models` | LoadLocationLog |
| `LoadLocationSharingStateDto` | dto | `api-dtos` | LoadLocationSharingState |
| `LoadLocationSharingStateDto` | dto | `data-models` | LoadLocationSharingState |
| `LoadLocationSharingStateReadDto` | dto | `read-models` | LoadLocationSharingState |
| `LoadReadDto` | dto | `read-models` | [Load](../domains/entities/Load.md) |
| `LoadReadDto` | dto | `read-models` | [Load](../domains/entities/Load.md) |
| `LocationDto` | dto | `api-dtos` | [Location](../domains/entities/Location.md) |
| `LocationDto` | dto | `ml-dtos` | [Location](../domains/entities/Location.md) |
| `LocationReadDto` | dto | `read-models` | [Location](../domains/entities/Location.md) |
| `LocationRequestDto` | dto | `data-models` | [Location](../domains/entities/Location.md) |
| `LocationWithCoordinatesReadDto` | dto | `read-models` | LocationWithCoordinates |
| `M22DamagesDto` | dto | `data-models` | M22Damages |
| `ManagedOrderReadDto` | dto | `read-models` | ManagedOrder |
| `MessageDataDto` | dto | `api-dtos` | MessageData |
| `MessageDto` | dto | `data-models` | [Message](../domains/entities/Message.md) |
| `NegotiationDto` | dto | `data-models` | [Negotiation](../domains/entities/Negotiation.md) |
| `NegotiationReadDto` | dto | `read-models` | [Negotiation](../domains/entities/Negotiation.md) |
| `OfferActivityLogDto` | dto | `data-models` | OfferActivityLog |
| `OfferActivityLogReadDto` | dto | `read-models` | OfferActivityLog |
| `OfferDetailsDto` | dto | `data-models` | OfferDetails |
| `OfferDetailsReadDto` | dto | `read-models` | OfferDetails |
| `OfferDto` | dto | `data-models` | [Offer](../domains/entities/Offer.md) |
| `OfferReadDto` | dto | `read-models` | [Offer](../domains/entities/Offer.md) |
| `PaymentReadDto` | dto | `read-models` | [Transaction](../domains/entities/Transaction.md) |
| `PostingDto` | dto | `api-dtos` | [Posting](../domains/entities/Posting.md) |
| `PostingDto` | dto | `data-models` | [Posting](../domains/entities/Posting.md) |
| `PostingReadDto` | dto | `read-models` | [Posting](../domains/entities/Posting.md) |
| `PostingVehicleReadDto` | dto | `read-models` | PostingVehicle |
| `PublicLinkInfoReadDto` | dto | `read-models` | LinkInfo |
| `PubsubMessageDto` | dto | `data-models` | PubsubMessage |
| `RangeDto` | dto | `api-dtos` | Range |
| `RateDto` | dto | `ml-dtos` | Rate |
| `RequestLocationDto` | dto | `ml-dtos` | RequestLocation |
| `RequestQuoteDto` | dto | `ml-dtos` | RequestQuote |
| `RequestVehicleDto` | dto | `ml-dtos` | RequestVehicle |
| `ResultDto` | dto | `api-dtos` | Result |
| `ResultsDto` | dto | `api-dtos` | Results |
| `RouteDto` | dto | `api-dtos` | [Trip](../domains/entities/Trip.md) |
| `RouteReadDto` | dto | `read-models` | [Trip](../domains/entities/Trip.md) |
| `SavedSearchSyncDto` | dto | `api-dtos` | SavedSearchSync |
| `ShippingItemBaseReadDto` | dto | `read-models` | ShippingItemBase |
| `ShippingItemWithDriverReadDto` | dto | `read-models` | ShippingItemWithDriver |
| `SlotDto` | dto | `api-dtos` | Slot |
| `SocketMessageDto` | dto | `data-models` | SocketMessage |
| `SocketMessageObjectDto` | dto | `api-dtos` | SocketMessageObject |
| `SpecificationDto` | dto | `data-models` | [VehicleSpecification](../domains/entities/VehicleSpecification.md) |
| `SpecificationReadDto` | dto | `read-models` | [VehicleSpecification](../domains/entities/VehicleSpecification.md) |
| `SpecificationsDto` | dto | `data-models` | [VehicleSpecification](../domains/entities/VehicleSpecification.md) |
| `SpecificationsReadDto` | dto | `read-models` | [VehicleSpecification](../domains/entities/VehicleSpecification.md) |
| `SpotDto` | dto | `api-dtos` | Spot |
| `SyncMessageDto` | dto | `api-dtos` | SyncMessage |
| `TripDto` | dto | `api-dtos` | [Trip](../domains/entities/Trip.md) |
| `TripDto` | dto | `data-models` | [Trip](../domains/entities/Trip.md) |
| `TripListDto` | dto | `api-dtos` | TripList |
| `TripLoadDto` | dto | `api-dtos` | TripLoad |
| `TripLoadListDto` | dto | `api-dtos` | TripLoadList |
| `TripLoadUpdateDto` | dto | `api-dtos` | TripLoadUpdate |
| `TripReadDto` | dto | `read-models` | [Trip](../domains/entities/Trip.md) |
| `TripStopDto` | dto | `api-dtos` | TripStop |
| `TripStopsDto` | dto | `api-dtos` | TripStops |
| `TripSyncDto` | dto | `api-dtos` | TripSync |
| `TripUpdateDto` | dto | `api-dtos` | TripUpdate |
| `UserAccountReadDto` | dto | `read-models` | [User](../domains/entities/User.md) |
| `UserDto` | dto | `api-dtos` | [User](../domains/entities/User.md) |
| `ValueDto` | dto | `api-dtos` | Value |
| `VehicleDto` | dto | `api-dtos` | [Vehicle](../domains/entities/Vehicle.md) |
| `VehicleDto` | dto | `ml-dtos` | [Vehicle](../domains/entities/Vehicle.md) |
| `VehicleDto` | dto | `data-models` | [Vehicle](../domains/entities/Vehicle.md) |
| `VehicleReadDto` | dto | `read-models` | [Vehicle](../domains/entities/Vehicle.md) |
| `VehicleReadDto` | dto | `read-models` | [Vehicle](../domains/entities/Vehicle.md) |
| `WebhookMessageDto` | dto | `api-dtos` | WebhookMessage |
| `WebhookSettingsDto` | dto | `api-dtos` | WebhookSettings |
<!-- entities-end -->
