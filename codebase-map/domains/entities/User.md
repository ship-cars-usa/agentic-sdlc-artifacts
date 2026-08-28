---
entity: User
aliases: [AccountDto, AccountResponseDto, DbUser, DbUserDto, User, UserAccount, UserAccountDto, UserAccountEventDto, UserAccountReadDto, UserDto, UserEmbedded, UserEntity, V1UserAccountDto, V1UserAccountPubSubDto, V2UserAccountDto, V2UserAccountPubSubDto]
status: auto-generated
domains: [communication, identity, integrations, listings-trade, operations, platform]
occurrence-count: 39
variant-count: 39
owning-service: user-backend
last-extracted-date: 2026-05-15
---

# User

## What it is

TODO: human narrative. 39 variants across 18 repos and 6 domains (communication, identity, integrations, listings-trade, operations, platform). Owning service: [`user-backend`](../../repos/user-backend.md).

## Variants

| Repo | Class | Kind | Module | Extends | Field count | Module path |
|---|---|---|---|---|---:|---|
| [autoims-backend](../../repos/autoims-backend.md) | `User` | dto | `domain` | — | 0 | `domain/src/main/java/cars/ship/autoims/domain/sharedkernel/User.java` |
| [chat-backend](../../repos/chat-backend.md) | `User` | dto | `chat-backend` | — | 6 | `src/main/java/cars/ship/shipperlite/chat/domain/model/sharedkernel/User.java` |
| [crm-workflows](../../repos/crm-workflows.md) | `AccountDto` | dto | `api-dtos` | — | 0 | `api-dtos/src/main/java/cars/ship/workflows/crm/dtos/AccountDto.java` |
| [crm-workflows](../../repos/crm-workflows.md) | `AccountResponseDto` | dto | `api-dtos` | — | 0 | `api-dtos/src/main/java/cars/ship/workflows/crm/dtos/AccountResponseDto.java` |
| [cube](../../repos/cube.md) | `UserEntity` | jpa | `db-entities` | `ExternallySyncedBaseEntity` | 4 | `db-entities/src/main/java/ship/cars/cube/UserEntity.java` |
| [driveaway-backend](../../repos/driveaway-backend.md) | `User` | dto | `domain` | — | 0 | `domain/src/main/java/cars/ship/driveaway/domain/sharedkernel/User.java` |
| [driveaway-backend](../../repos/driveaway-backend.md) | `UserEmbedded` | dto | `db-entities` | — | 0 | `db-entities/src/main/java/cars/ship/driveaway/db/entities/notification/embedded/UserEmbedded.java` |
| [inventory-backend](../../repos/inventory-backend.md) | `User` | dto | `domain` | — | 0 | `domain/src/main/java/cars/ship/inventory/domain/sharedkernel/User.java` |
| [load-recommender](../../repos/load-recommender.md) | `DbUser` | dto | `db-syncer` | — | 7 | `db-syncer/src/main/java/cars/ship/recommender/sync/models/DbUser.java` |
| [load-recommender](../../repos/load-recommender.md) | `UserEntity` | jpa | `db-entities` | `BaseEntity` | 7 | `db-entities/src/main/java/cars/ship/recommender/entities/UserEntity.java` |
| [loadboard-backend](../../repos/loadboard-backend.md) | `User` | dto | `services` | — | 4 | `services/src/main/java/cars/ship/loadboard/models/User.java` |
| [loadboard-backend](../../repos/loadboard-backend.md) | `UserEntity` | jpa | `db-entities` | `BaseEntity` | 5 | `db-entities/src/main/java/cars/ship/loadboard/entities/UserEntity.java` |
| [loadbuilder-backend](../../repos/loadbuilder-backend.md) | `User` | dto | `domain` | — | 0 | `domain/src/main/java/cars/ship/loadbuilder/domain/sharedkernel/User.java` |
| [models-lib](../../repos/models-lib.md) | `UserAccountReadDto` | dto | `read-models` | — | 5 | `read-models/src/main/java/cars/ship/modelslib/readmodels/posting/UserAccountReadDto.java` |
| [models-lib](../../repos/models-lib.md) | `UserDto` | dto | `api-dtos` | — | 3 | `api-dtos/src/main/java/cars/ship/modelslib/apidtos/tripplanner/out/UserDto.java` |
| [notification-backend](../../repos/notification-backend.md) | `User` | dto | `notification-app` | — | 2 | `notification-app/src/main/java/cars/ship/shipperlite/notification/domain/model/sharedkernel/User.java` |
| [notification-backend](../../repos/notification-backend.md) | `UserAccount` | jpa | `notification-app` | `BaseEntity` | 4 | `notification-app/src/main/java/cars/ship/shipperlite/notification/domain/model/UserAccount.java` |
| [notification-backend](../../repos/notification-backend.md) | `UserAccountDto` | dto | `notification-app` | — | 14 | `notification-app/src/main/java/cars/ship/shipperlite/notification/application/adapters/out/clients/dtos/UserAccountDto.java` |
| [notification-orchestrator](../../repos/notification-orchestrator.md) | `DbUser` | dto | `db-syncer` | — | 6 | `db-syncer/src/main/java/cars/ship/notification/orchestrator/sync/models/DbUser.java` |
| [notification-orchestrator](../../repos/notification-orchestrator.md) | `UserEntity` | jpa | `db-entities` | `BaseEntity` | 6 | `db-entities/src/main/java/cars/ship/notification/orchestrator/entities/UserEntity.java` |
| [posting-backend](../../repos/posting-backend.md) | `User` | dto | `posting-app` | — | 0 | `posting-app/src/main/java/cars/ship/shipperlite/posting/domain/model/sharedkernel/User.java` |
| [posting-backend](../../repos/posting-backend.md) | `UserAccount` | jpa | `posting-app` | `BaseEntity` | 7 | `posting-app/src/main/java/cars/ship/shipperlite/posting/domain/model/UserAccount.java` |
| [posting-backend](../../repos/posting-backend.md) | `UserAccountDto` | dto | `posting-dtos` | — | 7 | `posting-dtos/src/main/java/cars/ship/posting/dtos/UserAccountDto.java` |
| [posting-backend](../../repos/posting-backend.md) | `UserDto` | dto | `posting-dtos` | — | 4 | `posting-dtos/src/main/java/cars/ship/posting/dtos/UserDto.java` |
| [posting-backend](../../repos/posting-backend.md) | `V1UserAccountPubSubDto` | dto | `posting-dtos` | — | 3 | `posting-dtos/src/main/java/cars/ship/posting/dtos/pubsub/v1/V1UserAccountPubSubDto.java` |
| [pusher](../../repos/pusher.md) | `DbUserDto` | dto | `db-syncer` | — | 9 | `db-syncer/src/main/java/cars/ship/pusher/syncer/dtos/db/DbUserDto.java` |
| [pusher](../../repos/pusher.md) | `User` | dto | `commons` | — | 0 | `commons/src/main/java/cars/ship/pusher/shared/models/User.java` |
| [pusher](../../repos/pusher.md) | `UserEntity` | jpa | `db-entities` | — | 9 | `db-entities/src/main/java/cars/ship/pusher/entities/UserEntity.java` |
| [quarkus-user-syncer](../../repos/quarkus-user-syncer.md) | `UserAccountEventDto` | dto | `runtime` | `EventDto` | 0 | `runtime/src/main/java/cars/ship/quarkus/extensions/usersyncer/dtos/UserAccountEventDto.java` |
| [saved-search-handler](../../repos/saved-search-handler.md) | `User` | dto | `commons` | — | 5 | `commons/src/main/java/cars/ship/search/commons/models/User.java` |
| [saved-search-handler](../../repos/saved-search-handler.md) | `UserEntity` | jpa | `db-entities` | — | 4 | `db-entities/src/main/java/cars/ship/search/entities/UserEntity.java` |
| [trip-planner](../../repos/trip-planner.md) | `DbUserDto` | dto | `db-syncer` | — | 5 | `db-syncer/src/main/java/cars/ship/planner/sync/models/db/DbUserDto.java` |
| [trip-planner](../../repos/trip-planner.md) | `UserDto` | dto | `api-dtos` | — | 3 | `api-dtos/src/main/java/cars/ship/planner/dtos/out/UserDto.java` |
| [trip-planner](../../repos/trip-planner.md) | `UserEntity` | jpa | `db-entities` | `BaseDbEntity` | 5 | `db-entities/src/main/java/cars/ship/planner/entities/UserEntity.java` |
| [user-backend](../../repos/user-backend.md) | `User` | dto | `usermanagement-app` | — | 2 | `usermanagement-app/src/main/java/cars/ship/shipperlite/user/domain/model/sharedkernel/User.java` |
| [user-backend](../../repos/user-backend.md) | `UserAccount` | jpa | `usermanagement-app` | `BaseEntity` | 22 | `usermanagement-app/src/main/java/cars/ship/shipperlite/user/domain/model/UserAccount.java` |
| [user-backend](../../repos/user-backend.md) | `V1UserAccountDto` | dto | `usermanagement-dtos` | — | 19 | `usermanagement-dtos/src/main/java/cars/ship/usermanagement/dtos/v1/V1UserAccountDto.java` |
| [user-backend](../../repos/user-backend.md) | `V2UserAccountDto` | dto | `usermanagement-dtos` | — | 26 | `usermanagement-dtos/src/main/java/cars/ship/usermanagement/dtos/v2/V2UserAccountDto.java` |
| [user-backend](../../repos/user-backend.md) | `V2UserAccountPubSubDto` | dto | `usermanagement-dtos` | — | 22 | `usermanagement-dtos/src/main/java/cars/ship/usermanagement/dtos/v2/V2UserAccountPubSubDto.java` |

