---
repo: documentation
path: ~/projects/ship-cars-usa/documentation
stack: Node / Grunt 1.x / static-site generator for API reference docs
domain: platform
shape: documentation-site (Grunt-built, deployed to GCS)
last-synced-commit: 26f48027a5e0945d276ba9a96c737e17f86e64c7
last-synced-date: 2026-05-12
maintainer: unknown
status: seed
---

# documentation

## What it is
**`ship-cars-docs`** — static documentation site for `docs.ship.cars` covering the Platform API and Rate Engine API. Built with **Grunt 1.x** (uncommon in 2026; even more uncommon than `ui-commons`'s Gulp build). Deployed to a Google Cloud Storage bucket (`docs-production-ship-cars`) authenticated via personal Google account per the README.

**Last commit 2022-12-07** (`Added build scripts`) — **3.5 years stale**. The README is sparse, the build is Grunt, and the deploy mechanism depends on personal-Google-account auth — all hallmarks of a frozen / abandoned site that may have been superseded by something newer (Readme.com, Swagger UI, internal Confluence) but never formally retired.

## How it fits

- **Generates static docs for `docs.ship.cars`.** Public-facing developer documentation.
- **Sources:** `non-reference-source/` directory (markdown / hand-written), augmented by any API specs combined elsewhere (`api-documentation-builder` does that combining for the swagger side — see that seed).

## Build / test / run
```
npm install
npx grunt                            # build (Grunt is the build tool)
./build-and-deploy-to-{dev,qa,staging,production}.sh
```

## Don't-do-here / gotchas

- **Archive-candidate.** 3.5 years stale; verify `docs.ship.cars` is even still maintained from this repo before assuming any commit here will deploy.
- **Grunt-based.** Newer doc-site work would use Docusaurus / Vitepress / Readme.com / similar. If "the docs need to be updated" is a real ask, evaluate moving to a current tool rather than reviving this Grunt build.
- **Personal-Google-account auth for deploy** — fragile / employee-tied. If the original author left, deploys may already be broken.
- **`api-documentation-builder` is a related but distinct repo** — that one combines per-service swagger files; this one is the static-docs presentation layer.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/api-documentation-builder.md` — combines per-service swagger files; companion piece.
- `~/projects/codebase-map/repos/internal-api-docs.md` — internal Node + swagger-ui-express docs server (different audience).
- `~/projects/codebase-map/relations/infrastructure-triage.md` — flag for archive on next refresh.
- `~/projects/codebase-map/domains/platform.md`.
