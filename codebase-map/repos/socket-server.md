---
repo: socket-server
path: ~/projects/ship-cars-usa/socket-server
stack: Node.js + Express 4.17.1 + Socket.IO 2.0.4
domain: communication
shape: single-module
last-synced-commit: 391baff521fb1f8e0ce8bb7abd00ea7a451a49f7
last-synced-date: 2026-05-11
maintainer: unknown
status: seed
---

# socket-server

## What it is
Node.js / **Socket.IO 2.0.4** real-time WebSocket gateway. Authenticates clients via JWT (Keycloak RS256 public key, fetched and cached every 15 min), joins each connection to three rooms (`global`, `user_<userId>`, `company_<companyId>`), and **relays messages from `pusher` via Redis adapter** (`@socket.io/redis-emitter` 4.1.0) so multiple socket-server instances can broadcast to any room. Prometheus metrics on a separate port. Pure relay — no business logic, no persistence.

## How it fits
- Consumes API of: Keycloak (token-verification public-key endpoint, refreshed every 15 min).
- Publishes events to: none directly — pushes messages **to** connected clients over WebSocket.
- Subscribes to: Redis (`APPLICATION_REDIS_URL`, default `redis://localhost:6379/3`) via the Socket.IO Redis adapter — receives broadcasts from `pusher` and any other socket-emitter.
- Owns data store: **Redis** (Socket.IO adapter + emitter; volatile rooms, no persistence).

## Build / test / run
```
npm install
node index.js  # or whatever the entry point is
# Listens on SERVER_PORT (default 7083); metrics on METRICS_PORT (default 9090)
# Mounted at the path "/socket-server"
```

## Key abstractions
- `socketAuth` middleware — JWT verification + room joins (3 rooms per authenticated user).
- Keycloak public-key fetcher — 15-min cache of the RS256 public key.
- Socket.IO Redis adapter — multi-instance cluster bind.
- Prometheus metrics exporter — connections, messages, etc.
- Winston JSON logger — structured stdout logs.

## Don't-do-here / gotchas
- **Socket.IO 2.0.4 is the legacy major** — v3+ has incompatible wire format. Clients must use the matching client library version. Upgrading to v4 is a coordinated client-and-server effort.
- **Express 4.17.1** is older (4.18+ is current); review for CVE exposure.
- **No graceful shutdown handler** — no SIGTERM listener; connections drop abruptly on pod restart, forcing clients to reconnect. Add a drain hook that disables new connections and waits for in-flight messages.
- **JWT public-key cache 15-min refresh** — if Keycloak rotates keys, new clients can't authenticate for up to 15 min after the rotation. Acceptable for planned rotations; problematic for incident-driven rotation.
- **`origin: "*"`** — CORS is open; security relies entirely on JWT validation. Document the assumption that JWT validation is the only authn/authz layer.
- **Implicit authorization model** — clients can request to join `user_<id>` and `company_<id>` rooms with their own JWT-derived IDs; there's no server-side check that a client isn't joining someone else's room. Verify the JWT subject is matched against the room IDs server-side.
- **Hardcoded room prefixes** (`user_<id>`, `company_<id>`, `global`) — coordinated with `pusher`. Don't rename one without the other.
- **Redis is the cluster-mode hard dependency** — under Redis outage, single-instance fallback works; multi-instance cluster doesn't (messages from one node don't reach clients on another). Confirm Redis SLA matches the service's SLA.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/pusher.md` — primary upstream (fans out via Redis emitter).
- `~/projects/codebase-map/repos/socket-server-old.md` — predecessor (stub; archive candidate).
- `~/projects/codebase-map/domains/communication.md`.
