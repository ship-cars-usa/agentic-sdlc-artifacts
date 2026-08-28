---
repo: invoices
path: ~/projects/ship-cars-usa/invoices
stack: Java 21 / Quarkus 3.27.5
domain: pricing-billing
shape: multi-module (12 poms)
last-synced-commit: 8811c5e40f4f4710ee61b15060e3ba25bd2acf52
last-synced-date: 2026-08-28
maintainer: unknown
status: seed
---

# invoices

## What it is
Quarkus 3.27.5 / Java 21 service that owns the **carrier and customer invoice lifecycle**: generation on load-delivered events, revision tracking via a `latest` flag, payment-transaction reconciliation, Envers-audited history, CSV export, and REST APIs for filter/search/update. Sits between `posting-backend` (event source) and `payment-backend` (transaction target). Temporal workflows handle invoice generation and CSV export so the API stays responsive.

## How it fits
- Consumes API of: `payment-backend` (`PaymentClient`, configKey `payment`, `createTransaction`/`updateTransaction`), `posting-backend` via `impersonator` (`PostingClient`, configKey `impersonator`), `attachment-backend` (`AttachmentClient`, configKey `attachment`), `user-backend` (`UserManagementClient`, configKey `user-management`). All 4 are `@Retry`-annotated; **none has a `@Timeout` or a `quarkus.rest-client.*.connect-timeout`/`read-timeout`** — see `relations/rest-client-registry.md`.
- Publishes events to: Pub/Sub `config.pubsub.invoices-carrier-topic` (carrier invoice events) and the notification-extension topic `ship.cars.notification.topic` (CSV-export WebSocket notifications).
- Subscribes to: Pub/Sub `config.pubsub.posting-subscription` (`PostingPubSubListener` → customer-invoice creation on `LOAD_LEG_DELIVERED`), `config.pubsub.ctms-subscription` (`CtmsPubSubListener` + `CtmsPubSubConverter`), `config.pubsub.payment-transactions-subscription` (`PaymentTransactionPubSubListener`, `PubSubTransactionUpdateDto` → invoice-status updates).
- Owns data store: PostgreSQL (`invoices` db, `%dev` HikariCP max-size=16), Hibernate Envers audit, Flyway migrations, Caffeine cache (`quarkus.cache.caffeine` max 10 000, expire-after-write 1h).

## Build / test / run
```
./mvnw clean install
./mvnw quarkus:dev
# 12 poms: root + api-dtos, api-enums, application, commons, configuration,
#          coverage-report, db-entities, db-migration, repositories, resources, services
# Temporal task queues: {env}.invoices.queue.generate-invoice, {env}.invoices.queue.export-invoice
#   (config.temporal.*; %test uses quarkus.temporal.enable-mock=true)
```

## Key abstractions
- `CarrierInvoicesController` — `resources/.../rest/CarrierInvoicesController.java` — `/v1/companies/{companyId}/carrier-invoices`; CRUD + filter.
- `CustomerInvoiceServiceImpl` — `services/.../services/impl/CustomerInvoiceServiceImpl.java` — customer-invoice creation, revision tracking, `latest`-flag bookkeeping.
- `PostingPubSubListener` — `services/.../listeners/PostingPubSubListener.java` — creates customer invoice on `LOAD_LEG_DELIVERED`.
- `CtmsPubSubListener` — `services/.../listeners/CtmsPubSubListener.java` — CTMS revision flow (`CtmsPubSubConverter`).
- `PaymentTransactionPubSubListener` — `services/.../listeners/PaymentTransactionPubSubListener.java` — updates invoice status on transaction lifecycle events.
- Temporal workflows — `services/.../temporal/workflows/impl/` — `CreateCustomerInvoiceWorkflowImpl`, `CustomerInvoiceExportCsvWorkflowImpl`; queues wired in `TemporalWorkflowsConfig`.
- `PaymentClient` — `services/.../clients/PaymentClient.java:26` — `@Retry(delay=1s, maxRetries=3)` + `@RetryWhen(IsRetryable.class)`, **no `@Timeout`**. (`AttachmentClient`/`PostingClient`/`UserManagementClient` use `maxRetries=7`.)
- `InvoiceEntity` — `db-entities/.../entities/InvoiceEntity.java:180` — JPA entity, Envers-audited, `boolean latest` flag.

## Don't-do-here / gotchas
- **`@Retry` without `@Timeout` on all 4 REST clients** — same fleet anti-pattern (`~/projects/quarkus-rest-client-timeout-anti-pattern.md`); no `quarkus.rest-client.*.connect-timeout`/`read-timeout` in `configuration/.../application.properties`. Set both or the retries amplify a hanging downstream.
- **`latest` flag now DB-enforced** — the correctness concern from v1 is addressed: `db-migration/.../V18.0__add_is_latest_flag.sql` adds the flag and `V19.0__uk_latest_flag.sql` creates partial unique index `uk_invoices_carrier_invoice_company_latest`; `V20.0__uk_carrier_invoice_revisions.sql` adds `uk_invoices_carrier_revision`. Two `latest=true` rows for one carrier invoice are no longer possible at the DB level.
- **Filter API uses POST with a body** for `latest` / `notLatestButProcessed` / date-range filtering — hides query intent in the body, defeats request logging / OpenAPI usefulness.
- **No outbox** for the Pub/Sub publish to `invoices-carrier-topic`: a publish failure after DB commit loses the carrier event.
- Note on `@Version` optimistic locking: per the fleet audit, the Quarkus timestamp-`@Version` fires only intra-transaction — invoice correctness rests on the event-apply fence, and the payment path is the fleet's top defect (see memory `optimistic_lock_version_fleet_audit`).

