---
topic: integration-subscription
producers: []
consumers: [pusher]
tier: fleet
canonical-dto: cars.ship.integrations.dtos.out.IntegrationEventMessageDto
canonical-dto-file: ~/projects/ship-cars-usa/integrations-backend/integrations-backend-dtos/src/main/java/cars/ship/integrations/dtos/out/IntegrationEventMessageDto.java
schema-source: lombok-data
shared-with-producer: true
last-generated-date: 2026-05-15
status: stub
---

# Topic `integration-subscription` — schema

Canonical DTO: `cars.ship.integrations.dtos.out.IntegrationEventMessageDto`
(consumer-side, from `integrations-backend/integrations-backend-dtos/src/main/java/cars/ship/integrations/dtos/out/IntegrationEventMessageDto.java`)


## Payload shape (recursive JSON preview)

**Total fields:** 4

Values are JSON type annotations (e.g. `"string"`, `"integer"`, `"string (enum: A|B|C)"`). Nested DTOs are expanded inline; arrays use a single-element list to show the item shape; maps use `{"<key>": <value>}`. Generic placeholders show as `<T>`. Cycle / depth-capped types show as `<TypeName (cycle)>` / `<TypeName (depth-cap)>`.

```json
{
  "id": "string",
  "company_id": "string",
  "action": "string (enum: CREATE|UPDATE)",
  "integration_type": "string"
}
```


## Drift check
- **shared-with-producer:** `true` —
  producer and consumer reference the same DTO class (no static drift detected).
- Field-value drift cannot be detected statically.

## Evidence
- Consumer site: `pusher/db-syncer/src/main/java/cars/ship/pusher/syncer/services/IntegrationPubSubListener.java:L23`
- DTO source: `integrations-backend/integrations-backend-dtos/src/main/java/cars/ship/integrations/dtos/out/IntegrationEventMessageDto.java`
- Topic registry row: [../event-catalog.md](../event-catalog.md)
