---
repo: loadboard-frontend
path: ~/projects/ship-cars-usa/loadboard-frontend
stack: TypeScript 5.6 / React 18.3 / single-spa 5.9 + single-spa-react 5.1 / Webpack 5.75 / MUI 5.16 + @mui/x-date-pickers-pro 6.19 / axios 0.21.1 / Redux 4 (react-redux 8 + redux-thunk + normalizr) / react-chartjs-2 4 + chart.js 3.7 / react-dnd 16 / tss-react / Unleash
domain: listings-trade
shape: single-module
last-synced-commit: d0c6fdbc127c7c648bb02ca3ee4900e45332222a
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# loadboard-frontend

## What it is
`@ship-cars/loadboard-frontend` — the single-spa app-parcel MFE for the **loadboard** UI, registered by `platform-frontend` as `@ship-cars/loadboard` at dev port 8080. Companion to `loadboard-backend` (Quarkus). The loadboard is where carriers browse, filter, bid on, and dispatch loads — correspondingly the **richest interaction model among the listings-trade MFEs**:

- **Redux** (`src/{actions,reducers,selectors,state}/` + `src/store.ts`) — classic redux 4 + react-redux 8 + redux-thunk, not React Query.
- **normalizr** (`src/entities/`) — entity normalization.
- **single-spa sub-parcels** (`src/parcels/`) — the loadboard mounts smaller MFEs into itself.
- **DOM-CustomEvent sockets** (`src/sockets/`) — live-update bridge.
- **react-chartjs-2 4 / chart.js 3.7** — rate/volume charts; **react-dnd 16** (+ html5/touch backends) — drag-and-drop dispatch.

Node `>=22.14.0`. Still on the **older single-spa-5 generation** and the **carrier-packages** cohort — lags the single-spa-6 + `lm-*` modernization of `posting-frontend`/`inventory-frontend`.

## How it fits

- **Consumes API of** (in-repo `/api/...` paths, plus more via `entities-frontend-package`; all through `api-gateway`):
  - **`platform-backend` (Django monolith)** — unversioned DRF paths: `/api/postings/`, `/api/network_companies/` (incl. `.../safer_watch/`), `/api/carrier_companies/`, `/api/shipper_companies/`, `/api/generic_change_log/`. Primary carrier-discovery / posting-listing reads/writes.
  - **`loadboard-backend` (Quarkus)** — `/api/loadboard/v3/companies/{carriers,shippers}` (legacy v3; cube absorbs v4).
  - **`trip-planner` (Quarkus)** — heavy in-repo use of `/api/tripplanner/v1/...` (load-to-trip transfer, posting attach/detach, trip lists).
  - **`location-provider` (Quarkus)** — `/api/location-provider/v2/...` (directions, geocode, autocomplete).
  - **`user-backend`** (`/api/usermanagement/...`) and **`user-activity-tracker`** (`/api/user-activity-tracker/...`).
  - **`cube`** and the broad Java set via `entities-frontend-package` (negotiations-router, load-bookmark-backend, saved-search-handler, load-recommender, invoices, payment-backend, location-history-backend, attachment-backend, metadata, crm-workflows).
  - Google Maps (marker clustering, autocomplete, route preview).
- **URL-pattern decoder:** unversioned `/api/<noun>/` (trailing slash) → `platform-backend` (DRF); `/api/<service>/v<N>/...` → a Java/Quarkus service. `api-gateway` enforces routing by URL prefix.
- **Publishes events to / Subscribes to:** none server-side; live updates via the DOM-CustomEvent socket bridge from `socket-server`.
- **Owns data store:** none (Redux + normalizr in-memory).

> Note: the direct `company-documents` (FastAPI) calls the previous shadow attributed to this MFE are no longer present in-repo — that carrier-document flow now lives in `posting-frontend`.

## Build / test / run
```
npm install              # Node >=22.14.0
npm run start            # webpack-dev-server (port from webpack config)
npm run build            # webpack --mode=production
npm run analyze          # bundle-size analysis
npm run test             # jest (BABEL_ENV=test)
```
For deployed-env testing use single-spa's `import-map-overrides` to point QA/dev at a local bundle (per README).

## Key abstractions
- `src/shipcars-loadboard.tsx` — single-spa lifecycle entry.
- `src/set-public-path.tsx` — webpack public-path bootstrap (single-spa convention).
- `src/root.component.tsx` — top-level React tree.
- `src/store.ts` + `src/{actions,reducers,selectors,state}/` — Redux state surface.
- `src/entities/` — normalizr entity definitions.
- `src/containers/` + `src/components/` — connected vs. presentational.
- `src/parcels/` — single-spa sub-parcels mounted by this MFE.
- `src/sockets/` — DOM-CustomEvent socket subscribers.
- `src/hooks/`, `src/utils/`, `src/constants/`, `src/styles/`, `src/typings.d.ts` — supporting modules.

## Don't-do-here / gotchas
- **`axios` 0.21.1** — known CVEs (e.g. CVE-2023-45857 SSRF); no default `timeout`. Bumping to 1.x is non-trivial (interceptor-config shape change).
- **Older single-spa-5 generation** (`single-spa` 5.9.4 / `single-spa-react` 5.1.4) + **carrier-packages** cohort — one generation behind posting/inventory. Bump in lock-step with the shell.
- **Most complex MFE in listings-trade**: Redux + normalizr + sub-parcels + sockets + charts + drag-and-drop. Land refactors incrementally; verify each Redux slice in isolation.
- **Sub-parcels under `src/parcels/`** can have independent lifecycles — confirm they unmount cleanly to avoid single-spa memory leaks.
- **`react-dnd` 16** in React 18 strict mode can double-invoke — test against the prod shell.
- **`react-chartjs-2` 4 / `chart.js` 3.7** — API breaks between chart.js majors; keep them lock-stepped.
- **`@mui/x-date-pickers-pro` 6.19** is the **paid** MUI X Pro tier — license-key handling is done elsewhere (shell/env).
- **DOM-CustomEvent socket pattern** — if live load updates stop, the bug is in the shell's WebSocket bridge / `socket-server`, not here.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/loadboard-backend.md` — the Quarkus backend (3 PG datasources; Temporal workflows).
- `~/projects/codebase-map/repos/platform-backend.md` — the Django monolith this MFE depends on for postings/companies.
- `~/projects/codebase-map/repos/entities-frontend-package.md` — shared FE library carrying most `/api/...` paths.
- `~/projects/codebase-map/repos/cube.md` — modern loadboard read API.
- `~/projects/codebase-map/repos/api-gateway.md` — Go/Fiber edge proxy.
- `~/projects/codebase-map/repos/posting-frontend.md` / `inventory-frontend.md` — sibling MFEs on the newer stack.
- `~/projects/codebase-map/repos/socket-server.md` — WebSocket layer the shell bridges from.
- `~/projects/codebase-map/domains/listings-trade.md`.
