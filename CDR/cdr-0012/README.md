# Rename a loadboard column read cross-DB

`CDR-0012` · **proposed** · 2026-08-28 · hristo.savov@ship.cars

**Services:** `loadboard-backend`, `syncer`

![Design diagram](./diagram.svg)

## Context

Rename `expiration_time` → `expires_at` on the `postings` table for clarity. The catch: syncer's *full-resync* reads this database directly (its `lbv3` reactive datasource, via `fetch-v3lb-postings.sql`), so a bare rename breaks the resyncer — steady-state indexing goes through the Pub/Sub payload, but the resync SQL is column-coupled. **Decision:** expand → dual-write → cut the reader → contract, across two repos. **Blast radius:** loadboard-backend PG + syncer's `LoadboardV3IndexResyncer` read + the db-syncer sync-DTO + db-contract.

## §2a · PostgreSQL

*Column delta · postings (loadboard-backend)*

| Column | Type | Change | Null | Default / backfill |
| --- | --- | --- | --- | --- |
| `expiration_time → expires_at` | `timestamptz` | renamed | no | backfill expires_at := expiration_time; dual-write |

## Where it lives & how it's wired

| Aspect | Detail |
| --- | --- |
| service | loadboard-backend (Quarkus 3.27.5) |
| file | `db-migration/…/V1.42__rename_expiration_time.sql` |
| instance | main · DB loadboard-backend |
| entity | `PostingEntity · table postings (BaseEntity)` |
| host var | `DB_URL injected (no DB_HOST)` |
| tool | Flyway (flat V{maj.min}) |
| cross-DB reader | syncer LoadboardV3IndexResyncer · @ReactiveDataSource("lbv3") · fetch-v3lb-postings.sql |
| ES field | unchanged (loadboard-postings doc field stays) |

## Rollout

**§5 · rollout — the coordination landmine ⚠️**

> Not a single-repo change. Steady-state indexing reads the Pub/Sub payload (`LoadboardV3IndexListener`), but the full-resync path reads the column directly from `lbv3`. Order: (1) loadboard-backend adds `expires_at`, backfills, dual-writes, and updates its `db-syncer` sync-DTO; (2) syncer's `fetch-v3lb-postings.sql` / `LoadboardV3IndexResyncer` switches to `expires_at` and deploys; (3) after both are live, a follow-up migration drops `expiration_time`. Update `relations/db-contracts/syncer--multi-source.md` in the same PR.
