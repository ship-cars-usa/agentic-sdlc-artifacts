# Add expedited flag to CTMS orders

`CDR-0007` · **example** · 2026-08-28 · hristo.savov@ship.cars · illustrative walkthrough

**Services:** `platform-backend`, `syncer`, `cube`

**Legend:** 🟢 added · 🟡 updated · 🔴 removed · 🔵 reused

![Design diagram](./diagram.svg)

## Context

Dispatchers need to mark an order expedited so it sorts to the top of carrier search and drives an SLA badge.

**Decision:** add a boolean `expedited` to the order model, propagate it additively through the firehose, index it on `loads`, and surface it read-only via cube's order search.

**Blast radius:** platform-backend (PG + event) → carrierlb.events → syncer → ES loads → cube API.

*Illustrative — not a real shipped change.*

## §2a · PostgreSQL

*Column delta · public.loadboard_order*

| Column | Type | Change | Null | Default / backfill |
| --- | --- | --- | --- | --- |
| `expedited` | `boolean` | 🟢 added | no | default false; no data backfill |

## §2b · Elasticsearch

*Mapping delta · loads*

| ES field | Java field : type | ES type | Change | Indexed? |
| --- | --- | --- | --- | --- |
| `expedited` | `expedited : Boolean` | `boolean` | 🟢 added | yes |

## §3 · Pub/Sub event

*Payload delta · event.new_value (order)*

| Field | Type | Change | JSON name | Subscriber action |
| --- | --- | --- | --- | --- |
| `expedited` | `bool` | 🟢 added | `expedited` | syncer reads it; 15 others tolerate |

## §4 · REST API & DTO

*Endpoint · cube · Spring @RestController · springdoc*

| In-code | External | Method | Change | Response DTO |
| --- | --- | --- | --- | --- |
| `/v1/orders/search` | `/api/cube/v1/orders/search` | POST | 🟡 changed | `OrderRowDto` |

*DTO field delta*

| DTO | Field | Type | Change | JSON name |
| --- | --- | --- | --- | --- |
| `OrderRowDto` | `expedited` | `Boolean` | 🟢 added | `expedited` |

## Where it lives & how it's wired

| Aspect | Detail |
| --- | --- |
| service | platform-backend · Django/DRF |
| instance | platform · DB epod |
| host var | `PLATFORM_BACKEND_DB_HOST` |
| model | `loadboard/models.py::Order` |
| ES writer/reader | syncer → cube |
| ES index | loads (no alias) |
| topic | `cars.ship.production.carrierlb.events` |
| compat | additive · tolerant readers |

## Rollout

> ⚠️ **§5 · rollout**
>
> Additive end-to-end, so no coordinated cutover — but the ES step is a drop-and-rebuild: adding `expedited` to `CtmsOrderDocumentDto` changes the reflection mapping, and `CtmsOrdersIndexResyncer` deletes and recreates `loads`, then full-resyncs.
>
> Schedule that window. Deploy producer (platform-backend) before consumers rely on the field.
