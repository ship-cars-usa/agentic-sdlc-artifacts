---
repo: public-common-frontend
path: ~/projects/ship-cars-usa/public-common-frontend
stack: TypeScript / React 18.3 / single-spa-react 5.1 / single-spa 5.9 / MUI 5.16 / react-router 7.6 / Webpack
domain: platform
shape: single-spa app-parcel (companion to `public-root-app-frontend`)
last-synced-commit: a81d4fa3d5804e3ed74621589be166506ae7efe1
last-synced-date: 2026-05-12
maintainer: unknown
status: seed
---

# public-common-frontend

## What it is
**Shared chrome / common parcel** for the public-facing Ship.Cars site. Companion to `public-root-app-frontend`. Provides the layout, header / footer, and any common-across-pages UI elements that should be visible regardless of which public-facing app-parcel is currently mounted.

Stack matches `public-root-app-frontend` (single-spa 5.9 + Webpack 5) but adds React 18.3, MUI 5.16, and `react-router` 7.6. **Requires Node 22.x** per README.

Last commit 2025-10-10 (Claude Code config sweep only) — content is older but actively part of the deployment.

## How it fits

- **Mounted by:** `public-root-app-frontend` (the single-spa root config).
- **Sibling app-parcels:** `public-tracking-frontend`, `driveaway-public-tracking-frontend`. This parcel is the chrome they render inside.
- **Consumes API of:** likely minimal — possibly user-context APIs for public-side personalization. Confirm against `src/containers/`.
- **Publishes events to:** none.
- **Owns data store:** none.

## Build / test / run
```
npm install     # Node 22.x required
npm run start
npm run build
```

## Key abstractions

- `src/shipcars-public-common-frontend.tsx` — single-spa lifecycle entry.
- `src/root.component.tsx` + `root.component.test.tsx` — top-level component + test.
- `src/containers/` — Redux-connected or context-connected containers (likely header, footer, navigation).
- `src/assets/` — images / icons / fonts.
- `src/declarations.d.ts` — TypeScript ambient declarations.

## Don't-do-here / gotchas

- **Older single-spa generation** (5.9 / single-spa-react 5.1). Same caveat as `public-root-app-frontend` — when the modern Loadmate shell upgraded to v6, this public-side cohort stayed on v5.
- **MUI v5** (not v6 like the modern Loadmate MFEs). The public-facing visual language is intentionally separate; no version-coupling required.
- **No `timeout` configured on the axios instance** is the fleet default — verify and add one if any REST calls live here.
- **react-router 7.6** matches `driveaway-public-tracking-frontend` (the only fleet repos using react-router v7).
- **README is sparse** — workflow not documented beyond install / start / build.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/public-root-app-frontend.md` — the single-spa root that mounts this parcel.
- `~/projects/codebase-map/repos/public-tracking-frontend.md` / `driveaway-public-tracking-frontend.md` — sibling public app-parcels.
- `~/projects/codebase-map/domains/platform.md`.
