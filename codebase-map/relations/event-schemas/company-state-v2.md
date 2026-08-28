---
topic: company-state-v2
producers: [user-backend]
consumers: []
tier: carrier
canonical-dto: cars.ship.usermanagement.dtos.v2.V2CompanySubscriptionPubSubDto
canonical-dto-file: ~/projects/ship-cars-usa/user-backend/usermanagement-dtos/src/main/java/cars/ship/usermanagement/dtos/v2/V2CompanySubscriptionPubSubDto.java
schema-source: java-record
shared-with-producer: true
last-generated-date: 2026-05-15
status: stub
---

# Topic `company-state-v2` — schema

Canonical DTO: `cars.ship.usermanagement.dtos.v2.V2CompanySubscriptionPubSubDto`
(consumer-side, from `user-backend/usermanagement-dtos/src/main/java/cars/ship/usermanagement/dtos/v2/V2CompanySubscriptionPubSubDto.java`)

**Forward-compatible:** consumer is annotated with `@JsonIgnoreProperties(ignoreUnknown = true)` — unknown JSON fields are silently dropped on deserialization.

## Payload shape (recursive JSON preview)

**Total fields:** 12

Values are JSON type annotations (e.g. `"string"`, `"integer"`, `"string (enum: A|B|C)"`). Nested DTOs are expanded inline; arrays use a single-element list to show the item shape; maps use `{"<key>": <value>}`. Generic placeholders show as `<T>`. Cycle / depth-capped types show as `<TypeName (cycle)>` / `<TypeName (depth-cap)>`.

```json
{
  "subscriptionName": "string",
  "subscriptionStatus": "string (enum: CANCELED|ACTIVE|TRIALING|PAST_DUE|INCOMPLETE|INCOMPLETE_EXPIRED)",
  "addons": [
    "string"
  ],
  "subscriptionId": "string",
  "nextPaymentDueTo": "string (iso-8601 datetime)",
  "trialExpiryDate": "string (iso-8601 datetime)",
  "paymentMethodProvided": "boolean",
  "lastPaymentResult": "string (enum: SUCCESS)",
  "currentPeriodStart": "string (iso-8601 datetime)",
  "currentPeriodEnd": "string (iso-8601 datetime)",
  "hasUnpaidInvoices": "boolean",
  "cancelAtPeriodEnd": "boolean"
}
```


## Drift check
- **shared-with-producer:** `true` —
  producer and consumer reference the same DTO class (no static drift detected).
- Field-value drift cannot be detected statically.

## Evidence
- Consumer site: `user-backend/usermanagement-dtos/src/main/java/cars/ship/usermanagement/dtos/v2/V2CompanySubscriptionPubSubDto.java:L1`
- DTO source: `user-backend/usermanagement-dtos/src/main/java/cars/ship/usermanagement/dtos/v2/V2CompanySubscriptionPubSubDto.java`
- Topic registry row: [../event-catalog.md](../event-catalog.md)
