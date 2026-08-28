---
topic: loadmate-quote-manager-subscription
producers: []
consumers: [pusher]
tier: fleet
canonical-dto: cars.ship.pusher.dtos.in.loadmate.LoadMateQuoteManagerMessageDto
canonical-dto-file: ~/projects/ship-cars-usa/pusher/api-dtos/src/main/java/cars/ship/pusher/dtos/in/loadmate/LoadMateQuoteManagerMessageDto.java
schema-source: lombok-data
shared-with-producer: false
last-generated-date: 2026-05-15
status: stub
---

# Topic `loadmate-quote-manager-subscription` — schema

Canonical DTO: `cars.ship.pusher.dtos.in.loadmate.LoadMateQuoteManagerMessageDto`
(consumer-side, from `pusher/api-dtos/src/main/java/cars/ship/pusher/dtos/in/loadmate/LoadMateQuoteManagerMessageDto.java`)


## Payload shape (recursive JSON preview)

**Total fields:** 4

Values are JSON type annotations (e.g. `"string"`, `"integer"`, `"string (enum: A|B|C)"`). Nested DTOs are expanded inline; arrays use a single-element list to show the item shape; maps use `{"<key>": <value>}`. Generic placeholders show as `<T>`. Cycle / depth-capped types show as `<TypeName (cycle)>` / `<TypeName (depth-cap)>`.

```json
{
  "action": "string",
  "companyIds": [
    "string"
  ],
  "timestamp": "string (iso-8601 datetime)",
  "quote": {
    "providerId": "string",
    "providerName": "string",
    "providerProfilePictureUrl": "string",
    "processId": "string",
    "quoteDetails": "any"
  }
}
```


## Drift check
- **shared-with-producer:** `false` —
  producer and consumer DTOs are in separate packages; L3b authors should compare shapes.
- Field-value drift cannot be detected statically.

## Evidence
- Consumer site: `pusher/event-listener/src/main/java/cars/ship/pusher/listener/infra/LoadMateQuoteManagerPubSubListener.java:L22`
- DTO source: `pusher/api-dtos/src/main/java/cars/ship/pusher/dtos/in/loadmate/LoadMateQuoteManagerMessageDto.java`
- Topic registry row: [../event-catalog.md](../event-catalog.md)
