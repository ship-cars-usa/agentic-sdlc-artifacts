---
repo: inspection-requirements-frontend
path: ~/projects/ship-cars-usa/inspection-requirements-frontend
stack: TypeScript / React 18.3 / single-spa 5.9 / Webpack 5.75 / MUI 5.15 / react-error-boundary
domain: platform
shape: single-spa app-parcel (older generation)
last-synced-commit: 408055a28bf4380d87c65d755648e1973e3a1532
last-synced-date: 2026-05-12
maintainer: unknown
status: seed
---

# inspection-requirements-frontend

## What it is
**Inspection-requirements configurator** — single-spa MFE for defining what photo / damage / data requirements apply to a vehicle inspection (which photos must be captured, what damage codes are valid, etc.). Likely consumed by the ePOD apps + dispatcher UI. Dev port 8081. **Node 16.x per README** (outdated).

Last commit 2025-10-10 (Claude-config sweep only) — content is older, lower-touch than the other MFEs in this batch.

## How it fits

- **Consumes API of:** likely `inventory-backend` (per `InspectionConfigurationDto` / `InspectionConfigurationCustomPhotosDto` in `models-lib`) and any service that owns inspection-config persistence. Confirm by reading `src/`.
- **Loadmate-shell coupling:** mounted by `platform-frontend`'s root config.
- **Drives configuration consumed by:** `epod-android` + `epod-ios` (the actual inspection-capture apps). The "what to inspect" decision lives here; the "do the inspection" lives in mobile.

## Build / test / run
```
npm install         # README says Node 16.x — use Node 22 to match fleet
npm run start       # webpack serve --port 8081
npm run build:webpack
```

## Don't-do-here / gotchas

- **Low-touch MFE.** Last real-code commit predates 2026; current commit is just Claude config. Behavior may not have been exercised under recent stack changes.
- **README claims Node 16.x** — outdated.
- **Older single-spa generation.**
- **Inspection-requirement edits drive ePOD app behavior in the field.** A misconfiguration here (e.g. a required photo step that doesn't render correctly) directly affects driver UX on `epod-android` / `epod-ios`. Coordinate inspection-config schema changes with mobile.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/epod-android.md` / `epod-ios.md` — consumers of the inspection configurations defined here.
- `~/projects/codebase-map/repos/inventory-backend.md` — likely primary backend.
- `~/projects/codebase-map/repos/models-lib.md` — `InspectionConfigurationDto` lives there.
- `~/projects/codebase-map/repos/platform-frontend.md` — Loadmate root config.
- `~/projects/codebase-map/domains/platform.md`.
