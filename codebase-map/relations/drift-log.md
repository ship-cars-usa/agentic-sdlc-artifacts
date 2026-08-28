# Drift Check Log

Auto-appended by `scripts/run-drift-check.sh` (launchd job `cars.codebase-map.drift`, weekly Mondays 09:00). Each section is one run.

If a run reports drift, the affected shadow's frontmatter is rewritten to `status: stale` automatically — re-read the source and re-bootstrap (or re-author) the shadow to clear the stale state.


## 2026-05-08T14:34:11+03:00

```

checked 232 shadow(s): 232 clean, 0 drifted
```

## 2026-05-12 — manual correction (not from `run-drift-check.sh`)

Carrier-persona MFE shadows had vague "Consumes API of" sections that **missed the Django dependency**. Corrected after grepping every `/api/...` literal in the 4 MFE repos + 4 shared FE packages.

**Files updated (content correction, not drift; `last-synced-commit` unchanged):**

- `repos/ctms-frontend.md` — How it fits + Relevant ADRs
- `repos/loadboard-frontend.md` — How it fits + Relevant ADRs
- `repos/trip-planner-frontend.md` — How it fits + Relevant ADRs (dual-surface notice added)
- `repos/carrier-order-importer-frontend.md` — How it fits + Relevant ADRs (corrected: not via command-executor)
- `repos/platform-backend.md` — How it fits (4 inbound MFE callers + URL-ownership convention)
- `repos/entities-frontend-package.md` — How it fits (~100 `/api/...` paths catalogued; flagged as the API conduit)
- `relations/service-graph.md` — appended "MFE → backend edges (carrier-persona surface)" section + dual-surface noun table

**Root cause of the gap:** the seed authoring relied on shadow docs' English-language "Consumes API of" lists rather than grep on the source. The Django edges were assumed peripheral; in fact every carrier MFE has a heavy Django dependency that flows through the shared `entities-frontend-package`. Lesson for future seed passes on FE repos: grep `/api/` literals BEFORE writing "Consumes API of".

**Suggested follow-up:** run the same grep on the remaining frontend repos (chat-frontend, posting-frontend, inventory-frontend, public-root-app-frontend, executive-dashboard-frontend, contract-pricing-frontend, …) — they likely have similar undeclared Django edges, since they all import `entities-frontend-package` too.

## 2026-07-17 — manual correction (not from `run-drift-check.sh`)

Reconciled the JS/TS backend-service question against `PROJECTS_INDEX.md`. The shadow docs were already correct on stack; the **index is not**.

**Finding:** `PROJECTS_INDEX.md` lists `platform-backend` under "Node/Other" — it is **Python/Django** (verified via `manage.py` + `requirements.txt`; the root `package.json`/`bower.json` only bundle FE static assets). No shadow-doc stack change needed (`platform-backend.md` already reads `stack: Python 3.6 / Django + Daphne`); added an explicit index-conflict callout to that shadow's "What it is".

**Verified JS/TS backend services (SPAs, FE packages, and tooling excluded), 2026-07-17 — 4 active + 1 legacy:**

| Repo | Framework | Shadow `stack:` already correct? |
|---|---|---|
| `backoffice-backend` | NestJS 10 / TypeORM | ✅ |
| `uship-backoffice-backend` | NestJS 10 / TypeORM | ✅ |
| `home-delivery-backend` | Fastify 2 | ✅ |
| `socket-server` | Express 4 + Socket.IO 2 | ✅ |
| `socket-server-old` (legacy/deprecated) | Socket.IO 2 + redis | ✅ |

Excluded from the count: `platform-backend` (Django), `fe-exercise-inventory-api` (interview exercise), `public-root-app-frontend` / `carrier-packages-frontend` (frontend), `*-frontend-package` (FE libs), `argo-wf-notificator` / `api-documentation-builder` / `internal-api-docs` (tooling/docs), `devops-tf-module-github(u)ib-repositories` (Terraform helpers).

**Files updated (content correction, not drift; `last-synced-commit` unchanged):**
- `repos/platform-backend.md` — "What it is" (added PROJECTS_INDEX.md miscategorization callout)

**Lesson:** `PROJECTS_INDEX.md`'s language column is guessed and can be wrong *across* languages, not just Quarkus-vs-Spring (see also the known Quarkus/Spring miscount). For "how many <language> services" questions, trust shadow `stack:` fields + source markers over the index.

## 2026-08-03T09:04:00+03:00

