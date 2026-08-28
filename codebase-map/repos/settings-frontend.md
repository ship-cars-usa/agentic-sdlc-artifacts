---
repo: settings-frontend
path: ~/projects/ship-cars-usa/settings-frontend
stack: TypeScript 5.6 / React 18.3.1 / single-spa 5.9.3 + single-spa-react 5.1.2 / Webpack 5.75 / MUI 5.16 + @mui/lab alpha / axios 0.21.1 / Redux 4 (react-redux 8 + redux-thunk + reselect + normalizr) / react-router-dom 5 / npm (Node >=22.14)
domain: platform
shape: single-module
last-synced-commit: 1bc9fd5b72742900aaf070855ffe3353bcc421c7
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# settings-frontend

## What it is
`@ship-cars/settings-frontend` — a single-spa app-parcel MFE in the **CTMS / LoadBoard** frontend cohort (it depends on `@ship-cars-usa/entities-frontend-package`, `globals-frontend-package`, `ui-components-frontend-package`, `ctmslb-components-frontend-package` — **not** the Loadmate `lm-*` packages). Older single-spa-5 generation. npm-managed, Node >=22.14. Dev port 8085.

Redux-based (`redux` + `react-redux` + `redux-thunk` + `reselect` + `normalizr`), with `src/actions`, `src/reducers`, `src/selectors`, `src/state`. **The live routed surface today is the Billing page only** — `src/containers/Routes.tsx` renders just `billingIndex` → `BillingPage`; the profile and company routes are commented out. Latest commit SCP-15043 (2026-08-20) bumped `entities-frontend-package` to v20 (a major shared-package upgrade).

## How it fits

- **Consumes API of:** the Django **`platform-backend`** over same-origin relative paths (base axios, no `baseURL`; the shell proxies). `src/actions/billing.ts` calls `/api/companies/{id}/billing_info`, `/api/billing_periods`, `/api/billing_periods/user_info`, `/api/driver_loads`; errors run through `showDjangoAxiosError` (confirming the Django backend). `src/actions/{auth,addons,core}.ts` cover current user / add-ons / entity CRUD. Additional network access is inherited from `entities-frontend-package` actions.
- **Publishes events to:** none.
- **Subscribes to:** **Pusher**, via `entities-frontend-package`. `src/sockets/companies.ts` and `src/sockets/users.ts` call `entities-frontend-package/sockets/*.subscribeForPusherEvents({...})` and dispatch `addEntities` / `updateEntities` / `removeEntities` into the local Redux store. Also listens to `globals-frontend-package/utils/events` `onResetEntities` (a cross-MFE DOM-event bridge) to clear the store. (This is Pusher — NOT the `socket-server` WebSocket used by `chat-frontend`.)
- **Owns data store:** none (browser-only; normalized entities in Redux).

## Build / test / run
```
npm install                 # Node >=22.14
npm run start               # webpack serve --port 8085
npm run build:webpack       # webpack --mode=production
npm run lint / coverage     # eslint / jest 29
npm run update:carrier-packages   # bumps the 4 @ship-cars-usa CTMS/LB shared packages to latest
```

## Key abstractions

- `Entry` — `src/shipcars-settings.tsx` — single-spa lifecycle (`singleSpaReact`), error boundary renders "Error when mounting parcel".
- `Root` — `src/root.component.tsx` — provider stack: Redux `Provider` (`src/store.ts`), Unleash `FlagProvider` (`clients.unleash` from `globals-frontend-package/utils/integrations`), MUI `ThemeProvider` (`createExperimentalLightTheme` from `ui-components-frontend-package`), emotion + `tss-react` cache providers, `react-error-boundary`.
- `Settings` — `src/Settings.tsx` — on mount dispatches `ensureCurrentUser` + `ensureAddons`, subscribes company/user Pusher events, and wires `onResetEntities`; gates rendering on Unleash `flagsReady`.
- `src/containers/Routes.tsx` — `react-router-dom` v5 `Switch`; currently only `billingIndex` → `BillingPage`.
- `src/actions/*.ts` — `billing`, `auth`, `addons`, `core`, `notificationSnackbar` (thunks).
- `src/sockets/{companies,users}.ts` — Pusher subscriptions bridged to Redux.
- `src/theme/mui-classname-setup.ts`, `src/constants/` (incl. `CLASS_NAMES_PREFIX`, route + action constants).

## Don't-do-here / gotchas

- **Old shadow's backend guesses were wrong.** It speculated `user-backend` / `payment-backend` / Keycloak-admin; the actual live calls go to **Django `platform-backend`** (`/api/...` billing endpoints), with sockets via **Pusher** (`entities-frontend-package`). Trust the source.
- **CTMS/LB cohort, not Loadmate.** Do not confuse with `user-frontend` (the lm-* user/company MFE). Different shared-package families; the settings surfaces are not interchangeable.
- **`axios` 0.21.1** — old major with known CVEs; shared by the older single-spa-5 cohort. Bump requires coordinated shell testing.
- **Older single-spa generation** (single-spa 5.9 / single-spa-react 5.1, Webpack 5.75) — needs a coordinated bump when the shell upgrades.
- **`entities-frontend-package` is a heavy shared dependency** — it carries the Pusher socket layer, entity models, and much of the network access. The SCP-15043 v20 bump is a major; regressions here often originate in that package, not this repo.
- **Most routes are commented out** in `Routes.tsx` — the profile/company settings are dormant; only billing is live. Confirm intent before "re-enabling" them.
- `CLAUDE.md` present: enforces a "STOP and DESCRIBE before implementing, wait for approval" workflow and points at `dev-hub/ai/ai-rules-*.md`.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/platform-backend.md` — the Django backend serving the billing endpoints.
- `~/projects/codebase-map/repos/gallery-frontend.md` — sibling CTMS/LB cohort MFE (same `entities`/`globals` packages, same single-spa-5 generation).
- `~/projects/codebase-map/repos/user-frontend.md` — the Loadmate-cohort user/company MFE (different stack; do not conflate).
- `~/projects/codebase-map/domains/platform.md`.
