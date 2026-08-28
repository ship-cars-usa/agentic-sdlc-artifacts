---
reader: ml-demand-forecasting
sources: unknown (env-driven SOURCE_DB_*; likely posting-backend or a metadata aggregate)
edge-status: sanctioned (ADR-0003)
contract-version: 0.1-draft
last-reviewed: 2026-05-12
owner-reader: unknown
---

# Cross-DB Read Contract — `ml-demand-forecasting` ↔ source production PG

## What's read

`ml-demand-forecasting` is a **batch ML pipeline** (not a service) that reads historical transportation metrics from a single source production PostgreSQL via env-driven credentials (`SOURCE_DB_IP`, `SOURCE_DB_USER`, `SOURCE_DB_PASSWORD`, `SOURCE_DB_NAME`). It computes three quarterly forecasts: rate-per-mile (PPM), loads-per-carrier (LPC), and rejection-rate (RR). Evidence: shadow:ml-demand-forecasting; loader implementations at `code/data/price.py`, `code/data/volume.py`, `code/data/rejection.py`.

> **TODO (reader owner):** confirm **which** source service owns `SOURCE_DB_*`. Likely candidates: `posting-backend` (load-volume history), `metadata` (lane/region metadata), or a dedicated analytics-flavored DB.

| Hypothesis | Source service | Tables (TBD) |
|---|---|---|
| Most likely | `posting-backend` | load history + per-lane payment rates |
| Possible | `metadata` | lane metadata + region surcharge history |
| Possible | a dedicated analytics PG | aggregated metrics |

## Read pattern

- **Mode:** read-only, **batch-bulk**. Loads the entire historical dataset for each metric into pandas DataFrames.
- **Frequency:** scheduled (quarterly cadence, possibly more often).
- **Freshness tolerance:** quarterly resolution — staleness of days is acceptable.
- **Volume:** **high** in burst — entire history per run. Memory-bound on the pipeline pod.

## Schema dependencies

For each metric (PPM, LPC, RR), the reader relies on:

- A time-series of records with timestamp + numeric metric.
- Source-side aggregation (CSV-from-GCS staging is one path; direct PG read is another — verify which `load_data()` implementation is active).
- Lane/region context columns for grouping.

> **Note:** the shadow says GCS-staged CSV is the primary path. The direct-PG read may be a fallback or a separate ingestion. Confirm before adopting this contract.

## Migration / compatibility plan

Source-service maintainers MUST:

1. **Identify themselves** — this is the contract's most-load-bearing TODO. Until ownership is confirmed, the schema migration coordination story can't be written.
2. Once identified: notify the pipeline owner before migrating any column the loaders depend on.
3. **Run** the reader's compatibility test (TODO: author).

## SLO at the reader

- The pipeline is batch — read latency tolerance is **minutes**.
- No per-event SLO; the pipeline reads once per quarter.

## Migration off the direct-DB edge

- **Read from `bi-databricks-backend` / Databricks SQL warehouse instead.** Production-PG reads for analytics is the wrong tier; the right tier is the analytics warehouse the BI services already feed. **Best long-term target.** Effort: medium (re-write the loaders to use Databricks SQL).
- **Pub/Sub event sink.** `posting-backend` already publishes posting events via outbox; consume those into the pipeline's own staging PG, then forecast from local data. Effort: medium-high.
- **Status quo if neither migration is justified.** The pipeline is batch + low-frequency; the impact of a schema migration breaking it is "the next quarterly forecast is delayed" — not a production outage.

## References

- `~/projects/codebase-map/adr/0003-cross-service-db-read-policy.md`.
- `~/projects/codebase-map/repos/ml-demand-forecasting.md` — reader shadow.
- `~/projects/codebase-map/repos/bi-databricks-backend.md` — the proposed migration target.
