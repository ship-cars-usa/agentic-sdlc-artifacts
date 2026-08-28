---
repo: uship-backoffice-frontend
path: ~/projects/ship-cars-usa/uship-backoffice-frontend
stack: TypeScript / React 18.2 / **CRA 5 + craco-less** / react-router-dom 6.14 / axios 1.4 / react-ace / react-json-view
domain: platform
shape: standalone CRA-based admin SPA
last-synced-commit: 5243ecf51bd082fb06a5408dd423d15357a0d9e9
last-synced-date: 2026-05-12
maintainer: unknown
status: seed
---

# uship-backoffice-frontend

## What it is
**uShip BackOffice Frontend** — admin UI for `uship-backoffice-backend`. Built with **Create React App 5 + craco-less** for less-CSS support. Older stack than `backoffice-frontend` (which is on Vite 6 + React 19). Standalone nginx-served container.

Per README: requires `.env.local` with `REACT_APP_API_URL=http://localhost:9001` for local dev.

Last commit 2026-03-31 (`Fix Underbidding Policy`) — paired with the same-named commit in `uship-backoffice-backend`.

## How it fits

- **Consumes API of:** `uship-backoffice-backend`.
- **Owns data store:** none.
- **Auth:** through the backend.

## Build / test / run
```
npm install
npm run start         # craco start (CRA-based)
npm run build
```

## Don't-do-here / gotchas

- **CRA 5 is deprecated** as of 2023. Future major work here is a hidden cost — bumping to Vite 6 (matching `backoffice-frontend`) requires a full build-config rewrite.
- **`craco-less`** is a CRA-config-override layer for Less support. Most modern bundlers handle Less natively.
- **React 18.2** (vs. `backoffice-frontend`'s React 19) — stack drift between the two admin apps.
- **`react-ace` + `react-json-view`** — in-app code/JSON editors, same as `backoffice-frontend`. Admin tools heavily use raw-data viewing.
- **Coordinate with `uship-backoffice-backend`.** Schema or endpoint changes there propagate here.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/uship-backoffice-backend.md` — companion backend.
- `~/projects/codebase-map/repos/backoffice-frontend.md` — sibling on the modern Vite + React 19 stack.
- `~/projects/codebase-map/domains/platform.md`.
