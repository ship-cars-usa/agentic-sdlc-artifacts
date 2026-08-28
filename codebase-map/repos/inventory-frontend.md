---
repo: inventory-frontend
path: ~/projects/ship-cars-usa/inventory-frontend
stack: TypeScript 5.9 / React 18.3 / single-spa 6.0 + single-spa-react 6.0 / Webpack 5.104 / pnpm 11 / MUI 6.5 + @mui/x-date-pickers 7.23 / axios 1.17 / @tanstack/react-query 5.62 / react-hook-form 7.54 + yup + formik / material-react-table 3 / react-beautiful-dnd 13 / react-router 7 / Unleash 4.4
domain: listings-trade
shape: single-module
last-synced-commit: 5003948ccef1c966fc13a062ad1c978ee2b27d21
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# inventory-frontend

## What it is
`@shipcars/inventory` ("LoadMate Inventory Management") — single-spa app-parcel MFE for **vehicle-inventory management**, registered by `platform-frontend` as `@ship-cars/inventory` at dev port **7120**. Companion to `inventory-backend` (Spring Boot). Lets users manage carrier inventory (VINs, statuses, units filters, condition states) and build loads.

**Modernized stack** (biggest change since last sync): pnpm 11, **single-spa 6.0.3 / single-spa-react 6.0.2**, webpack 5.104, MUI 6.5, axios 1.17, React 18.3. Data via **@tanstack/react-query 5.62** (`src/query/`), forms via **react-hook-form 7.54 + yup** (also `formik` still present), tables via **material-react-table 3**, routing via **react-router 7** (`src/router/`), flags via **@unleash/proxy-client-react 4.4**, drag-and-drop via **react-beautiful-dnd 13**.

**Migrated off carrier-packages to the LoadMate `lm-*` package family**: `@ship-cars-usa/lm-components`, `lm-types`, `lm-utilities`, `lm-data-layer`, `lm-global-config`, `lm-import-map-overrides`. Env config comes from `lm-global-config` — `src/environments/*.environment.ts` is just `environments.inventory()`.

**Still ships two parallel UIs**: `src/InventoryManagement/` (v1) and `src/InventoryManagementV2/` (v2), selected at runtime by `src/FeatureBoundary/` (feature-flag gated). `src/SubscriptionNotActive/` guards users without an active subscription.

## How it fits

- **Consumes API of** (client modules in `src/api/`, base URLs from `lm-global-config`; README env vars now include `SHIPPER_LITE_API`, `NEGOTIATIONS_API`, `POSTINGS_API`, `COMPANIES_API`, `CARRIERS_API`, `LOCATION_TRACKING_API`, `REPORTING_TEMPLATES_API`, `QUOTE_MANAGER_API`, `INVENTORY_MANAGEMENT_API`, `LOAD_BUILDING_API`, plus `GOOGLE_*` and `UNLEASH_*`):
  - **`inventory-backend` (Spring Boot)** — `/api/inventory[/v1]` (heavy) via `src/api/inventoryManagement.ts`, `units.ts`, `vehicles.ts`.
  - **Load-building service** — very heavy `/api/loadbuilder/v1/...` via `src/api/loadBuilder.ts` (`/suggest/jobs`, build/status).
  - **`quote-manager`** (`/api/quote-manager/...`), **`cube`** (`/api/cube/...`), **`contract-pricing`** (`/api/contract-pricing/...`), **`payment-backend`** (`/api/payment/...`), **`location-history-backend`** (`/api/location_tracking/...`), **`location-provider`** (`/api/location-provider/...`), **`user-backend`** (`/api/usermanagement/...`), **`negotiations`/`postings`/`companies`/`carriers`/`network_companies`** (loadboard/platform), **`managedServices`**, **`driveaway`**, **`autoims`**, **`crm-workflow`**.
  - Google Maps + Directions for autocomplete/route preview.
- **Publishes events to / Subscribes to:** none server-side (browser-only).
- **Owns data store:** none (React Query cache + React context in `src/GlobalContextProvider.tsx` / `src/context/`).

## Build / test / run
```
corepack enable          # then pnpm >=11
pnpm install             # private registries: FontAwesome + GitHub Packages tokens in ~/.npmrc
pnpm start               # webpack serve --port 7120 --env isLocal
pnpm start:https         # HTTPS dev server
pnpm start:standalone    # standalone (no parent shell)
pnpm build               # concurrently build:webpack (webpack --mode=production) + build:types (tsc)
pnpm test                # jest
pnpm perf:table          # __perf__ table benchmarks
```
Toolchain: webpack 5.104 + webpack-cli 6 + webpack-dev-server 5.2. Modern ESLint 9 flat config (`eslint.config.mjs`).

## Key abstractions
- `src/shipcars-inventory.tsx` — single-spa lifecycle entry (captures `mountParcel`).
- `src/root.component.tsx` (+ `.scss`) — top-level React tree.
- `src/FeatureBoundary/` — picks v1 vs v2 UI from a feature flag.
- `src/InventoryManagement/` (v1) + `src/InventoryManagementV2/` (v2) — the two management surfaces.
- `src/SubscriptionNotActive/` — guarded UI for users without an active subscription.
- `src/ViewWrapper/` + `src/GlobalContextProvider.tsx` + `src/context/` — layout + top-level context.
- `src/api/` (`loadBuilder.ts`, `inventoryManagement.ts`, `units.ts`, `vehicles.ts`, `contacts.ts`, `managedServices.ts`, `locationProvider.ts`, `dropdowns.ts`) over `src/api/axios.ts`.
- `src/query/`, `src/services/`, `src/router/`, `src/hooks/`, `src/schemas/`, `src/interfaces/`, `src/types/`, `src/environments/` — standard structure shared with `posting-frontend`.

## Don't-do-here / gotchas
- **New `lm-*` package family, not carrier-packages.** Base URLs live in `lm-global-config`; don't hardcode env in `environment.ts`.
- **Two parallel UI versions in the bundle** (`InventoryManagement/` v1 + `InventoryManagementV2/` v2, gated by `FeatureBoundary/`). Editing the wrong one is a silent no-op for users on the other variant; bundle carries both until v1 is removed.
- **`SubscriptionNotActive/`** — this MFE is gated on subscription state owned by `payment-backend` / `user-backend`. Stale subscription state shows the wrong UI — verify freshness on state changes.
- **`react-beautiful-dnd` 13.1.1** — officially deprecated by Atlassian; React-18 strict-mode incompatibilities are known. A future bump means migrating to `@hello-pangea/dnd`.
- **single-spa 6 under a single-spa-5 root** — same skew note as `posting-frontend` (`platform-frontend` root is still single-spa 5.9).
- **`axios` 1.17** — confirm a default `timeout` is set on the instance.
- **Both `formik` and `react-hook-form` present** — pick the form lib already used in the surface you're editing rather than mixing.
- **pnpm workspace** — use pnpm (pinned via `packageManager`), not npm.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/inventory-backend.md` — the Spring Boot backend (Temporal for CSV/batch; `integrators-data-bridge` reads its PG directly).
- `~/projects/codebase-map/repos/posting-frontend.md` / `loadboard-frontend.md` — sibling listings-trade MFEs.
- `~/projects/codebase-map/repos/integrators-data-bridge.md` — shadow-caller on inventory's PG.
- `~/projects/codebase-map/repos/platform-frontend.md` — the root config that registers this MFE.
- `~/projects/codebase-map/domains/listings-trade.md`.
