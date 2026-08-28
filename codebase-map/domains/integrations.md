---
domain: integrations
status: draft
owner-team: unknown
member-services: 16
last-reviewed: 2026-05-12
---

# Domain — integrations

## Purpose
Brokers between Ship.Cars and external SaaS / data providers. Each service owns the conversation with one partner — taking inbound webhooks, calling outbound REST APIs, mapping wire formats to internal events.

## Member services
| Repo | Role | Stack | Status |
|---|---|---|---|
| aaag-integration | Async command executor for ASI / Auction Edge | Java/Quarkus 3.20.4 | seed |
| aaag-integration-logs-ARCHIVED | archived AAAG log shipper (Pub/Sub → AAAG REST) | Python | seed *(archive)* |
| aaag-poc | AAAG proof of concept (GCP Pub/Sub ↔ AWS SQS bridge); successor is `aaag-integration` | Python | seed *(archive-candidate)* |
| autoims-backend | AutoIMS sync (re-domained pricing-billing → integrations 4.7) | Java/Spring Boot 3.2.12 | seed |
| axe-call-integration | Axe call integration; rare fleet-good pattern (timeout + retry + CircuitBreaker) | Java/Quarkus 3.27.0 | seed |
| command-executor | Inbound integration command processor (Acertus, CarsArrive, SuperDispatch, EDI Orderful → impersonator → posting) | Java/Quarkus 3.20.2.2 | seed |
| integration-executor | Outbound integration message router to 7 external platforms | Java/Quarkus 3.20.4 | seed |
| integrations-backend | Multi-tenant gateway (logytext, quickbooks, axe, twilio) | Java/Quarkus 3.15.2 | seed |
| integrators-data-bridge | Camel ETL bridge across 4 source DBs | Java/Quarkus 3.20.2.2 | seed |
| ml-bot-order | v1 LLM order-import bot (legacy `google-genai` SDK; retire per ADR-0006) | Python | seed |
| ml-bot-order-v2 | v2 LLM order-import bot (LiteLLM / Gemini); the `oib-outbound-*` topic source | Python | seed |
| quarkus-user-syncer | `db-syncer` Quarkus extension library | Java/Quarkus 3.27.0 | seed |
| syncer | Second-largest direct-PG-reader in the fleet (6 upstream PGs → ES) | Java/Quarkus 3.27.0 | seed |
| synclink-backend | Chrome-extension load-state sync to posting | Java/Quarkus 3.27.0 | seed |
| webhook-relay | Stateless GitHub-webhook gateway (HMAC + IP whitelist + fan-out) | Go | seed |
| devops-tf-live-shipcars-logytext-integration | Terraform live env (Pub/Sub + IAM) for the Logytext integration; **suggest re-domain to `infrastructure`** | Terraform (live env) | seed |

## Key flows (verified)
**Auction Edge inbound (aaag-integration):**
1. `AuctionEdgePubSubListener` consumes a Pub/Sub message.
2. Optimistic-versioning + distributed lock (`LoadLegProcessingLockStorageEntity`) defuses redelivery.
3. `AsiPushServiceImpl` pushes outbound to ASI GraphQL with `@Retry(5×, 250ms)` (no jitter, no timeout).
4. `eventBus.send()` fans out to internal consumers.

**Logytext / QuickBooks / Axe / Twilio (integrations-backend):**
- Each is a separate Maven module under `integrations-backend`.
- Logytext + Axe inbound are Pub/Sub-routed; Logytext **does not verify webhook authenticity** (P0).
- QuickBooks token-refresh + downstream operation are **not transactionally atomic** (P0).
- Datasource max-size = 4 in production (alarmingly small).

**Integrators data bridge (integrators-data-bridge):**
- 4 Apache Camel routes pull from 4 source DBs (posting, inventory, autoims, contract-pricing) into a centralized target.
- 5 datasources × `jdbc.max-size=16` = 80 pooled connections, no `acquisition-timeout` set (P0).
- `LoadLegProcessor.java:133, :148` do `SELECT * FROM <table>` with no `LIMIT` — OOM risk on first sync of any large table (P0).

## Data stores
- `aaag-integration`: Postgres (LoadLegProcessingLockStorageEntity, Envers audit).
- `integrations-backend`: Postgres (per-module entity tables; `assistant_call_record` has unique `call_id`).
- `integrators-data-bridge`: 4 source PostgreSQL databases (read-only) + 1 target PostgreSQL (write).

## Cross-cutting concerns
- **Webhook authenticity is uneven** — Logytext and Axe consume Pub/Sub webhook events without HMAC verification. Add `quarkus-commons` HMAC validator.
- **Pub/Sub error semantics are inconsistent** — `AuctionEdgePubSubListener` and `AxeWebhookPubSubConsumer` are reasonable templates; `LogytextPubSubConsumer` swallows exceptions and silently drops messages.
- **REST timeouts systematically missing** — confirmed in `aaag-integration`, `integrations-backend`. Likely also in `axe-call-integration`, `command-executor`, `integration-executor`.

## Open questions / known gaps
- ~~`aaag-integration` (Java) vs. `aaag-poc` (Python) — is the POC superseded?~~ — resolved (Phase 4.19): yes, `aaag-poc` and `aaag-integration-logs-ARCHIVED` are both legacy. The productionized `aaag-integration` Quarkus service is canonical. Both Python repos belong in `infrastructure-triage.md`'s archive-candidate list.
- ~~`command-executor` vs. `integration-executor` — what's the split?~~ — resolved (Phase 4.19): `command-executor` is the **inbound** processor (consumes external-webhook Pub/Sub subscriptions from Acertus / CarsArrive / SuperDispatch / EDI Orderful → translates → calls `posting-backend` via `impersonator`); `integration-executor` (seeded Phase 4.9) is the **outbound** message router to 7 external platforms. They're complementary halves of the integration surface.
- ~~`syncer` vs. `quarkus-user-syncer`~~ — resolved (Phase 4.9): `quarkus-user-syncer` is a **library/extension** providing the `db-syncer` pattern used by Quarkus services; `syncer` is a **standalone service** that reads 6 upstream PGs into Elasticsearch.
- `devops-tf-live-shipcars-logytext-integration` is currently in `integrations` by name-match but is pure IaC supporting the Logytext integration. **Recommended re-domain to `infrastructure`** alongside other `devops-tf-live-*` repos.

## Related ADRs
- `~/projects/codebase-map/adr/0003-cross-service-db-read-policy.md` — applies to `integrators-data-bridge` (4 contracts drafted) and `syncer` (multi-source contract drafted).
- `~/projects/codebase-map/adr/0006-ml-bot-order-v1-retirement.md` — phases v1 out in favor of v2.
- Fleet review: `~/projects/quarkus-fleet-review-2026-05-07.md` covers 3 of the integrations services in depth (`aaag-integration`, `integrations-backend`, `integrators-data-bridge`).

## Coverage
**16 of 16 shadows are `seed`** — integrations domain is **catalog-complete** as of 2026-05-12 (Phase 4.19). Two of the seeds are explicit archive-candidates (`aaag-poc`, `aaag-integration-logs-ARCHIVED`); one (`devops-tf-live-shipcars-logytext-integration`) is recommended for re-domain to `infrastructure`. All 13 active services have full seed-quality shadow docs.
