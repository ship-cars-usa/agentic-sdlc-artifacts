---
repo: user-backend
path: ~/projects/ship-cars-usa/user-backend
stack: Java 21 / Spring Boot 3.2.12
domain: identity
shape: multi-module (3 poms: usermanagement-app, usermanagement-dtos, parent)
last-synced-commit: e4bdc31839d2090836a211e1e9c48d87349b3627
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# user-backend

## What it is
System-of-record for users and companies in the LoadMate product. Spring Boot 3.2.12 / Java 21, hexagonal architecture, multi-module. Manages user accounts (with MFA), company lifecycle (incl. white-label branding), and Stripe billing entities, and publishes user/company state changes to Pub/Sub. Authenticates via Keycloak (bearer-only resource server) and **owns the Keycloak Admin API integration** — the `keycloak-admin-client` dependency (`usermanagement-app/pom.xml:280`) plus `KeycloakSecurityProviderClientImpl` / `KeycloakIntegratorCredentialsClientImpl` provision KC users, roles, groups, and integrator clients under separate admin creds (`CONFIG_KEYCLOAK_ADMIN_CLIENT_ID` / `_SECRET`). **Not a façade** to Django or Keycloak — owns the canonical user/company tables itself.

> **🔄 Re-synced 2026-08-28 — two structural changes since last sync:**
> 1. **The transactional outbox was removed** (`V0.0.0_82__drop_outbox_table.sql` drops `outbox_message` + `_aud`). Pub/Sub is now published **synchronously in-flow**, not via a polled outbox: `PubSubMessageService` → `MessageSenderImpl` → `PubSubPublisherSync.publish(topic, msg, ordered=true)` (`MessageSenderImpl.java:60`). Publish failures are **caught and logged only** (`PubSubMessageService.java:66`) — effectively **at-most-once**; a failed publish is lost, there is no retry table anymore. `OutboxPollerImpl` and the `chron` package no longer exist.
> 2. **Company white-label branding** added (`LITE-8332`, #834): new `CompanyBranding` domain model (`domain/model/CompanyBranding.java`), `company_branding` table (`V0.0.0_86`), `V2InternalCompanyController` branding endpoints, and `V2CompanyBrandingDto` / `CompanyBrandingThemeModeEnum` in the dtos module.

## How it fits
- Consumes API of: `notification-backend` (via the notification-client library), `attachment-backend`, `metadata`, `media-proxy`, `payment-backend` (async via Pub/Sub), and the **Keycloak Admin API** (separate creds: `CONFIG_KEYCLOAK_ADMIN_CLIENT_ID` / `CONFIG_KEYCLOAK_ADMIN_CLIENT_SECRET`).
- Publishes events to: GCP Pub/Sub topics `user-state-v2`, `company-state-v2`, `notification` (`application.properties:128-130`) — **published synchronously in-flow with an ordering key** (no outbox since `V0.0.0_82`). JSON DTOs (`V2UserAccountPubSubDto` / `V2CompanyPubSubDto`), no schema registry.
- Subscribes to: GCP Pub/Sub `payment-backend` (Stripe webhook fan-out, `PaymentBackendConsumer`), `usage-record` (billing sync).
- Owns data store: PostgreSQL (schema via `CONFIG_DB_SCHEMA`), Redis (Lettuce 6.2.7) for cache.

## Build / test / run
```
export GITHUB_USERNAME=... GITHUB_READ_TOKEN=...
./build-project.sh                                       # or ./mvnw -s ./.mvn/settings.xml clean install
./utils/docker/build-docker-local.sh
./utils/docker-compose/docker-compose-local.sh up -d     # local stack
# Swagger: http://localhost:7010/swagger-ui/index.html
```

## Key abstractions
- `UserAccountServiceImpl` — `usermanagement-app/src/main/java/cars/ship/shipperlite/user/domain/ports/service/UserAccountServiceImpl.java` — user CRUD, MFA toggling, account-state transitions.
- `CompanyServiceImpl` — same package, `CompanyServiceImpl.java` — company lifecycle, Keycloak + Stripe sync.
- `CompanyNotifyService` — `usermanagement-app/.../domain/ports/service/CompanyNotifyService.java` — computes changed fields, fires Spring `ApplicationEvent`s (Redis cache invalidation) and delegates Pub/Sub publishing to `PubSubMessageService`.
- `PubSubMessageService` — `usermanagement-app/.../domain/ports/service/PubSubMessageService.java` — builds `V2UserAccountPubSubDto` / `V2CompanyPubSubDto` messages and hands them to `MessageSender`; **catches and logs publish failures** (`:66`) rather than retrying.
- `MessageSenderImpl` — `usermanagement-app/.../application/adapters/out/pubsub/MessageSenderImpl.java` — thin adapter over `spring-commons` `PubSubPublisherSync.publish(topic, msg, ordered=true)` (`:60`).
- `PaymentBackendConsumer` — `usermanagement-app/.../application/adapters/in/pubsub/payment/PaymentBackendConsumer.java` — consumes Stripe product/customer/price/subscription updates and syncs into `StripeProductRepository` etc. **Correct semantics:** nacks on exception (no silent drop).
- `SchedulerConfig` — `usermanagement-app/.../config/SchedulerConfig.java` — `@EnableScheduling` + ShedLock `JdbcTemplateLockProvider` over the `<schema>.shedlock` table. Scheduling infra remains, but the outbox poller that used it is gone.
- `CompanyBranding` — `usermanagement-app/.../domain/model/CompanyBranding.java` — white-label branding value object (theme mode, banner) surfaced via `V2InternalCompanyController`.
- `V2InternalUserAccountController` / `V2InternalCompanyController` — `usermanagement-app/.../application/adapters/in/web/rest/controllers/v2/` — internal-only APIs consumed by `notification-backend` and `chat-backend` (branding lives on the company controller).

## Don't-do-here / gotchas
- **Pub/Sub is now at-most-once, not outbox-backed.** The transactional outbox was dropped (`V0.0.0_82`); `PubSubMessageService.constructAndSend*Msg` catches every publish exception and only logs (`:66`). If GCP Pub/Sub is unreachable at publish time, the state-change event is **silently lost** — there is no retry table and no redelivery. Consumers (chat-backend, notification-orchestrator, syncer, etc.) can miss a user/company update. Treat downstream state as eventually-reconcilable, not guaranteed-delivered, and consider re-introducing an outbox if any consumer needs at-least-once.
- **Publishes use an ordering key** (`MessageSenderImpl.java:60`, `ordered=true`) — subscriptions must be ordering-enabled or messages may be rejected/reordered.
- **HikariCP pool size is env-driven** (`CONFIG_HIKARI_MAX_POOL_SIZE`); local default 10 (`application-local.properties:spring.datasource.hikari.maximumPoolSize=10`); production value is unverified — confirm before scaling traffic.
- **REST-client timeouts not configured at the application level** — relies on `spring-commons` `WebClientImpl`, which requires explicit timeouts at construction. Confirm each outbound client (notification-client, attachment, metadata, media-proxy) sets `connectTimeoutMs` / `readTimeoutMs`. Hardcoded outlier observed: attachment service timeout = `PT180S` (3 minutes — long).
- **Keycloak bearer-only mode** (`keycloak.bearer-only=true`, `application.properties:34`); standard Spring Security `oauth2.resourceserver` config (`issuer-uri`, `jwk-set-uri`). MFA + role assignment is driven by Keycloak groups (`canceled-group-id`, `api-integrator-group-id`) and roles (`ctms.unverified_carrier`, `um.mfa_enabled`).
- **Lettuce 6.2.7 is pinned** because of a RESP3 `CLIENT SETINFO` issue with Redis 7.2+. Don't bump Lettuce without retesting against the actual Redis version in prod.
- **Javers 7.6.3** wires audit on user/company changes (in addition to whatever JPA-level history exists).
- **No outbox / no CDC** — since `V0.0.0_82` there is no outbox table and no Debezium. Publishing is inline and synchronous; consumers must not assume replay or CDC ordering guarantees beyond the per-message ordering key.

## Relevant ADRs / docs
- `README.md` — tech stack, quick start.
- `CLAUDE.md` — hexagonal architecture diagram paths.
- `~/projects/quarkus-fleet-review-2026-05-07.md` — `chat-backend` and `contract-pricing-backend` both call this service; the timeout-on-caller gaps documented there are real even though `user-backend` itself is sound.


<!-- entities-begin -->
## Entities

Auto-generated by `scripts/cluster_entities.py`. Domain classes declared in this repo:

| Class | Kind | Module | Catalog canonical |
|---|---|---|---|
| `Attachment` | jpa | `usermanagement-app` | [Attachment](../domains/entities/Attachment.md) |
| `Banner` | jpa | `usermanagement-app` | Banner |
| `Company` | jpa | `usermanagement-app` | [Company](../domains/entities/Company.md) |
| `CompanyBranding` | jpa | `usermanagement-app` | CompanyBranding |
| `StripeCustomerEntity` | jpa | `usermanagement-app` | StripeCustomer |
| `StripeFeatureDisplayNameEntity` | jpa | `usermanagement-app` | StripeFeatureDisplayName |
| `StripeFeatureEntity` | jpa | `usermanagement-app` | StripeFeature |
| `StripeMeteredActionEntity` | jpa | `usermanagement-app` | StripeMeteredAction |
| `StripePriceEntity` | jpa | `usermanagement-app` | StripePrice |
| `StripePriceTierEntity` | jpa | `usermanagement-app` | StripePriceTier |
| `StripeProductEntity` | jpa | `usermanagement-app` | StripeProduct |
| `StripeProductFeatureEntity` | jpa | `usermanagement-app` | StripeProductFeature |
| `StripeSubscriptionEntity` | jpa | `usermanagement-app` | StripeSubscription |
| `StripeSubscriptionItemEntity` | jpa | `usermanagement-app` | StripeSubscriptionItem |
| `UserAccount` | jpa | `usermanagement-app` | [User](../domains/entities/User.md) |
| `VerificationCode` | jpa | `usermanagement-app` | VerificationCode |
| `AttachmentDetached` | dto | `usermanagement-app` | AttachmentDetached |
| `AttachmentVo` | dto | `usermanagement-app` | AttachmentVo |
| `BannerConditionFields` | dto | `usermanagement-app` | BannerConditionFields |
| `BannerDetached` | dto | `usermanagement-app` | BannerDetached |
| `BaseDetached` | dto | `usermanagement-app` | BaseDetached |
| `BaseEntityDetached` | dto | `usermanagement-app` | BaseEntityDetached |
| `BaseEntityStringId` | dto | `usermanagement-app` | BaseEntityStringId |
| `BaseReadOnlyDetached` | dto | `usermanagement-app` | BaseReadOnlyDetached |
| `CompanyBrandingDetached` | dto | `usermanagement-app` | CompanyBrandingDetached |
| `CompanyChangedEvent` | dto | `usermanagement-app` | CompanyChangedEvent |
| `CompanyDetached` | dto | `usermanagement-app` | CompanyDetached |
| `CompanyKeycloakChangedEvent` | dto | `usermanagement-app` | CompanyKeycloakChangedEvent |
| `CompanyKeycloakPlanGroupChangedEvent` | dto | `usermanagement-app` | CompanyKeycloakPlanGroupChangedEvent |
| `CompanyOwnerInitializedEvent` | dto | `usermanagement-app` | CompanyOwnerInitializedEvent |
| `CompanyPublicProfile` | dto | `usermanagement-app` | CompanyPublicProfile |
| `CompanySearchFilterVo` | dto | `usermanagement-app` | CompanySearchFilterVo |
| `CompanyStripeEmailChangeEvent` | dto | `usermanagement-app` | CompanyStripeEmailChangeEvent |
| `CreateLinkedUserAccount` | dto | `usermanagement-app` | CreateLinkedUserAccount |
| `CustomerSubscriptionSettings` | dto | `usermanagement-app` | CustomerSubscriptionSettings |
| `FileContent` | dto | `usermanagement-app` | [FileContent](../domains/entities/FileContent.md) |
| `KeycloakConfig` | dto | `usermanagement-app` | KeycloakConfig |
| `KeycloakTokensResponse` | dto | `usermanagement-app` | KeycloakTokens |
| `MainUserChangedEvent` | dto | `usermanagement-app` | MainUserChangedEvent |
| `NewCompanyRegisteredEvent` | dto | `usermanagement-app` | NewCompanyRegisteredEvent |
| `OutboxMessageFormat` | dto | `usermanagement-app` | OutboxMessageFormat |
| `Password` | dto | `usermanagement-app` | Password |
| `PaymentUserAccountDto` | dto | `usermanagement-app` | PaymentUserAccount |
| `StripeCustomer` | dto | `usermanagement-app` | StripeCustomer |
| `StripeFeature` | dto | `usermanagement-app` | StripeFeature |
| `StripeFeatureDisplayName` | dto | `usermanagement-app` | StripeFeatureDisplayName |
| `StripeMeteredAction` | dto | `usermanagement-app` | StripeMeteredAction |
| `StripePrice` | dto | `usermanagement-app` | StripePrice |
| `StripePriceTier` | dto | `usermanagement-app` | StripePriceTier |
| `StripeProduct` | dto | `usermanagement-app` | StripeProduct |
| `StripeSubscription` | dto | `usermanagement-app` | StripeSubscription |
| `StripeSubscriptionItem` | dto | `usermanagement-app` | StripeSubscriptionItem |
| `StripeUpdate` | dto | `usermanagement-app` | StripeUpdate |
| `SubscriptionPlans` | dto | `usermanagement-app` | SubscriptionPlans |
| `UpdateStripeCustomer` | dto | `usermanagement-app` | UpdateStripeCustomer |
| `UpdateStripePrice` | dto | `usermanagement-app` | UpdateStripePrice |
| `UpdateStripeProduct` | dto | `usermanagement-app` | UpdateStripeProduct |
| `UpdateStripeSubscription` | dto | `usermanagement-app` | UpdateStripeSubscription |
| `UpdateStripeSubscriptionItem` | dto | `usermanagement-app` | UpdateStripeSubscriptionItem |
| `UpdateUserContext` | dto | `usermanagement-app` | UpdateUserContext |
| `UrlResponse` | dto | `usermanagement-app` | Url |
| `User` | dto | `usermanagement-app` | [User](../domains/entities/User.md) |
| `UserAccountDetached` | dto | `usermanagement-app` | AccountDetached |
| `UserAccountSearch` | dto | `usermanagement-app` | AccountSearch |
| `UserChangedEvent` | dto | `usermanagement-app` | ChangedEvent |
| `UserVerificationChannels` | dto | `usermanagement-app` | VerificationChannels |
| `V1BannerDto` | dto | `usermanagement-dtos` | Banner |
| `V1CompanyDto` | dto | `usermanagement-dtos` | [Company](../domains/entities/Company.md) |
| `V1CompanyOwnerUserDto` | dto | `usermanagement-dtos` | CompanyOwnerUser |
| `V1CreateCompanyDto` | dto | `usermanagement-dtos` | CreateCompany |
| `V1MoveGroupDto` | dto | `usermanagement-dtos` | MoveGroup |
| `V1PagedResponseDto` | dto | `usermanagement-dtos` | Paged |
| `V1SortDto` | dto | `usermanagement-dtos` | Sort |
| `V1StripeDetailsDto` | dto | `usermanagement-dtos` | StripeDetails |
| `V1StripeDetailsWithCustomerIdDto` | dto | `usermanagement-dtos` | StripeDetailsWithCustomerId |
| `V1StripeUpdateDto` | dto | `usermanagement-dtos` | StripeUpdate |
| `V1SubscriptionDetailsDto` | dto | `usermanagement-dtos` | SubscriptionDetails |
| `V1TierDto` | dto | `usermanagement-dtos` | Tier |
| `V1UserAccountDto` | dto | `usermanagement-dtos` | [User](../domains/entities/User.md) |
| `V1UserAccountPagedDto` | dto | `usermanagement-dtos` | AccountPaged |
| `V1UserAccountSearchDto` | dto | `usermanagement-dtos` | AccountSearch |
| `V1UserAccountWithoutCompanyDto` | dto | `usermanagement-dtos` | AccountWithoutCompany |
| `V2AddChildCompanyDto` | dto | `usermanagement-dtos` | AddChildCompany |
| `V2ChangePasswordDto` | dto | `usermanagement-dtos` | ChangePassword |
| `V2ChildrenCompanySummarySearchDto` | dto | `usermanagement-dtos` | ChildrenCompanySummarySearch |
| `V2CompanyBrandingDto` | dto | `usermanagement-dtos` | CompanyBranding |
| `V2CompanyBrandingBannerDto` | dto | `usermanagement-dtos` | CompanyBrandingBanner |
| `V2CompanyDto` | dto | `usermanagement-dtos` | [Company](../domains/entities/Company.md) |
| `V2CompanyPubSubDto` | dto | `usermanagement-dtos` | [Company](../domains/entities/Company.md) |
| `V2CompanyPublicProfileDto` | dto | `usermanagement-dtos` | CompanyPublicProfile |
| `V2CompanySearchDto` | dto | `usermanagement-dtos` | CompanySearch |
| `V2CompanySubscriptionPubSubDto` | dto | `usermanagement-dtos` | Subscription |
| `V2CompanySummaryDto` | dto | `usermanagement-dtos` | CompanySummary |
| `V2CompanySummarySearchDto` | dto | `usermanagement-dtos` | CompanySummarySearch |
| `V2CreateChildCompanyDto` | dto | `usermanagement-dtos` | CreateChildCompany |
| `V2CreateChildUserAccountDto` | dto | `usermanagement-dtos` | CreateChildUserAccount |
| `V2CreateCompanyDto` | dto | `usermanagement-dtos` | CreateCompany |
| `V2CreateLinkedUserAccountDto` | dto | `usermanagement-dtos` | CreateLinkedUserAccount |
| `V2KeycloakRefreshTokenDto` | dto | `usermanagement-dtos` | KeycloakRefreshToken |
| `V2KeycloakRoleDto` | dto | `usermanagement-dtos` | KeycloakRole |
| `V2KeycloakTokensDto` | dto | `usermanagement-dtos` | KeycloakTokens |
| `V2LoginDto` | dto | `usermanagement-dtos` | Login |
| `V2MfaDto` | dto | `usermanagement-dtos` | Mfa |
| `V2MfaSettingsDto` | dto | `usermanagement-dtos` | MfaSettings |
| `V2PagedCompanyDto` | dto | `usermanagement-dtos` | PagedCompany |
| `V2PagedCompanySummaryDto` | dto | `usermanagement-dtos` | PagedCompanySummary |
| `V2PagedUserAccountDto` | dto | `usermanagement-dtos` | PagedUserAccount |
| `V2PagedUserAccountSummaryDto` | dto | `usermanagement-dtos` | PagedUserAccountSummary |
| `V2PaymentCompanyDto` | dto | `usermanagement-dtos` | PaymentCompany |
| `V2PrePopulatedDataDto` | dto | `usermanagement-dtos` | PrePopulatedData |
| `V2ResetPasswordDto` | dto | `usermanagement-dtos` | ResetPassword |
| `V2StripeDetailsDto` | dto | `usermanagement-dtos` | StripeDetails |
| `V2StripeDetailsWithCustomerIdDto` | dto | `usermanagement-dtos` | StripeDetailsWithCustomerId |
| `V2UpdateChildCompanyDto` | dto | `usermanagement-dtos` | UpdateChildCompany |
| `V2UpdateUserAccountDto` | dto | `usermanagement-dtos` | UpdateUserAccount |
| `V2UserAccountBasicDto` | dto | `usermanagement-dtos` | AccountBasic |
| `V2UserAccountDto` | dto | `usermanagement-dtos` | [User](../domains/entities/User.md) |
| `V2UserAccountPubSubDto` | dto | `usermanagement-dtos` | [User](../domains/entities/User.md) |
| `V2UserAccountSummaryDto` | dto | `usermanagement-dtos` | AccountSummary |
| `V2UserAccountWithoutCompanyDto` | dto | `usermanagement-dtos` | AccountWithoutCompany |
| `V2UserVerificationChannelDto` | dto | `usermanagement-dtos` | VerificationChannel |
| `V2UserVerificationChannelsDto` | dto | `usermanagement-dtos` | VerificationChannels |
| `V2VerifyCodeDto` | dto | `usermanagement-dtos` | VerifyCode |
| `V3Addon` | dto | `usermanagement-app` | Addon |
| `V3AddonDto` | dto | `usermanagement-dtos` | Addon |
| `V3CancelSubscription` | dto | `usermanagement-app` | CancelSubscription |
| `V3ChangeStripeSubscriptionItemDto` | dto | `usermanagement-dtos` | ChangeStripeSubscriptionItem |
| `V3CreatePortalDto` | dto | `usermanagement-dtos` | CreatePortal |
| `V3CreateStripeCustomerDto` | dto | `usermanagement-dtos` | CreateStripeCustomer |
| `V3CreateStripeSubscriptionDto` | dto | `usermanagement-dtos` | CreateStripeSubscription |
| `V3CreateStripeSubscriptionVo` | dto | `usermanagement-app` | CreateStripeSubscriptionVo |
| `V3RemoveSubscriptionDto` | dto | `usermanagement-dtos` | RemoveSubscription |
| `V3StripeCustomerDto` | dto | `usermanagement-dtos` | StripeCustomer |
| `V3StripeDataDto` | dto | `usermanagement-dtos` | StripeData |
| `V3StripeDataWithInternalIdsDto` | dto | `usermanagement-dtos` | StripeDataWithInternalIds |
| `V3StripePriceDto` | dto | `usermanagement-dtos` | StripePrice |
| `V3StripeProductDto` | dto | `usermanagement-dtos` | StripeProduct |
| `V3StripePubSubWrapperDto` | dto | `usermanagement-dtos` | StripePubSubWrapper |
| `V3StripeSubscriptionDto` | dto | `usermanagement-dtos` | StripeSubscription |
| `V3StripeSubscriptionItemDto` | dto | `usermanagement-dtos` | StripeSubscriptionItem |
| `V3SubscribeToProductsDto` | dto | `usermanagement-dtos` | SubscribeToProducts |
| `V3UpdateStripeSubscriptionDto` | dto | `usermanagement-dtos` | UpdateStripeSubscription |
| `V3UpdateStripeSubscriptionItemDto` | dto | `usermanagement-dtos` | UpdateStripeSubscriptionItem |
| `V3UpdateStripeSubscriptionItemVo` | dto | `usermanagement-app` | UpdateStripeSubscriptionItemVo |
| `V3UpdateStripeSubscriptionVo` | dto | `usermanagement-app` | UpdateStripeSubscriptionVo |
| `V3UsageRecordDto` | dto | `usermanagement-dtos` | Usage |
| `VerificationCode` | dto | `usermanagement-app` | VerificationCode |
<!-- entities-end -->
