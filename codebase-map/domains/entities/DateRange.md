---
entity: DateRange
aliases: [DateRange, DateRangeDto, DateRangeReadDto]
status: auto-generated
domains: [listings-trade, operations, platform]
occurrence-count: 8
variant-count: 8
owning-service: trip-planner
last-extracted-date: 2026-05-15
---

# DateRange

## What it is

TODO: human narrative. 8 variants across 5 repos and 3 domains (listings-trade, operations, platform). Owning service: [`trip-planner`](../../repos/trip-planner.md).

## Variants

| Repo | Class | Kind | Module | Extends | Field count | Module path |
|---|---|---|---|---|---:|---|
| [inventory-backend](../../repos/inventory-backend.md) | `DateRangeDto` | dto | `inventory-dtos` | — | 3 | `inventory-dtos/src/main/java/cars/ship/inventory/dtos/commons/DateRangeDto.java` |
| [loadboard-backend](../../repos/loadboard-backend.md) | `DateRange` | dto | `services` | — | 0 | `services/src/main/java/cars/ship/loadboard/models/DateRange.java` |
| [loadboard-backend](../../repos/loadboard-backend.md) | `DateRangeDto` | dto | `api-dtos` | — | 2 | `api-dtos/src/main/java/cars/ship/loadboard/dtos/DateRangeDto.java` |
| [models-lib](../../repos/models-lib.md) | `DateRangeDto` | dto | `api-dtos` | — | 2 | `api-dtos/src/main/java/cars/ship/modelslib/apidtos/tripplanner/out/DateRangeDto.java` |
| [models-lib](../../repos/models-lib.md) | `DateRangeDto` | dto | `data-models` | — | 2 | `data-models/src/main/java/cars/ship/modelslib/datamodels/DateRangeDto.java` |
| [models-lib](../../repos/models-lib.md) | `DateRangeReadDto` | dto | `read-models` | — | 2 | `read-models/src/main/java/cars/ship/modelslib/readmodels/DateRangeReadDto.java` |
| [posting-backend](../../repos/posting-backend.md) | `DateRangeDto` | dto | `posting-dtos` | — | 2 | `posting-dtos/src/main/java/cars/ship/posting/dtos/DateRangeDto.java` |
| [trip-planner](../../repos/trip-planner.md) | `DateRangeDto` | dto | `api-dtos` | — | 2 | `api-dtos/src/main/java/cars/ship/planner/dtos/out/DateRangeDto.java` |

## Field union / intersection

**Core fields** (present in ≥60% of variants — 4/8 or more):

_(no fields shared by ≥60% of variants — high heterogeneity)_

**Variant-specific fields** (present in <60% of variants, top 30 by spread):

| Field | Repos that declare it |
|---|---|
| `end` | `loadboard-backend`, `models-lib`, `trip-planner` |
| `start` | `loadboard-backend`, `models-lib`, `trip-planner` |
| `endDate` | `posting-backend` |
| `endDateString` | `inventory-backend` |
| `separator` | `inventory-backend` |
| `startDate` | `posting-backend` |
| `startDateString` | `inventory-backend` |

## Use cases

### REST surface

_(no REST endpoints reference this entity in any variant repo)_

### Repository operations

_(no Spring Data / Panache repositories typed on this entity found)_

### Carried by Pub/Sub topics

_(no resolved Pub/Sub schemas reference this entity; check `relations/event-schemas/` for unresolved canonical-dto fields)_

## Cross-references

- Owning service shadow: [`trip-planner`](../../repos/trip-planner.md)
- Domain rollup: [`listings-trade`](../listings-trade.md)
- Domain rollup: [`operations`](../operations.md)
- Domain rollup: [`platform`](../platform.md)
- Master index: [`entity-catalog.md`](../../relations/entity-catalog.md)
