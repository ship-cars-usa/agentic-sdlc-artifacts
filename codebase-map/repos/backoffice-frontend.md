---
repo: backoffice-frontend
path: ~/projects/ship-cars-usa/backoffice-frontend
stack: TypeScript / React 19.2 / Vite 6 / Ant Design (antd) 6 / axios 1.13 / react-router-dom 7.10 / TanStack Query 5.90 / @react-oauth/google / react-ace (ace-builds) / pnpm 10 (Node >20) / nginx-served
domain: platform
shape: single-module (standalone Vite SPA; not single-spa)
last-synced-commit: f42e75744ee06d3b9a8c9c2ebb137e4f71332138
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# backoffice-frontend

## What it is
**Ship.Cars BackOffice Frontend** (`name: "frontend"`) — the internal admin console for `backoffice-backend`. Standalone Vite SPA on the fleet's **newest React major (19.2)** + **Vite 6**, built and served as its own nginx container (`Dockerfile` + `nginx.conf`); it is **not** single-spa and does not go through the Loadmate shell.

The UI is **Ant Design (antd 6)**, not MUI — distinct from the tracking/Loadmate MFEs. Auth is **Google OAuth** (`@react-oauth/google`): the frontend obtains a Google token and posts it to `backoffice-backend` `/api/auth/login/google`, receiving JWT access + refresh tokens held in storage (`auth.service.ts`); `src/common/axios.ts` runs a 401→refresh-token interceptor with an `X-Refresh-Token-Request` guard against refresh loops. `VITE_API_URL` (from `.env.local`) points at the backoffice backend.

It is a broad CRUD admin surface. `src/crud/` is a **generic table/CRUD framework** (models, schema, registry, resources, services, components) that the per-domain pages build on. `src/pages/` covers a large surface: approvals, ASI, AutoIMS, component-registry, dataone, debugger, deployment-tracking, executive-dashboard, fraud-detector, loadmate, logging-manager, login, metadata, payment, proxy, public-tracking, pubsub-exception-handler, pusher, qa-queue, roles, syncer, user-management, plus standalone pages (Archival, Hasher, LocationProvider, Syncer). `src/services/*.service.ts` (~30 modules) wrap the corresponding backend feature areas; `src/dto/` holds generated-style DTO types mirroring backend contracts. Editors use `react-ace`/`ace-builds` (JSON/SQL/config), `@microlink/react-json-view` (JSON viewing), `@dnd-kit` (drag-ordering), and `react-markdown`+`remark-gfm`.

Per README: Node ≥20, pnpm 10 (`npm i -g pnpm@10`), and a `.env.local` with `VITE_API_URL`. (Note: `package.json` scripts invoke `vite` directly and even list `pnpm` itself as a dependency; the README's pnpm-10 workflow is the intended one.)

## How it fits

- **Consumes API of:** `backoffice-backend` only (single `VITE_API_URL` base; ~30 `*.service.ts` clients spanning approvals, payment, fraud-detector, syncer, location-provider, pubsub, pusher, qa-queue, user-management, roles, deployment-tracking, etc. — the backend fans these out to the underlying services).
- **Auth:** Google OAuth token exchanged at `backoffice-backend` for a JWT access/refresh pair; stateless bearer + refresh interceptor.
- **Publishes events to:** none.
- **Owns data store:** none (browser-only; tokens in web storage, server state in TanStack Query).
- **Deployment:** standalone nginx container at a separate admin domain; audience and auth are distinct from the Loadmate shell.

## Build / test / run
```
npm install -g pnpm@10
pnpm install
# create .env.local with:  VITE_API_URL=http://localhost:9001
pnpm start            # or: pnpm dev  (vite dev server)
pnpm build            # tsc -b && vite build
pnpm preview          # preview built output
pnpm lint             # eslint src
# Prod: build then serve dist via nginx (nginx.conf + Dockerfile in repo)
```

## Key abstractions

- `src/index.tsx` / `src/App.tsx` — SPA bootstrap + top-level routing (react-router-dom 7).
- `src/crud/` — generic CRUD engine: `models.ts`, `schema.ts`, `registry/`, `resources/`, `services/`, `components/`, `utils/`. Most admin pages are configured against this.
- `src/pages/<domain>/` — per-feature admin screens (see list above).
- `src/services/*.service.ts` — ~30 backend clients (one per feature area).
- `src/dto/` — TypeScript DTOs mirroring backoffice-backend contracts (e.g. `loginResponse.dto.ts`, `page.dto.ts`, `user-management/`).
- `src/common/axios.ts` — shared axios instance + 401 refresh interceptor.
- `src/common/auth/` + `src/services/auth.service.ts` — Google OAuth login, token storage/expiry, logout.
- `src/components/` — reusable table columns/renderers (`Table.tsx`, `*Column.tsx`, `AceEditor.tsx`, `AuditLog.tsx`, `ConfirmButton.tsx`, `EnvironmentBanner.tsx`, `ShipperCompanyGuard.tsx`).
- `Dockerfile`, `nginx.conf`, `vite.config.ts` — build/serve config.

## Don't-do-here / gotchas

- **React 19 + Vite 6 + antd 6** — newest React/antd majors in the fleet; verify third-party compatibility before adding deps, and don't pattern-match MUI conventions here (this is Ant Design).
- **pnpm 10 workflow** — README expects `pnpm@10`; don't `npm install`. (`package.json` oddly lists `pnpm` as a dependency and scripts call `vite`/`tsc` directly — follow the README.)
- **Auth is Google OAuth → backend JWT**, not Keycloak. The 401 interceptor refreshes once and guards against loops via `X-Refresh-Token-Request`; don't remove that guard.
- **`crud/` is a framework, not one screen.** Changing `models.ts`/`schema.ts`/registry affects every page wired through it.
- **No `timeout` on the axios instance** — fleet default.
- **This is a privileged admin console** touching payments, fraud-detection, syncer, PubSub exception handling, user/role management. Treat any change as high-blast-radius and audit the corresponding `*.service.ts` + backend endpoint.
- **Pairs with `uship-backoffice-frontend`** (older CRA 5 stack) — this repo modernized first; the two are separate admin UIs.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/backoffice-backend.md` — the sole backend (NestJS) this console talks to.
- `~/projects/codebase-map/repos/uship-backoffice-frontend.md` — sibling admin UI on the older CRA stack.
- `~/projects/codebase-map/domains/platform.md`.
