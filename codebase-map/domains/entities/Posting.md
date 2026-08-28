---
entity: Posting
aliases: [CtmsPostingDto, CtmsPostingEntityReadDto, CtmsPostingPubSubDto, CtmsPostingReadDto, Posting, PostingDto, PostingEntity, PostingPubSubDto, PostingReadDto, V1PostingReadDto]
status: auto-generated
domains: [integrations, listings-trade, operations, platform]
occurrence-count: 16
variant-count: 16
owning-service: loadboard-backend
last-extracted-date: 2026-05-15
---

# Posting

## What it is

TODO: human narrative. 16 variants across 7 repos and 4 domains (integrations, listings-trade, operations, platform). Owning service: [`loadboard-backend`](../../repos/loadboard-backend.md).

## Variants

| Repo | Class | Kind | Module | Extends | Field count | Module path |
|---|---|---|---|---|---:|---|
| [cube](../../repos/cube.md) | `PostingReadDto` | dto | `loadboard` | — | 83 | `loadboard/loadboard-dtos/src/main/java/cars/ship/cube/dtos/out/v2/PostingReadDto.java` |
| [cube](../../repos/cube.md) | `V1PostingReadDto` | dto | `loadboard` | — | 81 | `loadboard/loadboard-dtos/src/main/java/cars/ship/cube/dtos/out/v1/V1PostingReadDto.java` |
| [load-bookmark-backend](../../repos/load-bookmark-backend.md) | `PostingDto` | dto | `api-dtos` | — | 1 | `api-dtos/src/main/java/cars/ship/loadbookmark/dtos/PostingDto.java` |
| [loadboard-backend](../../repos/loadboard-backend.md) | `CtmsPostingPubSubDto` | dto | `services` | — | 174 | `services/src/main/java/cars/ship/loadboard/dtos/pubsub/CtmsPostingPubSubDto.java` |
| [loadboard-backend](../../repos/loadboard-backend.md) | `Posting` | dto | `services` | — | 55 | `services/src/main/java/cars/ship/loadboard/models/Posting.java` |
| [loadboard-backend](../../repos/loadboard-backend.md) | `PostingDto` | dto | `api-dtos` | — | 28 | `api-dtos/src/main/java/cars/ship/loadboard/dtos/PostingDto.java` |
| [loadboard-backend](../../repos/loadboard-backend.md) | `PostingEntity` | jpa | `db-entities` | `BaseEntity` | 77 | `db-entities/src/main/java/cars/ship/loadboard/entities/PostingEntity.java` |
| [loadboard-backend](../../repos/loadboard-backend.md) | `PostingPubSubDto` | dto | `api-dtos` | — | 55 | `api-dtos/src/main/java/cars/ship/loadboard/dtos/out/pubsub/PostingPubSubDto.java` |
| [loadboard-backend](../../repos/loadboard-backend.md) | `PostingReadDto` | dto | `api-dtos` | — | 46 | `api-dtos/src/main/java/cars/ship/loadboard/dtos/out/PostingReadDto.java` |
| [models-lib](../../repos/models-lib.md) | `CtmsPostingReadDto` | dto | `read-models` | — | 85 | `read-models/src/main/java/cars/ship/modelslib/readmodels/ctms/CtmsPostingReadDto.java` |
| [models-lib](../../repos/models-lib.md) | `PostingDto` | dto | `api-dtos` | — | 1 | `api-dtos/src/main/java/cars/ship/modelslib/apidtos/loadbookmark/PostingDto.java` |
| [models-lib](../../repos/models-lib.md) | `PostingDto` | dto | `data-models` | — | 11 | `data-models/src/main/java/cars/ship/modelslib/datamodels/PostingDto.java` |
| [models-lib](../../repos/models-lib.md) | `PostingReadDto` | dto | `read-models` | — | 85 | `read-models/src/main/java/cars/ship/modelslib/readmodels/es/PostingReadDto.java` |
| [posting-backend](../../repos/posting-backend.md) | `PostingDto` | dto | `posting-app` | `LoadDto` | 17 | `posting-app/src/main/java/cars/ship/shipperlite/posting/application/adapters/out/clients/dto/loadboard/PostingDto.java` |
| [syncer](../../repos/syncer.md) | `CtmsPostingEntityReadDto` | dto | `services` | — | 85 | `services/src/main/java/cars/ship/syncer/services/models/entity/ctms/CtmsPostingEntityReadDto.java` |
| [trip-planner](../../repos/trip-planner.md) | `CtmsPostingDto` | dto | `infra-interfaces` | `CtmsLoadBaseDto` | 4 | `infra-interfaces/src/main/java/cars/ship/planner/infra/ctms/dto/CtmsPostingDto.java` |

## Field union / intersection

**Core fields** (present in ≥60% of variants — 9/16 or more):

_(no fields shared by ≥60% of variants — high heterogeneity)_

**Variant-specific fields** (present in <60% of variants, top 30 by spread):

