---
topic: company-state
producers: []
consumers: [posting-backend]
tier: carrier
canonical-dto: cars.ship.shipperlite.posting.application.adapters.in.pubsub.dto.CompanyEventPubSubDto
canonical-dto-file: ~/projects/ship-cars-usa/posting-backend/posting-app/src/main/java/cars/ship/shipperlite/posting/application/adapters/in/pubsub/dto/CompanyEventPubSubDto.java
schema-source: lombok-data
shared-with-producer: false
last-generated-date: 2026-05-15
status: stub
---

# Topic `company-state` — schema

Canonical DTO: `cars.ship.shipperlite.posting.application.adapters.in.pubsub.dto.CompanyEventPubSubDto`
(consumer-side, from `posting-backend/posting-app/src/main/java/cars/ship/shipperlite/posting/application/adapters/in/pubsub/dto/CompanyEventPubSubDto.java`)

**Forward-compatible:** consumer is annotated with `@JsonIgnoreProperties(ignoreUnknown = true)` — unknown JSON fields are silently dropped on deserialization.

## Payload shape (recursive JSON preview)

**Total fields:** 1

Values are JSON type annotations (e.g. `"string"`, `"integer"`, `"string (enum: A|B|C)"`). Nested DTOs are expanded inline; arrays use a single-element list to show the item shape; maps use `{"<key>": <value>}`. Generic placeholders show as `<T>`. Cycle / depth-capped types show as `<TypeName (cycle)>` / `<TypeName (depth-cap)>`.

```json
{
  "entity": {
    "id": "string",
    "active": "boolean",
    "name": "string",
    "companyType": "string (enum: SHIPPER|CARRIER)",
    "companySubtype": "string (enum: DEALER|AUCTION|BROKER|CARRIER)",
    "usDotNumber": "string",
    "mcNumber": "string",
    "street": "string",
    "city": "string",
    "state": "string",
    "zipCode": "string",
    "email": "string",
    "accountingEmail": "string",
    "accountingEmails": "string",
    "phoneNumber": "string",
    "termsAndConditions": "string",
    "allowInstantBooking": "boolean",
    "centralDispatchId": "string",
    "logoUrl": "string",
    "ownerName": "string",
    "ownerId": "string",
    "carrierVerified": "boolean",
    "subscription": {
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
    },
    "singleOwnerOperator": "boolean",
    "createdAt": "string (iso-8601 datetime)",
    "lastModified": "string (iso-8601 datetime)",
    "parentCompanyId": "string",
    "keycloakId": "string",
    "changedFields": [
      "string"
    ],
    "actionEvents": {
      "<string>": [
        "string"
      ]
    }
  }
}
```


## Drift check
- **shared-with-producer:** `false` —
  producer and consumer DTOs are in separate packages; L3b authors should compare shapes.
- Field-value drift cannot be detected statically.

## Evidence
- Consumer site: `posting-backend/posting-app/src/main/java/cars/ship/shipperlite/posting/application/adapters/in/pubsub/CompanyStateConsumer.java:L60`
- DTO source: `posting-backend/posting-app/src/main/java/cars/ship/shipperlite/posting/application/adapters/in/pubsub/dto/CompanyEventPubSubDto.java`
- Topic registry row: [../event-catalog.md](../event-catalog.md)