```
[DRIFT]       aaag-integration.md: shadow=7472e8605302 HEAD=35d438f1e7dd
              -> marked status: stale
[DRIFT]       argo.md: shadow=bec1e1dce9de HEAD=0a7acf51d4aa
              -> marked status: stale
[DRIFT]       asg-checkout-spa.md: shadow=3252f7514419 HEAD=a0ffbccb9076
              -> marked status: stale
[DRIFT]       attachment-backend.md: shadow=2c97fc11853b HEAD=118e59df9287
              -> marked status: stale
[DRIFT]       autoims-backend.md: shadow=aebc0aa42bc5 HEAD=637a4ab0d599
              -> marked status: stale
[DRIFT]       automation.md: shadow=04bcafd4451d HEAD=812b48203770
              -> marked status: stale
[DRIFT]       axe-call-integration.md: shadow=777e18467d06 HEAD=d9a2609969f7
              -> marked status: stale
[DRIFT]       backoffice-backend.md: shadow=f521aa5dda88 HEAD=9bd26985b053
              -> marked status: stale
[DRIFT]       backoffice-frontend.md: shadow=2e3fa47c2b0f HEAD=e194993bdd03
              -> marked status: stale
[DRIFT]       bi-databricks-backend.md: shadow=aec9796f152d HEAD=679ca311e642
              -> marked status: stale
[DRIFT]       carrier-order-importer-frontend.md: shadow=c62e5767e99e HEAD=1f7ebba143a8
              -> marked status: stale
[DRIFT]       carrier-packages-frontend.md: shadow=ea97b6cd0443 HEAD=01849c82e0d2
              -> marked status: stale
[DRIFT]       chase-driver-tracking-frontend.md: shadow=7f7bc1fa67bf HEAD=e6020fbbba5b
              -> marked status: stale
[DRIFT]       chat-backend.md: shadow=634d4330590a HEAD=978961435b67
              -> marked status: stale
[DRIFT]       chat-frontend.md: shadow=17acf187444d HEAD=5b4b876063e9
              -> marked status: stale
[DRIFT]       claude-code-plugins.md: shadow=0d9859ce27a4 HEAD=b14d641fc1a7
              -> marked status: stale
[DRIFT]       command-executor.md: shadow=eaf4febacd0c HEAD=46e6be70b408
              -> marked status: stale
[DRIFT]       commons.md: shadow=ea8557cf6a72 HEAD=bb85b5cbef02
              -> marked status: stale
[DRIFT]       contract-pricing-backend.md: shadow=8aa940c5e7a4 HEAD=2e3465def9ea
              -> marked status: stale
[DRIFT]       contract-pricing-frontend.md: shadow=c2a1f6c583e2 HEAD=76f0b65112c1
              -> marked status: stale
[DRIFT]       crm-workflows.md: shadow=14dc9616c8bf HEAD=00161fa6d48c
              -> marked status: stale
[DRIFT]       ctms-frontend.md: shadow=27ea6a8196eb HEAD=f58b20bd87f3
              -> marked status: stale
[DRIFT]       cube.md: shadow=b11137cbc685 HEAD=bc94c0009519
              -> marked status: stale
[DRIFT]       dev-hub.md: shadow=8852ecc4a9eb HEAD=9eca3597aee7
              -> marked status: stale
[DRIFT]       devops-tf-live-atlantean-field-175514.md: shadow=9b18130089cf HEAD=ef8c7f636f6c
              -> marked status: stale
[DRIFT]       devops-tf-live-shipcars-development-env.md: shadow=65ae5c90d78b HEAD=fc44a40982e0
              -> marked status: stale
[DRIFT]       devops-tf-live-shipcars-gcp-projects-access.md: shadow=4d4d4f552a6c HEAD=c13a40f2af3e
              -> marked status: stale
[DRIFT]       devops-tf-live-shipcars-logytext-integration.md: shadow=37ade28ea16e HEAD=141a088c8592
              -> marked status: stale
[DRIFT]       devops-tf-live-shipcars-ml-data-dev.md: shadow=510ef56ca8cd HEAD=bba336015ce8
              -> marked status: stale
[DRIFT]       devops-tf-live-shipcars-ml-data-prod.md: shadow=78d0b7de1b4a HEAD=59dfa26247ca
              -> marked status: stale
[DRIFT]       devops-tf-live-shipcars-ml-data-staging.md: shadow=353283802935 HEAD=8148e789bfad
              -> marked status: stale
[DRIFT]       devops-tf-live-shipcars-platform-dev.md: shadow=8a1b4e4a520e HEAD=396f08454138
              -> marked status: stale
[DRIFT]       devops-tf-live-shipcars-platform-prod.md: shadow=d110047d2622 HEAD=935a414c1540
              -> marked status: stale
[DRIFT]       devops-tf-live-shipcars-platform-qa.md: shadow=0b4fab2fb6fa HEAD=b3dcd907c451
              -> marked status: stale
[DRIFT]       devops-tf-live-shipcars-platform-staging.md: shadow=b93d990ca6b0 HEAD=c6812b29e74a
              -> marked status: stale
[DRIFT]       devops-tf-live-shipcars-production-env.md: shadow=3575eef1c2be HEAD=071705897b71
              -> marked status: stale
[DRIFT]       devops-tf-live-shipcars-sf-lm-dev.md: shadow=7933e9db7854 HEAD=595ac64f3466
              -> marked status: stale
[DRIFT]       devops-tf-live-shipcars-sf-lm-prd.md: shadow=3eff8c6c014f HEAD=cfe590a36dd0
              -> marked status: stale
[DRIFT]       devops-tf-live-shipcars-sf-lm-qa.md: shadow=9af99651d5fc HEAD=94df1943edb8
              -> marked status: stale
[DRIFT]       devops-tf-live-shipcars-sf-lm-uat.md: shadow=808f5c6f6b52 HEAD=42d70e9599e3
              -> marked status: stale
[DRIFT]       devops-tf-live-shipcars-system-env.md: shadow=937930febebb HEAD=aeaf6756a402
              -> marked status: stale
[DRIFT]       devops-tf-live-shipcars-xa-montway-production.md: shadow=0d03c5a4bade HEAD=80d7cc62ec85
              -> marked status: stale
[DRIFT]       devops-tf-module-local-cloudsql-users.md: shadow=3104b2224d51 HEAD=0e36e7359563
              -> marked status: stale
[DRIFT]       devops-tf-module-postgres-cloudsql.md: shadow=9364cdefad80 HEAD=9e64a5928786
              -> marked status: stale
[DRIFT]       docker-utils.md: shadow=80d5ca64379b HEAD=083a2cfeafb8
              -> marked status: stale
[DRIFT]       driveaway-backend.md: shadow=2aa302510bb7 HEAD=924564094466
              -> marked status: stale
[DRIFT]       driveaway-public-tracking-frontend.md: shadow=afdd89cc0e2a HEAD=2f73e54e5836
              -> marked status: stale
[DRIFT]       epod-android.md: shadow=e1a5040383c0 HEAD=7aae6e09cc9f
              -> marked status: stale
[DRIFT]       epod-ios.md: shadow=d80a8ac5fbce HEAD=f5362a9353ae
              -> marked status: stale
[DRIFT]       executive-dashboard-frontend.md: shadow=07f91816bb72 HEAD=b8e096008972
              -> marked status: stale
[DRIFT]       gallery-frontend.md: shadow=7fe09b80fb25 HEAD=a6abdba5f0e6
              -> marked status: stale
[DRIFT]       helm-common-chart.md: shadow=efec6363fe6e HEAD=4ad4093d3733
              -> marked status: stale
[DRIFT]       helm.md: shadow=8c08b554782a HEAD=b8623a6a79e5
              -> marked status: stale
[DRIFT]       import-map-deployer.md: shadow=daff6e9146a0 HEAD=06a5f1ec615a
              -> marked status: stale
[DRIFT]       integration-executor.md: shadow=373388e7d729 HEAD=0339f9ed0360
              -> marked status: stale
[DRIFT]       integrations-backend.md: shadow=48a3a34f8a50 HEAD=6a05f0c3939c
              -> marked status: stale
[DRIFT]       integrators-data-bridge.md: shadow=e3da48668585 HEAD=5f0f2c878ea5
              -> marked status: stale
[DRIFT]       inventory-backend.md: shadow=ad10f97f729a HEAD=886d5f4d6f8e
              -> marked status: stale
[DRIFT]       inventory-frontend.md: shadow=37377357edf1 HEAD=9a1c451a9e03
              -> marked status: stale
[DRIFT]       invoices.md: shadow=1765b07648ce HEAD=1907c1544d02
              -> marked status: stale
[DRIFT]       knowledge.md: shadow=11a40d060779 HEAD=ad67d198f6cd
              -> marked status: stale
[DRIFT]       load-bookmark-backend.md: shadow=e6af5f15a3b8 HEAD=c28f2dfdf834
              -> marked status: stale
[DRIFT]       load-recommender.md: shadow=5e56fb874426 HEAD=60543de71050
              -> marked status: stale
[DRIFT]       loadboard-backend.md: shadow=25e365033e68 HEAD=e652c43ff84e
              -> marked status: stale
[DRIFT]       loadboard-frontend.md: shadow=35fec90b1de7 HEAD=6a680ad72d0c
              -> marked status: stale
[DRIFT]       loadbuilder-backend.md: shadow=3c8c91c29403 HEAD=0da9b96798bd
              -> marked status: stale
[DRIFT]       location-history-backend.md: shadow=b518d9a759d9 HEAD=7d70791bac7e
              -> marked status: stale
[DRIFT]       location-provider.md: shadow=4596c3656e24 HEAD=5e5313b59e36
              -> marked status: stale
[DRIFT]       metadata.md: shadow=5cfe40609af5 HEAD=a1e613c923f4
              -> marked status: stale
[DRIFT]       ml-data-hamal.md: shadow=763821754b11 HEAD=db1fad6158ab
              -> marked status: stale
[DRIFT]       ml-document-parser.md: shadow=2b613791debd HEAD=da73d9065b29
              -> marked status: stale
[DRIFT]       ml-experiments.md: shadow=ab0895c5c68c HEAD=1b2b0d9b17b4
              -> marked status: stale
[DRIFT]       ml-service-recommender.md: shadow=c5a969aef0cc HEAD=8087efcd6e57
              -> marked status: stale
[DRIFT]       models-lib.md: shadow=2f684ec3959a HEAD=09cc0357cdec
              -> marked status: stale
[DRIFT]       negotiations-router.md: shadow=054a93436545 HEAD=35e8712e22a3
              -> marked status: stale
[DRIFT]       payment-backend.md: shadow=06c4dd96743c HEAD=9f732f77fc0a
              -> marked status: stale
[malformed]   platform-backend-data-model.md: missing repo/last-synced-commit
[DRIFT]       platform-backend.md: shadow=b4cb3033aa20 HEAD=34f21ba37ae5
              -> marked status: stale
[DRIFT]       platform-frontend.md: shadow=bdcc84e2ed76 HEAD=ad2985de1ac1
              -> marked status: stale
[DRIFT]       posting-backend.md: shadow=748aa454f28f HEAD=a2c3fbebc347
              -> marked status: stale
[DRIFT]       posting-frontend.md: shadow=d495168f4ad2 HEAD=97b9b7764155
              -> marked status: stale
[DRIFT]       public-root-app-frontend.md: shadow=8eccff0845b1 HEAD=55ce49ce868b
              -> marked status: stale
[DRIFT]       public-tracking-backend.md: shadow=f2ec60f48272 HEAD=425ab6e0b4b3
              -> marked status: stale
[DRIFT]       public-tracking-frontend.md: shadow=3c10118c957d HEAD=805ab55d73ed
              -> marked status: stale
[DRIFT]       pusher.md: shadow=1f4213b6b541 HEAD=334fe2357acb
              -> marked status: stale
[DRIFT]       quarkus-commons.md: shadow=23ac13807011 HEAD=38395e50d6c6
              -> marked status: stale
[DRIFT]       quarkus-extension-firestore-storage.md: shadow=2bdd17cc7f46 HEAD=9106721e603a
              -> marked status: stale
[DRIFT]       quarkus-extension-webclient.md: shadow=efece7068d68 HEAD=383e6724b288
              -> marked status: stale
[DRIFT]       quarkus-imperative-boilerplate.md: shadow=b6dd9612f254 HEAD=695f885a5702
              -> marked status: stale
[DRIFT]       quarkus-notification-client.md: shadow=528e8fb37cf3 HEAD=491a4e4a25d9
              -> marked status: stale
[DRIFT]       quarkus-request-filter.md: shadow=9cb4dec60529 HEAD=16c95f87a0dc
              -> marked status: stale
[DRIFT]       quarkus-user-syncer.md: shadow=ffec208ae351 HEAD=0c43f138f960
              -> marked status: stale
[DRIFT]       quote-manager-backend.md: shadow=41cbbc8a35d0 HEAD=729a55029bc1
              -> marked status: stale
[DRIFT]       saved-search-handler.md: shadow=d870ca3110fd HEAD=1f1fb6250b99
              -> marked status: stale
[DRIFT]       sc-reusable-workflows.md: shadow=78ed06bbadca HEAD=30b53f68f2e3
              -> marked status: stale
[DRIFT]       sdlc-agents.md: shadow=d40d299fc0eb HEAD=5ee72b403bcc
              -> marked status: stale
[DRIFT]       settings-frontend.md: shadow=a3491f733f67 HEAD=2140af4c64f1
              -> marked status: stale
[DRIFT]       shipcars-quarkus-bom.md: shadow=1016af5a08ca HEAD=367823b47a99
              -> marked status: stale
[DRIFT]       spring-commons.md: shadow=99b0efcf8f2c HEAD=0675b3eac85e
              -> marked status: stale
[DRIFT]       syncer.md: shadow=4c0f72febe26 HEAD=08306732fb2c
              -> marked status: stale
[DRIFT]       synclink-backend.md: shadow=0c14795875fc HEAD=f006a87c1d3c
              -> marked status: stale
[DRIFT]       trip-planner-frontend.md: shadow=17ef6f01dec5 HEAD=0fa1c99d8daf
              -> marked status: stale
[DRIFT]       trip-planner.md: shadow=e01f207ce899 HEAD=67d9f1d431c7
              -> marked status: stale
[DRIFT]       ui-commons.md: shadow=6858be6d8432 HEAD=6a3c77008dee
              -> marked status: stale
[DRIFT]       user-backend.md: shadow=886f47f6983a HEAD=5f7457562a90
              -> marked status: stale
[DRIFT]       user-frontend.md: shadow=c6cb77d1649f HEAD=20024f144e47
              -> marked status: stale
[DRIFT]       uship-quotes.md: shadow=b6cae9667e42 HEAD=5f0fa1a754a5
              -> marked status: stale

checked 233 shadow(s): 126 clean, 107 drifted
```

