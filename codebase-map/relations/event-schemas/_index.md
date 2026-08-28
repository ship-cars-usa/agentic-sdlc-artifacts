---
name: event-schemas-index
description: Per-topic schema files for the Ship.Cars Pub/Sub fleet (Tier 1.5 sidecar to event-catalog.md)
generator: ~/projects/codebase-map/scripts/gen_event_schemas.py
last-generated-date: 2026-05-15
total-topics: 80
schema-source-counts:
  lombok-data: 26
  java-record: 6
  pydantic: 0
  partial: 1
  none: 47
status: stub
---

# Event schemas — per-topic index

One markdown file per resolved topic in
[`../event-catalog.md`](../event-catalog.md). Each file captures the
**consumer-side** DTO that the topic's payload deserializes into, with field
names, types, JSON aliases (from `@JsonProperty`), and nullability hints.

**Why this exists**: the L3b contract program (per
`~/projects/carrier-test-strategy/CONTRACT-TESTING-PREREQUISITES.md`) is
going to author canonical machine-readable schemas. This sidecar captures
*what's there today* so the L3b authors have a concrete starting point rather
than a blank slate. **Not** a replacement for L3b contracts.

## Topic index

| Topic | Schema source | DTO | Tier |
|---|---|---|---|
| [`cars.ship.*.carrierlb.events`](./cars.ship.*.carrierlb.events.md) | none | — | carrier |
| [`cars.ship.*.lh-load-location-log.events`](./cars.ship.*.lh-load-location-log.events.md) | none | — | carrier |
| [`cars.ship.*.notification`](./cars.ship.*.notification.md) | none | — | carrier |
| [`cars.ship.prod.carrierlb.events-ml-recommender`](./cars.ship.prod.carrierlb.events-ml-recommender.md) | none | — | carrier |
| [`cars.ship.prod.ml.recommender`](./cars.ship.prod.ml.recommender.md) | none | — | carrier |
| [`cars.ship.qa.notification`](./cars.ship.qa.notification.md) | none | — | carrier |
| [`company-state`](./company-state.md) | lombok-data | `CompanyEventPubSubDto` | carrier |
| [`company-state-v2`](./company-state-v2.md) | java-record | `V2CompanySubscriptionPubSubDto` | carrier |
| [`company-subscription`](./company-subscription.md) | none | — | carrier |
| [`company-subscription-v2`](./company-subscription-v2.md) | lombok-data | `MessageObjectDto` | carrier |
| [`contacts-state`](./contacts-state.md) | none | — | carrier |
| [`ctms-subscription`](./ctms-subscription.md) | lombok-data | `CtmsAttachmentPubSubDto` | carrier |
| [`cube.search-posting-events`](./cube.search-posting-events.md) | java-record | `SearchPostingEventPubSubDto` | carrier |
| [`events`](./events.md) | none | — | carrier |
| [`events-topic`](./events-topic.md) | none | — | carrier |
| [`invoices-carrier-topic`](./invoices-carrier-topic.md) | none | — | carrier |
| [`loadboard-events-topic`](./loadboard-events-topic.md) | none | — | carrier |
| [`loadboard-notifications-topic`](./loadboard-notifications-topic.md) | none | — | carrier |
| [`loadboard-state`](./loadboard-state.md) | lombok-data | `LoadboardEventPubSubDto` | carrier |
| [`loadboard-v3-events`](./loadboard-v3-events.md) | none | — | carrier |
| [`ml-recommender-subscription`](./ml-recommender-subscription.md) | lombok-data | `RecommendationMessageDto` | carrier |
| [`notification`](./notification.md) | lombok-data | `V1NotificationPubSubDto` | carrier |
| [`notification-topic`](./notification-topic.md) | none | — | carrier |
| [`notifications-topic`](./notifications-topic.md) | none | — | carrier |
| [`payment-transactions-subscription`](./payment-transactions-subscription.md) | lombok-data | `PubSubTransactionUpdateDto` | carrier |
| [`posting-job-events`](./posting-job-events.md) | lombok-data | `WorkflowEventPubSubDto` | carrier |
| [`posting-state`](./posting-state.md) | none | — | carrier |
| [`posting-subscription`](./posting-subscription.md) | lombok-data | `LoadLegMsgPubSubDto` | carrier |
| [`posting-v2-state`](./posting-v2-state.md) | none | — | carrier |
| [`quote-state`](./quote-state.md) | lombok-data | `QuoteManagerUpdateEventPubSubDto` | carrier |
| [`sent-emails-subscription`](./sent-emails-subscription.md) | lombok-data | `SentEmailDto` | carrier |
| [`sent-emails-topic`](./sent-emails-topic.md) | none | — | carrier |
| [`sync-topic`](./sync-topic.md) | none | — | carrier |
| [`temporal-workflows-events-topic`](./temporal-workflows-events-topic.md) | lombok-data | `WorkflowEventPubSubDto` | carrier |
| [`um-usage-record`](./um-usage-record.md) | none | — | carrier |
| [`usage-record`](./usage-record.md) | java-record | `V3UsageRecordDto` | carrier |
| [`user-state`](./user-state.md) | lombok-data | `UserEventPubSubDto` | carrier |
| [`user-state-v2`](./user-state-v2.md) | lombok-data | `V2UserAccountPubSubDto` | carrier |
| [`user-subscription`](./user-subscription.md) | none | — | carrier |
| [`user-subscription-v2`](./user-subscription-v2.md) | lombok-data | `MessageObjectDto` | carrier |
| [`carrier`](./carrier.md) | none | — | fleet |
| [`carrier-company`](./carrier-company.md) | none | — | fleet |
| [`ctms-state`](./ctms-state.md) | none | — | fleet |
| [`email-subscription`](./email-subscription.md) | none | — | fleet |
| [`fraud-alerts-topic`](./fraud-alerts-topic.md) | none | — | fleet |
| [`integration-subscription`](./integration-subscription.md) | lombok-data | `IntegrationEventMessageDto` | fleet |
| [`keycloak-subscription`](./keycloak-subscription.md) | lombok-data | `KeyCloakEventDto` | fleet |
| [`lm-contacts`](./lm-contacts.md) | none | — | fleet |
| [`lm-posting`](./lm-posting.md) | none | — | fleet |
| [`load-info-state`](./load-info-state.md) | lombok-data | `LoadLegMsgPubSubDto` | fleet |
| [`load-location-log`](./load-location-log.md) | none | — | fleet |
| [`load-recommender.feedback-events`](./load-recommender.feedback-events.md) | none | — | fleet |
| [`loadboard`](./loadboard.md) | none | — | fleet |
| [`loadboard-v3`](./loadboard-v3.md) | none | — | fleet |
| [`loadboard-v3-subscription`](./loadboard-v3-subscription.md) | none | — | fleet |
| [`loadmate-posting-subscription`](./loadmate-posting-subscription.md) | lombok-data | `LoadMatePostingMessageDto` | fleet |
| [`loadmate-posting-v2-subscription`](./loadmate-posting-v2-subscription.md) | lombok-data | `LoadMatePostingV2MessageDto` | fleet |
| [`loadmate-quote-manager-subscription`](./loadmate-quote-manager-subscription.md) | lombok-data | `LoadMateQuoteManagerMessageDto` | fleet |
| [`metadata-subscription`](./metadata-subscription.md) | partial | `MetadataMessageObjectDto` | fleet |
| [`notification-state`](./notification-state.md) | lombok-data | `V1NotificationPubSubDto` | fleet |
| [`oib-inbound-lm`](./oib-inbound-lm.md) | none | — | fleet |
| [`oib-inbound-sf`](./oib-inbound-sf.md) | none | — | fleet |
| [`oib-outbound-lm`](./oib-outbound-lm.md) | none | — | fleet |
| [`oib-outbound-sf`](./oib-outbound-sf.md) | none | — | fleet |
| [`payment-notification`](./payment-notification.md) | none | — | fleet |
| [`platform-subscription`](./platform-subscription.md) | lombok-data | `PlatformMessageObjectDto` | fleet |
| [`quote-notification`](./quote-notification.md) | none | — | fleet |
| [`quote-receive-state`](./quote-receive-state.md) | lombok-data | `QuotePubSubDto` | fleet |
| [`quote-send-state`](./quote-send-state.md) | none | — | fleet |
| [`saved-search-percolate`](./saved-search-percolate.md) | none | — | fleet |
| [`ship.cars.notification.topic`](./ship.cars.notification.topic.md) | none | — | fleet |
| [`sms-events`](./sms-events.md) | none | — | fleet |
| [`subscription-bank-account-update`](./subscription-bank-account-update.md) | java-record | `BankAccountUpdatePubSubDto` | fleet |
| [`topics-bank-account-update`](./topics-bank-account-update.md) | java-record | `BankAccountUpdatePubSubDto` | fleet |
| [`topics-payment-notification`](./topics-payment-notification.md) | java-record | `PaymentNotificationPubSubDto` | fleet |
| [`topics-payment-update`](./topics-payment-update.md) | none | — | fleet |
| [`topics-transaction-update`](./topics-transaction-update.md) | none | — | fleet |
| [`user-management-company-subscription`](./user-management-company-subscription.md) | lombok-data | `UserManagementCompanyPubSubDto` | fleet |
| [`user-management-user-subscription`](./user-management-user-subscription.md) | lombok-data | `UserManagementUserPubSubDto` | fleet |
| [`useractivitytracker.internal-subscription`](./useractivitytracker.internal-subscription.md) | none | — | fleet |

## Schema-source legend
- **lombok-data** — Java Lombok `@Data` / `@Value` class. Fields extracted.
- **java-record** — Java record. Components extracted.
- **pydantic** — Python Pydantic `BaseModel`. Fields extracted.
- **partial** — DTO file found but not a recognized convention. Minimal extraction.
- **none** — no typed DTO found. Consumer uses raw dict / `JsonNode` access,
  or the consumer file couldn't be matched to this topic. Flagged as audit todo.

## Regenerate

```
python3 ~/projects/codebase-map/scripts/gen_event_schemas.py             # writes per-topic files + this index
python3 ~/projects/codebase-map/scripts/gen_event_schemas.py --dry-run   # preview to stdout (no writes)
python3 ~/projects/codebase-map/scripts/gen_event_schemas.py --discover-only
                                                                          # print (topic -> consumer file -> DTO) bindings only
```

## Status lifecycle

All files ship with `status: stub` on first generation. After a human review
pass against the source DTOs, flip individual frontmatter `status: stub` →
`status: seed`.
