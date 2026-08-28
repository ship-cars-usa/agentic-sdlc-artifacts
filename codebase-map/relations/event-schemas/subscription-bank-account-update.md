---
topic: subscription-bank-account-update
producers: []
consumers: [payment-backend]
tier: fleet
canonical-dto: cars.ship.payment.dtos.pubsub.BankAccountUpdatePubSubDto
canonical-dto-file: ~/projects/ship-cars-usa/payment-backend/api-dtos/src/main/java/cars/ship/payment/dtos/pubsub/BankAccountUpdatePubSubDto.java
schema-source: java-record
shared-with-producer: false
last-generated-date: 2026-05-15
status: stub
---

# Topic `subscription-bank-account-update` — schema

Canonical DTO: `cars.ship.payment.dtos.pubsub.BankAccountUpdatePubSubDto`
(consumer-side, from `payment-backend/api-dtos/src/main/java/cars/ship/payment/dtos/pubsub/BankAccountUpdatePubSubDto.java`)

**Forward-compatible:** consumer is annotated with `@JsonIgnoreProperties(ignoreUnknown = true)` — unknown JSON fields are silently dropped on deserialization.

## Payload shape (recursive JSON preview)

**Total fields:** 3

Values are JSON type annotations (e.g. `"string"`, `"integer"`, `"string (enum: A|B|C)"`). Nested DTOs are expanded inline; arrays use a single-element list to show the item shape; maps use `{"<key>": <value>}`. Generic placeholders show as `<T>`. Cycle / depth-capped types show as `<TypeName (cycle)>` / `<TypeName (depth-cap)>`.

```json
{
  "carrierCompanyId": "string",
  "timestamp": "string (iso-8601 datetime)",
  "initiatedBy": "string"
}
```


## Drift check
- **shared-with-producer:** `false` —
  producer and consumer DTOs are in separate packages; L3b authors should compare shapes.
- Field-value drift cannot be detected statically.

## Evidence
- Consumer site: `payment-backend/services/src/main/java/cars/ship/payment/listeners/BankAccountUpdatePubSubListener.java:L22`
- DTO source: `payment-backend/api-dtos/src/main/java/cars/ship/payment/dtos/pubsub/BankAccountUpdatePubSubDto.java`
- Topic registry row: [../event-catalog.md](../event-catalog.md)
