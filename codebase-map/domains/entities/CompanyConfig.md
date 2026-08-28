---
entity: CompanyConfig
aliases: [CompanyConfig, CompanyConfigDbEntity, CompanyConfigDto, CompanyConfigEntity, PublicCompanyConfigDto]
status: auto-generated
domains: [analytics, integrations, pricing-billing]
occurrence-count: 10
variant-count: 10
owning-service: integrations-backend
last-extracted-date: 2026-05-15
---

# CompanyConfig

## What it is

TODO: human narrative. 10 variants across 5 repos and 3 domains (analytics, integrations, pricing-billing). Owning service: [`integrations-backend`](../../repos/integrations-backend.md).

## Variants

| Repo | Class | Kind | Module | Extends | Field count | Module path |
|---|---|---|---|---|---:|---|
| [autoims-backend](../../repos/autoims-backend.md) | `CompanyConfigDbEntity` | jpa | `db-entities` | `BaseDbEntity` | 28 | `db-entities/src/main/java/cars/ship/autoims/db/entities/companyconfig/CompanyConfigDbEntity.java` |
| [autoims-backend](../../repos/autoims-backend.md) | `CompanyConfigDto` | dto | `api-dtos` | — | 0 | `api-dtos/src/main/java/cars/ship/autoims/dtos/companyconfig/CompanyConfigDto.java` |
| [bi-databricks-backend](../../repos/bi-databricks-backend.md) | `CompanyConfig` | jpa | `bi-databricks-backend` | `BaseDbEntity` | 5 | `src/main/java/cars/ship/databricks/entity/CompanyConfig.java` |
| [bi-databricks-backend](../../repos/bi-databricks-backend.md) | `CompanyConfigDto` | dto | `bi-databricks-backend` | — | 0 | `src/main/java/cars/ship/databricks/dtos/CompanyConfigDto.java` |
| [integrations-backend](../../repos/integrations-backend.md) | `CompanyConfig` | dto | `quickbooks` | — | 0 | `quickbooks/api-dtos/src/main/java/cars/ship/integrations/quickbooks/dtos/CompanyConfig.java` |
| [payment-backend](../../repos/payment-backend.md) | `CompanyConfigDto` | dto | `api-dtos` | — | 0 | `api-dtos/src/main/java/cars/ship/payment/dtos/CompanyConfigDto.java` |
| [payment-backend](../../repos/payment-backend.md) | `CompanyConfigEntity` | jpa | `db-entities` | `BaseDbEntity` | 4 | `db-entities/src/main/java/cars/ship/payment/entities/CompanyConfigEntity.java` |
| [payment-backend](../../repos/payment-backend.md) | `PublicCompanyConfigDto` | dto | `api-dtos` | — | 0 | `api-dtos/src/main/java/cars/ship/payment/dtos/PublicCompanyConfigDto.java` |
| [uship-quotes](../../repos/uship-quotes.md) | `CompanyConfigDto` | dto | `api-dtos` | — | 0 | `api-dtos/src/main/java/cars/ship/uship/dtos/out/config/CompanyConfigDto.java` |
| [uship-quotes](../../repos/uship-quotes.md) | `CompanyConfigEntity` | jpa | `db-entities` | — | 7 | `db-entities/src/main/java/cars/ship/uship/quotes/entities/CompanyConfigEntity.java` |

## Field union / intersection

**Core fields** (present in ≥60% of variants — 6/10 or more):

_(no fields shared by ≥60% of variants — high heterogeneity)_

**Variant-specific fields** (present in <60% of variants, top 30 by spread):

| Field | Repos that declare it |
|---|---|
| `companyId` | `bi-databricks-backend`, `payment-backend` |
| `authType` | `autoims-backend` |
| `botConfig` | `uship-quotes` |
| `clientId` | `bi-databricks-backend` |
| `clientSecret` | `bi-databricks-backend` |
| `companyName` | `uship-quotes` |
| `config` | `uship-quotes` |
| `createdAt` | `uship-quotes` |
| `dashboard` | `bi-databricks-backend` |
| `dashboards` | `bi-databricks-backend` |
| `data` | `payment-backend` |
| `id` | `uship-quotes` |
| `lastModified` | `uship-quotes` |
| `referenceId` | `payment-backend` |
| `requesterId` | `autoims-backend` |
| `secret` | `payment-backend` |
| `secretKey` | `autoims-backend` |
| `secretValue` | `autoims-backend` |
| `syncFromArchiveStatuses` | `autoims-backend` |
| `syncFromAutoImsBaseUrl` | `autoims-backend` |
| `syncFromAutoImsCronEnabled` | `autoims-backend` |
| `syncFromAutoImsEndpoint` | `autoims-backend` |
| `syncFromAutoImsFormat` | `autoims-backend` |
| `syncFromAutoImsIntervalMinutes` | `autoims-backend` |
| `syncFromAutoImsLast` | `autoims-backend` |
| `syncFromAutoImsLastStatus` | `autoims-backend` |
| `syncFromAutoImsLastSuccessful` | `autoims-backend` |
| `syncFromAutoImsNext` | `autoims-backend` |
| `syncFromAutoImsPutOnHold` | `autoims-backend` |
| `syncFromEnabledStatuses` | `autoims-backend` |

