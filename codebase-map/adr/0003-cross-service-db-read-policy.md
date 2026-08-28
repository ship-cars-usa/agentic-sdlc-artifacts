# ADR 0003 — Cross-Service Direct DB Reads

**Status:** Proposed (not yet ratified by service owners)
**Date:** 2026-05-11
**Context author:** codebase-map maintenance

## Context

As of the 44-seed shadow catalog, **at least 11 cross-service direct-PostgreSQL-read edges** are confirmed in `relations/service-graph.md`. Three services routinely connect a Quarkus / Spring datasource to *another service's* primary PostgreSQL cluster and read from it:

| Reader | Reads from |
|---|---|
| `integrators-data-bridge` | `posting-backend`, `inventory-backend`, `autoims-backend`, `contract-pricing-backend` |
| `syncer` | `lm-posting`, `saved-search`, `platform`/`lbv3`, `location-history`, `metadata`, `trip-planner` |
| `pusher` | `ctms-db`, `usermanagement-db` (read replicas) |

Source services have no awareness of these consumers: no API contract, no schema-change hook, no compatibility test. Schema migrations in the source services can silently break the readers, and there is no per-source contract about what columns or semantics the reader depends on.

This is a *de facto* architecture, not a designed one. It works because the source-service owners and the reader-service owners overlap in headcount, but it doesn't scale and it ships with hidden coordination cost.

## Forces

- **Pro direct reads:** simple, fast to ship, leverages PG features the source already provides (joins, full-table scans, transactions). Cheap when the reader's needs change faster than the source-service's API can.
- **Pro abstractions:** schema migrations in the source service can't silently break readers; API ownership is explicit; data shape is a versioned contract.
- **Reality:** the readers are not all the same. `integrators-data-bridge` exists *because* the legacy CTMS / partner integrations require bulk-relational queries that don't fit the source services' REST surfaces. `syncer` exists because Elasticsearch index-population needs joins across the source schema and bulk-export volumes. `pusher` reads `ctms-db` and `usermanagement-db` because routing decisions need synchronous lookup latency under a few milliseconds — calling REST is too slow.
- The fleet already pays the coordination cost; the question is whether to make it explicit.

## Decision (proposed)

Adopt a **two-tier policy**:

1. **Sanctioned shadow reads.** Each currently-existing cross-DB read edge becomes a **named, documented, versioned contract**. Every such read pair maintains:
   - A `db-contracts/<reader>-<source>.md` doc listing tables/columns the reader depends on, the read pattern (full scan / point lookup / streaming export), and the SLO the reader requires.
   - A consumer-driven compatibility test (CI-runnable, owned by the reader) that catches incompatible source migrations *before* they land.
   - A Slack/issue notification when the source schema migration touches a contracted table/column.

2. **No new shadow reads.** Any new cross-service data dependency must be served via REST, Pub/Sub event-stream, or a dedicated read-replica with a documented contract. If a new direct-DB read is genuinely the right answer, propose it via a new ADR documenting why the alternative is insufficient.

## Consequences

- **Pro:** existing edges become legible; source-service owners can plan migrations against a real consumer list; readers gain a defensible position when a migration breaks them.
- **Con:** documentation cost up front (3 readers × 4-6 source DBs = ~16 contract docs). Mitigation: start with the highest-impact edges (`integrators-data-bridge` ↔ `posting-backend` and `inventory-backend` are the most-changed surfaces; do those first).
- **Pro:** new architecture decisions get scrutinized rather than accumulating accidentally.
- **Con:** rejecting a "just read the DB" shortcut in favor of a Pub/Sub-replication layer can slow down a single feature. Acceptable cost.

## Migration path if the decision is reversed (or eased)

If the policy proves too heavy, the lighter alternative is to keep only one element: the consumer-driven compatibility test. The schema-migration notification can be automated from CI (post-merge hook against the source-service repo) without per-edge contract docs.

## Out of scope

- Whether `integrators-data-bridge`, `syncer`, or `pusher` *should* be rewritten to use Pub/Sub replication instead of direct DB reads. That is a per-edge decision better made by the owning team, informed by the latency / volume / freshness needs documented in the contract doc.
- Read-replica vs. primary-DB read: that is an ops decision; this ADR is technology-agnostic.

## References

- `~/projects/codebase-map/relations/service-graph.md` — current edge list (44-seed graph).
- `~/projects/codebase-map/relations/data-stores.md` — pool sizes + ownership.
- `~/projects/codebase-map/repos/integrators-data-bridge.md`, `~/projects/codebase-map/repos/syncer.md`, `~/projects/codebase-map/repos/pusher.md` — the three current cross-DB readers.
