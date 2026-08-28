---
topic: usage-record
producers: []
consumers: [user-backend]
tier: carrier
canonical-dto: cars.ship.usermanagement.dtos.v3.in.pubsub.V3UsageRecordDto
canonical-dto-file: ~/projects/ship-cars-usa/user-backend/usermanagement-dtos/src/main/java/cars/ship/usermanagement/dtos/v3/in/pubsub/V3UsageRecordDto.java
schema-source: java-record
shared-with-producer: false
last-generated-date: 2026-05-15
status: stub
---

# Topic `usage-record` — schema

Canonical DTO: `cars.ship.usermanagement.dtos.v3.in.pubsub.V3UsageRecordDto`
(consumer-side, from `user-backend/usermanagement-dtos/src/main/java/cars/ship/usermanagement/dtos/v3/in/pubsub/V3UsageRecordDto.java`)

**Forward-compatible:** consumer is annotated with `@JsonIgnoreProperties(ignoreUnknown = true)` — unknown JSON fields are silently dropped on deserialization.

## Payload shape (recursive JSON preview)

**Total fields:** 4

Values are JSON type annotations (e.g. `"string"`, `"integer"`, `"string (enum: A|B|C)"`). Nested DTOs are expanded inline; arrays use a single-element list to show the item shape; maps use `{"<key>": <value>}`. Generic placeholders show as `<T>`. Cycle / depth-capped types show as `<TypeName (cycle)>` / `<TypeName (depth-cap)>`.

```json
{
  "companyId": "string",
  "action": "string",
  "amount": "integer (long)",
  "createdAt": "string (iso-8601 datetime)"
}
```


## Drift check
- **shared-with-producer:** `false` —
  producer and consumer DTOs are in separate packages; L3b authors should compare shapes.
- Field-value drift cannot be detected statically.

## Evidence
- Consumer site: `user-backend/usermanagement-app/src/main/java/cars/ship/shipperlite/user/application/adapters/in/pubsub/subscription/UsageRecordConsumer.java:L53`
- DTO source: `user-backend/usermanagement-dtos/src/main/java/cars/ship/usermanagement/dtos/v3/in/pubsub/V3UsageRecordDto.java`
- Topic registry row: [../event-catalog.md](../event-catalog.md)