## Field union / intersection

**Core fields** (present in ≥60% of variants — 23/39 or more):

_(no fields shared by ≥60% of variants — high heterogeneity)_

**Variant-specific fields** (present in <60% of variants, top 30 by spread):

| Field | Repos that declare it |
|---|---|
| `company` | `load-recommender`, `loadboard-backend`, `models-lib`, `notification-backend`, `notification-orchestrator`, `posting-backend`, `pusher`, `saved-search-handler`, `trip-planner`, `user-backend` |
| `email` | `chat-backend`, `cube`, `load-recommender`, `loadboard-backend`, `notification-backend`, `notification-orchestrator`, `posting-backend`, `pusher`, `saved-search-handler`, `user-backend` |
| `id` | `load-recommender`, `loadboard-backend`, `models-lib`, `notification-backend`, `notification-orchestrator`, `posting-backend`, `pusher`, `saved-search-handler`, `trip-planner`, `user-backend` |
| `companyId` | `chat-backend`, `cube`, `load-recommender`, `notification-backend`, `notification-orchestrator`, `pusher`, `saved-search-handler`, `trip-planner`, `user-backend` |
| `name` | `chat-backend`, `load-recommender`, `notification-backend`, `notification-orchestrator`, `posting-backend`, `pusher`, `saved-search-handler`, `trip-planner`, `user-backend` |
| `active` | `load-recommender`, `loadboard-backend`, `notification-backend`, `notification-orchestrator`, `pusher`, `trip-planner`, `user-backend` |
| `primaryRole` | `cube`, `load-recommender`, `loadboard-backend`, `notification-backend`, `notification-orchestrator`, `pusher`, `user-backend` |
| `profilePictureUrl` | `chat-backend`, `models-lib`, `notification-backend`, `posting-backend`, `trip-planner`, `user-backend` |
| `roles` | `cube`, `load-recommender`, `loadboard-backend`, `notification-backend`, `pusher`, `user-backend` |
| `externalUpdateTime` | `load-recommender`, `notification-orchestrator`, `pusher`, `saved-search-handler`, `trip-planner` |
| `phoneNumber` | `chat-backend`, `notification-backend`, `pusher`, `user-backend` |
| `userId` | `chat-backend`, `notification-backend`, `user-backend` |
| `city` | `notification-backend`, `user-backend` |
| `externalId` | `notification-backend`, `posting-backend` |
| `fullName` | `models-lib`, `trip-planner` |
| `lastModified` | `pusher`, `user-backend` |
| `lastModifiedUserBe` | `notification-backend`, `posting-backend` |
| `mainCompanyId` | `posting-backend`, `user-backend` |
| `mainUserEmail` | `posting-backend`, `user-backend` |
| `mainUserId` | `posting-backend`, `user-backend` |
| `owner` | `notification-backend`, `user-backend` |
| `phone` | `models-lib`, `posting-backend` |
| `profilePicture` | `models-lib`, `trip-planner` |
| `state` | `notification-backend`, `user-backend` |
| `street` | `notification-backend`, `user-backend` |
| `userManagementId` | `models-lib`, `posting-backend` |
| `zipCode` | `notification-backend`, `user-backend` |
| `admin` | `user-backend` |
| `changedFields` | `user-backend` |
| `companyName` | `posting-backend` |

