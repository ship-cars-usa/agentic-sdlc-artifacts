---
repo: fe-exercise-inventory-api
path: ~/projects/ship-cars-usa/fe-exercise-inventory-api
stack: Node / TypeScript 5.8 / Express 5 / Mongoose 8.16 / Jest 30 / mongodb-memory-server
domain: listings-trade
shape: single-module
last-synced-commit: 77ba5a3e64175fa37c39dc45ea0d9e6f22a248f9
last-synced-date: 2026-05-12
maintainer: unknown
status: seed
---

# fe-exercise-inventory-api

## What it is
**Hiring artifact — not a production service.** A reference Vehicle Inventory REST API used as the backend half of the Ship.Cars Front-End Developer coding challenge (see sibling repo `fe-exercise-inventory-ui` for the candidate-facing README). Express 5 + Mongoose + TypeScript with a controllers / routes / middleware / data / config layout. Ships its own Jest test suite and `mongodb-memory-server` for in-memory MongoDB during tests. SWAGGER.md documents the API surface.

The repo is **not deployed to any Ship.Cars production environment**. It exists so that interview candidates have a working backend to point their React UI at when completing the take-home exercise. Last commit 2025-07-28.

## How it fits

- **Not part of any production data flow.** Doesn't talk to any fleet service.
- **Standalone:** runs locally against an embedded or local MongoDB.

## Build / test / run
```
npm install
npm run dev              # nodemon hot-reload
npm run build            # tsc
npm run lint             # type-check
npm test                 # Jest with in-memory MongoDB
```

## Key abstractions

- `src/server.ts` + `src/app.ts` — Express bootstrap.
- `src/routes/` — REST route definitions.
- `src/controllers/` — handler logic.
- `src/middleware/` — Express middleware.
- `src/data/` — Mongoose models / repositories.
- `src/config/` — app config.
- `src/swagger/` — OpenAPI spec source.
- `SWAGGER.md` — markdown copy of the API spec for candidates.

## Don't-do-here / gotchas

- **Don't pattern-match production services after this repo.** Production fleet services are Quarkus (Java) or Spring Boot (Java); the only Node/TypeScript backend in the active production fleet is `home-delivery-backend`. This Express + Mongo stack appears nowhere else in the production fleet.
- **No Ship.Cars-specific data or credentials** should be added here. The repo is shared with external candidates (or is on a public-ish GitHub org).
- **Currently sits in the `listings-trade` domain** by name-match (`inventory`). Consider re-domain to `infrastructure` or marking as a hiring artifact in the next infrastructure-triage refresh.
- **`Ignore photos`** as the last commit message — probably a `.gitignore` tweak so candidate uploads don't get committed. Don't accidentally remove that ignore rule.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/fe-exercise-inventory-ui.md` — the candidate-facing README that pairs with this API.
- `~/projects/codebase-map/relations/infrastructure-triage.md` — flag both `fe-exercise-*` repos as hiring artifacts on next refresh.
- `~/projects/codebase-map/domains/listings-trade.md`.
