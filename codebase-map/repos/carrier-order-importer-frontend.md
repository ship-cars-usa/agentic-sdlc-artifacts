---
repo: carrier-order-importer-frontend
path: ~/projects/ship-cars-usa/carrier-order-importer-frontend
stack: TypeScript 4.9 / React 18.3 / single-spa 5.9 + single-spa-react 5.1 / Webpack 5.75 / MUI 5.16 + @mui/x-date-pickers-pro 6.19 / Redux (react-redux 8 + redux-thunk) + Normalizr / formik + yup / @unleash/proxy-client-react / axios 0.21 / Node 22+
domain: listings-trade
shape: single-module (single-spa app-parcel)
last-synced-commit: e8d8eee21d6a8dc241a820b019ba608dbe2df3da
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# carrier-order-importer-frontend

## What it is
`@ship-cars/carrier-order-importer-frontend` — the single-spa MFE that owns the **Carrier Order Importer** flow: a multi-step form letting a Ship.Cars-side user input or import an order on behalf of a carrier, capturing contacts, payment details, vehicle restrictions, close-reasons, and other operational metadata. App-parcel mounted by the Loadmate shell; lower-traffic than `posting-frontend` / `loadboard-frontend`. Mounted at `:8083` in dev.

Form-heavy: **Formik + Yup** (`formik`, `yup` deps; `src/validationSchemas.ts` + `src/formSections.ts`), with dedicated enum config (`contactValues.ts`, `paymentType.ts`, `phoneType.ts`, `closeReason.ts`, `restrictionsType.ts`, `values.ts`). Feature flags via `@unleash/proxy-client-react`. Recently migrated to MUI's experimental theme (SCP-14849), bumped `@ship-cars-usa/entities-frontend-package` to v20 (SCP-15043), added hot-reload (SCP-14917), and updated the pricing dialog (SCP-14468). (Correction vs. previous shadow: Node engine is now **22.14+**, not 18.x; Formik/Yup are confirmed in deps.)

## How it fits

- **Consumes API of (in-repo `/api/...` paths — all Django):**
  - **`platform-backend` (Django monolith)** — `/api/contacts/`, `/api/contacts/${id}/`, `/api/extra/loads/next_shipper_id/`, `/api/vehicles/${id}/`, `/api/vehicles/${vin}/vin/`. This MFE's entire **direct** API surface is Django — the form binds order/contact/vehicle data into the legacy monolith.
  - Plus the broad set via `@ship-cars-usa/entities-frontend-package` v20 (mixed Django + Java: loads, postings, companies, carriers, …). Order creation likely flows through that path.
  - No `/api/command-executor/...`, `/api/usermanagement/...`, or `/api/posting/...` in-repo paths — order creation goes through Django, not the integration backbone.
- **URL-pattern decoder:** unversioned `/api/<noun>/` → `platform-backend` (DRF); `/api/<service>/v<N>/...` → Java/Quarkus. Every direct path here matches the Django convention.
- **Publishes events to:** none directly.
- **Owns data store:** none — ephemeral Redux store (`store.ts` + `actions/reducers/state/entities/`).
- **Loadmate-shell coupling:** single-spa app-parcel mounted by the parent shell via the import-map.

## Build / test / run
```
npm install                   # Node >= 22.14.0
npm run start                 # webpack serve --port 8083
npm run build                 # concurrently build:webpack + build:types (tsc)
npm run build:webpack         # webpack --mode=production
npm run analyze               # bundle-size analysis
npm test                      # cross-env BABEL_ENV=test jest
```

## Key abstractions

- `src/shipcars-carrier-order-importer.tsx` — single-spa lifecycle entry (error boundary → `<div>Something went wrong</div>`).
- `src/root.component.tsx` — top-level React tree (reads Unleash flags).
- `src/CarrierOrderImporter.tsx` — the importer page.
- `src/store.ts` + `src/{actions,reducers,state,entities}/` — Redux state surface (Normalizr-normalized, similar to loadboard-frontend's older pattern).
- `src/validationSchemas.ts` + `src/formSections.ts` — Formik + Yup form definitions.
- `src/{contactValues,paymentType,phoneType,closeReason,restrictionsType,values}.ts` — typed enum lists for the form's selectors.
- `src/parcels/InspectionDialog.tsx` — single-spa sub-parcel (vehicle inspection dialog).
- `src/hoc/`, `src/hooks/`, `src/components/` (incl. `Payment.tsx`, `ContactForm.tsx`), `src/utils/loads.ts`, `src/constants/`, `src/assets/`, `src/theme/`, `src/typings.d.ts`.
- `root.component.test.tsx` — top-level test.

## Don't-do-here / gotchas

- **`axios 0.21.1` — deprecated 0.x line with known CVEs** (same flag as `loadboard-frontend` / `trip-planner-frontend`). Bumping to 1.x is non-trivial (interceptor config-shape changes).
- **`single-spa 5.9` + `single-spa-react 5.1`** — older generation; migration to v6 must be coordinated with the parent shell.
- **`@mui/x-date-pickers-pro` 6.19 is the paid MUI X Pro version** — license-key handling done elsewhere.
- **`react-dropzone` 3.13.2 is ~9 majors behind** the current 14.x, and **`react-number-format` 4.4.1** is a major behind 5.x. File-upload / number-input flows will not survive a dep bump without code changes.
- **Node engine now 22.14+** (README says "install Node 22.x") — previous shadow's Node-18 note is stale.
- **Form harness is Formik + Yup** (`validationSchemas.ts` / `formSections.ts`) — don't assume a bespoke form library; changes must keep the Formik/Yup wiring intact.
- **No `timeout` on the axios instance** — fleet pattern.
- **Recent history to know:** `SCP-14309: Remove ds fallback` removed a DealerSocket import fallback path (older); recent work is the pricing dialog (SCP-14468), experimental-theme migration (SCP-14849), and entities v20 (SCP-15043). If "DS import broke after $DATE" is reported, check the git log around the fallback-removal commit.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/platform-backend.md` — the Django monolith; this MFE's entire direct API surface (contacts/vehicles/extra-loads).
- `~/projects/codebase-map/repos/entities-frontend-package.md` — shared FE library (v20) carrying the rest of the order/load/posting API paths (mixed Django + Java).
- `~/projects/codebase-map/repos/api-gateway.md` — the Go/Fiber proxy routing every `/api/...` call.
- `~/projects/codebase-map/repos/command-executor.md` — inbound integration backend (Acertus / CarsArrive / SuperDispatch / EDI). Not directly called by this MFE.
- `~/projects/codebase-map/repos/posting-backend.md` — eventual downstream of order creation (via Django + Pub/Sub state sync).
- `~/projects/codebase-map/repos/loadboard-frontend.md` / `trip-planner-frontend.md` — sibling MFEs sharing the older single-spa generation.
- `~/projects/codebase-map/domains/listings-trade.md`.
