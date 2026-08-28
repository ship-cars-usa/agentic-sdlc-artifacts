---
topic: quote-receive-state
producers: []
consumers: [quote-manager-backend]
tier: fleet
canonical-dto: cars.ship.quotemanager.application.adapters.in.pubsub.dto.QuotePubSubDto
canonical-dto-file: ~/projects/ship-cars-usa/quote-manager-backend/src/main/java/cars/ship/quotemanager/application/adapters/in/pubsub/dto/QuotePubSubDto.java
schema-source: lombok-data
shared-with-producer: false
last-generated-date: 2026-05-15
status: stub
---

# Topic `quote-receive-state` — schema

Canonical DTO: `cars.ship.quotemanager.application.adapters.in.pubsub.dto.QuotePubSubDto`
(consumer-side, from `quote-manager-backend/src/main/java/cars/ship/quotemanager/application/adapters/in/pubsub/dto/QuotePubSubDto.java`)

**Forward-compatible:** consumer is annotated with `@JsonIgnoreProperties(ignoreUnknown = true)` — unknown JSON fields are silently dropped on deserialization.

## Payload shape (recursive JSON preview)

**Total fields:** 5

Values are JSON type annotations (e.g. `"string"`, `"integer"`, `"string (enum: A|B|C)"`). Nested DTOs are expanded inline; arrays use a single-element list to show the item shape; maps use `{"<key>": <value>}`. Generic placeholders show as `<T>`. Cycle / depth-capped types show as `<TypeName (cycle)>` / `<TypeName (depth-cap)>`.

```json
{
  "authConfig": "<ProviderAuthConfig>",
  "requestPayload": {
    "pickupDate": "string (iso-8601 date)",
    "pickupStreet": "string",
    "pickupCity": "string",
    "pickupState": "string",
    "pickupZipCode": "string",
    "deliveryStreet": "string",
    "deliveryCity": "string",
    "deliveryState": "string",
    "deliveryZipCode": "string",
    "trailerType": "string (enum: OPEN|ENCLOSED|TO_BE_DRIVEN)",
    "customerName": "string",
    "customerEmail": "string",
    "customerPhone": "string",
    "brokerExternalId": "string",
    "vehicles": [
      {
        "vin": "string",
        "year": "integer",
        "make": "string",
        "model": "string",
        "bodyType": "string",
        "operableType": "string (enum: OPERABLE)",
        "dually": "boolean",
        "lifted": "boolean"
      }
    ]
  },
  "managedServiceProvider": {
    "id": "integer (long)",
    "name": "string",
    "profilePictureUrl": "string",
    "quoteUrl": "string",
    "orderUrl": "string",
    "sfQuoteUrl": "string",
    "sfOrderUrl": "string",
    "sfCancelOrderUrl": "string",
    "sfProviderId": "string",
    "displayOrder": "integer",
    "defaultAuthConfig": "<ProviderAuthConfig>"
  },
  "receivers": [
    "string"
  ],
  "processId": "integer (long)"
}
```


## Drift check
- **shared-with-producer:** `false` —
  producer and consumer DTOs are in separate packages; L3b authors should compare shapes.
- Field-value drift cannot be detected statically.

## Evidence
- Consumer site: `quote-manager-backend/src/main/java/cars/ship/quotemanager/application/adapters/in/pubsub/QuoteStateConsumer.java:L52`
- DTO source: `quote-manager-backend/src/main/java/cars/ship/quotemanager/application/adapters/in/pubsub/dto/QuotePubSubDto.java`
- Topic registry row: [../event-catalog.md](../event-catalog.md)
