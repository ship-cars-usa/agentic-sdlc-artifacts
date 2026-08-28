---
topic: company-subscription
producers: []
consumers: [loadboard-backend, notification-orchestrator, saved-search-handler]
tier: carrier
canonical-dto: ~
canonical-dto-file: ~
schema-source: none
candidate-dto-count: 19
binding: candidates-only
shared-with-producer: ~
last-generated-date: 2026-05-15
status: stub
---

# Topic `company-subscription` — schema

**No single canonical DTO.** The topic carries one or more of the candidate DTOs listed below — likely an outbox-style polymorphic stream. L3b will likely need one contract *per DTO type* rather than one per topic.

## Evidence
- No code site bound to this topic by subscription key or DTO-name match — needs manual seeding.
- Topic registry row: [../event-catalog.md](../event-catalog.md)

## Candidate DTOs in producer/consumer repos

These are typed DTO files in the producer/consumer repos that *could* be the payload for this topic. Sorted by name-match score against the topic. If a single one is canonical, flip this file to `schema-source: lombok-data` by hand and re-run.

- [`CtmsVehiclePubSubDto`](~/projects/ship-cars-usa/loadboard-backend/services/src/main/java/cars/ship/loadboard/dtos/pubsub/CtmsVehiclePubSubDto.java) — score 0
- [`CtmsSpecificationsPubSubDto`](~/projects/ship-cars-usa/loadboard-backend/services/src/main/java/cars/ship/loadboard/dtos/pubsub/CtmsSpecificationsPubSubDto.java) — score 0
- [`CtmsSpecificationPubSubDto`](~/projects/ship-cars-usa/loadboard-backend/services/src/main/java/cars/ship/loadboard/dtos/pubsub/CtmsSpecificationPubSubDto.java) — score 0
- [`CtmsPostingPubSubDto`](~/projects/ship-cars-usa/loadboard-backend/services/src/main/java/cars/ship/loadboard/dtos/pubsub/CtmsPostingPubSubDto.java) — score 0
- [`CtmsPostingDetailsPubSubDto`](~/projects/ship-cars-usa/loadboard-backend/services/src/main/java/cars/ship/loadboard/dtos/pubsub/CtmsPostingDetailsPubSubDto.java) — score 0
- [`CtmsNegotiationPubSubDto`](~/projects/ship-cars-usa/loadboard-backend/services/src/main/java/cars/ship/loadboard/dtos/pubsub/CtmsNegotiationPubSubDto.java) — score 0
- [`CtmsImagePubSubDto`](~/projects/ship-cars-usa/loadboard-backend/services/src/main/java/cars/ship/loadboard/dtos/pubsub/CtmsImagePubSubDto.java) — score 0
- [`CtmsAttachmentPubSubDto`](~/projects/ship-cars-usa/loadboard-backend/services/src/main/java/cars/ship/loadboard/dtos/pubsub/CtmsAttachmentPubSubDto.java) — score 0
- [`CtmsAddressLocationPubSubDto`](~/projects/ship-cars-usa/loadboard-backend/services/src/main/java/cars/ship/loadboard/dtos/pubsub/CtmsAddressLocationPubSubDto.java) — score 0
- [`WorkflowEventPubSubDto`](~/projects/ship-cars-usa/loadboard-backend/api-dtos/src/main/java/cars/ship/loadboard/dtos/out/pubsub/WorkflowEventPubSubDto.java) — score 0
- [`VehicleSpecificationPubSubDto`](~/projects/ship-cars-usa/loadboard-backend/api-dtos/src/main/java/cars/ship/loadboard/dtos/out/pubsub/VehicleSpecificationPubSubDto.java) — score 0
- [`VehiclePubSubDto`](~/projects/ship-cars-usa/loadboard-backend/api-dtos/src/main/java/cars/ship/loadboard/dtos/out/pubsub/VehiclePubSubDto.java) — score 0
- [`PostingPubSubDto`](~/projects/ship-cars-usa/loadboard-backend/api-dtos/src/main/java/cars/ship/loadboard/dtos/out/pubsub/PostingPubSubDto.java) — score 0
- [`PaymentDetailsPubSubDto`](~/projects/ship-cars-usa/loadboard-backend/api-dtos/src/main/java/cars/ship/loadboard/dtos/out/pubsub/PaymentDetailsPubSubDto.java) — score 0
- [`OfferPubSubDto`](~/projects/ship-cars-usa/loadboard-backend/api-dtos/src/main/java/cars/ship/loadboard/dtos/out/pubsub/OfferPubSubDto.java) — score 0
- [`NegotiationPubSubDto`](~/projects/ship-cars-usa/loadboard-backend/api-dtos/src/main/java/cars/ship/loadboard/dtos/out/pubsub/NegotiationPubSubDto.java) — score 0
- [`LocationDetailsPubSubDto`](~/projects/ship-cars-usa/loadboard-backend/api-dtos/src/main/java/cars/ship/loadboard/dtos/out/pubsub/LocationDetailsPubSubDto.java) — score 0
- [`CustomerPubSubDto`](~/projects/ship-cars-usa/loadboard-backend/api-dtos/src/main/java/cars/ship/loadboard/dtos/out/pubsub/CustomerPubSubDto.java) — score 0
- [`AttachmentPubSubDto`](~/projects/ship-cars-usa/loadboard-backend/api-dtos/src/main/java/cars/ship/loadboard/dtos/out/pubsub/AttachmentPubSubDto.java) — score 0

## Schema status: `none` (`candidates-only`)
This file ships with `schema-source: none` and `status: stub`. The L3b
contract program will produce the canonical schema; this stub records the
gap and (when present) lists candidate DTOs to seed from.
