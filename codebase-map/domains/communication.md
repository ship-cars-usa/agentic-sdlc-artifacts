---
domain: communication
status: draft
owner-team: unknown
member-services: 12
last-reviewed: 2026-05-12
---

# Domain — communication

## Purpose
Real-time chat, email / push notifications, websocket fanout, and the orchestration that decides what notification fires when. Includes the LLM-backed customer/carrier chat assistant ("Sofia").

## Member services
| Repo | Role | Stack | Status |
|---|---|---|---|
| chat-backend | discussion / chat backend | Java/Spring Boot 3.2.12 | seed |
| chat-frontend | chat UI (single-spa MFE, `@shipcars/chat`) | TS/React 18 + single-spa + Webpack 5 | seed |
| ml-service-chat | LLM-backed chat assistant API | Python 3.9 / FastAPI / Tortoise / OpenAI GPT-4o | seed |
| ml-ui-chat | Streamlit UI for `ml-service-chat /customer/...` ("Sofia") | Python 3.9 / Streamlit 1.27.0 | seed |
| notification-backend | per-channel notification senders (SendGrid / Twilio / Firebase) | Java/Spring Boot 3.2.12 | seed |
| notification-orchestrator | parallel SendGrid path with replicated user/company state via `db-syncer` | Java/Quarkus 3.8.3 | seed |
| quarkus-notification-client | Quarkus extension library — `NotificationClient` published-API contract used by 40+ services | Java/Quarkus 3.27.0 ext | seed |
| pusher | central event-router brain — 10+ Pub/Sub subscriptions, fan-out to 5 channels | Java/Quarkus 3.27.0 | seed |
| socket-server | Keycloak-RS256 WebSocket gateway (modern); Redis adapter on `socket.redis...` | Node + Socket.IO 2.0.4 + Express | seed |
| socket-server-old | legacy HS256 WebSocket gateway (parallel, frozen but deployed); Redis adapter on `main.redis...` | Node + Socket.IO 2.0.4 | seed |
| devops-kubernetes-notificationss | K8s notifications config | Docs/Markdown | stub *(probably belongs in `infrastructure`)* |
| devops-tf-module-google-gke-cluster-notifications | GKE notifications Terraform module | Terraform (module) | stub *(probably belongs in `infrastructure`)* |

## Key flows

**Chat → notification (Spring path):**
1. `DiscussionController` (chat-backend) accepts a chat message.
2. `DiscussionService.save()` persists.
3. `NotificationServiceImpl.broadcastChanges()` makes a **synchronous REST call to `notification-backend`** — **verified P0**: catches `Exception` and only logs (silent loss if notification-backend is down).
4. `@Async publishEmail()` / `sendNotificationForUser()` paths are fire-and-forget without error handlers (P1).

**Event-routing (Pub/Sub path):**
- `pusher` consumes ~10 Pub/Sub subscriptions (`carrierlb`, `posting`, `posting.v2`, `quotemanager.notification`, `usermanagement.user.v2`, `usermanagement.company.v2`, `integrations.events`, `metadata`, `loadboard.events`, …) and decides per-event which channel to use.
- Outbound channels: REST → `notification-backend` (for email/SMS/push delivery), Redis emitter → `socket-server` (for WebSocket), Pub/Sub topics → `notification-orchestrator` (parallel SendGrid path).
- `quarkus-notification-client` is the binary-compat library that 40+ Quarkus services use to **publish** to the central `notification` topic — its synchronous `future.get()` propagates Pub/Sub latency into every caller.

**LLM chat path ("Sofia"):**
1. Customer arrives at `/chat/?token=…&load_id=…`.
2. `ml-ui-chat` (Streamlit) POSTs `/customer/chat/conversation/init` to `ml-service-chat`.
3. `ml-service-chat` (FastAPI) calls OpenAI Chat Completions (`gpt-4o-2024-05-13`, `temperature=0`, `seed=23`) with RAG context from its LlamaIndex Postgres vector store.
4. Same flow for `/question` (Q&A) and `/question/rate` (thumbs vote).
5. Rate-limit enforcement is **per-token** via hardcoded `CARRIER_TOKENS` / `CUSTOMER_TOKENS` whitelist in `settings.py` (DB counters back the per-token quotas).

**WebSocket parallel-paths topology:**
- `socket-server` — Keycloak-RS256 JWTs, joins `user_<id>` / `company_<id>` / `global` rooms, Redis adapter on `socket.redis.shipcars-platform-prod.shipcars.dev`.
- `socket-server-old` — opaque HS256 JWTs, joins arbitrary rooms from JWT claims (no server-side authz), Redis adapter on `main.redis.shipcars-platform-prod.shipcars.dev`.
- **Different Redis clusters → not a single broadcast bus.** `pusher`'s Redis-emitter target determines which gateway sees its broadcasts; needs confirmation whether one or both are targeted.