## 2026-08-10T09:13:44+03:00

```
[DRIFT]       aaag-integration.md: shadow=7472e8605302 HEAD=35d438f1e7dd
[DRIFT]       argo.md: shadow=bec1e1dce9de HEAD=0a7acf51d4aa
[DRIFT]       asg-checkout-spa.md: shadow=3252f7514419 HEAD=a0ffbccb9076
[DRIFT]       attachment-backend.md: shadow=2c97fc11853b HEAD=118e59df9287
[DRIFT]       autoims-backend.md: shadow=aebc0aa42bc5 HEAD=637a4ab0d599
[DRIFT]       automation.md: shadow=04bcafd4451d HEAD=812b48203770
[DRIFT]       axe-call-integration.md: shadow=777e18467d06 HEAD=d9a2609969f7
[DRIFT]       backoffice-backend.md: shadow=f521aa5dda88 HEAD=9bd26985b053
[DRIFT]       backoffice-frontend.md: shadow=2e3fa47c2b0f HEAD=e194993bdd03
[DRIFT]       bi-databricks-backend.md: shadow=aec9796f152d HEAD=679ca311e642
[DRIFT]       carrier-order-importer-frontend.md: shadow=c62e5767e99e HEAD=1f7ebba143a8
[DRIFT]       carrier-packages-frontend.md: shadow=ea97b6cd0443 HEAD=01849c82e0d2
[DRIFT]       chase-driver-tracking-frontend.md: shadow=7f7bc1fa67bf HEAD=e6020fbbba5b
[DRIFT]       chat-backend.md: shadow=634d4330590a HEAD=978961435b67
[DRIFT]       chat-frontend.md: shadow=17acf187444d HEAD=5b4b876063e9
[DRIFT]       claude-code-plugins.md: shadow=0d9859ce27a4 HEAD=b14d641fc1a7
[DRIFT]       command-executor.md: shadow=eaf4febacd0c HEAD=46e6be70b408
[DRIFT]       commons.md: shadow=ea8557cf6a72 HEAD=bb85b5cbef02
[DRIFT]       contract-pricing-backend.md: shadow=8aa940c5e7a4 HEAD=2e3465def9ea
[DRIFT]       contract-pricing-frontend.md: shadow=c2a1f6c583e2 HEAD=76f0b65112c1
[DRIFT]       crm-workflows.md: shadow=14dc9616c8bf HEAD=00161fa6d48c
[DRIFT]       ctms-frontend.md: shadow=27ea6a8196eb HEAD=f58b20bd87f3
[DRIFT]       cube.md: shadow=b11137cbc685 HEAD=bc94c0009519
[DRIFT]       dev-hub.md: shadow=8852ecc4a9eb HEAD=9eca3597aee7
[DRIFT]       devops-tf-live-atlantean-field-175514.md: shadow=9b18130089cf HEAD=ef8c7f636f6c
[DRIFT]       devops-tf-live-shipcars-development-env.md: shadow=65ae5c90d78b HEAD=fc44a40982e0
[DRIFT]       devops-tf-live-shipcars-gcp-projects-access.md: shadow=4d4d4f552a6c HEAD=c13a40f2af3e
[DRIFT]       devops-tf-live-shipcars-logytext-integration.md: shadow=37ade28ea16e HEAD=141a088c8592
[DRIFT]       devops-tf-live-shipcars-ml-data-dev.md: shadow=510ef56ca8cd HEAD=bba336015ce8
[DRIFT]       devops-tf-live-shipcars-ml-data-prod.md: shadow=78d0b7de1b4a HEAD=59dfa26247ca
[DRIFT]       devops-tf-live-shipcars-ml-data-staging.md: shadow=353283802935 HEAD=8148e789bfad
[DRIFT]       devops-tf-live-shipcars-platform-dev.md: shadow=8a1b4e4a520e HEAD=396f08454138
[DRIFT]       devops-tf-live-shipcars-platform-prod.md: shadow=d110047d2622 HEAD=935a414c1540
[DRIFT]       devops-tf-live-shipcars-platform-qa.md: shadow=0b4fab2fb6fa HEAD=b3dcd907c451
[DRIFT]       devops-tf-live-shipcars-platform-staging.md: shadow=b93d990ca6b0 HEAD=c6812b29e74a
[DRIFT]       devops-tf-live-shipcars-production-env.md: shadow=3575eef1c2be HEAD=071705897b71
[DRIFT]       devops-tf-live-shipcars-sf-lm-dev.md: shadow=7933e9db7854 HEAD=595ac64f3466
[DRIFT]       devops-tf-live-shipcars-sf-lm-prd.md: shadow=3eff8c6c014f HEAD=cfe590a36dd0
[DRIFT]       devops-tf-live-shipcars-sf-lm-qa.md: shadow=9af99651d5fc HEAD=94df1943edb8
[DRIFT]       devops-tf-live-shipcars-sf-lm-uat.md: shadow=808f5c6f6b52 HEAD=42d70e9599e3
[DRIFT]       devops-tf-live-shipcars-system-env.md: shadow=937930febebb HEAD=aeaf6756a402
[DRIFT]       devops-tf-live-shipcars-xa-montway-production.md: shadow=0d03c5a4bade HEAD=80d7cc62ec85
[DRIFT]       devops-tf-module-local-cloudsql-users.md: shadow=3104b2224d51 HEAD=0e36e7359563
[DRIFT]       devops-tf-module-postgres-cloudsql.md: shadow=9364cdefad80 HEAD=9e64a5928786
[DRIFT]       docker-utils.md: shadow=80d5ca64379b HEAD=083a2cfeafb8
[DRIFT]       driveaway-backend.md: shadow=2aa302510bb7 HEAD=924564094466
[DRIFT]       driveaway-public-tracking-frontend.md: shadow=afdd89cc0e2a HEAD=2f73e54e5836
[DRIFT]       epod-android.md: shadow=e1a5040383c0 HEAD=7aae6e09cc9f
[DRIFT]       epod-ios.md: shadow=d80a8ac5fbce HEAD=f5362a9353ae
[DRIFT]       executive-dashboard-frontend.md: shadow=07f91816bb72 HEAD=b8e096008972
[DRIFT]       gallery-frontend.md: shadow=7fe09b80fb25 HEAD=a6abdba5f0e6
[DRIFT]       helm-common-chart.md: shadow=efec6363fe6e HEAD=4ad4093d3733
[DRIFT]       helm.md: shadow=8c08b554782a HEAD=b8623a6a79e5
[DRIFT]       import-map-deployer.md: shadow=daff6e9146a0 HEAD=06a5f1ec615a
[DRIFT]       integration-executor.md: shadow=373388e7d729 HEAD=0339f9ed0360
[DRIFT]       integrations-backend.md: shadow=48a3a34f8a50 HEAD=6a05f0c3939c
[DRIFT]       integrators-data-bridge.md: shadow=e3da48668585 HEAD=5f0f2c878ea5
[DRIFT]       inventory-backend.md: shadow=ad10f97f729a HEAD=886d5f4d6f8e
[DRIFT]       inventory-frontend.md: shadow=37377357edf1 HEAD=9a1c451a9e03
[DRIFT]       invoices.md: shadow=1765b07648ce HEAD=1907c1544d02
[DRIFT]       knowledge.md: shadow=11a40d060779 HEAD=ad67d198f6cd
[DRIFT]       load-bookmark-backend.md: shadow=e6af5f15a3b8 HEAD=c28f2dfdf834
[DRIFT]       load-recommender.md: shadow=5e56fb874426 HEAD=60543de71050
[DRIFT]       loadboard-backend.md: shadow=25e365033e68 HEAD=e652c43ff84e
[DRIFT]       loadboard-frontend.md: shadow=35fec90b1de7 HEAD=6a680ad72d0c
[DRIFT]       loadbuilder-backend.md: shadow=3c8c91c29403 HEAD=0da9b96798bd
[DRIFT]       location-history-backend.md: shadow=b518d9a759d9 HEAD=7d70791bac7e
[DRIFT]       location-provider.md: shadow=4596c3656e24 HEAD=5e5313b59e36
[DRIFT]       metadata.md: shadow=5cfe40609af5 HEAD=a1e613c923f4
[DRIFT]       ml-data-hamal.md: shadow=763821754b11 HEAD=db1fad6158ab
[DRIFT]       ml-document-parser.md: shadow=2b613791debd HEAD=da73d9065b29
[DRIFT]       ml-experiments.md: shadow=ab0895c5c68c HEAD=1b2b0d9b17b4
[DRIFT]       ml-service-recommender.md: shadow=c5a969aef0cc HEAD=8087efcd6e57
[DRIFT]       models-lib.md: shadow=2f684ec3959a HEAD=09cc0357cdec
[DRIFT]       negotiations-router.md: shadow=054a93436545 HEAD=35e8712e22a3
[DRIFT]       payment-backend.md: shadow=06c4dd96743c HEAD=9f732f77fc0a
[malformed]   platform-backend-data-model.md: missing repo/last-synced-commit
[DRIFT]       platform-backend.md: shadow=b4cb3033aa20 HEAD=34f21ba37ae5
[DRIFT]       platform-frontend.md: shadow=bdcc84e2ed76 HEAD=ad2985de1ac1
[DRIFT]       posting-backend.md: shadow=748aa454f28f HEAD=a2c3fbebc347
[DRIFT]       posting-frontend.md: shadow=d495168f4ad2 HEAD=97b9b7764155
[DRIFT]       public-root-app-frontend.md: shadow=8eccff0845b1 HEAD=55ce49ce868b
[DRIFT]       public-tracking-backend.md: shadow=f2ec60f48272 HEAD=425ab6e0b4b3
[DRIFT]       public-tracking-frontend.md: shadow=3c10118c957d HEAD=805ab55d73ed
[DRIFT]       pusher.md: shadow=1f4213b6b541 HEAD=334fe2357acb
[DRIFT]       quarkus-commons.md: shadow=23ac13807011 HEAD=38395e50d6c6
[DRIFT]       quarkus-extension-firestore-storage.md: shadow=2bdd17cc7f46 HEAD=9106721e603a
[DRIFT]       quarkus-extension-webclient.md: shadow=efece7068d68 HEAD=383e6724b288
[DRIFT]       quarkus-imperative-boilerplate.md: shadow=b6dd9612f254 HEAD=695f885a5702
[DRIFT]       quarkus-notification-client.md: shadow=528e8fb37cf3 HEAD=491a4e4a25d9
[DRIFT]       quarkus-request-filter.md: shadow=9cb4dec60529 HEAD=16c95f87a0dc
[DRIFT]       quarkus-user-syncer.md: shadow=ffec208ae351 HEAD=0c43f138f960
[DRIFT]       quote-manager-backend.md: shadow=41cbbc8a35d0 HEAD=729a55029bc1
[DRIFT]       saved-search-handler.md: shadow=d870ca3110fd HEAD=1f1fb6250b99
[DRIFT]       sc-reusable-workflows.md: shadow=78ed06bbadca HEAD=30b53f68f2e3
[DRIFT]       sdlc-agents.md: shadow=d40d299fc0eb HEAD=5ee72b403bcc
[DRIFT]       settings-frontend.md: shadow=a3491f733f67 HEAD=2140af4c64f1
[DRIFT]       shipcars-quarkus-bom.md: shadow=1016af5a08ca HEAD=367823b47a99
[DRIFT]       spring-commons.md: shadow=99b0efcf8f2c HEAD=0675b3eac85e
[DRIFT]       syncer.md: shadow=4c0f72febe26 HEAD=08306732fb2c
[DRIFT]       synclink-backend.md: shadow=0c14795875fc HEAD=f006a87c1d3c
[DRIFT]       trip-planner-frontend.md: shadow=17ef6f01dec5 HEAD=0fa1c99d8daf
[DRIFT]       trip-planner.md: shadow=e01f207ce899 HEAD=67d9f1d431c7
[DRIFT]       ui-commons.md: shadow=6858be6d8432 HEAD=6a3c77008dee
[DRIFT]       user-backend.md: shadow=886f47f6983a HEAD=5f7457562a90
[DRIFT]       user-frontend.md: shadow=c6cb77d1649f HEAD=20024f144e47
[DRIFT]       uship-quotes.md: shadow=b6cae9667e42 HEAD=5f0fa1a754a5

checked 233 shadow(s): 126 clean, 107 drifted
```

