---
topic: loadboard-state
producers: []
consumers: [notification-backend, posting-backend]
tier: carrier
canonical-dto: cars.ship.shipperlite.notification.application.adapters.in.pubsub.dtos.token.LoadboardEventPubSubDto
canonical-dto-file: ~/projects/ship-cars-usa/notification-backend/notification-app/src/main/java/cars/ship/shipperlite/notification/application/adapters/in/pubsub/dtos/token/LoadboardEventPubSubDto.java
schema-source: lombok-data
shared-with-producer: false
last-generated-date: 2026-05-15
status: stub
---

# Topic `loadboard-state` — schema

Canonical DTO: `cars.ship.shipperlite.notification.application.adapters.in.pubsub.dtos.token.LoadboardEventPubSubDto`
(consumer-side, from `notification-backend/notification-app/src/main/java/cars/ship/shipperlite/notification/application/adapters/in/pubsub/dtos/token/LoadboardEventPubSubDto.java`)

**Forward-compatible:** consumer is annotated with `@JsonIgnoreProperties(ignoreUnknown = true)` — unknown JSON fields are silently dropped on deserialization.

## Payload shape (recursive JSON preview)

**Total fields:** 5

Values are JSON type annotations (e.g. `"string"`, `"integer"`, `"string (enum: A|B|C)"`). Nested DTOs are expanded inline; arrays use a single-element list to show the item shape; maps use `{"<key>": <value>}`. Generic placeholders show as `<T>`. Cycle / depth-capped types show as `<TypeName (cycle)>` / `<TypeName (depth-cap)>`.

```json
{
  "action": "string",
  "object_type": "string",
  "object_pk": "string",
  "created": "boolean",
  "parent_type": "string"
}
```


## Drift check
- **shared-with-producer:** `false` —
  producer and consumer DTOs are in separate packages; L3b authors should compare shapes.
- Field-value drift cannot be detected statically.

## Evidence
- Consumer site: `notification-backend/notification-app/src/main/java/cars/ship/shipperlite/notification/application/adapters/in/pubsub/TokenStateConsumer.java:L87`
- DTO source: `notification-backend/notification-app/src/main/java/cars/ship/shipperlite/notification/application/adapters/in/pubsub/dtos/token/LoadboardEventPubSubDto.java`
- Topic registry row: [../event-catalog.md](../event-catalog.md)
