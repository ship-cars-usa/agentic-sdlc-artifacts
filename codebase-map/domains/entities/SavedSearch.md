---
entity: SavedSearch
aliases: [SavedSearch, SavedSearchDto, SavedSearchEntity, SavedSearchReadDto]
status: auto-generated
domains: [integrations, listings-trade, operations]
occurrence-count: 6
variant-count: 6
owning-service: saved-search-handler
last-extracted-date: 2026-05-15
---

# SavedSearch

## What it is

TODO: human narrative. 6 variants across 3 repos and 3 domains (integrations, listings-trade, operations). Owning service: [`saved-search-handler`](../../repos/saved-search-handler.md).

## Variants

| Repo | Class | Kind | Module | Extends | Field count | Module path |
|---|---|---|---|---|---:|---|
| [saved-search-handler](../../repos/saved-search-handler.md) | `SavedSearch` | dto | `commons` | — | 9 | `commons/src/main/java/cars/ship/search/commons/models/SavedSearch.java` |
| [saved-search-handler](../../repos/saved-search-handler.md) | `SavedSearchDto` | dto | `api-dtos` | — | 6 | `api-dtos/src/main/java/cars/ship/search/dtos/SavedSearchDto.java` |
| [saved-search-handler](../../repos/saved-search-handler.md) | `SavedSearchEntity` | jpa | `db-entities` | — | 9 | `db-entities/src/main/java/cars/ship/search/entities/SavedSearchEntity.java` |
| [syncer](../../repos/syncer.md) | `SavedSearchDto` | dto | `api-dtos` | — | 0 | `api-dtos/src/main/java/cars/ship/syncer/dtos/SavedSearchDto.java` |
| [syncer](../../repos/syncer.md) | `SavedSearchReadDto` | dto | `api-dtos` | — | 2 | `api-dtos/src/main/java/cars/ship/syncer/dtos/SavedSearchReadDto.java` |
| [trip-planner](../../repos/trip-planner.md) | `SavedSearchDto` | dto | `infra-interfaces` | — | 6 | `infra-interfaces/src/main/java/cars/ship/planner/infra/savedsearch/dto/SavedSearchDto.java` |

## Field union / intersection

**Core fields** (present in ≥60% of variants — 3/6 or more):

| Field | Common type | Variants with it |
|---|---|---:|
| `id` | `String` | 3 |

**Variant-specific fields** (present in <60% of variants, top 30 by spread):

| Field | Repos that declare it |
|---|---|
| `createTime` | `saved-search-handler`, `trip-planner` |
| `emailNotification` | `saved-search-handler`, `trip-planner` |
| `name` | `saved-search-handler`, `trip-planner` |
| `queryParams` | `saved-search-handler`, `trip-planner` |
| `updateTime` | `saved-search-handler`, `trip-planner` |
| `esQuery` | `saved-search-handler` |
| `query` | `syncer` |
| `tripId` | `saved-search-handler` |
| `userId` | `saved-search-handler` |

## Use cases

### REST surface

_(no REST endpoints reference this entity in any variant repo)_

### Repository operations

_(no Spring Data / Panache repositories typed on this entity found)_

### Carried by Pub/Sub topics

_(no resolved Pub/Sub schemas reference this entity; check `relations/event-schemas/` for unresolved canonical-dto fields)_

## Cross-references

- Owning service shadow: [`saved-search-handler`](../../repos/saved-search-handler.md)
- Domain rollup: [`integrations`](../integrations.md)
- Domain rollup: [`listings-trade`](../listings-trade.md)
- Domain rollup: [`operations`](../operations.md)
- Master index: [`entity-catalog.md`](../../relations/entity-catalog.md)