| Field | Repos that declare it |
|---|---|
| `deliveryRequestedDateEnd` | `cube`, `loadboard-backend`, `models-lib`, `syncer`, `trip-planner` |
| `deliveryRequestedDateStart` | `cube`, `loadboard-backend`, `models-lib`, `syncer`, `trip-planner` |
| `pickupRequestedDateEnd` | `cube`, `loadboard-backend`, `models-lib`, `syncer`, `trip-planner` |
| `pickupRequestedDateStart` | `cube`, `loadboard-backend`, `models-lib`, `syncer`, `trip-planner` |
| `status` | `cube`, `load-bookmark-backend`, `loadboard-backend`, `models-lib`, `syncer` |
| `canBeBooked` | `cube`, `loadboard-backend`, `models-lib`, `syncer` |
| `canBeClaimed` | `cube`, `loadboard-backend`, `models-lib`, `syncer` |
| `createTime` | `cube`, `loadboard-backend`, `models-lib`, `syncer` |
| `customerEmail` | `cube`, `loadboard-backend`, `models-lib`, `syncer` |
| `customerEmail2` | `cube`, `loadboard-backend`, `models-lib`, `syncer` |
| `customerEmail3` | `cube`, `loadboard-backend`, `models-lib`, `syncer` |
| `customerName` | `cube`, `loadboard-backend`, `models-lib`, `syncer` |
| `customerPhone1` | `cube`, `loadboard-backend`, `models-lib`, `syncer` |
| `customerPhone1Notes` | `cube`, `loadboard-backend`, `models-lib`, `syncer` |
| `customerPhone1Type` | `cube`, `loadboard-backend`, `models-lib`, `syncer` |
| `customerPhone2` | `cube`, `loadboard-backend`, `models-lib`, `syncer` |
| `customerPhone2Notes` | `cube`, `loadboard-backend`, `models-lib`, `syncer` |
| `customerPhone2Type` | `cube`, `loadboard-backend`, `models-lib`, `syncer` |
| `customerPhone3` | `cube`, `loadboard-backend`, `models-lib`, `syncer` |
| `customerPhone3Notes` | `cube`, `loadboard-backend`, `models-lib`, `syncer` |
| `customerPhone3Type` | `cube`, `loadboard-backend`, `models-lib`, `syncer` |
| `deliveryAddressLocation` | `cube`, `loadboard-backend`, `models-lib`, `syncer` |
| `deliveryCity` | `cube`, `loadboard-backend`, `models-lib`, `syncer` |
| `deliveryRequestedDateEndType` | `cube`, `loadboard-backend`, `models-lib`, `syncer` |
| `deliveryRequestedDateStartType` | `cube`, `loadboard-backend`, `models-lib`, `syncer` |
| `deliveryState` | `cube`, `loadboard-backend`, `models-lib`, `syncer` |
| `deliveryZip` | `cube`, `loadboard-backend`, `models-lib`, `syncer` |
| `distanceImperial` | `cube`, `loadboard-backend`, `models-lib`, `syncer` |
| `enclosedTrailer` | `cube`, `loadboard-backend`, `models-lib`, `syncer` |
| `exclusivityExpirationTime` | `cube`, `loadboard-backend`, `models-lib`, `syncer` |

## Use cases

### REST surface

**cube**:
- `GET /{id}` — `loadboard/loadboard-services/src/main/java/cars/ship/cube/rest/controller/v1/V1PostingsController.java`
- `GET /company/{companyId}` — `loadboard/loadboard-services/src/main/java/cars/ship/cube/rest/controller/v2/V2PostingsInternalController.java`
- `POST /company/{companyId}` — `loadboard/loadboard-services/src/main/java/cars/ship/cube/rest/controller/v2/V2PostingsInternalController.java`

**loadboard-backend**:
- `GET /{id}` — `resources/src/main/java/cars/ship/loadboard/rest/PostingQueryController.java`
- `ANY /{id}/claim` — `resources/src/main/java/cars/ship/loadboard/rest/PostingController.java`
- `ANY /{id}/dispatch` — `resources/src/main/java/cars/ship/loadboard/rest/PostingController.java`
- `ANY /{id}/cancel` — `resources/src/main/java/cars/ship/loadboard/rest/PostingController.java`
- `ANY /{id}/offer` — `resources/src/main/java/cars/ship/loadboard/rest/PostingController.java`
- `PUT /{id}` — `resources/src/main/java/cars/ship/loadboard/rest/PostingsInternalController.java`
- `GET /postings/{id}/owner` — `resources/src/main/java/cars/ship/loadboard/rest/InternalLoadboardController.java`
- `GET /negotiations/{id}/posting/owner` — `resources/src/main/java/cars/ship/loadboard/rest/InternalLoadboardController.java`
- `ANY /{id}` — `resources/src/main/java/cars/ship/loadboard/rest/PostingWorkflowsController.java`
- `POST /repost` — `resources/src/main/java/cars/ship/loadboard/rest/PostingsJobsInternalController.java`

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
