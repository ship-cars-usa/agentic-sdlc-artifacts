---
entity: Load
aliases: [Load, LoadDbEntity, LoadDto, LoadInfo, LoadInfoDbEntity, LoadInfoDto, LoadLeg, LoadLegPubSubDto, LoadReadDto, PublicLoadDto, ShipmentDto, ShipmentModelDto, TripLoadDto, TripLoadEntity, TripLoadOrder, V1LoadLegEventDto, V1LoadLegPubSubDto, V1LoadPubSubDto]
status: auto-generated
domains: [communication, listings-trade, operations, platform]
occurrence-count: 25
variant-count: 25
owning-service: trip-planner
last-extracted-date: 2026-05-15
---

# Load

## What it is

TODO: human narrative. 25 variants across 9 repos and 4 domains (communication, listings-trade, operations, platform). Owning service: [`trip-planner`](../../repos/trip-planner.md).

## Variants

| Repo | Class | Kind | Module | Extends | Field count | Module path |
|---|---|---|---|---|---:|---|
| [driveaway-backend](../../repos/driveaway-backend.md) | `LoadInfo` | dto | `api-dtos` | — | 11 | `api-dtos/src/main/java/cars/ship/driveaway/dtos/loadinfo/LoadInfo.java` |
| [driveaway-backend](../../repos/driveaway-backend.md) | `LoadInfoDbEntity` | jpa | `db-entities` | `BaseDbEntity` | 7 | `db-entities/src/main/java/cars/ship/driveaway/db/entities/load/LoadInfoDbEntity.java` |
| [driveaway-backend](../../repos/driveaway-backend.md) | `PublicLoadDto` | dto | `api-dtos` | — | 6 | `api-dtos/src/main/java/cars/ship/driveaway/dtos/loadinfo/PublicLoadDto.java` |
| [load-recommender](../../repos/load-recommender.md) | `LoadDto` | dto | `api-dtos` | — | 44 | `api-dtos/src/main/java/cars/ship/recommender/dtos/out/LoadDto.java` |
| [loadbuilder-backend](../../repos/loadbuilder-backend.md) | `LoadDbEntity` | other | `db-entities` | `StorageEntity` | 10 | `db-entities/src/main/java/cars/ship/loadbuilder/db/entities/LoadDbEntity.java` |
| [location-provider](../../repos/location-provider.md) | `LoadDto` | dto | `api-dtos` | — | 0 | `api-dtos/src/main/java/cars/ship/locationprovider/dtos/routeoptimization/LoadDto.java` |
| [location-provider](../../repos/location-provider.md) | `ShipmentDto` | dto | `api-dtos` | — | 0 | `api-dtos/src/main/java/cars/ship/locationprovider/dtos/routeoptimization/ShipmentDto.java` |
| [location-provider](../../repos/location-provider.md) | `ShipmentModelDto` | dto | `api-dtos` | — | 0 | `api-dtos/src/main/java/cars/ship/locationprovider/dtos/routeoptimization/ShipmentModelDto.java` |
| [models-lib](../../repos/models-lib.md) | `LoadDto` | dto | `data-models` | — | 255 | `data-models/src/main/java/cars/ship/modelslib/datamodels/LoadDto.java` |
| [models-lib](../../repos/models-lib.md) | `LoadReadDto` | dto | `read-models` | — | 232 | `read-models/src/main/java/cars/ship/modelslib/readmodels/es/LoadReadDto.java` |
| [models-lib](../../repos/models-lib.md) | `LoadReadDto` | dto | `read-models` | — | 9 | `read-models/src/main/java/cars/ship/modelslib/readmodels/posting/LoadReadDto.java` |
| [posting-backend](../../repos/posting-backend.md) | `Load` | jpa | `posting-app` | `BaseEntity` | 13 | `posting-app/src/main/java/cars/ship/shipperlite/posting/domain/model/Load.java` |
| [posting-backend](../../repos/posting-backend.md) | `LoadDto` | dto | `posting-app` | — | 116 | `posting-app/src/main/java/cars/ship/shipperlite/posting/application/adapters/out/clients/dto/loadboard/LoadDto.java` |
| [posting-backend](../../repos/posting-backend.md) | `LoadDto` | dto | `posting-dtos` | `LoadBaseDto` | 8 | `posting-dtos/src/main/java/cars/ship/posting/dtos/LoadDto.java` |
| [posting-backend](../../repos/posting-backend.md) | `LoadLeg` | jpa | `posting-app` | `BaseEntity` | 43 | `posting-app/src/main/java/cars/ship/shipperlite/posting/domain/model/LoadLeg.java` |
| [posting-backend](../../repos/posting-backend.md) | `LoadLegPubSubDto` | dto | `posting-app` | — | 42 | `posting-app/src/main/java/cars/ship/shipperlite/posting/application/adapters/in/pubsub/dto/LoadLegPubSubDto.java` |
| [posting-backend](../../repos/posting-backend.md) | `V1LoadLegEventDto` | dto | `posting-dtos` | — | 1 | `posting-dtos/src/main/java/cars/ship/posting/dtos/pubsub/v1/V1LoadLegEventDto.java` |
| [posting-backend](../../repos/posting-backend.md) | `V1LoadLegPubSubDto` | dto | `posting-dtos` | — | 24 | `posting-dtos/src/main/java/cars/ship/posting/dtos/pubsub/v1/V1LoadLegPubSubDto.java` |
| [posting-backend](../../repos/posting-backend.md) | `V1LoadPubSubDto` | dto | `posting-dtos` | — | 8 | `posting-dtos/src/main/java/cars/ship/posting/dtos/pubsub/v1/V1LoadPubSubDto.java` |
| [public-tracking-backend](../../repos/public-tracking-backend.md) | `LoadInfo` | jpa | `public-tracking-backend` | `BaseEntity` | 5 | `src/main/java/cars/ship/publictracking/domain/model/LoadInfo.java` |
| [public-tracking-backend](../../repos/public-tracking-backend.md) | `LoadInfoDto` | dto | `public-tracking-backend` | — | 0 | `src/main/java/cars/ship/publictracking/application/adapters/in/rest/dtos/LoadInfoDto.java` |
| [pusher](../../repos/pusher.md) | `LoadDto` | dto | `event-listener` | — | 16 | `event-listener/src/main/java/cars/ship/pusher/listener/dtos/in/LoadDto.java` |
| [trip-planner](../../repos/trip-planner.md) | `TripLoadDto` | dto | `api-dtos` | — | 11 | `api-dtos/src/main/java/cars/ship/planner/dtos/out/TripLoadDto.java` |
| [trip-planner](../../repos/trip-planner.md) | `TripLoadEntity` | jpa | `db-entities` | `BaseDbEntity` | 22 | `db-entities/src/main/java/cars/ship/planner/entities/TripLoadEntity.java` |
| [trip-planner](../../repos/trip-planner.md) | `TripLoadOrder` | dto | `domain` | `TripLoadInternal` | 1 | `domain/src/main/java/cars/ship/planner/domain/trip/TripLoadOrder.java` |

