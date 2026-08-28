---
entity: Offer
aliases: [CarrierOffer, CarrierOfferDto, CarrierOfferReadDto, Offer, OfferDto, OfferEntity, OfferPubSubDto, OfferReadDto, V1CarrierOfferPubSubDto, V1OfferReadDto]
status: auto-generated
domains: [listings-trade, operations, platform]
occurrence-count: 16
variant-count: 16
owning-service: loadboard-backend
last-extracted-date: 2026-05-15
---

# Offer

## What it is

TODO: human narrative. 16 variants across 5 repos and 3 domains (listings-trade, operations, platform). Owning service: [`loadboard-backend`](../../repos/loadboard-backend.md).

## Variants

| Repo | Class | Kind | Module | Extends | Field count | Module path |
|---|---|---|---|---|---:|---|
| [cube](../../repos/cube.md) | `OfferReadDto` | dto | `loadboard` | — | 12 | `loadboard/loadboard-dtos/src/main/java/cars/ship/cube/dtos/out/v2/OfferReadDto.java` |
| [cube](../../repos/cube.md) | `V1OfferReadDto` | dto | `loadboard` | — | 8 | `loadboard/loadboard-dtos/src/main/java/cars/ship/cube/dtos/out/v1/V1OfferReadDto.java` |
| [loadboard-backend](../../repos/loadboard-backend.md) | `Offer` | dto | `services` | — | 18 | `services/src/main/java/cars/ship/loadboard/models/Offer.java` |
| [loadboard-backend](../../repos/loadboard-backend.md) | `OfferDto` | dto | `api-dtos` | — | 5 | `api-dtos/src/main/java/cars/ship/loadboard/dtos/OfferDto.java` |
| [loadboard-backend](../../repos/loadboard-backend.md) | `OfferEntity` | jpa | `db-entities` | `BaseEntity` | 11 | `db-entities/src/main/java/cars/ship/loadboard/entities/OfferEntity.java` |
| [loadboard-backend](../../repos/loadboard-backend.md) | `OfferPubSubDto` | dto | `api-dtos` | — | 0 | `api-dtos/src/main/java/cars/ship/loadboard/dtos/out/pubsub/OfferPubSubDto.java` |
| [loadboard-backend](../../repos/loadboard-backend.md) | `OfferReadDto` | dto | `api-dtos` | — | 17 | `api-dtos/src/main/java/cars/ship/loadboard/dtos/out/OfferReadDto.java` |
| [models-lib](../../repos/models-lib.md) | `CarrierOfferReadDto` | dto | `read-models` | — | 7 | `read-models/src/main/java/cars/ship/modelslib/readmodels/posting/CarrierOfferReadDto.java` |
| [models-lib](../../repos/models-lib.md) | `OfferDto` | dto | `data-models` | — | 18 | `data-models/src/main/java/cars/ship/modelslib/datamodels/OfferDto.java` |
| [models-lib](../../repos/models-lib.md) | `OfferReadDto` | dto | `read-models` | — | 12 | `read-models/src/main/java/cars/ship/modelslib/readmodels/es/OfferReadDto.java` |
| [posting-backend](../../repos/posting-backend.md) | `CarrierOffer` | jpa | `posting-app` | `BaseEntity` | 5 | `posting-app/src/main/java/cars/ship/shipperlite/posting/domain/model/CarrierOffer.java` |
| [posting-backend](../../repos/posting-backend.md) | `CarrierOfferDto` | dto | `posting-app` | — | 1 | `posting-app/src/main/java/cars/ship/shipperlite/posting/application/adapters/out/clients/dto/loadboard/CarrierOfferDto.java` |
| [posting-backend](../../repos/posting-backend.md) | `CarrierOfferDto` | dto | `posting-dtos` | — | 7 | `posting-dtos/src/main/java/cars/ship/posting/dtos/CarrierOfferDto.java` |
| [posting-backend](../../repos/posting-backend.md) | `OfferPubSubDto` | dto | `posting-app` | — | 6 | `posting-app/src/main/java/cars/ship/shipperlite/posting/application/adapters/in/pubsub/dto/OfferPubSubDto.java` |
| [posting-backend](../../repos/posting-backend.md) | `V1CarrierOfferPubSubDto` | dto | `posting-dtos` | — | 7 | `posting-dtos/src/main/java/cars/ship/posting/dtos/pubsub/v1/V1CarrierOfferPubSubDto.java` |
| [trip-planner](../../repos/trip-planner.md) | `OfferDto` | dto | `infra-interfaces` | — | 1 | `infra-interfaces/src/main/java/cars/ship/planner/infra/ctms/dto/OfferDto.java` |

