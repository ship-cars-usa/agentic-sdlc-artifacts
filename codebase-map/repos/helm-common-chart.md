---
repo: helm-common-chart
path: ~/projects/ship-cars-usa/helm-common-chart
stack: Helm library chart (OCI-published) / `common-chart` + `example-chart` + tests/
domain: infrastructure
shape: shared Helm template library (60 files)
last-synced-commit: efec6363fe6e4392e290f39bc18f264be2f71fcb
last-synced-date: 2026-05-12
maintainer: unknown
status: stale
---

# helm-common-chart

## What it is
**The fleet's reusable Helm library chart** — `common-chart` provides standardized templates and configuration for K8s deployments, distributed via OCI at `oci://us-central1-docker.pkg.dev/shipcars-system-env/shipcars`. Per the README, consumed by adding it as a `dependencies:` entry in another chart's `Chart.yaml`:

```yaml
dependencies:
  - name: common-chart
    version: "1.0.0"
    repository: "oci://us-central1-docker.pkg.dev/shipcars-system-env/shipcars"
```

Then including all resources via:
```yaml
{{- include "common-chart.all" . }}
```

Companion `example-chart/` demonstrates the integration pattern. `tests/` validates template rendering.

Last commit 2026-04-28 — actively maintained.

## How it fits

- **Compile-time dependency of:** every per-service Helm chart in the `helm` monorepo that wants the standardized template patterns.
- **Provides:** Deployment / Service / Ingress / ServiceAccount / ExternalSecrets / ConfigMap / PodDisruptionBudget / HPA templates with conventional defaults.
- **Distributed via:** OCI registry (Helm 3.8+).

## Build / test / run
```
helm lint common-chart/
helm template example-chart/ -f example-chart/values.yaml
helm test -f tests/  # if test framework present
```

## Don't-do-here / gotchas

- **Breaking changes here cascade to every consuming chart in `helm/`.** Version-bump semver respect required.
- **OCI distribution** — consumers need OCI-aware Helm (3.8+) and access to the GCP Artifact Registry.
- **Pairs with `helm` monorepo.** Most per-service charts in `helm/ship-cars-usa/<service>/` either depend on `common-chart` or hand-roll their templates.

## Relevant ADRs / docs
- `~/projects/codebase-map/repos/helm.md` — primary consumer monorepo.
- `~/projects/codebase-map/domains/infrastructure.md`.
