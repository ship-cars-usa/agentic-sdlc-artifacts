---
topic: topics-payment-notification
producers: [payment-backend]
consumers: []
tier: fleet
canonical-dto: cars.ship.payment.dtos.pubsub.PaymentNotificationPubSubDto
canonical-dto-file: ~/projects/ship-cars-usa/payment-backend/api-dtos/src/main/java/cars/ship/payment/dtos/pubsub/PaymentNotificationPubSubDto.java
schema-source: java-record
shared-with-producer: true
last-generated-date: 2026-05-15
status: stub
---

# Topic `topics-payment-notification` — schema

Canonical DTO: `cars.ship.payment.dtos.pubsub.PaymentNotificationPubSubDto`
(consumer-side, from `payment-backend/api-dtos/src/main/java/cars/ship/payment/dtos/pubsub/PaymentNotificationPubSubDto.java`)


## Payload shape (recursive JSON preview)

**Total fields:** 4

Values are JSON type annotations (e.g. `"string"`, `"integer"`, `"string (enum: A|B|C)"`). Nested DTOs are expanded inline; arrays use a single-element list to show the item shape; maps use `{"<key>": <value>}`. Generic placeholders show as `<T>`. Cycle / depth-capped types show as `<TypeName (cycle)>` / `<TypeName (depth-cap)>`.

```json
{
  "action": "string (enum: ONE_TIME_PAYMENT_COMPLETE)",
  "timestamp": "string (iso-8601 datetime)",
  "companyIds": [
    "string"
  ],
  "data": "any"
}
```


## Drift check
- **shared-with-producer:** `true` —
  producer and consumer reference the same DTO class (no static drift detected).
- Field-value drift cannot be detected statically.

## Evidence
- Consumer site: `payment-backend/api-dtos/src/main/java/cars/ship/payment/dtos/pubsub/PaymentNotificationPubSubDto.java:L1`
- DTO source: `payment-backend/api-dtos/src/main/java/cars/ship/payment/dtos/pubsub/PaymentNotificationPubSubDto.java`
- Topic registry row: [../event-catalog.md](../event-catalog.md)
