---
repo: aaag-integration-logs-ARCHIVED
path: ~/projects/ship-cars-usa/aaag-integration-logs-ARCHIVED
stack: Python (`google-cloud-pubsub` 2.18.4, `requests`, `structlog` 23.1, `ddtrace` 2.1)
domain: integrations
shape: single-module (`src/main.py` + liveness + setup-logging)
last-synced-commit: f0b09e1103ca0d4d119999def71e1560e6fadd84
last-synced-date: 2026-05-12
maintainer: unknown
status: seed
---

# aaag-integration-logs-ARCHIVED

## What it is
**Archive — already named with the `-ARCHIVED` suffix.** A Python Pub/Sub consumer that:

1. Subscribes to `CONFIG_AAAG_LOGS_SUBSCRIPTION` (a GCP Pub/Sub subscription carrying AAAG-side log events).
2. For each message, POSTs the payload to AAAG's logs endpoint (`CONFIG_AAAG_LOGS_ENDPOINT` + `CONFIG_AAAG_LOGS_ENDPOINT_SECRET` as `x-api-key`).
3. ACKs on HTTP 200; logs and leaves un-ACKed on non-200.
4. Reports liveness via a `mark_liveness_check` ticker pattern (`liveness_check.py`).

In short: a one-way Ship.Cars → AAAG log-shipper.

Last commit 2023-12-19 (`LITE-000 Added readme`). Two-plus years stale. Repo name already declares it archived. Helm deployment status is the only question worth confirming before formal removal.

## How it fits

- **Consumes:** GCP Pub/Sub subscription (`CONFIG_AAAG_LOGS_SUBSCRIPTION`).
- **Publishes:** outbound HTTP POST to AAAG's log-ingest endpoint (`CONFIG_AAAG_LOGS_ENDPOINT`).
- **Owns data store:** none.

## Build / test / run
```
pip install -r requirements.txt
DEV_MODE=true python src/main.py
```

## Key abstractions

- `src/main.py` — Pub/Sub pull loop + forward-to-AAAG REST call + liveness ticker.
- `src/liveness_check.py` — `mark_liveness_check` / `execute_monitor_liveness` helpers.
- `src/setup_logging.py` — structlog-based JSON logger config.

## Don't-do-here / gotchas

- **Archived per repo name.** Don't pattern-match new Python services after this one.
- **Confirm whether it's still deployed** before formal repository archival. The flag in the name doesn't necessarily mean the helm chart was withdrawn — check `helm/ship-cars-usa/` for any chart pointing at this image.
- **No `timeout=` on `requests.post(...)`** to AAAG's endpoint — same fleet Python no-timeout anti-pattern.
- **Unconditional Pub/Sub pull loop with `max_messages=10`** but no flow-control / backpressure handling — would matter under high message rate, doesn't matter at archive scale.
- **Plain `try/except` swallows all exceptions in the outer listen loop**. Useful for resilience but masks debugging.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/aaag-integration.md` — the production successor.
- `~/projects/codebase-map/repos/aaag-poc.md` — PoC sibling, also archive-candidate.
- `~/projects/codebase-map/relations/infrastructure-triage.md` — flag for removal on next refresh.
- `~/projects/codebase-map/domains/integrations.md`.
