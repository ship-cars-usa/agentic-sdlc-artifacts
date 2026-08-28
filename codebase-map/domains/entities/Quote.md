---
entity: Quote
aliases: [Quote, QuoteDto, QuotePubSubDto, QuoteRequestDto, QuoteRequestPubSubDto, QuoteResponse, QuoteResponseDto]
status: auto-generated
domains: [listings-trade, pricing-billing]
occurrence-count: 13
variant-count: 13
owning-service: quote-manager-backend
last-extracted-date: 2026-05-15
---

# Quote

## What it is

TODO: human narrative. 13 variants across 3 repos and 2 domains (listings-trade, pricing-billing). Owning service: [`quote-manager-backend`](../../repos/quote-manager-backend.md).

## Variants

| Repo | Class | Kind | Module | Extends | Field count | Module path |
|---|---|---|---|---|---:|---|
| [loadbuilder-backend](../../repos/loadbuilder-backend.md) | `QuoteDto` | dto | `infra` | — | 1 | `infra/src/main/java/cars/ship/loadbuilder/infra/quotemanager/impl/dtos/QuoteDto.java` |
| [loadbuilder-backend](../../repos/loadbuilder-backend.md) | `QuoteRequestDto` | dto | `infra-interfaces` | — | 12 | `infra-interfaces/src/main/java/cars/ship/loadbuilder/infra/quotemanager/dtos/QuoteRequestDto.java` |
| [quote-manager-backend](../../repos/quote-manager-backend.md) | `Quote` | jpa | `quote-manager-backend` | `BaseEntity` | 10 | `src/main/java/cars/ship/quotemanager/domain/model/Quote.java` |
| [quote-manager-backend](../../repos/quote-manager-backend.md) | `QuoteDto` | dto | `quote-manager-backend` | `SocketMessageActionDto` | 6 | `src/main/java/cars/ship/quotemanager/application/adapters/out/pubsub/dto/QuoteDto.java` |
| [quote-manager-backend](../../repos/quote-manager-backend.md) | `QuoteDto` | dto | `quote-manager-backend` | — | 6 | `src/main/java/cars/ship/quotemanager/application/adapters/in/web/rest/dto/QuoteDto.java` |
| [quote-manager-backend](../../repos/quote-manager-backend.md) | `QuotePubSubDto` | dto | `quote-manager-backend` | — | 5 | `src/main/java/cars/ship/quotemanager/application/adapters/in/pubsub/dto/QuotePubSubDto.java` |
| [quote-manager-backend](../../repos/quote-manager-backend.md) | `QuotePubSubDto` | dto | `quote-manager-backend` | — | 6 | `src/main/java/cars/ship/quotemanager/domain/model/vo/QuotePubSubDto.java` |
| [quote-manager-backend](../../repos/quote-manager-backend.md) | `QuoteRequestDto` | dto | `quote-manager-backend` | `QuoteRequestBaseDto` | 1 | `src/main/java/cars/ship/quotemanager/application/adapters/in/web/rest/dto/QuoteRequestDto.java` |
| [quote-manager-backend](../../repos/quote-manager-backend.md) | `QuoteRequestPubSubDto` | dto | `quote-manager-backend` | `QuoteRequestBaseDto` | 1 | `src/main/java/cars/ship/quotemanager/application/adapters/in/pubsub/dto/QuoteRequestPubSubDto.java` |
| [quote-manager-backend](../../repos/quote-manager-backend.md) | `QuoteRequestPubSubDto` | dto | `quote-manager-backend` | — | 15 | `src/main/java/cars/ship/quotemanager/domain/model/vo/QuoteRequestPubSubDto.java` |
| [quote-manager-backend](../../repos/quote-manager-backend.md) | `QuoteResponse` | dto | `quote-manager-backend` | — | 6 | `src/main/java/cars/ship/quotemanager/domain/model/vo/QuoteResponse.java` |
| [quote-manager-backend](../../repos/quote-manager-backend.md) | `QuoteResponseDto` | dto | `quote-manager-backend` | — | 8 | `src/main/java/cars/ship/quotemanager/application/adapters/in/web/rest/dto/QuoteResponseDto.java` |
| [uship-quotes](../../repos/uship-quotes.md) | `QuoteDto` | dto | `api-dtos` | — | 0 | `api-dtos/src/main/java/cars/ship/uship/dtos/out/quotes/QuoteDto.java` |

## Field union / intersection

**Core fields** (present in ≥60% of variants — 7/13 or more):

_(no fields shared by ≥60% of variants — high heterogeneity)_

**Variant-specific fields** (present in <60% of variants, top 30 by spread):

| Field | Repos that declare it |
|---|---|
| `deliveryCity` | `loadbuilder-backend`, `quote-manager-backend` |
| `deliveryState` | `loadbuilder-backend`, `quote-manager-backend` |
| `deliveryStreet` | `loadbuilder-backend`, `quote-manager-backend` |
| `deliveryZipCode` | `loadbuilder-backend`, `quote-manager-backend` |
| `payload` | `loadbuilder-backend`, `quote-manager-backend` |
| `pickupCity` | `loadbuilder-backend`, `quote-manager-backend` |
| `pickupDate` | `loadbuilder-backend`, `quote-manager-backend` |
| `pickupState` | `loadbuilder-backend`, `quote-manager-backend` |
| `pickupStreet` | `loadbuilder-backend`, `quote-manager-backend` |
| `pickupZipCode` | `loadbuilder-backend`, `quote-manager-backend` |
| `providerId` | `loadbuilder-backend`, `quote-manager-backend` |
| `trailerType` | `loadbuilder-backend`, `quote-manager-backend` |
| `vehicles` | `loadbuilder-backend`, `quote-manager-backend` |
| `authConfig` | `quote-manager-backend` |
| `bookingDetails` | `quote-manager-backend` |
| `brokerExternalId` | `quote-manager-backend` |
| `companyId` | `quote-manager-backend` |
| `customerEmail` | `quote-manager-backend` |
| `customerName` | `quote-manager-backend` |
| `customerPhone` | `quote-manager-backend` |
| `displayOrder` | `quote-manager-backend` |
| `expiresAt` | `quote-manager-backend` |
| `loadId` | `quote-manager-backend` |
| `managedServiceProvider` | `quote-manager-backend` |
| `orderId` | `quote-manager-backend` |
| `orderRefId` | `quote-manager-backend` |
| `processId` | `quote-manager-backend` |
| `provider` | `quote-manager-backend` |
| `providerName` | `quote-manager-backend` |
| `providerProfilePictureUrl` | `quote-manager-backend` |

## Use cases

### REST surface

**quote-manager-backend**:
- `ANY v1/quotes` — `src/main/java/cars/ship/quotemanager/application/adapters/in/web/rest/controller/QuoteController.java`

**uship-quotes**:
- `ANY /{id}` — `resources/src/main/java/cars/ship/uship/quotes/rest/QuotesResource.java`

### Repository operations

_(no Spring Data / Panache repositories typed on this entity found)_

### Carried by Pub/Sub topics

- [`quote-receive-state`](../../relations/event-schemas/quote-receive-state.md) — DTO `QuotePubSubDto`

## Cross-references

- Owning service shadow: [`quote-manager-backend`](../../repos/quote-manager-backend.md)
- Domain rollup: [`listings-trade`](../listings-trade.md)
- Domain rollup: [`pricing-billing`](../pricing-billing.md)
- Master index: [`entity-catalog.md`](../../relations/entity-catalog.md)
