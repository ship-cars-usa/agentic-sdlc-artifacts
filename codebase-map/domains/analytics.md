---
domain: analytics
status: draft
owner-team: unknown
member-services: 24
last-reviewed: 2026-05-12
---

# Domain — analytics

## Purpose
Business intelligence (Databricks-based dashboards), the dashboard backend that brokers Databricks tokens, ML-platform infrastructure (training, experiment templates, dispatcher), document parsing, demand forecasting, and the AI-flavored testing tools.

## Member services
| Repo | Role | Stack | Status |
|---|---|---|---|
| ai-dashboard-backend | dashboard CRUD with audit | Java/Quarkus 3.27.0 | seed |
| bi-databricks-backend | Databricks OAuth + embed-token broker | Java/Quarkus 3.27.0 | seed |
| ai-testgen | Jira+Figma → Claude → test cases | Python (Claude API + AWS Secrets Mgr) | seed |
| company-documents | company documents service | Python / FastAPI | seed |
| databricks-embedding-test | base64-encoded JSON externalValue experiment | Node / Vite (test harness) | seed *(archive-candidate)* |
| elk-backup-restore | ELK snapshot/restore operational script | Python (operator-run) | seed *(operationally infra; re-domain candidate)* |
| executive-dashboard-frontend | executive dashboard UI (single-spa MFE) | TS/React / single-spa app-parcel | seed |
| ml-central-data-storage | Databricks asset bundle (transformations / dashboards / governance / utilities) | Databricks YAML config | seed |
| ml-data-hamal | source-to-sink DB data porter ("datahamal") | Python / SQL-driven | seed |
| ml-demand-forecasting | quarterly batch forecasting (PyTorch / TempoPFN) | Python | seed |
| ml-document-parser | pluggable document-parsing surface | Python / FastAPI | seed |
| ml-experiments | historical research notebooks (3 sub-experiments) | Jupyter + Python | seed |
| ml-experiments-template | canonical experiment template (DVC + GCS + dev containers) | Python / VS Code Dev Containers | seed |
| ml-lib-extraction | async LiteLLM extraction library w/ structured output + repair | Python (LiteLLM router) | seed |
| ml-model-training | rate / confidence / correction-model training pipeline (Jenkins-driven) | Python / MySQL / GCS / Jenkins | seed |
| ml-notebooks-archive | flat archive of `[RE-NNN]` Jupyter notebooks | Jupyter | seed *(archive-candidate)* |
| ml-pricing-app | Streamlit BI dashboard for pricing-accuracy | Python / Streamlit (re-domained from pricing-billing) | seed |
| ml-playground | 2023-era ChatGPT learning experiments | Mixed (3-years stale) | seed *(archive-candidate)* |
| ml-service-dispatcher | synchronous ML-prediction gateway | Python / FastAPI | seed |
| ml-service-listener | ML event listener (Pub/Sub sink) | Python / FastAPI | seed |
| user-activity-tracker | event tracking + HyperLogLog + Parquet export (re-domained from identity) | Java/Quarkus 3.20.2.2 | seed |
| devops-tf-live-shipcars-ml-data-dev | Terraform live env for `shipcars-ml-data-dev` GCP project | Terraform | seed *(re-domain to `infrastructure`)* |
| devops-tf-live-shipcars-ml-data-prod | Terraform live env for `shipcars-ml-data-prod` GCP project | Terraform | seed *(re-domain to `infrastructure`)* |
| devops-tf-live-shipcars-ml-data-staging | Terraform live env for `shipcars-ml-data-staging` GCP project | Terraform | seed *(re-domain to `infrastructure`)* |

## Key flows (partial — from seeds)
**Dashboard embed (bi-databricks-backend):**
1. `DashboardResource` accepts a request with company context.
2. `CompanyConfigService` reads encrypted Databricks creds from Postgres (`AesGcmEncryptionService` decrypts).
3. `DatabricksOAuthService.getServicePrincipalToken()` — `@Retry(maxRetries=7)` against Databricks OAuth, **no `@Timeout`** (P0). Worst-case 8 attempts × ~60s = 607s.
4. Embed token returned to caller.

**Dashboard CRUD (ai-dashboard-backend):**
- Plain CRUD over `dashboards`, `cities`, `states` tables with Hibernate Envers audit. No outbound calls.

## Data stores
- `bi-databricks-backend`: Postgres (`company_config` with AES-GCM-encrypted secrets).
- `ai-dashboard-backend`: Postgres (Envers tables included).
- ML pipelines: Databricks tables + S3-style buckets; specific stores are managed by the 3 `devops-tf-live-shipcars-ml-data-*` repos.
- ELK: Elasticsearch indexes, snapshots managed by `elk-backup-restore`.

