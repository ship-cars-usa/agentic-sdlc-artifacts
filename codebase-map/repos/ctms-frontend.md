---
repo: ctms-frontend
path: ~/projects/ship-cars-usa/ctms-frontend
stack: TypeScript 5.6 / React 18.3 / single-spa 5.9 + single-spa-react 5.1 / Webpack 5.75 / MUI 5.15 + @mui/lab 5-alpha + @mui/x-date-pickers-pro 6.20 + **@mui/x-data-grid-premium 8.23** (paid MUI X Premium) / Redux (react-redux 8 + normalizr) / axios 0.21.1 / Unleash (@unleash/proxy-client-react 4.3)
domain: platform
shape: single-module
last-synced-commit: 9babc645247e235f19db154f709a62bddfbc9d48
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# ctms-frontend

## What it is
`@ship-cars/ctms-frontend` — the single-spa **app-parcel** MFE for the **CarrierTMS (CTMS)** surface. Registered by the `platform-frontend` root config as `@ship-cars/ctms` at dev port **8086** (`package.json` `start` → `webpack serve --port 8086`; README requires Node 22.x). Entry lifecycle in `src/shipcars-ctms.tsx` (`singleSpaReact` → `bootstrap`/`mount`/`unmount`); top React tree in `src/root.component.tsx` / `src/CarrierTMS.tsx`.

Distinctive among fleet MFEs for using **`@mui/x-data-grid-premium` ^8.23** — the **paid MUI X Premium** tier (Excel export, row pinning, aggregation), plus `@mui/x-date-pickers-pro` 6.20 (Pro tier). New since the last sync: **Unleash feature flags** via `@unleash/proxy-client-react` 4.3.1.

Still on the **older single-spa-5 generation** (`single-spa` ^5.9.3 / `single-spa-react` ^5.1.4) and still on the **carrier-packages** shared cohort (`@ship-cars-usa/*-frontend-package`), unlike the modernized `posting-frontend`/`inventory-frontend` which moved to single-spa 6 + the `lm-*` cohort.

## How it fits

- **Consumes API of** (all via `api-gateway`; in-repo `/api/...` paths are sparse because most endpoint strings live in the shared `entities-frontend-package`):
  - **`platform-backend` (Django monolith)** — the heaviest dependency, via unversioned DRF paths in `entities-frontend-package` (loads/orders/negotiations/offers/postings/contacts/companies/carriers) plus in-repo `/api/users`, `/api/reports`.
  - **`trip-planner` (Quarkus)** — in-repo `/api/tripplanner/v1/...` (trip archive/delete/count).
  - **`location-provider` (Quarkus)** — in-repo `/api/location-provider/v1,v2/...` (geocode, autocomplete, directions).
  - **`cube` (Quarkus)** and the broader Java set (negotiations-router, user-backend, attachment-backend, load-bookmark-backend, saved-search-handler, load-recommender, invoices, payment-backend, location-history-backend, crm-workflows, user-activity-tracker) — via `entities-frontend-package` endpoint modules.
- **Publishes events to:** none. Live updates arrive via a DOM CustomEvent socket bridge (`src/sockets/`) fed by the shell / `socket-server`.
- **Subscribes to:** none directly (see socket bridge above).
- **Owns data store:** none — Redux + normalizr in-memory store (`src/store.ts`, `src/{actions,reducers,selectors,state}/`).

## Build / test / run
```
npm install         # Node 22.x
npm run start       # webpack serve --port 8086
npm run build       # build:webpack (webpack --mode=production) + build:types (tsc)
npm run analyze
npm run test        # jest (BABEL_ENV=test)
```

## Key abstractions
- `src/shipcars-ctms.tsx` — single-spa lifecycle entry.
- `src/root.component.tsx` / `src/CarrierTMS.tsx` — top-level React tree.
- `src/store.ts` + `src/{actions,reducers,selectors,state}/` — Redux surface (react-redux 8, normalizr).
- `src/parcels/` — single-spa sub-parcels mounted by this MFE.
- `src/sockets/` — DOM-CustomEvent socket subscribers (live update bridge).
- `src/containers/` + `src/components/` + `src/hocs/` — connected vs. presentational vs. HOC-wrapped UI.
- `src/hooks/`, `src/utils/`, `src/constants/`, `src/theme/`, `src/typings.d.ts` — supporting modules.
- `@mui/x-data-grid-premium` (paid Premium) — the CTMS data grids; license-key handling is env/shell-injected.

## Don't-do-here / gotchas
- **MUI X Premium license required for production builds.** A missing key renders watermarked grids at runtime — verify the key is set in the build pipeline.
- **Older single-spa-5 generation.** `single-spa` 5.9 / `single-spa-react` 5.1 — one major behind `posting-frontend`/`inventory-frontend` (single-spa 6). Coordinated bump needed when the shell upgrades.
- **Still on the carrier-packages cohort** (`entities`/`globals`/`ui-components`/`ctmslb`-frontend-package), not the newer `lm-*` cohort. The bulk of the backend endpoint surface is defined there, not in this repo — trace `entities-frontend-package` to see what CTMS actually calls.
- **CTMS is a legacy surface** flagged for phase-out in prior reviews (`negotiations-router` seed). Weigh new investment accordingly.
- **`axios` 0.21.1** — old major with known CVEs; no default `timeout` (fleet pattern).
- **Dual-existence with `platform-frontend/src/CTMS/` and `src/CTMSParcel/`.** The root config still ships in-repo CTMS parcels; `ctms-frontend` is the standalone/newer render path. Verify which is canonical before changing CTMS UI.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/platform-frontend.md` — the dispatch-panel root config that registers this MFE (and still holds in-repo CTMS parcels).
- `~/projects/codebase-map/repos/platform-backend.md` — the Django monolith this MFE depends on heavily.
- `~/projects/codebase-map/repos/entities-frontend-package.md` — shared FE library holding the actual `/api/...` endpoint paths.
- `~/projects/codebase-map/repos/carrier-packages-frontend.md` — Nx monorepo home of the carrier-packages cohort this MFE consumes.
- `~/projects/codebase-map/repos/cube.md` — Quarkus read API for CTMS orders / loadboard postings.
- `~/projects/codebase-map/repos/api-gateway.md` — Go/Fiber edge proxy that JWT-verifies and routes every `/api/...` call.
- `~/projects/codebase-map/domains/platform.md`.
