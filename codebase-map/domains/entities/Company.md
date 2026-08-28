---
entity: Company
aliases: [Carrier, CarrierDto, CarrierEntity, CarrierReadDto, Company, CompanyDto, CompanyEntity, CompanyEventDto, CompanyReadDto, Customer, CustomerDto, CustomerEntity, CustomerPubSubDto, CustomerReadDto, DbCompany, DbCompanyDto, V1CarrierPubSubDto, V1CompanyDto, V2CompanyDto, V2CompanyPubSubDto]
status: auto-generated
domains: [communication, identity, integrations, listings-trade, operations, platform, pricing-billing]
occurrence-count: 42
variant-count: 42
owning-service: inventory-backend
last-extracted-date: 2026-05-15
---

# Company

## What it is

TODO: human narrative. 42 variants across 18 repos and 7 domains (communication, identity, integrations, listings-trade, operations, platform, pricing-billing). Owning service: [`inventory-backend`](../../repos/inventory-backend.md).

## Variants

| Repo | Class | Kind | Module | Extends | Field count | Module path |
|---|---|---|---|---|---:|---|
| [chat-backend](../../repos/chat-backend.md) | `Company` | jpa | `chat-backend` | `BaseEntity` | 7 | `src/main/java/cars/ship/shipperlite/chat/domain/model/Company.java` |
| [contract-pricing-backend](../../repos/contract-pricing-backend.md) | `CarrierDto` | dto | `contract-pricing-dtos` | — | 0 | `contract-pricing-dtos/src/main/java/cars/ship/contractpricing/dtos/CarrierDto.java` |
| [contract-pricing-backend](../../repos/contract-pricing-backend.md) | `CarrierEntity` | jpa | `db-entities` | `BaseDbEntity` | 8 | `db-entities/src/main/java/cars/ship/contractpricing/entities/CarrierEntity.java` |
| [contract-pricing-backend](../../repos/contract-pricing-backend.md) | `CustomerDto` | dto | `contract-pricing-dtos` | — | 0 | `contract-pricing-dtos/src/main/java/cars/ship/contractpricing/dtos/CustomerDto.java` |
| [contract-pricing-backend](../../repos/contract-pricing-backend.md) | `CustomerEntity` | jpa | `db-entities` | `BaseDbEntity` | 10 | `db-entities/src/main/java/cars/ship/contractpricing/entities/CustomerEntity.java` |
| [crm-workflows](../../repos/crm-workflows.md) | `Company` | dto | `services` | — | 19 | `services/src/main/java/cars/ship/crm/workflows/models/Company.java` |
| [crm-workflows](../../repos/crm-workflows.md) | `CompanyEntity` | jpa | `db-entities` | `BaseDbEntity` | 14 | `db-entities/src/main/java/cars/ship/crm/workflows/entities/CompanyEntity.java` |
| [cube](../../repos/cube.md) | `CompanyDto` | dto | `loadboard` | — | 2 | `loadboard/loadboard-dtos/src/main/java/cars/ship/cube/dtos/out/CompanyDto.java` |
| [inventory-backend](../../repos/inventory-backend.md) | `CustomerDto` | dto | `inventory-dtos` | — | 0 | `inventory-dtos/src/main/java/cars/ship/inventory/dtos/units/CustomerDto.java` |
| [invoices](../../repos/invoices.md) | `CompanyEntity` | jpa | `db-entities` | `BaseDbEntity` | 4 | `db-entities/src/main/java/cars/ship/invoices/entities/CompanyEntity.java` |
| [load-recommender](../../repos/load-recommender.md) | `CompanyEntity` | jpa | `db-entities` | `BaseEntity` | 4 | `db-entities/src/main/java/cars/ship/recommender/entities/CompanyEntity.java` |
| [load-recommender](../../repos/load-recommender.md) | `DbCompany` | dto | `db-syncer` | — | 7 | `db-syncer/src/main/java/cars/ship/recommender/sync/models/DbCompany.java` |
| [loadboard-backend](../../repos/loadboard-backend.md) | `Company` | dto | `services` | — | 13 | `services/src/main/java/cars/ship/loadboard/models/Company.java` |
| [loadboard-backend](../../repos/loadboard-backend.md) | `CompanyEntity` | jpa | `db-entities` | `BaseEntity` | 12 | `db-entities/src/main/java/cars/ship/loadboard/entities/CompanyEntity.java` |
| [loadboard-backend](../../repos/loadboard-backend.md) | `Customer` | dto | `services` | — | 20 | `services/src/main/java/cars/ship/loadboard/models/Customer.java` |
| [loadboard-backend](../../repos/loadboard-backend.md) | `CustomerDto` | dto | `api-dtos` | — | 20 | `api-dtos/src/main/java/cars/ship/loadboard/dtos/CustomerDto.java` |
| [loadboard-backend](../../repos/loadboard-backend.md) | `CustomerPubSubDto` | dto | `api-dtos` | — | 20 | `api-dtos/src/main/java/cars/ship/loadboard/dtos/out/pubsub/CustomerPubSubDto.java` |
| [loadboard-backend](../../repos/loadboard-backend.md) | `CustomerReadDto` | dto | `api-dtos` | — | 20 | `api-dtos/src/main/java/cars/ship/loadboard/dtos/out/CustomerReadDto.java` |
| [models-lib](../../repos/models-lib.md) | `CarrierReadDto` | dto | `read-models` | — | 14 | `read-models/src/main/java/cars/ship/modelslib/readmodels/posting/CarrierReadDto.java` |
| [models-lib](../../repos/models-lib.md) | `CompanyDto` | dto | `data-models` | — | 66 | `data-models/src/main/java/cars/ship/modelslib/datamodels/CompanyDto.java` |
| [models-lib](../../repos/models-lib.md) | `CompanyReadDto` | dto | `read-models` | — | 55 | `read-models/src/main/java/cars/ship/modelslib/readmodels/es/CompanyReadDto.java` |
| [models-lib](../../repos/models-lib.md) | `CompanyReadDto` | dto | `read-models` | — | 10 | `read-models/src/main/java/cars/ship/modelslib/readmodels/posting/CompanyReadDto.java` |
| [notification-backend](../../repos/notification-backend.md) | `CompanyDto` | dto | `notification-app` | — | 19 | `notification-app/src/main/java/cars/ship/shipperlite/notification/application/adapters/out/clients/dtos/CompanyDto.java` |
| [notification-orchestrator](../../repos/notification-orchestrator.md) | `CompanyEntity` | jpa | `db-entities` | `BaseEntity` | 2 | `db-entities/src/main/java/cars/ship/notification/orchestrator/entities/CompanyEntity.java` |
| [notification-orchestrator](../../repos/notification-orchestrator.md) | `DbCompany` | dto | `db-syncer` | — | 4 | `db-syncer/src/main/java/cars/ship/notification/orchestrator/sync/models/DbCompany.java` |
| [posting-backend](../../repos/posting-backend.md) | `Carrier` | jpa | `posting-app` | `BaseEntity` | 3 | `posting-app/src/main/java/cars/ship/shipperlite/posting/domain/model/Carrier.java` |
| [posting-backend](../../repos/posting-backend.md) | `CarrierDto` | dto | `posting-dtos` | — | 14 | `posting-dtos/src/main/java/cars/ship/posting/dtos/CarrierDto.java` |
| [posting-backend](../../repos/posting-backend.md) | `Company` | jpa | `posting-app` | `BaseEntity` | 8 | `posting-app/src/main/java/cars/ship/shipperlite/posting/domain/model/Company.java` |
| [posting-backend](../../repos/posting-backend.md) | `CompanyDto` | dto | `posting-dtos` | — | 10 | `posting-dtos/src/main/java/cars/ship/posting/dtos/CompanyDto.java` |
| [posting-backend](../../repos/posting-backend.md) | `V1CarrierPubSubDto` | dto | `posting-dtos` | — | 14 | `posting-dtos/src/main/java/cars/ship/posting/dtos/pubsub/v1/V1CarrierPubSubDto.java` |
| [pusher](../../repos/pusher.md) | `Company` | dto | `commons` | — | 0 | `commons/src/main/java/cars/ship/pusher/shared/models/Company.java` |
| [pusher](../../repos/pusher.md) | `CompanyEntity` | jpa | `db-entities` | — | 3 | `db-entities/src/main/java/cars/ship/pusher/entities/CompanyEntity.java` |
| [pusher](../../repos/pusher.md) | `DbCompanyDto` | dto | `db-syncer` | — | 6 | `db-syncer/src/main/java/cars/ship/pusher/syncer/dtos/db/DbCompanyDto.java` |
| [quarkus-user-syncer](../../repos/quarkus-user-syncer.md) | `CompanyEventDto` | dto | `runtime` | `EventDto` | 0 | `runtime/src/main/java/cars/ship/quarkus/extensions/usersyncer/dtos/CompanyEventDto.java` |
| [quote-manager-backend](../../repos/quote-manager-backend.md) | `CompanyDto` | dto | `quote-manager-backend` | — | 6 | `src/main/java/cars/ship/quotemanager/application/adapters/out/clients/dto/usermanagment/CompanyDto.java` |
| [saved-search-handler](../../repos/saved-search-handler.md) | `CompanyEntity` | jpa | `db-entities` | — | 1 | `db-entities/src/main/java/cars/ship/search/entities/CompanyEntity.java` |
| [trip-planner](../../repos/trip-planner.md) | `CompanyEntity` | jpa | `db-entities` | `BaseDbEntity` | 2 | `db-entities/src/main/java/cars/ship/planner/entities/CompanyEntity.java` |
| [trip-planner](../../repos/trip-planner.md) | `DbCompanyDto` | dto | `db-syncer` | — | 2 | `db-syncer/src/main/java/cars/ship/planner/sync/models/db/DbCompanyDto.java` |
| [user-backend](../../repos/user-backend.md) | `Company` | jpa | `usermanagement-app` | `BaseEntity` | 29 | `usermanagement-app/src/main/java/cars/ship/shipperlite/user/domain/model/Company.java` |
| [user-backend](../../repos/user-backend.md) | `V1CompanyDto` | dto | `usermanagement-dtos` | — | 23 | `usermanagement-dtos/src/main/java/cars/ship/usermanagement/dtos/v1/V1CompanyDto.java` |
| [user-backend](../../repos/user-backend.md) | `V2CompanyDto` | dto | `usermanagement-dtos` | — | 27 | `usermanagement-dtos/src/main/java/cars/ship/usermanagement/dtos/v2/V2CompanyDto.java` |
| [user-backend](../../repos/user-backend.md) | `V2CompanyPubSubDto` | dto | `usermanagement-dtos` | — | 30 | `usermanagement-dtos/src/main/java/cars/ship/usermanagement/dtos/v2/V2CompanyPubSubDto.java` |

