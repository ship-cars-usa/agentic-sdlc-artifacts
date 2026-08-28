---
reader: integrators-data-bridge
source: posting-backend
edge-status: sanctioned (ADR-0003)
contract-version: 0.1-draft
last-reviewed: 2026-05-12
owner-reader: unknown
owner-source: unknown
---

# Cross-DB Read Contract — `integrators-data-bridge` ↔ `posting-backend`

## What's read

`integrators-data-bridge` connects a JDBC datasource directly to `posting-backend`'s PostgreSQL primary and reads from the following tables. Evidence: `services/.../posting/LoadLegProcessor.java:117, 133, 148`.

| Table | Purpose at reader | Read pattern | Volume |
|---|---|---|---|
| (TBD) Load-related primary table — likely `load` / `posting` | resolve load-state for export to integrators | point lookup + bulk export | medium |
| (TBD) Load-leg join table — likely `load_leg` | enumerate legs per load for partner-payload composition | join with parent load | medium |
| (TBD) Vehicle/unit join — likely `vehicle` or `load_vehicle` | enumerate vehicles per load for partner-payload composition | join | medium |

> **TODO (reader owner):** fill in the exact table/column lists from `LoadLegProcessor.java` and any other reader-side query class. This is the proof-of-concept contract doc; the column-level detail is the load-bearing part.

## Read pattern

- **Mode:** read-only JDBC; no writes back into `posting-backend`'s PG.
- **Frequency:** triggered by integrator-export jobs (per-partner cadence); not request-path latency-critical.
- **Freshness tolerance:** reads can be a few minutes stale without business impact.
- **Volume:** medium — bulk scan of a load's full sub-tree per export.

## Schema dependencies the reader relies on

The reader's correct behavior depends on the following being **stable**:

- Table names listed above.
- Column names listed in the per-row lookups in `LoadLegProcessor.java` (TODO: enumerate).
- The presence of the foreign-key relationships between load → load_leg → vehicle (the join shape).
- The semantic meaning of the `status` enums on each table (rename or value-rename will silently misroute exports).

## Migration / compatibility plan

Source-service (`posting-backend`) maintainers MUST:

1. **Notify** `integrators-data-bridge` owner before any migration that touches a table or column on the list above.
2. **Run** the reader's consumer-driven compatibility test (TODO: `integrators-data-bridge/src/test/java/.../ContractCompatibility*` — to be authored) against the proposed migration in CI before merge.
3. **For renames / drops:** stage the change as add-new-column → backfill → switch reader → drop-old-column, not as a single migration.

## SLO at the reader

- Acceptable replica lag at read time: **up to 5 minutes** (TODO: confirm with reader owner).
- Acceptable read latency per export job: **up to 30 s** for a single load-tree fetch (TODO: confirm).

## Migration off the direct-DB edge

If this edge is later retired (per ADR-0003's spirit), the alternatives are:

- **Pub/Sub replication.** `posting-backend` publishes a canonical `load-state` topic; `integrators-data-bridge` consumes and maintains a local materialized projection. Effort: medium (the topic mostly exists for other reasons; reader just needs to consume).
- **REST batch endpoint.** A dedicated `GET /v1/loads/since/{cursor}` on `posting-backend` that returns the same payload. Effort: small for the source service, medium for the reader (re-pagination logic).

## References

- `~/projects/codebase-map/adr/0003-cross-service-db-read-policy.md` — policy.
- `~/projects/codebase-map/repos/integrators-data-bridge.md` — reader shadow.
- `~/projects/codebase-map/repos/posting-backend.md` — source shadow.
- `services/.../posting/LoadLegProcessor.java:117, 133, 148` — actual read sites.
