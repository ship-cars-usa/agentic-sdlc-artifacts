---
repo: ml-pricing-app
path: ~/projects/ship-cars-usa/ml-pricing-app
stack: Python / Streamlit 0.65.1 (2020) / SQLAlchemy 1.3.19 / pandas 1.1.0
domain: analytics
shape: single-module
last-synced-commit: 47e2950f9719d477a0baff56c6326c7cbb7e1273
last-synced-date: 2026-05-12
maintainer: unknown
status: seed
---

# ml-pricing-app

## What it is
**Streamlit BI dashboard + cron data pipeline** for monitoring the accuracy of `rateengine` / `ml-model-rate` predictions against actual dispatched orders. **Not a backend service** — no REST, no event subscriptions. Two parts:
1. **Daily cron** (`fetch_matchings.py`): matches yesterday's dispatched orders against rate-engine predictions; computes overpriced / underpriced deltas; writes into a `MONITORING` PG.
2. **Streamlit dashboard** (`pricing_app.py`): date-range selector, error breakdowns, Altair charts, CSV exports.

**Re-domained `pricing-billing` → `analytics` on 2026-05-12** — pricing-monitoring is analytics work, not the pricing-stack itself. Sits in the same domain as `bi-databricks-backend` and `user-activity-tracker`. **Major EOL flag**: Streamlit 0.65.1 and SQLAlchemy 1.3.19 are from 2019-2020.

## How it fits
- Consumes API of: none — pulls directly from three databases.
- Publishes events to: none.
- Subscribes to: none.
- Owns data store: writes to **`MONITORING` PostgreSQL** (`matched_orders_to_predictions`, `omitted_ids`, `app_zipdetails`). **Direct-DB-reads**: `MONTWAY` MySQL (dispatched orders) and `RATE_ENGINE` PostgreSQL (predictions). Both are shadow-caller edges that should be added to ADR-0003.

## Build / test / run
```
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run pricing_app.py   # local UI, port 8501
python fetch_matchings.py      # daily cron
python match.py YYYY-MM-DD YYYY-MM-DD  # historical batch
```

## Key abstractions
- `pricing_app.py` — Streamlit entry; `@st.cache` data loading; date-range and filter widgets; Altair chart specs.
- `fetch_matchings.py` — daily cron; pulls yesterday's orders + predictions; writes matches.
- `match.py` — historical batch matcher; CLI date-range args.
- `data_utilities.py` — SQLAlchemy connection helpers (`create_connection_descriptor()`, `fetch_data()`).
- `pricing_report.py` — metric calculations, outlier filtering, region aggregation.

## Don't-do-here / gotchas (lifecycle and correctness flags)
- **Streamlit 0.65.1 is from August 2020** — multiple major versions and security fixes since. `@st.cache` was renamed to `@st.cache_data` / `@st.cache_resource` in modern Streamlit; the current decorator usage is deprecated. **Plan an upgrade** before any non-trivial feature work.
- **SQLAlchemy 1.3.19 is from 2019** — 2.0 migration has API breaks but is the supported line. Coordinate the upgrade with the rest of the Python fleet.
- **MySQL via `mysqldb`** — the synchronous binding is fine for a cron job but old.
- **No error handling in the cron**: `fetch_matchings.py` lacks `try/except` and structured logging. A silent failure on any day means the dashboard shows yesterday's data without warning. Add at minimum a wrap-and-log + alert on non-zero exit.
- **String-interpolated SQL** in `pricing_app.py` for filter parameters — if any filter widget value reaches the SQL via f-string, that's SQL injection. Use parameterized queries everywhere.
- **No model-version stamp** on the match rows — when `ml-model-rate` ships a new model, historical accuracy comparisons mix model versions silently. Add a `model_version` column populated from each prediction.
- **Reads from `MONTWAY` MySQL and `RATE_ENGINE` PG directly** — two more shadow-caller edges (added to the 12 already documented in `data-stores.md`). Add to ADR-0003 candidate-edge list.
- **No auth** on the Streamlit UI in the code; rely on the deploy environment to enforce.
- **`@st.cache` is broken in newer Streamlit** — when the upgrade happens, every cache call site must be updated.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/rateengine.md` — the predictions being monitored.
- `~/projects/codebase-map/repos/ml-model-rate.md` — model-version tracking is the integration point.
- `~/projects/codebase-map/repos/bi-databricks-backend.md` — analytics-domain peer (modern stack); long-term, this dashboard's logic likely moves into Databricks.
- `~/projects/codebase-map/adr/0003-cross-service-db-read-policy.md` — `MONTWAY` MySQL and `RATE_ENGINE` PG reads are new shadow-caller candidates.
- `~/projects/codebase-map/domains/analytics.md`.