## Field union / intersection

**Core fields** (present in ≥60% of variants — 25/42 or more):

_(no fields shared by ≥60% of variants — high heterogeneity)_

**Variant-specific fields** (present in <60% of variants, top 30 by spread):

| Field | Repos that declare it |
|---|---|
| `name` | `chat-backend`, `contract-pricing-backend`, `crm-workflows`, `cube`, `invoices`, `load-recommender`, `loadboard-backend`, `models-lib`, `notification-backend`, `notification-orchestrator`, `posting-backend`, `pusher`, `quote-manager-backend`, `user-backend` |
| `email` | `chat-backend`, `crm-workflows`, `load-recommender`, `loadboard-backend`, `models-lib`, `notification-backend`, `notification-orchestrator`, `posting-backend`, `pusher`, `quote-manager-backend`, `user-backend` |
| `id` | `cube`, `load-recommender`, `loadboard-backend`, `models-lib`, `notification-backend`, `notification-orchestrator`, `posting-backend`, `pusher`, `saved-search-handler`, `trip-planner`, `user-backend` |
| `active` | `crm-workflows`, `load-recommender`, `loadboard-backend`, `notification-orchestrator`, `pusher`, `trip-planner`, `user-backend` |
| `logoUrl` | `chat-backend`, `loadboard-backend`, `models-lib`, `notification-backend`, `posting-backend`, `user-backend` |
| `usDotNumber` | `crm-workflows`, `loadboard-backend`, `models-lib`, `notification-backend`, `posting-backend`, `user-backend` |
| `companyType` | `chat-backend`, `crm-workflows`, `loadboard-backend`, `notification-backend`, `user-backend` |
| `externalUpdateTime` | `crm-workflows`, `load-recommender`, `notification-orchestrator`, `pusher`, `trip-planner` |
| `city` | `loadboard-backend`, `models-lib`, `notification-backend`, `user-backend` |
| `lastModified` | `crm-workflows`, `load-recommender`, `pusher`, `user-backend` |
| `phoneNumber` | `chat-backend`, `notification-backend`, `quote-manager-backend`, `user-backend` |
| `state` | `loadboard-backend`, `models-lib`, `notification-backend`, `user-backend` |
| `accountingEmail` | `models-lib`, `posting-backend`, `user-backend` |
| `accountingEmails` | `models-lib`, `posting-backend`, `user-backend` |
| `externalId` | `chat-backend`, `contract-pricing-backend`, `posting-backend` |
| `isSingleOwnerOperator` | `models-lib`, `pusher`, `user-backend` |
| `lastModifiedUserBe` | `chat-backend`, `contract-pricing-backend`, `posting-backend` |
| `location` | `invoices`, `models-lib`, `posting-backend` |
| `mcNumber` | `models-lib`, `notification-backend`, `user-backend` |
| `phone` | `crm-workflows`, `invoices`, `loadboard-backend` |
| `primaryPhone` | `loadboard-backend`, `models-lib`, `posting-backend` |
| `primaryPhoneNotes` | `loadboard-backend`, `models-lib`, `posting-backend` |
| `secondaryPhone` | `loadboard-backend`, `models-lib`, `posting-backend` |
| `secondaryPhoneNotes` | `loadboard-backend`, `models-lib`, `posting-backend` |
| `singleOwnerOperator` | `notification-backend`, `pusher`, `user-backend` |
| `subscriptionStatus` | `crm-workflows`, `load-recommender`, `posting-backend` |
| `thirdPhone` | `loadboard-backend`, `models-lib`, `posting-backend` |
| `thirdPhoneNotes` | `loadboard-backend`, `models-lib`, `posting-backend` |
| `usDot` | `crm-workflows`, `models-lib`, `posting-backend` |
| `address` | `loadboard-backend`, `models-lib` |

