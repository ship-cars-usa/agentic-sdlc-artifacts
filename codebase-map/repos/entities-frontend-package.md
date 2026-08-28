---
repo: entities-frontend-package
path: ~/projects/ship-cars-usa/entities-frontend-package
stack: TypeScript / React / Vite 5.2 / vitest
domain: platform
shape: **standalone version** of `@ship-cars-usa/entities-frontend-package` (version 16.36.0) — older sibling of the monorepo-housed package
last-synced-commit: 2e437f267587786eedb472bb2c6abaf908c132f9
last-synced-date: 2026-05-12
maintainer: unknown
status: seed
---

# entities-frontend-package

## What it is
**Standalone-repo version** of `@ship-cars-usa/entities-frontend-package`: entity models, Zod / Yup schemas, Redux actions, Socket.IO event listeners — the typed-data layer that Loadmate / public MFEs import. **This standalone is at version 16.36.0**; the same-named package inside the `carrier-packages-frontend` Nx monorepo is at **16.37.6** — 1-2 patch versions ahead.

Highest version number among the four `*-frontend-package` siblings (16.x) — implies the most churn / most API evolution.

Recent commit (`SCP-14309: Add parse DS actions`) suggests the same DealerSocket-removal work as `carrier-order-importer-frontend` (commit `SCP-14309: Remove ds fallback` from the same date). Coordinated cross-repo change.

Last commit 2026-04-30.

## How it fits

- **Dual-existence with the monorepo** — see `carrier-packages-frontend`.
- **Notable contents:** "entity models, schemas, actions, sockets" per the monorepo README. The **Socket.IO event listeners here are how non-MFE-resident socket events flow through the typed layer** — pair with `socket-server` + `socket-server-old`.
- **THE API CONDUIT for the carrier MFE surface.** Grep on 2026-05-12 enumerated **~100 distinct `/api/...` endpoint paths declared inside this package** — every Loadmate / carrier MFE that imports `actions/*` or `models/*` from here transitively makes calls to this set. The endpoints split cleanly along the fleet's URL conventions:
  - **Django (`platform-backend`) — unversioned, trailing slash:** `/api/loads/`, `/api/orders/`, `/api/postings/` (unversioned), `/api/negotiations/`, `/api/offers/`, `/api/companies/`, `/api/carriers/`, `/api/carrier_companies/`, `/api/network_companies/`, `/api/shipper_companies/`, `/api/contacts/`, `/api/users/`, `/api/vehicles/`, `/api/trips/` (unversioned), `/api/invoices/`, `/api/revised_invoices/`, `/api/load_cancel_reasons/`, `/api/load_decline_reasons/`, `/api/quickbooks_default/`, `/api/shipper_stats/`, `/api/reports/templates/`, `/api/extra/loads/`, `/api/location_items/`, `/api/location_requests/`.
  - **Java / Quarkus — versioned `/api/<svc>/v<N>/`:** `/api/attachment/v1/`, `/api/bookmarks/v2`, `/api/cube/ctms/v1/`, `/api/cube/loadboard/v3,v4/`, `/api/integrations/v1/`, `/api/load-recommender/v1/`, `/api/loadboard/v3/`, `/api/loadmate/invoices/v1/`, `/api/location-provider/v2/`, `/api/location_tracking/`, `/api/metadata/v1/`, `/api/negotiations-router/v1/`, `/api/payment/v1/`, `/api/saved-search/v3/`, `/api/tripplanner/v1/`, `/api/usermanagement/v2,v3/`.
- **Direct consequence:** any field rename in `models/loads`, `models/postings`, `models/users`, `models/companies`, etc. simultaneously affects Django response shapes and Java DTO contracts. Changes to entities defined here cascade fleet-wide on FE rebuild — and they cannot be safely landed without coordinating both backend ecosystems.

## Build / test / run
```
npm install
npm run dev
npm run test
npm run test:coverage
```

## Don't-do-here / gotchas

- **Same dual-existence + manual-version-bump caveat as `globals-frontend-package`.**
- **The Socket.IO event-listener contract is shared with `chat-frontend` / `trip-planner-frontend` / `loadboard-frontend`** etc. — those MFEs subscribe via DOM CustomEvents whose payload shapes are presumably typed by this package's `actions/sockets` modules. A field rename here propagates through every MFE that reads typed socket events.
- **The `Add parse DS actions` commit + sibling `Remove ds fallback` in `carrier-order-importer-frontend`** = coordinated DealerSocket-source removal. Don't accidentally re-introduce DealerSocket-specific actions without coordinating with the carrier-order-importer flow.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/carrier-packages-frontend.md` — Nx monorepo (newer version of this package).
- `~/projects/codebase-map/repos/platform-backend.md` — **the Django monolith this package's unversioned `/api/<noun>/` actions target**.
- `~/projects/codebase-map/repos/api-gateway.md` — the Go/Fiber proxy that routes the `/api/...` calls declared here.
- `~/projects/codebase-map/repos/globals-frontend-package.md` — companion package; its `utils/errors.ts` exports both `parseDjangoErrorMessage` and `parseJavaErrorMessage`, confirming the dual-backend reality this package's API surface implies.
- `~/projects/codebase-map/repos/socket-server.md` / `socket-server-old.md` — the WebSocket layer this package types.
- `~/projects/codebase-map/repos/carrier-order-importer-frontend.md` — the consumer that triggered the `SCP-14309` cross-repo change.
- `~/projects/codebase-map/repos/ctms-frontend.md` / `loadboard-frontend.md` / `trip-planner-frontend.md` — the carrier MFEs that import this package and transitively make all the calls.
- `~/projects/codebase-map/domains/platform.md`.
