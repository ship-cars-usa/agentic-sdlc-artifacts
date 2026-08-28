---
entity: Contact
aliases: [Contact, ContactDto, ContactEntity, ContactReadDto, PublicTrackingContactDto, V1ContactPubSubDto]
status: auto-generated
domains: [integrations, listings-trade, operations, platform, pricing-billing]
occurrence-count: 9
variant-count: 9
owning-service: posting-backend
last-extracted-date: 2026-05-15
---

# Contact

## What it is

TODO: human narrative. 9 variants across 7 repos and 5 domains (integrations, listings-trade, operations, platform, pricing-billing). Owning service: [`posting-backend`](../../repos/posting-backend.md).

## Variants

| Repo | Class | Kind | Module | Extends | Field count | Module path |
|---|---|---|---|---|---:|---|
| [command-executor](../../repos/command-executor.md) | `ContactDto` | dto | `api-dtos` | — | 0 | `api-dtos/src/main/java/cars/ship/commandexecutor/dtos/quotemanager/ContactDto.java` |
| [invoices](../../repos/invoices.md) | `ContactEntity` | jpa | `db-entities` | `BaseDbEntity` | 7 | `db-entities/src/main/java/cars/ship/invoices/entities/ContactEntity.java` |
| [loadbuilder-backend](../../repos/loadbuilder-backend.md) | `ContactDto` | dto | `infra-interfaces` | — | 17 | `infra-interfaces/src/main/java/cars/ship/loadbuilder/infra/quotemanager/dtos/order/ContactDto.java` |
| [models-lib](../../repos/models-lib.md) | `ContactReadDto` | dto | `read-models` | — | 13 | `read-models/src/main/java/cars/ship/modelslib/readmodels/posting/ContactReadDto.java` |
| [posting-backend](../../repos/posting-backend.md) | `Contact` | jpa | `posting-app` | `BaseEntity` | 23 | `posting-app/src/main/java/cars/ship/shipperlite/posting/domain/model/Contact.java` |
| [posting-backend](../../repos/posting-backend.md) | `ContactDto` | dto | `posting-dtos` | — | 18 | `posting-dtos/src/main/java/cars/ship/posting/dtos/ContactDto.java` |
| [posting-backend](../../repos/posting-backend.md) | `V1ContactPubSubDto` | dto | `posting-dtos` | — | 12 | `posting-dtos/src/main/java/cars/ship/posting/dtos/pubsub/v1/V1ContactPubSubDto.java` |
| [public-tracking-backend](../../repos/public-tracking-backend.md) | `PublicTrackingContactDto` | dto | `public-tracking-backend` | — | 0 | `src/main/java/cars/ship/publictracking/application/adapters/in/rest/dtos/PublicTrackingContactDto.java` |
| [quote-manager-backend](../../repos/quote-manager-backend.md) | `ContactDto` | dto | `quote-manager-backend` | — | 17 | `src/main/java/cars/ship/quotemanager/application/adapters/in/web/rest/dto/ContactDto.java` |

## Field union / intersection

**Core fields** (present in ≥60% of variants — 5/9 or more):

_(no fields shared by ≥60% of variants — high heterogeneity)_

**Variant-specific fields** (present in <60% of variants, top 30 by spread):

| Field | Repos that declare it |
|---|---|
| `companyName` | `invoices`, `loadbuilder-backend`, `posting-backend`, `quote-manager-backend` |
| `id` | `loadbuilder-backend`, `models-lib`, `posting-backend`, `quote-manager-backend` |
| `primaryPhoneNotes` | `loadbuilder-backend`, `models-lib`, `posting-backend`, `quote-manager-backend` |
| `secondaryPhone` | `loadbuilder-backend`, `models-lib`, `posting-backend`, `quote-manager-backend` |
| `secondaryPhoneNotes` | `loadbuilder-backend`, `models-lib`, `posting-backend`, `quote-manager-backend` |
| `thirdPhone` | `loadbuilder-backend`, `models-lib`, `posting-backend`, `quote-manager-backend` |
| `thirdPhoneNotes` | `loadbuilder-backend`, `models-lib`, `posting-backend`, `quote-manager-backend` |
| `workingHours` | `loadbuilder-backend`, `models-lib`, `posting-backend`, `quote-manager-backend` |
| `location` | `invoices`, `models-lib`, `posting-backend` |
| `autoImsClientId` | `models-lib`, `posting-backend` |
| `city` | `loadbuilder-backend`, `quote-manager-backend` |
| `createdAt` | `models-lib`, `posting-backend` |
| `email` | `invoices`, `posting-backend` |
| `emailAddress` | `loadbuilder-backend`, `quote-manager-backend` |
| `firstName` | `loadbuilder-backend`, `quote-manager-backend` |
| `lastModified` | `models-lib`, `posting-backend` |
| `lastName` | `loadbuilder-backend`, `quote-manager-backend` |
| `locationId` | `loadbuilder-backend`, `quote-manager-backend` |
| `name` | `invoices`, `posting-backend` |
| `notes` | `models-lib`, `posting-backend` |
| `phoneNumber` | `loadbuilder-backend`, `quote-manager-backend` |
| `state` | `loadbuilder-backend`, `quote-manager-backend` |
| `streetAddress` | `loadbuilder-backend`, `quote-manager-backend` |
| `type` | `models-lib`, `posting-backend` |
| `zipCode` | `loadbuilder-backend`, `quote-manager-backend` |
| `active` | `posting-backend` |
| `allEmails` | `posting-backend` |
| `company` | `posting-backend` |
| `companyId` | `posting-backend` |
| `defaultContactsExclusions` | `posting-backend` |

## Use cases

### REST surface

**posting-backend**:
- `PUT /{id}` — `posting-app/src/main/java/cars/ship/shipperlite/posting/application/adapters/in/web/rest/controller/ContactG2Controller.java`
- `POST upload/csv` — `posting-app/src/main/java/cars/ship/shipperlite/posting/application/adapters/in/web/rest/controller/ContactG1Controller.java`

### Repository operations

_(no Spring Data / Panache repositories typed on this entity found)_

### Carried by Pub/Sub topics

_(no resolved Pub/Sub schemas reference this entity; check `relations/event-schemas/` for unresolved canonical-dto fields)_

## Cross-references

- Owning service shadow: [`posting-backend`](../../repos/posting-backend.md)
- Domain rollup: [`integrations`](../integrations.md)
- Domain rollup: [`listings-trade`](../listings-trade.md)
- Domain rollup: [`operations`](../operations.md)
- Domain rollup: [`platform`](../platform.md)
- Domain rollup: [`pricing-billing`](../pricing-billing.md)
- Master index: [`entity-catalog.md`](../../relations/entity-catalog.md)
