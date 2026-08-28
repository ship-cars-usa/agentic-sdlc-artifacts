---
repo: user-frontend
path: ~/projects/ship-cars-usa/user-frontend
stack: TypeScript 5.9 / React 18.3.1 / single-spa 6.0.3 + single-spa-react 6.0.2 / Webpack 5.105 / MUI 6.5 + @mui/x-date-pickers 7.28 / axios 1.17 / @tanstack/react-query 5.71 / react-router 7.17 / pnpm 11 (Node >=22)
domain: identity
shape: single-module
last-synced-commit: 17771fca3a62ae59952e160909009407a0b929d6
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# user-frontend

## What it is
`@shipcars/user` — the single-spa micro-frontend that owns the **user / company / billing UI** in the Loadmate/LITE shell. Scaffolded with `npx create-single-spa --moduleType app-parcel` (per `README.md`), bundled with `webpack-config-single-spa-react-ts`, and mounted by the Loadmate root config. pnpm-managed (`packageManager: pnpm@11.6.0`), Node >=22.

The live surface is five page groups under `src/pages/`: `CompanyProfile` (management / settings / IM-settings tabs), `ManageUsers`, `ManageCompanies`, `ManageCompanyUsers` (create/edit each), and `PricingPlans` (`/change-plans`). Routing is a `createBrowserRouter` tree in `src/router/router.tsx` keyed off `UserRoutes` in `src/router/routes.ts`; the IM-settings tab is feature-gated (`ELoadMateFeature.AutoIms`).

The broadest API surface of the assigned MFEs — its `src/api/axios.ts` wires **seven** axios instances against six-plus backends.

## How it fits

