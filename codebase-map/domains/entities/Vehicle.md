---
entity: Vehicle
aliases: [AutoImsUnitDbEntity, AutoImsUnitDto, CtmsVehicleDto, CtmsVehicleEntityReadDto, CtmsVehicleEventDto, CtmsVehiclePubSubDto, CtmsVehicleReadDto, InventoryUnitDbEntity, InventoryUnitDto, PublicTrackingVehicleDto, TruckModelEntity, V1VehicleDto, V1VehiclePubSubDto, Vehicle, VehicleDto, VehicleEntity, VehicleMSRPCacheEntity, VehiclePubSubDto, VehicleReadDto, VehicleRequestPubSubDto, VehicleResponseDto]
status: auto-generated
domains: [communication, integrations, listings-trade, operations, platform, pricing-billing]
occurrence-count: 42
variant-count: 42
owning-service: inventory-backend
last-extracted-date: 2026-05-15
---

# Vehicle

## What it is

TODO: human narrative. 42 variants across 20 repos and 6 domains (communication, integrations, listings-trade, operations, platform, pricing-billing). Owning service: [`inventory-backend`](../../repos/inventory-backend.md).

## Variants

| Repo | Class | Kind | Module | Extends | Field count | Module path |
|---|---|---|---|---|---:|---|
| [autoims-backend](../../repos/autoims-backend.md) | `AutoImsUnitDbEntity` | jpa | `db-entities` | `BaseDbEntity` | 28 | `db-entities/src/main/java/cars/ship/autoims/db/entities/units/AutoImsUnitDbEntity.java` |
| [autoims-backend](../../repos/autoims-backend.md) | `AutoImsUnitDto` | dto | `api-dtos` | — | 0 | `api-dtos/src/main/java/cars/ship/autoims/dtos/units/AutoImsUnitDto.java` |
| [autoims-backend](../../repos/autoims-backend.md) | `VehicleResponseDto` | dto | `autoims-mock` | — | 0 | `autoims-mock/src/main/java/cars/ship/autoims/mock/dto/VehicleResponseDto.java` |
| [contract-pricing-backend](../../repos/contract-pricing-backend.md) | `VehicleDto` | dto | `contract-pricing-dtos` | — | 0 | `contract-pricing-dtos/src/main/java/cars/ship/contractpricing/dtos/VehicleDto.java` |
| [cube](../../repos/cube.md) | `VehicleDto` | dto | `ctms-orders` | `VehicleBaseDto` | 1 | `ctms-orders/ctms-orders-dtos/src/main/java/cars/ship/cube/ctms/orders/dtos/out/VehicleDto.java` |
| [dataone](../../repos/dataone.md) | `TruckModelEntity` | other | `db-entities` | — | 8 | `db-entities/src/main/java/cars/ship/dataone/entities/TruckModelEntity.java` |
| [dataone](../../repos/dataone.md) | `VehicleDto` | dto | `api-dtos` | — | 15 | `api-dtos/src/main/java/cars/ship/dataone/dtos/VehicleDto.java` |
| [driveaway-backend](../../repos/driveaway-backend.md) | `VehicleDto` | dto | `api-dtos` | — | 0 | `api-dtos/src/main/java/cars/ship/driveaway/dtos/decoding/VehicleDto.java` |
| [fraud-detector](../../repos/fraud-detector.md) | `VehicleMSRPCacheEntity` | jpa | `db-entities` | — | 2 | `db-entities/src/main/java/cars/ship/frauddetector/entities/VehicleMSRPCacheEntity.java` |
| [inventory-backend](../../repos/inventory-backend.md) | `InventoryUnitDbEntity` | jpa | `db-entities` | `BaseDbEntity` | 52 | `db-entities/src/main/java/cars/ship/inventory/db/entities/units/InventoryUnitDbEntity.java` |
| [inventory-backend](../../repos/inventory-backend.md) | `InventoryUnitDto` | dto | `inventory-dtos` | — | 94 | `inventory-dtos/src/main/java/cars/ship/inventory/dtos/units/InventoryUnitDto.java` |
| [invoices](../../repos/invoices.md) | `VehicleEntity` | jpa | `db-entities` | `BaseDbEntity` | 8 | `db-entities/src/main/java/cars/ship/invoices/entities/VehicleEntity.java` |
| [load-bookmark-backend](../../repos/load-bookmark-backend.md) | `VehicleDto` | dto | `api-dtos` | — | 6 | `api-dtos/src/main/java/cars/ship/loadbookmark/dtos/VehicleDto.java` |
| [loadboard-backend](../../repos/loadboard-backend.md) | `CtmsVehiclePubSubDto` | dto | `services` | — | 23 | `services/src/main/java/cars/ship/loadboard/dtos/pubsub/CtmsVehiclePubSubDto.java` |
| [loadboard-backend](../../repos/loadboard-backend.md) | `Vehicle` | dto | `services` | — | 17 | `services/src/main/java/cars/ship/loadboard/models/Vehicle.java` |
| [loadboard-backend](../../repos/loadboard-backend.md) | `VehicleDto` | dto | `api-dtos` | — | 14 | `api-dtos/src/main/java/cars/ship/loadboard/dtos/VehicleDto.java` |
| [loadboard-backend](../../repos/loadboard-backend.md) | `VehicleEntity` | jpa | `db-entities` | `BaseEntity` | 8 | `db-entities/src/main/java/cars/ship/loadboard/entities/VehicleEntity.java` |
| [loadboard-backend](../../repos/loadboard-backend.md) | `VehiclePubSubDto` | dto | `api-dtos` | — | 17 | `api-dtos/src/main/java/cars/ship/loadboard/dtos/out/pubsub/VehiclePubSubDto.java` |
| [loadboard-backend](../../repos/loadboard-backend.md) | `VehicleReadDto` | dto | `api-dtos` | — | 17 | `api-dtos/src/main/java/cars/ship/loadboard/dtos/out/VehicleReadDto.java` |
| [loadbuilder-backend](../../repos/loadbuilder-backend.md) | `VehicleDto` | dto | `infra-interfaces` | — | 7 | `infra-interfaces/src/main/java/cars/ship/loadbuilder/infra/quotemanager/dtos/order/VehicleDto.java` |
| [location-history-backend](../../repos/location-history-backend.md) | `VehicleEntity` | jpa | `db-entities` | — | 6 | `db-entities/src/main/java/cars/ship/locationhistory/entities/VehicleEntity.java` |
| [location-provider](../../repos/location-provider.md) | `VehicleDto` | dto | `api-dtos` | — | 0 | `api-dtos/src/main/java/cars/ship/locationprovider/dtos/routeoptimization/VehicleDto.java` |
| [models-lib](../../repos/models-lib.md) | `CtmsVehicleReadDto` | dto | `read-models` | — | 56 | `read-models/src/main/java/cars/ship/modelslib/readmodels/ctms/CtmsVehicleReadDto.java` |
| [models-lib](../../repos/models-lib.md) | `VehicleDto` | dto | `api-dtos` | — | 5 | `api-dtos/src/main/java/cars/ship/modelslib/apidtos/loadbookmark/VehicleDto.java` |
| [models-lib](../../repos/models-lib.md) | `VehicleDto` | dto | `ml-dtos` | — | 0 | `ml-dtos/src/main/java/cars/ship/ml/rateengine/dtos/out/VehicleDto.java` |
| [models-lib](../../repos/models-lib.md) | `VehicleDto` | dto | `data-models` | — | 64 | `data-models/src/main/java/cars/ship/modelslib/datamodels/VehicleDto.java` |
| [models-lib](../../repos/models-lib.md) | `VehicleReadDto` | dto | `read-models` | — | 57 | `read-models/src/main/java/cars/ship/modelslib/readmodels/es/VehicleReadDto.java` |
| [models-lib](../../repos/models-lib.md) | `VehicleReadDto` | dto | `read-models` | — | 13 | `read-models/src/main/java/cars/ship/modelslib/readmodels/posting/VehicleReadDto.java` |
| [posting-backend](../../repos/posting-backend.md) | `V1VehicleDto` | dto | `posting-dtos` | `CommonVehicleDto` | 8 | `posting-dtos/src/main/java/cars/ship/posting/dtos/deprecated/v1/V1VehicleDto.java` |
| [posting-backend](../../repos/posting-backend.md) | `V1VehiclePubSubDto` | dto | `posting-dtos` | — | 22 | `posting-dtos/src/main/java/cars/ship/posting/dtos/pubsub/v1/V1VehiclePubSubDto.java` |
| [posting-backend](../../repos/posting-backend.md) | `Vehicle` | jpa | `posting-app` | `BaseEntity` | 23 | `posting-app/src/main/java/cars/ship/shipperlite/posting/domain/model/Vehicle.java` |
| [posting-backend](../../repos/posting-backend.md) | `VehicleDto` | dto | `posting-dtos` | `CommonVehicleDto` | 13 | `posting-dtos/src/main/java/cars/ship/posting/dtos/VehicleDto.java` |
| [posting-backend](../../repos/posting-backend.md) | `VehiclePubSubDto` | dto | `posting-app` | — | 18 | `posting-app/src/main/java/cars/ship/shipperlite/posting/application/adapters/in/pubsub/dto/VehiclePubSubDto.java` |
| [public-tracking-backend](../../repos/public-tracking-backend.md) | `CtmsVehicleEventDto` | dto | `public-tracking-backend` | — | 1 | `src/main/java/cars/ship/publictracking/application/adapters/in/pubsub/carriertms/dtos/CtmsVehicleEventDto.java` |
| [public-tracking-backend](../../repos/public-tracking-backend.md) | `CtmsVehiclePubSubDto` | dto | `public-tracking-backend` | — | 8 | `src/main/java/cars/ship/publictracking/application/adapters/in/pubsub/carriertms/dtos/CtmsVehiclePubSubDto.java` |
| [public-tracking-backend](../../repos/public-tracking-backend.md) | `PublicTrackingVehicleDto` | dto | `public-tracking-backend` | — | 0 | `src/main/java/cars/ship/publictracking/application/adapters/in/rest/dtos/PublicTrackingVehicleDto.java` |
| [pusher](../../repos/pusher.md) | `VehicleDto` | dto | `event-listener` | — | 2 | `event-listener/src/main/java/cars/ship/pusher/listener/dtos/in/VehicleDto.java` |
| [quote-manager-backend](../../repos/quote-manager-backend.md) | `Vehicle` | jpa | `quote-manager-backend` | `BaseEntity` | 7 | `src/main/java/cars/ship/quotemanager/domain/model/Vehicle.java` |
| [quote-manager-backend](../../repos/quote-manager-backend.md) | `VehicleRequestPubSubDto` | dto | `quote-manager-backend` | — | 8 | `src/main/java/cars/ship/quotemanager/application/adapters/in/pubsub/dto/VehicleRequestPubSubDto.java` |
| [quote-manager-backend](../../repos/quote-manager-backend.md) | `VehicleRequestPubSubDto` | dto | `quote-manager-backend` | — | 8 | `src/main/java/cars/ship/quotemanager/domain/model/vo/VehicleRequestPubSubDto.java` |
| [syncer](../../repos/syncer.md) | `CtmsVehicleEntityReadDto` | dto | `services` | — | 59 | `services/src/main/java/cars/ship/syncer/services/models/entity/ctms/CtmsVehicleEntityReadDto.java` |
| [trip-planner](../../repos/trip-planner.md) | `CtmsVehicleDto` | dto | `infra-interfaces` | — | 0 | `infra-interfaces/src/main/java/cars/ship/planner/infra/ctms/dto/CtmsVehicleDto.java` |

