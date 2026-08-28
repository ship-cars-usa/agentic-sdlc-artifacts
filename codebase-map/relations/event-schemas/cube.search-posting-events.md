---
topic: cube.search-posting-events
producers: [cube]
consumers: [ml-service-listener]
tier: carrier
canonical-dto: cars.ship.cube.dtos.out.SearchPostingEventPubSubDto
canonical-dto-file: ~/projects/ship-cars-usa/cube/loadboard/loadboard-dtos/src/main/java/cars/ship/cube/dtos/out/SearchPostingEventPubSubDto.java
schema-source: java-record
shared-with-producer: true
last-generated-date: 2026-05-15
status: stub
---

# Topic `cube.search-posting-events` — schema

Canonical DTO: `cars.ship.cube.dtos.out.SearchPostingEventPubSubDto`
(consumer-side, from `cube/loadboard/loadboard-dtos/src/main/java/cars/ship/cube/dtos/out/SearchPostingEventPubSubDto.java`)


## Payload shape (recursive JSON preview)

**Total fields:** 6

Values are JSON type annotations (e.g. `"string"`, `"integer"`, `"string (enum: A|B|C)"`). Nested DTOs are expanded inline; arrays use a single-element list to show the item shape; maps use `{"<key>": <value>}`. Generic placeholders show as `<T>`. Cycle / depth-capped types show as `<TypeName (cycle)>` / `<TypeName (depth-cap)>`.

```json
{
  "company_id": "string",
  "company_type": "string (enum: API_INTEGRATOR|SHIPPER|CARRIER)",
  "user_id": "string",
  "search_criteria": {
    "ids": [
      "string"
    ],
    "search": "string",
    "pickup_city": [
      "string"
    ],
    "pickup_range": [
      "string"
    ],
    "delivery_city": [
      "string"
    ],
    "delivery_range": [
      "string"
    ],
    "pickup_state": [
      "string"
    ],
    "delivery_state": [
      "string"
    ],
    "enclosed_trailer": "boolean",
    "operable": "boolean",
    "vehicle_types": [
      "integer"
    ],
    "number_vehicles": "integer",
    "max_number_vehicles": "integer",
    "ship_within": "integer",
    "total_carrier_pay": "number",
    "price_per_mile": "number",
    "payment_terms": [
      "string"
    ],
    "route_origin": "string",
    "route_destination": "string",
    "route_waypoint": [
      "string"
    ],
    "route_offset": "integer",
    "min_distance": "integer",
    "shipper_ids": [
      "string"
    ],
    "negotiation_carrier_ids": [
      "string"
    ],
    "private_only": "boolean",
    "ordering": "string",
    "offset": "integer",
    "negotiation_state": [
      "string"
    ],
    "labels": [
      "string"
    ],
    "builder": "<HashCodeBuilder>"
  },
  "checksum": "integer",
  "polyline": "string"
}
```


## Drift check
- **shared-with-producer:** `true` —
  producer and consumer reference the same DTO class (no static drift detected).
- Field-value drift cannot be detected statically.

## Evidence
- Consumer site: `cube/loadboard/loadboard-dtos/src/main/java/cars/ship/cube/dtos/out/SearchPostingEventPubSubDto.java:L1`
- DTO source: `cube/loadboard/loadboard-dtos/src/main/java/cars/ship/cube/dtos/out/SearchPostingEventPubSubDto.java`
- Topic registry row: [../event-catalog.md](../event-catalog.md)