- **Consumes API of** (base URLs resolved by `@ship-cars-usa/lm-global-config` `environments.user()`; every `src/environments/*.ts` just re-exports it — no URLs live in the repo):
  - `SHIPPER_LITE_USER_API` → `user-backend` (`userApiInstance`; e.g. `src/api/integratorCredentials.ts` → `/v3/company/integrator-credentials`).
  - `PAYMENT_API` + `/v1` → `payment-backend` (`paymentApiInstance`).
  - `QUOTE_MANAGER_API` → `quote-manager-backend` (`quoteManagerServiceApiInstance`).
  - `AUTOIMS_SERVICE_URL` → `autoims-backend` (`autoImsApiInstance`).
  - `SHIPPER_LITE_API` → the posting backend (`postingApiInstance`).
  - `LOCATION_PROVIDER_API` → `location-provider` (`locationProviderApiInstance`).
  - `envPath() + "/api/loadmate"` → the Loadmate gateway (`loadmateApiInstance`; commented as part of a future BE migration).
  - `CRM_API` + `/v1/event/<event>` → FreshSales CRM proxy, via `src/services/analytics.service.ts` (fired only for a whitelist of events to stay under FreshSales' rate limit).
  - `GOOGLE_API_KEY` → Google Places autocomplete for location inputs (passed through `SCProvider` global context, not an axios call).
- **Publishes events to:** none. Browser-only.
- **Subscribes to:** none directly (no socket bridge in this repo). Mixpanel tracking is set up in the router via `useSetMixpanelTracking`.
- **Owns data store:** none (browser-only; server state cached by React Query).

## Build / test / run
```
pnpm install                   # Node >=22, pnpm >=11; needs FontAwesome + GitHub Packages tokens in ~/.npmrc
pnpm start                     # webpack serve --port 7070 --env isLocal
pnpm start:https               # HTTPS dev server (webpack.https.mjs)
pnpm start:standalone          # standalone (no parent shell)
pnpm build:webpack             # webpack --mode=production
pnpm analyze                   # bundle-size analysis
pnpm lint / pnpm typecheck     # eslint 9 flat config / tsc
pnpm test / test:coverage      # jest 30 + @testing-library/react 16
```
Registry note (`README.md`): private FontAwesome + GitHub Packages tokens must be set at the **user** `~/.npmrc` via `pnpm config set` — pnpm ignores the committed `.npmrc` for auth.

## Key abstractions

- `Entry` — `src/shipcars-user.tsx` — single-spa lifecycle (`singleSpaReact`); error boundary reports to `window.Rollbar.critical`.
- `Root` — `src/root.component.tsx` — providers: `QueryClientProvider` (React Query, global error → toast), `FlagProvider` (Unleash), `ThemeProvider` + `StyledEngineProvider`, `SCProvider` (global context: `GOOGLE_API_KEY`, `BASE_PATH`), and `OverrideWidget` (import-map overrides, dev/qa only). Class prefix `slujss`. Wires the 401 callback from shell props via `setAxiosInstancesResponseInterceptors(handleUnauthorizedResponse)`.
- `AppRouter` — `src/router/router.tsx` — `createBrowserRouter`; `FeatureRoute` gates routes on Unleash flags.
- `src/api/axios.ts` — the seven axios instances above + `apiInstances` array.
- `src/api/apiUtils.ts` — shared request interceptor (`getAuthToken`: Bearer from `localStorage.getItem("token")`) and response-error normalizer (`handleResponseError`: unwraps `errorDetails`/`error`, renames `status`→`httpStatus`, calls the shell's 401 callback).
- `src/api/*.ts` — per-domain REST modules: `user`, `company`, `childCompanies`, `childCompanyUsers`, `integratorCredentials`, `subscription`, `payment`, `invoices`, `lineItems`, `quoteManagerService`, `locationProvider`, `autoims`, `dropdowns`, `optionsData`.
- `src/services/http.service.ts` — legacy axios wrapper (Bearer interceptor) kept **only** for the Mixpanel/analytics path; marked TODO to delete once analytics moves to React Query.
- `src/hooks/query/` — React Query hooks (incl. `useFeature`).
- `src/context/`, `src/schemas/` (Yup), `src/common/Theme/theme.ts`, `src/ViewWrapper/`.

## Don't-do-here / gotchas

- **Token in `localStorage`.** Both the api-instance interceptor and the legacy `http.service.ts` read `localStorage.getItem("token")` on every request. XSS in the shell exfiltrates it; the shell's CSP is part of this MFE's threat surface.
- **No `timeout` on any axios instance.** All seven are `axios.create({ baseURL })` with no `timeout`; a hung backend holds the request until the browser aborts. Add `timeout` if latency guarantees matter.
- **Shared deps from the shell.** React/MUI/single-spa are expected via the import-map shared scope. **MUI 6.5** and **single-spa/single-spa-react 6** here must match the shell — a shell still on MUI 5 or single-spa 5 produces mismatched-runtime/mismatched-hooks errors only at mount, not in CI.
- **Two overlapping analytics paths** — Mixpanel (router hook) and FreshSales CRM (`analytics.service.ts`). The CRM path filters to a whitelist to avoid FreshSales' ~2k req/min cap; don't broaden it casually.
- **Widest blast radius of the FE fleet.** A wire-format change in `user-backend`, `payment-backend`, `quote-manager-backend`, `autoims-backend`, `location-provider`, or the posting backend can surface here first.
- **`@mui/x-date-pickers` 7.28.3 is the free (non-Pro) build** — confirm before reaching for Pro-only pickers.
- **Forms use both `react-hook-form` 7.72 and `formik` 2.4.9** — check which a given page uses before adding validation.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/user-backend.md` — primary backend (users + companies, system of record).
- `~/projects/codebase-map/repos/payment-backend.md`, `quote-manager-backend.md`, `autoims-backend.md`, `location-provider.md`, `invoices.md` — other backends this MFE drives.
- `~/projects/codebase-map/repos/contract-pricing-frontend.md` — same lm-* MFE cohort, same axios/interceptor pattern.
- `~/projects/codebase-map/domains/identity.md`.
