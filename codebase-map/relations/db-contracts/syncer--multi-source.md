---
reader: syncer
sources: lm-posting, saved-search, platform, lbv3, location-history, metadata, trip-planner
edge-status: sanctioned (ADR-0003)
contract-version: 0.1-draft
last-reviewed: 2026-05-12
owner-reader: unknown
---

# Cross-DB Read Contract — `syncer` ↔ 6 upstream Postgres databases

## What's read

`syncer` opens **6 separate reactive Quarkus datasources** (each `max-size=4`) to read directly from six upstream services' PostgreSQL databases. Reads feed Elasticsearch bulk-index writes. Evidence: `services/...` per-source listener classes (`LmPostingListener`, `CarrierListener`, `LoadboardListener`, etc.) per shadow:syncer.

| Source DB | Owning service | Tables (TBD) | Volume | Resync mode |
|---|---|---|---|---|
| `lm-posting` | (probably `posting-backend`'s "LM" line) | `posting`-related tables | medium-high | full-resync supported |
| `saved-search` | `saved-search-handler` | saved-search definitions + percolate-query metadata | low | full-resync |
| `platform` | (cluster-wide PG used by multiple platform services?) | various | low | – |
| `lbv3` | `loadboard-backend` v3 | loadboard v3 tables | medium | full-resync |
| `location-history` | (TBD — possibly a sub-service of `location-provider`?) | location-history time series | high | partial-resync only |
| `metadata` | `metadata` service | metadata K/V table | low | full-resync |
| `trip-planner` | `trip-planner` | trip + plan tables | medium | full-resync |

> **TODO (reader owner):** enumerate exact tables/columns per source DB. The reader has 8+ Pub/Sub listeners; map each listener to its source-DB read sites (`services/.../*Listener.java`).

## Read pattern

- **Mode:** read-only reactive JDBC (Quarkus reactive PG client); each source pool `max-size=4`.
- **Trigger:** Pub/Sub event arrives → listener reads from the matching source DB → applies delta to Elasticsearch bulk indexer.
- **Resync:** dedicated `ResyncerBase` reads a full table via reactive stream (`fetch-size=2000`) and re-indexes.
- **Freshness tolerance:** **seconds-scale ES eventual consistency** is the design contract.
- **Volume:** medium-to-high during steady-state event processing; spikes during resync.

## Schema dependencies

For each of the 6 source DBs, the reader relies on:

- The Pub/Sub event-DTO's `id` field mapping to the source-DB primary key.
- Specific column names used to build the ES document.
- The semantic shape of join tables (one-to-many vehicle-per-load, etc.).

**Cross-cutting:** `syncer` has **its own ES schema** (per `models/`), which is decoupled from the source-DB schema. Renames in the source don't necessarily break ES queries — but they do break the read step. The reader's compatibility test surface is broad.

## Migration / compatibility plan

Source-service maintainers (across 6 services) MUST:

1. **Notify** `syncer` owner before migrations to any read column.
2. **Run** the reader's consumer-driven compatibility test (TODO: author one test per source DB).
3. **Coordinate** `lbv3` and `trip-planner` migrations especially — both have active feature work in 2026.

## SLO at the reader

- Acceptable replica lag at read: **up to 30 seconds** (the reader is the freshness-critical layer in front of ES).
- Acceptable read latency per event: **up to 1 s** per Pub/Sub message (longer = consumer backlog).

## Migration off the direct-DB edge

- **Self-contained Pub/Sub payloads.** If each upstream service published full enough event payloads, `syncer` could index directly from the message without reading source DB. **Highest-leverage refactor** — but requires payload-schema discipline across 6 services.
- **REST batch endpoint per source.** Each upstream exposes `/internal/v1/{entity}/{id}` returning the full ES-document shape. Low effort per source, but 6× the boilerplate.
- **Reality check:** `syncer` is the fleet's second-largest direct-DB-reader (after `integrators-data-bridge`); migrating it requires per-source decisions and likely 1-2 quarters of work.

## References

- `~/projects/codebase-map/adr/0003-cross-service-db-read-policy.md`.
- `~/projects/codebase-map/repos/syncer.md` — reader shadow.
- `~/projects/codebase-map/repos/posting-backend.md`, `saved-search-handler.md`, `loadboard-backend.md`, `metadata.md`, `trip-planner.md` — source shadows for 5 of the 6 DBs (the `platform` and `location-history` DBs need owner confirmation first).