## Field union / intersection

**Core fields** (present in ≥60% of variants — 9/16 or more):

_(no fields shared by ≥60% of variants — high heterogeneity)_

**Variant-specific fields** (present in <60% of variants, top 30 by spread):

| Field | Repos that declare it |
|---|---|
| `companyId` | `cube`, `loadboard-backend`, `models-lib`, `posting-backend` |
| `id` | `cube`, `loadboard-backend`, `models-lib`, `posting-backend` |
| `offer` | `cube`, `loadboard-backend`, `models-lib`, `posting-backend` |
| `status` | `cube`, `loadboard-backend`, `models-lib`, `posting-backend` |
| `companyUserManagementId` | `cube`, `models-lib`, `trip-planner` |
| `createTime` | `cube`, `loadboard-backend`, `models-lib` |
| `expirationTime` | `cube`, `loadboard-backend`, `models-lib` |
| `negotiationId` | `loadboard-backend`, `models-lib`, `posting-backend` |
| `updateTime` | `cube`, `loadboard-backend`, `models-lib` |
| `activityLog` | `cube`, `models-lib` |
| `carrierDot` | `models-lib`, `posting-backend` |
| `company` | `loadboard-backend`, `models-lib` |
| `expirationDate` | `models-lib`, `posting-backend` |
| `externalId` | `models-lib`, `posting-backend` |
| `negotiation` | `loadboard-backend`, `models-lib` |
| `priceInCents` | `models-lib`, `posting-backend` |
| `reviewActorUserManagementId` | `cube`, `models-lib` |
| `reviewStatus` | `cube`, `models-lib` |
| `reviewTime` | `cube`, `models-lib` |
| `carrierOffer` | `posting-backend` |
| `creatorUserManagementId` | `models-lib` |
| `deliveryDateEnd` | `loadboard-backend` |
| `deliveryDateStart` | `loadboard-backend` |
| `expirationWarningSent` | `loadboard-backend` |
| `lbExternalId` | `posting-backend` |
| `lbNegotiationId` | `posting-backend` |
| `lbStatus` | `posting-backend` |
| `loadLeg` | `posting-backend` |
| `offerValidityHours` | `loadboard-backend` |
| `orderId` | `models-lib` |

## Use cases

### REST surface

**loadboard-backend**:
- `ANY /{id}/claim` — `resources/src/main/java/cars/ship/loadboard/rest/PostingController.java`
- `ANY /{id}/dispatch` — `resources/src/main/java/cars/ship/loadboard/rest/PostingController.java`
- `ANY /{id}/cancel` — `resources/src/main/java/cars/ship/loadboard/rest/PostingController.java`
- `ANY /{id}/offer` — `resources/src/main/java/cars/ship/loadboard/rest/PostingController.java`

### Repository operations

_(no Spring Data / Panache repositories typed on this entity found)_

### Carried by Pub/Sub topics

_(no resolved Pub/Sub schemas reference this entity; check `relations/event-schemas/` for unresolved canonical-dto fields)_

## Cross-references

- Owning service shadow: [`loadboard-backend`](../../repos/loadboard-backend.md)
- Domain rollup: [`listings-trade`](../listings-trade.md)
- Domain rollup: [`operations`](../operations.md)
- Domain rollup: [`platform`](../platform.md)
- Master index: [`entity-catalog.md`](../../relations/entity-catalog.md)
