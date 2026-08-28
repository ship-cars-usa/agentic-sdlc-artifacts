---
entity: GpsPosition
aliases: [Coordinates, CoordinatesDto, GeoPointDto, GeoPointEntity, GeoPointReadDto]
status: auto-generated
domains: [integrations, listings-trade, operations, platform]
occurrence-count: 14
variant-count: 14
owning-service: trip-planner
last-extracted-date: 2026-05-15
---

# GpsPosition

## What it is

TODO: human narrative. 14 variants across 7 repos and 4 domains (integrations, listings-trade, operations, platform). Owning service: [`trip-planner`](../../repos/trip-planner.md).

## Variants

| Repo | Class | Kind | Module | Extends | Field count | Module path |
|---|---|---|---|---|---:|---|
| [cube](../../repos/cube.md) | `Coordinates` | dto | `loadboard` | — | 2 | `loadboard/loadboard-commons/src/main/java/cars/ship/cube/model/Coordinates.java` |
| [cube](../../repos/cube.md) | `CoordinatesDto` | dto | `core` | — | 0 | `core/core-dtos/src/main/java/ship/cars/cube/core/dtos/CoordinatesDto.java` |
| [cube](../../repos/cube.md) | `GeoPointDto` | dto | `ctms-orders` | — | 2 | `ctms-orders/ctms-orders-dtos/src/main/java/cars/ship/cube/ctms/orders/dtos/out/GeoPointDto.java` |
| [cube](../../repos/cube.md) | `GeoPointReadDto` | dto | `loadboard` | — | 2 | `loadboard/loadboard-dtos/src/main/java/cars/ship/cube/dtos/out/GeoPointReadDto.java` |
| [cube](../../repos/cube.md) | `GeoPointReadDto` | dto | `core` | — | 2 | `core/core-dtos/src/main/java/ship/cars/cube/core/dtos/GeoPointReadDto.java` |
| [integration-executor](../../repos/integration-executor.md) | `Coordinates` | dto | `event-listener` | — | 0 | `event-listener/src/main/java/cars/ship/integrationexecutor/executors/carsarrive/dtos/Coordinates.java` |
| [location-history-backend](../../repos/location-history-backend.md) | `CoordinatesDto` | dto | `api-dtos` | — | 0 | `api-dtos/src/main/java/cars/ship/locationhistory/dtos/CoordinatesDto.java` |
| [models-lib](../../repos/models-lib.md) | `CoordinatesDto` | dto | `api-dtos` | — | 2 | `api-dtos/src/main/java/cars/ship/modelslib/apidtos/locationhistory/CoordinatesDto.java` |
| [models-lib](../../repos/models-lib.md) | `GeoPointDto` | dto | `api-dtos` | — | 0 | `api-dtos/src/main/java/cars/ship/modelslib/apidtos/tripplanner/GeoPointDto.java` |
| [models-lib](../../repos/models-lib.md) | `GeoPointReadDto` | dto | `read-models` | — | 2 | `read-models/src/main/java/cars/ship/modelslib/readmodels/GeoPointReadDto.java` |
| [posting-backend](../../repos/posting-backend.md) | `CoordinatesDto` | dto | `posting-dtos` | — | 0 | `posting-dtos/src/main/java/cars/ship/posting/dtos/CoordinatesDto.java` |
| [public-tracking-backend](../../repos/public-tracking-backend.md) | `CoordinatesDto` | dto | `public-tracking-backend` | — | 2 | `src/main/java/cars/ship/publictracking/application/adapters/in/pubsub/dtos/location/CoordinatesDto.java` |
| [trip-planner](../../repos/trip-planner.md) | `GeoPointDto` | dto | `api-dtos` | — | 2 | `api-dtos/src/main/java/cars/ship/planner/dtos/out/GeoPointDto.java` |
| [trip-planner](../../repos/trip-planner.md) | `GeoPointEntity` | embedded | `db-entities` | — | 2 | `db-entities/src/main/java/cars/ship/planner/entities/GeoPointEntity.java` |

## Field union / intersection

**Core fields** (present in ≥60% of variants — 8/14 or more):

_(no fields shared by ≥60% of variants — high heterogeneity)_

**Variant-specific fields** (present in <60% of variants, top 30 by spread):

| Field | Repos that declare it |
|---|---|
| `latitude` | `models-lib`, `public-tracking-backend`, `trip-planner` |
| `longitude` | `models-lib`, `public-tracking-backend`, `trip-planner` |
| `lat` | `cube`, `models-lib` |
| `lon` | `cube`, `models-lib` |
| `lng` | `cube` |

## Use cases

### REST surface

_(no REST endpoints reference this entity in any variant repo)_

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
- Master index: [`entity-catalog.md`](../../relations/entity-catalog.md)
