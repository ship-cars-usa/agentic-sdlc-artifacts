---
topic: posting-state
producers: [posting-backend, quote-manager-backend]
consumers: []
tier: carrier
canonical-dto: ~
canonical-dto-file: ~
schema-source: none
candidate-dto-count: 27
binding: candidates-only
shared-with-producer: ~
last-generated-date: 2026-05-15
status: stub
---

# Topic `posting-state` — schema

**No single canonical DTO.** The topic carries one or more of the candidate DTOs listed below — likely an outbox-style polymorphic stream. L3b will likely need one contract *per DTO type* rather than one per topic.

## Evidence
- No code site bound to this topic by subscription key or DTO-name match — needs manual seeding.
- Topic registry row: [../event-catalog.md](../event-catalog.md)

## Candidate DTOs in producer/consumer repos

These are typed DTO files in the producer/consumer repos that *could* be the payload for this topic. Sorted by name-match score against the topic. If a single one is canonical, flip this file to `schema-source: lombok-data` by hand and re-run.

- [`V1VehiclePubSubDto`](~/projects/ship-cars-usa/posting-backend/posting-dtos/src/main/java/cars/ship/posting/dtos/pubsub/v1/V1VehiclePubSubDto.java) — score 0
- [`V1UserAccountPubSubDto`](~/projects/ship-cars-usa/posting-backend/posting-dtos/src/main/java/cars/ship/posting/dtos/pubsub/v1/V1UserAccountPubSubDto.java) — score 0
- [`V1ShippingItemPubSubDto`](~/projects/ship-cars-usa/posting-backend/posting-dtos/src/main/java/cars/ship/posting/dtos/pubsub/v1/V1ShippingItemPubSubDto.java) — score 0
- [`V1RoutePubSubDto`](~/projects/ship-cars-usa/posting-backend/posting-dtos/src/main/java/cars/ship/posting/dtos/pubsub/v1/V1RoutePubSubDto.java) — score 0
- [`V1PublicLinkInfoPubSubDto`](~/projects/ship-cars-usa/posting-backend/posting-dtos/src/main/java/cars/ship/posting/dtos/pubsub/v1/V1PublicLinkInfoPubSubDto.java) — score 0
- [`V1PaymentPubSubDto`](~/projects/ship-cars-usa/posting-backend/posting-dtos/src/main/java/cars/ship/posting/dtos/pubsub/v1/V1PaymentPubSubDto.java) — score 0
- [`V1LocationWithCoordinatesPubSubDto`](~/projects/ship-cars-usa/posting-backend/posting-dtos/src/main/java/cars/ship/posting/dtos/pubsub/v1/V1LocationWithCoordinatesPubSubDto.java) — score 0
- [`V1LocationPubSubDto`](~/projects/ship-cars-usa/posting-backend/posting-dtos/src/main/java/cars/ship/posting/dtos/pubsub/v1/V1LocationPubSubDto.java) — score 0
- [`V1LoadPubSubDto`](~/projects/ship-cars-usa/posting-backend/posting-dtos/src/main/java/cars/ship/posting/dtos/pubsub/v1/V1LoadPubSubDto.java) — score 0
- [`V1LoadLegSyncPubSubDto`](~/projects/ship-cars-usa/posting-backend/posting-dtos/src/main/java/cars/ship/posting/dtos/pubsub/v1/V1LoadLegSyncPubSubDto.java) — score 0
- [`V1LoadLegStatusPubSubDto`](~/projects/ship-cars-usa/posting-backend/posting-dtos/src/main/java/cars/ship/posting/dtos/pubsub/v1/V1LoadLegStatusPubSubDto.java) — score 0
- [`V1LoadLegPubSubDto`](~/projects/ship-cars-usa/posting-backend/posting-dtos/src/main/java/cars/ship/posting/dtos/pubsub/v1/V1LoadLegPubSubDto.java) — score 0
- [`V1LoadLegMsgPubSubDto`](~/projects/ship-cars-usa/posting-backend/posting-dtos/src/main/java/cars/ship/posting/dtos/pubsub/v1/V1LoadLegMsgPubSubDto.java) — score 0
- [`V1DriverPubSubDto`](~/projects/ship-cars-usa/posting-backend/posting-dtos/src/main/java/cars/ship/posting/dtos/pubsub/v1/V1DriverPubSubDto.java) — score 0
- [`V1DriveawayPubSubDto`](~/projects/ship-cars-usa/posting-backend/posting-dtos/src/main/java/cars/ship/posting/dtos/pubsub/v1/V1DriveawayPubSubDto.java) — score 0
- [`V1DriveawayDriverPubSubDto`](~/projects/ship-cars-usa/posting-backend/posting-dtos/src/main/java/cars/ship/posting/dtos/pubsub/v1/V1DriveawayDriverPubSubDto.java) — score 0
- [`V1DateDetailPubSubDto`](~/projects/ship-cars-usa/posting-backend/posting-dtos/src/main/java/cars/ship/posting/dtos/pubsub/v1/V1DateDetailPubSubDto.java) — score 0
- [`V1ContractPubSubDto`](~/projects/ship-cars-usa/posting-backend/posting-dtos/src/main/java/cars/ship/posting/dtos/pubsub/v1/V1ContractPubSubDto.java) — score 0
- [`V1ContactPubSubDto`](~/projects/ship-cars-usa/posting-backend/posting-dtos/src/main/java/cars/ship/posting/dtos/pubsub/v1/V1ContactPubSubDto.java) — score 0
- [`V1CarrierPubSubDto`](~/projects/ship-cars-usa/posting-backend/posting-dtos/src/main/java/cars/ship/posting/dtos/pubsub/v1/V1CarrierPubSubDto.java) — score 0
- [`V1CarrierOfferPubSubDto`](~/projects/ship-cars-usa/posting-backend/posting-dtos/src/main/java/cars/ship/posting/dtos/pubsub/v1/V1CarrierOfferPubSubDto.java) — score 0
- [`V1AttachmentPubSubDto`](~/projects/ship-cars-usa/posting-backend/posting-dtos/src/main/java/cars/ship/posting/dtos/pubsub/v1/V1AttachmentPubSubDto.java) — score 0
- [`V1AccountingLineItemPubSubDto`](~/projects/ship-cars-usa/posting-backend/posting-dtos/src/main/java/cars/ship/posting/dtos/pubsub/v1/V1AccountingLineItemPubSubDto.java) — score 0
- [`LoadLegStatusPubSubDto`](~/projects/ship-cars-usa/posting-backend/posting-dtos/src/main/java/cars/ship/posting/dtos/pubsub/LoadLegStatusPubSubDto.java) — score 0
- [`LoadLegMsgPubSubDto`](~/projects/ship-cars-usa/posting-backend/posting-dtos/src/main/java/cars/ship/posting/dtos/pubsub/LoadLegMsgPubSubDto.java) — score 0
- [`ContactMsgPubSubDto`](~/projects/ship-cars-usa/posting-backend/posting-dtos/src/main/java/cars/ship/posting/dtos/pubsub/ContactMsgPubSubDto.java) — score 0
- [`MlBotMessagePubSubDto`](~/projects/ship-cars-usa/posting-backend/posting-dtos/src/main/java/cars/ship/posting/dtos/mlbot/MlBotMessagePubSubDto.java) — score 0

## Schema status: `none` (`candidates-only`)
This file ships with `schema-source: none` and `status: stub`. The L3b
contract program will produce the canonical schema; this stub records the
gap and (when present) lists candidate DTOs to seed from.
