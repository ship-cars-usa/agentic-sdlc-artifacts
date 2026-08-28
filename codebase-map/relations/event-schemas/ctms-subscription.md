---
topic: ctms-subscription
producers: []
consumers: [invoices, load-recommender, loadboard-backend, pusher, saved-search-handler]
tier: carrier
canonical-dto: cars.ship.loadboard.dtos.pubsub.CtmsAttachmentPubSubDto
canonical-dto-file: ~/projects/ship-cars-usa/loadboard-backend/services/src/main/java/cars/ship/loadboard/dtos/pubsub/CtmsAttachmentPubSubDto.java
schema-source: lombok-data
shared-with-producer: false
last-generated-date: 2026-05-15
status: stub
---

# Topic `ctms-subscription` — schema

Canonical DTO: `cars.ship.loadboard.dtos.pubsub.CtmsAttachmentPubSubDto`
(consumer-side, from `loadboard-backend/services/src/main/java/cars/ship/loadboard/dtos/pubsub/CtmsAttachmentPubSubDto.java`)


## Payload shape (recursive JSON preview)

**Total fields:** 14

Values are JSON type annotations (e.g. `"string"`, `"integer"`, `"string (enum: A|B|C)"`). Nested DTOs are expanded inline; arrays use a single-element list to show the item shape; maps use `{"<key>": <value>}`. Generic placeholders show as `<T>`. Cycle / depth-capped types show as `<TypeName (cycle)>` / `<TypeName (depth-cap)>`.

```json
{
  "id": "string",
  "file": "string",
  "image": {
    "full_size": "string",
    "thumbnail": "string"
  },
  "creator_company_user_management_id": "string",
  "type": "string",
  "original_file": "string",
  "height": "string",
  "width": "string",
  "active": "boolean",
  "share_with_driver": "boolean",
  "create_time": "string (iso-8601 datetime)",
  "load_id": "string",
  "creator_user_management_id": "string",
  "vehicle_id": "string"
}
```


## Drift check
- **shared-with-producer:** `false` —
  producer and consumer DTOs are in separate packages; L3b authors should compare shapes.
- Field-value drift cannot be detected statically.

## Evidence
- Consumer site: `loadboard-backend/services/src/main/java/cars/ship/loadboard/dtos/pubsub/CtmsAttachmentPubSubDto.java:L1`
- DTO source: `loadboard-backend/services/src/main/java/cars/ship/loadboard/dtos/pubsub/CtmsAttachmentPubSubDto.java`
- Topic registry row: [../event-catalog.md](../event-catalog.md)
