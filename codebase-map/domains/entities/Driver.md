---
entity: Driver
aliases: [DriveawayDriver, DriveawayDriverDto, DriveawayDriverReadDto, Driver, DriverDto, DriverReadDto, ExternalDriveawayDriverDto, V1DriveawayDriverPubSubDto, V1DriverPubSubDto]
status: auto-generated
domains: [listings-trade, operations, platform]
occurrence-count: 11
variant-count: 11
owning-service: posting-backend
last-extracted-date: 2026-05-15
---

# Driver

## What it is

TODO: human narrative. 11 variants across 3 repos and 3 domains (listings-trade, operations, platform). Owning service: [`posting-backend`](../../repos/posting-backend.md).

## Variants

| Repo | Class | Kind | Module | Extends | Field count | Module path |
|---|---|---|---|---|---:|---|
| [driveaway-backend](../../repos/driveaway-backend.md) | `DriveawayDriver` | jpa | `db-entities` | `BaseDbEntity` | 13 | `db-entities/src/main/java/cars/ship/driveaway/db/entities/driver/DriveawayDriver.java` |
| [driveaway-backend](../../repos/driveaway-backend.md) | `DriveawayDriverDto` | dto | `api-dtos` | — | 13 | `api-dtos/src/main/java/cars/ship/driveaway/dtos/drivers/DriveawayDriverDto.java` |
| [models-lib](../../repos/models-lib.md) | `DriveawayDriverReadDto` | dto | `read-models` | — | 7 | `read-models/src/main/java/cars/ship/modelslib/readmodels/posting/DriveawayDriverReadDto.java` |
| [models-lib](../../repos/models-lib.md) | `DriverReadDto` | dto | `read-models` | — | 8 | `read-models/src/main/java/cars/ship/modelslib/readmodels/posting/DriverReadDto.java` |
| [posting-backend](../../repos/posting-backend.md) | `DriveawayDriver` | jpa | `posting-app` | `BaseEntity` | 7 | `posting-app/src/main/java/cars/ship/shipperlite/posting/domain/model/DriveawayDriver.java` |
| [posting-backend](../../repos/posting-backend.md) | `DriveawayDriverDto` | dto | `posting-dtos` | — | 8 | `posting-dtos/src/main/java/cars/ship/posting/dtos/DriveawayDriverDto.java` |
| [posting-backend](../../repos/posting-backend.md) | `Driver` | jpa | `posting-app` | `BaseEntity` | 3 | `posting-app/src/main/java/cars/ship/shipperlite/posting/domain/model/Driver.java` |
| [posting-backend](../../repos/posting-backend.md) | `DriverDto` | dto | `posting-dtos` | — | 8 | `posting-dtos/src/main/java/cars/ship/posting/dtos/DriverDto.java` |
| [posting-backend](../../repos/posting-backend.md) | `ExternalDriveawayDriverDto` | dto | `posting-app` | `DriveawayDriverDto` | 5 | `posting-app/src/main/java/cars/ship/shipperlite/posting/application/adapters/out/clients/dto/driveaway/ExternalDriveawayDriverDto.java` |
| [posting-backend](../../repos/posting-backend.md) | `V1DriveawayDriverPubSubDto` | dto | `posting-dtos` | — | 4 | `posting-dtos/src/main/java/cars/ship/posting/dtos/pubsub/v1/V1DriveawayDriverPubSubDto.java` |
| [posting-backend](../../repos/posting-backend.md) | `V1DriverPubSubDto` | dto | `posting-dtos` | — | 6 | `posting-dtos/src/main/java/cars/ship/posting/dtos/pubsub/v1/V1DriverPubSubDto.java` |

## Field union / intersection

**Core fields** (present in ≥60% of variants — 6/11 or more):

_(no fields shared by ≥60% of variants — high heterogeneity)_

**Variant-specific fields** (present in <60% of variants, top 30 by spread):

| Field | Repos that declare it |
|---|---|
| `companyName` | `driveaway-backend`, `models-lib`, `posting-backend` |
| `email` | `driveaway-backend`, `models-lib`, `posting-backend` |
| `id` | `driveaway-backend`, `models-lib`, `posting-backend` |
| `name` | `driveaway-backend`, `models-lib`, `posting-backend` |
| `phone` | `driveaway-backend`, `models-lib`, `posting-backend` |
| `phoneNotes` | `driveaway-backend`, `models-lib`, `posting-backend` |
| `additionalPhone` | `models-lib`, `posting-backend` |
| `address` | `driveaway-backend`, `posting-backend` |
| `city` | `driveaway-backend`, `posting-backend` |
| `enforceTermsAndConditions` | `driveaway-backend`, `posting-backend` |
| `externalId` | `models-lib`, `posting-backend` |
| `lbExternalId` | `models-lib`, `posting-backend` |
| `location` | `models-lib`, `posting-backend` |
| `profilePictureUrl` | `models-lib`, `posting-backend` |
| `state` | `driveaway-backend`, `posting-backend` |
| `userManagementId` | `models-lib`, `posting-backend` |
| `zip` | `driveaway-backend`, `posting-backend` |
| `active` | `driveaway-backend` |
| `companyId` | `driveaway-backend` |
| `notes` | `driveaway-backend` |
| `searchableContent` | `driveaway-backend` |
| `userAccount` | `posting-backend` |

## Use cases

### REST surface

**posting-backend**:
- `POST /loads` — `posting-app/src/main/java/cars/ship/shipperlite/posting/application/adapters/in/web/rest/controller/ChaseDriverController.java`

### Repository operations

**driveaway-backend**:
- `db-entities/src/main/java/cars/ship/driveaway/db/entities/driver/DriveawayDriverRepository.java` — `DriveawayDriver`
  - methods: `driverExists()`, `existsByCompanyIdAndNameIgnoreCaseAndCompanyNameIgnoreCaseAndPhone()`, `existsByCompanyIdAndNameIgnoreCaseAndPhone()`, `findAllByCompanyIdAndSearchableContentContains()`, `findAllByCompanyIdAndSearchableContentContainsAndActive()`, `findByIdAndCompanyId()`

### Carried by Pub/Sub topics

_(no resolved Pub/Sub schemas reference this entity; check `relations/event-schemas/` for unresolved canonical-dto fields)_

## Cross-references

- Owning service shadow: [`posting-backend`](../../repos/posting-backend.md)
- Domain rollup: [`listings-trade`](../listings-trade.md)
- Domain rollup: [`operations`](../operations.md)
- Domain rollup: [`platform`](../platform.md)
- Master index: [`entity-catalog.md`](../../relations/entity-catalog.md)
