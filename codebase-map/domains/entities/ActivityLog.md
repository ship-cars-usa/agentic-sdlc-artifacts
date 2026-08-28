---
entity: ActivityLog
aliases: [ActivityLog, ActivityLogDto, ActivityLogReadDto, V3ActivityLogDto]
status: auto-generated
domains: [communication, listings-trade, platform]
occurrence-count: 7
variant-count: 7
owning-service: posting-backend
last-extracted-date: 2026-05-15
---

# ActivityLog

## What it is

TODO: human narrative. 7 variants across 4 repos and 3 domains (communication, listings-trade, platform). Owning service: [`posting-backend`](../../repos/posting-backend.md).

## Variants

| Repo | Class | Kind | Module | Extends | Field count | Module path |
|---|---|---|---|---|---:|---|
| [cube](../../repos/cube.md) | `ActivityLogDto` | dto | `ctms-orders` | — | 13 | `ctms-orders/ctms-orders-dtos/src/main/java/cars/ship/cube/ctms/orders/dtos/out/ActivityLogDto.java` |
| [models-lib](../../repos/models-lib.md) | `ActivityLogDto` | dto | `data-models` | — | 25 | `data-models/src/main/java/cars/ship/modelslib/datamodels/ActivityLogDto.java` |
| [models-lib](../../repos/models-lib.md) | `ActivityLogReadDto` | dto | `read-models` | — | 13 | `read-models/src/main/java/cars/ship/modelslib/readmodels/es/ActivityLogReadDto.java` |
| [posting-backend](../../repos/posting-backend.md) | `ActivityLog` | jpa | `posting-app` | `BaseEntity` | 8 | `posting-app/src/main/java/cars/ship/shipperlite/posting/domain/model/ActivityLog.java` |
| [posting-backend](../../repos/posting-backend.md) | `ActivityLogDto` | dto | `posting-dtos` | — | 10 | `posting-dtos/src/main/java/cars/ship/posting/dtos/ActivityLogDto.java` |
| [posting-backend](../../repos/posting-backend.md) | `V3ActivityLogDto` | dto | `posting-dtos` | — | 8 | `posting-dtos/src/main/java/cars/ship/posting/dtos/deprecated/v3/V3ActivityLogDto.java` |
| [pusher](../../repos/pusher.md) | `ActivityLogDto` | dto | `event-listener` | — | 18 | `event-listener/src/main/java/cars/ship/pusher/listener/dtos/in/ActivityLogDto.java` |

## Field union / intersection

**Core fields** (present in ≥60% of variants — 4/7 or more):

| Field | Common type | Variants with it |
|---|---|---:|
| `actorId` | `String` | 4 |
| `id` | `String` | 4 |

**Variant-specific fields** (present in <60% of variants, top 30 by spread):

| Field | Repos that declare it |
|---|---|
| `actorCompanyId` | `cube`, `models-lib`, `pusher` |
| `brokerId` | `cube`, `models-lib`, `pusher` |
| `carrierId` | `cube`, `models-lib`, `pusher` |
| `eventType` | `cube`, `models-lib`, `pusher` |
| `eventTypeCategory` | `cube`, `models-lib`, `pusher` |
| `extraObject` | `cube`, `models-lib`, `pusher` |
| `loadId` | `cube`, `models-lib`, `pusher` |
| `orderId` | `cube`, `models-lib`, `pusher` |
| `shipperId` | `cube`, `models-lib`, `pusher` |
| `timestamp` | `cube`, `models-lib`, `pusher` |
| `actor` | `models-lib`, `pusher` |
| `actorCompany` | `models-lib`, `pusher` |
| `broker` | `models-lib`, `pusher` |
| `carrier` | `models-lib`, `pusher` |
| `comment` | `cube`, `models-lib` |
| `load` | `models-lib`, `pusher` |
| `shipper` | `models-lib`, `pusher` |
| `actorCompanyUserManagementId` | `models-lib` |
| `actorName` | `posting-backend` |
| `actorType` | `posting-backend` |
| `actorUser` | `posting-backend` |
| `actorUserManagementId` | `models-lib` |
| `brokerUserManagementId` | `models-lib` |
| `carrierUserManagementId` | `models-lib` |
| `createdAt` | `posting-backend` |
| `externalLoadId` | `posting-backend` |
| `loadCreator` | `posting-backend` |
| `loadLeg` | `posting-backend` |
| `loadLegId` | `posting-backend` |
| `loadType` | `posting-backend` |

## Use cases

### REST surface

_(no REST endpoints reference this entity in any variant repo)_

### Repository operations

_(no Spring Data / Panache repositories typed on this entity found)_

### Carried by Pub/Sub topics

_(no resolved Pub/Sub schemas reference this entity; check `relations/event-schemas/` for unresolved canonical-dto fields)_

## Cross-references

- Owning service shadow: [`posting-backend`](../../repos/posting-backend.md)
- Domain rollup: [`communication`](../communication.md)
- Domain rollup: [`listings-trade`](../listings-trade.md)
- Domain rollup: [`platform`](../platform.md)
- Master index: [`entity-catalog.md`](../../relations/entity-catalog.md)
