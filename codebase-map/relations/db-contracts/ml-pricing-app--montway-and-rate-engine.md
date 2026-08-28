---
reader: ml-pricing-app
sources: MONTWAY (MySQL), RATE_ENGINE (PostgreSQL)
edge-status: sanctioned (ADR-0003)
contract-version: 0.1-draft
last-reviewed: 2026-05-12
owner-reader: unknown
---

# Cross-DB Read Contract — `ml-pricing-app` ↔ `MONTWAY` MySQL + `RATE_ENGINE` PG

## What's read

`ml-pricing-app` is a **Streamlit BI dashboard + daily Python cron** that reads from two upstream databases and writes a local `MONITORING` PG. Both reads are shadow-caller edges under ADR-0003. Evidence: shadow:ml-pricing-app; loaders at `fetch_matchings.py`, `match.py`, `data_utilities.py`.

| Source DB | Owning service | What's read | Read pattern |
|---|---|---|---|
| `MONTWAY` MySQL | (TBD — likely a legacy carrier-side DB owned by the Montway integration team) | dispatched-orders rows for yesterday (and historical ranges via `match.py`) | bulk date-range scan |
| `RATE_ENGINE` PG | `rateengine` | predictions rows for the same time window | bulk date-range scan |

> **TODO (reader owner):** confirm who owns `MONTWAY` MySQL — the env-var-only configuration suggests this is *not* `posting-backend`/`inventory-backend`. **`MONTWAY` may be entirely outside the `~/projects/ship-cars-usa/` perimeter** (a partner DB), in which case the contract is partner-facing, not internal.

## Read pattern

- **Mode:** read-only via SQLAlchemy 1.3.19 / `mysqldb` (sync) and `psycopg2` (sync).
- **Frequency:** daily cron for yesterday's window; ad-hoc `match.py` runs on historical ranges.
- **Freshness tolerance:** daily resolution — staleness of hours is acceptable.
- **Volume:** medium-high — one day's worth of dispatched orders + matching predictions per run.

## Schema dependencies

For `MONTWAY` MySQL, the reader relies on:

- A dispatched-orders table with at minimum: `order_id`, `dispatched_at`, route info (pickup/delivery zip + coords), vehicle info, dispatched-rate.
- (TBD) — the loader is in `fetch_matchings.py`; enumerate exact columns there.

For `RATE_ENGINE` PG, the reader relies on:

- A predictions table keyed on order/quote ID with predicted-rate columns. Per the `rateengine` shadow, this is a Django ORM-managed schema with 54+ migrations.

## Migration / compatibility plan

**`MONTWAY`** maintainers (if they exist within Ship.Cars): notify the pricing-app owner before schema changes. If `MONTWAY` is a partner DB, the contract is informal at best — and the pricing-app should mirror to its own staging table before reading, to insulate from upstream changes.

**`rateengine`** maintainers MUST:

1. Notify the pricing-app owner before migrating prediction-table columns.
2. **Coordinate with ADR-0005's rewrite plan**: the migration off Django 2.1.7 to a Python 3.12 + FastAPI replacement will change the prediction-table schema. `ml-pricing-app` is a downstream consumer; the cutover must account for the dashboard not breaking.

## SLO at the reader

- The pipeline is daily — read latency tolerance is **minutes**.
- Dashboard latency: each Streamlit page-load issues fresh SQL; if the underlying DBs are slow, the dashboard is slow. Not user-facing in the request-path sense, so the tolerance is generous.

## Migration off the direct-DB edges

Both reads should ultimately go through **`bi-databricks-backend` / Databricks SQL warehouse** rather than production OLTP databases. Pattern:

1. Source services publish their state to the analytics warehouse via existing CDC/ETL.
2. `ml-pricing-app` rewrites loaders to read from the warehouse.
3. `MONTWAY` MySQL reads similarly: if a partner DB, the right answer is to import via a controlled CDC into the warehouse, then read from the warehouse.

Effort: medium for the rewrite; depends on warehouse coverage of the upstream tables.

## Special interaction with ADR-0005

The `rateengine` rewrite proposed in ADR-0005 changes the prediction-table schema as a side effect. **`ml-pricing-app` must be in the migration-compatibility test set** for that rewrite, or it will silently break on cutover.

## References

- `~/projects/codebase-map/adr/0003-cross-service-db-read-policy.md`.
- `~/projects/codebase-map/adr/0005-rateengine-eol-rewrite.md` — affects this contract.
- `~/projects/codebase-map/repos/ml-pricing-app.md` — reader shadow.
- `~/projects/codebase-map/repos/rateengine.md` — `RATE_ENGINE` PG source.
- `~/projects/codebase-map/repos/bi-databricks-backend.md` — proposed long-term migration target.
