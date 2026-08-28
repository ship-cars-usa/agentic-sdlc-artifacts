---
repo: backoffice-backend
path: ~/projects/ship-cars-usa/backoffice-backend
stack: Node / TypeScript / NestJS (`nest-cli.json`) / TypeORM 0.3 / migration/ directory
domain: platform
shape: NestJS service
last-synced-commit: f521aa5dda88b618c441a63bd470c847c59fae01
last-synced-date: 2026-05-12
maintainer: unknown
status: stale
---

# backoffice-backend

## What it is
**Ship.Cars BackOffice Backend** — NestJS internal admin API for managing the Ship.Cars platform. Per the README, handles:

- Centralized authentication / authorization for BackOffice users (separate from Loadmate user auth).
- User, role, and permission management.
- Payment processing.
- Integrations with internal and external services.

Uses **TypeORM 0.3** + TypeScript + `nest-cli.json` (the NestJS canonical layout) + a `migration/` directory for TypeORM migrations. Has `Dockerfile` + `Dockerfile-test`.

Last commit 2026-04-28 (Claude-config sweep) — content older but still in the active dev path.

## How it fits

- **Consumes API of:** the operational backends (`user-backend`, `payment-backend`, etc.) on behalf of BackOffice users.
- **Drives:** the `backoffice-frontend` admin UI.
- **Owns data store:** Postgres (TypeORM-managed; schema in `migration/`). Tracks BackOffice users / roles / permissions / audit.
- **Auth:** likely Keycloak via NestJS OIDC, with a BackOffice-specific realm or role.

## Build / test / run
```
npm install
npm run start:dev
npm run typeorm migration:run
```

## Don't-do-here / gotchas

- **BackOffice access is privileged.** A misconfigured permission check exposes the entire fleet's admin surface. Be conservative when adding new roles.
- **TypeORM 0.3.x** — modern, but TypeORM migrations are notoriously fiddly (auto-generated vs hand-written). Coordinate `migration/` with deploys.
- **NestJS isn't Quarkus / Spring.** Conventions differ — DI, decorators, exception filters, request pipelines. Don't pattern-match the Quarkus services onto this.
- **Pairs with `uship-backoffice-backend`** — separate but parallel admin backend for uShip. Some logic may be duplicated; check both before touching either.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/backoffice-frontend.md` — companion UI.
- `~/projects/codebase-map/repos/uship-backoffice-backend.md` — sibling for uShip.
- `~/projects/codebase-map/repos/user-backend.md` / `payment-backend.md` — primary backends BackOffice talks to.
- `~/projects/codebase-map/domains/platform.md`.
