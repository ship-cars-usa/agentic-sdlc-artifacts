---
topic: user-state-v2
producers: [user-backend]
consumers: []
tier: carrier
canonical-dto: cars.ship.usermanagement.dtos.v2.V2UserAccountPubSubDto
canonical-dto-file: ~/projects/ship-cars-usa/user-backend/usermanagement-dtos/src/main/java/cars/ship/usermanagement/dtos/v2/V2UserAccountPubSubDto.java
schema-source: lombok-data
shared-with-producer: true
last-generated-date: 2026-05-15
status: stub
---

# Topic `user-state-v2` — schema

Canonical DTO: `cars.ship.usermanagement.dtos.v2.V2UserAccountPubSubDto`
(consumer-side, from `user-backend/usermanagement-dtos/src/main/java/cars/ship/usermanagement/dtos/v2/V2UserAccountPubSubDto.java`)

**Forward-compatible:** consumer is annotated with `@JsonIgnoreProperties(ignoreUnknown = true)` — unknown JSON fields are silently dropped on deserialization.

## Payload shape (recursive JSON preview)

**Total fields:** 22

Values are JSON type annotations (e.g. `"string"`, `"integer"`, `"string (enum: A|B|C)"`). Nested DTOs are expanded inline; arrays use a single-element list to show the item shape; maps use `{"<key>": <value>}`. Generic placeholders show as `<T>`. Cycle / depth-capped types show as `<TypeName (cycle)>` / `<TypeName (depth-cap)>`.

```json
{
  "id": "string",
  "active": "boolean",
  "lastModified": "string (iso-8601 datetime)",
  "createdAt": "string (iso-8601 datetime)",
  "keycloakId": "string",
  "name": "string",
  "street": "string",
  "city": "string",
  "state": "string",
  "zipCode": "string",
  "email": "string",
  "phoneNumber": "string",
  "owner": "boolean",
  "admin": "boolean",
  "company": {
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
  },
  "profilePictureUrl": "string",
  "roles": [
    "string (enum: ACCOUNTANT|DISPATCHER|DRIVER|SUPERVISOR)"
  ],
  "primaryRole": "string (enum: ACCOUNTANT|DISPATCHER|DRIVER|SUPERVISOR)",
  "changedFields": [
    "string"
  ],
  "mainUserId": "string",
  "mainUserEmail": "string",
  "mainCompanyId": "string"
}
```


## Drift check
- **shared-with-producer:** `true` —
  producer and consumer reference the same DTO class (no static drift detected).
- Field-value drift cannot be detected statically.

## Evidence
- Consumer site: `user-backend/usermanagement-dtos/src/main/java/cars/ship/usermanagement/dtos/v2/V2UserAccountPubSubDto.java:L1`
- DTO source: `user-backend/usermanagement-dtos/src/main/java/cars/ship/usermanagement/dtos/v2/V2UserAccountPubSubDto.java`
- Topic registry row: [../event-catalog.md](../event-catalog.md)