## Use cases

### REST surface

**autoims-backend**:
- `POST /update-sync-times` — `api-services/src/main/java/cars/ship/autoims/rest/CompanyConfigController.java`

**bi-databricks-backend**:
- `ANY /api/dashboards` — `src/main/java/cars/ship/databricks/resource/DashboardResource.java`
- `ANY /{userId}/{companyId}` — `src/main/java/cars/ship/databricks/resource/DashboardResource.java`
- `ANY /internal/company-config` — `src/main/java/cars/ship/databricks/resource/CompanyConfigResource.java`
- `ANY /{companyId}` — `src/main/java/cars/ship/databricks/resource/CompanyConfigResource.java`

**integrations-backend**:
- `POST /connect` — `quickbooks/resources/src/main/java/cars/ship/integrations/quickbooks/rest/controllers/AuthorizationController.java`
- `GET /status` — `quickbooks/resources/src/main/java/cars/ship/integrations/quickbooks/rest/controllers/AuthorizationController.java`
- `POST /disconnect` — `quickbooks/resources/src/main/java/cars/ship/integrations/quickbooks/rest/controllers/AuthorizationController.java`
- `GET /service-items` — `quickbooks/resources/src/main/java/cars/ship/integrations/quickbooks/rest/controllers/ConfigurationController.java`
- `GET /invoice-description-fields` — `quickbooks/resources/src/main/java/cars/ship/integrations/quickbooks/rest/controllers/ConfigurationController.java`
- `PUT /config` — `quickbooks/resources/src/main/java/cars/ship/integrations/quickbooks/rest/controllers/ConfigurationController.java`
- `GET /config` — `quickbooks/resources/src/main/java/cars/ship/integrations/quickbooks/rest/controllers/ConfigurationController.java`

**payment-backend**:
- `ANY /{shipperCompanyId}/carriers/{carrierCompanyId}/integration` — `resources/src/main/java/cars/ship/payment/rest/v1/ShipperController.java`
- `ANY /{shipperCompanyId}/config` — `resources/src/main/java/cars/ship/payment/rest/v1/ShipperController.java`
- `ANY /{shipperCompanyId}/payment-etas` — `resources/src/main/java/cars/ship/payment/rest/v1/ShipperController.java`
- `ANY /{companyId}` — `resources/src/main/java/cars/ship/payment/rest/v1/internal/CompanyConfigInternalController.java`
- `ANY /{companyConfigId}` — `resources/src/main/java/cars/ship/payment/rest/v1/internal/CompanyConfigInternalController.java`
- `ANY /{companyId}/audit` — `resources/src/main/java/cars/ship/payment/rest/v1/internal/CompanyConfigInternalController.java`

**uship-quotes**:
- `ANY /{id}` — `resources/src/main/java/cars/ship/uship/quotes/rest/CompanyConfigsResource.java`
- `ANY /{id}/preview-quote` — `resources/src/main/java/cars/ship/uship/quotes/rest/CompanyConfigsResource.java`
- `ANY /{id}/revisions` — `resources/src/main/java/cars/ship/uship/quotes/rest/CompanyConfigsResource.java`

### Repository operations

**autoims-backend**:
- `db-entities/src/main/java/cars/ship/autoims/db/entities/companyconfig/CompanyConfigDbRepository.java` — `CompanyConfigDbEntity`
  - methods: `findByPublicIdAndActiveIsTrue()`, `findAllCompanyConfigsForSync()`, `updateSyncToAutoImsLastSync()`, `updateSyncToAutoImsLastSuccessfulNext()`, `updateSyncFromAutoImsLastSuccessfulNext()`, `updateSyncFromAutoImsLastSuccessful()`

### Carried by Pub/Sub topics

_(no resolved Pub/Sub schemas reference this entity; check `relations/event-schemas/` for unresolved canonical-dto fields)_

## Cross-references

- Owning service shadow: [`integrations-backend`](../../repos/integrations-backend.md)
- Domain rollup: [`analytics`](../analytics.md)
- Domain rollup: [`integrations`](../integrations.md)
- Domain rollup: [`pricing-billing`](../pricing-billing.md)
- Master index: [`entity-catalog.md`](../../relations/entity-catalog.md)
