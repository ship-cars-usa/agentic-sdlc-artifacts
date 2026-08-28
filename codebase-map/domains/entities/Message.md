---
entity: Message
aliases: [ChatMessageDto, MessageDto, V1ChatMessageDto]
status: auto-generated
domains: [communication, operations, platform, pricing-billing]
occurrence-count: 5
variant-count: 5
owning-service: notification-backend
last-extracted-date: 2026-05-15
---

# Message

## What it is

TODO: human narrative. 5 variants across 4 repos and 4 domains (communication, operations, platform, pricing-billing). Owning service: [`notification-backend`](../../repos/notification-backend.md).

## Variants

| Repo | Class | Kind | Module | Extends | Field count | Module path |
|---|---|---|---|---|---:|---|
| [invoices](../../repos/invoices.md) | `MessageDto` | dto | `api-dtos` | — | 0 | `api-dtos/src/main/java/cars/ship/invoices/dtos/commons/MessageDto.java` |
| [location-history-backend](../../repos/location-history-backend.md) | `MessageDto` | dto | `api-dtos` | — | 17 | `api-dtos/src/main/java/cars/ship/locationhistory/dtos/MessageDto.java` |
| [models-lib](../../repos/models-lib.md) | `MessageDto` | dto | `data-models` | — | 18 | `data-models/src/main/java/cars/ship/modelslib/datamodels/MessageDto.java` |
| [notification-backend](../../repos/notification-backend.md) | `ChatMessageDto` | dto | `notification-app` | — | 5 | `notification-app/src/main/java/cars/ship/shipperlite/notification/application/adapters/out/clients/dtos/ChatMessageDto.java` |
| [notification-backend](../../repos/notification-backend.md) | `V1ChatMessageDto` | dto | `notification-dtos` | — | 5 | `notification-dtos/src/main/java/cars/ship/notification/dtos/v1/push/V1ChatMessageDto.java` |

## Field union / intersection

**Core fields** (present in ≥60% of variants — 3/5 or more):

_(no fields shared by ≥60% of variants — high heterogeneity)_

**Variant-specific fields** (present in <60% of variants, top 30 by spread):

| Field | Repos that declare it |
|---|---|
| `action` | `location-history-backend`, `models-lib` |
| `actorPk` | `location-history-backend`, `models-lib` |
| `actorUserManagementId` | `location-history-backend`, `models-lib` |
| `created` | `location-history-backend`, `models-lib` |
| `deleted` | `location-history-backend`, `models-lib` |
| `demoOwnerId` | `location-history-backend`, `models-lib` |
| `drivers` | `location-history-backend`, `models-lib` |
| `event` | `location-history-backend`, `models-lib` |
| `eventPk` | `location-history-backend`, `models-lib` |
| `isDemo` | `location-history-backend`, `models-lib` |
| `objectPk` | `location-history-backend`, `models-lib` |
| `objectType` | `location-history-backend`, `models-lib` |
| `parentPk` | `location-history-backend`, `models-lib` |
| `parentType` | `location-history-backend`, `models-lib` |
| `shipperLoadId` | `location-history-backend`, `models-lib` |
| `timestamp` | `location-history-backend`, `models-lib` |
| `changedFields` | `location-history-backend` |
| `content` | `notification-backend` |
| `createdAt` | `notification-backend` |
| `creator` | `notification-backend` |
| `id` | `notification-backend` |
| `isRead` | `notification-backend` |
| `objectUserManagementId` | `models-lib` |
| `orderingKey` | `models-lib` |

## Use cases

### REST surface

_(no REST endpoints reference this entity in any variant repo)_

### Repository operations

_(no Spring Data / Panache repositories typed on this entity found)_

### Carried by Pub/Sub topics

_(no resolved Pub/Sub schemas reference this entity; check `relations/event-schemas/` for unresolved canonical-dto fields)_

## Cross-references

- Owning service shadow: [`notification-backend`](../../repos/notification-backend.md)
- Domain rollup: [`communication`](../communication.md)
- Domain rollup: [`operations`](../operations.md)
- Domain rollup: [`platform`](../platform.md)
- Domain rollup: [`pricing-billing`](../pricing-billing.md)
- Master index: [`entity-catalog.md`](../../relations/entity-catalog.md)