## Field union / intersection

**Core fields** (present in ≥60% of variants — 15/25 or more):

_(no fields shared by ≥60% of variants — high heterogeneity)_

**Variant-specific fields** (present in <60% of variants, top 30 by spread):

| Field | Repos that declare it |
|---|---|
| `deliveryCity` | `load-recommender`, `models-lib`, `posting-backend`, `pusher`, `trip-planner` |
| `id` | `driveaway-backend`, `load-recommender`, `models-lib`, `posting-backend`, `trip-planner` |
| `pickupCity` | `load-recommender`, `models-lib`, `posting-backend`, `pusher`, `trip-planner` |
| `shipperLoadId` | `driveaway-backend`, `load-recommender`, `models-lib`, `posting-backend`, `trip-planner` |
| `status` | `load-recommender`, `models-lib`, `posting-backend`, `pusher`, `trip-planner` |
| `companyId` | `driveaway-backend`, `loadbuilder-backend`, `posting-backend`, `public-tracking-backend` |
| `deliveryState` | `load-recommender`, `models-lib`, `posting-backend`, `trip-planner` |
| `pickupState` | `load-recommender`, `models-lib`, `posting-backend`, `trip-planner` |
| `totalPaymentToCarrier` | `load-recommender`, `models-lib`, `pusher`, `trip-planner` |
| `attachments` | `driveaway-backend`, `models-lib`, `posting-backend` |
| `createTime` | `load-recommender`, `models-lib`, `posting-backend` |
| `deliveryContact` | `loadbuilder-backend`, `models-lib`, `posting-backend` |
| `deliveryZip` | `load-recommender`, `models-lib`, `trip-planner` |
| `forceDriverAssignment` | `models-lib`, `posting-backend`, `pusher` |
| `labels` | `load-recommender`, `models-lib`, `posting-backend` |
| `paymentMethod` | `load-recommender`, `models-lib`, `posting-backend` |
| `paymentOnDelivery` | `load-recommender`, `models-lib`, `posting-backend` |
| `paymentOnPickup` | `load-recommender`, `models-lib`, `posting-backend` |
| `paymentTermBegins` | `load-recommender`, `models-lib`, `posting-backend` |
| `pickupContact` | `loadbuilder-backend`, `models-lib`, `posting-backend` |
| `pickupZip` | `load-recommender`, `models-lib`, `trip-planner` |
| `shipperName` | `load-recommender`, `models-lib`, `pusher` |
| `source` | `models-lib`, `posting-backend`, `public-tracking-backend` |
| `trip` | `load-recommender`, `models-lib`, `trip-planner` |
| `type` | `driveaway-backend`, `posting-backend`, `trip-planner` |
| `updateTime` | `load-recommender`, `models-lib`, `posting-backend` |
| `useEnclosedTrailer` | `loadbuilder-backend`, `models-lib`, `posting-backend` |
| `allowCarrierToEditLoads` | `models-lib`, `posting-backend` |
| `atgDriverCode` | `models-lib`, `posting-backend` |
| `atgEnabled` | `models-lib`, `pusher` |