## Cross-cutting concerns
- ML services share an extraction library (`ml-lib-extraction`) — central foot-gun if it has bugs.
- 22 services in this domain is the largest count after `infrastructure` and `platform`. Sub-grouping (BI vs. ML-platform vs. document parsing) is plausible if it grows further.
- The 3 `devops-tf-live-shipcars-ml-data-*` repos manage prod/staging/dev environments separately — a typical Terraform pattern for blast-radius isolation.

## Open questions / known gaps
- ~~`ml-service-dispatcher` orchestrates "ML predictions" — for which downstream models?~~ **Resolved (Phase 4.10):** synchronous gateway in front of `ml-model-rate`, `ml-model-rate-confidence-absolute`, `ml-model-rate-confidence-percentage`, `ml-model-rate-multivehicle`, `ml-model-rate` family, plus `dataone` and the recommender path.
- ~~`ml-experiments`, `ml-notebooks-archive`, `ml-playground` — production-relevant or archive candidates?~~ **Resolved (Phase 4.24):** `ml-experiments` is historical research feeding `ml-bot-order-v2` / `load-recommender` / `ml-service-recommender`; `ml-notebooks-archive` is the `[RE-NNN]` notebook dump feeding `ml-document-parser` / `ml-demand-forecasting`; `ml-playground` is 3-years-stale ChatGPT experimentation (archive). All three flagged for the next infrastructure-triage refresh.
- ~~`ml-central-data-storage` has no code; is it a docs-only repo?~~ **Resolved (Phase 4.24):** it's the Databricks Asset Bundle config (`databricks.yml`) plus per-folder transformations / dashboards / governance / utilities. Deployed via `databricks bundle deploy`, not via Ship.Cars helm.
- **New shadow-caller edge surfaced (Phase 4.24):** `ml-model-training` reads `rateengine`'s MySQL database directly using `RATE_ENGINE_PASSWORD`. Adds to the cross-service direct-DB-read count (now 16). Needs an ADR-0003 contract draft.
- The 3 `devops-tf-live-shipcars-ml-data-*` repos belong in `infrastructure`, not `analytics` — re-domain pending.
- `elk-backup-restore` is operationally an ELK-cluster admin tool — could be re-domained to `infrastructure` alongside the Terraform repos.

## Related ADRs
- Fleet review: `~/projects/quarkus-fleet-review-2026-05-07.md#2-ai-dashboard-backend` (verdict: ship-as-is) and `#3-bi-databricks-backend` (the timeout anti-pattern in textbook form).
- Anti-pattern: `~/projects/quarkus-rest-client-timeout-anti-pattern.md` uses `bi-databricks-backend` as its worked example.
- `~/projects/codebase-map/adr/0003-cross-service-db-read-policy.md` — applies to `ml-model-training` → `rateengine`-MySQL read (new this phase).
- `~/projects/codebase-map/adr/0005-rateengine-eol-rewrite.md` — `ml-model-training`'s MySQL dependency migrates with the rateengine rewrite.

## Coverage
**24 of 24 shadows are `seed`** — analytics is **catalog-complete** as of 2026-05-12 (Phase 4.24).

Newly seeded in Phase 4.24 (15 seeds):

**Substantive ML / data services (8):**
- `ai-testgen` — Claude + Jira + Figma test-case generator.
- `ml-data-hamal` — source-to-sink DB porter.
- `ml-experiments` — historical research repo (3 sub-experiments: automated-posting / recommender / template).
- `ml-experiments-template` — canonical DVC+GCS+dev-container template for new experiments.
- `ml-lib-extraction` — async LiteLLM extraction library (very well documented: ARCHITECTURE / SPEC / STATE / LESSONS / EXAMPLES).
- `ml-model-training` — Jenkins-driven training pipeline; new shadow-caller edge to `rateengine` MySQL.
- `elk-backup-restore` — ELK snapshot/restore operational script.

**Frontends (2):**
- `executive-dashboard-frontend` — single-spa MFE for executive metrics.
- `databricks-embedding-test` — small Vite test harness for the Databricks-embedding experiment (archive-candidate).

**Docs/archive (3):**
- `ml-central-data-storage` — Databricks Asset Bundle config.
- `ml-notebooks-archive` — `[RE-NNN]`-tagged Jupyter notebooks dump (archive-candidate).
- `ml-playground` — 2023-era ChatGPT learning repo (archive-candidate).

**Terraform live-envs (3, all re-domain candidates → `infrastructure`):**
- `devops-tf-live-shipcars-ml-data-dev` — richer (has `live/iam/`).
- `devops-tf-live-shipcars-ml-data-staging`.
- `devops-tf-live-shipcars-ml-data-prod`.

**Archive-candidates surfaced this pass**: `ml-playground`, `ml-notebooks-archive`, `databricks-embedding-test`. **Re-domain candidates**: 3 `devops-tf-live-shipcars-ml-data-*` (→ infrastructure), `elk-backup-restore` (→ infrastructure).