## Field union / intersection

**Core fields** (present in ≥60% of variants — 25/42 or more):

_(no fields shared by ≥60% of variants — high heterogeneity)_

**Variant-specific fields** (present in <60% of variants, top 30 by spread):

| Field | Repos that declare it |
|---|---|
| `year` | `autoims-backend`, `dataone`, `inventory-backend`, `invoices`, `load-bookmark-backend`, `loadboard-backend`, `loadbuilder-backend`, `models-lib`, `posting-backend`, `quote-manager-backend`, `syncer` |
| `make` | `dataone`, `inventory-backend`, `invoices`, `load-bookmark-backend`, `loadboard-backend`, `loadbuilder-backend`, `models-lib`, `posting-backend`, `quote-manager-backend`, `syncer` |
| `id` | `fraud-detector`, `inventory-backend`, `load-bookmark-backend`, `loadboard-backend`, `loadbuilder-backend`, `location-history-backend`, `models-lib`, `posting-backend`, `syncer` |
| `model` | `dataone`, `inventory-backend`, `load-bookmark-backend`, `loadboard-backend`, `loadbuilder-backend`, `models-lib`, `posting-backend`, `quote-manager-backend`, `syncer` |
| `vin` | `autoims-backend`, `inventory-backend`, `loadboard-backend`, `loadbuilder-backend`, `models-lib`, `posting-backend`, `quote-manager-backend`, `syncer` |
| `buyerNumber` | `inventory-backend`, `loadboard-backend`, `models-lib`, `posting-backend`, `syncer` |
| `lotNumber` | `inventory-backend`, `loadboard-backend`, `models-lib`, `posting-backend`, `syncer` |
| `operable` | `load-bookmark-backend`, `loadboard-backend`, `models-lib`, `posting-backend`, `syncer` |
| `operableType` | `autoims-backend`, `inventory-backend`, `models-lib`, `posting-backend`, `quote-manager-backend` |
| `type` | `dataone`, `load-bookmark-backend`, `loadboard-backend`, `models-lib`, `syncer` |
| `attachments` | `cube`, `loadboard-backend`, `models-lib`, `syncer` |
| `bodyType` | `dataone`, `loadbuilder-backend`, `posting-backend`, `quote-manager-backend` |
| `color` | `loadboard-backend`, `models-lib`, `posting-backend`, `syncer` |
| `inventoryUnitId` | `autoims-backend`, `models-lib`, `posting-backend`, `quote-manager-backend` |
| `loadId` | `inventory-backend`, `location-history-backend`, `models-lib`, `syncer` |
| `logo` | `loadboard-backend`, `models-lib`, `posting-backend`, `syncer` |
| `status` | `inventory-backend`, `models-lib`, `posting-backend`, `syncer` |
| `brokerVehicleId` | `loadboard-backend`, `models-lib`, `syncer` |
| `createTime` | `loadboard-backend`, `models-lib`, `syncer` |
| `created` | `loadboard-backend`, `models-lib`, `syncer` |
| `deleting` | `loadboard-backend`, `models-lib`, `syncer` |
| `drivetrain` | `loadboard-backend`, `models-lib`, `syncer` |
| `humanType` | `loadboard-backend`, `models-lib`, `syncer` |
| `m22Damages` | `models-lib`, `posting-backend`, `syncer` |
| `parentVehicleId` | `location-history-backend`, `models-lib`, `syncer` |
| `shipperVehicleId` | `loadboard-backend`, `models-lib`, `syncer` |
| `specificationsData` | `loadboard-backend`, `models-lib`, `syncer` |
| `specificationsYear` | `loadboard-backend`, `models-lib`, `syncer` |
| `stockNumber` | `inventory-backend`, `loadboard-backend`, `posting-backend` |
| `updateTime` | `loadboard-backend`, `models-lib`, `syncer` |

