---
repo: ctmslb-components-frontend-package
path: ~/projects/ship-cars-usa/ctmslb-components-frontend-package
stack: TypeScript / React / Vite (React + TS Vite template per README)
domain: platform
shape: **standalone version** of `@ship-cars-usa/ctmslb-components-frontend-package` (version 1.28.0) — older sibling of the monorepo-housed package
last-synced-commit: 6f9975812d39c2c8f9e2745b25a444905c81158b
last-synced-date: 2026-05-12
maintainer: unknown
status: seed
---

# ctmslb-components-frontend-package

## What it is
**Standalone-repo version** of `@ship-cars-usa/ctmslb-components-frontend-package`: **CTMS + Loadboard-specific React components** per the `carrier-packages-frontend` monorepo README. **This standalone is at version 1.28.0**; the monorepo's copy is at **1.30.0**.

Scoped to the CTMS + loadboard surfaces (`loadboard-frontend`, `inventory-frontend`, plus possibly `posting-frontend`) — the "domain-aware" component layer that builds on the foundational `ui-components-frontend-package` primitives.

README is the default Vite + React + TS template intro. Actual content lives in `src/` (CTMS-specific tables / filters / cells / loadboard-specific widgets).

Last commit 2026-04-28 (Claude-config sweep) — content older but still on the active dev path.

## How it fits

- **Dual-existence with the monorepo** — see `carrier-packages-frontend`.
- **Pairs with:**
  - `ui-components-frontend-package` — primitive theme + icons; this package builds on those.
  - `loadboard-frontend` / `inventory-frontend` — primary consumers.
- **CTMS coupling:** the "CTMS" in the name refers to the legacy CTMS system. As CTMS is retired (per `negotiations-router`'s seed flagging CTMS as deprecated), the CTMS-specific components here become migration debt.

## Build / test / run
```
npm install
npm run dev
npm run build
```

## Don't-do-here / gotchas

- **Same dual-existence + manual-version-bump caveat** as the other `*-frontend-package` standalones.
- **CTMS legacy coupling.** When CTMS is fully retired, the CTMS-specific components in this package need to be either dropped (with corresponding consumer cleanup) or kept for the Loadboard-only side. Coordinate with `negotiations-router`'s retirement plan.
- **Smaller than `entities-frontend-package`** (in terms of version-number churn — 1.28.0 vs 16.36.0) — implies less API breakage history but still actively used.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/carrier-packages-frontend.md` — Nx monorepo (newer version).
- `~/projects/codebase-map/repos/ui-components-frontend-package.md` — primitive sibling.
- `~/projects/codebase-map/repos/loadboard-frontend.md` / `inventory-frontend.md` — primary consumers.
- `~/projects/codebase-map/repos/negotiations-router.md` — CTMS retirement plan (this package's CTMS components are downstream).
- `~/projects/codebase-map/domains/platform.md`.
