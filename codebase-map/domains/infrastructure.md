---
domain: infrastructure
status: draft
owner-team: unknown
member-services: 68
last-reviewed: 2026-05-08
---

# Domain — infrastructure

## Purpose
Everything that's *outside* the request path: Terraform live envs + modules, Helm charts, Argo workflows, Jenkins, Docker base images, devops scripts, hackathon repos, knowledge-base / docs repos, dev-tooling experiments, AI-coding-assistant configs.

This is the largest single domain by repo count (68 of 232 = 29%) but the lowest by request-path criticality. A failure here doesn't take production down (until it does — see below).

## Member services (by sub-group)

### Terraform — live environments (10)
- `devops-tf-live-shipcars-gcp-projects-access`
- `devops-tf-live-shipcars-platform-dev`
- `devops-tf-live-shipcars-platform-prod`
- `devops-tf-live-shipcars-platform-qa`
- `devops-tf-live-shipcars-playground`
- `devops-tf-live-shipcars-playground-02`
- *Plus 13 more `devops-tf-live-*` and 2 typo'd duplicates that show up as `Docs/Markdown`-only*
- `ddevops-tf-live-shipcars-gcp-projects-access` (typo'd duplicate; empty)

### Terraform — modules (7+)
- `devops-tf-module-google-iam-management`
- `devops-tf-module-google-quick-openvpn`
- `devops-tf-module-google-remote-state-gcs-backend`
- `devops-tf-module-google-secret-manager`
- `devops-tf-module-local-cloudsql-users`
- `devops-tf-module-postgres-cloudsql`
- `devops-tf-module-cloudsql-postgresql-test`
- `devops-tf-module-github-repositories` + `devops-tf-module-githuib-repositories` (typo'd duplicate)
- `asenmx-terraformer`, `devops-terraformer-ro-import`, `terraform`, `test-terraform`, `test-terraform1` (placeholders / test repos)

### Helm / K8s
- `helm`, `helm-common-chart`, `argo`, `argo-stresstests`
- `argo-wf-finalizer` (Go), `argo-wf-notificator` (Node)
- `kubernetes` (empty placeholder per PROJECTS_INDEX.md)

### CI / Dev tooling
- `automation` (Gradle / Jenkins test automation)
- `automation-epod-github-actions-test` (note: also referenced by `operations` if you'd rather group ePOD-related test infra there)
- `sc-reusable-workflows` (reusable GitHub Actions)
- `jenkins-master-system-env`, `devops-container-jenkins`
- `docker-utils`, `etcd-migrate`
- `restore-function` (Argo CD-deployed Go restore tool)
- `devops-database-backup-cloud-function`
- `devops-ssl-check`
- `devops-tf-module-cloudsql-postgresql-test`

### AI-coding assistants / templates
- `claude-code-plugins`, `codex-cli-ai-code-reviewer`, `sdlc-agents`, `tmp-openclaw-demo`
- `ai-actions-test`, `figma-mcp-code-connect`, `apache-camel-etl-demo` (ETL example)
- `dev-hub` (IntelliJ / dev-environment hub)

### Knowledge / docs
- `knowledge`, `knowledge-products`
- `devops-docs`, `devops-helpers`, `devops-poc`

### Hackathons / archived
- `hackaton-team-1`, `hackaton-team-3-backend`, `hackaton_team_4`
- `quarkus-boilerplate-DEPRECATED`

## Key flows
- **Provisioning a new environment:** clone an existing `devops-tf-live-*` repo → adapt `live/<area>/` for the new env → `terraform init/plan/apply`.
- **Deploying a service to K8s:** GitHub Actions (likely from `sc-reusable-workflows`) → builds image → pushes to registry → Argo CD picks up the chart change → `helm-common-chart` renders → applied.
- **Backups:** `devops-database-backup-cloud-function` runs scheduled DB exports; `restore-function` reverses.
- **SSL hygiene:** `devops-ssl-check` flags expiring certs.

## Cross-cutting concerns
- **Two typo'd Terraform repos coexist with their correctly-named originals** — this domain has the highest "are we sure both are still active?" risk. Confirm and archive duplicates.
- Several repos in this domain are tagged `Docs/Markdown` — they have only Markdown content (no `*.tf` or other code). Some are placeholders for live envs that haven't been spun up yet, others are stale.
- The hackathon repos (`hackaton-team-*`) are presumably one-off — should be archived if not.
- `quarkus-boilerplate-DEPRECATED` is explicitly deprecated; the active boilerplate is `quarkus-k8s-boilerplate` (in the `platform` domain).

## Open questions / known gaps
- Which terraform-live repos are *actually applied* vs. which are placeholders?
- The two typo'd duplicates — which is the canonical?
- `dev-hub` describes itself as "IntelliJ Java settings / dev environment hub" — is this still actively used by the team, or one engineer's settings backup?
- `tmp-openclaw-demo` and `sdlc-agents` are AI-agent experiments — research, demo, or production?

## Related ADRs
- None recorded yet.

## Coverage
**34 of 68 shadows are `seed` status** as of 2026-05-12 (Phase 4.29). All **33 active-classified repos** from `infrastructure-triage.md` are seeded, plus 1 prior seed from earlier passes. The remaining 34 stubs are the **12 archive-candidates + 23 unsure** per the 2026-05-08 triage — left at stub deliberately, pending human-triage decisions on each.

**Phase 4.29 newly seeded (33):**

**Terraform live envs (13):** `devops-tf-live-shipcars-platform-{dev,qa,staging,prod}` (the canonical 4-tier per-env GCP infra), `-system-env` (cross-env: TLS / DNS / Cloudflare / Jenkins / OpenVPN / network), `-development-env` + `-production-env` (older predecessor envs that still coexist), `-gcp-projects-access` (cross-project IAM), `-xa-montway-production` (Montway-partner separate GCP project), `-atlantean-field-175514` (legacy GCP project hosting the `production-rate-engine-model` GCS bucket consumed by all 4 `ml-model-*` services), `-sf-lm-{dev,qa,uat,prd}` (Salesforce ↔ Loadmate integration, 4-env dev/qa/uat/prd progression — Salesforce-convention).

**Terraform modules (4):** `devops-tf-module-postgres-cloudsql` (canonical CloudSQL PG instance module), `devops-tf-module-local-cloudsql-users` (DB-side user management), `devops-tf-module-google-iam-management` (cluster-wide IAM), `devops-tf-module-github-repositories` (GitHub-as-code for all 232 repos).

**Helm + K8s (4):** `helm` (1904 files — fleet's authoritative Helm-chart monorepo, source of truth for K8s production state, Atlantis-managed; **most-frequently-touched repo in the catalog**), `helm-common-chart` (reusable library chart, OCI-published), `argo` (Argo CD + Workflows + Events config), `argo-stresstests` (workflow stress-test repo; 2-yrs-stale — flag for re-evaluation).

**Go / Node services (4):** `catch-me` (Go Fiber web service, purpose unclear without deeper read), `argo-wf-finalizer` (Go Argo Workflow finalizer), `argo-wf-notificator` (Go CLI sending Slack + GitHub notifications from Argo Workflows), `automation` (1461 files — fleet's primary Jenkins-driven test framework; 1-day-fresh).

**Docs / knowledge (5):** `knowledge` (engineering KB with ADRs / contracts / conventions / domain / guides), `knowledge-products` (CTMS + Loadmate product-specific docs), `devops-docs` (DevOps team's reference docs), `devops-helpers` (DevOps helper scripts), `sc-reusable-workflows` (shared GitHub Actions reusable workflows).

**CI / Docker / Jenkins (3):** `docker-utils` (8 base Docker images — every fleet `Dockerfile` extends one of these), `jenkins-master-system-env` (Jenkins-master container config + plugins.txt), `automation` (already covered above).

## Key catalog observations from this pass

1. **The `helm` repo is the fleet's authoritative source-of-truth for production K8s state.** Per-service `values-*.yaml` files carry replica counts, pool sizes, secrets wiring. Several earlier-seeded P0 findings (like `socket-server-old`'s hardcoded JWT secret in `helm/.../values-{dev,qa,staging,production}.yaml`) live here.
2. **Atlantis-managed PR-based applies** (`atlantis.yaml` in `helm/`) appear to be the canonical mechanism for both Helm changes and likely Terraform live-env changes — confirms the GitOps posture.
3. **`devops-tf-live-atlantean-field-175514`** hosts the **ML model GCS bucket** consumed by every `ml-model-*` inference service — legacy GCP project that became load-bearing.
4. **`devops-tf-live-shipcars-system-env/live/repositories/`** uses `devops-tf-module-github-repositories` to manage all 232 Ship.Cars GitHub repos as code — highest blast-radius Terraform module in the catalog.
5. **Three generations of fleet docs/knowledge repos:** `devops-docs` (DevOps-specific), `knowledge` (engineering-wide ADRs / contracts / conventions / domain), `knowledge-products` (per-product CTMS + Loadmate).

## Remaining 34 stubs (deliberately left for human triage)

Per `infrastructure-triage.md`:
- **12 archive-candidates**: typo'd duplicates (`ddevops-*`, `devops-tf-module-githuib-*`), empty placeholders (`kubernetes/`, `terraform/`, `devops-database-backup-cloud-function/`), one-off hackathons (`hackaton-team-*`), explicit deprecations (`quarkus-boilerplate-DEPRECATED`), `tmp-*` prefix, test-* stale.
- **23 unsure**: AI/dev-tooling experiments (`claude-code-plugins`, `dev-hub`, `sdlc-agents`, `codex-cli-ai-code-reviewer`, `figma-mcp-code-connect`, `ai-actions-test`), old dev-tooling (`devops-poc`, `devops-ssl-check`, `etcd-migrate`, `restore-function`), older live-envs / modules (`devops-tf-live-gcp-dev-cluster-live`, `devops-tf-live-private-vault-*`, `devops-tf-live-ship-cars-private-vault`, `asenmx-terraformer`, `devops-tf-module-google-quick-openvpn`, `devops-tf-module-google-remote-state-gcs-backend`, `devops-tf-module-google-secret-manager`, `devops-tf-module-cloudsql-postgresql-test`), playground envs (`devops-tf-live-shipcars-playground` + `-02`), `apache-camel-etl-demo`, `devops-container-jenkins`, `devops-terraformer-ro-import`, `jenkins-master-system-env`'s sibling? — see triage doc for the canonical list.

Each unsure repo needs a one-line decision from the dev-tooling area owner.

**Infrastructure domain: 34 of 68 seeds (active subset 33/33 + 1 prior); 34 stubs (archive-candidates + unsure subset) preserved for human triage.**
