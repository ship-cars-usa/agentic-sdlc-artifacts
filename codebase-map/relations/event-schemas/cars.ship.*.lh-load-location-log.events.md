---
topic: cars.ship.*.lh-load-location-log.events
producers: []
consumers: [location-history-backend]
tier: carrier
canonical-dto: ~
canonical-dto-file: ~
schema-source: none
candidate-dto-count: 1
binding: candidates-only
shared-with-producer: ~
last-generated-date: 2026-05-15
status: stub
---

# Topic `cars.ship.*.lh-load-location-log.events` — schema

**No single canonical DTO.** The topic carries one or more of the candidate DTOs listed below — likely an outbox-style polymorphic stream. L3b will likely need one contract *per DTO type* rather than one per topic.

## Evidence
- No code site bound to this topic by subscription key or DTO-name match — needs manual seeding.
- Topic registry row: [../event-catalog.md](../event-catalog.md)

## Candidate DTOs in producer/consumer repos

These are typed DTO files in the producer/consumer repos that *could* be the payload for this topic. Sorted by name-match score against the topic. If a single one is canonical, flip this file to `schema-source: lombok-data` by hand and re-run.

- [`LoadLocationLogMsgPubSubDto`](~/projects/ship-cars-usa/location-history-backend/api-dtos/src/main/java/cars/ship/locationhistory/dtos/pubsub/LoadLocationLogMsgPubSubDto.java) — score 37

## Schema status: `none` (`candidates-only`)
This file ships with `schema-source: none` and `status: stub`. The L3b
contract program will produce the canonical schema; this stub records the
gap and (when present) lists candidate DTOs to seed from.
