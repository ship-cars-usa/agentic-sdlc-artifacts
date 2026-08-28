---
repo: pricing-frontend-components-package
path: ~/projects/ship-cars-usa/pricing-frontend-components-package
stack: TypeScript 4.9 / React 18 (peer) / Rollup 3.21 / @mui/material 5.15+ (peer) / axios 0.21.1
domain: pricing-billing
shape: single-module (npm-published library; not deployed)
last-synced-commit: 41b461714739025d556e27d4f78802163aafed78
last-synced-date: 2026-05-12
maintainer: unknown
status: seed
---

# pricing-frontend-components-package

## What it is
**`@ship-cars-usa/pricing-frontend-components-package`** — a Rollup-bundled React component library distributed via internal npm. Provides shared pricing-UI components (carousels via `react-slick`, custom hooks via `react-use`, presumably price-display widgets and form controls) for the pricing-related MFEs. Built as a CJS + ESM + d.ts package; consumed via Yalc (per the README) during local dev.

The library is **not deployed** as a service — it's a compile-time dependency for whichever pricing-side MFE imports it. Last commit 2026-02-17 (`SCP-13861: Use new globals` — likely a refactor to use `@ship-cars-usa/lm-global-config`).

## How it fits

- **Compile-time consumers:** pricing-related MFEs that need shared components. Consumer count unconfirmed at this depth (one or two MFEs, likely `posting-frontend` for quote-acceptance widgets or `contract-pricing-frontend`). Worth a `grep "@ship-cars-usa/pricing-frontend-components-package"` to enumerate.
- **Consumes API of:** none directly (it's a library). React + MUI declared as peers.
- **Publishes events to:** none.
- **Owns data store:** none.

## Build / test / run
```
npm install
npm start                # rollup -c -w (watch mode)
npm run build:clean      # clean + production rollup build

# Local consumer dev via Yalc (per README):
yalc publish              # in this repo
yalc add @ship-cars-usa/pricing-frontend-components-package  # in the consumer repo
```

## Key abstractions

- `src/index.ts` — public exports.
- `src/components/` — exported React components (the library's public API).
- `src/hooks/` — shared hooks.
- `src/entities/` — typed entity shapes used by the components.
- `src/constants/` — shared constants.
- `src/assets/` — image / svg / css resources (svg + postcss rollup plugins handle them).
- `rollup.config.js` — build config (CJS + ESM + d.ts outputs).

## Don't-do-here / gotchas

- **TypeScript 4.9.5** is one major behind current 5.x. Bumping has no obvious blockers but may surface stricter inference issues in consumer apps.
- **`axios 0.21.1` in dependencies** — same CVE caveat as `loadboard-frontend` / `trip-planner-frontend` / `carrier-order-importer-frontend`. Should be peer-or-bumped to 1.x.
- **`react-slick` 0.29.0** is on a 2022-era version (current is 0.30+); minor.
- **React + MUI declared as peers** (`react: ^18.0.0`, `@mui/material: ^5.15.21`). **Pinning to MUI 5 limits adoption by modern-generation MFEs on MUI 6** — when a consumer is on MUI 6 (`posting-frontend`, `inventory-frontend`, `user-frontend`, `contract-pricing-frontend`), peer-dep resolution will warn and you'll have two MUI runtimes in the consumer's bundle. The library needs an MUI v6 peer bump before it can be cleanly consumed by modern MFEs.
- **Yalc-based local dev** is fragile — package version isn't bumped on yalc publish, so consumer caches can hold stale builds. Always `yalc remove` + `yalc add` when iterating.
- **No tests visible** at this level (no `__tests__/` or jest config). Bumping components here without tests means consumer breakage is detected only at consumer-app test time.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/contract-pricing-frontend.md` — likely consumer.
- `~/projects/codebase-map/repos/posting-frontend.md` — possible consumer for quote-related widgets.
- `~/projects/codebase-map/domains/pricing-billing.md`.