## Use cases

### REST surface

**autoims-backend**:
- `PUT /{id}` — `api-services/src/main/java/cars/ship/autoims/rest/UnitsController.java`
- `GET /{id}` — `api-services/src/main/java/cars/ship/autoims/rest/UnitsController.java`
- `GET /batch` — `api-services/src/main/java/cars/ship/autoims/rest/UnitsController.java`
- `DELETE /{id}` — `api-services/src/main/java/cars/ship/autoims/rest/UnitsController.java`
- `DELETE /{id}/hard` — `api-services/src/main/java/cars/ship/autoims/rest/UnitsController.java`

**dataone**:
- `ANY /trucks` — `resources/src/main/java/cars/ship/dataone/rest/TruckController.java`
- `ANY /powersports` — `resources/src/main/java/cars/ship/dataone/rest/PowerSportsController.java`

**inventory-backend**:
- `POST create` — `api-services/src/main/java/cars/ship/inventory/rest/v1/V1UnitsController.java`
- `PUT /{id}` — `api-services/src/main/java/cars/ship/inventory/rest/v1/V1UnitsController.java`
- `POST /{id}/gatepass` — `api-services/src/main/java/cars/ship/inventory/rest/v1/V1UnitsController.java`
- `POST /{id}/autoims-notes` — `api-services/src/main/java/cars/ship/inventory/rest/v1/V1UnitsController.java`
- `POST /{id}/autoims-notes/system` — `api-services/src/main/java/cars/ship/inventory/rest/v1/V1UnitsController.java`
- `GET /{id}` — `api-services/src/main/java/cars/ship/inventory/rest/v1/V1UnitsController.java`
- `GET /batch` — `api-services/src/main/java/cars/ship/inventory/rest/v1/V1UnitsController.java`
- `POST /put-on-hold` — `api-services/src/main/java/cars/ship/inventory/rest/v1/V1UnitsController.java`
- `POST /release-on-hold` — `api-services/src/main/java/cars/ship/inventory/rest/v1/V1UnitsController.java`
- `POST /added-to-load` — `api-services/src/main/java/cars/ship/inventory/rest/v1/V1UnitsController.java`
- `POST /removed-from-load` — `api-services/src/main/java/cars/ship/inventory/rest/v1/V1UnitsController.java`
- `DELETE /{id}` — `api-services/src/main/java/cars/ship/inventory/rest/v1/V1UnitsController.java`
- `DELETE /{id}/hard` — `api-services/src/main/java/cars/ship/inventory/rest/v1/V1UnitsController.java`
- `DELETE /batch` — `api-services/src/main/java/cars/ship/inventory/rest/v1/V1UnitsController.java`
- `DELETE /batch/hard` — `api-services/src/main/java/cars/ship/inventory/rest/v1/V1UnitsController.java`
- `GET /enums/pickup-locations` — `api-services/src/main/java/cars/ship/inventory/rest/v1/V1UnitsController.java`
- `GET /enums/delivery-locations` — `api-services/src/main/java/cars/ship/inventory/rest/v1/V1UnitsController.java`
- `GET /enums/customers` — `api-services/src/main/java/cars/ship/inventory/rest/v1/V1UnitsController.java`
- `POST /lock` — `api-services/src/main/java/cars/ship/inventory/rest/v1/V1UnitsController.java`
- `POST /unlock` — `api-services/src/main/java/cars/ship/inventory/rest/v1/V1UnitsController.java`

