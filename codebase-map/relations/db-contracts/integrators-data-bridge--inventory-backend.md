---
reader: integrators-data-bridge
source: inventory-backend
edge-status: sanctioned (ADR-0003)
contract-version: 0.1-draft
last-reviewed: 2026-05-12
owner-reader: unknown
owner-source: unknown
---

# Cross-DB Read Contract — `integrators-data-bridge` ↔ `inventory-backend`

## What's read

`integrators-data-bridge` connects a JDBC datasource directly to `inventory-backend`'s PostgreSQL primary and reads from the inventory unit / vehicle tables. Evidence: `services/.../InventoryProcessor` (per the integrators-data-bridge shadow).

| Table | Purpose at reader | Read pattern | Volume |
|---|---|---|---|
| (TBD) `inventory_unit` / equivalent | export per-unit state into integrator payloads | point lookup + bulk by company / status | medium |
| (TBD) `vehicle` / `unit_vehicle` join | enumerate vehicles per unit | join | medium |
| (TBD) audit-revision tables (Envers) | conditional — only if the reader uses revision history for delta export | rarely | low |

> **TODO (reader owner):** fill in exact table/column list from `InventoryProcessor` and any related export class. This stub establishes the policy precedent; the column-level enumeration is the actual load-bearing artifact.

## Read pattern

- **Mode:** read-only JDBC.
- **Frequency:** integrator-export jobs (per-partner cadence).
- **Freshness tolerance:** minutes-scale staleness is acceptable.
- **Volume:** medium — bulk scans by `(company_id, status)` or `(company_id, updated_at > cursor)`.

## Schema dependencies

The reader relies on:

- Table and column names listed above (TODO: enumerate).
- The status-enum vocabulary on the unit table (rename or addition needs reader awareness).
- The Envers `_aud` companion tables **if** the reader uses revision history. The frontmatter `audit: Envers` on the source shadow indicates these exist; confirm whether the reader queries them.

## Migration / compatibility plan

Source-service (`inventory-backend`) maintainers MUST:

1. **Notify** `integrators-data-bridge` owner before migrations that touch read columns.
2. **Run** the reader's consumer-driven compatibility test (TODO: author).
3. **Stage destructive changes** (rename/drop) as add → backfill → switch → drop, not single-migration.

## SLO at the reader

- Acceptable replica lag: **up to 5 minutes** (TODO: confirm).
- Acceptable read latency per export job: **up to 30 s** per company batch (TODO: confirm).

## Migration off the direct-DB edge

- **Pub/Sub replication.** `inventory-backend` currently has **no** canonical inventory-state topic (its shadow flags this as a missing topic). If one is added — as the `inventory-backend` shadow recommends — the bridge can subscribe and maintain its own materialized projection. Effort: medium for source, medium for reader.
- **REST batch endpoint.** `inventory-backend` already exposes `/v1/units`; a `since/{cursor}` variant would suffice. Effort: small for source.
- **Best long-term answer**: pair this migration with the inventory-state-topic recommendation in `inventory-backend.md`. Once published, multiple downstream consumers (including the bridge) drop their direct-DB read in the same release.

## References

- `~/projects/codebase-map/adr/0003-cross-service-db-read-policy.md`.
- `~/projects/codebase-map/repos/integrators-data-bridge.md`.
- `~/projects/codebase-map/repos/inventory-backend.md` — note the recommendation to publish a canonical `inventory-state` topic.
- `services/.../InventoryProcessor` — actual read site.
