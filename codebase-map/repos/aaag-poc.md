---
repo: aaag-poc
path: ~/projects/ship-cars-usa/aaag-poc
stack: Python (`google-cloud-pubsub`, `boto3`, `structlog`, stdlib `http.server`)
domain: integrations
shape: single-module (single `main.py` + Docker / k8s helper scripts)
last-synced-commit: 38a411d2ef01d0c6a680f751e721a47c5cee3b8c
last-synced-date: 2026-05-12
maintainer: unknown
status: seed
---

# aaag-poc

## What it is
A **proof-of-concept Python bridge between Ship.Cars Pub/Sub and AAAG's AWS SQS+SNS surface**, predating the productionized `aaag-integration` Quarkus service.

The PoC:
1. Subscribes to `CONFIG_INVENTORY_AAAG_SUBSCRIPTION` (a GCP Pub/Sub subscription).
2. For each inventory message, builds a payload (`{Source: "Ship.Cars", Destination: "Auction A", EventType: "InventoryUnit", Version: "0.1", Data: <json>}`) and POSTs it to AAAG's SNS endpoint (`CONFIG_AAAG_SNS_ENDPOINT` + `CONFIG_AAAG_SNS_ENDPOINT_SECRET` as `x-api-key`).
3. Separately, polls an AWS SQS queue (`CONFIG_AAAG_AWS_COMMAND_QUEUE_URL`) for inbound commands and republishes them to a GCP Pub/Sub topic (`CONFIG_AAAG_COMMAND_TOPIC`).
4. Runs an `http.server` HTTP listener on `CONFIG_SERVER_PORT` (default `:8080`) — likely a liveness probe or webhook receiver (the file truncates before that section is fully visible).

**Status: stale.** Last commit 2023-10-19 (`AMS-000 Fixed`). Two-plus years stale. The productionized successor is `aaag-integration` (Quarkus 3.20.2.4), which is in `seed` status and is the canonical integration for the auction-aggregator flow.

## How it fits

- **Consumes:**
  - GCP Pub/Sub subscription (`CONFIG_INVENTORY_AAAG_SUBSCRIPTION`) — inventory events from Ship.Cars.
  - AWS SQS queue (`CONFIG_AAAG_AWS_COMMAND_QUEUE_URL`) — inbound commands from AAAG.
- **Publishes:**
  - GCP Pub/Sub topic (`CONFIG_AAAG_COMMAND_TOPIC`) — AAAG-originated commands republished to Ship.Cars side.
  - AAAG SNS endpoint (`CONFIG_AAAG_SNS_ENDPOINT`) — outbound inventory events to AAAG.
- **Owns data store:** none (stateless bridge).

## Build / test / run
```
pip install -r requirements.txt
python main.py
```
Docker via `Dockerfile` + `docker-build.sh` + `docker-push.sh`. Several `k8s-*.sh` helper scripts (`k8s-cp-from`, `k8s-cp-to`, `k8s-logs`, `k8s-port-fwd`, `k8s-remote-bash`, `k8s-remote-exec`, `k8s-remove`, `k8s-run`) — operational helpers for working with a deployed pod, characteristic of the PoC era before standardized helm charts.

## Key abstractions

- `main.py` — single-file Python entry. Sets up structlog JSON logging, configures GCP `pubsub_v1.PublisherClient`, configures AWS `boto3.client('sqs', …)`, defines `publish_message`, `process_message`, `pull` loop, and a stdlib HTTP server.
- `igd-utils-lib.sh` — shared bash helper for the k8s scripts.

## Don't-do-here / gotchas

- **Likely an archive-candidate.** The productionized `aaag-integration` Quarkus service supersedes this. Whether `aaag-poc` is still deployed (or kept around for reference) needs a helm check before any retirement decision. Add to the next `infrastructure-triage.md` refresh pass.
- **Mixed cloud SDK surface.** Uses both `google-cloud-pubsub` and `boto3` in one process. Credentials managed via env vars (`AAAG_AWS_ACCESS_KEY_ID`, `AAAG_AWS_SECRET_ACCESS_KEY`, `AAAG_AWS_REGION_NAME`) — verify those flow through proper secret rotation if still deployed.
- **`CMD_SECRET = os.environ.get('CONFIG_AAAG_COMMAND_SECRET', 'secret')`** — default fallback secret `"secret"` is the literal POC-grade default. If this code is still running anywhere, the fallback is active in any environment that doesn't override it.
- **No retry / backoff on outbound SNS POST.** `requests.post(...)` without `timeout=` — a slow AAAG SNS hangs the worker process.
- **No graceful shutdown.** stdlib `BaseHTTPRequestHandler` + `HTTPServer` running in a child `multiprocessing.Process` — pod restarts drop both the HTTP listener and any in-flight Pub/Sub batch.
- **PoC era (2023).** Predates the fleet's standardized Pub/Sub-consumer pattern (`PubSubConsumerBlocking` via `quarkus-pubsub`) and the fleet-wide structured-logging conventions. Don't pattern-match other Python services after this one.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/aaag-integration.md` — the production successor; the v1 seed shadow.
- `~/projects/codebase-map/repos/aaag-integration-logs-ARCHIVED.md` — sibling Python service for log forwarding; also archived.
- `~/projects/codebase-map/relations/infrastructure-triage.md` — should flag this as archive-candidate on next refresh.
- `~/projects/codebase-map/domains/integrations.md`.
