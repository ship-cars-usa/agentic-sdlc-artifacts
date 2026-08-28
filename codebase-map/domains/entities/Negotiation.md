---
entity: Negotiation
aliases: [CtmsNegotiationDto, CtmsNegotiationEntityReadDto, CtmsNegotiationPubSubDto, CtmsNegotiationReadDto, Negotiation, NegotiationDto, NegotiationEntity, NegotiationPubSubDto, NegotiationReadDto, V1NegotiationReadDto]
status: auto-generated
domains: [integrations, listings-trade, operations, platform]
occurrence-count: 13
variant-count: 13
owning-service: loadboard-backend
last-extracted-date: 2026-05-15
---

# Negotiation

## What it is

TODO: human narrative. 13 variants across 6 repos and 4 domains (integrations, listings-trade, operations, platform). Owning service: [`loadboard-backend`](../../repos/loadboard-backend.md).

## Variants

| Repo | Class | Kind | Module | Extends | Field count | Module path |
|---|---|---|---|---|---:|---|
| [cube](../../repos/cube.md) | `NegotiationReadDto` | dto | `loadboard` | — | 18 | `loadboard/loadboard-dtos/src/main/java/cars/ship/cube/dtos/out/v2/NegotiationReadDto.java` |
| [cube](../../repos/cube.md) | `V1NegotiationReadDto` | dto | `loadboard` | — | 17 | `loadboard/loadboard-dtos/src/main/java/cars/ship/cube/dtos/out/v1/V1NegotiationReadDto.java` |
| [loadboard-backend](../../repos/loadboard-backend.md) | `CtmsNegotiationPubSubDto` | dto | `services` | — | 12 | `services/src/main/java/cars/ship/loadboard/dtos/pubsub/CtmsNegotiationPubSubDto.java` |
| [loadboard-backend](../../repos/loadboard-backend.md) | `Negotiation` | dto | `services` | — | 12 | `services/src/main/java/cars/ship/loadboard/models/Negotiation.java` |
| [loadboard-backend](../../repos/loadboard-backend.md) | `NegotiationEntity` | jpa | `db-entities` | `BaseEntity` | 7 | `db-entities/src/main/java/cars/ship/loadboard/entities/NegotiationEntity.java` |
| [loadboard-backend](../../repos/loadboard-backend.md) | `NegotiationPubSubDto` | dto | `api-dtos` | — | 0 | `api-dtos/src/main/java/cars/ship/loadboard/dtos/out/pubsub/NegotiationPubSubDto.java` |
| [loadboard-backend](../../repos/loadboard-backend.md) | `NegotiationReadDto` | dto | `api-dtos` | — | 12 | `api-dtos/src/main/java/cars/ship/loadboard/dtos/out/NegotiationReadDto.java` |
| [models-lib](../../repos/models-lib.md) | `CtmsNegotiationReadDto` | dto | `read-models` | — | 18 | `read-models/src/main/java/cars/ship/modelslib/readmodels/ctms/CtmsNegotiationReadDto.java` |
| [models-lib](../../repos/models-lib.md) | `NegotiationDto` | dto | `data-models` | — | 21 | `data-models/src/main/java/cars/ship/modelslib/datamodels/NegotiationDto.java` |
| [models-lib](../../repos/models-lib.md) | `NegotiationReadDto` | dto | `read-models` | — | 20 | `read-models/src/main/java/cars/ship/modelslib/readmodels/es/NegotiationReadDto.java` |
| [posting-backend](../../repos/posting-backend.md) | `NegotiationPubSubDto` | dto | `posting-app` | — | 6 | `posting-app/src/main/java/cars/ship/shipperlite/posting/application/adapters/in/pubsub/dto/NegotiationPubSubDto.java` |
| [syncer](../../repos/syncer.md) | `CtmsNegotiationEntityReadDto` | dto | `services` | — | 18 | `services/src/main/java/cars/ship/syncer/services/models/entity/ctms/CtmsNegotiationEntityReadDto.java` |
| [trip-planner](../../repos/trip-planner.md) | `CtmsNegotiationDto` | dto | `infra-interfaces` | — | 5 | `infra-interfaces/src/main/java/cars/ship/planner/infra/ctms/dto/CtmsNegotiationDto.java` |

