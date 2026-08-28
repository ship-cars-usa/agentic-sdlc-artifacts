---
topic: notification
producers: [inventory-backend, loadboard-backend, notification-backend, user-backend]
consumers: []
tier: carrier
canonical-dto: cars.ship.notification.dtos.v1.V1NotificationPubSubDto
canonical-dto-file: ~/projects/ship-cars-usa/notification-backend/notification-dtos/src/main/java/cars/ship/notification/dtos/v1/V1NotificationPubSubDto.java
schema-source: lombok-data
shared-with-producer: true
last-generated-date: 2026-05-15
status: stub
---

# Topic `notification` — schema

Canonical DTO: `cars.ship.notification.dtos.v1.V1NotificationPubSubDto`
(consumer-side, from `notification-backend/notification-dtos/src/main/java/cars/ship/notification/dtos/v1/V1NotificationPubSubDto.java`)

**Forward-compatible:** consumer is annotated with `@JsonIgnoreProperties(ignoreUnknown = true)` — unknown JSON fields are silently dropped on deserialization.

## Payload shape (recursive JSON preview)

**Total fields:** 6

Values are JSON type annotations (e.g. `"string"`, `"integer"`, `"string (enum: A|B|C)"`). Nested DTOs are expanded inline; arrays use a single-element list to show the item shape; maps use `{"<key>": <value>}`. Generic placeholders show as `<T>`. Cycle / depth-capped types show as `<TypeName (cycle)>` / `<TypeName (depth-cap)>`.

```json
{
  "type": "string",
  "receiver": [
    "string"
  ],
  "event": "string",
  "data": "any",
  "text": "string",
  "source": "string"
}
```


## Drift check
- **shared-with-producer:** `true` —
  producer and consumer reference the same DTO class (no static drift detected).
- Field-value drift cannot be detected statically.

## Evidence
- Consumer site: `notification-backend/notification-dtos/src/main/java/cars/ship/notification/dtos/v1/V1NotificationPubSubDto.java:L1`
- DTO source: `notification-backend/notification-dtos/src/main/java/cars/ship/notification/dtos/v1/V1NotificationPubSubDto.java`
- Topic registry row: [../event-catalog.md](../event-catalog.md)
