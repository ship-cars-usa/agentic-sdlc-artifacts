---
repo: ui-components-frontend-package
path: ~/projects/ship-cars-usa/ui-components-frontend-package
stack: TypeScript / React / Vite (React + TS Vite template per README)
domain: platform
shape: **standalone version** of `@ship-cars-usa/ui-components-frontend-package` (version 1.2.0) — older sibling of the monorepo-housed package
last-synced-commit: c3f0c61cdfbb3e4a018e67c85c03665299fe0082
last-synced-date: 2026-05-12
maintainer: unknown
status: seed
---

# ui-components-frontend-package

## What it is
**Standalone-repo version** of `@ship-cars-usa/ui-components-frontend-package`: shared UI primitives (theme, icons, fonts) per the `carrier-packages-frontend` monorepo README. **This standalone is at version 1.2.0**; the monorepo's copy is at **1.3.4**.

Smaller surface than `ui-commons` — primarily theme + icon + font primitives rather than full Alert / Avatar / Button-style components. Pairs with `ui-commons` (full components) and `ctmslb-components-frontend-package` (CTMS / Loadboard-specific).

README is the default Vite + React + TS template intro (`React + TypeScript + Vite`) — actual content lives in `src/` (theme files, icon components, font config).

Last commit 2026-03-13 (`SCP-0000: IconButton ripple borderRadius`) — actively-touched but on a slow cadence.

## How it fits

- **Dual-existence with the monorepo** — see `carrier-packages-frontend`.
- **Pairs with:**
  - `globals-frontend-package` — primitive types + constants.
  - `entities-frontend-package` — entity types.
  - `ctmslb-components-frontend-package` — CTMS / Loadboard-specific components built on these primitives.
  - `ui-commons` — older / heavier shared component library (Gulp-built).

## Build / test / run
```
npm install
npm run dev      # Vite dev server
npm run build
```

## Don't-do-here / gotchas

- **Same dual-existence + manual-version-bump caveat** as `globals-frontend-package` / `entities-frontend-package`.
- **Theme primitives are load-bearing.** A breaking change here forces visual regression risk across every MFE that uses the shared theme. Coordinate with consumers.
- **`IconButton ripple borderRadius` commit** suggests fine-grained UI-tuning churn. The library cares about pixel-perfect behavior.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/carrier-packages-frontend.md` — Nx monorepo (newer version).
- `~/projects/codebase-map/repos/ui-commons.md` — older / heavier sibling library (Gulp-built; broader component surface).
- `~/projects/codebase-map/repos/pricing-frontend-components-package.md` — domain-specific Rollup-built library.
- `~/projects/codebase-map/domains/platform.md`.
