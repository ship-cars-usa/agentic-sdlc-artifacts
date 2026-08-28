---
repo: hasher
path: ~/projects/ship-cars-usa/hasher
stack: Go 1.18 / Fiber v2 + go-hashids/v2
domain: identity
shape: single-module
last-synced-commit: c9a82f0aee9f3993069729bc76603415e4c89b84
last-synced-date: 2026-05-11
maintainer: unknown
status: seed
---

# hasher

## What it is
Tiny Go / Fiber v2 service that **encodes and decodes integer IDs** using the Hashids algorithm (configurable salt + alphabet + min length). Single-binary, distroless image, port 3000. Used to obfuscate sequential numeric IDs (shipment ID, quote ID, etc.) in public-facing URLs and API responses so they don't leak sequence information. **The cryptographic strength is *only* obfuscation, not security** — anyone with the salt/alphabet can decode. Stateless, horizontally scalable, no DB.

## How it fits
- Consumes API of: none.
- Publishes events to: none.
- Subscribes to: none.
- Owns data store: none.

## Build / test / run
```
go build ./...
go test ./...
./hasher   # listens on :3000
# Required env: APP_HASHIDS_SALT, APP_HASHIDS_ALPHABET, APP_HASHIDS_MIN_LENGTH
```

## Key abstractions
- `main.go:main()` (lines 11-64) — Fiber init; env parsing; route registration.
- `GET /encode/{id}` (line ~37) — int → hashids string.
- `GET /decode/{id}` (line ~52) — hashids string → int.
- `GET /health` — 200 OK.
- Static-files mount on `/public`.

## Don't-do-here / gotchas
- **Not a security control.** Hashids is reversible by anyone with the salt + alphabet. If the salt is hardcoded in Helm values or env-yaml, the encoding adds zero authorization. Treat as URL hygiene only.
- **No authentication / authorization** on `/encode` and `/decode` — any caller in the network can use the service. Add an API-gateway-level mTLS or shared-secret if you need to gate.
- **Single salt/alphabet per instance** — supporting multiple encoding schemes requires separate deployments. Refactor to take params from request if more flexibility is needed.
- **Changing salt or alphabet is a breaking change for any previously-emitted encoded ID** — every URL ever shared becomes undecodable. Treat the config as a hard public contract.
- **`APP_HASHIDS_MIN_LENGTH` non-integer crashes startup** with no graceful degradation. Add a default + log-warn.
- **20 MB body limit** is the only bound — large invalid requests fail opaquely on the limit, not on a clean parse error.
- **No rate limiting** — must be implemented upstream.
- **Distroless image has no shell** — debugging a failed pod requires ephemeral debug containers or `kubectl debug`.

## Relevant ADRs / docs
- `~/projects/codebase-map/domains/identity.md`.
