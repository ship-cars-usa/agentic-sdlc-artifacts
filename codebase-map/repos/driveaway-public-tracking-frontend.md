---
repo: driveaway-public-tracking-frontend
path: ~/projects/ship-cars-usa/driveaway-public-tracking-frontend
stack: TypeScript / React 18.3.1 / single-spa 6.0.3 + single-spa-react 6.0.2 / Webpack 5.105 / MUI 6.4 (+ @mui/system 6.4) / react-router 7.17 / TanStack Query 5.95 / axios 1.17 / pnpm 11 (Node ≥22)
domain: operations
shape: single-module (single-spa app-parcel)
last-synced-commit: 5f0a34948d497cddf53ff88c4128fa418cd571c7
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# driveaway-public-tracking-frontend

## What it is
The public-facing **tracking UI for Driveaway** (`@ship-cars/driveaway-public-tracking-frontend`) — the Driveaway-side counterpart to `public-tracking-frontend`. A single-spa app-parcel that lets a Driveaway customer view live status / hand-off details of a vehicle delivery via a public tracking link. Entry parcel is `src/shipcars-driveaway-public-tracking-app.tsx`; the screen tree is `src/DriveawayTracking/` (Status, LoadDetails, Attachments, Actions, Buttons, BackgroundElements) rendered by `src/root.component.tsx` with routes in `src/routes.ts`.

Modernized to match the current Loadmate MFE generation: **pnpm 11 / Node ≥22**, **axios 1.17**, **react-router 7.17**, single-spa 6.0.3 + single-spa-react 6.0.2, MUI 6.4 with an explicit `@mui/system` 6.4. Like `chase-driver-tracking-frontend`, it now consumes the shared **`@ship-cars-usa/lm-*` packages** published from `ui-commons` — data comes from **`driveawayHooks` in `@ship-cars-usa/lm-data-layer/tracking`** (see `DriveawayTracking.tsx`, `DriveawayTrackingHeader.tsx`, `DriveawayTrackingAttachments.tsx`, `DriveawayTrackingActions.tsx`); env config comes from `lm-global-config` via `environments.driveawayTracking()`. Mixpanel analytics via `src/constants/mixpanel.ts` + `src/utils/analyticsUtils.ts`. Dev port `:7130`; standalone-deployed at `public-dev.ship.cars`.

Styling is a mix: several components still carry `Styled*.ts` (emotion/`@mui/system`) files, while newer ones use `.module.scss` — hence the explicit `@mui/system` dep.

## How it fits

- **Consumes API of:** the Driveaway tracking backend **via `@ship-cars-usa/lm-data-layer/tracking` (`driveawayHooks`)** — the actual base URL is resolved by `lm-global-config`. The backend is `driveaway-backend` (Spring Boot; Cloud Vision ID OCR, Fingerprint Pro on the auth path). This repo has no local `src/services/`; the API contract lives in `lm-data-layer`.
- **Publishes events to:** none.
- **Owns data store:** none (browser-only; TanStack Query cache).
- **Deployment surface:** public, no Loadmate-shell auth — access is via `driveaway-backend`'s tracking-link token. No Keycloak hand-off.

## Build / test / run
```
corepack enable                 # pnpm 11, Node ≥22
pnpm install                    # needs user-level ~/.npmrc tokens for FontAwesome + GitHub Packages
pnpm start                      # webpack serve --port 7130 --env isLocal
pnpm start:https                # HTTPS dev server (webpack.https.js)
pnpm build                      # webpack --mode=production
pnpm test                       # jest
pnpm typecheck                  # tsc
# Deployed view: https://public-dev.ship.cars/
```

## Key abstractions

- `src/shipcars-driveaway-public-tracking-app.tsx` — single-spa parcel entry.
- `src/root.component.tsx` — root component (handles `AxiosError` typing at the top level).
- `src/DriveawayTracking/` — the tracking screen: `DriveawayTrackingStatus`, `DriveawayTrackingLoadDetails` (+ `DriveawayTrackingHeader`), `DriveawayTrackingAttachments`, `DriveawayTrackingActions`, `DriveawayTrackingButtons`, `DriveawayTrackingBackgroundElements`.
- `src/common/` — shared UI (`GenericDialog`, `Loading`, `LoadingOverlay`, `StatusUpdateFailed`, `Theme`).
- `src/environments/` — env files; `environment.ts` re-exports `environments.driveawayTracking()` from `lm-global-config`.
- `src/utils/vehicleTransform.ts` — vehicle/status transform (with tests).
- `src/assets/` — brand SVGs (logo, shapes) + status icons (`ArchivedIcon`, `CancelledIcon`, `DeclinedIcon`, `DeliveredIcon`).

## Don't-do-here / gotchas

- **API + shared UI/config live in `lm-*`, not here.** The tracking data contract is `lm-data-layer/tracking`; the env map is `lm-global-config`. Change those in the `ui-commons` monorepo and bump via `update:lm-packages`, not by adding a local services layer.
- **Public, no-auth surface** — access is gated only by `driveaway-backend`'s tracking-link token. Treat the wire format as an externally reachable contract.
- **pnpm 11 / Node ≥22 only** — don't `npm install`; private-registry tokens go in user-level `~/.npmrc`.
- **Two styling conventions coexist** (`Styled*.ts` via `@mui/system` and `.module.scss`). Match the file you're editing; don't assume one convention repo-wide.
- **axios 1.17 with no default `timeout`** — fleet default.
- **Standalone deployment** (own pipeline + runtime import-map caching), unlike the shell-mounted `chase-driver-tracking-frontend`.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/driveaway-backend.md` — the Spring Boot backend (Cloud Vision, Fingerprint Pro) behind the `lm-data-layer/tracking` hooks.
- `~/projects/codebase-map/repos/ui-commons.md` — publishes the `@ship-cars-usa/lm-*` packages this app consumes.
- `~/projects/codebase-map/repos/chase-driver-tracking-frontend.md`, `public-tracking-frontend.md` — sibling tracking MFEs.
- `~/projects/codebase-map/domains/operations.md`.
