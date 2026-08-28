---
topic: payment-transactions-subscription
producers: []
consumers: [invoices]
tier: carrier
canonical-dto: cars.ship.payment.dtos.pubsub.PubSubTransactionUpdateDto
canonical-dto-file: ~/projects/ship-cars-usa/payment-backend/api-dtos/src/main/java/cars/ship/payment/dtos/pubsub/PubSubTransactionUpdateDto.java
schema-source: lombok-data
shared-with-producer: true
last-generated-date: 2026-05-15
status: stub
---

# Topic `payment-transactions-subscription` — schema

Canonical DTO: `cars.ship.payment.dtos.pubsub.PubSubTransactionUpdateDto`
(consumer-side, from `payment-backend/api-dtos/src/main/java/cars/ship/payment/dtos/pubsub/PubSubTransactionUpdateDto.java`)

**Base class / envelope:** `PubsubMessageDto<TransactionDto>` (see [event-envelope.md](./event-envelope.md) when applicable)

**Forward-compatible:** consumer is annotated with `@JsonIgnoreProperties(ignoreUnknown = true)` — unknown JSON fields are silently dropped on deserialization.

## Payload shape (recursive JSON preview)

**Total fields:** 19 (19 inherited, 0 declared)

Values are JSON type annotations (e.g. `"string"`, `"integer"`, `"string (enum: A|B|C)"`). Nested DTOs are expanded inline; arrays use a single-element list to show the item shape; maps use `{"<key>": <value>}`. Generic placeholders show as `<T>`. Cycle / depth-capped types show as `<TypeName (cycle)>` / `<TypeName (depth-cap)>`.

```json
{
  "action": "string",
  "actor_pk": "string",
  "actor": "string",
  "object_type": "string",
  "object_pk": "string",
  "url": "string",
  "event_pk": "string",
  "parent_type": "string",
  "parent_pk": "string",
  "created": "boolean",
  "deleted": "boolean",
  "timestamp": "string (iso-8601 datetime)",
  "changed_fields": {
    "<string>": "any"
  },
  "actor_user_management_id": "string",
  "demo_owner_id": "string",
  "broker_load_id": "string",
  "demo": "boolean",
  "drivers": [
    "string"
  ],
  "data": "<T>"
}
```


## Drift check
- **shared-with-producer:** `true` —
  producer and consumer reference the same DTO class (no static drift detected).
- Field-value drift cannot be detected statically.

## Evidence
- Consumer site: `invoices/services/src/main/java/cars/ship/invoices/listeners/PaymentTransactionPubSubListener.java:L24`
- DTO source: `payment-backend/api-dtos/src/main/java/cars/ship/payment/dtos/pubsub/PubSubTransactionUpdateDto.java`
- Topic registry row: [../event-catalog.md](../event-catalog.md)
