---
repo: globals-frontend-package
path: ~/projects/ship-cars-usa/globals-frontend-package
stack: TypeScript / React / Vite 5.2 / vitest / Node 20.x
domain: platform
shape: **standalone version** of `@ship-cars-usa/globals-frontend-package` (version 5.22.0) — older sibling of the monorepo-housed package
last-synced-commit: cd905d790273be6df8a84b82353a5e68d0cdc3fd
last-synced-date: 2026-05-12
maintainer: unknown
status: seed
---

# globals-frontend-package

## What it is
**Standalone-repo version** of `@ship-cars-usa/globals-frontend-package`: shared types, constants, and utilities consumed by Loadmate / public MFEs. **This standalone is at version 5.22.0**; the same-named package inside the `carrier-packages-frontend` Nx monorepo is at **5.27.1** — 5 minor versions ahead.

Same Vite-based build shape as the monorepo's copy. Per the README, every PR must bump `version` in package.json + run `npm install` (manual version-bump workflow, unlike the monorepo's `nx release` automation).

Last commit 2026-04-30 (`SCP-14309: Add places utils`) — still receives commits, but on a slower cadence than the monorepo.

## How it fits

- **Dual-existence with the monorepo.** Same package name, different versions. Consumers can pin to either via npm; whichever they pin determines which they get. **See `carrier-packages-frontend` for the canonical newer version.**
- **Published to:** the same internal npm registry as the monorepo version (it's the same package name).
- **Recent additions:** `places utils` (per the latest commit) — geocoding / location-utility primitives.

## Build / test / run
```
npm install      # Node 20.x required
npm run dev      # Vite dev server (--host)
npm run test     # vitest run
npm run test:watch
npm run test:coverage
```

## Don't-do-here / gotchas

- **Confirm whether this standalone is still the canonical version-bump path** or whether `carrier-packages-frontend` has fully taken over. Both repos receiving April-May 2026 commits suggests **active dual maintenance** — which is itself a gap (changes need to land in both, manually).
- **Manual version-bump workflow** (per README) — easy to forget. The monorepo's `nx release` avoids this.
- **Vite 5.2.6 + Vitest 1.2.1** — slightly behind the monorepo's likely-newer Vite.
- **Don't deepen this seed further** until the dual-existence situation is resolved — wasted effort if this gets retired.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/carrier-packages-frontend.md` — the Nx monorepo housing the newer version + the canonical home for active development.
- `~/projects/codebase-map/relations/infrastructure-triage.md` — flag for re-evaluation on next refresh.
- `~/projects/codebase-map/domains/platform.md`.
