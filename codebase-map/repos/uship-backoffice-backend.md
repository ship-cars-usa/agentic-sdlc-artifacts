---
repo: uship-backoffice-backend
path: ~/projects/ship-cars-usa/uship-backoffice-backend
stack: Node / TypeScript / NestJS (`nest-cli.json`) / TypeORM 0.3 / migration/ directory
domain: platform
shape: NestJS service (uShip-specific BackOffice admin API)
last-synced-commit: 336735cff4cd127fba10b319b79556b549e798ae
last-synced-date: 2026-05-12
maintainer: unknown
status: seed
---

# uship-backoffice-backend

## What it is
**uShip-specific BackOffice Backend** — sibling of `backoffice-backend`, scoped to admin operations against the **uShip marketplace integration**. Same NestJS + TypeORM 0.3 stack. Per README, local dev uses port-forwards to specific cluster services (e.g. `localhost:9271` for uShip BE itself) configured in `src/config/service/config.service.ts`.

Last commit 2026-03-31 (`LITE-000 Fix Underbidding Policy`) — actively maintained on a slower cadence than `backoffice-backend`.

## How it fits

- **Consumes API of:** `uship-quotes` (the Quarkus uShip integration; per the version-matrix on 3.20.2.2) + likely `posting-backend` / `quote-manager-backend`.
- **Drives:** `uship-backoffice-frontend` admin UI.
- **Owns data store:** Postgres (TypeORM-managed; schema in `migration/`).

## Build / test / run
```
npm install
npm run start:dev
# Local: port-forward per src/config/service/config.service.ts (e.g. kubectl port-forward localhost:9271)
```

## Don't-do-here / gotchas

- **"Underbidding Policy"** is the most recent feature work — admin-side enforcement of marketplace bidding rules. Don't break the policy without coordinating with the uShip business team.
- **Port-forward-based local dev** is fragile. The README's port mappings can drift from actual cluster config; double-check before assuming a connection works.
- **Sibling of `backoffice-backend` with overlapping concerns.** Some code (auth, roles) may be duplicated. Coordinate cross-repo changes.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/uship-backoffice-frontend.md` — companion UI.
- `~/projects/codebase-map/repos/uship-quotes.md` — the production Quarkus service this admin tool drives.
- `~/projects/codebase-map/repos/backoffice-backend.md` — sibling for the main Ship.Cars BackOffice.
- `~/projects/codebase-map/domains/platform.md`.
