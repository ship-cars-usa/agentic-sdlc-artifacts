---
repo: payment-backend
path: ~/projects/ship-cars-usa/payment-backend
stack: Java 21 / Quarkus 3.27.5
domain: pricing-billing
shape: multi-module (12 poms)
last-synced-commit: 40d0bfe3ebb2ccd45276513fe03762ebc9d7c5ab
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# payment-backend

## What it is
Quarkus 3.27.5 / Java 21 service that owns payment methods, bank accounts, transactions, one-time payments, and the Stripe + RoadSync integrations. Receives Stripe webhooks via `StipeWebhookController` (typo real, see below) and RoadSync webhooks via `RoadSyncController`, validates signatures, and processes lifecycle events. Manages per-company config and bank-account records, syncs funding sources / payees with RoadSync, and fans out internal payment-state events over Pub/Sub. The Stripe→Pub/Sub events that `user-backend.PaymentBackendConsumer` consumes originate here.

## How it fits
- Consumes API of: `user-backend` (`@RegisterRestClient(configKey="user-management")`), RoadSync (external, `@RegisterRestClient(configKey="roadsync-api")`), Stripe (via `StripeClient` wrapping the Stripe SDK).
- Publishes events to: Pub/Sub topics `config.pubsub.topics-payment-notification` (one-time payment created), `topics-payment-update` (Stripe webhook state changes), `topics-transaction-update`, `topics-bank-account-update` (via `BankAccountEventPublisher`, CREATED/UPDATED/DELETED). Also uses the notification extension topic `ship.cars.notification.topic`.
- Subscribes to: `config.pubsub.subscription-bank-account-update` — `BankAccountUpdatePubSubDto` from `user-backend`, via `BankAccountUpdatePubSubListener`.
- Owns data store: PostgreSQL (`payment` db) — `company_configs`, `company_bank_accounts`, `transactions`, `roadsync_payees`, plus Hibernate Envers audit (`revinfo` + `_aud` tables, `CustomRevisionListener`).

## Build / test / run
```
mvn clean install
mvn clean test
mvn clean verify -Pnative
quarkus dev
# 12 poms: root + api-dtos, api-enums, application, commons, configuration,
#          coverage-report, db-entities, db-migration, repositories, resources, services
```

