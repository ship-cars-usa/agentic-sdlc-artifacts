---
repo: carrier-packages-frontend
path: ~/projects/ship-cars-usa/carrier-packages-frontend
stack: Nx 22.4 monorepo / npm workspaces / TypeScript 5.8 / Vite 6.3 (per-package) + vite-plugin-dts / Vitest 3.1 / Verdaccio local registry + yalc
domain: platform
shape: multi-module
last-synced-commit: b6e6a4538eacee868e2786843dddf221d19347c0
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# carrier-packages-frontend

## What it is
**The Nx monorepo housing the four canonical carrier-packages shared FE libraries** (`package.json` `name == "carrier-packages-frontend"`, `private: true`, `workspaces: ["packages/*"]`). Node `>=22.14.0`.

Packages under `packages/` (name → current version at this commit):

| Package | Version | Role |
|---|---|---|
| `@ship-cars-usa/globals-frontend-package` | 6.24.0 | shared types, constants, utilities (base of the graph) |
| `@ship-cars-usa/entities-frontend-package` | 20.2.0 | entity models, schemas, actions, sockets, the backend `/api/...` endpoint paths |
| `@ship-cars-usa/ui-components-frontend-package` | 2.1.6 | shared UI primitives (theme, icons, fonts) |
| `@ship-cars-usa/ctmslb-components-frontend-package` | 5.2.7 | CTMS / Loadboard components |

This monorepo is the **canonical development home** for these four packages. The identically-named **standalone sibling repos still exist** (`~/projects/ship-cars-usa/{globals,entities,ui-components,ctmslb}-frontend-package`) but are now **far behind** (standalone globals 5.22.0 vs 6.24.0, entities 16.36.0 vs 20.2.0, ui-components 1.2.0 vs 2.1.6) — effectively legacy. New consumers should depend on the npm-published versions from this monorepo.

**Two shared-library generations now coexist across the fleet:** this carrier-packages cohort (consumed by the single-spa-5 MFEs — `ctms-frontend`, `loadboard-frontend`, `platform-frontend`) and the newer **LoadMate `lm-*` cohort** (`@ship-cars-usa/lm-components` / `lm-types` / `lm-utilities` / `lm-data-layer` / `lm-global-config` / `lm-import-map-overrides`) that the modernized single-spa-6 MFEs (`posting-frontend`, `inventory-frontend`, `user-frontend`, `contract-pricing-frontend`, `executive-dashboard-frontend`, `chase-driver-tracking-frontend`, `public-tracking-frontend`, `driveaway-public-tracking-frontend`) have migrated to. The `lm-*` packages' home repo is not in this workspace.

## How it fits

- **Houses:** the 4 published packages above (build/test via Nx).
- **Compile-time consumers:** every MFE that imports `@ship-cars-usa/{globals,entities,ui-components,ctmslb}-frontend-package` from npm — chiefly the carrier-packages-cohort MFEs (`ctms-frontend`, `loadboard-frontend`, `platform-frontend`).
- **Publishes events to / Subscribes to / Owns data store:** none — build-time library repo, not a runtime service.

## Build / test / run
```
npm install                     # links local packages via Nx + npm workspaces
npm run build                   # nx run-many -t build
npm run build:affected          # nx affected -t build (only changed packages)
npm run test                    # nx run-many -t test (Vitest)
npm run lint                    # nx run-many -t lint
npm run graph                   # nx graph (visualize package deps)

# Release workflow:
npm run release:dry-run         # nx release --skip-publish --dry-run
npm run release                 # nx release --skip-publish (version + changelog)
npm run release:publish         # nx release publish (CI does this on merge)

# Local consumer testing:
npm run local-dev               # scripts/local-dev.sh
npm run yalc:dev                # scripts/yalc-dev.sh (link into a consumer via yalc)
```
Each package builds with **Vite** (+ `vite-plugin-dts` for `.d.ts`); tests run on **Vitest 3**. A **Verdaccio** local npm registry target (`local-registry`, port 4873) supports publishing/consuming packages locally before real publish.

## Key abstractions
- `packages/globals-frontend-package/` — shared types/constants/utilities (base of the dependency graph; a bump forces all four to rebuild).
- `packages/entities-frontend-package/` — entity models, schemas, Redux actions, socket listeners, and the backend endpoint path strings that consuming MFEs call.
- `packages/ui-components-frontend-package/` — shared UI primitives (theme, icons, fonts).
- `packages/ctmslb-components-frontend-package/` — CTMS + Loadboard-specific components.
- `nx.json` — Nx workspace config (release + affected-build orchestration).
- `.verdaccio/config.yml` + `scripts/{local-dev,yalc-dev}.sh` — local-registry / yalc developer loop.

## Don't-do-here / gotchas
- **Standalone-repo vs monorepo dual-existence.** The standalone sibling repos are now many versions behind and effectively legacy — new consumers should pin the monorepo-published versions. When a consumer "sees an older feature," check which source it's pinned to.
- **`nx release` is the canonical version-bump path.** Don't hand-edit `version` in any package's `package.json` — Nx owns the bump + changelog automation.
- **The README omits a version table on purpose** (anti-drift): versions live in each package's `CHANGELOG.md` and GitHub Releases.
- **`nx affected -t build`** depends on a correct git base ref in CI — a misconfigured ref rebuilds everything.
- **Two competing shared-lib generations** (carrier-packages here vs. `lm-*` elsewhere) — before adding a shared component, confirm which cohort the target MFE consumes; they are not interchangeable.
- **Independently versioned packages** — consumers can pin any combination; verify peer-dep compatibility when a consumer imports multiple.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/globals-frontend-package.md` / `entities-frontend-package.md` / `ui-components-frontend-package.md` / `ctmslb-components-frontend-package.md` — the (now-legacy) standalone versions.
- `~/projects/codebase-map/repos/ctms-frontend.md` / `loadboard-frontend.md` / `platform-frontend.md` — the carrier-packages-cohort MFE consumers.
- `~/projects/codebase-map/repos/posting-frontend.md` / `inventory-frontend.md` — MFEs on the newer `lm-*` cohort (not this repo).
- `~/projects/codebase-map/relations/infrastructure-triage.md` — standalone-repo re-evaluation candidates.
- `~/projects/codebase-map/domains/platform.md`.
