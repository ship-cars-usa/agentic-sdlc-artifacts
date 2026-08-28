---
repo: platform-frontend
path: ~/projects/ship-cars-usa/platform-frontend
stack: TypeScript 5.6 / React 18.3 / single-spa 5.9 + single-spa-react 4.3 / Webpack 5.89 / MUI 5.16 + @mui/x-date-pickers-pro 6.19 / Keycloak (@react-keycloak/web 3.4) / socket.io-client / @vis.gl/react-google-maps / @dnd-kit / Unleash / axios 0.21.1
domain: platform
shape: multi-module
last-synced-commit: 7e51dc635c63183dc5c68e1a6d435dab0cf87423
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# platform-frontend

## What it is
**The dispatch-panel single-spa root config** — `package.json` `name == "@ship-cars/root-config"`. Per the README it "owns the HTML shell, the shared import map, and the registration of every microfrontend (loadboard, CTMS, trip-planner, settings, etc.)." This is the **authenticated** dispatch-panel shell; `public-root-app-frontend` is the public-side counterpart. Node `>=22.14.0` (`engines`).

The repo is **both a root config and a bag of in-repo parcels**: `src/` holds the root-config entry (`shipcars-root-config.ts`, `single-spa-app.ts`, `index.tsx`, `src/routes/`) **and** many feature parcels — `App`, `Authentication`, `CTMS`, `CTMSParcel`, `Company`, `ContractPricing`, `Conversations.tsx`, `DriverChat`, `DriverOnly`, `ExecutiveDashboard`, `Inventory`, `Loadboard`, `LoadScout`, `Orders`, `ShipperLite`, `OrderImporter`, `VirtualTripPlanner`, `Gallery`, `Inspection`, `Settings`, `Users`, etc. Many of these have since been extracted to standalone MFE repos (e.g. `ctms-frontend`, `posting-frontend`, `inventory-frontend`, `contract-pricing-frontend`, `executive-dashboard-frontend`, `chat-frontend`) — the in-repo parcels are the older, not-yet-extracted versions.

The **import map lives in `webpack/index.ejs`**; in `start:*` (local) mode it points each module at a fixed localhost port so you can run one MFE from source (README table): loadboard 8080, inspection-requirements 8081, trip-planner 8082, carrier-order-importer 8083, gallery 8084, settings 8085, ctms 8086, posting (`@ship-cars/shipperlite/posting`) 7050, user 7070, chat 7080, inventory 7120, contract-pricing 7125.

## How it fits

- **Registers / mounts:** every dispatch-panel MFE via the single-spa import map. Standalone MFEs (`ctms-frontend`, `loadboard-frontend`, `posting-frontend`, `inventory-frontend`, `trip-planner-frontend`, `chat-frontend`, …) are wired in here.
- **Hosts in-repo parcels:** the feature parcels under `src/` ship inside this root's bundle (slowly being extracted).
- **Consumes API of:** every dispatch-panel backend transitively, via the mounted MFEs and the shared `entities-frontend-package`; directly handles **Keycloak** auth (`src/Authentication/`, `@react-keycloak/web`) and a `socket.io-client` bridge for live events.
- **Publishes events to / Subscribes to:** none server-side; brokers a WebSocket (`socket.io-client`) → DOM CustomEvent bridge that child MFEs subscribe to.
- **Owns data store:** none (in-memory orchestration; Redux via react-redux 8).

## Build / test / run
```
npm install                 # Node >=22.14.0; needs NPM_FONT_AWESOME_AUTH_TOKEN + GITHUB_READ_TOKEN
npm run start:dev           # webpack serve --port 3000, API proxied to https://dev.ship.cars
npm run start:qa            # → qa.ship.cars
npm run start:staging       # → staging.ship.cars
npm run build               # build:webpack (webpack --mode=production) + build:types (tsc)
npm run test                # jest
```
There is no plain `npm start` — pick the `start:*` variant matching the backend you want to hit; the app always serves at `http://localhost:3000/app/`.

## Key abstractions
- `src/shipcars-root-config.ts` + `src/single-spa-app.ts` + `src/index.tsx` — root-config entry + app registration.
- `src/routes/` — top-level route registration.
- `webpack/index.ejs` — the import map (the source of truth for which MFE loads from where).
- `src/Authentication/` — Keycloak-side auth (`@react-keycloak/web`, `jwt-decode`).
- `src/CTMS`, `src/CTMSParcel`, `src/ContractPricing`, `src/ExecutiveDashboard`, `src/Conversations.tsx`, `src/DriverChat`, `src/LoadScout`, `src/Loadboard`, `src/Inventory`, `src/Orders`, `src/ShipperLite`, `src/OrderImporter`, `src/VirtualTripPlanner` — in-repo feature parcels (pre-extraction).
- `src/Common`, `src/Core`, `src/Entities`, `src/Filtering`, `src/Layout`, `src/hoc`, `src/hooks`, `src/store` — shared utilities.
- `admin/` — admin-only routes shipped in the same bundle.

## Don't-do-here / gotchas
- **README is now correct on Node** (`>=22.14.0`) — the earlier "Node 10.x" claim is gone. Use Node 22.
- **Oldest single-spa-react in the cohort** (`single-spa-react` ^4.3.1, `single-spa` ^5.9.4) — behind the standalone MFEs (which run single-spa-react 5–6). Upgrading is hard precisely because of the in-repo parcels; single-spa 6 MFEs (posting/inventory) run under this v5 root, so watch for interop skew.
- **Dual-existence with extracted MFEs.** In-repo `CTMS/`, `ContractPricing/`, `ExecutiveDashboard/`, `Conversations.tsx`, `DriverChat/`, `Inventory/`, `Loadboard/` are siblings of the standalone repos. Confirm which is the canonical render path before editing a feature.
- **Still on the carrier-packages cohort** (`entities`/`globals`/`ui-components`/`ctmslb`-frontend-package 20.0.0/6.22.1/2.1.6/5.2.4), not the newer `lm-*` cohort — different shared-lib generation from posting/inventory.
- **`axios` 0.21.1** — old major; no default timeout.
- **`admin/` at the top level** — verify prod routing gates these behind Keycloak roles rather than shipping them to every user.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/public-root-app-frontend.md` — public-side root config; smaller / simpler.
- `~/projects/codebase-map/repos/ctms-frontend.md` / `loadboard-frontend.md` / `posting-frontend.md` / `inventory-frontend.md` / `trip-planner-frontend.md` / `chat-frontend.md` / `contract-pricing-frontend.md` / `executive-dashboard-frontend.md` — MFEs registered by this root.
- `~/projects/codebase-map/repos/entities-frontend-package.md` — shared FE library holding backend endpoint paths.
- `~/projects/codebase-map/repos/api-gateway.md` — Go/Fiber edge proxy.
- `~/projects/codebase-map/domains/platform.md`.