## Key abstractions
- `StipeWebhookController` — `resources/src/main/java/cars/ship/payment/rest/v1/StipeWebhookController.java` — `processWebhookEvent` / `processWebhookConnectEvent` (verifies `stripe-signature`). *Class and filename both misspell "Stipe" — real, still current.*
- `RoadSyncController` — `resources/.../rest/v1/RoadSyncController.java` — reads raw body + `svix-id`/`svix-timestamp`/`svix-signature` headers (NEW, SCP-0000 #243); unverified → 403.
- `SvixSignatureVerifier` — `services/.../services/utils/SvixSignatureVerifier.java` — `base64(HMAC-SHA256(base64decode(secret), "{id}.{ts}.{body}"))` + timestamp-tolerance check for RoadSync webhooks.
- `RoadSyncWebhookServiceImpl` — `services/.../services/impl/RoadSyncWebhookServiceImpl.java` — `verifySignature` gated by `verificationEnforced()` (see gotchas).
- `StripeWebhookServiceImpl` (iface `StripeWebhookService`) — Stripe charge/customer/subscription lifecycle; publishes `topics-payment-update` (`StripeWebhookServiceImpl.java:366`).
- `PaymentStripeServiceImpl` / `StripeClient` — `services/.../services/clients/stripe/` — Stripe SDK wrapper (customers, subscriptions, portal).
- `UserManagementRestClient` — `services/.../services/clients/usermanagement/impl/UserManagementRestClient.java:17` — `@Retry(delay=1s, maxRetries=7)` + `@RetryWhen(IsRetryable.class)`, **no `@Timeout`**.
- `RoadSyncClient` — `services/.../services/clients/roadsync/RoadSyncClient.java:34` — `@Retry(delay=1s)` on every method, **no `@Timeout`**.
- `BankAccountUpdatePubSubListener` — `services/.../listeners/BankAccountUpdatePubSubListener.java` — implements `PubSubConsumerBlocking<BankAccountUpdatePubSubDto>`.
- `MessageSenderServiceImpl` — `services/.../services/clients/pubsub/MessageSenderServiceImpl.java` — synchronous Pub/Sub publish via `PubSubPublisherSync`.

## Don't-do-here / gotchas
- **Retry-without-timeout (P0)** — both `user-management` and `roadsync-api` REST clients carry `@Retry` (7 attempts, 1s delay) but no `@Timeout` and no `connect-timeout`/`read-timeout` in `configuration/.../application.properties`. Worst-case latency = attempts × downstream-hang. Fix: set `quarkus.rest-client.<key>.connect-timeout`/`read-timeout` and add `@Timeout`. (Fleet-wide anti-pattern.)
- **RoadSync signature verification can be soft** — `RoadSyncWebhookServiceImpl.verifySignature` is gated by `verificationEnforced()`; when not enforced, an unverified webhook is still processed with only a warning. Confirm `config.roadsync.webhook` is enforced in prod, or spoofed callbacks are accepted.
- **No `@CircuitBreaker` on Stripe/RoadSync calls** — Stripe/RoadSync outages cascade directly into webhook-handler thread pressure.
- **No outbox** — `MessageSenderServiceImpl.send()` is synchronous-but-fire-and-forget; if publish fails after DB commit the payment-state event is lost. No `@Scheduled + ShedLock` outbox as in the Spring services.
- **HikariCP `max-size=16`** only in `%dev` (`application.properties:165`); no `%prod` datasource keys in-repo — prod pool size relies on Quarkus defaults / externalized env. Confirm sizing.
- **Stripe webhook idempotency not visible** — signatures are verified but processed-event-id dedup is not obvious; Stripe at-least-once delivery means duplicate receipts must be guarded.

## Relevant ADRs / docs
- README is the default Bitbucket boilerplate stub — no real content.
- `~/projects/quarkus-rest-client-timeout-anti-pattern.md` — applies directly here (user-management + roadsync-api).
- `relations/rest-client-registry.md#payment-backend` — configKeys + URLs.
- `~/projects/codebase-map/repos/user-backend.md` — `PaymentBackendConsumer` consumes payment-backend's fan-out.


<!-- entities-begin -->
## Entities

Auto-generated by `scripts/cluster_entities.py`. Domain classes declared in this repo:

| Class | Kind | Module | Catalog canonical |
|---|---|---|---|
| `CompanyBankAccountEntity` | jpa | `db-entities` | BankAccount |
| `CompanyConfigEntity` | jpa | `db-entities` | [CompanyConfig](../domains/entities/CompanyConfig.md) |
| `RoadSyncPayeesEntity` | jpa | `db-entities` | RoadSyncPayees |
| `TransactionEntity` | jpa | `db-entities` | [Transaction](../domains/entities/Transaction.md) |
| `BankAccountSocketMessageDto` | dto | `api-dtos` | BankAccountSocketMessage |
| `BankAccountUpdatePubSubDto` | dto | `api-dtos` | BankAccountUpdate |
| `CarrierIntegrationDto` | dto | `api-dtos` | CarrierIntegration |
| `CompanyBankAccountDto` | dto | `api-dtos` | BankAccount |
| `CompanyBankAccountRevDto` | dto | `api-dtos` | CompanyBankAccountRev |
| `CompanyConfigDto` | dto | `api-dtos` | [CompanyConfig](../domains/entities/CompanyConfig.md) |
| `CompanyConfigRevDto` | dto | `api-dtos` | CompanyConfigRev |
| `CompanyConfigUpdateDto` | dto | `api-dtos` | CompanyConfigUpdate |
| `CreateTransactionDto` | dto | `api-dtos` | CreateTransaction |
| `CreateUpdateBankAccountDto` | dto | `api-dtos` | CreateUpdateBankAccount |
| `OneTimePaymentCheckoutVo` | dto | `services` | OneTimePaymentCheckoutVo |
| `OneTimePaymentInvoiceLineDto` | dto | `api-dtos` | OneTimePaymentInvoiceLine |
| `OneTimePaymentInvoiceLineVo` | dto | `services` | OneTimePaymentInvoiceLineVo |
| `OneTimePaymentRequestDto` | dto | `api-dtos` | OneTimePayment |
| `OneTimePaymentResponseDto` | dto | `api-dtos` | OneTimePayment |
| `OneTimePaymentSatusVo` | dto | `services` | OneTimePaymentSatusVo |
| `OneTimePaymentStatusDto` | dto | `api-dtos` | OneTimePaymentStatus |
| `OneTimePaymentVo` | dto | `services` | OneTimePaymentVo |
| `PaymentETAsDto` | dto | `api-dtos` | ETAs |
| `PaymentInformationVo` | dto | `services` | InformationVo |
| `PaymentMethodStatusDto` | dto | `api-dtos` | MethodStatus |
| `PaymentNotificationPubSubDto` | dto | `api-dtos` | Notification |
| `PubSubTransactionUpdateDto` | dto | `api-dtos` | PubSubTransactionUpdate |
| `PublicCompanyConfigDto` | dto | `api-dtos` | [CompanyConfig](../domains/entities/CompanyConfig.md) |
| `RoadSyncConfig` | dto | `services` | RoadSyncConfig |
| `RoadSyncCreatePayeeRequest` | dto | `services` | RoadSyncCreatePayee |
| `RoadSyncCredentials` | dto | `services` | RoadSyncCredentials |
| `RoadSyncEtaResponse` | dto | `services` | RoadSyncEta |
| `RoadSyncFailureDetailsDto` | dto | `api-dtos` | RoadSyncFailureDetails |
| `RoadSyncFundingSourceRequest` | dto | `services` | RoadSyncFundingSource |
| `RoadSyncFundingSourceResponse` | dto | `services` | RoadSyncFundingSource |
| `RoadSyncFundingSourcesResponse` | dto | `services` | RoadSyncFundingSources |
| `RoadSyncImportPayeeRequest` | dto | `services` | RoadSyncImportPayee |
| `RoadSyncImportPayeeResponse` | dto | `services` | RoadSyncImportPayee |
| `RoadSyncMetadataDto` | dto | `api-dtos` | RoadSyncMetadata |
| `RoadSyncPayeeCandidateResponse` | dto | `services` | RoadSyncPayeeCandidate |
| `RoadSyncPayeeDto` | dto | `api-dtos` | RoadSyncPayee |
| `RoadSyncPayeeResponse` | dto | `services` | RoadSyncPayee |
| `RoadSyncTransactionRequest` | dto | `services` | RoadSyncTransaction |
| `RoadSyncTransactionResponse` | dto | `services` | RoadSyncTransaction |
| `RoadSyncUpdatePayeeRequest` | dto | `services` | RoadSyncUpdatePayee |
| `RoadSyncWebhookDto` | dto | `api-dtos` | RoadSyncWebhook |
| `SubscriptionVo` | dto | `services` | SubscriptionVo |
| `TransactionDto` | dto | `api-dtos` | [Transaction](../domains/entities/Transaction.md) |
| `TransactionRevDto` | dto | `api-dtos` | TransactionRev |
| `TransactionUpdateDto` | dto | `api-dtos` | TransactionUpdate |
| `UserVo` | dto | `services` | UserVo |
| `V3ChangeStripeSubscriptionItem` | dto | `services` | ChangeStripeSubscriptionItem |
| `V3CreateStripeCustomer` | dto | `services` | CreateStripeCustomer |
| `V3CreateStripeSubscription` | dto | `services` | CreateStripeSubscription |
| `V3StripeCustomerSyncVo` | dto | `services` | StripeCustomerSyncVo |
| `V3StripeCustomerVo` | dto | `services` | StripeCustomerVo |
| `V3StripePriceVo` | dto | `services` | StripePriceVo |
| `V3StripeProductVo` | dto | `services` | StripeProductVo |
| `V3StripeSubscriptionItemVo` | dto | `services` | StripeSubscriptionItemVo |
| `V3StripeSubscriptionVo` | dto | `services` | StripeSubscriptionVo |
| `V3UpdateStripeSubscription` | dto | `services` | UpdateStripeSubscription |
| `V3UpdateStripeSubscriptionItem` | dto | `services` | UpdateStripeSubscriptionItem |
<!-- entities-end -->
