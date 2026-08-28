---
topic: platform-subscription
producers: []
consumers: [fraud-detector]
tier: fleet
canonical-dto: cars.ship.frauddetector.dtos.pubsub.PlatformMessageObjectDto
canonical-dto-file: ~/projects/ship-cars-usa/fraud-detector/api-dtos/src/main/java/cars/ship/frauddetector/dtos/pubsub/PlatformMessageObjectDto.java
schema-source: lombok-data
shared-with-producer: false
last-generated-date: 2026-05-15
status: stub
---

# Topic `platform-subscription` — schema

Canonical DTO: `cars.ship.frauddetector.dtos.pubsub.PlatformMessageObjectDto`
(consumer-side, from `fraud-detector/api-dtos/src/main/java/cars/ship/frauddetector/dtos/pubsub/PlatformMessageObjectDto.java`)

**Base class / envelope:** `MessageDto<Object>` (see [event-envelope.md](./event-envelope.md) when applicable)

**Forward-compatible:** consumer is annotated with `@JsonIgnoreProperties(ignoreUnknown = true)` — unknown JSON fields are silently dropped on deserialization.

## Payload shape (recursive JSON preview)

**Total fields:** 18 (18 inherited, 0 declared)

Values are JSON type annotations (e.g. `"string"`, `"integer"`, `"string (enum: A|B|C)"`). Nested DTOs are expanded inline; arrays use a single-element list to show the item shape; maps use `{"<key>": <value>}`. Generic placeholders show as `<T>`. Cycle / depth-capped types show as `<TypeName (cycle)>` / `<TypeName (depth-cap)>`.

```json
{
  "action": "string",
  "actor_pk": "string",
  "actor_user_management_id": "string",
  "object_type": "string",
  "object_pk": "string",
  "object_user_management_id": "string",
  "event_pk": "string",
  "parent_type": "string",
  "parent_pk": "string",
  "is_demo": "boolean",
  "demo_owner_id": "string",
  "shipper_load_id": "string",
  "created": "boolean",
  "deleted": "boolean",
  "timestamp": "string (iso-8601 datetime)",
  "ordering_key": "string",
  "event": {
    "action": "string (enum: CREATE)",
    "entity": "<T>"
  },
  "drivers": [
    "string"
  ]
}
```


## Drift check
- **shared-with-producer:** `false` —
  producer and consumer DTOs are in separate packages; L3b authors should compare shapes.
- Field-value drift cannot be detected statically.

## Evidence
- Consumer site: `fraud-detector/services/src/main/java/cars/ship/frauddetector/services/listeners/PlatformPubSubListener.java:L41`
- DTO source: `fraud-detector/api-dtos/src/main/java/cars/ship/frauddetector/dtos/pubsub/PlatformMessageObjectDto.java`
- Topic registry row: [../event-catalog.md](../event-catalog.md)
