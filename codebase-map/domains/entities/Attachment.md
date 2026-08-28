---
entity: Attachment
aliases: [Attachment, AttachmentDto, AttachmentEntity, AttachmentPubSubDto, AttachmentReadDto, CtmsAttachmentEntityReadDto, CtmsAttachmentPubSubDto, CtmsAttachmentReadDto, PublicTrackingAttachmentDto, V1AttachmentPubSubDto]
status: auto-generated
domains: [communication, identity, integrations, listings-trade, operations, platform]
occurrence-count: 25
variant-count: 25
owning-service: loadboard-backend
last-extracted-date: 2026-05-15
---

# Attachment

## What it is

TODO: human narrative. 25 variants across 10 repos and 6 domains (communication, identity, integrations, listings-trade, operations, platform). Owning service: [`loadboard-backend`](../../repos/loadboard-backend.md).

## Variants

| Repo | Class | Kind | Module | Extends | Field count | Module path |
|---|---|---|---|---|---:|---|
| [attachment-backend](../../repos/attachment-backend.md) | `Attachment` | dto | `db-entities` | — | 15 | `db-entities/src/main/java/cars/ship/attachment/entities/Attachment.java` |
| [attachment-backend](../../repos/attachment-backend.md) | `AttachmentDto` | dto | `api-dtos` | — | 0 | `api-dtos/src/main/java/cars/ship/attachment/dtos/AttachmentDto.java` |
| [attachment-backend](../../repos/attachment-backend.md) | `AttachmentEntity` | jpa | `db-entities` | `BaseEntity` | 11 | `db-entities/src/main/java/cars/ship/attachment/entities/AttachmentEntity.java` |
| [cube](../../repos/cube.md) | `AttachmentDto` | dto | `ctms-orders` | — | 28 | `ctms-orders/ctms-orders-dtos/src/main/java/cars/ship/cube/ctms/orders/dtos/out/AttachmentDto.java` |
| [integration-executor](../../repos/integration-executor.md) | `Attachment` | jpa | `db-entities` | `BaseEntity` | 7 | `db-entities/src/main/java/cars/ship/integrationexecutor/entities/Attachment.java` |
| [loadboard-backend](../../repos/loadboard-backend.md) | `Attachment` | dto | `services` | — | 8 | `services/src/main/java/cars/ship/loadboard/models/Attachment.java` |
| [loadboard-backend](../../repos/loadboard-backend.md) | `AttachmentDto` | dto | `api-dtos` | — | 4 | `api-dtos/src/main/java/cars/ship/loadboard/dtos/AttachmentDto.java` |
| [loadboard-backend](../../repos/loadboard-backend.md) | `AttachmentEntity` | jpa | `db-entities` | `BaseEntity` | 4 | `db-entities/src/main/java/cars/ship/loadboard/entities/AttachmentEntity.java` |
| [loadboard-backend](../../repos/loadboard-backend.md) | `AttachmentPubSubDto` | dto | `api-dtos` | — | 8 | `api-dtos/src/main/java/cars/ship/loadboard/dtos/out/pubsub/AttachmentPubSubDto.java` |
| [loadboard-backend](../../repos/loadboard-backend.md) | `AttachmentReadDto` | dto | `api-dtos` | — | 8 | `api-dtos/src/main/java/cars/ship/loadboard/dtos/out/AttachmentReadDto.java` |
| [loadboard-backend](../../repos/loadboard-backend.md) | `CtmsAttachmentPubSubDto` | dto | `services` | — | 14 | `services/src/main/java/cars/ship/loadboard/dtos/pubsub/CtmsAttachmentPubSubDto.java` |
| [models-lib](../../repos/models-lib.md) | `AttachmentDto` | dto | `data-models` | — | 35 | `data-models/src/main/java/cars/ship/modelslib/datamodels/AttachmentDto.java` |
| [models-lib](../../repos/models-lib.md) | `AttachmentReadDto` | dto | `read-models` | — | 28 | `read-models/src/main/java/cars/ship/modelslib/readmodels/es/AttachmentReadDto.java` |
| [models-lib](../../repos/models-lib.md) | `AttachmentReadDto` | dto | `read-models` | — | 11 | `read-models/src/main/java/cars/ship/modelslib/readmodels/posting/AttachmentReadDto.java` |
| [models-lib](../../repos/models-lib.md) | `CtmsAttachmentReadDto` | dto | `read-models` | — | 28 | `read-models/src/main/java/cars/ship/modelslib/readmodels/ctms/CtmsAttachmentReadDto.java` |
| [posting-backend](../../repos/posting-backend.md) | `Attachment` | jpa | `posting-app` | `BaseEntity` | 13 | `posting-app/src/main/java/cars/ship/shipperlite/posting/domain/model/Attachment.java` |
| [posting-backend](../../repos/posting-backend.md) | `AttachmentDto` | dto | `posting-app` | — | 12 | `posting-app/src/main/java/cars/ship/shipperlite/posting/application/adapters/out/clients/dto/loadboard/AttachmentDto.java` |
| [posting-backend](../../repos/posting-backend.md) | `AttachmentDto` | dto | `posting-dtos` | `BaseAttachmentDto` | 5 | `posting-dtos/src/main/java/cars/ship/posting/dtos/AttachmentDto.java` |
| [posting-backend](../../repos/posting-backend.md) | `AttachmentPubSubDto` | dto | `posting-app` | — | 7 | `posting-app/src/main/java/cars/ship/shipperlite/posting/application/adapters/in/pubsub/dto/AttachmentPubSubDto.java` |
| [posting-backend](../../repos/posting-backend.md) | `V1AttachmentPubSubDto` | dto | `posting-dtos` | — | 9 | `posting-dtos/src/main/java/cars/ship/posting/dtos/pubsub/v1/V1AttachmentPubSubDto.java` |
| [public-tracking-backend](../../repos/public-tracking-backend.md) | `CtmsAttachmentPubSubDto` | dto | `public-tracking-backend` | — | 9 | `src/main/java/cars/ship/publictracking/application/adapters/in/pubsub/carriertms/dtos/CtmsAttachmentPubSubDto.java` |
| [public-tracking-backend](../../repos/public-tracking-backend.md) | `PublicTrackingAttachmentDto` | dto | `public-tracking-backend` | — | 0 | `src/main/java/cars/ship/publictracking/application/adapters/in/rest/dtos/PublicTrackingAttachmentDto.java` |
| [pusher](../../repos/pusher.md) | `AttachmentDto` | dto | `event-listener` | — | 5 | `event-listener/src/main/java/cars/ship/pusher/listener/dtos/in/AttachmentDto.java` |
| [syncer](../../repos/syncer.md) | `CtmsAttachmentEntityReadDto` | dto | `services` | — | 28 | `services/src/main/java/cars/ship/syncer/services/models/entity/ctms/CtmsAttachmentEntityReadDto.java` |
| [user-backend](../../repos/user-backend.md) | `Attachment` | jpa | `usermanagement-app` | `BaseEntity` | 4 | `usermanagement-app/src/main/java/cars/ship/shipperlite/user/domain/model/Attachment.java` |

