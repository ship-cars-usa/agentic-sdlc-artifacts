---
repo: public-root-app-frontend
path: ~/projects/ship-cars-usa/public-root-app-frontend
stack: TypeScript 4.3 / single-spa 5.9 root + single-spa-layout 2.1 / Webpack 5.51 / no MUI (orchestrator only); GTM + Rollbar snippets baked into the shell
domain: platform
shape: single-spa **root config** (not an app-parcel)
last-synced-commit: 55ce49ce868ba6bf09af95233629a0c18247390f
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# public-root-app-frontend

## What it is
**The single-spa root-config orchestrator for the public-facing Ship.Cars site** (`public.ship.cars` / `public-dev.ship.cars`). It constructs applications + routes from a declarative `single-spa-layout` HTML file, `System.import`s each app-parcel from the import-map, activates the layout engine, and `start()`s single-spa. It also carries the site-wide **Google Tag Manager** and **Rollbar** bootstrap snippets (`src/config/`), which is why the shell — not the parcels — owns page-level analytics/error chrome.

**Distinct from the authenticated Loadmate-app shell**, which mounts the logged-in MFEs. This repo is the **public, no-auth** counterpart.

Listens at `:7120` in dev. **Port collision with `inventory-frontend` (also 7120)** — never run both locally at once.

## How it fits

- **Mounts (per `src/microfrontend-layout.html`, current):**
  - `/app/chase-driver` → `@ship-cars/chase-driver-tracking` (`chase-driver-tracking-frontend`)
  - `/app/gallery` → `@ship-cars/public-gallery` (`public-gallery-frontend`) — registered with `customProps.code = location.hash.slice(1)`
  - `/app/epod/interstitial` → `@ship-cars/public-common` (`public-common-frontend`)
  - `/app/driveaway` → `@ship-cars/driveaway-public-tracking-app` (`driveaway-public-tracking-frontend`)
  - **default route** → `@ship-cars/public-tracking-app` (`public-tracking-frontend`)
  - (Correction vs. previous shadow: the mounted set is now these five, not just public-tracking + driveaway.)
- **Consumes API of:** none directly. Each mounted parcel makes its own REST calls.
- **Publishes events to:** none.
- **Owns data store:** none.

## Build / test / run
```
npm install
npm run start        # webpack serve --port 7120 --env environment=local  -> http://localhost:7120/
npm run build        # webpack --mode=production
npm run lint         # eslint app/src root/src --ext js,ts,tsx
npm run format / check-format
```
Note: `pre-commit` shells out to a sibling checkout's `pretty-quick` binary (`ship-cars-public-tracking-frontend/node_modules/.bin/pretty-quick`) — brittle if that sibling isn't present.

## Key abstractions

- `src/shipcars-public-root-app.ts` — root-config entry: `constructRoutes(microfrontendLayout)` + `constructApplications({ loadApp: ({name}) => System.import(name) })` + `constructLayoutEngine`, then `registerApplication` per app (special-casing `public-gallery` to inject `customProps.code` from the URL hash), `layoutEngine.activate()`, `start()`.
- `src/microfrontend-layout.html` — declarative `single-spa-layout` route→parcel map (the source of truth for what mounts where).
- `src/config/googletagmanager.config.js` — GTM container `GTM-MLLB7PT` bootstrap.
- `src/config/rollbar.config.js` — Rollbar snippet + `_rollbarConfig` (ignores 401s, honors `window.rollbarEnabled` / `window.deploymentInstance`).
- `src/index.ejs` — HTML template rendered into the deployed `index.html` (loads the import-map + config snippets).
- `src/declarations.d.ts`, `webpack.config.js` (uses `webpack-config-single-spa-ts`, not the react variant).

## Don't-do-here / gotchas

- **Route changes = edit `microfrontend-layout.html` + rebuild**, not just config. The layout is declarative HTML, parsed at bootstrap.
- **Older single-spa generation.** `single-spa@5.9.3` / `single-spa-layout@2.1.0` / `webpack@5.51.1` / TypeScript 4.3 / ESLint 7 — well behind the parcels it mounts (public-tracking-frontend is now single-spa 6). Mixed v5-root + v6-parcel in the import-map generally works but can produce subtle mount-order edge cases; confirm before assuming the root will be upgraded.
- **Port 7120 collides with `inventory-frontend`.** Override one locally.
- **README is partially TODO** ("Deploy - TODO", "Import map Overrides - TODO") — operational runbook incomplete; validate any deploy / import-map-override step fresh.
- **Analytics/error chrome lives here, once, for all public parcels** (GTM + Rollbar in `src/config/`). Don't duplicate GTM/Rollbar init inside a mounted parcel — it double-fires.
- **No `axios` / MUI at this level** — root configs are deliberately minimal; UI lives in the parcels.
- **Brittle `pre-commit`** depends on a sibling `public-tracking-frontend` checkout for its `pretty-quick` binary.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/public-tracking-frontend.md` — default-route parcel.
- `~/projects/codebase-map/repos/driveaway-public-tracking-frontend.md` — `/app/driveaway` parcel.
- `~/projects/codebase-map/repos/chase-driver-tracking-frontend.md` — `/app/chase-driver` parcel.
- `~/projects/codebase-map/repos/public-gallery-frontend.md` — `/app/gallery` parcel (hash-code customProp).
- `~/projects/codebase-map/repos/public-common-frontend.md` — `/app/epod/interstitial` parcel / shared public chrome.
- `~/projects/codebase-map/domains/platform.md`.
