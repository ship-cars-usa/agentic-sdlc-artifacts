---
repo: socket-server-old
path: ~/projects/ship-cars-usa/socket-server-old
stack: Node 16.6.2 + Socket.IO 2.0.4 + socket.io-redis 5.2.0 + socketio-auth 0.1.1 + jsonwebtoken 8.5.1
domain: communication
shape: single-module
last-synced-commit: 35b90ad9a237fb88abd43130aeea90cad892850f
last-synced-date: 2026-05-12
maintainer: unknown
status: seed
---

# socket-server-old

## What it is
The fleet's **legacy WebSocket gateway**, predecessor to `socket-server`. A 39-line single-file Node service (`index.js`) that:

1. Listens for Socket.IO connections on port 8001.
2. Authenticates each socket via `socketio-auth` using an **HS256 JWT signed with a shared secret** (`SECRET_KEY`).
3. After auth, joins the socket to the rooms named in the JWT claims (`auth_data.rooms`) — or, as a fallback, to a single room named after the JWT-claimed `user_id`.
4. Uses the Socket.IO Redis adapter (`socket.io-redis`) so that multiple replicas form a broadcast cluster.

There is no application logic, no persistence, no metrics, no graceful shutdown. It is a thin JWT-verify-and-relay layer.

The repo has **a single commit** (`35b90ad` "Init", 2022-11-29) and has not been touched in 3.5 years. **However, it is still actively deployed** — `helm/ship-cars-usa/socket-server-old/` carries an active chart (production: 2 replicas, NodePort, resources 100m/1.5Gi). It coexists with the modern `socket-server` because the two use **different authentication schemes**:

- `socket-server` — Keycloak RS256 JWTs (public-key verification, key cache 15 min).
- `socket-server-old` — opaque HS256 JWTs with a shared secret.

So the retirement path is gated on migrating the remaining legacy clients to Keycloak-issued JWTs.

## How it fits
- **Connected by:** an unknown population of "legacy" clients still using HS256 JWTs. Not surfaced from inside this repo; the consumer set lives in upstream FE / BE config.
- **Consumes API of:** none.
- **Publishes events to:** none directly — pushes messages **to** connected sockets over WebSocket.
- **Subscribes to:** Redis (`REDIS_URL`, production `redis://main.redis.shipcars-platform-prod.shipcars.dev:6379`, default DB `/3`) via the Socket.IO Redis adapter. **This is a different Redis cluster from `socket-server`** (which uses `socket.redis...`), so the two services are *parallel* listeners, not a single broadcast bus.
- **Owns data store:** Redis (Socket.IO adapter — volatile rooms only, no persistence).

## Build / test / run
```
npm install
node index.js          # listens on :8001 by default
# Required env: SECRET_KEY (HS256 signing secret), REDIS_URL.
```

## Key abstractions
- `index.js` (the entire service):
  - `io.adapter(redis(redis_url))` — Redis pubsub adapter for cluster mode.
  - `socketio-auth` callback — verifies the incoming JWT with `jsonwebtoken.verify(data, secret_key, …)`.
  - `postAuthenticate` — joins rooms named in `socket.auth_data.rooms`, or falls back to `socket.auth_data.user_id`.
  - Auth timeout: `10 * 1000` ms (10s).

## Don't-do-here / gotchas
- **P0 — JWT signing secret committed to git in plaintext, identical across all four environments.** `index.js` carries a hardcoded default (`'k@2e62p%c(a%_lj28*68o-!=x(5yncv4ac0vm8@!=f*vcyoo6$'`) and **`helm/ship-cars-usa/socket-server-old/values-{dev,qa,staging,production}.yaml` all set `secretConfig.SECRET_KEY` to that same literal**. Anyone with read access to the repo can forge a valid JWT and connect, claim any `user_id`, and join any room — including other users' rooms — in any environment. The secret has not been rotated since the 2022-11-29 init commit. Rotation requires a coordinated client + server update.
- **No server-side authorization check on room membership.** The client's JWT claims its own `rooms` array (or `user_id`); the server trusts it. Combined with the secret-rotation gap above, this is "forge any JWT → eavesdrop on any user/company room."
- **Socket.IO 2.0.4 is the legacy wire format** (2017-era). v3+ is incompatible. The lock-in on this wire version is *exactly* the constraint that makes upgrading the client population hard.
- **Node 16.6.2 (Aug 2021) is EOL since Sep 2023.** The Dockerfile pins `node:16.6.2-alpine3.13`. Alpine 3.13 is also unsupported. Image rebuild = forced runtime bump.
- **No graceful shutdown** — no SIGTERM listener, no drain. Pod restarts drop all connections abruptly. Acceptable in a legacy service whose retirement is more valuable than tuning, but worth documenting.
- **No metrics, no structured logging, no health endpoint.** Operability is sub-fleet-baseline. Treat this as an opaque box during incidents; the `socket-server` (Keycloak-JWT path) is the observable one.
- **Single Init commit (2022-11-29).** The repo is effectively frozen. Any change here triggers a "should this just be retired?" conversation.
- **`socketio-auth` 0.1.1** is a pre-1.0 unmaintained library — last npm release was 2017. Replacement is the modern Socket.IO middleware API.

## Status / retirement plan
- **Classification:** *frozen but deployed*. Not an immediate archive-candidate — production helm chart with 2 replicas active.
- **Retirement is gated on:** migrating all remaining HS256-JWT clients to Keycloak-issued RS256 JWTs handled by `socket-server`.
- **Compensating control until retirement:** rotate `SECRET_KEY` immediately (move it out of `values-*.yaml` into a secret manager — `pusher`'s pattern via `externalSecrets` / `gcp-secret-manager` is the fleet template). This requires a coordinated re-issue of all live HS256 JWTs in client config (rare event — usually means re-deploying every legacy client that still embeds a long-lived token), but eliminates the credentials-in-git problem.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/socket-server.md` — the modern Keycloak-JWT replacement.
- `~/projects/codebase-map/repos/pusher.md` — the upstream event router; whether it speaks to `socket-server-old` at all (vs only `socket-server`) needs confirmation. The two services are on different Redis clusters, so `pusher`'s Redis-emitter target determines which one sees its broadcasts.
- `~/projects/codebase-map/domains/communication.md`.
- `~/projects/codebase-map/relations/infrastructure-triage.md` — earlier triage called this "archive candidate"; **reclassify to "frozen but deployed; retirement-blocked-on-client-migration."**
