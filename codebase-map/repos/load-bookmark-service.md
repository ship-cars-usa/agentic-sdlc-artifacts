---
repo: load-bookmark-service
path: ~/projects/ship-cars-usa/load-bookmark-service
stack: Python 3.10 / FastAPI
domain: listings-trade
shape: single-module
last-synced-commit: baf47a64c95f58b5b2914e52820e71b49f875099
last-synced-date: 2026-05-11
maintainer: unknown
status: seed
---

# load-bookmark-service

## What it is
Python 3.10 / FastAPI **sidecar** that listens to posting and vehicle events on Google Pub/Sub and **syncs bookmark-relevant state into etcd v3** (distributed K/V) keyed by carrier. Provides a small FastAPI surface for bookmark CRUD against etcd. Lighter-weight than the JVM `load-bookmark-backend` — likely meant for low-latency lookups by other services that prefer etcd over a REST call to PG. Boundary with the JVM counterpart is undocumented (see Don't-do-here).

## How it fits
- Consumes API of: none direct (no HTTP clients). Integrates via Pub/Sub and etcd.
- Publishes events to: holds a reference to topic `cars.ship.qa.notification` but no publish path observed.
- Subscribes to: Google Pub/Sub `projects/atlantean-field-175514/subscriptions/dido` (configurable via `APP_PUBSUB_SUBSCRIPTION`). Routes by `message.attributes['object_type']` → `SynchronizePosting` or `SynchronizeVehicle`.
- Owns data store: **etcd v3** — single host/port + key prefix. No SQL, no Redis. Bookmark JSON is stored as a serialized value per `<prefix>/<carrier>/<load_id>` key.

## Build / test / run
```
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
pytest
```

## Key abstractions
- `Subscriber` — threading wrapper around `google.cloud.pubsub_v1.SubscriberClient`; manages lifecycle (start on FastAPI `startup`, stop on `shutdown`).
- `SynchronizerMixin` — base class for message handlers; parses Pub/Sub JSON payload.
- `SynchronizePosting` — `act()` reads existing etcd value, conflict-resolves on `updated_at` timestamp, writes new value.
- `SynchronizeVehicle` — applies vehicle add/update/delete to the bookmark JSON object.
- `bookmarks` router — REST endpoints for CRUD against etcd.

## Don't-do-here / gotchas
- **Always-ACK pattern** (`message.ack()` in a `finally` block) — even if the etcd write throws, the Pub/Sub message is acknowledged. **Silent data-loss risk if etcd is unavailable**; failures are logged but invisible to Pub/Sub redelivery. Move ACK into the success branch or wire DLQ.
- **`eval(bookmark_info)`** on raw etcd values (`SynchronizePosting.act()` and `SynchronizeVehicle.act()`) — **arbitrary-code execution** if etcd is ever compromised or anyone writes a non-trusted value to a key. Replace with `json.loads()`.
- **Hardcoded 3 s etcd timeout** — too short under any network congestion; tune or make configurable.
- **No transactional read-modify-write** — multiple etcd reads followed by a write; a concurrent handler can overwrite. etcd v3 supports CAS via revision; not used here.
- **Flow control `max_messages=50`** — unbounded memory if processing is slow; the Pub/Sub client buffers up to 50 in-flight, each holding a JSON payload.
- **Python 3.10 + pydantic v1** (inferred from `BaseSettings`) — pydantic v1 is EOL for new features; migration to v2 has breaking syntax changes.
- **Subscription `dido`** is non-obvious — verify the topic actually attached to it (and that the env-var override is consistently set in prod).
- **No metrics / structured logs / health-check endpoint** — operational opacity for a sidecar that holds bookmark state.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/load-bookmark-backend.md` — JVM sibling; boundary question (which is authoritative?).
- `~/projects/codebase-map/domains/listings-trade.md`.