**Chat-frontend bridge:**
- `chat-frontend` (`@shipcars/chat` single-spa MFE) does **not** open its own WebSocket. Its `SocketService` subscribes to DOM `CustomEvent`s under `new_socket_events.*`. The parent shell owns the actual WebSocket and re-dispatches events on `document`. If `ChatUpdated` events stop arriving, the bug is upstream of this repo.

## Data stores
- `chat-backend`: `chat` PG, HikariCP `maximum-pool-size=5` (way too small for a chat service).
- `notification-backend`: `notification` PG, HikariCP **5 (hardcoded)** — same pool-size flag.
- `notification-orchestrator`: `notification_orchestrator` PG (16) + `usermanagement` PG (reactive, replica).
- `pusher`: `pusher` PG (10) + read-only on `ctms-db` (10) + `usermanagement-db` (10).
- `ml-service-chat`: `ml_service_chat` PG (Tortoise 10/10, twice — two logical apps on same DB) + LlamaIndex Postgres vector store + **`production` PG as user `rateengine` (shadow caller; ADR-0003 contract not yet drafted)**.
- `ml-ui-chat`: none — pure UI, `st.session_state` only.
- `socket-server` / `socket-server-old`: Redis only (volatile rooms; **different clusters**).
- `chat-frontend`: none.

## Cross-cutting concerns
- `chat-backend` is **Spring Boot, not Quarkus** — `PROJECTS_INDEX.md` miscategorizes.
- **Two socket-server repos are not a migration in progress — they are parallel auth schemes** (Keycloak-RS256 vs. legacy HS256). Retirement of `socket-server-old` is gated on migrating remaining HS256 clients.
- **`notification-backend` (Spring) + `notification-orchestrator` (Quarkus) are parallels, not a stack** — they both subscribe to Pub/Sub and both reach SendGrid; `notification-orchestrator` does **not** call `notification-backend`. The boundary needs an explicit owner decision.
- **The communication domain holds the fleet's central binary-compat dependency** (`quarkus-notification-client`, 40+ consumers). Its synchronous `future.get()` makes every caller pay Pub/Sub latency. Highest-leverage async-ification target in the fleet.
- **Pool-size hygiene is concerning across the domain**: `chat-backend` 5, `notification-backend` 5, `pusher` 3×10. All sit on the request path of fleet-wide fanout.

## P0 / fleet-significant findings surfaced in this domain
- **`socket-server-old`**: HS256 JWT signing secret is committed to git as a plaintext literal — identical in `index.js` and `helm/.../values-{dev,qa,staging,production}.yaml`. Anyone with read access can forge JWTs accepted by any environment. Has not been rotated since the 2022-11-29 init commit. **Compensating control**: move to `gcp-secret-manager`/`externalSecrets` and rotate. Full retirement requires client-side Keycloak-JWT migration.
- **`chat-backend → notification-backend`**: synchronous REST call with `catch(Exception)` + log-only — silent notification loss on `notification-backend` downtime.
- **`notification-backend.NotificationConsumer.java:126`**: silent-ack on exception (P0 carried from earlier review).
- **`ml-service-chat`**: `openai==1.30.1` dep + `openai.ChatCompletion.acreate(...)` call site — incompatible APIs (v0 surface removed in v1). Verify runtime path is alive.
- **`ml-ui-chat`** + **`chat-frontend`**: REST clients (`requests.post()` / `axios.create()`) without timeout — same anti-pattern as the Quarkus fleet, but at the Python and browser layers.

## Open questions / known gaps
- `notification-backend` ↔ `notification-orchestrator` boundary — which channels / subscriptions belong to which? Empirically parallel today; intentionally?
- Does `pusher` publish to **one or both** Redis clusters (i.e., does it broadcast to `socket-server` only, or to `socket-server-old` as well)? The two clusters mean the question is real.
- Which clients still use HS256 JWTs against `socket-server-old`? Until that population is known, retirement is unplannable.
- `ml-service-chat`'s **`db-source` shadow-caller edge into `rateengine`'s `production` PG** has no ADR-0003 contract draft yet. Action: draft `db-contracts/ml-service-chat--rateengine-production-pg.md` and identify the column set being read.
- `devops-kubernetes-notificationss` and `devops-tf-module-google-gke-cluster-notifications` are name-matched into `communication` but are infra config; probably should be re-domained `infrastructure`.

## Related ADRs
- `~/projects/codebase-map/adr/0003-cross-service-db-read-policy.md` — applies to `ml-service-chat`'s new shadow-caller edge.
- `~/projects/codebase-map/adr/0005-rateengine-eol-rewrite.md` — `ml-service-chat`'s `db-source` migrates with `rateengine`.
- Fleet review: `~/projects/quarkus-fleet-review-2026-05-07.md#4-chat-backend` for `chat-backend` depth.

## Coverage
**10 of 12 shadows are `seed`** as of 2026-05-12 (was 6/12 before Phase 4.14). Remaining 2 stubs are devops/Terraform repos that are arguably miscategorized into this domain. **The communication domain is catalog-complete for active services.**
