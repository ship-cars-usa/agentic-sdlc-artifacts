---
repo: ui-commons
path: ~/projects/ship-cars-usa/ui-commons
stack: Nx 22.6 monorepo (pnpm 11, Node ≥22) / TypeScript 5.9 / React 18.3 / MUI 6.5 / Vite 7 + vite-plugin-dts / Vitest 4 / Storybook 10.3 (react-vite) / react-hook-form 7.72 + Yup / TanStack Query 5.96 / axios 1.14 / Verdaccio + yalc (local publish)
domain: platform
shape: multi-module (Nx workspace publishing six `@ship-cars-usa/lm-*` packages)
last-synced-commit: 84f6a163662eccd9d3964f61d983feca7e9d55e0
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# ui-commons

## What it is
**`@ship-cars-usa/ui-commons`** is now an **Nx 22 pnpm-workspace monorepo** (root package is private, version `0.0.0`) that builds and publishes the fleet's shared **`lm-*` ("Loadmate") frontend libraries**. This is a complete re-platform from the old single Gulp-built `ui-commons` package: the toolchain is now Nx + Vite 7 (`vite-plugin-dts`) + Vitest 4 + Storybook 10.3, with a **Verdaccio** local registry and **yalc** for local cross-repo dev.

The workspace ships six independently-versioned packages (`pnpm-workspace.yaml`):

- **`@ship-cars-usa/lm-components`** (0.15.x) — React UI library: `SCProvider` (theme/context), `Alert`, `toast`, plus `components/`, `hooks/`, `theme/`, `constants/`, `types/`, and a `style.css`. Exported from `lm-components/src/`. Consumers import `@ship-cars-usa/lm-components` and `@ship-cars-usa/lm-components/style.css`.
- **`@ship-cars-usa/lm-data-layer`** (0.13.x) — API clients + React Query hooks. Exposes sub-path entrypoints, e.g. `@ship-cars-usa/lm-data-layer/tracking` (`driveawayHooks`). This is where MFEs' backend contracts actually live.
- **`@ship-cars-usa/lm-global-config`** (0.6.x) — per-app environment config; exports `environments.<app>()` factories (e.g. `environments.chaseDriverTracking()`, `environments.driveawayTracking()`).
- **`@ship-cars-usa/lm-utilities`** (0.13.x) — utility functions, hooks, and Yup schemas.
- **`@ship-cars-usa/lm-types`** (0.17.x) — shared domain TypeScript type definitions.
- **`@ship-cars-usa/lm-import-map-overrides`** (0.2.x) — the single-spa `OverrideWidget` + import-map override tooling.

Committing is via commitizen (`npm run commit` → conventional `{type}({ticket_id}): {desc}`, ticket from the `LITE-*` branch name); `chore(release): publish` commits (like HEAD) are the automated version bumps. Per-package `CLAUDE.md` files carry library-specific guidance; the repo pulls agents/skills from the `sc-marketplace` plugins.

## How it fits

- **Compile-time consumers (the `lm-*` packages):** the modern Loadmate MFEs. Verified consumers in this batch: `chase-driver-tracking-frontend` and `driveaway-public-tracking-frontend` (both pull `lm-components`, `lm-data-layer`, `lm-global-config`, `lm-types`, `lm-utilities`, `lm-import-map-overrides` and bump them via their `update:lm-packages` script). Other Loadmate MFEs consume the same set — confirm with `grep -rl "@ship-cars-usa/lm-" ~/projects/ship-cars-usa/*/package.json`.
- **This monorepo is the source of truth for shared FE UI, API hooks, env config, and types.** MFEs no longer carry their own `src/services/` — the API contract lives in `lm-data-layer`.
- **Consumes API of:** none directly (it's a library set), but `lm-data-layer` defines the axios/React-Query clients the MFEs use.
- **Publishes events to:** none.
- **Owns data store:** none.

## Build / test / run
```
corepack enable                 # pnpm 11, Node ≥22
pnpm install
pnpm build                      # nx run-many -t build (all libs)
npx nx build lm-components      # build a single lib
pnpm test                       # nx run-many -t test (Vitest)
pnpm lint                       # nx run-many -t lint
pnpm typecheck                  # nx run-many -t typecheck
pnpm storybook                  # nx run lm-components:storybook (Storybook 10.3)
pnpm local-dev                  # scripts/local-dev.sh (Verdaccio-based local publish)
pnpm yalc:dev                   # scripts/yalc-dev.sh (yalc into a consuming MFE)
```

## Key abstractions

- `lm-components/src/` — `SCProvider.tsx`, `index.ts`, `components/`, `hooks/`, `theme/`, `constants/`, `types/`, `utils/`, `google-places.d.ts`, `style.css` output.
- `lm-data-layer/` — API clients + React Query hooks, exposed via sub-path exports (e.g. `/tracking`).
- `lm-global-config/` — `environments.<app>()` config factories.
- `lm-utilities/`, `lm-types/`, `lm-import-map-overrides/` — utilities/Yup, shared types, import-map override widget.
- `nx.json`, `pnpm-workspace.yaml`, `tsconfig.base.json` — Nx + workspace wiring (`defaultBase: master`, `minimumReleaseAge: 1440`).
- `.verdaccio/config.yml` + `scripts/local-dev.sh` / `yalc-dev.sh` — local registry / yalc dev loop.
- `CLAUDE.md` (root) + per-package `CLAUDE.md` — guidance; code style is strict TS (no `any`), 4-space tabs, print width 120, CSS Modules (styled-components deprecated).

## Don't-do-here / gotchas

- **This is an Nx monorepo, not the old Gulp single package.** Ignore any prior "Gulp / Storybook 7.6 / single `src/`" description — build is Nx + Vite, Storybook is 10.3, tests are Vitest.
- **Six separately-versioned packages** — a breaking change to `lm-components`/`lm-types`/`lm-data-layer` forces a coordinated bump across every consuming MFE (each pins exact versions via `--save-exact`). Renamed props/types = fleet-wide recompile.
- **API contracts live here (`lm-data-layer`), not in the MFEs.** Backend-contract changes are made in this repo and propagated by version bump.
- **MUI is 6.5 here** while consumers are on MUI 6.4 — keep peer ranges compatible; type-compat across MUI minors is usually fine but verify on bumps.
- **`minimumReleaseAge: 1440`** (24h) in `pnpm-workspace.yaml` delays picking up freshly published deps — expect a lag when a new lm-* version is published and a consumer tries to install it immediately.
- **Publish is automated** via `chore(release): publish` commits — don't hand-edit package versions; use the commitizen/release flow.
- **CSS Modules only** — styled-components are deprecated per the repo's own code-style rules.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/chase-driver-tracking-frontend.md`, `driveaway-public-tracking-frontend.md` — verified consumers of the `lm-*` packages.
- `~/projects/codebase-map/repos/carrier-packages-frontend.md`, `pricing-frontend-components-package.md` — other shared-FE-package cohorts (distinct from this one).
- `~/projects/codebase-map/domains/platform.md`.