## 2026-08-17T09:10:32+03:00

```
[DRIFT]       aaag-integration.md: shadow=7472e8605302 HEAD=35d438f1e7dd
[DRIFT]       argo.md: shadow=bec1e1dce9de HEAD=0a7acf51d4aa
[DRIFT]       asg-checkout-spa.md: shadow=3252f7514419 HEAD=a0ffbccb9076
[DRIFT]       attachment-backend.md: shadow=2c97fc11853b HEAD=118e59df9287
[DRIFT]       autoims-backend.md: shadow=aebc0aa42bc5 HEAD=637a4ab0d599
[DRIFT]       automation.md: shadow=04bcafd4451d HEAD=812b48203770
[DRIFT]       axe-call-integration.md: shadow=777e18467d06 HEAD=d9a2609969f7
[DRIFT]       backoffice-backend.md: shadow=f521aa5dda88 HEAD=9bd26985b053
[DRIFT]       backoffice-frontend.md: shadow=2e3fa47c2b0f HEAD=e194993bdd03
[DRIFT]       bi-databricks-backend.md: shadow=aec9796f152d HEAD=679ca311e642
[DRIFT]       carrier-order-importer-frontend.md: shadow=c62e5767e99e HEAD=1f7ebba143a8
[DRIFT]       carrier-packages-frontend.md: shadow=ea97b6cd0443 HEAD=01849c82e0d2
[DRIFT]       chase-driver-tracking-frontend.md: shadow=7f7bc1fa67bf HEAD=e6020fbbba5b
[DRIFT]       chat-backend.md: shadow=634d4330590a HEAD=978961435b67
[DRIFT]       chat-frontend.md: shadow=17acf187444d HEAD=5b4b876063e9
[DRIFT]       claude-code-plugins.md: shadow=0d9859ce27a4 HEAD=b14d641fc1a7
[DRIFT]       command-executor.md: shadow=eaf4febacd0c HEAD=46e6be70b408
[DRIFT]       commons.md: shadow=ea8557cf6a72 HEAD=bb85b5cbef02
[DRIFT]       contract-pricing-backend.md: shadow=8aa940c5e7a4 HEAD=2e3465def9ea
[DRIFT]       contract-pricing-frontend.md: shadow=c2a1f6c583e2 HEAD=76f0b65112c1
[DRIFT]       crm-workflows.md: shadow=14dc9616c8bf HEAD=00161fa6d48c
[DRIFT]       ctms-frontend.md: shadow=27ea6a8196eb HEAD=f58b20bd87f3
[DRIFT]       cube.md: shadow=b11137cbc685 HEAD=bc94c0009519
[DRIFT]       dev-hub.md: shadow=8852ecc4a9eb HEAD=9eca3597aee7
[DRIFT]       devops-tf-live-atlantean-field-175514.md: shadow=9b18130089cf HEAD=ef8c7f636f6c
[DRIFT]       devops-tf-live-shipcars-development-env.md: shadow=65ae5c90d78b HEAD=fc44a40982e0
[DRIFT]       devops-tf-live-shipcars-gcp-projects-access.md: shadow=4d4d4f552a6c HEAD=c13a40f2af3e
[DRIFT]       devops-tf-live-shipcars-logytext-integration.md: shadow=37ade28ea16e HEAD=141a088c8592
[DRIFT]       devops-tf-live-shipcars-ml-data-dev.md: shadow=510ef56ca8cd HEAD=bba336015ce8
[DRIFT]       devops-tf-live-shipcars-ml-data-prod.md: shadow=78d0b7de1b4a HEAD=59dfa26247ca
[DRIFT]       devops-tf-live-shipcars-ml-data-staging.md: shadow=353283802935 HEAD=8148e789bfad
[DRIFT]       devops-tf-live-shipcars-platform-dev.md: shadow=8a1b4e4a520e HEAD=396f08454138
[DRIFT]       devops-tf-live-shipcars-platform-prod.md: shadow=d110047d2622 HEAD=935a414c1540
[DRIFT]       devops-tf-live-shipcars-platform-qa.md: shadow=0b4fab2fb6fa HEAD=b3dcd907c451
[DRIFT]       devops-tf-live-shipcars-platform-staging.md: shadow=b93d990ca6b0 HEAD=c6812b29e74a
[DRIFT]       devops-tf-live-shipcars-production-env.md: shadow=3575eef1c2be HEAD=071705897b71
[DRIFT]       devops-tf-live-shipcars-sf-lm-dev.md: shadow=7933e9db7854 HEAD=595ac64f3466
[DRIFT]       devops-tf-live-shipcars-sf-lm-prd.md: shadow=3eff8c6c014f HEAD=cfe590a36dd0
[DRIFT]       devops-tf-live-shipcars-sf-lm-qa.md: shadow=9af99651d5fc HEAD=94df1943edb8
[DRIFT]       devops-tf-live-shipcars-sf-lm-uat.md: shadow=808f5c6f6b52 HEAD=42d70e9599e3
[DRIFT]       devops-tf-live-shipcars-system-env.md: shadow=937930febebb HEAD=aeaf6756a402
[DRIFT]       devops-tf-live-shipcars-xa-montway-production.md: shadow=0d03c5a4bade HEAD=80d7cc62ec85
[DRIFT]       devops-tf-module-local-cloudsql-users.md: shadow=3104b2224d51 HEAD=0e36e7359563
[DRIFT]       devops-tf-module-postgres-cloudsql.md: shadow=9364cdefad80 HEAD=9e64a5928786
[DRIFT]       docker-utils.md: shadow=80d5ca64379b HEAD=083a2cfeafb8
[DRIFT]       driveaway-backend.md: shadow=2aa302510bb7 HEAD=924564094466
[DRIFT]       driveaway-public-tracking-frontend.md: shadow=afdd89cc0e2a HEAD=2f73e54e5836
[DRIFT]       epod-android.md: shadow=e1a5040383c0 HEAD=7aae6e09cc9f
[DRIFT]       epod-ios.md: shadow=d80a8ac5fbce HEAD=f5362a9353ae
[DRIFT]       executive-dashboard-frontend.md: shadow=07f91816bb72 HEAD=b8e096008972
[DRIFT]       gallery-frontend.md: shadow=7fe09b80fb25 HEAD=a6abdba5f0e6
[DRIFT]       helm-common-chart.md: shadow=efec6363fe6e HEAD=4ad4093d3733
[DRIFT]       helm.md: shadow=8c08b554782a HEAD=b8623a6a79e5
[DRIFT]       import-map-deployer.md: shadow=daff6e9146a0 HEAD=06a5f1ec615a
[DRIFT]       integration-executor.md: shadow=373388e7d729 HEAD=0339f9ed0360
[DRIFT]       integrations-backend.md: shadow=48a3a34f8a50 HEAD=6a05f0c3939c
[DRIFT]       integrators-data-bridge.md: shadow=e3da48668585 HEAD=5f0f2c878ea5
[DRIFT]       inventory-backend.md: shadow=ad10f97f729a HEAD=886d5f4d6f8e
[DRIFT]       inventory-frontend.md: shadow=37377357edf1 HEAD=9a1c451a9e03
[DRIFT]       invoices.md: shadow=1765b07648ce HEAD=1907c1544d02
[DRIFT]       knowledge.md: shadow=11a40d060779 HEAD=ad67d198f6cd
[DRIFT]       load-bookmark-backend.md: shadow=e6af5f15a3b8 HEAD=c28f2dfdf834
[DRIFT]       load-recommender.md: shadow=5e56fb874426 HEAD=60543de71050
[DRIFT]       loadboard-backend.md: shadow=25e365033e68 HEAD=e652c43ff84e
[DRIFT]       loadboard-frontend.md: shadow=35fec90b1de7 HEAD=6a680ad72d0c
[DRIFT]       loadbuilder-backend.md: shadow=3c8c91c29403 HEAD=0da9b96798bd
[DRIFT]       location-history-backend.md: shadow=b518d9a759d9 HEAD=7d70791bac7e
[DRIFT]       location-provider.md: shadow=4596c3656e24 HEAD=5e5313b59e36
[DRIFT]       metadata.md: shadow=5cfe40609af5 HEAD=a1e613c923f4
[DRIFT]       ml-data-hamal.md: shadow=763821754b11 HEAD=db1fad6158ab
[DRIFT]       ml-document-parser.md: shadow=2b613791debd HEAD=da73d9065b29
[DRIFT]       ml-experiments.md: shadow=ab0895c5c68c HEAD=1b2b0d9b17b4
[DRIFT]       ml-service-recommender.md: shadow=c5a969aef0cc HEAD=8087efcd6e57
[DRIFT]       models-lib.md: shadow=2f684ec3959a HEAD=09cc0357cdec
[DRIFT]       negotiations-router.md: shadow=054a93436545 HEAD=35e8712e22a3
[DRIFT]       payment-backend.md: shadow=06c4dd96743c HEAD=9f732f77fc0a
[malformed]   platform-backend-data-model.md: missing repo/last-synced-commit
[DRIFT]       platform-backend.md: shadow=b4cb3033aa20 HEAD=34f21ba37ae5
[DRIFT]       platform-frontend.md: shadow=bdcc84e2ed76 HEAD=ad2985de1ac1
[DRIFT]       posting-backend.md: shadow=748aa454f28f HEAD=a2c3fbebc347
[DRIFT]       posting-frontend.md: shadow=d495168f4ad2 HEAD=97b9b7764155
[DRIFT]       public-root-app-frontend.md: shadow=8eccff0845b1 HEAD=55ce49ce868b
[DRIFT]       public-tracking-backend.md: shadow=f2ec60f48272 HEAD=425ab6e0b4b3
[DRIFT]       public-tracking-frontend.md: shadow=3c10118c957d HEAD=805ab55d73ed
[DRIFT]       pusher.md: shadow=1f4213b6b541 HEAD=334fe2357acb
[DRIFT]       quarkus-commons.md: shadow=23ac13807011 HEAD=38395e50d6c6
[DRIFT]       quarkus-extension-firestore-storage.md: shadow=2bdd17cc7f46 HEAD=9106721e603a
[DRIFT]       quarkus-extension-webclient.md: shadow=efece7068d68 HEAD=383e6724b288
[DRIFT]       quarkus-imperative-boilerplate.md: shadow=b6dd9612f254 HEAD=695f885a5702
[DRIFT]       quarkus-notification-client.md: shadow=528e8fb37cf3 HEAD=491a4e4a25d9
[DRIFT]       quarkus-request-filter.md: shadow=9cb4dec60529 HEAD=16c95f87a0dc
[DRIFT]       quarkus-user-syncer.md: shadow=ffec208ae351 HEAD=0c43f138f960
[DRIFT]       quote-manager-backend.md: shadow=41cbbc8a35d0 HEAD=729a55029bc1
[DRIFT]       saved-search-handler.md: shadow=d870ca3110fd HEAD=1f1fb6250b99
[DRIFT]       sc-reusable-workflows.md: shadow=78ed06bbadca HEAD=30b53f68f2e3
[DRIFT]       sdlc-agents.md: shadow=d40d299fc0eb HEAD=5ee72b403bcc
[DRIFT]       settings-frontend.md: shadow=a3491f733f67 HEAD=2140af4c64f1
[DRIFT]       shipcars-quarkus-bom.md: shadow=1016af5a08ca HEAD=367823b47a99
[DRIFT]       spring-commons.md: shadow=99b0efcf8f2c HEAD=0675b3eac85e
[DRIFT]       syncer.md: shadow=4c0f72febe26 HEAD=08306732fb2c
[DRIFT]       synclink-backend.md: shadow=0c14795875fc HEAD=f006a87c1d3c
[DRIFT]       trip-planner-frontend.md: shadow=17ef6f01dec5 HEAD=0fa1c99d8daf
[DRIFT]       trip-planner.md: shadow=e01f207ce899 HEAD=67d9f1d431c7
[DRIFT]       ui-commons.md: shadow=6858be6d8432 HEAD=6a3c77008dee
[DRIFT]       user-backend.md: shadow=886f47f6983a HEAD=5f7457562a90
[DRIFT]       user-frontend.md: shadow=c6cb77d1649f HEAD=20024f144e47
[DRIFT]       uship-quotes.md: shadow=b6cae9667e42 HEAD=5f0fa1a754a5

checked 233 shadow(s): 126 clean, 107 drifted
```

