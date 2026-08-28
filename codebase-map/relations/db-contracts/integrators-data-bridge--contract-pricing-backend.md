---
reader: integrators-data-bridge
source: contract-pricing-backend
edge-status: sanctioned (ADR-0003)
contract-version: 0.1-draft
last-reviewed: 2026-05-12
owner-reader: unknown
owner-source: unknown
---

# Cross-DB Read Contract — `integrators-data-bridge` ↔ `contract-pricing-backend`

## What's read

`integrators-data-bridge` connects a JDBC datasource directly to `contract-pricing-backend`'s PostgreSQL primary and reads contract/pricing data for integrator-export payloads. Evidence: `services/.../ContractPricingProcessor`.

| Table | Purpose at reader | Read pattern | Volume |
|---|---|---|---|
| (TBD) `contract` / equivalent | export per-customer contract terms into integrator payloads | point lookup by company/contract-id | medium |
| (TBD) Region / lane / surcharge tables | export per-customer pricing rules | join with contract | medium |
| (TBD) Flyway V1–V7 migration tables (per shadow:contract-pricing-backend) | not relevant to reader directly; documents schema history | – | – |

> **TODO (reader owner):** enumerate exact tables and columns from `ContractPricingProcessor.java`. The contract-pricing schema has at least 7 Flyway versions; pin to the columns this reader actually depends on.

## Read pattern

- **Mode:** read-only JDBC.
- **Frequency:** integrator-export jobs (per-partner cadence).
- **Freshness tolerance:** minutes-scale staleness acceptable; pricing changes mid-day are rare and not partner-export-critical.
- **Volume:** medium — bulk scans for affected partners.

## Schema dependencies

The reader relies on:

- Table/column names listed above (TODO: enumerate).
- The `is_active` / `effective_date` semantics on contract rows (silently misroutes if effective-date logic changes).
- The relationship between `contract` and region/lane/surcharge join tables.

## Migration / compatibility plan

Source-service (`contract-pricing-backend`) maintainers MUST:

1. **Notify** the reader owner before migrating contract/region/surcharge tables.
2. **Run** the reader's consumer-driven compatibility test (TODO: author).
3. **Stage destructive changes** as add → backfill → switch → drop.
4. **Coordinate with `integrators-data-bridge`** on `effective_date` semantics — a change in how the source service interprets it cascades silently.

## SLO at the reader

- Acceptable replica lag: **up to 5 minutes** (TODO: confirm).
- Acceptable read latency per export job: **up to 30 s per partner batch** (TODO: confirm).

## Migration off the direct-DB edge

- **REST batch endpoint.** `contract-pricing-backend` already exposes a REST surface; add a `GET /v1/contracts/{company_id}/effective-as-of/{date}` to satisfy the reader. Effort: small for source.
- **Pub/Sub state replication.** `contract-pricing-backend` could publish a `contract-state` topic; reader maintains a local projection. Effort: medium.
- **Pricing is the most-critical-correctness surface in the fleet** — a direct-DB-read here is more delicate than `posting-backend` or `inventory-backend`. **Migrate this edge first** if any ADR-0003 contract gets migrated off DB-read.

## References

- `~/projects/codebase-map/adr/0003-cross-service-db-read-policy.md`.
- `~/projects/codebase-map/repos/integrators-data-bridge.md`.
- `~/projects/codebase-map/repos/contract-pricing-backend.md` — note the **do-not-ship-without-rework** verdict from the fleet review; coordinating cross-DB reads on a flagged service requires extra care.
- `services/.../ContractPricingProcessor` — actual read site.
