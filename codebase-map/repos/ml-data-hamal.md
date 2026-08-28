---
repo: ml-data-hamal
path: ~/projects/ship-cars-usa/ml-data-hamal
stack: Python / SQL-driven source-to-sink data porter (config-driven; Docker-deployable)
domain: analytics
shape: single-module (`code/` + `bin/` + `builder/` + `sink_creation.sql`)
last-synced-commit: 763821754b11d66436b68aec552cc4cf298f2de1
last-synced-date: 2026-05-12
maintainer: unknown
status: stale
---

# ml-data-hamal

## What it is
**`datahamal`** — a Python service that **moves data from source databases to sink databases** on a configurable schedule. Effectively a small ETL pipeline ("Hamal" = "porter" in several languages). Launched 2023-06-06 (per the README).

Built on the fleet's standard Python service template (`code/` + `builder/files/requirements.txt` + `Dockerfile` + `Dockerfile-test`), same shape as the seeded `ml-model-rate` family and `ml-document-parser`.

## How it fits

- **Consumes:** one or more source databases (config-driven; likely production PGs for various services).
- **Writes to:** one or more sink databases (likely the ML/analytics Postgres or BigQuery surface). The repo carries `sink_creation.sql` which defines the **target schema**.
- **Publishes events to:** none directly.
- **Owns data store:** none — pure data porter. Source DBs are owned by other services; sink schema (per `sink_creation.sql`) is owned by this service.

## Build / test / run
```
pip install -r builder/files/requirements.txt
cd code
python main.py
# Or via Docker:
docker build -t ml-data-hamal .
docker run ml-data-hamal
```

## Key abstractions

- `code/` — main Python source.
- `bin/` — utility scripts (likely `run-all.sh` or per-table runners).
- `builder/files/requirements.txt` — Python deps.
- `sink_creation.sql` — target-schema DDL (probably idempotent CREATE TABLE IF NOT EXISTS for every sink table).
- `Dockerfile` + `Dockerfile-test` — runtime + test images.
- `pyproject.toml` — package metadata.

## Don't-do-here / gotchas

- **Source-DB read is presumably direct.** Like `integrators-data-bridge` and `syncer`, this likely adds to the fleet's cross-service direct-DB-read count (see `relations/data-stores.md`). Worth a follow-up to confirm which source DBs are read and whether ADR-0003 contracts apply.
- **`sink_creation.sql` is load-bearing.** Schema changes need to land here AND in any consumer of the sink DB. Drift between the SQL and the actual deployed schema is a real risk.
- **No retry / DLQ semantics visible at this depth.** A failed copy presumably means the next run tries again; verify the failure-recovery behavior before treating this as resilient.
- **Per-table mapping configuration** — the README mentions "Adding source and sink tables" — implies a config-driven mapping format. Adding a table requires updating that config + the sink SQL together.
- **Same Python template as ml-model-*** (`builder/` + `code/` + per-env Dockerfile). Many fleet ML services share this shape; common version-bump conventions apply.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/integrators-data-bridge.md` — sibling fleet data-porter pattern (Java/Camel rather than Python).
- `~/projects/codebase-map/repos/syncer.md` — another fleet direct-DB-reader.
- `~/projects/codebase-map/relations/data-stores.md` — shadow-caller pattern catalog; this service may add to the list.
- `~/projects/codebase-map/adr/0003-cross-service-db-read-policy.md` — applies if source reads bypass service APIs.
- `~/projects/codebase-map/domains/analytics.md`.