## 2026-08-24T09:01:47+03:00

```
[DRIFT]       aaag-integration.md: shadow=7472e8605302 HEAD=ab9a61f40b96
[DRIFT]       argo.md: shadow=bec1e1dce9de HEAD=9a44609bc245
[DRIFT]       asg-checkout-spa.md: shadow=3252f7514419 HEAD=a0ffbccb9076
[DRIFT]       attachment-backend.md: shadow=2c97fc11853b HEAD=50e6583bc200
[DRIFT]       autoims-backend.md: shadow=aebc0aa42bc5 HEAD=47e2f9408877
[DRIFT]       automation.md: shadow=04bcafd4451d HEAD=b25042b14e6e
[DRIFT]       axe-call-integration.md: shadow=777e18467d06 HEAD=d9a2609969f7
[DRIFT]       backoffice-backend.md: shadow=f521aa5dda88 HEAD=f11dcb21280b
[DRIFT]       backoffice-frontend.md: shadow=2e3fa47c2b0f HEAD=6c1bde31e386
[DRIFT]       bi-databricks-backend.md: shadow=aec9796f152d HEAD=679ca311e642
[DRIFT]       carrier-order-importer-frontend.md: shadow=c62e5767e99e HEAD=861e36cbf9ce
[DRIFT]       carrier-packages-frontend.md: shadow=ea97b6cd0443 HEAD=4ea5e8a82006
[DRIFT]       chase-driver-tracking-frontend.md: shadow=7f7bc1fa67bf HEAD=f784a66d187e
[DRIFT]       chat-backend.md: shadow=634d4330590a HEAD=978961435b67
[DRIFT]       chat-frontend.md: shadow=17acf187444d HEAD=5b4b876063e9
[DRIFT]       claude-code-plugins.md: shadow=0d9859ce27a4 HEAD=b14d641fc1a7
[DRIFT]       command-executor.md: shadow=eaf4febacd0c HEAD=90c3994f3f6b
[DRIFT]       commons.md: shadow=ea8557cf6a72 HEAD=10dbbbf0071d
[DRIFT]       contract-pricing-backend.md: shadow=8aa940c5e7a4 HEAD=8b2c5d7b7801
[DRIFT]       contract-pricing-frontend.md: shadow=c2a1f6c583e2 HEAD=d1c0f7eee302
[DRIFT]       crm-workflows.md: shadow=14dc9616c8bf HEAD=8c307ca35354
[DRIFT]       ctms-frontend.md: shadow=27ea6a8196eb HEAD=9babc645247e
[DRIFT]       cube.md: shadow=b11137cbc685 HEAD=1045bb3b1cfb
[DRIFT]       dataone.md: shadow=6f3ecde0358d HEAD=04fc9814fede
              -> marked status: stale
[DRIFT]       dev-hub.md: shadow=8852ecc4a9eb HEAD=3103ade205b8
[DRIFT]       devops-helpers.md: shadow=6ff262a070f7 HEAD=2d419e5eba0d
              -> marked status: stale
[DRIFT]       devops-tf-live-atlantean-field-175514.md: shadow=9b18130089cf HEAD=740b8fde7350
[DRIFT]       devops-tf-live-shipcars-development-env.md: shadow=65ae5c90d78b HEAD=ac360724fa55
[DRIFT]       devops-tf-live-shipcars-gcp-projects-access.md: shadow=4d4d4f552a6c HEAD=a96fddfda70d
[DRIFT]       devops-tf-live-shipcars-logytext-integration.md: shadow=37ade28ea16e HEAD=d294434e1e46
[DRIFT]       devops-tf-live-shipcars-ml-data-dev.md: shadow=510ef56ca8cd HEAD=ad8b96a3e812
[DRIFT]       devops-tf-live-shipcars-ml-data-prod.md: shadow=78d0b7de1b4a HEAD=e48981e4fa2b
[DRIFT]       devops-tf-live-shipcars-ml-data-staging.md: shadow=353283802935 HEAD=8148e789bfad
[DRIFT]       devops-tf-live-shipcars-platform-dev.md: shadow=8a1b4e4a520e HEAD=e98ee6845695
[DRIFT]       devops-tf-live-shipcars-platform-prod.md: shadow=d110047d2622 HEAD=4f10290c45ee
[DRIFT]       devops-tf-live-shipcars-platform-qa.md: shadow=0b4fab2fb6fa HEAD=a76115cfb807
[DRIFT]       devops-tf-live-shipcars-platform-staging.md: shadow=b93d990ca6b0 HEAD=f8c5020bd41f
[DRIFT]       devops-tf-live-shipcars-production-env.md: shadow=3575eef1c2be HEAD=152cd426f7c2
[DRIFT]       devops-tf-live-shipcars-sf-lm-dev.md: shadow=7933e9db7854 HEAD=7700e8e48145
[DRIFT]       devops-tf-live-shipcars-sf-lm-prd.md: shadow=3eff8c6c014f HEAD=6ca3bb2e8db0
[DRIFT]       devops-tf-live-shipcars-sf-lm-qa.md: shadow=9af99651d5fc HEAD=94f8239665e1
[DRIFT]       devops-tf-live-shipcars-sf-lm-uat.md: shadow=808f5c6f6b52 HEAD=471fb12f8e4c
[DRIFT]       devops-tf-live-shipcars-system-env.md: shadow=937930febebb HEAD=c6c147da63ff
[DRIFT]       devops-tf-live-shipcars-xa-montway-production.md: shadow=0d03c5a4bade HEAD=fb8d6ce46828
[DRIFT]       devops-tf-module-local-cloudsql-users.md: shadow=3104b2224d51 HEAD=eaa6f57f0c48
[DRIFT]       devops-tf-module-postgres-cloudsql.md: shadow=9364cdefad80 HEAD=9e64a5928786
[DRIFT]       docker-utils.md: shadow=80d5ca64379b HEAD=083a2cfeafb8
[DRIFT]       driveaway-backend.md: shadow=2aa302510bb7 HEAD=5c53c9855ce1
[DRIFT]       driveaway-public-tracking-frontend.md: shadow=afdd89cc0e2a HEAD=e1d8220c535e
[DRIFT]       epod-android.md: shadow=e1a5040383c0 HEAD=e281953c4697
[DRIFT]       epod-ios.md: shadow=d80a8ac5fbce HEAD=f5362a9353ae
[DRIFT]       executive-dashboard-frontend.md: shadow=07f91816bb72 HEAD=b8e096008972
[DRIFT]       gallery-frontend.md: shadow=7fe09b80fb25 HEAD=f3ad1a1dd4cd
[DRIFT]       helm-common-chart.md: shadow=efec6363fe6e HEAD=4ad4093d3733
[DRIFT]       helm.md: shadow=8c08b554782a HEAD=a2b5bcc8ba77
[DRIFT]       import-map-deployer.md: shadow=daff6e9146a0 HEAD=06a5f1ec615a
[DRIFT]       integration-executor.md: shadow=373388e7d729 HEAD=1fb3bd2bee19
[DRIFT]       integrations-backend.md: shadow=48a3a34f8a50 HEAD=ffc9bc6adb9f
[DRIFT]       integrators-data-bridge.md: shadow=e3da48668585 HEAD=188b0b69f203
[DRIFT]       inventory-backend.md: shadow=ad10f97f729a HEAD=bff6db45d1c7
[DRIFT]       inventory-frontend.md: shadow=37377357edf1 HEAD=61a6dfb64324
[DRIFT]       invoices.md: shadow=1765b07648ce HEAD=8811c5e40f4f
[DRIFT]       keycloak-password-reset-link.md: shadow=3d42e1cfac34 HEAD=7d5b6aa71ed5
              -> marked status: stale
[DRIFT]       keycloak-phone-login-plugin.md: shadow=7e2db276d3a4 HEAD=6f82c815cefb
              -> marked status: stale
[DRIFT]       keycloak.md: shadow=dd6613103263 HEAD=6a8637d57c01
              -> marked status: stale
[DRIFT]       knowledge.md: shadow=11a40d060779 HEAD=ad67d198f6cd
[DRIFT]       load-bookmark-backend.md: shadow=e6af5f15a3b8 HEAD=c875a6a61d04
[DRIFT]       load-recommender.md: shadow=5e56fb874426 HEAD=2470b2b7d62e
[DRIFT]       loadboard-backend.md: shadow=25e365033e68 HEAD=e89c9af80414
[DRIFT]       loadboard-frontend.md: shadow=35fec90b1de7 HEAD=70dab849ec3d
[DRIFT]       loadbuilder-backend.md: shadow=3c8c91c29403 HEAD=11f4ca0f35f4
[DRIFT]       location-history-backend.md: shadow=b518d9a759d9 HEAD=764f7672606d
[DRIFT]       location-provider.md: shadow=4596c3656e24 HEAD=9313d7a60e6f
[DRIFT]       metadata.md: shadow=5cfe40609af5 HEAD=288a08b279ed
[DRIFT]       ml-data-hamal.md: shadow=763821754b11 HEAD=db1fad6158ab
[DRIFT]       ml-document-parser.md: shadow=2b613791debd HEAD=da73d9065b29
[DRIFT]       ml-experiments.md: shadow=ab0895c5c68c HEAD=1b2b0d9b17b4
[DRIFT]       ml-service-recommender.md: shadow=c5a969aef0cc HEAD=8087efcd6e57
[DRIFT]       models-lib.md: shadow=2f684ec3959a HEAD=3c43dd1fbcba
[DRIFT]       negotiations-router.md: shadow=054a93436545 HEAD=b5f5ecf63ec2
[DRIFT]       notification-orchestrator.md: shadow=0855a77f23ba HEAD=88b5ffefc53a
              -> marked status: stale
[DRIFT]       payment-backend.md: shadow=06c4dd96743c HEAD=fd4ab4ed5274
[malformed]   platform-backend-data-model.md: missing repo/last-synced-commit
[DRIFT]       platform-backend.md: shadow=b4cb3033aa20 HEAD=7d2092ec5e96
[DRIFT]       platform-frontend.md: shadow=bdcc84e2ed76 HEAD=7e51dc635c63
[DRIFT]       posting-backend.md: shadow=748aa454f28f HEAD=5dad74e1205c
[DRIFT]       posting-frontend.md: shadow=d495168f4ad2 HEAD=97b228e12196
[DRIFT]       public-root-app-frontend.md: shadow=8eccff0845b1 HEAD=55ce49ce868b
[DRIFT]       public-tracking-backend.md: shadow=f2ec60f48272 HEAD=3314908e5152
[DRIFT]       public-tracking-frontend.md: shadow=3c10118c957d HEAD=805ab55d73ed
[DRIFT]       pusher.md: shadow=1f4213b6b541 HEAD=f6a173626aaf
[DRIFT]       quarkus-auto-reflection.md: shadow=73893ab9b930 HEAD=01577ba8b318
              -> marked status: stale
[DRIFT]       quarkus-commons.md: shadow=23ac13807011 HEAD=506da35ae128
[DRIFT]       quarkus-data-migration.md: shadow=7faf22ff6703 HEAD=6cba94762ba0
              -> marked status: stale
[DRIFT]       quarkus-extension-firestore-storage.md: shadow=2bdd17cc7f46 HEAD=75c54e5c5e96
[DRIFT]       quarkus-extension-media-proxy.md: shadow=e0c453287ead HEAD=d9094bf782da
              -> marked status: stale
[DRIFT]       quarkus-extension-persistence.md: shadow=05e0a0695506 HEAD=7ae564798208
              -> marked status: stale
[DRIFT]       quarkus-extension-webclient.md: shadow=efece7068d68 HEAD=5e4799418494
[DRIFT]       quarkus-imperative-boilerplate.md: shadow=b6dd9612f254 HEAD=6ea57c90d60b
[DRIFT]       quarkus-k8s-boilerplate.md: shadow=3faf69567e6d HEAD=048c37b1d888
              -> marked status: stale
[DRIFT]       quarkus-locationprovider-client.md: shadow=197e3fe5fe13 HEAD=5762e8144c83
              -> marked status: stale
[DRIFT]       quarkus-notification-client.md: shadow=528e8fb37cf3 HEAD=1f5a74ce1421
[DRIFT]       quarkus-pubsub.md: shadow=6d7790af17b1 HEAD=a69b7b13e89a
              -> marked status: stale
[DRIFT]       quarkus-request-filter.md: shadow=9cb4dec60529 HEAD=025b6cddce44
[DRIFT]       quarkus-user-syncer.md: shadow=ffec208ae351 HEAD=3fa7b91f51f4
[DRIFT]       quote-manager-backend.md: shadow=41cbbc8a35d0 HEAD=e6676532f4ed
[DRIFT]       saved-search-handler.md: shadow=d870ca3110fd HEAD=56c9223e53eb
[DRIFT]       sc-reusable-workflows.md: shadow=78ed06bbadca HEAD=30b53f68f2e3
[DRIFT]       sdlc-agents.md: shadow=d40d299fc0eb HEAD=55713f15740c
[DRIFT]       settings-frontend.md: shadow=a3491f733f67 HEAD=c7dee90d8184
[DRIFT]       shipcars-quarkus-bom.md: shadow=1016af5a08ca HEAD=29b25f22eb70
[DRIFT]       spring-commons.md: shadow=99b0efcf8f2c HEAD=0eeed7b5bf51
[DRIFT]       syncer.md: shadow=4c0f72febe26 HEAD=4cf49bd44625
[DRIFT]       synclink-backend.md: shadow=0c14795875fc HEAD=f006a87c1d3c
[DRIFT]       toolbox-service.md: shadow=33cf005b31a0 HEAD=8954069698ce
              -> marked status: stale
[DRIFT]       trip-planner-frontend.md: shadow=17ef6f01dec5 HEAD=bdf2a0958e92
[DRIFT]       trip-planner.md: shadow=e01f207ce899 HEAD=ffb50f6f0105
[DRIFT]       ui-commons.md: shadow=6858be6d8432 HEAD=9775591827bc
[DRIFT]       user-activity-tracker.md: shadow=785d14364b7d HEAD=4807eacac37e
              -> marked status: stale
[DRIFT]       user-backend.md: shadow=886f47f6983a HEAD=2e3c5402e225
[DRIFT]       user-frontend.md: shadow=c6cb77d1649f HEAD=07ebe4ad60cc
[DRIFT]       uship-quotes.md: shadow=b6cae9667e42 HEAD=c858aedf7480

checked 233 shadow(s): 111 clean, 122 drifted
```
