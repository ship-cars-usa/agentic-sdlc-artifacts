---
topic: posting-job-events
producers: []
consumers: [posting-backend]
tier: carrier
canonical-dto: cars.ship.loadboard.dtos.out.pubsub.WorkflowEventPubSubDto
canonical-dto-file: ~/projects/ship-cars-usa/loadboard-backend/api-dtos/src/main/java/cars/ship/loadboard/dtos/out/pubsub/WorkflowEventPubSubDto.java
schema-source: lombok-data
shared-with-producer: true
last-generated-date: 2026-05-15
status: stub
---

# Topic `posting-job-events` — schema

Canonical DTO: `cars.ship.loadboard.dtos.out.pubsub.WorkflowEventPubSubDto`
(consumer-side, from `loadboard-backend/api-dtos/src/main/java/cars/ship/loadboard/dtos/out/pubsub/WorkflowEventPubSubDto.java`)


## Payload shape (recursive JSON preview)

**Total fields:** 6

Values are JSON type annotations (e.g. `"string"`, `"integer"`, `"string (enum: A|B|C)"`). Nested DTOs are expanded inline; arrays use a single-element list to show the item shape; maps use `{"<key>": <value>}`. Generic placeholders show as `<T>`. Cycle / depth-capped types show as `<TypeName (cycle)>` / `<TypeName (depth-cap)>`.

```json
{
  "workflowId": "string",
  "resourceId": "string",
  "status": "string (enum: COMPLETED|IN_PROGRESS)",
  "errorMessage": "string",
  "objectType": "string (enum: POSTING)",
  "resource": "any"
}
```


## Drift check
- **shared-with-producer:** `true` —
  producer and consumer reference the same DTO class (no static drift detected).
- Field-value drift cannot be detected statically.

## Evidence
- Consumer site: `posting-backend/posting-app/src/main/java/cars/ship/shipperlite/posting/application/adapters/in/pubsub/LoadLegPostingJobConsumer.java:L75`
- DTO source: `loadboard-backend/api-dtos/src/main/java/cars/ship/loadboard/dtos/out/pubsub/WorkflowEventPubSubDto.java`
- Topic registry row: [../event-catalog.md](../event-catalog.md)
