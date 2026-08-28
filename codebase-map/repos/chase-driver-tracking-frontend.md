---
repo: chase-driver-tracking-frontend
path: ~/projects/ship-cars-usa/chase-driver-tracking-frontend
stack: TypeScript / React 18.3.1 / single-spa 6.0.3 + single-spa-react 6.0.2 / Webpack 5.105 / MUI 6.4 / react-router 7.17 / TanStack Query 5.95 / react-hook-form 7.72 / axios 1.17 / pnpm 11 (Node ≥22)
domain: operations
shape: single-module (single-spa app-parcel)
last-synced-commit: a64a02e3463cb4ad283dc2ff6e31e4cfb3f1b4cd
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# chase-driver-tracking-frontend

## What it is
The **"Chase" driver-load tracking MFE** — a single-spa app-parcel (`@shipcars/chase-driver-tracking`) that renders a driver's load view. Its pages are `ChaseDriverLoad`, `LoadSummaryView`, and `PaperFlowLoad` (`src/pages/`), routed by `src/router/router.tsx` + `routes.ts`, with `LoadRouteWrapper` as the per-load loader. Entry parcel is `src/shipcars-chase-driver-tracking.tsx`; `src/root.component.tsx` is the mounted root.

The stack has been modernized well beyond the old shadow: it's now on **pnpm 11 / Node ≥22** (not npm), **axios 1.17**, and — most importantly — it consumes the fleet's shared **`@ship-cars-usa/lm-*` packages** (published from `ui-commons`): `lm-components` (UI + `SCProvider`, `Alert`, `toast`, `style.css`), `lm-data-layer` (API clients / React Query hooks), `lm-types`, `lm-utilities`, `lm-global-config` (env config), and `lm-import-map-overrides` (the `OverrideWidget`). It no longer depends on `@ship-cars-usa/ui-commons` as a single package — that repo is now the Nx monorepo that ships these `lm-*` libs.

`src/root.component.tsx` wires a `QueryClientProvider` (retry:1, refetch-on-focus off, toast-based error surfacing) inside `SCProvider` inside a `FingerprintProvider` (`@fingerprint/react` 3.0, keyed by `environment.FINGERPRINT_API_KEY`). Mixpanel (`src/constants/mixpanel.ts`, `src/utils/analyticsUtils.ts`) provides analytics. Dev port `:7150`.

**README is still template-leftover** ("It should handle the posting functionality" is unedited create-single-spa scaffolding, and it lists a nonexistent `pnpm build:webpack` — the real build script is `pnpm build`).

## How it fits

- **Consumes API of:** driver-load / chase-tracking backends **via `@ship-cars-usa/lm-data-layer` hooks**, not local `src/services/` (there is no services dir). Concrete base URLs come from `lm-global-config`'s `environments.chaseDriverTracking()` (`src/environments/*.environment.ts`), not from this repo. (Which backend the tracking hooks resolve to is owned by `lm-data-layer` — assumed load/location backends.)
- **Publishes events to:** none.
- **Owns data store:** none (browser-only; TanStack Query cache).
- **Loadmate-shell coupling:** mounted as a single-spa app-parcel into the parent Loadmate shell; not standalone-deployed (unlike its public tracking siblings).

## Build / test / run
```
corepack enable                 # pnpm 11, Node ≥22
pnpm install                    # needs user-level ~/.npmrc tokens for FontAwesome + GitHub Packages
pnpm start                      # webpack serve --port 7150 --env isLocal
pnpm start:https                # HTTPS dev server (webpack.https.mjs)
pnpm build                      # webpack --mode=production
pnpm analyze                    # bundle-size analysis
pnpm test                       # jest
pnpm typecheck                  # tsc
```

## Key abstractions

- `src/shipcars-chase-driver-tracking.tsx` — single-spa parcel entry (`bootstrap`/`mount`/`unmount`).
- `src/root.component.tsx` — root: QueryClient + `SCProvider` + `FingerprintProvider` + `OverrideWidget` (dev/qa only) + React Query Devtools.
- `src/pages/ChaseDriverLoad/`, `LoadSummaryView/`, `PaperFlowLoad/`, `LoadRouteWrapper/` — the load views.
- `src/router/router.tsx`, `src/router/routes.ts` — react-router 7 route table (`AppRouter`).
- `src/environments/` — env files; `environment.ts` re-exports `environments.chaseDriverTracking()` from `lm-global-config`.
- `src/utils/` — `mapVehicleStatus`, `buildAddress`, `parseShippingItem`, `analyticsUtils` (Mixpanel); each with colocated tests.
- `src/types/loadActions.ts`, `vehicleActions.ts` — local domain types (broader types come from `lm-types`).

## Don't-do-here / gotchas

- **README is stale template scaffolding.** Don't trust its description or its `pnpm build:webpack` line; the app is driver-load tracking and builds with `pnpm build`.
- **Shared logic lives in `lm-*`, not here.** API hooks (`lm-data-layer`), UI primitives (`lm-components`), env config (`lm-global-config`) are all in the `ui-commons` Nx monorepo. A change to a shared button/hook/type is made there and pulled in via `pnpm add ... @latest` (`update:lm-packages` script), not edited locally.
- **pnpm 11 / Node ≥22 only.** Don't `npm install`. Private packages (FontAwesome, GitHub Packages) require user-level `~/.npmrc` tokens, not the committed `.npmrc`.
- **axios 1.17 with no default `timeout`** is the fleet default — a hung backend hangs the request.
- **Fingerprint Pro on the app root** — `FINGERPRINT_API_KEY`/endpoint must be set per env or the provider fails to init.
- **Mounted by the Loadmate shell**, not standalone; import-map overrides (`OverrideWidget`) are gated to local/dev/qa.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/ui-commons.md` — the Nx monorepo that publishes the `@ship-cars-usa/lm-*` packages this app depends on.
- `~/projects/codebase-map/repos/driveaway-public-tracking-frontend.md` — sibling tracking MFE (same `lm-*` + single-spa generation; public-facing).
- `~/projects/codebase-map/domains/operations.md`.
