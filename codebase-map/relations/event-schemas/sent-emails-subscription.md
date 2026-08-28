---
topic: sent-emails-subscription
producers: []
consumers: [load-recommender]
tier: carrier
canonical-dto: cars.ship.search.dtos.SentEmailDto
canonical-dto-file: ~/projects/ship-cars-usa/saved-search-handler/api-dtos/src/main/java/cars/ship/search/dtos/SentEmailDto.java
schema-source: lombok-data
shared-with-producer: true
last-generated-date: 2026-05-15
status: stub
---

# Topic `sent-emails-subscription` — schema

Canonical DTO: `cars.ship.search.dtos.SentEmailDto`
(consumer-side, from `saved-search-handler/api-dtos/src/main/java/cars/ship/search/dtos/SentEmailDto.java`)


## Payload shape (recursive JSON preview)

**Total fields:** 3

Values are JSON type annotations (e.g. `"string"`, `"integer"`, `"string (enum: A|B|C)"`). Nested DTOs are expanded inline; arrays use a single-element list to show the item shape; maps use `{"<key>": <value>}`. Generic placeholders show as `<T>`. Cycle / depth-capped types show as `<TypeName (cycle)>` / `<TypeName (depth-cap)>`.

```json
{
  "user_id": "string",
  "posting_id": "string",
  "sent_at": "string (iso-8601 datetime)"
}
```


## Drift check
- **shared-with-producer:** `true` —
  producer and consumer reference the same DTO class (no static drift detected).
- Field-value drift cannot be detected statically.

## Evidence
- Consumer site: `load-recommender/services/src/main/java/cars/ship/recommender/services/listeners/SavedSearchSentEmailsListener.java:L21`
- DTO source: `saved-search-handler/api-dtos/src/main/java/cars/ship/search/dtos/SentEmailDto.java`
- Topic registry row: [../event-catalog.md](../event-catalog.md)