## Field union / intersection

**Core fields** (present in ≥60% of variants — 15/25 or more):

_(no fields shared by ≥60% of variants — high heterogeneity)_

**Variant-specific fields** (present in <60% of variants, top 30 by spread):

| Field | Repos that declare it |
|---|---|
| `id` | `attachment-backend`, `cube`, `loadboard-backend`, `models-lib`, `posting-backend`, `syncer` |
| `type` | `cube`, `loadboard-backend`, `models-lib`, `posting-backend`, `pusher`, `syncer` |
| `loadId` | `cube`, `integration-executor`, `loadboard-backend`, `models-lib`, `syncer` |
| `shareWithDriver` | `cube`, `loadboard-backend`, `models-lib`, `posting-backend`, `syncer` |
| `vehicleId` | `cube`, `loadboard-backend`, `models-lib`, `posting-backend`, `syncer` |
| `active` | `cube`, `loadboard-backend`, `models-lib`, `syncer` |
| `createTime` | `cube`, `loadboard-backend`, `models-lib`, `syncer` |
| `file` | `cube`, `loadboard-backend`, `models-lib`, `syncer` |
| `height` | `cube`, `loadboard-backend`, `models-lib`, `syncer` |
| `image` | `cube`, `loadboard-backend`, `models-lib`, `syncer` |
| `isSharedWithShipper` | `cube`, `models-lib`, `posting-backend`, `syncer` |
| `originalFile` | `cube`, `loadboard-backend`, `models-lib`, `syncer` |
| `timestamp` | `cube`, `models-lib`, `public-tracking-backend`, `syncer` |
| `width` | `cube`, `loadboard-backend`, `models-lib`, `syncer` |
| `area` | `cube`, `models-lib`, `syncer` |
| `comments` | `cube`, `models-lib`, `syncer` |
| `companyId` | `attachment-backend`, `integration-executor`, `posting-backend` |
| `convertedTimestamp` | `cube`, `models-lib`, `syncer` |
| `createdAt` | `attachment-backend`, `models-lib`, `posting-backend` |
| `creatorCompanyId` | `cube`, `models-lib`, `syncer` |
| `creatorId` | `cube`, `models-lib`, `syncer` |
| `damages` | `cube`, `models-lib`, `syncer` |
| `description` | `cube`, `models-lib`, `syncer` |
| `driverOnly` | `cube`, `models-lib`, `syncer` |
| `fileUrl` | `loadboard-backend`, `models-lib`, `posting-backend` |
| `location` | `cube`, `models-lib`, `syncer` |
| `locationAddress` | `cube`, `models-lib`, `syncer` |
| `orderId` | `cube`, `models-lib`, `syncer` |
| `segment` | `cube`, `models-lib`, `syncer` |
| `shareWithShipper` | `cube`, `models-lib`, `syncer` |

