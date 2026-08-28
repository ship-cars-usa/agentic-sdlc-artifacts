---
reader: pusher
sources: usermanagement-db, ctms-db
edge-status: sanctioned (ADR-0003)
contract-version: 0.1-draft
last-reviewed: 2026-05-12
owner-reader: unknown
---

# Cross-DB Read Contract — `pusher` ↔ `usermanagement-db` + `ctms-db`

## What's read

`pusher` opens **read-only** JDBC connections (HikariCP `max-size=10` each) to two upstream PostgreSQL databases for **synchronous-routing-decision lookups** during notification fan-out. Unlike the bulk-export readers, this reader is **on the request path** of every notification event — staleness or unavailability degrades real-time delivery latency. Evidence: shadow:pusher.

| Source DB | Owning service | What's read | Read pattern | Volume |
|---|---|---|---|---|
| `usermanagement-db` | `user-backend` | user + company records — recipient resolution + channel-preference lookup | point lookup per event | **high** (every notification) |
| `ctms-db` | legacy CTMS Django | load/order context for legacy-flow notifications | point lookup per legacy event | medium |

> **TODO (reader owner):** enumerate the specific columns (e.g., `user.email`, `user.phone`, `user.notification_preferences`, etc.) from `pusher`'s `notification-sender/impl/...` package.

## Read pattern

- **Mode:** read-only JDBC, **on the synchronous notification-event path**.
- **Frequency:** per notification event (the throughput drives the connection-pool sizing).
- **Freshness tolerance:** seconds-scale staleness (user preferences updated <minute-ago should be reflected). This is **tighter than the bulk-export readers** above.
- **Volume:** high during peak notification traffic.

## Schema dependencies

The reader relies on:

- `user-backend`'s user table: `id`, `email`, `phone`, notification-preference column(s), `is_enabled`.
- `user-backend`'s company table: `id`, name, the relevant routing-criteria columns.
- The legacy CTMS schema for load/order lookup tables.

Because this read is on the request path, **the source services should consider `pusher` a P1 consumer**: a schema migration that breaks `pusher` breaks notification delivery.

## Migration / compatibility plan

Source-service maintainers MUST:

1. **Notify** `pusher` owner before migrating user/company tables in `user-backend` or load/order tables in `ctms-db`.
2. **Run** the reader's consumer-driven compatibility test (TODO: author).
3. **Stage destructive changes** as add → backfill → switch → drop, with `pusher` deployed against the additive schema before the source switches.
4. **Treat `usermanagement-db` as `pusher`'s P1 dependency** — coordinated on-call.

## SLO at the reader

- Read latency per lookup: **< 50 ms p99** (notification fan-out is latency-sensitive).
- Acceptable replica lag (if reading from a replica): **< 5 seconds** (preferences applied 5+ s after change is acceptable; longer breaks user trust).

## Migration off the direct-DB edge

- **`user-backend` already publishes `user-state-v2` + `company-state-v2` Pub/Sub topics via outbox** — `pusher` could maintain a **local replicated cache** of the routing-relevant fields and avoid the synchronous read entirely. **This is the cleanest migration target in the fleet** for this edge: `pusher` already consumes Pub/Sub heavily; adding two more subscriptions to maintain a local cache is incremental. Effort: medium for `pusher`, none for `user-backend`.
- **For the CTMS leg**: CTMS is legacy Django; pushing it to publish events is a non-starter. The right answer is to deprecate CTMS entirely (already in motion per `loadboard-backend`'s shadow). Until then, this edge stays.

## References

- `~/projects/codebase-map/adr/0003-cross-service-db-read-policy.md`.
- `~/projects/codebase-map/repos/pusher.md`.
- `~/projects/codebase-map/repos/user-backend.md` — note the `user-state-v2` / `company-state-v2` outbox topics already exist.
- `~/projects/codebase-map/repos/loadboard-backend.md` — CTMS deprecation context.
