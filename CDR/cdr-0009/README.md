# Add DRIVER_REASSIGNED lifecycle event

`CDR-0009` · **proposed** · 2026-08-28 · hristo.savov@ship.cars

**Services:** `posting-backend`, `driveaway-backend`, `autoims-backend`, `integration-executor`, `invoices`

**Legend:** 🟢 added · 🟡 updated · 🔴 removed · 🔵 reused

![Design diagram](./diagram.svg)

## Context

Mid-transit driver reassignment needs a distinct signal — the enum has `DRIVER_ASSIGNED`/`DRIVER_UNASSIGNED` but no reassignment value. Consumers deserialize `action` into `PubSubActionTypeEnum`, so a new value is **not tolerant-reader safe** by default.

**Decision:** add `DRIVER_REASSIGNED` to the shared `posting-dtos` enum, upgrade and deploy consumers first, then emit it.

**Blast radius:** posting-backend producer → shared `posting-dtos` Maven artifact → driveaway-backend, autoims-backend, integration-executor, invoices.

## §3 · Pub/Sub event

*Payload delta · posting-v2-state (LoadLegMsgPubSubDto)*

| Field | Type | Change | JSON name | Subscriber action |
| --- | --- | --- | --- | --- |
| `action` | `PubSubActionTypeEnum` | 🟢 new enum value | `action` | each consumer must handle DRIVER_REASSIGNED (or tolerate unknown enums) |
| `actionData.reassignedDriverId` | `Long (illustrative)` | 🟢 added | `reassignedDriverId` | carried in the existing PubSubActionDataDto |

## Where it lives & how it's wired

| Aspect | Detail |
| --- | --- |
| topic | `posting-v2-state (cars.ship.{env}.posting.v2)` |
| envelope | `LoadLegMsgPubSubDto (Lombok @Data)` |
| dialect | camelCase (Java-origin) |
| discriminator | `PubSubActionTypeEnum (24 values today)` |
| producer | posting-backend · PubSubPublisherSync |
| shared artifact | `ship.cars:posting-dtos (GitHub Packages)` |
| version | dual-DTO: legacy V1 → posting-state, modern → posting-v2-state |
| ordering | enabled |

## Rollout

> ⚠️ **§5 · rollout — the breaking bit**
>
> Adding an enum value is not tolerant-reader safe by default — Jackson throws on an unknown enum unless a consumer sets `READ_UNKNOWN_ENUM_VALUES_AS_NULL`. Order:
>
> 1. publish the bumped `posting-dtos` artifact
> 2. recompile + deploy every consumer (driveaway-backend, autoims-backend, integration-executor, invoices)
> 3. only then have posting-backend emit `DRIVER_REASSIGNED`
>
> Consumers-before-producer.