## Use cases

### REST surface

**attachment-backend**:
- `ANY /{id}` — `resources/src/main/java/cars/ship/attachment/rest/AttachmentController.java`
- `ANY /bulk` — `resources/src/main/java/cars/ship/attachment/rest/AttachmentController.java`
- `ANY /form-data` — `resources/src/main/java/cars/ship/attachment/rest/AttachmentController.java`

**integration-executor**:
- `ANY /context-company/{COMPANY_ID}/context-user/{USER_ID}/v1/attachments/form-data` — `event-listener/src/main/java/cars/ship/integrationexecutor/clients/AttachmentClient.java`
- `ANY /context-company/{COMPANY_ID}/context-user/{USER_ID}/v1/attachments/{ID}` — `event-listener/src/main/java/cars/ship/integrationexecutor/clients/AttachmentClient.java`

**loadboard-backend**:
- `ANY /{postingId}/attachments` — `resources/src/main/java/cars/ship/loadboard/rest/AttachmentsController.java`
- `ANY /{postingId}/attachments/{attachmentId}` — `resources/src/main/java/cars/ship/loadboard/rest/AttachmentsController.java`
- `ANY /attachments/{attachmentId}` — `resources/src/main/java/cars/ship/loadboard/rest/AttachmentsController.java`
- `ANY /{postingId}/vehicles/{vehicleId}/attachments` — `resources/src/main/java/cars/ship/loadboard/rest/AttachmentsController.java`

### Repository operations

_(no Spring Data / Panache repositories typed on this entity found)_

### Carried by Pub/Sub topics

- [`ctms-subscription`](../../relations/event-schemas/ctms-subscription.md) — DTO `CtmsAttachmentPubSubDto`

## Cross-references

- Owning service shadow: [`loadboard-backend`](../../repos/loadboard-backend.md)
- Domain rollup: [`communication`](../communication.md)
- Domain rollup: [`identity`](../identity.md)
- Domain rollup: [`integrations`](../integrations.md)
- Domain rollup: [`listings-trade`](../listings-trade.md)
- Domain rollup: [`operations`](../operations.md)
- Domain rollup: [`platform`](../platform.md)
- Master index: [`entity-catalog.md`](../../relations/entity-catalog.md)
