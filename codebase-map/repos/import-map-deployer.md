---
repo: import-map-deployer
path: ~/projects/ship-cars-usa/import-map-deployer
stack: Go / Cobra (`cmd.Execute()` pattern) / logrus JSON logging
domain: platform
shape: small Go CLI / service
last-synced-commit: daff6e9146a0357351acc92cdc02e5bd41cdb786
last-synced-date: 2026-05-12
maintainer: unknown
status: stale
---

# import-map-deployer

## What it is
**Ship.Cars Import Map Deployer** — Go service / CLI for managing the **single-spa import maps** that the Loadmate + public-site roots read at runtime. Each time an MFE is deployed (e.g. `posting-frontend`, `inventory-frontend`, `chat-frontend`, `loadboard-frontend`, etc.), this service updates the central import-map with the new URL → bundle mapping so the root config picks up the new version.

The repo carries `cmd/`, `main.go`, `import-map.json` (sample or initial state), `go.mod` — standard small-Go-service layout.

Last commit 2025-10-10 (Claude-config sweep only) — content older but on the active deploy path.

## How it fits

- **Consumed by:** every MFE deploy pipeline. CI for `posting-frontend` / `inventory-frontend` / `chat-frontend` etc. calls this service after publishing a new bundle.
- **Drives:** the import-map that `platform-frontend` (Loadmate root) and `public-root-app-frontend` (public root) read at runtime. A new MFE bundle takes effect when this service updates the map.
- **Owns data store:** the canonical `import-map.json` (likely stored in GCS or a similar object store; the in-repo `import-map.json` is template / fixture).

## Build / test / run
```
go build ./...
./import-map-deployer       # CLI invocation
```

## Don't-do-here / gotchas

- **Single point of failure for fleet-wide MFE deploys.** If this service is down, MFE deploys can't propagate. A backup / restore mechanism for the import map is essential.
- **No README content visible** at this depth — operational details (how it authenticates, where it stores the canonical map, what the rollback procedure is) need to be probed in the source.
- **Coordinates with `platform-frontend` + `public-root-app-frontend`.** Both root configs assume the import-map URL pattern this service exposes.
- **Last real-content commit predates 2026.** Confirm whether the import-map deploy is still done through this service or via a different / newer mechanism (Argo CD / direct GCS push).

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/platform-frontend.md` — Loadmate root config; reads the import map.
- `~/projects/codebase-map/repos/public-root-app-frontend.md` — public root config; reads the import map.
- All MFE repos — each deploys via this service.
- `~/projects/codebase-map/domains/platform.md`.