## Use cases

### REST surface

**loadbuilder-backend**:
- `GET /{jobId}/status` — `api-services/src/main/java/cars/ship/loadbuilder/rest/SuggestLoadsController.java`
- `GET /active` — `api-services/src/main/java/cars/ship/loadbuilder/rest/SuggestLoadsController.java`
- `GET /{jobId}` — `api-services/src/main/java/cars/ship/loadbuilder/rest/SuggestLoadsController.java`
- `DELETE /{jobId}` — `api-services/src/main/java/cars/ship/loadbuilder/rest/SuggestLoadsController.java`

**posting-backend**:
- `POST private` — `posting-app/src/main/java/cars/ship/shipperlite/posting/application/adapters/in/web/rest/controller/StandaloneLoadLegG1Controller.java`
- `POST central-dispatch` — `posting-app/src/main/java/cars/ship/shipperlite/posting/application/adapters/in/web/rest/controller/StandaloneLoadLegG1Controller.java`

**public-tracking-backend**:
- `ANY v1/loads` — `src/main/java/cars/ship/publictracking/application/adapters/in/rest/controller/LoadInfoController.java`

**trip-planner**:
- `ANY /{trip-id}` — `api-services/src/main/java/cars/ship/planner/rest/controller/TripController.java`
- `ANY /{trip-id}/plan` — `api-services/src/main/java/cars/ship/planner/rest/controller/TripController.java`
- `ANY /count` — `api-services/src/main/java/cars/ship/planner/rest/controller/TripController.java`
- `ANY /{trip-id}/postings` — `api-services/src/main/java/cars/ship/planner/rest/controller/TripController.java`
- `ANY /{trip-id}/orders` — `api-services/src/main/java/cars/ship/planner/rest/controller/TripController.java`
- `ANY /{trip-id}/candidate` — `api-services/src/main/java/cars/ship/planner/rest/controller/TripController.java`
- `ANY {trip-id}/trip-loads/{trip-load-id}` — `api-services/src/main/java/cars/ship/planner/rest/controller/TripController.java`
- `ANY {trip-id}/loads/{load-id}` — `api-services/src/main/java/cars/ship/planner/rest/controller/TripController.java`
- `ANY {trip-id}/loads/{load-id}/transfer` — `api-services/src/main/java/cars/ship/planner/rest/controller/TripController.java`
- `ANY {trip-id}/candidates/{trip-load-id}/promote` — `api-services/src/main/java/cars/ship/planner/rest/controller/TripController.java`
- `ANY {trip-id}/candidates/{trip-load-id}` — `api-services/src/main/java/cars/ship/planner/rest/controller/TripController.java`
- `ANY {trip-id}/rearrange-stops` — `api-services/src/main/java/cars/ship/planner/rest/controller/TripController.java`
- `ANY {trip-id}/rename` — `api-services/src/main/java/cars/ship/planner/rest/controller/TripController.java`
- `ANY {trip-id}/change-capacity` — `api-services/src/main/java/cars/ship/planner/rest/controller/TripController.java`
- `ANY /{trip-id}/optimize-route` — `api-services/src/main/java/cars/ship/planner/rest/controller/TripController.java`
- `ANY {trip-id}` — `api-services/src/main/java/cars/ship/planner/rest/controller/TripController.java`
- `ANY {trip-id}/email-notifications` — `api-services/src/main/java/cars/ship/planner/rest/controller/TripController.java`

### Repository operations

**driveaway-backend**:
- `db-entities/src/main/java/cars/ship/driveaway/db/entities/load/LoadInfoRepository.java` — `LoadInfoDbEntity`
  - methods: `findByPublicKey()`, `findByPublicKeyAndType()`, `findByLoadIdAndState()`, `findByLoadIdAndCompanyIdAndStateIn()`, `countByStateInAndModifiedAtBefore()`

### Carried by Pub/Sub topics

_(no resolved Pub/Sub schemas reference this entity; check `relations/event-schemas/` for unresolved canonical-dto fields)_

## Cross-references

- Owning service shadow: [`trip-planner`](../../repos/trip-planner.md)
- Domain rollup: [`communication`](../communication.md)
- Domain rollup: [`listings-trade`](../listings-trade.md)
- Domain rollup: [`operations`](../operations.md)
- Domain rollup: [`platform`](../platform.md)
- Master index: [`entity-catalog.md`](../../relations/entity-catalog.md)