### Repository operations

**autoims-backend**:
- `db-entities/src/main/java/cars/ship/autoims/db/entities/units/AutoImsUnitDbRepository.java` — `AutoImsUnitDbEntity`
  - methods: `findByIdAndActiveIsTrue()`, `findByPublicIdAndActiveIsTrue()`, `findByInventoryUnitIdAndActiveIsTrue()`, `findByExternalIdAndCompanyIdAndActiveIsTrue()`, `findByPublicIdInAndActiveIsTrue()`, `findByExternalIdInAndCompanyIdAndActiveIsTrue()`, `findByCompanyIdAndActiveIsTrue()`, `findByCompanyId()`, `findByCompanyIdAndLastUpdatedFromSystemAfter()`, `findByExternalIdAndCompanyIdAndActive()`, `findByPublicIdAndCompanyId()`, `hardDeleteById()`, `hardDeleteAudById()`

**inventory-backend**:
- `db-entities/src/main/java/cars/ship/inventory/db/entities/units/InventoryUnitDbRepository.java` — `InventoryUnitDbEntity`
  - methods: `findByPublicId()`, `findByPublicIdIn()`, `getInternalId()`, `getAllUnitIds()`, `findDistinctPickupLocations()`, `findDistinctDeliveryLocations()`, `findDistinctCustomers()`, `getAllByModifiedAtBeforeAndGatePassDownloadStatusOrderById()`, `hardDeleteById()`, `hardDeleteAudById()`, `hardDeleteNotesById()`, `hardDeleteNotesAudById()`, `findIdsByActiveFalse()`

**posting-backend**:
- `posting-app/src/main/java/cars/ship/shipperlite/posting/application/adapters/out/repo/VehicleRepository.java` — `Vehicle`
  - methods: `findByLbExternalId()`

### Carried by Pub/Sub topics

_(no resolved Pub/Sub schemas reference this entity; check `relations/event-schemas/` for unresolved canonical-dto fields)_

## Cross-references

- Owning service shadow: [`inventory-backend`](../../repos/inventory-backend.md)
- Domain rollup: [`communication`](../communication.md)
- Domain rollup: [`integrations`](../integrations.md)
- Domain rollup: [`listings-trade`](../listings-trade.md)
- Domain rollup: [`operations`](../operations.md)
- Domain rollup: [`platform`](../platform.md)
- Domain rollup: [`pricing-billing`](../pricing-billing.md)
- Master index: [`entity-catalog.md`](../../relations/entity-catalog.md)
