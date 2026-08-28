---
topic: loadmate-posting-subscription
producers: []
consumers: [pusher]
tier: fleet
canonical-dto: cars.ship.pusher.dtos.in.loadmate.LoadMatePostingMessageDto
canonical-dto-file: ~/projects/ship-cars-usa/pusher/api-dtos/src/main/java/cars/ship/pusher/dtos/in/loadmate/LoadMatePostingMessageDto.java
schema-source: lombok-data
shared-with-producer: false
last-generated-date: 2026-05-15
status: stub
---

# Topic `loadmate-posting-subscription` — schema

Canonical DTO: `cars.ship.pusher.dtos.in.loadmate.LoadMatePostingMessageDto`
(consumer-side, from `pusher/api-dtos/src/main/java/cars/ship/pusher/dtos/in/loadmate/LoadMatePostingMessageDto.java`)


## Payload shape (recursive JSON preview)

**Total fields:** 7

Values are JSON type annotations (e.g. `"string"`, `"integer"`, `"string (enum: A|B|C)"`). Nested DTOs are expanded inline; arrays use a single-element list to show the item shape; maps use `{"<key>": <value>}`. Generic placeholders show as `<T>`. Cycle / depth-capped types show as `<TypeName (cycle)>` / `<TypeName (depth-cap)>`.

```json
{
  "action": "string",
  "object_type": "string",
  "object_id": "string",
  "shipper_company_id": "string",
  "version": "integer",
  "timestamp": "string (iso-8601 datetime)",
  "event": {
    "value": "any"
  }
}
```


## Drift check
- **shared-with-producer:** `false` —
  producer and consumer DTOs are in separate packages; L3b authors should compare shapes.
- Field-value drift cannot be detected statically.

## Evidence
- Consumer site: `pusher/event-listener/src/main/java/cars/ship/pusher/listener/infra/LoadMatePostingPubSubListener.java:L22`
- DTO source: `pusher/api-dtos/src/main/java/cars/ship/pusher/dtos/in/loadmate/LoadMatePostingMessageDto.java`
- Topic registry row: [../event-catalog.md](../event-catalog.md)
