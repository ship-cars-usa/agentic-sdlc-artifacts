# Data Stores

Which services own / read / write which data store. Rolled up from the **72 seed shadow docs** as of 2026-05-12 (Phase 4.14 completed the communication-domain depth pass); rows added as new seeds land.

## Conventions

- `mode` is one of: `owns` (this service is the only writer), `writes` (one of multiple writers), `reads` (read-only / replicated).
- `kind` is one of: `Postgres-db`, `Postgres-schema`, `Mongo-collection`, `Redis-keyspace`, `Elasticsearch-index`, `GCS-bucket`, `etcd-prefix`, `Pub/Sub-topic`, `Kafka-topic`.
- `evidence` is `path:line` or `shadow:<repo-name>`.
- HikariCP / Quarkus `jdbc.max-size` column captures the **prod or default** value when explicit; `?` when not surfaced.

## Postgres stores

| Service | DB / schema | Pool (`jdbc.max-size` / `maximumPoolSize`) | Audit | Mode | Evidence |
|---|---|---|---|---|---|
| `aaag-integration` | `aaag` PG | 16 (default) | – | owns | shadow:aaag-integration |
| `apache-camel-etl-demo` | dual PG (`shipcars` source 5002 → target 6002) | 16 / 16 | – | reads+writes (demo) | shadow:apache-camel-etl-demo |
| `axe-call-integration` | `axe_call_integration` PG | 16 (dev) | Envers | owns | shadow:axe-call-integration |
| `cube` | `cube` PG + secondary `usermanagement` PG | 16 (main) | – | owns + reads | shadow:cube |
| `dataone` | `dataone` PG (vehicle catalog) | **4** | – | owns | shadow:dataone |
| `ai-dashboard-backend` | `aidashboard` PG | 16 | – | owns | shadow:ai-dashboard-backend |
| `attachment-backend` | `attachment` PG | 16 (dev) | – | owns | shadow:attachment-backend |
| `autoims-backend` | `autoims` PG via `CONFIG_DB_JDBC_URL` | **10** | – | owns | shadow:autoims-backend |
| `bi-databricks-backend` | (Databricks; see below) | n/a | – | reads | shadow:bi-databricks-backend |
| `chat-backend` | `chat` PG | 20 | – | owns | shadow:chat-backend |
| `contract-pricing-backend` | `contractpricing` PG | 16 | – | owns | shadow:contract-pricing-backend |
| `driveaway-backend` | `driveaway` PG | **10** | Envers | owns | shadow:driveaway-backend |
| `fraud-detector` | `frauddetector` PG | 16 (dev) | – | owns | shadow:fraud-detector |
| `integrations-backend` | `integrations` PG | 16 | – | owns | shadow:integrations-backend |
| `integrators-data-bridge` | central target PG (writes) | 16 | – | writes | shadow:integrators-data-bridge |
| `integrators-data-bridge` | `posting-backend` PG | – | – | **reads** | `services/.../posting/LoadLegProcessor.java:117` |
| `integrators-data-bridge` | `inventory-backend` PG | – | – | **reads** | shadow:integrators-data-bridge |
| `integrators-data-bridge` | `autoims-backend` PG | – | – | **reads** | `services/.../autoims/AutoImsProcessor.java:99` |
| `integrators-data-bridge` | `contract-pricing-backend` PG | – | – | **reads** | shadow:integrators-data-bridge |
| `integration-executor` | `integration_executor` PG | default | – | owns | shadow:integration-executor |
| `inventory-backend` | `inventory` PG | 20 | Envers | owns | shadow:inventory-backend |
| `invoices` | `invoices` PG | 16 (dev) | Envers | owns | shadow:invoices |
| `lead-parser` | MySQL via `datasource_*` env vars | ? (default) | – | owns | shadow:lead-parser |
| `load-bookmark-backend` | `loadbookmark` PG | **4 (prod) / 16 (dev)** | – | owns | shadow:load-bookmark-backend |
| `load-recommender` | `loadrecommender` PG | 16 | – | owns | shadow:load-recommender |
| `load-recommender` | `usermanagement` PG (replica) | reactive 10 | – | reads | shadow:load-recommender |
| `loadboard-backend` | `loadboard` PG | 20 | – | owns | shadow:loadboard-backend |
| `loadbuilder-backend` | **GCS as primary store** *(serialized Java + JSON, optimistic locking via version field)* | n/a | – | **owns (GCS, not PG)** | shadow:loadbuilder-backend |
| `location-history-backend` | `locationhistory` PG (6 tables with PostGIS-style POINT type) | **4 (prod) / 16 (dev)** | – | owns | shadow:location-history-backend |
| `ml-service-dispatcher` | `mldispatcher` PG (`fetched_vehicle` cache, `model_prediction`, etc.) | Tortoise `maxsize=5` | – | owns | shadow:ml-service-dispatcher |
| `ml-bot-order-v2` | PG (`incoming_requests`, `ingest_requests_log`, `extraction_results`, `attachment_records`, `pubsub_events_log`) | Tortoise default | – | owns | shadow:ml-bot-order-v2 |
| `ml-demand-forecasting` | sink PG (`ppm_fc`, `lpc_fc`, `rr_fc`) + reads source production PG | n/a (batch) | – | writes + **reads upstream** | shadow:ml-demand-forecasting |
| `ml-bot-order` *(v1)* | `mlbotorder` PG (Tortoise: `sms_request`, `email_request`, `incoming_event_log`, ...) | Tortoise `maxsize=10` | – | owns | shadow:ml-bot-order |
| `ml-document-parser` | `mldocparser` PG | Tortoise `min=10 / max=10 / idle=120s` | – | owns | shadow:ml-document-parser |
| `ml-pricing-app` *(batch + Streamlit)* | `MONITORING` PG *(matched_orders_to_predictions)* + reads `MONTWAY` MySQL + `RATE_ENGINE` PG | n/a | – | writes + **reads upstream** | shadow:ml-pricing-app |
| `ml-model-rate` | (none — in-memory models, GCS for artifacts at startup) | – | – | – | shadow:ml-model-rate |
| `uship-quotes` | `uship_quotes` PG | 16 (dev) | Envers | owns | shadow:uship-quotes |
| `negotiations-router` | (none — stateless) | – | – | – | shadow:negotiations-router |
| `api-gateway` | Redis (rate-limit counters + legacy tokens) | – | – | owns | shadow:api-gateway |
| `company-documents` | `companydocuments` PG (sync SQLAlchemy / psycopg2) | SQLAlchemy defaults | – | owns | shadow:company-documents |
| `ml-service-listener` | `mllistener` PG (event sink) | Tortoise `maxsize=10` | – | owns | shadow:ml-service-listener |
| `ml-service-recommender` | `mlrecommender` PG + `recommender` PG (dual) | Tortoise `maxsize=10 / 5` | – | owns | shadow:ml-service-recommender |
| `loadboard-backend` | `users` PG (secondary) | 20 | – | reads | shadow:loadboard-backend |
| `loadboard-backend` | `ctms` PG (secondary) | 20 | – | reads | shadow:loadboard-backend |
| `location-provider` | `route_distance` PG | **4** | – | owns | shadow:location-provider |
| `metadata` | `metadata` PG | 16 (dev) | – | owns | shadow:metadata |
| `notification-backend` | `notification` PG | **5 (hardcoded)** | – | owns | shadow:notification-backend |
| `notification-orchestrator` | `notification_orchestrator` PG | 16 | – | owns | shadow:notification-orchestrator |
| `notification-orchestrator` | `usermanagement` PG (replica) | reactive 10 | – | reads | shadow:notification-orchestrator |
| `payment-backend` | `payment` PG | 16 | – | owns | shadow:payment-backend |
| `posting-backend` | `posting` PG | 20 | – | owns | shadow:posting-backend |
| `pusher` | `pusher` PG (primary) + `ctms-db` + `usermanagement-db` (read replicas) | **10 / 10 / 10** | – | owns + reads | shadow:pusher |
| `public-tracking-backend` | `publictracking` PG | **5** | – | owns | shadow:public-tracking-backend |
| `quote-manager-backend` | `quotemanager` PG | 16 | – | owns | shadow:quote-manager-backend |
| `rateengine` | `rateengine` PG (Django ORM) | Django defaults | – | owns | shadow:rateengine |
| `saved-search-handler` | `savedsearch` PG (3 datasources: main + users + ctms) | ? | – | owns | shadow:saved-search-handler |
| `syncer` | (reads 6 other services' PGs reactively, `max-size=4` each — see shadow-caller note) | reactive 4 × 6 | – | **reads** | shadow:syncer |
| `synclink-backend` | `synclink` PG | 16 (dev) | Envers | owns | shadow:synclink-backend |
| `trip-planner` | `trip_planner` PG | Quarkus default 20 | – | owns | shadow:trip-planner |
| `trip-planner` | `usermanagement` PG (replica) | reactive 10 | – | reads | shadow:trip-planner |
| `trip-planner` | `ctms` PG (secondary) | reactive 10 | – | reads | shadow:trip-planner |
| `user-activity-tracker` | `useractivitytracker` PG | 16 (dev) | – | owns | shadow:user-activity-tracker |
| `user-backend` | `usermanagement` PG | 20 | – | owns | shadow:user-backend |
| `ml-service-chat` | `ml_service_chat` PG (Tortoise; `default` + `customer_default` connections to same DB) | Tortoise 10 / 10 each | – | owns | shadow:ml-service-chat |
| `ml-service-chat` | `production` PG as user `rateengine` (via `db-source` connection — **shadow caller**) | Tortoise 5 / 5 | – | **reads** | shadow:ml-service-chat |

### Pool-size outliers (worth a one-pass right-sizing review)

| Service | Pool | Risk |
|---|---|---|
| `notification-backend` | **5 (hardcoded)** | Highest-fanout REST callee; under burst, pool exhaustion is the first failure mode |
| `public-tracking-backend` | **5** | Public-facing; vulnerable to traffic spikes (shared customer links) |
| `dataone` | **4** | **One of the highest-fanout read-only callees** (8 inbound); cache miss → tiny pool fronts Caffeine |
| `load-bookmark-backend` | **4 (prod)** | Almost certainly a copy-paste oversight; raise to 16 |
| `location-history-backend` | **4 (prod)** | Read directly by `syncer` (shadow caller); pool exhaustion affects ES sync |
| `location-provider` | **4** | Cached behind ES+Redis, but cache miss → 4-pool sync to Maps |
| `autoims-backend` | **10** | TODO in repo asks for tuning |
| `driveaway-backend` | **10** | Same fleet-norm under-sizing risk |

## Redis keyspaces

| Service | Keyspace / use | Mode | Evidence |
|---|---|---|---|
| `impersonator` | `company::<id>` / `user::<id>` access-token cache | owns | shadow:impersonator |
| `location-provider` | Maps result cache | owns | shadow:location-provider |
| `posting-backend` | Bucket4j rate-limiting via ehcache (not Redis) | local | shadow:posting-backend |
| `public-tracking-backend` | reCAPTCHA attempt counts (implied) | owns | shadow:public-tracking-backend |
| `rateengine` | django-redis cache + sessions | owns | shadow:rateengine |
| `socket-server` | Socket.IO adapter + `@socket.io/redis-emitter` cluster bus on `socket.redis.shipcars-platform-prod.shipcars.dev` | reads/writes | shadow:socket-server |
| `socket-server-old` | Socket.IO adapter on `main.redis.shipcars-platform-prod.shipcars.dev` (DB `/3`) — **different Redis cluster from `socket-server`** | reads/writes | shadow:socket-server-old |
| `cube` | reactive Redis pool (`max-pool-size=10000`, `max-pool-waiting=10000`) | owns | shadow:cube |
| `syncer` | reactive Redis pool (`max-pool-size=10000`, `max-pool-waiting=10000`) | owns | shadow:syncer |
| `user-activity-tracker` | HyperLogLog (unique-user counts, 30d TTL) + dedup keys (1h TTL) | owns | shadow:user-activity-tracker |

## Elasticsearch indices

| Service | Index / use | Mode | Evidence |
|---|---|---|---|
| `location-provider` | Maps cache index | owns | shadow:location-provider |
| `rateengine` | Quote audit / search (legacy) | owns | shadow:rateengine |
| `saved-search-handler` | **Percolate index** (saved-query reverse-index, size=10000 hardcoded) | owns | shadow:saved-search-handler |
| `syncer` | Fleet-wide ES indexes for postings / carriers / loadboard / saved-search / location / metadata / trip-planner *(bulk writes, eventual consistency)* | owns | shadow:syncer |
| `cube` | ES read-query backend for loadboard search *(per README)* | reads | shadow:cube |
| `ml-service-dispatcher` | Audit-log index (`AUDIT_LOGGER_URL`) | writes | shadow:ml-service-dispatcher |

## GCS buckets / blob stores

| Service | Bucket | Mode | Evidence |
|---|---|---|---|
| `attachment-backend` | `shipcars-platform-dev-media` (env-overridable) | owns | shadow:attachment-backend |
| `loadbuilder-backend` | `CONFIG_DB_BUCKET` (**entity storage**) + `CONFIG_MEDIA_BUCKET` | **owns (as DB)** | shadow:loadbuilder-backend |
| `media-proxy` | (proxies to GCS via service account) | reads | shadow:media-proxy |
| `posting-backend` | dispatch-sheet PDF output (Temporal worker) | writes | shadow:posting-backend |
| `user-activity-tracker` | `USER_ACTIVITY_TRACKER_GCS_BUCKET` (Parquet archive) | owns | shadow:user-activity-tracker |

## etcd / other K/V

| Service | Prefix / use | Mode | Evidence |
|---|---|---|---|
| `load-bookmark-service` | `<prefix>/<carrier>/<load_id>` (bookmark JSON; `eval()` on reads — P0) | owns | shadow:load-bookmark-service |

## External / SaaS data stores

| Service | Store | Mode | Evidence |
|---|---|---|---|
| `bi-databricks-backend` | Databricks Workspace | reads | shadow:bi-databricks-backend |
| `ai-dashboard-backend` | Databricks SQL Warehouse | reads | shadow:ai-dashboard-backend |
| `payment-backend` | Stripe (customer + payment-method state) | reads/writes | shadow:payment-backend |
| `payment-backend` | RoadSync | writes | shadow:payment-backend |
| `notification-backend` | SendGrid suppression lists / contact lists | writes | shadow:notification-backend |

## Notable cross-service patterns

- **`integrators-data-bridge` directly reads four other services' Postgres** (`posting-backend`, `inventory-backend`, `autoims-backend`, `contract-pricing-backend`). Source services have no awareness; schema migrations there can silently break the bridge.
- **`syncer` is the second-largest direct-PG reader** — reads from 6 other services' PostgreSQL DBs (`lm-posting`, `saved-search`, `platform/lbv3`, `location-history`, `metadata`, `trip-planner`) into Elasticsearch. Same coordination risk as the bridge.
- **`pusher` holds read-only connections to `ctms-db` and `usermanagement-db`** for routing-decision lookups (smaller scope but same pattern).
- **`ml-demand-forecasting` reads a source production PG** for historical metric ingestion. Shadow-caller edge; draft contract published.
- **`ml-pricing-app` reads `MONTWAY` MySQL + `RATE_ENGINE` PG** for daily pricing-accuracy matching (added 2026-05-12). Two more shadow-caller edges; no contract draft yet.
- **`ml-service-chat` reads `rateengine`'s `production` PG as user `rateengine`** via Tortoise's `db-source` connection (added 2026-05-12, Phase 4.14). Subject to ADR-0003; **no contract draft yet**. Ties to ADR-0005 (`rateengine` EOL rewrite) — when `rateengine` moves off Django 2.1.7, this read path must move with it.
- Net: **15 cross-service direct-DB-read edges** total. **ADR-0003 (`adr/0003-cross-service-db-read-policy.md`) is the proposed policy**; **8 contract drafts** are now in `relations/db-contracts/`; **1 unsanctioned edge** still needs a contract (`ml-service-chat → rateengine.production`). Each draft has a column-list TODO requiring reader-owner human input to close.
- **Replicated `usermanagement-db` is read by three services** (`load-recommender`, `notification-orchestrator`, `trip-planner`) via `db-syncer` modules — all reactive, all max-size=10. If the replica lags, user/company context goes stale fleet-wide.
- **`ctms` PG is read by three services** (`loadboard-backend`, `saved-search-handler`, `trip-planner`) as a secondary datasource. CTMS itself is a legacy Django system; these reads are migration scaffolding. Should be retired with CTMS.
- **Pool-size hygiene is uneven**: 6 services run with `max-size ≤ 10`, which is below the fleet norm of 16–20. `notification-backend` (5, hardcoded), `load-bookmark-backend` (4 prod), `location-provider` (4), and `public-tracking-backend` (5) are the most concerning given each one's call pattern.
- **Audit-table coverage is incomplete**: only `driveaway-backend`, `inventory-backend`, and `invoices` use Hibernate Envers. For services with compliance exposure (`payment-backend`, `user-backend`, `notification-backend`) the lack of an audit table means change history depends on Pub/Sub event retention.

## Open questions

- Many shadow docs report `quarkus.datasource.jdbc.url=postgres://...` but don't surface the cluster name. Mapping URL → cluster needs the `devops-tf-live-*` Terraform repos.
- Multi-tenant services likely share a Postgres cluster but own distinct schemas; cluster vs. schema isn't disambiguated above.
- Whether `loadboard-backend`'s 3 PGs are 3 clusters or 3 schemas on one cluster isn't visible from the shadow alone — confirm with ops.
