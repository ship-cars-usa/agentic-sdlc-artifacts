---
reader: integrators-data-bridge
source: autoims-backend
edge-status: sanctioned (ADR-0003)
contract-version: 0.1-draft
last-reviewed: 2026-05-12
owner-reader: unknown
owner-source: unknown
---

# Cross-DB Read Contract — `integrators-data-bridge` ↔ `autoims-backend`

## What's read

`integrators-data-bridge` connects a JDBC datasource directly to `autoims-backend`'s PostgreSQL primary and reads from its inventory/order sync tables. Evidence: `services/.../autoims/AutoImsProcessor.java:99-100`.

| Table | Purpose at reader | Read pattern | Volume |
|---|---|---|---|
| (TBD) Unit-sync table — likely `autoims_unit` or `unit_sync_state` | export per-unit AutoIMS-sync status into integrator payloads | point lookup + bulk by company / sync-status | medium |
| (TBD) Company-config table | resolve per-company integration settings before export | point lookup | low |
| (TBD) Audit / revision tables | conditional — only if delta-export uses revision history | rarely | low |

> **TODO (reader owner):** fill in the exact tables/columns from `AutoImsProcessor.java:99-100` and surrounding query sites.

## Read pattern

- **Mode:** read-only JDBC.
- **Frequency:** integrator-export jobs (per-partner cadence).
- **Freshness tolerance:** minutes-scale staleness acceptable.
- **Volume:** medium — bulk scans by `(company_id, sync_status)`.

## Schema dependencies

The reader relies on:

- Table and column names listed above (TODO: enumerate).
- The `sync_status` enum vocabulary (rename/addition needs reader awareness).
- The semantic meaning of `last_synced_at` timestamp columns (used as cursor for delta export).

## Migration / compatibility plan

Source-service (`autoims-backend`) maintainers MUST:

1. **Notify** `integrators-data-bridge` owner before migrations to listed tables/columns.
2. **Run** the reader's consumer-driven compatibility test (TODO: author).
3. **Stage destructive changes** as add → backfill → switch → drop.

## SLO at the reader

- Acceptable replica lag: **up to 5 minutes** (TODO: confirm).
- Acceptable read latency per export job: **up to 30 s per company batch** (TODO: confirm).

## Migration off the direct-DB edge

- **Pub/Sub replication.** `autoims-backend` already publishes sync events internally; surface a canonical `autoims-state` topic. Effort: small for source.
- **REST batch endpoint.** Add `GET /v1/units/since/{cursor}` on `autoims-backend`. Effort: small.
- **Note:** unlike `posting-backend` and `inventory-backend`, `autoims-backend` is itself an integration shim. Reducing the direct-DB-read here also opens the door to consolidating the integrator-export logic.

## References

- `~/projects/codebase-map/adr/0003-cross-service-db-read-policy.md`.
- `~/projects/codebase-map/repos/integrators-data-bridge.md`.
- `~/projects/codebase-map/repos/autoims-backend.md`.
- `services/.../autoims/AutoImsProcessor.java:99-100` — actual read site.