## Use cases

### REST surface

**contract-pricing-backend**:
- `ANY /{id}` — `resources/src/main/java/cars/ship/contractpricing/rest/ContractPricingController.java`
- `POST /{id}` — `resources/src/main/java/cars/ship/contractpricing/rest/ContractPricingController.java`
- `ANY regions/templates` — `resources/src/main/java/cars/ship/contractpricing/rest/ContractPricingController.java`
- `ANY /internal/v2/companies/search` — `services/src/main/java/cars/ship/contractpricing/clients/UserManagementClient.java`

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

**invoices**:
- `ANY /internal/v2/companies/{COMPANY_ID}` — `services/src/main/java/cars/ship/invoices/clients/UserManagementClient.java`

**user-backend**:
- `POST /register` — `usermanagement-app/src/main/java/cars/ship/shipperlite/user/application/adapters/in/web/rest/controllers/v1/V1CompanyRegisterController.java`
- `PUT /{companyId}` — `usermanagement-app/src/main/java/cars/ship/shipperlite/user/application/adapters/in/web/rest/controllers/v2/V2InternalCompanyController.java`
- `POST {childCompanyId}/users` — `usermanagement-app/src/main/java/cars/ship/shipperlite/user/application/adapters/in/web/rest/controllers/v2/V2InternalCompanyChildrenUsersController.java`
- `GET {childCompanyId}/users/{userId}` — `usermanagement-app/src/main/java/cars/ship/shipperlite/user/application/adapters/in/web/rest/controllers/v2/V2InternalCompanyChildrenUsersController.java`
- `GET {childCompanyId}/users` — `usermanagement-app/src/main/java/cars/ship/shipperlite/user/application/adapters/in/web/rest/controllers/v2/V2InternalCompanyChildrenUsersController.java`
- `PUT /{childCompanyId}/users/{userId}` — `usermanagement-app/src/main/java/cars/ship/shipperlite/user/application/adapters/in/web/rest/controllers/v2/V2InternalCompanyChildrenUsersController.java`
- `POST /add` — `usermanagement-app/src/main/java/cars/ship/shipperlite/user/application/adapters/in/web/rest/controllers/v2/V2InternalCompanyChildrenController.java`
- `GET {childCompanyId}` — `usermanagement-app/src/main/java/cars/ship/shipperlite/user/application/adapters/in/web/rest/controllers/v2/V2InternalCompanyChildrenController.java`
- `PUT /{childCompanyId}` — `usermanagement-app/src/main/java/cars/ship/shipperlite/user/application/adapters/in/web/rest/controllers/v2/V2InternalCompanyChildrenController.java`
- `POST /keycloak/sync-plan` — `usermanagement-app/src/main/java/cars/ship/shipperlite/user/application/adapters/in/web/rest/controllers/v2/V2InternalCompanyChildrenController.java`
- `POST /{childCompanyId}/keycloak/sync-plan` — `usermanagement-app/src/main/java/cars/ship/shipperlite/user/application/adapters/in/web/rest/controllers/v2/V2InternalCompanyChildrenController.java`
- `GET /{companyId}/profile` — `usermanagement-app/src/main/java/cars/ship/shipperlite/user/application/adapters/in/web/rest/controllers/v2/V2PublicCompanyController.java`
- `PUT /public-profile` — `usermanagement-app/src/main/java/cars/ship/shipperlite/user/application/adapters/in/web/rest/controllers/v2/V2CompanyController.java`
- `GET /public-profile` — `usermanagement-app/src/main/java/cars/ship/shipperlite/user/application/adapters/in/web/rest/controllers/v2/V2CompanyController.java`

### Repository operations

_(no Spring Data / Panache repositories typed on this entity found)_

### Carried by Pub/Sub topics

_(no resolved Pub/Sub schemas reference this entity; check `relations/event-schemas/` for unresolved canonical-dto fields)_

## Cross-references

- Owning service shadow: [`inventory-backend`](../../repos/inventory-backend.md)
- Domain rollup: [`communication`](../communication.md)
- Domain rollup: [`identity`](../identity.md)
- Domain rollup: [`integrations`](../integrations.md)
- Domain rollup: [`listings-trade`](../listings-trade.md)
- Domain rollup: [`operations`](../operations.md)
- Domain rollup: [`platform`](../platform.md)
- Domain rollup: [`pricing-billing`](../pricing-billing.md)
- Master index: [`entity-catalog.md`](../../relations/entity-catalog.md)
