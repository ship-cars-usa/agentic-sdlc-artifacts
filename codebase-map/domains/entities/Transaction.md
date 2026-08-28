---
entity: Transaction
aliases: [ChargeEntity, Payment, PaymentDto, PaymentReadDto, TransactionDto, TransactionEntity, V1PaymentDto, V1PaymentPubSubDto]
status: auto-generated
domains: [listings-trade, platform, pricing-billing]
occurrence-count: 9
variant-count: 9
owning-service: payment-backend
last-extracted-date: 2026-05-15
---

# Transaction

## What it is

TODO: human narrative. 9 variants across 4 repos and 3 domains (listings-trade, platform, pricing-billing). Owning service: [`payment-backend`](../../repos/payment-backend.md).

## Variants

| Repo | Class | Kind | Module | Extends | Field count | Module path |
|---|---|---|---|---|---:|---|
| [invoices](../../repos/invoices.md) | `ChargeEntity` | jpa | `db-entities` | `BaseDbEntity` | 6 | `db-entities/src/main/java/cars/ship/invoices/entities/ChargeEntity.java` |
| [invoices](../../repos/invoices.md) | `TransactionEntity` | jpa | `db-entities` | `BaseDbEntity` | 13 | `db-entities/src/main/java/cars/ship/invoices/entities/TransactionEntity.java` |
| [models-lib](../../repos/models-lib.md) | `PaymentReadDto` | dto | `read-models` | — | 8 | `read-models/src/main/java/cars/ship/modelslib/readmodels/posting/PaymentReadDto.java` |
| [payment-backend](../../repos/payment-backend.md) | `TransactionDto` | dto | `api-dtos` | — | 0 | `api-dtos/src/main/java/cars/ship/payment/dtos/TransactionDto.java` |
| [payment-backend](../../repos/payment-backend.md) | `TransactionEntity` | jpa | `db-entities` | `BaseDbEntity` | 17 | `db-entities/src/main/java/cars/ship/payment/entities/TransactionEntity.java` |
| [posting-backend](../../repos/posting-backend.md) | `Payment` | jpa | `posting-app` | `BaseEntity` | 9 | `posting-app/src/main/java/cars/ship/shipperlite/posting/domain/model/Payment.java` |
| [posting-backend](../../repos/posting-backend.md) | `PaymentDto` | dto | `posting-dtos` | — | 8 | `posting-dtos/src/main/java/cars/ship/posting/dtos/PaymentDto.java` |
| [posting-backend](../../repos/posting-backend.md) | `V1PaymentDto` | dto | `posting-dtos` | — | 5 | `posting-dtos/src/main/java/cars/ship/posting/dtos/deprecated/v1/V1PaymentDto.java` |
| [posting-backend](../../repos/posting-backend.md) | `V1PaymentPubSubDto` | dto | `posting-dtos` | — | 8 | `posting-dtos/src/main/java/cars/ship/posting/dtos/pubsub/v1/V1PaymentPubSubDto.java` |

## Field union / intersection

**Core fields** (present in ≥60% of variants — 5/9 or more):

_(no fields shared by ≥60% of variants — high heterogeneity)_

**Variant-specific fields** (present in <60% of variants, top 30 by spread):

| Field | Repos that declare it |
|---|---|
| `paymentMethod` | `invoices`, `models-lib`, `payment-backend`, `posting-backend` |
| `carrierPayInCents` | `models-lib`, `posting-backend` |
| `feeInCents` | `invoices`, `payment-backend` |
| `id` | `models-lib`, `posting-backend` |
| `initiatedTime` | `invoices`, `payment-backend` |
| `message` | `invoices`, `payment-backend` |
| `notes` | `models-lib`, `posting-backend` |
| `paymentEta` | `invoices`, `payment-backend` |
| `paymentTermsBeginType` | `models-lib`, `posting-backend` |
| `paymentTermsType` | `models-lib`, `posting-backend` |
| `paymentTransactionType` | `models-lib`, `posting-backend` |
| `paymentType` | `models-lib`, `posting-backend` |
| `scheduledSendTime` | `invoices`, `payment-backend` |
| `settlementTime` | `invoices`, `payment-backend` |
| `status` | `invoices`, `payment-backend` |
| `targetAvailabilityDate` | `invoices`, `payment-backend` |
| `totalAmountInCents` | `invoices`, `payment-backend` |
| `amountInCents` | `invoices` |
| `code` | `invoices` |
| `costInCents` | `invoices` |
| `externalId` | `payment-backend` |
| `fromCompanyId` | `payment-backend` |
| `invoice` | `invoices` |
| `isTotalRate` | `invoices` |
| `lastEventDatetime` | `payment-backend` |
| `loadLeg` | `posting-backend` |
| `name` | `invoices` |
| `parent` | `payment-backend` |
| `payment` | `posting-backend` |
| `paymentId` | `invoices` |

## Use cases

### REST surface

**invoices**:
- `PATCH /internal/v1/transactions` — `services/src/main/java/cars/ship/invoices/clients/PaymentClient.java`
- `ANY /internal/v1/transactions/{transactionId}` — `services/src/main/java/cars/ship/invoices/clients/PaymentClient.java`

**payment-backend**:
- `ANY /enabled` — `resources/src/main/java/cars/ship/payment/rest/v1/PaymentMethodController.java`
- `ANY /{shipperCompanyId}/carriers/{carrierCompanyId}/integration` — `resources/src/main/java/cars/ship/payment/rest/v1/ShipperController.java`
- `ANY /{shipperCompanyId}/config` — `resources/src/main/java/cars/ship/payment/rest/v1/ShipperController.java`
- `ANY /{shipperCompanyId}/payment-etas` — `resources/src/main/java/cars/ship/payment/rest/v1/ShipperController.java`
- `ANY /{transactionId}` — `resources/src/main/java/cars/ship/payment/rest/v1/internal/TransactionInternalController.java`
- `ANY /{parentId}/children` — `resources/src/main/java/cars/ship/payment/rest/v1/internal/TransactionInternalController.java`
- `ANY /{transactionId}/audit` — `resources/src/main/java/cars/ship/payment/rest/v1/internal/TransactionInternalController.java`
- `ANY /process-scheduled` — `resources/src/main/java/cars/ship/payment/rest/v1/internal/TransactionInternalController.java`

### Repository operations

_(no Spring Data / Panache repositories typed on this entity found)_

### Carried by Pub/Sub topics

_(no resolved Pub/Sub schemas reference this entity; check `relations/event-schemas/` for unresolved canonical-dto fields)_

## Cross-references

- Owning service shadow: [`payment-backend`](../../repos/payment-backend.md)
- Domain rollup: [`listings-trade`](../listings-trade.md)
- Domain rollup: [`platform`](../platform.md)
- Domain rollup: [`pricing-billing`](../pricing-billing.md)
- Master index: [`entity-catalog.md`](../../relations/entity-catalog.md)
