---
repo: api-documentation-builder
path: ~/projects/ship-cars-usa/api-documentation-builder
stack: Node / `swagger-combine` / `rdme` (Readme.com CLI)
domain: platform
shape: tooling script (combines per-service swagger files into one OpenAPI spec; uploads to Readme.com)
last-synced-commit: 50d2e1340127214ecc96cf5125e8919191a858b7
last-synced-date: 2026-05-12
maintainer: unknown
status: seed
---

# api-documentation-builder

## What it is
A small Node tool that **aggregates per-service Swagger / OpenAPI files into one combined spec** and then publishes them — both to local `output/*.json` (consumed by `internal-api-docs`) and to **Readme.com** (the public-facing docs platform, via the `rdme` CLI).

The `index.js` entry runs `swagger-combine('config/config-main.json')` to merge per-service swagger files into `output/main.json`. After combining, it post-processes the spec to inject `bearerAuth` security across every endpoint (so every documented endpoint shows up as requiring a Bearer token). Per-config combining files (`config-main.json`, presumably other variants) define which service swaggers get merged.

There's commented-out CTMS-fetching logic (downloading `https://dev.ship.cars/api/swagger.json` directly) — a dead-code branch from when CTMS was sourced live; now sources come from `config/`.

Last commit 2025-10-10 (Claude-config sweep only). Content older.

## How it fits

- **Consumes:** per-service swagger files referenced by `config/config-main.json` (and presumably variants). Each Ship.Cars Quarkus service exposes `/q/openapi` (the standard Quarkus endpoint), Spring services expose `/v3/api-docs` — the config tells `swagger-combine` which URLs to merge.
- **Produces:** `output/main.json` (combined spec; consumed by `internal-api-docs`) + Readme.com publishing via `rdme`.
- **Companion services:** `internal-api-docs` (the Swagger UI renderer) + `internal-api-docs-controller` (the K8s-aware path-config controller).

## Build / test / run
```
npm install
node index.js
```

## Don't-do-here / gotchas

- **Readme.com cost.** `rdme` publishes to Readme.com, which is a paid product. Confirm the org's Readme.com plan supports the publish frequency / API call volume.
- **Bearer-auth injection** is applied to every endpoint post-merge. If a service legitimately has unauthenticated endpoints (e.g. health-checks, public-facing), the generated docs will misrepresent them as requiring Bearer auth.
- **Per-service swagger source URLs** in `config/config-main.json` need to be kept in sync as services are added / renamed. A broken URL produces a silent partial-merge.
- **No CI integration visible at this depth** — confirm whether this runs on schedule or on-demand.
- **Commented-out CTMS-fetch logic** suggests historical iterations on the data-source approach.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/internal-api-docs.md` — Swagger UI server that consumes `output/main.json`.
- `~/projects/codebase-map/repos/internal-api-docs-controller.md` — K8s-aware path-config controller.
- `~/projects/codebase-map/repos/documentation.md` — separate public docs site (static; non-Swagger).
- `~/projects/codebase-map/domains/platform.md`.
