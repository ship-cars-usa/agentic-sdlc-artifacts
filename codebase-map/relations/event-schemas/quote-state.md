---
topic: quote-state
producers: []
consumers: [posting-backend]
tier: carrier
canonical-dto: cars.ship.shipperlite.posting.application.adapters.in.pubsub.dto.QuoteManagerUpdateEventPubSubDto
canonical-dto-file: ~/projects/ship-cars-usa/posting-backend/posting-app/src/main/java/cars/ship/shipperlite/posting/application/adapters/in/pubsub/dto/QuoteManagerUpdateEventPubSubDto.java
schema-source: lombok-data
shared-with-producer: false
last-generated-date: 2026-05-15
status: stub
---

# Topic `quote-state` — schema

Canonical DTO: `cars.ship.shipperlite.posting.application.adapters.in.pubsub.dto.QuoteManagerUpdateEventPubSubDto`
(consumer-side, from `posting-backend/posting-app/src/main/java/cars/ship/shipperlite/posting/application/adapters/in/pubsub/dto/QuoteManagerUpdateEventPubSubDto.java`)

**Forward-compatible:** consumer is annotated with `@JsonIgnoreProperties(ignoreUnknown = true)` — unknown JSON fields are silently dropped on deserialization.

## Payload shape (recursive JSON preview)

**Total fields:** 11

Values are JSON type annotations (e.g. `"string"`, `"integer"`, `"string (enum: A|B|C)"`). Nested DTOs are expanded inline; arrays use a single-element list to show the item shape; maps use `{"<key>": <value>}`. Generic placeholders show as `<T>`. Cycle / depth-capped types show as `<TypeName (cycle)>` / `<TypeName (depth-cap)>`.

```json
{
  "loadId": "string",
  "providerId": "integer (long)",
  "providerName": "string",
  "providerLogoUrl": "string",
  "providerServiceAccountName": "string",
  "orderId": "string",
  "orderRefId": "string",
  "selectedQuoteId": "string",
  "selectedQuoteRateType": "string",
  "mustBeDisabled": "boolean",
  "currentUserEmail": "string"
}
```


## Drift check
- **shared-with-producer:** `false` —
  producer and consumer DTOs are in separate packages; L3b authors should compare shapes.
- Field-value drift cannot be detected statically.

## Evidence
- Consumer site: `posting-backend/posting-app/src/main/java/cars/ship/shipperlite/posting/application/adapters/in/pubsub/QuoteManagerStateConsumer.java:L60`
- DTO source: `posting-backend/posting-app/src/main/java/cars/ship/shipperlite/posting/application/adapters/in/pubsub/dto/QuoteManagerUpdateEventPubSubDto.java`
- Topic registry row: [../event-catalog.md](../event-catalog.md)
