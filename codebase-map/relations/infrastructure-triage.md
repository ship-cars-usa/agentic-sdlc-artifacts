# Infrastructure Domain Triage

Auto-generated 2026-05-08 by a one-shot triage pass over the 68 shadows in `domain: infrastructure`. Re-run the script in `~/projects/codebase-map/PLAN.md` notes to refresh.

**Classifications**

- **active** — likely still in use; recent commit, real content. 33 repo(s).
- **archive-candidate** — strong signal of disposability (DEPRECATED, _ARCHIVED, hackathon, typo'd duplicate, empty). 12 repo(s).
- **unsure** — needs human eyes. Possibly research / POC / dev-tooling that may or may not be production-relevant. 23 repo(s).

## Triage table

| Repo | Stack | Last commit | Days ago | File count | Classification | Reason |
|---|---|---|---|---:|---|---|
| [ddevops-tf-live-shipcars-gcp-projects-access](../repos/ddevops-tf-live-shipcars-gcp-projects-access.md) | unknown | 2025-08-26 | 254 | 1 | **archive-candidate** | typo'd duplicate of devops-tf-live-shipcars-gcp-projects-access |
| [devops-database-backup-cloud-function](../repos/devops-database-backup-cloud-function.md) | unknown | 2023-01-12 | 1212 | 0 | **archive-candidate** | directory is empty |
| [devops-tf-module-githuib-repositories](../repos/devops-tf-module-githuib-repositories.md) | Node/JavaScript | 2025-03-06 | 428 | 39 | **archive-candidate** | typo'd duplicate of devops-tf-module-github-repositories |
| [hackaton-team-1](../repos/hackaton-team-1.md) | Helm chart | 2025-12-11 | 147 | 307 | **archive-candidate** | one-off hackathon repo |
| [hackaton-team-3-backend](../repos/hackaton-team-3-backend.md) | Docs/Markdown | 2025-12-17 | 141 | 18 | **archive-candidate** | one-off hackathon repo |
| [hackaton_team_4](../repos/hackaton_team_4.md) | Node/Frontend (React/Vite) | 2025-12-11 | 148 | 69 | **archive-candidate** | one-off hackathon repo |
| [kubernetes](../repos/kubernetes.md) | unknown | n/a | n/a | 0 | **archive-candidate** | directory is empty |
| [quarkus-boilerplate-DEPRECATED](../repos/quarkus-boilerplate-DEPRECATED.md) | Java/Quarkus 2.16.7.Final | 2023-09-26 | 955 | 130 | **archive-candidate** | name signals archived/deprecated |
| [terraform](../repos/terraform.md) | unknown | n/a | n/a | 0 | **archive-candidate** | directory is empty |
| [test-terraform](../repos/test-terraform.md) | Docs/Markdown | 2024-11-28 | 525 | 3 | **archive-candidate** | test-* repo not touched in 525 days |
| [test-terraform1](../repos/test-terraform1.md) | Docs/Markdown | 2024-11-28 | 525 | 3 | **archive-candidate** | test-* repo not touched in 525 days |
| [tmp-openclaw-demo](../repos/tmp-openclaw-demo.md) | unknown | 2026-03-24 | 45 | 29 | **archive-candidate** | tmp-* prefix |
| [ai-actions-test](../repos/ai-actions-test.md) | Docs/Markdown | 2025-07-29 | 283 | 2 | **unsure** | only 2 files; verify it's still meaningful |
| [apache-camel-etl-demo](../repos/apache-camel-etl-demo.md) | Java/Quarkus 3.4.1 | 2023-10-12 | 939 | 15 | **unsure** | no commit in 939 days; review |
| [asenmx-terraformer](../repos/asenmx-terraformer.md) | Terraform | 2022-11-01 | 1284 | 332 | **unsure** | no commit in 1284 days; review |
| [claude-code-plugins](../repos/claude-code-plugins.md) | Docs/Markdown | 2026-04-28 | 10 | 190 | **unsure** | AI/dev-tooling repo — confirm production use vs. experiment |
| [codex-cli-ai-code-reviewer](../repos/codex-cli-ai-code-reviewer.md) | unknown | 2025-08-01 | 280 | 3 | **unsure** | AI/dev-tooling repo — confirm production use vs. experiment |
| [dev-hub](../repos/dev-hub.md) | unknown | 2026-04-28 | 9 | 133 | **unsure** | AI/dev-tooling repo — confirm production use vs. experiment |
| [devops-container-jenkins](../repos/devops-container-jenkins.md) | Docs/Markdown | 2023-08-30 | 981 | 1 | **unsure** | no commit in 981 days; review |
| [devops-poc](../repos/devops-poc.md) | Docs/Markdown | 2022-11-09 | 1275 | 2 | **unsure** | no commit in 1275 days; review |
| [devops-ssl-check](../repos/devops-ssl-check.md) | Docs/Markdown | 2023-01-03 | 1221 | 1 | **unsure** | no commit in 1221 days; review |
| [devops-terraformer-ro-import](../repos/devops-terraformer-ro-import.md) | Docs/Markdown | 2023-02-02 | 1191 | 671 | **unsure** | no commit in 1191 days; review |
| [devops-tf-live-gcp-dev-cluster-live](../repos/devops-tf-live-gcp-dev-cluster-live.md) | Docs/Markdown | 2023-02-03 | 1189 | 67 | **unsure** | no commit in 1189 days; review |
| [devops-tf-live-private-vault-sql-db-backups](../repos/devops-tf-live-private-vault-sql-db-backups.md) | Docs/Markdown | 2023-01-27 | 1197 | 1 | **unsure** | no commit in 1197 days; review |
| [devops-tf-live-ship-cars-private-vault](../repos/devops-tf-live-ship-cars-private-vault.md) | Docs/Markdown | 2023-02-24 | 1169 | 61 | **unsure** | no commit in 1169 days; review |
| [devops-tf-live-shipcars-playground](../repos/devops-tf-live-shipcars-playground.md) | Terraform (live env) | 2024-08-08 | 637 | 130 | **unsure** | POC / playground / experiment naming — confirm relevance |
| [devops-tf-live-shipcars-playground-02](../repos/devops-tf-live-shipcars-playground-02.md) | Terraform (live env) | 2024-08-08 | 637 | 130 | **unsure** | POC / playground / experiment naming — confirm relevance |
| [devops-tf-module-cloudsql-postgresql-test](../repos/devops-tf-module-cloudsql-postgresql-test.md) | Docs/Markdown | 2025-05-22 | 351 | 1 | **unsure** | only 1 files; verify it's still meaningful |
| [devops-tf-module-google-quick-openvpn](../repos/devops-tf-module-google-quick-openvpn.md) | Terraform (module) | 2023-03-29 | 1135 | 16 | **unsure** | no commit in 1135 days; review |
| [devops-tf-module-google-remote-state-gcs-backend](../repos/devops-tf-module-google-remote-state-gcs-backend.md) | Terraform (module) | 2023-03-29 | 1136 | 12 | **unsure** | no commit in 1136 days; review |
| [devops-tf-module-google-secret-manager](../repos/devops-tf-module-google-secret-manager.md) | Terraform (module) | 2023-09-20 | 961 | 6 | **unsure** | no commit in 961 days; review |
| [etcd-migrate](../repos/etcd-migrate.md) | Docs/Markdown | 2023-01-19 | 1205 | 1 | **unsure** | no commit in 1205 days; review |
| [figma-mcp-code-connect](../repos/figma-mcp-code-connect.md) | Node/Frontend (React/Vite) | 2026-04-22 | 15 | 5780 | **unsure** | AI/dev-tooling repo — confirm production use vs. experiment |
| [restore-function](../repos/restore-function.md) | Go | 2023-02-21 | 1172 | 7 | **unsure** | no commit in 1172 days; review |
| [sdlc-agents](../repos/sdlc-agents.md) | unknown | 2026-04-09 | 28 | 36 | **unsure** | AI/dev-tooling repo — confirm production use vs. experiment |
| [argo](../repos/argo.md) | Helm chart | 2026-04-15 | 23 | 195 | **active** | recent commit (23d ago); content present (195 files) |
| [argo-stresstests](../repos/argo-stresstests.md) | Helm chart | 2024-05-20 | 717 | 151 | **active** | recent commit (717d ago); content present (151 files) |
| [argo-wf-finalizer](../repos/argo-wf-finalizer.md) | Go | 2024-06-24 | 683 | 6 | **active** | recent commit (683d ago); content present (6 files) |
| [argo-wf-notificator](../repos/argo-wf-notificator.md) | Node/JavaScript | 2026-01-24 | 104 | 58 | **active** | recent commit (104d ago); content present (58 files) |
| [automation](../repos/automation.md) | Java/Gradle | 2026-05-07 | 1 | 1461 | **active** | recent commit (1d ago); content present (1461 files) |
| [catch-me](../repos/catch-me.md) | Go | 2025-10-10 | 210 | 55 | **active** | recent commit (210d ago); content present (55 files) |
| [devops-docs](../repos/devops-docs.md) | Docs/Markdown | 2025-10-16 | 203 | 25 | **active** | recent commit (203d ago); content present (25 files) |
| [devops-helpers](../repos/devops-helpers.md) | Docs/Markdown | 2026-03-30 | 38 | 34 | **active** | recent commit (38d ago); content present (34 files) |
| [devops-tf-live-atlantean-field-175514](../repos/devops-tf-live-atlantean-field-175514.md) | Docs/Markdown | 2025-12-12 | 146 | 80 | **active** | recent commit (146d ago); content present (80 files) |
| [devops-tf-live-shipcars-development-env](../repos/devops-tf-live-shipcars-development-env.md) | Docs/Markdown | 2025-08-19 | 262 | 240 | **active** | recent commit (262d ago); content present (240 files) |
| [devops-tf-live-shipcars-gcp-projects-access](../repos/devops-tf-live-shipcars-gcp-projects-access.md) | Terraform (live env) | 2026-04-06 | 32 | 91 | **active** | recent commit (32d ago); content present (91 files) |
| [devops-tf-live-shipcars-platform-dev](../repos/devops-tf-live-shipcars-platform-dev.md) | Terraform (live env) | 2026-05-07 | 1 | 224 | **active** | recent commit (1d ago); content present (224 files) |
| [devops-tf-live-shipcars-platform-prod](../repos/devops-tf-live-shipcars-platform-prod.md) | Terraform (live env) | 2026-05-04 | 3 | 399 | **active** | recent commit (3d ago); content present (399 files) |
| [devops-tf-live-shipcars-platform-qa](../repos/devops-tf-live-shipcars-platform-qa.md) | Terraform (live env) | 2026-04-22 | 16 | 232 | **active** | recent commit (16d ago); content present (232 files) |
| [devops-tf-live-shipcars-platform-staging](../repos/devops-tf-live-shipcars-platform-staging.md) | Docs/Markdown | 2026-04-15 | 22 | 308 | **active** | recent commit (22d ago); content present (308 files) |
| [devops-tf-live-shipcars-production-env](../repos/devops-tf-live-shipcars-production-env.md) | Docs/Markdown | 2025-07-14 | 298 | 31 | **active** | recent commit (298d ago); content present (31 files) |
| [devops-tf-live-shipcars-sf-lm-dev](../repos/devops-tf-live-shipcars-sf-lm-dev.md) | Docs/Markdown | 2025-11-05 | 184 | 39 | **active** | recent commit (184d ago); content present (39 files) |
| [devops-tf-live-shipcars-sf-lm-prd](../repos/devops-tf-live-shipcars-sf-lm-prd.md) | Docs/Markdown | 2026-01-28 | 99 | 39 | **active** | recent commit (99d ago); content present (39 files) |
| [devops-tf-live-shipcars-sf-lm-qa](../repos/devops-tf-live-shipcars-sf-lm-qa.md) | Docs/Markdown | 2026-02-06 | 91 | 47 | **active** | recent commit (91d ago); content present (47 files) |
| [devops-tf-live-shipcars-sf-lm-uat](../repos/devops-tf-live-shipcars-sf-lm-uat.md) | Docs/Markdown | 2026-02-06 | 91 | 44 | **active** | recent commit (91d ago); content present (44 files) |
| [devops-tf-live-shipcars-system-env](../repos/devops-tf-live-shipcars-system-env.md) | Docs/Markdown | 2026-04-28 | 9 | 196 | **active** | recent commit (9d ago); content present (196 files) |
| [devops-tf-live-shipcars-xa-montway-production](../repos/devops-tf-live-shipcars-xa-montway-production.md) | Docs/Markdown | 2025-07-14 | 298 | 32 | **active** | recent commit (298d ago); content present (32 files) |
| [devops-tf-module-github-repositories](../repos/devops-tf-module-github-repositories.md) | Node/JavaScript | 2025-08-12 | 268 | 47 | **active** | recent commit (268d ago); content present (47 files) |
| [devops-tf-module-google-iam-management](../repos/devops-tf-module-google-iam-management.md) | Terraform (module) | 2025-10-14 | 205 | 9 | **active** | recent commit (205d ago); content present (9 files) |
| [devops-tf-module-local-cloudsql-users](../repos/devops-tf-module-local-cloudsql-users.md) | Terraform (module) | 2025-09-03 | 246 | 9 | **active** | recent commit (246d ago); content present (9 files) |
| [devops-tf-module-postgres-cloudsql](../repos/devops-tf-module-postgres-cloudsql.md) | Terraform (module) | 2026-02-18 | 78 | 21 | **active** | recent commit (78d ago); content present (21 files) |
| [docker-utils](../repos/docker-utils.md) | unknown | 2026-02-17 | 80 | 145 | **active** | recent commit (80d ago); content present (145 files) |
| [helm](../repos/helm.md) | Helm chart | 2026-05-07 | 0 | 1904 | **active** | recent commit (0d ago); content present (1904 files) |
| [helm-common-chart](../repos/helm-common-chart.md) | Helm chart | 2026-04-28 | 9 | 60 | **active** | recent commit (9d ago); content present (60 files) |
| [jenkins-master-system-env](../repos/jenkins-master-system-env.md) | unknown | 2025-03-28 | 406 | 8 | **active** | recent commit (406d ago); content present (8 files) |
| [knowledge](../repos/knowledge.md) | unknown | 2026-03-20 | 48 | 107 | **active** | recent commit (48d ago); content present (107 files) |
| [knowledge-products](../repos/knowledge-products.md) | unknown | 2026-03-20 | 48 | 30 | **active** | recent commit (48d ago); content present (30 files) |
| [sc-reusable-workflows](../repos/sc-reusable-workflows.md) | unknown | 2026-04-28 | 9 | 16 | **active** | recent commit (9d ago); content present (16 files) |

## Suggested follow-up

1. **Archive the archive-candidates first** — typo'd duplicates and explicit DEPRECATED/_ARCHIVED repos are the cleanest wins. One PR per repo to add a top-level `ARCHIVED.md` (or, if the no-files-in-repos constraint is later relaxed, just delete the contents and tag).
2. **For the `unsure` set**: a short one-line clarification per repo from whoever owns the dev-tooling area resolves most of them. Capture their decision in the corresponding shadow's `maintainer:` and rewrite this triage's row.
3. **Active set is the floor** — these are the infra repos a Claude Code session can safely rely on as living artifacts.

## Methodology

Rule-based classification on three signals: name patterns (DEPRECATED / _ARCHIVED / hackaton- / tmp- / typo'd duplicates), last commit recency, and file count. Edge cases (`dev-hub`, `sdlc-agents`, `codex-cli-ai-code-reviewer`, `claude-code-plugins`, `figma-mcp-code-connect`) are surfaced as `unsure` because they're plausibly active dev tooling but also plausibly experiments. Empty directories (`kubernetes/`, `terraform/`) are auto-classified `archive-candidate`.

## Re-run

```
# inline script lives in ~/projects/codebase-map/PLAN.md notes
python3 - <<'PY' ... PY
```

(The script is inline in this commit and not yet a standalone tool — promote to `scripts/infrastructure_triage.py` if rerun cadence becomes regular.)