## Field union / intersection

**Core fields** (present in ≥60% of variants — 7/13 or more):

_(no fields shared by ≥60% of variants — high heterogeneity)_

**Variant-specific fields** (present in <60% of variants, top 30 by spread):

| Field | Repos that declare it |
|---|---|
| `status` | `cube`, `loadboard-backend`, `models-lib`, `posting-backend`, `syncer`, `trip-planner` |
| `carrierId` | `cube`, `loadboard-backend`, `models-lib`, `posting-backend`, `syncer` |
| `id` | `cube`, `loadboard-backend`, `models-lib`, `posting-backend`, `syncer` |
| `lastOffer` | `cube`, `loadboard-backend`, `models-lib`, `syncer`, `trip-planner` |
| `offers` | `cube`, `loadboard-backend`, `models-lib`, `posting-backend`, `syncer` |
| `orderId` | `cube`, `loadboard-backend`, `models-lib`, `syncer`, `trip-planner` |
| `cancelReason` | `cube`, `loadboard-backend`, `models-lib`, `syncer` |
| `carrierUserManagementId` | `cube`, `models-lib`, `syncer`, `trip-planner` |
| `createTime` | `cube`, `loadboard-backend`, `models-lib`, `syncer` |
| `isBookAttempt` | `cube`, `loadboard-backend`, `models-lib`, `syncer` |
| `originalPrice` | `cube`, `loadboard-backend`, `models-lib`, `syncer` |
| `shipperId` | `cube`, `loadboard-backend`, `models-lib`, `syncer` |
| `shipperUserManagementId` | `cube`, `models-lib`, `syncer`, `trip-planner` |
| `updateTime` | `cube`, `loadboard-backend`, `models-lib`, `syncer` |
| `carrierInfo` | `cube`, `models-lib`, `syncer` |
| `lastOfferId` | `cube`, `models-lib`, `syncer` |
| `shipperInfo` | `cube`, `models-lib`, `syncer` |
| `carrier` | `loadboard-backend`, `models-lib` |
| `loadPrice` | `models-lib`, `syncer` |
| `negotiationState` | `cube`, `models-lib` |
| `shipper` | `loadboard-backend`, `models-lib` |
| `carrierOfferPrice` | `models-lib` |
| `carrierOfferStatus` | `models-lib` |
| `currentOffer` | `posting-backend` |
| `loadLegId` | `posting-backend` |
| `order` | `models-lib` |
| `posting` | `loadboard-backend` |
| `postingId` | `loadboard-backend` |
| `url` | `models-lib` |

## Use cases

### REST surface

**loadboard-backend**:
- `ANY /{id}/accept` — `resources/src/main/java/cars/ship/loadboard/rest/NegotiationsController.java`
- `ANY /{id}/cancel` — `resources/src/main/java/cars/ship/loadboard/rest/NegotiationsController.java`

### Repository operations

_(no Spring Data / Panache repositories typed on this entity found)_

### Carried by Pub/Sub topics

_(no resolved Pub/Sub schemas reference this entity; check `relations/event-schemas/` for unresolved canonical-dto fields)_

## Cross-references

- Owning service shadow: [`loadboard-backend`](../../repos/loadboard-backend.md)
- Domain rollup: [`integrations`](../integrations.md)
- Domain rollup: [`listings-trade`](../listings-trade.md)
- Domain rollup: [`operations`](../operations.md)
- Domain rollup: [`platform`](../platform.md)
- Master index: [`entity-catalog.md`](../../relations/entity-catalog.md)
