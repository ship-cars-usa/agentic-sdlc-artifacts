---
entity: Filter
aliases: [AutoImsFilterDto, Filter, InventoryFilterDto]
status: auto-generated
domains: [communication, integrations, listings-trade, pricing-billing]
occurrence-count: 5
variant-count: 5
owning-service: inventory-backend
last-extracted-date: 2026-05-15
---

# Filter

## What it is

TODO: human narrative. 5 variants across 5 repos and 4 domains (communication, integrations, listings-trade, pricing-billing). Owning service: [`inventory-backend`](../../repos/inventory-backend.md).

## Variants

| Repo | Class | Kind | Module | Extends | Field count | Module path |
|---|---|---|---|---|---:|---|
| [autoims-backend](../../repos/autoims-backend.md) | `AutoImsFilterDto` | dto | `api-dtos` | — | 0 | `api-dtos/src/main/java/cars/ship/autoims/dtos/units/AutoImsFilterDto.java` |
| [chat-backend](../../repos/chat-backend.md) | `Filter` | dto | `chat-backend` | — | 3 | `src/main/java/cars/ship/shipperlite/chat/domain/model/vo/common/Filter.java` |
| [inventory-backend](../../repos/inventory-backend.md) | `InventoryFilterDto` | dto | `inventory-dtos` | — | 12 | `inventory-dtos/src/main/java/cars/ship/inventory/dtos/units/InventoryFilterDto.java` |
| [quote-manager-backend](../../repos/quote-manager-backend.md) | `Filter` | dto | `quote-manager-backend` | — | 3 | `src/main/java/cars/ship/quotemanager/domain/model/vo/common/Filter.java` |
| [saved-search-handler](../../repos/saved-search-handler.md) | `Filter` | dto | `api-dtos` | — | 1 | `api-dtos/src/main/java/cars/ship/search/dtos/es/Filter.java` |

## Field union / intersection

**Core fields** (present in ≥60% of variants — 3/5 or more):

_(no fields shared by ≥60% of variants — high heterogeneity)_

**Variant-specific fields** (present in <60% of variants, top 30 by spread):

| Field | Repos that declare it |
|---|---|
| `field` | `chat-backend`, `quote-manager-backend` |
| `operator` | `chat-backend`, `quote-manager-backend` |
| `value` | `chat-backend`, `quote-manager-backend` |
| `advanceSearch` | `inventory-backend` |
| `createdAfter` | `inventory-backend` |
| `createdBefore` | `inventory-backend` |
| `customers` | `inventory-backend` |
| `deliveryAddresses` | `inventory-backend` |
| `deliveryDateAfter` | `inventory-backend` |
| `deliveryDateBefore` | `inventory-backend` |
| `modifiedAfter` | `inventory-backend` |
| `modifiedBefore` | `inventory-backend` |
| `percolate` | `saved-search-handler` |
| `pickupAddresses` | `inventory-backend` |
| `shippingDateAfter` | `inventory-backend` |
| `shippingDateBefore` | `inventory-backend` |

## Use cases

### REST surface

**autoims-backend**:
- `PUT /{id}` — `api-services/src/main/java/cars/ship/autoims/rest/UnitsController.java`
- `GET /{id}` — `api-services/src/main/java/cars/ship/autoims/rest/UnitsController.java`
- `GET /batch` — `api-services/src/main/java/cars/ship/autoims/rest/UnitsController.java`
- `DELETE /{id}` — `api-services/src/main/java/cars/ship/autoims/rest/UnitsController.java`
- `DELETE /{id}/hard` — `api-services/src/main/java/cars/ship/autoims/rest/UnitsController.java`

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

_(no Spring Data / Panache repositories typed on this entity found)_

### Carried by Pub/Sub topics

_(no resolved Pub/Sub schemas reference this entity; check `relations/event-schemas/` for unresolved canonical-dto fields)_

## Cross-references

- Owning service shadow: [`inventory-backend`](../../repos/inventory-backend.md)
- Domain rollup: [`communication`](../communication.md)
- Domain rollup: [`integrations`](../integrations.md)
- Domain rollup: [`listings-trade`](../listings-trade.md)
- Domain rollup: [`pricing-billing`](../pricing-billing.md)
- Master index: [`entity-catalog.md`](../../relations/entity-catalog.md)