## Use cases

### REST surface

**chat-backend**:
- `ANY v1/discussions` — `src/main/java/cars/ship/shipperlite/chat/application/adapters/in/web/rest/controller/DiscussionController.java`
- `GET /unread` — `src/main/java/cars/ship/shipperlite/chat/application/adapters/in/web/rest/controller/DiscussionController.java`

**crm-workflows**:
- `ANY /{userId}` — `services/src/main/java/cars/ship/crm/workflows/services/clients/UserManagementClient.java`

**loadbuilder-backend**:
- `GET /{jobId}/status` — `api-services/src/main/java/cars/ship/loadbuilder/rest/BuildLoadsController.java`
- `GET /{jobId}` — `api-services/src/main/java/cars/ship/loadbuilder/rest/BuildLoadsController.java`
- `GET /active` — `api-services/src/main/java/cars/ship/loadbuilder/rest/BuildLoadsController.java`
- `DELETE /{jobId}` — `api-services/src/main/java/cars/ship/loadbuilder/rest/SuggestLoadsController.java`

**user-backend**:
- `GET /search` — `usermanagement-app/src/main/java/cars/ship/shipperlite/user/application/adapters/in/web/rest/controllers/v1/V1UserAccountController.java`
- `GET current-user` — `usermanagement-app/src/main/java/cars/ship/shipperlite/user/application/adapters/in/web/rest/controllers/v1/V1UserAccountController.java`
- `GET /email` — `usermanagement-app/src/main/java/cars/ship/shipperlite/user/application/adapters/in/web/rest/controllers/v2/V2InternalUserAccountController.java`
- `PUT /{userId}` — `usermanagement-app/src/main/java/cars/ship/shipperlite/user/application/adapters/in/web/rest/controllers/v2/V2InternalUserAccountController.java`
- `PUT /{companyId}` — `usermanagement-app/src/main/java/cars/ship/shipperlite/user/application/adapters/in/web/rest/controllers/v2/V2InternalCompanyController.java`
- `POST {childCompanyId}/users` — `usermanagement-app/src/main/java/cars/ship/shipperlite/user/application/adapters/in/web/rest/controllers/v2/V2InternalCompanyChildrenUsersController.java`
- `GET {childCompanyId}/users/{userId}` — `usermanagement-app/src/main/java/cars/ship/shipperlite/user/application/adapters/in/web/rest/controllers/v2/V2InternalCompanyChildrenUsersController.java`
- `GET {childCompanyId}/users` — `usermanagement-app/src/main/java/cars/ship/shipperlite/user/application/adapters/in/web/rest/controllers/v2/V2InternalCompanyChildrenUsersController.java`
- `PUT /{childCompanyId}/users/{userId}` — `usermanagement-app/src/main/java/cars/ship/shipperlite/user/application/adapters/in/web/rest/controllers/v2/V2InternalCompanyChildrenUsersController.java`
- `GET /current` — `usermanagement-app/src/main/java/cars/ship/shipperlite/user/application/adapters/in/web/rest/controllers/v2/V2UserAccountController.java`

