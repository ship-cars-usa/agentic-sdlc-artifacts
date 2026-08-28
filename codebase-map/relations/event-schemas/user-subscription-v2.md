---
topic: user-subscription-v2
producers: []
consumers: [load-recommender, pusher, saved-search-handler]
tier: carrier
canonical-dto: cars.ship.pusher.dtos.in.ctms.MessageObjectDto
canonical-dto-file: ~/projects/ship-cars-usa/pusher/api-dtos/src/main/java/cars/ship/pusher/dtos/in/ctms/MessageObjectDto.java
schema-source: lombok-data
shared-with-producer: false
last-generated-date: 2026-05-15
status: stub
---

# Topic `user-subscription-v2` — schema

Canonical DTO: `cars.ship.pusher.dtos.in.ctms.MessageObjectDto`
(consumer-side, from `pusher/api-dtos/src/main/java/cars/ship/pusher/dtos/in/ctms/MessageObjectDto.java`)

**Base class / envelope:** `MessageDto<Object>` (see [event-envelope.md](./event-envelope.md) when applicable)


## Payload shape (recursive JSON preview)

**Total fields:** 19 (18 inherited, 1 declared)

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
  ],
  "changed_fields": {
    "<string>": "any"
  }
}
```


## Drift check
- **shared-with-producer:** `false` —
  producer and consumer DTOs are in separate packages; L3b authors should compare shapes.
- Field-value drift cannot be detected statically.

## Evidence
- Consumer site: `pusher/event-listener/src/main/java/cars/ship/pusher/listener/infra/CtmsPubSubListener.java:L23`
- DTO source: `pusher/api-dtos/src/main/java/cars/ship/pusher/dtos/in/ctms/MessageObjectDto.java`
- Topic registry row: [../event-catalog.md](../event-catalog.md)
