---
entity: DateDetail
aliases: [DateDetail, DateDetailDto, DateDetailReadDto, PublicTrackingDateDetailDto, V1DateDetailDto, V1DateDetailPubSubDto]
status: auto-generated
domains: [listings-trade, operations, platform]
occurrence-count: 6
variant-count: 6
owning-service: posting-backend
last-extracted-date: 2026-05-15
---

# DateDetail

## What it is

TODO: human narrative. 6 variants across 3 repos and 3 domains (listings-trade, operations, platform). Owning service: [`posting-backend`](../../repos/posting-backend.md).

## Variants

| Repo | Class | Kind | Module | Extends | Field count | Module path |
|---|---|---|---|---|---:|---|
| [models-lib](../../repos/models-lib.md) | `DateDetailReadDto` | dto | `read-models` | — | 6 | `read-models/src/main/java/cars/ship/modelslib/readmodels/posting/DateDetailReadDto.java` |
| [posting-backend](../../repos/posting-backend.md) | `DateDetail` | jpa | `posting-app` | `BaseEntity` | 5 | `posting-app/src/main/java/cars/ship/shipperlite/posting/domain/model/DateDetail.java` |
| [posting-backend](../../repos/posting-backend.md) | `DateDetailDto` | dto | `posting-dtos` | — | 6 | `posting-dtos/src/main/java/cars/ship/posting/dtos/DateDetailDto.java` |
| [posting-backend](../../repos/posting-backend.md) | `V1DateDetailDto` | dto | `posting-dtos` | — | 4 | `posting-dtos/src/main/java/cars/ship/posting/dtos/deprecated/v1/V1DateDetailDto.java` |
| [posting-backend](../../repos/posting-backend.md) | `V1DateDetailPubSubDto` | dto | `posting-dtos` | — | 6 | `posting-dtos/src/main/java/cars/ship/posting/dtos/pubsub/v1/V1DateDetailPubSubDto.java` |
| [public-tracking-backend](../../repos/public-tracking-backend.md) | `PublicTrackingDateDetailDto` | dto | `public-tracking-backend` | — | 0 | `src/main/java/cars/ship/publictracking/application/adapters/in/rest/dtos/PublicTrackingDateDetailDto.java` |

## Field union / intersection

**Core fields** (present in ≥60% of variants — 3/6 or more):

_(no fields shared by ≥60% of variants — high heterogeneity)_

**Variant-specific fields** (present in <60% of variants, top 30 by spread):

| Field | Repos that declare it |
|---|---|
| `estimatedEndDate` | `models-lib`, `posting-backend` |
| `estimatedStartDate` | `models-lib`, `posting-backend` |
| `id` | `models-lib`, `posting-backend` |
| `reason` | `models-lib`, `posting-backend` |
| `restriction` | `models-lib`, `posting-backend` |
| `timeframe` | `models-lib`, `posting-backend` |

## Use cases

### REST surface

_(no REST endpoints reference this entity in any variant repo)_

### Repository operations

_(no Spring Data / Panache repositories typed on this entity found)_

### Carried by Pub/Sub topics

_(no resolved Pub/Sub schemas reference this entity; check `relations/event-schemas/` for unresolved canonical-dto fields)_

## Cross-references

- Owning service shadow: [`posting-backend`](../../repos/posting-backend.md)
- Domain rollup: [`listings-trade`](../listings-trade.md)
- Domain rollup: [`operations`](../operations.md)
- Domain rollup: [`platform`](../platform.md)
- Master index: [`entity-catalog.md`](../../relations/entity-catalog.md)
