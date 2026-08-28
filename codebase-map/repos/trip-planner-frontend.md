---
repo: trip-planner-frontend
path: ~/projects/ship-cars-usa/trip-planner-frontend
stack: TypeScript 4.9 / React 18.3 / single-spa 5.9 + single-spa-react 5.1 / Webpack 5.75 / MUI 5.16 + @mui/lab 5-alpha + @mui/x-date-pickers-pro 6.19 / Redux (react-redux 8 + redux-thunk) + Normalizr / @dnd-kit (drag-drop) / @vis.gl/react-google-maps / @unleash/proxy-client-react / formik / axios 0.21 / Node 18+
domain: operations
shape: single-module (single-spa app-parcel)
last-synced-commit: bdf2a0958e927300e41a98d0a926ea54eb5c3d8c
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# trip-planner-frontend

## What it is
`@ship-cars/trip-planner-frontend` — the **single-spa micro-frontend** for the Trip Planner feature in the Loadmate carrier shell. Lets users build / edit / dispatch multi-stop trips that string together loads, vehicles, drivers, and customers, with drag-and-drop stop ordering (`@dnd-kit`) and a Google Maps route view (`@vis.gl/react-google-maps` + marker clusterers). Backend is `trip-planner` (Quarkus).

App-parcel mounted by the parent Loadmate shell. Redux store (normalized via `normalizr`) holds trip + load + vehicle + user + company + addon + offer + negotiation entities. Updates flow in via two paths: REST (initial load + writes) and a **DOM-CustomEvent socket bridge** (`document.addEventListener('new_socket_events.trip', …)`) for live invalidation when the upstream WebSocket emits a `TRIP_EVENT`. Feature flags are read via `@unleash/proxy-client-react`. Recently migrated to MUI's experimental theme palette tokens (SCP-14849) and bumped `@ship-cars-usa/entities-frontend-package` to v20 (SCP-15043).

## How it fits

- **Consumes API of (in-repo `/api/...` paths, plus the broad set via `entities-frontend-package`):**
  - **`platform-backend` (Django monolith)** — unversioned DRF paths: `/api/loads/`, `/api/trips/${id}`, `/api/trips/${id}/assign/`, `/api/trips/${id}/reassign/`, `/api/users/`, `/api/extra/loads/next_shipper_id/`. The legacy load/trip/user surface still lives on Django.
  - **`trip-planner` (Quarkus)** — `/api/tripplanner/v1/trips/`, `.../trips/${id}/loads/${id}`, `.../trips/${id}/loads/${id}/transfer`, `.../trips/${id}/optimize-route`, `.../trips/${id}/postings`. The modern trip surface; runs in parallel with the Django one.
  - Plus the broad set via `@ship-cars-usa/entities-frontend-package` v20 (cube, negotiations-router, user-backend, attachment-backend, metadata, …) — same as the other carrier MFEs.
- **Dual-surface notice:** `/api/trips/${id}` (Django) and `/api/tripplanner/v1/trips/${id}` (Quarkus) **both exist** in this MFE — trip data is dual-written to PG + CTMS via the sync path. Touching either side without the other risks divergence.
- **URL-pattern decoder:** unversioned `/api/<noun>/` → `platform-backend`; `/api/<service>/v<N>/...` → Java/Quarkus. `api-gateway` (Go/Fiber) routes by prefix.
- **Publishes events to:** none directly. Redux state is local, browser-only.
- **Owns data store:** none — ephemeral Redux store.
- **Socket bridge:** subscribes to `document` CustomEvents under `new_socket_events.{trip,company,user,load}` (`src/constants/sockets.ts`, `src/sockets/*.ts`). The parent shell owns the WebSocket connection to `socket-server`; this MFE never opens one.

## Build / test / run
```
npm install                   # Node >= 18.12.1
npm run start                 # webpack serve --port 8082
npm run build                 # concurrently build:webpack + build:types (tsc)
npm run build:webpack         # webpack --mode=production
npm run analyze               # bundle-size analysis
npm test                      # cross-env BABEL_ENV=test jest
```
single-spa dev workflow: serve locally, override the import-map entry in a deployed QA shell to point at `https://localhost:8082`.

