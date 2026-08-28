---
entity: Trip
aliases: [Route, RouteDto, RouteEntity, RouteReadDto, Trip, TripDto, TripEntity, TripEntityReadDto, TripPubSubDto, TripReadDto, V1RouteDto, V1RoutePubSubDto, V2RouteDto]
status: auto-generated
domains: [integrations, listings-trade, operations, platform, pricing-billing]
occurrence-count: 21
variant-count: 21
owning-service: trip-planner
last-extracted-date: 2026-05-15
---

# Trip

## What it is

TODO: human narrative. 21 variants across 6 repos and 5 domains (integrations, listings-trade, operations, platform, pricing-billing). Owning service: [`trip-planner`](../../repos/trip-planner.md).

## Variants

| Repo | Class | Kind | Module | Extends | Field count | Module path |
|---|---|---|---|---|---:|---|
| [cube](../../repos/cube.md) | `Route` | dto | `loadboard` | — | 2 | `loadboard/loadboard-commons/src/main/java/cars/ship/cube/model/Route.java` |
| [cube](../../repos/cube.md) | `TripDto` | dto | `ctms-orders` | — | 3 | `ctms-orders/ctms-orders-dtos/src/main/java/cars/ship/cube/ctms/orders/dtos/out/TripDto.java` |
| [cube](../../repos/cube.md) | `TripReadDto` | dto | `loadboard` | — | 3 | `loadboard/loadboard-dtos/src/main/java/cars/ship/cube/dtos/out/TripReadDto.java` |
| [models-lib](../../repos/models-lib.md) | `RouteDto` | dto | `api-dtos` | — | 3 | `api-dtos/src/main/java/cars/ship/modelslib/apidtos/tripplanner/out/RouteDto.java` |
| [models-lib](../../repos/models-lib.md) | `RouteReadDto` | dto | `read-models` | — | 15 | `read-models/src/main/java/cars/ship/modelslib/readmodels/posting/RouteReadDto.java` |
| [models-lib](../../repos/models-lib.md) | `TripDto` | dto | `api-dtos` | — | 15 | `api-dtos/src/main/java/cars/ship/modelslib/apidtos/tripplanner/out/TripDto.java` |
| [models-lib](../../repos/models-lib.md) | `TripDto` | dto | `data-models` | — | 3 | `data-models/src/main/java/cars/ship/modelslib/datamodels/TripDto.java` |
| [models-lib](../../repos/models-lib.md) | `TripReadDto` | dto | `read-models` | — | 3 | `read-models/src/main/java/cars/ship/modelslib/readmodels/TripReadDto.java` |
| [posting-backend](../../repos/posting-backend.md) | `Route` | jpa | `posting-app` | `BaseEntity` | 10 | `posting-app/src/main/java/cars/ship/shipperlite/posting/domain/model/Route.java` |
| [posting-backend](../../repos/posting-backend.md) | `RouteDto` | dto | `posting-dtos` | — | 17 | `posting-dtos/src/main/java/cars/ship/posting/dtos/RouteDto.java` |
| [posting-backend](../../repos/posting-backend.md) | `V1RouteDto` | dto | `posting-dtos` | — | 7 | `posting-dtos/src/main/java/cars/ship/posting/dtos/deprecated/v1/V1RouteDto.java` |
| [posting-backend](../../repos/posting-backend.md) | `V1RoutePubSubDto` | dto | `posting-dtos` | — | 9 | `posting-dtos/src/main/java/cars/ship/posting/dtos/pubsub/v1/V1RoutePubSubDto.java` |
| [posting-backend](../../repos/posting-backend.md) | `V2RouteDto` | dto | `posting-dtos` | — | 7 | `posting-dtos/src/main/java/cars/ship/posting/dtos/deprecated/v2/V2RouteDto.java` |
| [syncer](../../repos/syncer.md) | `TripEntityReadDto` | dto | `services` | — | 3 | `services/src/main/java/cars/ship/syncer/services/models/TripEntityReadDto.java` |
| [trip-planner](../../repos/trip-planner.md) | `RouteDto` | dto | `api-dtos` | — | 3 | `api-dtos/src/main/java/cars/ship/planner/dtos/out/RouteDto.java` |
| [trip-planner](../../repos/trip-planner.md) | `RouteEntity` | other | `db-entities` | — | 3 | `db-entities/src/main/java/cars/ship/planner/entities/RouteEntity.java` |
| [trip-planner](../../repos/trip-planner.md) | `Trip` | dto | `domain` | `AggregateRoot` | 79 | `domain/src/main/java/cars/ship/planner/domain/trip/Trip.java` |
| [trip-planner](../../repos/trip-planner.md) | `TripDto` | dto | `api-dtos` | — | 17 | `api-dtos/src/main/java/cars/ship/planner/dtos/out/TripDto.java` |
| [trip-planner](../../repos/trip-planner.md) | `TripEntity` | jpa | `db-entities` | `BaseDbEntity` | 19 | `db-entities/src/main/java/cars/ship/planner/entities/TripEntity.java` |
| [trip-planner](../../repos/trip-planner.md) | `TripPubSubDto` | dto | `api-dtos` | — | 6 | `api-dtos/src/main/java/cars/ship/planner/dtos/out/TripPubSubDto.java` |
| [uship-quotes](../../repos/uship-quotes.md) | `RouteDto` | dto | `api-dtos` | — | 0 | `api-dtos/src/main/java/cars/ship/uship/dtos/in/commons/RouteDto.java` |

