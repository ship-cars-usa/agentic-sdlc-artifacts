---
topic: keycloak-subscription
producers: []
consumers: [fraud-detector]
tier: fleet
canonical-dto: cars.ship.modelslib.apidtos.keycloak.KeyCloakEventDto
canonical-dto-file: ~/projects/ship-cars-usa/models-lib/api-dtos/src/main/java/cars/ship/modelslib/apidtos/keycloak/KeyCloakEventDto.java
schema-source: lombok-data
shared-with-producer: true
last-generated-date: 2026-05-15
status: stub
---

# Topic `keycloak-subscription` — schema

Canonical DTO: `cars.ship.modelslib.apidtos.keycloak.KeyCloakEventDto`
(consumer-side, from `models-lib/api-dtos/src/main/java/cars/ship/modelslib/apidtos/keycloak/KeyCloakEventDto.java`)


## Payload shape (recursive JSON preview)

**Total fields:** 12

Values are JSON type annotations (e.g. `"string"`, `"integer"`, `"string (enum: A|B|C)"`). Nested DTOs are expanded inline; arrays use a single-element list to show the item shape; maps use `{"<key>": <value>}`. Generic placeholders show as `<T>`. Cycle / depth-capped types show as `<TypeName (cycle)>` / `<TypeName (depth-cap)>`.

```json
{
  "id": "string",
  "time": "integer (long)",
  "type": "string",
  "realmId": "string",
  "realmName": "string",
  "clientId": "string",
  "userId": "string",
  "sessionId": "string",
  "ipAddress": "string",
  "error": "string",
  "details": {
    "<string>": "any"
  },
  "user": {
    "firstName": "string",
    "lastName": "string",
    "isEnabled": "boolean",
    "username": "string",
    "email": "string",
    "isEmailVerified": "boolean"
  }
}
```


## Drift check
- **shared-with-producer:** `true` —
  producer and consumer reference the same DTO class (no static drift detected).
- Field-value drift cannot be detected statically.

## Evidence
- Consumer site: `fraud-detector/services/src/main/java/cars/ship/frauddetector/services/listeners/KeyCloakPubSubListener.java:L19`
- DTO source: `models-lib/api-dtos/src/main/java/cars/ship/modelslib/apidtos/keycloak/KeyCloakEventDto.java`
- Topic registry row: [../event-catalog.md](../event-catalog.md)
