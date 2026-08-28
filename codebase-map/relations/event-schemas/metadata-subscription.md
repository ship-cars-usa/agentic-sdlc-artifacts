---
topic: metadata-subscription
producers: []
consumers: [pusher]
tier: fleet
canonical-dto: cars.ship.pusher.dtos.in.ctms.MetadataMessageObjectDto
canonical-dto-file: ~/projects/ship-cars-usa/pusher/api-dtos/src/main/java/cars/ship/pusher/dtos/in/ctms/MetadataMessageObjectDto.java
schema-source: partial
shared-with-producer: false
last-generated-date: 2026-05-15
status: stub
---

# Topic `metadata-subscription` — schema

Canonical DTO: `cars.ship.pusher.dtos.in.ctms.MetadataMessageObjectDto`
(consumer-side, from `pusher/api-dtos/src/main/java/cars/ship/pusher/dtos/in/ctms/MetadataMessageObjectDto.java`)

**Base class / envelope:** `PubSubMessageDto<Object>` (see [event-envelope.md](./event-envelope.md) when applicable)


## Payload shape (recursive JSON preview)

**Total fields:** 6 (6 inherited, 0 declared)

Values are JSON type annotations (e.g. `"string"`, `"integer"`, `"string (enum: A|B|C)"`). Nested DTOs are expanded inline; arrays use a single-element list to show the item shape; maps use `{"<key>": <value>}`. Generic placeholders show as `<T>`. Cycle / depth-capped types show as `<TypeName (cycle)>` / `<TypeName (depth-cap)>`.

```json
{
  "objectId": "string",
  "objectType": "string (enum: RESTRICTION)",
  "created": "boolean",
  "deleted": "boolean",
  "timestamp": "string (iso-8601 datetime)",
  "data": "<T>"
}
```


## Drift check
- **shared-with-producer:** `false` —
  producer and consumer DTOs are in separate packages; L3b authors should compare shapes.
- Field-value drift cannot be detected statically.

## Evidence
- Consumer site: `pusher/event-listener/src/main/java/cars/ship/pusher/listener/infra/MetadataPubSubListener.java:L21`
- DTO source: `pusher/api-dtos/src/main/java/cars/ship/pusher/dtos/in/ctms/MetadataMessageObjectDto.java`
- Topic registry row: [../event-catalog.md](../event-catalog.md)
