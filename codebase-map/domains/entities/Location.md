---
entity: Location
aliases: [AddressDto, Location, LocationDto, LocationEntity, LocationPubSubDto, LocationReadDto, LocationRequest, LocationRequestDto, LocationResponseDto, PublicTrackingLocationDto, V1LocationPubSubDto, V2LocationDto]
status: auto-generated
domains: [communication, integrations, listings-trade, operations, platform, pricing-billing]
occurrence-count: 25
variant-count: 25
owning-service: inventory-backend
last-extracted-date: 2026-05-15
---

# Location

## What it is

TODO: human narrative. 25 variants across 15 repos and 6 domains (communication, integrations, listings-trade, operations, platform, pricing-billing). Owning service: [`inventory-backend`](../../repos/inventory-backend.md).

## Variants

| Repo | Class | Kind | Module | Extends | Field count | Module path |
|---|---|---|---|---|---:|---|
| [autoims-backend](../../repos/autoims-backend.md) | `LocationDto` | dto | `autoims-mock` | — | 0 | `autoims-mock/src/main/java/cars/ship/autoims/mock/dto/LocationDto.java` |
| [contract-pricing-backend](../../repos/contract-pricing-backend.md) | `LocationDto` | dto | `contract-pricing-dtos` | — | 0 | `contract-pricing-dtos/src/main/java/cars/ship/contractpricing/dtos/LocationDto.java` |
| [contract-pricing-backend](../../repos/contract-pricing-backend.md) | `LocationEntity` | jpa | `db-entities` | `BaseDbEntity` | 3 | `db-entities/src/main/java/cars/ship/contractpricing/entities/LocationEntity.java` |
| [cube](../../repos/cube.md) | `LocationDto` | dto | `core` | — | 3 | `core/core-dtos/src/main/java/ship/cars/cube/core/dtos/LocationDto.java` |
| [inventory-backend](../../repos/inventory-backend.md) | `LocationDto` | dto | `inventory-dtos` | — | 0 | `inventory-dtos/src/main/java/cars/ship/inventory/dtos/units/LocationDto.java` |
| [invoices](../../repos/invoices.md) | `LocationEntity` | jpa | `db-entities` | `BaseDbEntity` | 5 | `db-entities/src/main/java/cars/ship/invoices/entities/LocationEntity.java` |
| [loadboard-backend](../../repos/loadboard-backend.md) | `LocationRequest` | dto | `services` | — | 6 | `services/src/main/java/cars/ship/loadboard/temporal/dtos/LocationRequest.java` |
| [location-history-backend](../../repos/location-history-backend.md) | `LocationDto` | dto | `api-dtos` | — | 3 | `api-dtos/src/main/java/cars/ship/locationhistory/dtos/LocationDto.java` |
| [location-history-backend](../../repos/location-history-backend.md) | `LocationResponseDto` | dto | `api-dtos` | — | 0 | `api-dtos/src/main/java/cars/ship/locationhistory/dtos/LocationResponseDto.java` |
| [location-history-backend](../../repos/location-history-backend.md) | `V2LocationDto` | dto | `api-dtos` | — | 0 | `api-dtos/src/main/java/cars/ship/locationhistory/dtos/v2/V2LocationDto.java` |
| [location-provider](../../repos/location-provider.md) | `LocationDto` | dto | `api-dtos` | — | 0 | `api-dtos/src/main/java/cars/ship/locationprovider/dtos/routeoptimization/LocationDto.java` |
| [models-lib](../../repos/models-lib.md) | `LocationDto` | dto | `api-dtos` | — | 2 | `api-dtos/src/main/java/cars/ship/modelslib/apidtos/locationhistory/LocationDto.java` |
| [models-lib](../../repos/models-lib.md) | `LocationDto` | dto | `ml-dtos` | — | 0 | `ml-dtos/src/main/java/cars/ship/ml/rateengine/dtos/out/LocationDto.java` |
| [models-lib](../../repos/models-lib.md) | `LocationReadDto` | dto | `read-models` | — | 1 | `read-models/src/main/java/cars/ship/modelslib/readmodels/posting/LocationReadDto.java` |
| [models-lib](../../repos/models-lib.md) | `LocationRequestDto` | dto | `data-models` | — | 0 | `data-models/src/main/java/cars/ship/modelslib/datamodels/LocationRequestDto.java` |
| [posting-backend](../../repos/posting-backend.md) | `Location` | jpa | `posting-app` | `BaseEntity` | 7 | `posting-app/src/main/java/cars/ship/shipperlite/posting/domain/model/Location.java` |
| [posting-backend](../../repos/posting-backend.md) | `LocationDto` | dto | `posting-dtos` | — | 6 | `posting-dtos/src/main/java/cars/ship/posting/dtos/LocationDto.java` |
| [posting-backend](../../repos/posting-backend.md) | `LocationPubSubDto` | dto | `posting-app` | — | 2 | `posting-app/src/main/java/cars/ship/shipperlite/posting/application/adapters/in/pubsub/dto/location/LocationPubSubDto.java` |
| [posting-backend](../../repos/posting-backend.md) | `V1LocationPubSubDto` | dto | `posting-dtos` | — | 5 | `posting-dtos/src/main/java/cars/ship/posting/dtos/pubsub/v1/V1LocationPubSubDto.java` |
| [public-tracking-backend](../../repos/public-tracking-backend.md) | `PublicTrackingLocationDto` | dto | `public-tracking-backend` | — | 0 | `src/main/java/cars/ship/publictracking/application/adapters/in/rest/dtos/PublicTrackingLocationDto.java` |
| [pusher](../../repos/pusher.md) | `LocationRequestDto` | dto | `event-listener` | — | 0 | `event-listener/src/main/java/cars/ship/pusher/listener/dtos/in/LocationRequestDto.java` |
| [quote-manager-backend](../../repos/quote-manager-backend.md) | `LocationDto` | dto | `quote-manager-backend` | — | 2 | `src/main/java/cars/ship/quotemanager/application/adapters/out/clients/dto/LocationDto.java` |
| [trip-planner](../../repos/trip-planner.md) | `LocationDto` | dto | `api-dtos` | — | 4 | `api-dtos/src/main/java/cars/ship/planner/dtos/LocationDto.java` |
| [uship-quotes](../../repos/uship-quotes.md) | `AddressDto` | dto | `api-dtos` | — | 0 | `api-dtos/src/main/java/cars/ship/uship/dtos/in/commons/AddressDto.java` |
| [uship-quotes](../../repos/uship-quotes.md) | `LocationDto` | dto | `api-dtos` | — | 0 | `api-dtos/src/main/java/cars/ship/uship/dtos/in/commons/LocationDto.java` |

