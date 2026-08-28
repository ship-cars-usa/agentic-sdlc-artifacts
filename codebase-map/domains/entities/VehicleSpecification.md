---
entity: VehicleSpecification
aliases: [SpecificationDto, SpecificationReadDto, SpecificationsDto, SpecificationsReadDto, VehicleSpecification, VehicleSpecificationDto, VehicleSpecificationPubSubDto, VehicleSpecificationReadDto]
status: auto-generated
domains: [listings-trade, platform]
occurrence-count: 14
variant-count: 14
owning-service: models-lib
last-extracted-date: 2026-05-15
---

# VehicleSpecification

## What it is

TODO: human narrative. 14 variants across 4 repos and 2 domains (listings-trade, platform). Owning service: [`models-lib`](../../repos/models-lib.md).

## Variants

| Repo | Class | Kind | Module | Extends | Field count | Module path |
|---|---|---|---|---|---:|---|
| [cube](../../repos/cube.md) | `SpecificationDto` | dto | `ctms-orders` | — | 2 | `ctms-orders/ctms-orders-dtos/src/main/java/cars/ship/cube/ctms/orders/dtos/out/SpecificationDto.java` |
| [cube](../../repos/cube.md) | `SpecificationReadDto` | dto | `loadboard` | — | 2 | `loadboard/loadboard-dtos/src/main/java/cars/ship/cube/dtos/out/SpecificationReadDto.java` |
| [cube](../../repos/cube.md) | `SpecificationsDto` | dto | `ctms-orders` | — | 4 | `ctms-orders/ctms-orders-dtos/src/main/java/cars/ship/cube/ctms/orders/dtos/out/SpecificationsDto.java` |
| [cube](../../repos/cube.md) | `SpecificationsReadDto` | dto | `loadboard` | — | 4 | `loadboard/loadboard-dtos/src/main/java/cars/ship/cube/dtos/out/SpecificationsReadDto.java` |
| [inventory-backend](../../repos/inventory-backend.md) | `VehicleSpecificationDto` | dto | `infra-interfaces` | — | 0 | `infra-interfaces/src/main/java/cars/ship/inventory/infra/dataone/dto/VehicleSpecificationDto.java` |
| [loadboard-backend](../../repos/loadboard-backend.md) | `SpecificationDto` | dto | `db-syncer` | — | 2 | `db-syncer/src/main/java/cars/ship/loadboard/sync/models/SpecificationDto.java` |
| [loadboard-backend](../../repos/loadboard-backend.md) | `VehicleSpecification` | dto | `services` | — | 4 | `services/src/main/java/cars/ship/loadboard/models/VehicleSpecification.java` |
| [loadboard-backend](../../repos/loadboard-backend.md) | `VehicleSpecificationDto` | dto | `services` | — | 4 | `services/src/main/java/cars/ship/loadboard/dtos/dataone/VehicleSpecificationDto.java` |
| [loadboard-backend](../../repos/loadboard-backend.md) | `VehicleSpecificationPubSubDto` | dto | `api-dtos` | — | 4 | `api-dtos/src/main/java/cars/ship/loadboard/dtos/out/pubsub/VehicleSpecificationPubSubDto.java` |
| [loadboard-backend](../../repos/loadboard-backend.md) | `VehicleSpecificationReadDto` | dto | `api-dtos` | — | 4 | `api-dtos/src/main/java/cars/ship/loadboard/dtos/out/VehicleSpecificationReadDto.java` |
| [models-lib](../../repos/models-lib.md) | `SpecificationDto` | dto | `data-models` | — | 2 | `data-models/src/main/java/cars/ship/modelslib/datamodels/SpecificationDto.java` |
| [models-lib](../../repos/models-lib.md) | `SpecificationReadDto` | dto | `read-models` | — | 2 | `read-models/src/main/java/cars/ship/modelslib/readmodels/SpecificationReadDto.java` |
| [models-lib](../../repos/models-lib.md) | `SpecificationsDto` | dto | `data-models` | — | 4 | `data-models/src/main/java/cars/ship/modelslib/datamodels/SpecificationsDto.java` |
| [models-lib](../../repos/models-lib.md) | `SpecificationsReadDto` | dto | `read-models` | — | 4 | `read-models/src/main/java/cars/ship/modelslib/readmodels/SpecificationsReadDto.java` |

## Field union / intersection

**Core fields** (present in ≥60% of variants — 8/14 or more):

_(no fields shared by ≥60% of variants — high heterogeneity)_

**Variant-specific fields** (present in <60% of variants, top 30 by spread):

| Field | Repos that declare it |
|---|---|
| `height` | `cube`, `loadboard-backend`, `models-lib` |
| `length` | `cube`, `loadboard-backend`, `models-lib` |
| `max` | `cube`, `loadboard-backend`, `models-lib` |
| `min` | `cube`, `loadboard-backend`, `models-lib` |
| `weight` | `cube`, `loadboard-backend`, `models-lib` |
| `width` | `cube`, `loadboard-backend`, `models-lib` |

## Use cases

### REST surface

_(no REST endpoints reference this entity in any variant repo)_

### Repository operations

_(no Spring Data / Panache repositories typed on this entity found)_

### Carried by Pub/Sub topics

_(no resolved Pub/Sub schemas reference this entity; check `relations/event-schemas/` for unresolved canonical-dto fields)_

## Cross-references

- Owning service shadow: [`models-lib`](../../repos/models-lib.md)
- Domain rollup: [`listings-trade`](../listings-trade.md)
- Domain rollup: [`platform`](../platform.md)
- Master index: [`entity-catalog.md`](../../relations/entity-catalog.md)
