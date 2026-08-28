---
repo: contract-pricing-frontend
path: ~/projects/ship-cars-usa/contract-pricing-frontend
stack: TypeScript 5.9 / React 18.3.1 / single-spa 6.0.3 + single-spa-react 6.0.2 / Webpack 5.105 / MUI 6.5 + @mui/icons-material 6.4 + @mui/x-date-pickers 7.28 / material-react-table 3.2 / axios 1.17 / @tanstack/react-query 5.95 / react-router 7.17 / pnpm 11 (Node >=22)
domain: pricing-billing
shape: single-module
last-synced-commit: 321958ea84759a30be163a6295c935e0bbb1fb11
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# contract-pricing-frontend

## What it is
`@shipcars/contract-pricing` — the single-spa MFE for the **contract-pricing / customer-and-carrier pricing-contract admin UI** in the Loadmate/LITE shell. Companion to `contract-pricing-backend` (Quarkus). pnpm-managed, Node >=22; same modern lm-* cohort and toolchain as `user-frontend`.

The surface (`src/pages/`) is a landing page (`ContractsLandingPage`), a `ContractsList` (rendered for both customer and carrier routes), and `ManageContract` (create/edit, incl. cost-plus contracts, `PowerLanes`, and surcharges/discounts — the latest commit LITE-8421 preserves `applySurchargesDiscounts` when editing cost-plus). Grids use `material-react-table` + `@tanstack/react-virtual`.

The **whole MFE is subscription-gated**: `src/router/router.tsx` wraps every route in a single `GuardedOutlet` — routes added under it inherit the guard; when the `ContractPricing` feature/subscription is off, all routes render `SubscriptionNotActive`.

## How it fits

- **Consumes API of** (base URLs from `@ship-cars-usa/lm-global-config` `environments.contractPricing()`; `src/environments/*.ts` just re-export it):
  - `CONTRACT_PRICING_API` → `contract-pricing-backend` (`contractApiInstance`; `src/api/contracts.ts`, `validations.ts`, `generatedData.ts` — cost-estimator, power lanes, `/v1/contracts`).
  - `SHIPPER_LITE_API` → the posting backend (`postingApiInstance`; `src/api/contacts.ts` `/v3/contacts/search`, `dropdowns.ts`, `vehicles.ts`).
  - `LOCATION_PROVIDER_API` → `location-provider` (`locationProviderApiInstance`).
  - `CRM_API` → FreshSales CRM proxy via `src/services/analytics.service.ts`.
  - `GOOGLE_API_KEY` → Google Maps (`src/components/map/`).
- **Publishes events to:** none. Browser-only.
- **Subscribes to:** none directly. Mixpanel tracking via a hook; Unleash flags (`src/unleash.ts`).
- **Owns data store:** none (React Query caches server state).

## Build / test / run
```
pnpm install                   # Node >=22, pnpm >=11; FontAwesome + GitHub Packages tokens in ~/.npmrc
pnpm start                     # webpack serve --port 7125 --env isLocal
pnpm start:https               # HTTPS dev server
pnpm start:standalone          # standalone (no parent shell)
pnpm build:webpack             # webpack --mode=production
pnpm analyze                   # bundle-size analysis
pnpm lint / pnpm typecheck     # eslint 9 flat config / tsc
pnpm test / test:coverage      # jest 30 + @testing-library/react 16
pnpm check:circular            # madge --circular over ts/tsx
```

## Key abstractions

- `Entry` — `src/shipcars-contract-pricing.tsx` — single-spa lifecycle; error boundary returns `null` (leftover scaffolding — no Rollbar wiring unlike `user-frontend`).
- `Root` — `src/root.component.tsx` — provider stack (React Query, Unleash `FlagProvider`, MUI theme, `SCProvider`).
- `AppRouter` — `src/router/router.tsx` — `createBrowserRouter`; single `GuardedOutlet` enforces the `ContractPricing` subscription for the whole tree; routes in `src/router/routes.ts` (`ContractPricing` landing, `CustomerContracts`, `CarrierContracts`, contract + cost-plus create/edit).
- `src/api/axios.ts` — three axios instances (`contractApiInstance`, `postingApiInstance`, `locationProviderApiInstance`) in an `apiInstances` array.
- `src/api/utils.ts` — shared request interceptor: Bearer from `localStorage.getItem("token")` (`setAxiosInstancesRequestInterceptors`) + the same response-error normalizer as `user-frontend`.
- `src/services/http.service.ts` — legacy axios wrapper retained for the Mixpanel/analytics path (TODO to migrate to React Query).
- `src/api/*.ts` — `contracts`, `contacts`, `vehicles`, `dropdowns`, `generatedData`, `validations`, `locationProvider`, `analytics`.
- `src/schemas/` — Yup schemas (`createContract`, `costEstimator`); `src/hooks/query/` — React Query hooks; `src/components/FeatureBoundary/`, `src/components/map/`.

## Don't-do-here / gotchas

- **Old shadow undercounted the backends** — this MFE calls **three** backends at runtime (contract-pricing, posting, location-provider) plus CRM + Google Maps, not just `CONTRACT_PRICING_API`.
- **`axios` is declared under `devDependencies`** in `package.json` (1.17.0) yet imported at runtime in `src/api/axios.ts`. It resolves today via the workspace/hoisting, but it belongs in `dependencies`; don't rely on the current placement.
- **Token in `localStorage`** + **no `timeout` on any axios instance** — same caveats as `user-frontend`.
- **Whole-MFE subscription gate.** If pages render `SubscriptionNotActive` in an env, that is the `GuardedOutlet` doing its job — check the Unleash/subscription flag before suspecting a routing bug.
- **Shared-dep drift.** MUI 6.5 / single-spa 6 must match the shell's import-map (mismatch fails only at mount). Note MUI `material` is 6.5 while `icons-material` is 6.4 — minor intra-repo drift.
- **README is scaffolding boilerplate** — its "It should handle the posting functionality" line is a create-single-spa leftover; the real scope is the contract-pricing admin UI.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/contract-pricing-backend.md` — the Quarkus backend (per-customer/carrier pricing overrides).
- `~/projects/codebase-map/repos/user-frontend.md` — sibling lm-* MFE; identical axios/interceptor/analytics pattern.
- `~/projects/codebase-map/repos/location-provider.md` — location autocomplete backend.
- `~/projects/codebase-map/domains/pricing-billing.md`.