## Field union / intersection

**Core fields** (present in ≥60% of variants — 15/25 or more):

_(no fields shared by ≥60% of variants — high heterogeneity)_

**Variant-specific fields** (present in <60% of variants, top 30 by spread):

| Field | Repos that declare it |
|---|---|
| `city` | `contract-pricing-backend`, `invoices`, `posting-backend`, `trip-planner` |
| `state` | `contract-pricing-backend`, `invoices`, `posting-backend`, `trip-planner` |
| `timestamp` | `cube`, `location-history-backend`, `models-lib`, `posting-backend` |
| `coordinates` | `cube`, `location-history-backend`, `posting-backend` |
| `id` | `models-lib`, `posting-backend` |
| `latitude` | `posting-backend`, `quote-manager-backend` |
| `location` | `models-lib`, `trip-planner` |
| `locationId` | `invoices`, `posting-backend` |
| `longitude` | `posting-backend`, `quote-manager-backend` |
| `status` | `cube`, `location-history-backend` |
| `street` | `invoices`, `posting-backend` |
| `zip` | `contract-pricing-backend`, `trip-planner` |
| `zipCode` | `invoices`, `posting-backend` |
| `deliveryCity` | `loadboard-backend` |
| `deliveryState` | `loadboard-backend` |
| `deliveryZipCode` | `loadboard-backend` |
| `pickupCity` | `loadboard-backend` |
| `pickupState` | `loadboard-backend` |
| `pickupZipCode` | `loadboard-backend` |

## Use cases

### REST surface

**cube**:
- `ANY /{company_id}/{load_id}` — `core/core-resources/src/main/java/ship/cars/cube/rest/locationhistory/LHLogController.java`

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

**location-history-backend**:
- `ANY /history` — `resources/src/main/java/cars/ship/locationhistory/rest/v1/LocationHistoryResource.java`
- `ANY /{company_id}/{load_id}` — `resources/src/main/java/cars/ship/locationhistory/rest/v1/LocationHistoryResource.java`
- `ANY /{company_id}/{load_id}/structured` — `resources/src/main/java/cars/ship/locationhistory/rest/v1/LocationHistoryResource.java`
- `ANY /driver` — `resources/src/main/java/cars/ship/locationhistory/rest/v1/DriverLocationResource.java`
- `ANY /{driver_id}/locations` — `resources/src/main/java/cars/ship/locationhistory/rest/v1/DriverLocationResource.java`
- `ANY /{driver_id}/locations/latest` — `resources/src/main/java/cars/ship/locationhistory/rest/v1/DriverLocationResource.java`
- `ANY /batch/locations/latest` — `resources/src/main/java/cars/ship/locationhistory/rest/v1/DriverLocationResource.java`
- `ANY /load/state` — `resources/src/main/java/cars/ship/locationhistory/rest/v1/LoadLocationSharingStateResource.java`
- `ANY /{company_id}` — `resources/src/main/java/cars/ship/locationhistory/rest/v1/LoadLocationSharingStateResource.java`
- `ANY /driver/{driver_id}` — `resources/src/main/java/cars/ship/locationhistory/rest/v1/DriverUpdateResource.java`
- `ANY /state` — `resources/src/main/java/cars/ship/locationhistory/rest/v1/DriverUpdateResource.java`
- `ANY /start` — `resources/src/main/java/cars/ship/locationhistory/rest/v1/DriverUpdateResource.java`
- `ANY /start/{load_id}` — `resources/src/main/java/cars/ship/locationhistory/rest/v1/DriverUpdateResource.java`
- `ANY /stop` — `resources/src/main/java/cars/ship/locationhistory/rest/v1/DriverUpdateResource.java`
- `ANY /stop/{load_id}` — `resources/src/main/java/cars/ship/locationhistory/rest/v1/DriverUpdateResource.java`
- `ANY /off_duty` — `resources/src/main/java/cars/ship/locationhistory/rest/v1/DriverUpdateResource.java`

### Repository operations

_(no Spring Data / Panache repositories typed on this entity found)_

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