### Repository operations

**notification-backend**:
- `notification-app/src/main/java/cars/ship/shipperlite/notification/domain/ports/out/repo/UserRepository.java` — `UserAccount`
  - methods: `findByExternalId()`, `findByEmailIgnoreCase()`, `findByExternalIdInAndActiveTrue()`

**posting-backend**:
- `posting-app/src/main/java/cars/ship/shipperlite/posting/domain/ports/out/repo/UserRepository.java` — `UserAccount`
  - methods: `findById()`, `findByExternalId()`, `findByEmail()`, `findByEmailAndExternalCompanyId()`, `findByPhoneAndExternalCompanyId()`, `save()`, `findByKeyCloakId()`, `findOwnerByCompanyId()`, `findAllBySearchAndExternalCompanyId()`

### Carried by Pub/Sub topics

- [`user-state-v2`](../../relations/event-schemas/user-state-v2.md) — DTO `V2UserAccountPubSubDto`

## Cross-references

- Owning service shadow: [`user-backend`](../../repos/user-backend.md)
- Domain rollup: [`communication`](../communication.md)
- Domain rollup: [`identity`](../identity.md)
- Domain rollup: [`integrations`](../integrations.md)
- Domain rollup: [`listings-trade`](../listings-trade.md)
- Domain rollup: [`operations`](../operations.md)
- Domain rollup: [`platform`](../platform.md)
- Master index: [`entity-catalog.md`](../../relations/entity-catalog.md)
