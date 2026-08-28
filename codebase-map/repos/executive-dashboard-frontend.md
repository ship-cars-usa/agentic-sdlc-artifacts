---
repo: executive-dashboard-frontend
path: ~/projects/ship-cars-usa/executive-dashboard-frontend
stack: TypeScript 5.9 / React 18.3 / single-spa 6.0.3 + single-spa-react 6.0.2 (app-parcel) / Webpack 5.105 / MUI 6.4 + @mui/x-charts 7 + @mui/x-data-grid 7 / @tanstack/react-query 5 / @databricks/aibi-client (embedded Databricks AI/BI dashboard) / recharts 3 / axios 1.17 / pnpm 11 / Node 22+
domain: analytics
shape: single-module (single-spa app-parcel)
last-synced-commit: b8e096008972baca0bb3d6250c56ca774f4c0da9
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# executive-dashboard-frontend

## What it is
`@shipcars/executive-dashboard` — a single-spa MFE mounted into the Loadmate shell that surfaces executive-level BI. **The dashboard itself is a Databricks AI/BI dashboard embedded client-side**, not charts drawn in-repo: the MFE fetches a short-lived embed token from its backend and hands it to `@databricks/aibi-client`'s `DatabricksDashboard`, which renders the Databricks dashboard into a container `<div>` (`src/pages/Dashboard/useDatabricksDashboard.ts`). (Correction vs. previous shadow: this is not a recharts/MUI-charts-rendered dashboard — `recharts` / `@mui/x-charts` / `@mui/x-data-grid` are present as deps but the live executive dashboard is the embedded Databricks one.)

Modern LoadMate ("lm-") MFE generation: single-spa 6, react-query, MUI 6.4, pnpm, Node 22, ESLint 9 flat config. README is still the unmodified `create-single-spa --moduleType app-parcel` template ("It should handle the posting functionality") — ignore it. Commit history is on the **LITE** Jira project (LoadMate/Lite).

## How it fits

- **Consumes API of:** the executive-dashboard backend at `environment.EXECUTIVE_DASHBOARD_API` (resolved by `@ship-cars-usa/lm-global-config` → `environments.executiveDashboard()`), via `GET /dashboards` (`src/api/dashboard.ts`). The response is `{ token, workspaceUrl, workspaceId, dashboardId, expiresAt }` — a Databricks embed token + workspace/dashboard identifiers. Backend is almost certainly `ai-dashboard-backend` (Spring Boot, Databricks integration) — confirm the mapping in lm-global-config; the previous shadow's `bi-databricks-backend` claim is not corroborated in-repo.
- **Then talks directly to Databricks:** `@databricks/aibi-client` opens the embedded dashboard against `workspaceUrl`, refreshing the token via a `getNewToken` callback (`fetchNewToken` → re-fetch `GET /dashboards`). So the browser holds a live connection to the Databricks workspace for the dashboard iframe/SDK.
- **Publishes events to:** none.
- **Owns data store:** none (react-query cache only; `staleTime: 0` so the token is always re-fetched).

## Build / test / run
```
# Registry auth (one-time): FontAwesome + GitHub Packages tokens in ~/.npmrc
pnpm config set "//npm.fontawesome.com/:_authToken" "$FONTAWESOME_TOKEN"
pnpm config set "//npm.pkg.github.com/:_authToken" "$GITHUB_TOKEN"
pnpm install
pnpm start               # webpack serve --port 7080 --env isLocal
pnpm start:standalone    # webpack serve --env standalone
pnpm build               # concurrently build:webpack + build:types
pnpm test                # jest --passWithNoTests
pnpm typecheck / lint / format / check:circular (madge)
```

## Key abstractions

- `src/shipcars-executive-dashboard.tsx` — single-spa app-parcel lifecycle via `single-spa-react` (error boundary returns `null`).
- `src/root.component.tsx` (+ `root.component.scss`) — top-level React tree.
- `src/pages/Dashboard/Dashboard.tsx` — the dashboard page; wires the embed-token query to the Databricks container.
- `src/pages/Dashboard/useDatabricksDashboard.ts` — constructs `DatabricksDashboard({ instanceUrl, workspaceId, dashboardId, token, container, getNewToken, colorScheme })`, calls `.initialize()`, and `.destroy()` on cleanup (StrictMode double-destroy tolerated).
- `src/query/useGetExecutiveDashboard.ts` — react-query `queryOptions` (key `["executiveDashboard","getExecutiveDashboard"]`, `staleTime: 0`) wrapping `DashboardApi.getExecutiveDashboard()`.
- `src/api/axios.ts` — `axios.create({ baseURL: environment.EXECUTIVE_DASHBOARD_API })` + `setAxiosInstancesRequestInterceptors` (auth interceptors from `lm-data-layer`).
- `src/api/dashboard.ts` — `getExecutiveDashboard()` → `GET /dashboards`; `IExecutiveDashboardResponse` type.
- `environments/*.environment.ts` — all delegate to `environments.executiveDashboard()` from `lm-global-config`.
- `Dockerfile` / `Dockerfile-test`, `eslint.config.mjs` (ESLint 9 flat), `webpack.common.mjs` + `webpack.config.mjs`.

## Don't-do-here / gotchas

- **The dashboard is Databricks-embedded — don't assume in-repo chart code renders it.** If the dashboard is blank/errored, the failure is almost always the token fetch (`GET /dashboards`) or the Databricks SDK init (`useDatabricksDashboard`), not a chart component. `recharts` / `@mui/x-charts` / `@mui/x-data-grid` are deps but are not what draws the executive dashboard.
- **Short-lived Databricks token.** `expiresAt` matters; the SDK's `getNewToken` re-hits the backend. A backend outage on `/dashboards` breaks the whole page, including refreshes.
- **Audience is executives** — a broken embed or stale token is high-visibility. Verify end-to-end (backend token → Databricks render) before shipping rendering-layer changes.
- **`EXECUTIVE_DASHBOARD_API` base URL comes from `lm-global-config`**, not this repo. "Wrong environment's dashboard" is usually a lm-global-config / `deploymentInstance` issue.
- **README is template-leftover** ("It should handle the posting functionality") — do not treat it as accurate.
- **Mounted by the Loadmate shell** via the import-map (standard app-parcel model).

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/ai-dashboard-backend.md` — the Spring Boot backend that mints the Databricks embed token (`GET /dashboards`).
- `~/projects/codebase-map/repos/ml-central-data-storage.md` — Databricks-side config / dashboards / governance.
- `~/projects/codebase-map/domains/analytics.md`.
