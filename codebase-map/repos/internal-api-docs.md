---
repo: internal-api-docs
path: ~/projects/ship-cars-usa/internal-api-docs
stack: Node / Express + swagger-ui-express 5.0.2
domain: platform
shape: tiny single-file Node service (`index.js`)
last-synced-commit: 10da53816bd1e182e2bca0157076e3aecd302da3
last-synced-date: 2026-05-12
maintainer: unknown
status: seed
---

# internal-api-docs

## What it is
A minimal **Swagger UI server** for browsing the Ship.Cars **internal** API documentation. Renders the combined OpenAPI spec produced by `api-documentation-builder`'s `output/main.json`. Internal-only — not publicly exposed.

Single-file Node service: `index.js` + `package.json` + `Dockerfile`. No README content. Last commit 2025-05-22 (`Update the swagger-ui-express to v5.0.2`) — minor bump.

## How it fits

- **Hosts:** the static Swagger UI for engineers / SREs to browse the internal API surface.
- **Consumes:** the combined OpenAPI spec from `api-documentation-builder` (which aggregates per-service swagger files via `swagger-combine`).
- **Companion service:** `internal-api-docs-controller` — the Go service that dynamically updates which API paths are exposed based on K8s configmap state.

## Build / test / run
```
npm install
node index.js
```

## Don't-do-here / gotchas

- **Internal-only** — make sure the deploy is not publicly exposed; check ingress / loadbalancer config.
- **Tiny service, but coupled to two others** (`api-documentation-builder` upstream + `internal-api-docs-controller` for dynamic config). A breakage in any of the three breaks internal API browsing.
- **No README.** Operational details are in the upstream `api-documentation-builder`'s comments / scripts.
- **Last commit was a swagger-ui-express bump.** Watch for future swagger-ui security advisories.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/api-documentation-builder.md` — produces the combined OpenAPI spec this server renders.
- `~/projects/codebase-map/repos/internal-api-docs-controller.md` — Go K8s-aware controller that manages dynamic doc-path config.
- `~/projects/codebase-map/repos/documentation.md` — public-facing docs site (different audience).
- `~/projects/codebase-map/domains/platform.md`.
