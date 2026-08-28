---
topic: ml-recommender-subscription
producers: []
consumers: [load-recommender]
tier: carrier
canonical-dto: cars.ship.recommender.dtos.in.RecommendationMessageDto
canonical-dto-file: ~/projects/ship-cars-usa/load-recommender/api-dtos/src/main/java/cars/ship/recommender/dtos/in/RecommendationMessageDto.java
schema-source: lombok-data
shared-with-producer: false
last-generated-date: 2026-05-15
status: stub
---

# Topic `ml-recommender-subscription` — schema

Canonical DTO: `cars.ship.recommender.dtos.in.RecommendationMessageDto`
(consumer-side, from `load-recommender/api-dtos/src/main/java/cars/ship/recommender/dtos/in/RecommendationMessageDto.java`)


## Payload shape (recursive JSON preview)

**Total fields:** 5

Values are JSON type annotations (e.g. `"string"`, `"integer"`, `"string (enum: A|B|C)"`). Nested DTOs are expanded inline; arrays use a single-element list to show the item shape; maps use `{"<key>": <value>}`. Generic placeholders show as `<T>`. Cycle / depth-capped types show as `<TypeName (cycle)>` / `<TypeName (depth-cap)>`.

```json
{
  "reference_id": "string",
  "load_id_hashed": "string",
  "posting_id_hashed": "string",
  "create_time": "string (iso-8601 datetime)",
  "similar_loads": [
    "<RecommendationScore>"
  ]
}
```


## Drift check
- **shared-with-producer:** `false` —
  producer and consumer DTOs are in separate packages; L3b authors should compare shapes.
- Field-value drift cannot be detected statically.

## Evidence
- Consumer site: `load-recommender/services/src/main/java/cars/ship/recommender/services/listeners/LoadRecommendationListener.java:L23`
- DTO source: `load-recommender/api-dtos/src/main/java/cars/ship/recommender/dtos/in/RecommendationMessageDto.java`
- Topic registry row: [../event-catalog.md](../event-catalog.md)
