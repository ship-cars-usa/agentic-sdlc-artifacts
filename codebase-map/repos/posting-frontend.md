---
repo: posting-frontend
path: ~/projects/ship-cars-usa/posting-frontend
stack: TypeScript 5.8 / React 18.2 / single-spa 6.0 + single-spa-react 6.0 / Webpack 5.105 / pnpm 11 / MUI 6.5 + @mui/x-date-pickers 7.28 / axios 1.17 / @reduxjs/toolkit 2 + react-redux 9 / @tanstack/react-query 5.71 + @tanstack/react-table 8 / react-hook-form 7.72 + yup / react-router 7 / Unleash 5
domain: listings-trade
shape: single-module
last-synced-commit: 5c0fb36438384223551f05d338c38497538930bd
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# posting-frontend

## What it is
`@shipcars/posting` — the single-spa app-parcel MFE for the **post-a-load** UI, registered by `platform-frontend` as `@ship-cars/shipperlite/posting` at dev port **7050**. Companion to `posting-backend` (Spring Boot). Lets users create/edit/dispatch postings, manage loads, contacts, invoices, driveaway, managed-services, and reporting.

**Fully modernized stack** (biggest change since last sync): pnpm 11, **single-spa 6.0.3 / single-spa-react 6.0.2**, webpack 5.105, MUI 6.5, axios 1.17, React 18.2. State is **@reduxjs/toolkit 2 + react-redux 9** (`src/store/`) alongside **@tanstack/react-query 5.71** (`src/query/`), **react-hook-form 7.72 + yup** (`src/schemas/`), **@tanstack/react-table 8** and **react-virtuoso / react-window** for large lists. Routing via **react-router 7** (`src/router/`). Feature flags via **@unleash/proxy-client-react 5** (`src/unleash.ts`). Error boundary reports to **Rollbar** (`src/shipcars-posting.tsx`).

**Migrated off the carrier-packages cohort to the new LoadMate `lm-*` package family**: `@ship-cars-usa/lm-components`, `lm-types`, `lm-utilities`, `lm-data-layer`, `lm-global-config`, `lm-import-map-overrides` (the `lm-*` packages' home repo is not in this workspace). Environment config now comes from `lm-global-config` — `src/environments/*.environment.ts` is just `environments.posting()`.

Note: several `src/` subtrees carry their own in-repo `CLAUDE.md` (`src/api/`, `src/services/`, `src/pages/`, `src/query/`) — read those for local guidance.

## How it fits

- **Consumes API of** (per-service client modules in `src/api/`, base URLs from `lm-global-config`; README env vars: `SHIPPER_LITE_API`, `NEGOTIATIONS_API`, `POSTINGS_API`, `COMPANIES_API`, `CARRIERS_API`, `GOOGLE_API_KEY`, `GOOGLE_DIRECTIONS_API_ENDPOINT`, `BASE_PATH`):
  - **`posting-backend` (Spring Boot)** — the main `SHIPPER_LITE_API` (`src/api/load.ts`, `loadAssistant.ts`, `dropdowns.ts`, `lineItems.ts`).
  - **`loadboard-backend` (Quarkus)** — negotiations/postings/companies/carriers (`networkCompany.ts`, `company.ts`, `carrier.ts`, `reviewOffers.ts`).
  - **`company-documents` (Python / FastAPI)** — `src/api/companyDocuments.ts` + `src/query/companyDocuments.ts` (CoI / carrier-document compliance, e.g. `AddLoad/CoiStatusPanel`). This carrier-document flow moved here from `loadboard-frontend`.
  - Plus `invoices`, `payment`, `vehicles`, `contacts`, `locationProvider`, `locationTracking`, `managedServices`, `inventoryManagement`, `axe` (axe-call-integration), `chat`, `driver`, `files`, `dashboard`, `reports`, `suggestRate` — each a module under `src/api/`.
  - Google Maps + Directions for autocomplete/route preview.
- **Publishes events to / Subscribes to:** none server-side (browser-only).
- **Owns data store:** none (React Query cache + Redux Toolkit client state).

## Build / test / run
```
corepack enable          # then pnpm >=11
pnpm install             # private registries: FontAwesome + GitHub Packages tokens in ~/.npmrc
pnpm start               # webpack serve --port 7050 --env isLocal
pnpm start:https         # HTTPS dev server
pnpm start:standalone    # standalone (no parent shell)
pnpm build               # webpack --mode=production
pnpm test                # jest
pnpm check:circular      # madge --circular
```
Toolchain: webpack 5.105 + webpack-cli 7 + webpack-dev-server 5.2. Local `lm-*` linking via `scripts/yalc-link-lm.sh` (`pnpm link:lm-packages`).

## Key abstractions
- `src/shipcars-posting.tsx` — single-spa lifecycle entry (captures `mountParcel`; Rollbar error boundary).
- `src/root.component.tsx` (+ `.scss`) — top-level React tree.
- `src/api/` — per-service REST client modules (`load.ts`, `companyDocuments.ts`, `networkCompany.ts`, …) over `src/api/axios.ts`.
- `src/services/http.service.ts` + `analytics.service.ts` — HTTP + analytics wrappers.
- `src/query/` — React Query hooks (mirror of `src/api/`).
- `src/store/` — Redux Toolkit slices.
- `src/router/` — react-router 7 routing.
- `src/pages/` — `AddLoad`, `ContactBook`, `Dashboard`, `Driveaway`, `Invoices`, `LoadDetails`, `Loads`, `ManagedServices`, `Reporting`.
- `src/schemas/` — yup/react-hook-form validation.
- `src/providers/`, `src/theme/`, `src/unleash.ts`, `src/environments/` — context, MUI theme, Unleash, env config.

## Don't-do-here / gotchas
- **New `lm-*` package family, not carrier-packages.** Don't add `@ship-cars-usa/*-frontend-package` deps here — this MFE is on the LoadMate `lm-*` cohort. Env/base-URLs live in `lm-global-config`, not in local `environment.ts`.
- **single-spa 6 under a single-spa-5 root.** `platform-frontend` (the root config) is still on single-spa 5.9 while this MFE declares single-spa 6.0.3 — watch for lifecycle/interop skew when mount behavior looks off.
- **Multi-backend REST surface** (5+ base URLs). A wire-format change in `posting-backend`, `loadboard-backend`, or `company-documents` surfaces here first — coordinate breaking changes through the shared type layer.
- **Unleash feature flags** (`src/unleash.ts`) drive conditional rendering — check the Unleash dashboard for "the button isn't there" bugs.
- **`axios` 1.17** — modern; confirm a default `timeout` is set on the instance (fleet gap otherwise).
- **pnpm workspace.** Use pnpm (not npm); `packageManager` pins the exact pnpm version.
- **Google Maps key in env** — scope by HTTP referrer in Google Cloud Console.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/posting-backend.md` — the Spring Boot backend (densest fanout in listings-trade).
- `~/projects/codebase-map/repos/company-documents.md` — the FastAPI carrier-document service this MFE calls directly.
- `~/projects/codebase-map/repos/loadboard-frontend.md` / `inventory-frontend.md` — sibling listings-trade MFEs.
- `~/projects/codebase-map/repos/platform-frontend.md` — the root config that registers this MFE.
- `~/projects/codebase-map/domains/listings-trade.md`.