## Field union / intersection

**Core fields** (present in ≥60% of variants — 12/21 or more):

_(no fields shared by ≥60% of variants — high heterogeneity)_

**Variant-specific fields** (present in <60% of variants, top 30 by spread):

| Field | Repos that declare it |
|---|---|
| `id` | `cube`, `models-lib`, `posting-backend`, `syncer`, `trip-planner` |
| `name` | `cube`, `models-lib`, `syncer`, `trip-planner` |
| `polyline` | `cube`, `models-lib`, `trip-planner` |
| `capacity` | `models-lib`, `trip-planner` |
| `carrierUserManagementId` | `cube`, `models-lib` |
| `deliveryActualDate` | `models-lib`, `posting-backend` |
| `deliveryCarrierEtaDateDetail` | `models-lib`, `posting-backend` |
| `deliveryContractualDateDetail` | `models-lib`, `posting-backend` |
| `deliveryEstimatedDateDetail` | `models-lib`, `posting-backend` |
| `deliveryLocation` | `models-lib`, `posting-backend` |
| `deliveryRequestedDateDetail` | `models-lib`, `posting-backend` |
| `destination` | `models-lib`, `trip-planner` |
| `distanceInMiles` | `models-lib`, `posting-backend` |
| `driver` | `models-lib`, `trip-planner` |
| `endDate` | `models-lib`, `trip-planner` |
| `legs` | `models-lib`, `trip-planner` |
| `loads` | `models-lib`, `trip-planner` |
| `origin` | `models-lib`, `trip-planner` |
| `pickupActualDate` | `models-lib`, `posting-backend` |
| `pickupCarrierEtaDateDetail` | `models-lib`, `posting-backend` |
| `pickupContractualDateDetail` | `models-lib`, `posting-backend` |
| `pickupEstimatedDateDetail` | `models-lib`, `posting-backend` |
| `pickupLocation` | `models-lib`, `posting-backend` |
| `pickupRequestedDateDetail` | `models-lib`, `posting-backend` |
| `plan` | `models-lib`, `trip-planner` |
| `revenue` | `models-lib`, `trip-planner` |
| `route` | `models-lib`, `trip-planner` |
| `startDate` | `models-lib`, `trip-planner` |
| `status` | `models-lib`, `trip-planner` |
| `stops` | `models-lib`, `trip-planner` |

## Use cases

### REST surface

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

_(no Spring Data / Panache repositories typed on this entity found)_

### Carried by Pub/Sub topics

_(no resolved Pub/Sub schemas reference this entity; check `relations/event-schemas/` for unresolved canonical-dto fields)_

## Cross-references

- Owning service shadow: [`trip-planner`](../../repos/trip-planner.md)
- Domain rollup: [`integrations`](../integrations.md)
- Domain rollup: [`listings-trade`](../listings-trade.md)
- Domain rollup: [`operations`](../operations.md)
- Domain rollup: [`platform`](../platform.md)
- Domain rollup: [`pricing-billing`](../pricing-billing.md)
- Master index: [`entity-catalog.md`](../../relations/entity-catalog.md)
