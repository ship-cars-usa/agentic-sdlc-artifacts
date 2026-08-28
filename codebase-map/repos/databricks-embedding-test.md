---
repo: databricks-embedding-test
path: ~/projects/ship-cars-usa/databricks-embedding-test
stack: Node / Vite / minimal frontend (no CLAUDE.md, no README content visible at top level)
domain: analytics
shape: experimental / test harness (no `tsconfig.json`, just `server.js` + `vite.config.js` + `src/`)
last-synced-commit: 699cd7bd8ddf3acc7234298edff826cf159a4837
last-synced-date: 2026-05-12
maintainer: unknown
status: seed
---

# databricks-embedding-test

## What it is
**Test harness for embedding Databricks dashboards via base64-encoded JSON payloads.** Per the most recent commit (`Send base64 encoded json as externalValue to DataBricks`), the repo was used to validate that base64-encoded JSON could be passed to a Databricks dashboard as an `externalValue` parameter — likely a research artifact for the `bi-databricks-backend` / `ai-dashboard-backend` integration path.

Minimal Vite + Node-server scaffold (`server.js` + `vite.config.js` + `src/`). No standard CLAUDE.md / lint config / TypeScript visible at top level — this is a one-off test harness, not a productionized frontend.

Last commit 2026-01-13. Likely complete-as-experiment.

## How it fits

- **Consumes API of:** Databricks (presumably via `ai-dashboard-backend` or directly). The integration path the experiment validated.
- **Owns data store:** none.
- **Not deployed** as a service. Likely never had a production deployment.

## Build / test / run
```
npm install
npm run dev           # via Vite
node server.js        # if running the experimental Node server
```

## Key abstractions

- `server.js` — small Node server (likely Express-ish, serving the test page or providing the base64-encoding endpoint).
- `vite.config.js` — Vite build config.
- `src/` — minimal frontend source.
- `package.json` — minimal deps.

## Don't-do-here / gotchas

- **Experimental test harness, not production.** Don't pattern-match a real frontend on this repo's structure.
- **Likely archivable.** If the embedding experiment validated successfully (which the commit message suggests), the findings should be in `bi-databricks-backend` / `ai-dashboard-backend` and this repo can be retired.
- **No README, no CLAUDE.md** — knowledge is in the commit log alone.
- Flag for the next `infrastructure-triage.md` refresh as archive-candidate.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/bi-databricks-backend.md` — the productionized Databricks-integration backend.
- `~/projects/codebase-map/repos/ai-dashboard-backend.md` — likely the dashboard backend driving the embedding flow.
- `~/projects/codebase-map/repos/ml-central-data-storage.md` — Databricks-side config.
- `~/projects/codebase-map/relations/infrastructure-triage.md` — flag for archive on next refresh.
- `~/projects/codebase-map/domains/analytics.md`.