## Key abstractions

- `src/shipcars-trip-planner.tsx` — single-spa lifecycle exports via `single-spa-react`, with an error boundary rendering `<div>Something went wrong</div>` on unhandled errors.
- `src/root.component.tsx` — top-level React tree; `src/Planner.tsx` — the main Trip Planner page.
- `src/store.ts` — Redux store; holds normalized entities (`companies`, `trips`, `tripLoads`, `users`, `addons`, `loads`, `vehicles`, `negotiations`, `offers`).
- `src/utils/api.ts` — `processApiData(data, schema)` normalizes API responses via Normalizr.
- `src/sockets/{trips,companies,loads,users}.ts` — socket-event subscribers; on each event, dispatch `SET_OUTDATED` so the next render re-fetches.
- `src/parcels/OrderImporterDialog.tsx` — order-import sub-parcel; `src/dialogs/` — modal dialogs.
- `src/constants/{sockets,actions,routes,colors,errors,map,queryParams}.ts` — typed constants.
- `src/utils/maps.tsx` + `@vis.gl/react-google-maps` + `@google*`/`@googlemaps/markerclusterer` — Google Maps route rendering + clustering.

## Don't-do-here / gotchas

- **`axios 0.21.1` is a known-vulnerable version** (CVE-2023-45857 SSRF in 0.x). Bumping to 1.x is a non-trivial migration (interceptor/config-shape changes). Highest-priority hygiene item.
- **`@mui/lab 5.0.0-alpha.173`** is a pre-1.0 alpha; any feature using it (Timeline/LoadingButton-style) is on an unstable API and must move lock-step with `@mui/material` 5.16.7.
- **`@mui/x-date-pickers-pro` 6.19.9 is a paid MUI X commercial component.** License-key handling is done elsewhere (parent shell / env injection).
- **`single-spa 5.9` + `single-spa-react 5.1` — one major behind the modern shell (single-spa 6).** When the parent shell upgrades, this MFE needs the matching bump; mixed v5+v6 in the import-map can cause subtle mount-order bugs.
- **DOM-CustomEvent socket pattern (shell owns the WebSocket).** If trip events stop arriving, the bug is upstream — check `socket-server` and the shell's bridge, not this repo. Socket subscribers use a module-level `isSubscribed` dedupe guard that can stick `true` after a hot-reload; restart the dev server if subscriptions go missing.
- **Normalizr entity store keys are strings.** Mixing numeric and string IDs in a payload silently breaks normalization (two entries for one logical entity). Any new entity type needs a coordinated `normalizr.schema.Entity` definition.
- **No `timeout` on the axios client** (fleet pattern) — a hung `trip-planner` backend hangs every Redux fetch indefinitely.
- **The error boundary `<div>Something went wrong</div>` is a placeholder** — no visible Sentry/Rollbar capture at the entry point.
- **Recently migrated to MUI experimental theme palette tokens (SCP-14849) and entities v20 (SCP-15043)** — deprecated `colorConstants` were removed; don't reintroduce them.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/trip-planner.md` — the Quarkus backend.
- `~/projects/codebase-map/repos/platform-backend.md` — the Django monolith this MFE still hits for the unversioned `/api/loads/`, `/api/trips/`, `/api/users/` surface (dual-surface origin).
- `~/projects/codebase-map/repos/entities-frontend-package.md` — shared FE library (v20); the bulk of remaining API paths.
- `~/projects/codebase-map/repos/api-gateway.md` — the Go/Fiber proxy routing `/api/<noun>/` (Django) vs `/api/<service>/v<N>/` (Java).
- `~/projects/codebase-map/repos/chat-frontend.md` — sibling MFE; same socket-bridge pattern and axios-timeout gap.
- `~/projects/codebase-map/repos/socket-server.md` — the WebSocket layer the shell bridges from.
- `~/projects/codebase-map/domains/operations.md`.