## Relevant ADRs / docs
- README is substantive (module-by-module layout + domain description) — not a template stub.
- `~/projects/codebase-map/repos/payment-backend.md` — transaction sink.
- `~/projects/codebase-map/repos/posting-backend.md` — load-delivered event source.
- `~/projects/codebase-map/relations/rest-client-registry.md` — the 4-client no-timeout posture.
- `~/projects/quarkus-rest-client-timeout-anti-pattern.md`; `~/projects/codebase-map/domains/pricing-billing.md`.


<!-- entities-begin -->
## Entities

Auto-generated by `scripts/cluster_entities.py`. Domain classes declared in this repo:

| Class | Kind | Module | Catalog canonical |
|---|---|---|---|
| `ChargeEntity` | jpa | `db-entities` | [Transaction](../domains/entities/Transaction.md) |
| `CompanyEntity` | jpa | `db-entities` | [Company](../domains/entities/Company.md) |
| `ContactEntity` | jpa | `db-entities` | [Contact](../domains/entities/Contact.md) |
| `InvoiceEntity` | jpa | `db-entities` | Invoice |
| `LocationEntity` | jpa | `db-entities` | [Location](../domains/entities/Location.md) |
| `ServiceEntity` | jpa | `db-entities` | Service |
| `TransactionEntity` | jpa | `db-entities` | [Transaction](../domains/entities/Transaction.md) |
| `VehicleEntity` | jpa | `db-entities` | [Vehicle](../domains/entities/Vehicle.md) |
| `AttachmentMultipartForm` | dto | `services` | AttachmentMultipartForm |
| `CarrierInvoiceDto` | dto | `api-dtos` | CarrierInvoice |
| `CarrierInvoiceTransactionDto` | dto | `api-dtos` | CarrierInvoiceTransaction |
| `CarrierInvoiceUpdateDto` | dto | `api-dtos` | CarrierInvoiceUpdate |
| `CarrierServiceDto` | dto | `api-dtos` | CarrierService |
| `CarrierVehicleDto` | dto | `api-dtos` | CarrierVehicle |
| `CompanyInvoiceDto` | dto | `api-dtos` | CompanyInvoice |
| `ContactInvoiceDto` | dto | `api-dtos` | ContactInvoice |
| `CreateCustomerInvoiceInDto` | dto | `services` | CreateCustomerInvoiceIn |
| `CsvExportJobDto` | dto | `api-dtos` | CsvExportJob |
| `CsvExportJobIdentityDto` | dto | `api-dtos` | CsvExportJobIdentity |
| `CsvExportedEvent` | dto | `services` | CsvExportedEvent |
| `CsvExportedWebSocketMsgDto` | dto | `services` | CsvExportedWebSocketMsg |
| `CtmsPubSubConverter` | dto | `services` | CtmsPubSubConverter |
| `CustomerFooterNoteDto` | dto | `api-dtos` | CustomerFooterNote |
| `CustomerInvoiceDto` | dto | `api-dtos` | CustomerInvoice |
| `CustomerInvoiceExportCsvJobServiceImpl` | dto | `services` | CustomerInvoiceExportCsvJobServiceImpl |
| `CustomerInvoiceExportDto` | dto | `services` | CustomerInvoiceExport |
| `CustomerInvoiceServiceImpl` | dto | `services` | CustomerInvoiceServiceImpl |
| `CustomerInvoiceUpdateDto` | dto | `api-dtos` | CustomerInvoiceUpdate |
| `CustomerKey` | dto | `services` | CustomerKey |
| `CustomerVehicleChargeDto` | dto | `api-dtos` | CustomerVehicleCharge |
| `CustomerVehicleDto` | dto | `api-dtos` | CustomerVehicle |
| `EmailMessageDto` | dto | `services` | EmailMessage |
| `ExportCsvExportWorkflowOutDto` | dto | `services` | ExportCsvExportWorkflowOut |
| `ExportCsvInDto` | dto | `services` | ExportCsvIn |
| `ExportCsvOutDto` | dto | `services` | ExportCsvOut |
| `ExportCsvWorkflowInDto` | dto | `services` | ExportCsvWorkflowIn |
| `ExportDataDto` | dto | `api-dtos` | ExportData |
| `InvoiceFilter` | dto | `db-entities` | InvoiceFilter |
| `LocationInvoiceDto` | dto | `api-dtos` | LocationInvoice |
| `MessageDto` | dto | `api-dtos` | [Message](../domains/entities/Message.md) |
| `SchedulePaymentRequestDto` | dto | `api-dtos` | SchedulePayment |
| `UpdateTransactionRequestDto` | dto | `api-dtos` | UpdateTransaction |
| `UserVo` | dto | `services` | UserVo |
| `ValueToLabelDto` | dto | `api-dtos` | ValueToLabel |
<!-- entities-end -->
