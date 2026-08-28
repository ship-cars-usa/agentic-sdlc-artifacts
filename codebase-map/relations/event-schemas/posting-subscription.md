---
topic: posting-subscription
producers: []
consumers: [invoices]
tier: carrier
canonical-dto: cars.ship.posting.dtos.pubsub.LoadLegMsgPubSubDto
canonical-dto-file: ~/projects/ship-cars-usa/posting-backend/posting-dtos/src/main/java/cars/ship/posting/dtos/pubsub/LoadLegMsgPubSubDto.java
schema-source: lombok-data
shared-with-producer: true
last-generated-date: 2026-05-15
status: stub
---

# Topic `posting-subscription` — schema

Canonical DTO: `cars.ship.posting.dtos.pubsub.LoadLegMsgPubSubDto`
(consumer-side, from `posting-backend/posting-dtos/src/main/java/cars/ship/posting/dtos/pubsub/LoadLegMsgPubSubDto.java`)

**Forward-compatible:** consumer is annotated with `@JsonIgnoreProperties(ignoreUnknown = true)` — unknown JSON fields are silently dropped on deserialization.

## Payload shape (recursive JSON preview)

**Total fields:** 9

Values are JSON type annotations (e.g. `"string"`, `"integer"`, `"string (enum: A|B|C)"`). Nested DTOs are expanded inline; arrays use a single-element list to show the item shape; maps use `{"<key>": <value>}`. Generic placeholders show as `<T>`. Cycle / depth-capped types show as `<TypeName (cycle)>` / `<TypeName (depth-cap)>`.

```json
{
  "shipperCompanyId": "string",
  "action": "string (enum: UPDATE|CREATE|LOAD_LEG_PICKED_UP|LOAD_LEG_DELIVERED|SHIPPING_ITEM_PICKED_UP|SHIPPING_ITEM_DELIVERED|LOAD_LEG_ARCHIVED|DRIVER_ASSIGNED|...)",
  "actionData": {
    "addedAttachmentId": "string",
    "coordinates": {
      "latitude": "number",
      "longitude": "number"
    }
  },
  "targetId": "string",
  "loadLeg": {
    "id": "string",
    "status": "string (enum: NEW|PENDING_POSTING|POSTED|PENDING_CLAIM|CARRIER_PENDING|DISPATCHED|DRY_RUN_PENDING|DRY_RUN|...)",
    "bookingAgent": "string",
    "shipperLoadId": "string",
    "shipperExternalId": "string",
    "payments": [
      {
        "id": "string",
        "carrierPayInCents": "integer (long)",
        "notes": "string",
        "paymentType": "string (enum: COD|COP|USHIP|BILLING)",
        "paymentTransactionType": "string (enum: CUSTOMER_TO_CARRIER|CARRIER_TO_SHIPPER|SHIPPER_TO_CARRIER|CUSTOMER_TO_CARRIER|CARRIER_TO_SHIPPER|SHIPPER_TO_CARRIER|CUSTOMER_TO_CARRIER|CARRIER_TO_SHIPPER|...)",
        "paymentMethod": "string (enum: CASH|CERTIFIED_FUNDS|ACH|SMARTHAUL_PAYMENTS|COMPANY_CHECK|WIRE_TRANSFER|COMCHEK|VENMO|...)",
        "paymentTermsBeginType": "string (enum: ON_PICKUP|ON_DELIVERY|ON_BOL|ON_RECEIPT_INVOICE|ON_PICKUP|ON_DELIVERY|ON_BOL|ON_RECEIPT_INVOICE)",
        "paymentTermsType": "string (enum: IMMEDIATE|TWO_DAYS|FIVE_DAYS|TEN_DAYS|FIFTEEN_DAYS|THIRTY_DAYS|SIXTY_DAYS|NET_SEVEN_DAYS|...)"
      }
    ],
    "carrierPayInCents": "integer (long)",
    "createdAt": "string (iso-8601 datetime)",
    "lastModified": "string (iso-8601 datetime)",
    "type": "string (enum: STANDARD|MANAGED_ORDER|DRIVEAWAY|CHASE_DRIVER)",
    "labels": [
      "string"
    ],
    "contract": {
      "id": "string",
      "shipperId": "string",
      "crossRegionalType": "string (enum: PICKUP_LOCATION_PRICING|DELIVERY_LOCATION_PRICING)",
      "active": "boolean",
      "createdAt": "string (iso-8601 datetime)",
      "lastModified": "string (iso-8601 datetime)",
      "carriers": [
        "<@Valid CarrierDto>"
      ],
      "customers": [
        "<@Valid CustomerDto>"
      ],
      "regions": [
        "<@Valid RegionDto>"
      ],
      "powerLanes": [
        "<@Valid PowerLaneDto>"
      ],
      "surcharges": [
        "<@Valid SurchargeDto>"
      ],
      "discounts": [
        "<@Valid DiscountDto>"
      ]
    },
    "attachments": [
      {
        "id": "string",
        "url": "string",
        "file": "string",
        "image": {
          "full_size": "string",
          "thumbnail": "string"
        },
        "damages": [
          {
            "id": "string",
            "url": "string",
            "type": "string",
            "segment": "string",
            "timestamp": "string (iso-8601 datetime)",
            "location": {
              "type": "string",
              "coordinates": [
                "number"
              ]
            },
            "attachment": "string",
            "attachment_id": "string"
          }
        ],
        "load": "string",
        "order": "string",
        "creator": "string",
        "segment": "string",
        "converted_timestamp": "string",
        "creator_company_id": "string",
        "creator_company_user_management_id": "string",
        "is_shared_with_shipper": "boolean",
        "type": "string",
        "original_file": "string",
        "height": "string",
        "width": "string",
        "active": "boolean",
        "share_with_driver": "boolean",
        "share_with_shipper": "boolean",
        "location": {
          "type": "string",
          "coordinates": [
            "number"
          ]
        },
        "location_address": "string",
        "comments": "string",
        "create_time": "string (iso-8601 datetime)",
        "timestamp": "string (iso-8601 datetime)",
        "timezone": "string",
        "area": "string",
        "description": "string",
        "vehicle": "string",
        "load_id": "string",
        "order_id": "string",
        "creator_id": "string",
        "creator_user_management_id": "string",
        "vehicle_id": "string",
        "driver_only": "boolean"
      }
    ],
    "publicLinkInfo": {
      "id": "string",
      "publicLinkKey": "string",
      "publicLink": "string"
    },
    "externalId": "string",
    "load": {
      "id": "string",
      "url": "string",
      "vehicles": [
        {
          "vehicleId": "string",
          "type": "string",
          "model": "string",
          "originalModel": "string",
          "year": "integer",
          "make": "string",
          "vehicleType": "string",
          "rearAxle": "string",
          "bodyType": "string",
          "bodySubtype": "string",
          "approxBedLength": "string",
          "image": "string",
          "fuelTypes": [
            "string"
          ],
          "specifications": {
            "<string>": "any"
          },
          "msrp": "integer"
        }
      ],
      "trips": [
        {
          "id": "string",
          "name": "string",
          "status": "string (enum: ACTIVE|COMPLETED)",
          "capacity": "integer",
          "driver": {
            "id": "string",
            "full_name": "string",
            "profile_picture": "string"
          },
          "origin": {
            "city": "string",
            "state": "string",
            "zip": "string"
          },
          "destination": {
            "city": "string",
            "state": "string",
            "zip": "string"
          },
          "revenue": "number",
          "route": {
            "distance": "<DistanceDto (depth-cap)>",
            "items": [
              "<LocationDto (depth-cap)>"
            ]
          },
          "plan": [
            {
              "exceeding_capacity": "boolean",
              "spots": [
                "<SpotDto (depth-cap)>"
              ]
            }
          ],
          "loads": [
            {
              "id": "string",
              "load_id": "string",
              "shipper_load_id": "string",
              "pickup_city": "<CityStateDto (depth-cap)>",
              "delivery_city": "<CityStateDto (depth-cap)>",
              "pickup_dates_range": "<DateRangeDto (depth-cap)>",
              "delivery_dates_range": "<DateRangeDto (depth-cap)>",
              "vehicles_count": "integer",
              "status": "<TripLoadDtoStatus (depth-cap)>",
              "total_payment_to_carrier": "number"
            }
          ],
          "stops": [
            {
              "trip_load_id": "string",
              "type": "<StopType (depth-cap)>"
            }
          ],
          "vault": [
            {
              "trip_load_id": "string",
              "type": "<StopType (depth-cap)>"
            }
          ],
          "start_date": "string (iso-8601 date)",
          "end_date": "string (iso-8601 date)"
        }
      ],
      "activity_log": [
        {
          "id": "string",
          "event_type": "string",
          "event_type_category": "string",
          "extra_object": {
            "pk": "string",
            "object_type": "string",
            "user_management_id": "string",
            "recipients_list": [
              "string"
            ],
            "initial_recipients": [
              "string"
            ],
            "recipient": "string",
            "create_time": "string (iso-8601 datetime)",
            "status": "string",
            "external_id": "string",
            "revision_number": "integer",
            "shipper_load_id": "string"
          },
          "actor_company": "string",
          "actor_company_user_management_id": "string",
          "carrier": "string",
          "broker": "string",
          "shipper": "string",
          "timestamp": "string (iso-8601 datetime)",
          "load": "string",
          "actor": "string",
          "carrier_id": "string",
          "carrier_user_management_id": "string",
          "broker_id": "string",
          "broker_user_management_id": "string",
          "shipper_id": "string",
          "shipper_user_management_id": "string",
          "actor_company_id": "string",
          "order": "string",
          "order_id": "string",
          "load_id": "string",
          "actor_id": "string",
          "actor_user_management_id": "string",
          "comment": "string"
        }
      ],
      "attachments": [
        {
          "id": "string",
          "url": "string",
          "file": "string",
          "image": {
            "full_size": "string",
            "thumbnail": "string"
          },
          "damages": [
            {
              "id": "string",
              "url": "string",
              "type": "string",
              "segment": "string",
              "timestamp": "string (iso-8601 datetime)",
              "location": "<AddressLocationDto (depth-cap)>",
              "attachment": "string",
              "attachment_id": "string"
            }
          ],
          "load": "string",
          "order": "string",
          "creator": "string",
          "segment": "string",
          "converted_timestamp": "string",
          "creator_company_id": "string",
          "creator_company_user_management_id": "string",
          "is_shared_with_shipper": "boolean",
          "type": "string",
          "original_file": "string",
          "height": "string",
          "width": "string",
          "active": "boolean",
          "share_with_driver": "boolean",
          "share_with_shipper": "boolean",
          "location": {
            "type": "string",
            "coordinates": [
              "number"
            ]
          },
          "location_address": "string",
          "comments": "string",
          "create_time": "string (iso-8601 datetime)",
          "timestamp": "string (iso-8601 datetime)",
          "timezone": "string",
          "area": "string",
          "description": "string",
          "vehicle": "string",
          "load_id": "string",
          "order_id": "string",
          "creator_id": "string",
          "creator_user_management_id": "string",
          "vehicle_id": "string",
          "driver_only": "boolean"
        }
      ],
      "distance_imperial": "integer",
      "driver_verification_expiration": "string (iso-8601 datetime)",
      "broker": "string",
      "shipper": "string",
      "payment_to_carrier": "string",
      "carrier_dot_number": "string",
      "payment_hidden_from_driver": "boolean",
      "forbid_vehicle_update": "boolean",
      "driver_is_active": "boolean",
      "driver_name": "string",
      "driver_phone_number": "string",
      "driver_email": "string",
      "referral": "string",
      "force_dates_estimation": "boolean",
      "posting": {
        "status": "string"
      },
      "broker_dot_number": "string",
      "shipper_dot_number": "string",
      "shipper_logo": "string",
      "shipper_city": "string",
      "shipper_state": "string",
      "shipper_zip": "string",
      "broker_load_id": "string",
      "terms_and_conditions": "string",
      "invoice_number": "string",
      "can_be_claimed": "boolean",
      "shipper_name": "string",
      "shipper_address": "string",
      "shipper_email": "string",
      "shipper_phone": "string",
      "price_per_mile": "number",
      "inspection_configuration": {
        "level": "integer",
        "roof_photo": "boolean",
        "odometer_photo": "boolean",
        "custom_photos": [
          {
            "id": "string",
            "area": "string",
            "description": "string",
            "_localPhotoUri": "string"
          }
        ]
      },
      "location_sharing_required_by_shipper": "boolean",
      "pickup_requested_times": "string",
      "pickup_name": "string",
      "pickup_contact": "string",
      "pickup_address": "string",
      "pickup_address_location": {
        "type": "string",
        "coordinates": [
          "number"
        ]
      },
      "pickup_city": "string",
      "pickup_state": "string",
      "pickup_zip": "string",
      "pickup_phone_1": "string",
      "pickup_phone_1_notes": "string",
      "pickup_phone_1_type": "string",
      "pickup_phone_2": "string",
      "pickup_phone_2_notes": "string",
      "pickup_phone_2_type": "string",
      "pickup_phone_3": "string",
      "pickup_phone_3_notes": "string",
      "pickup_phone_3_type": "string",
      "pickup_date": "string (iso-8601 datetime)",
      "pickup_no_damages": "boolean",
      "pickup_notes": "string",
      "pickup_customer_not_present": "boolean",
      "pickup_estimate_type": "string",
      "pickup_estimate_date": "string (iso-8601 datetime)",
      "pickup_estimate_end_type": "string",
      "pickup_estimate_end_date": "string (iso-8601 datetime)",
      "pickup_requested_date_start": "string (iso-8601 datetime)",
      "pickup_requested_date_start_type": "string",
      "pickup_requested_date_end": "string (iso-8601 datetime)",
      "pickup_requested_date_end_type": "string",
      "pickup_contract_date_start": "string (iso-8601 datetime)",
      "pickup_contract_date_start_type": "string",
      "pickup_contract_date_end": "string (iso-8601 datetime)",
      "pickup_contract_date_end_type": "string",
      "pickup_contact_is_personal": "boolean",
      "pickup_email_1": "string",
      "pickup_email_2": "string",
      "pickup_email_3": "string",
      "pickup_working_time_start": "string",
      "pickup_working_time_end": "string",
      "pickup_estimate_timeframe": "string",
      "pickup_estimate_reason": "string",
      "pickup_estimate_date_status": "string",
      "pickup_estimate_date_status_timestamp": "string (iso-8601 datetime)",
      "delivery_requested_times": "string",
      "delivery_name": "string",
      "delivery_contact": "string",
      "delivery_address": "string",
      "delivery_address_location": {
        "type": "string",
        "coordinates": [
          "number"
        ]
      },
      "delivery_city": "string",
      "delivery_state": "string",
      "delivery_zip": "string",
      "delivery_phone_1": "string",
      "delivery_phone_1_notes": "string",
      "delivery_phone_1_type": "string",
      "delivery_phone_2": "string",
      "delivery_phone_2_notes": "string",
      "delivery_phone_2_type": "string",
      "delivery_phone_3": "string",
      "delivery_phone_3_notes": "string",
      "delivery_phone_3_type": "string",
      "delivery_date": "string (iso-8601 datetime)",
      "delivery_notes": "string",
      "delivery_customer_not_present": "boolean",
      "delivery_no_damages": "string",
      "delivery_estimate_type": "string",
      "delivery_estimate_date": "string (iso-8601 datetime)",
      "delivery_estimate_end_type": "string",
      "delivery_estimate_end_date": "string (iso-8601 datetime)",
      "delivery_requested_date_start": "string (iso-8601 datetime)",
      "delivery_requested_date_start_type": "string",
      "delivery_requested_date_end": "string (iso-8601 datetime)",
      "delivery_requested_date_end_type": "string",
      "delivery_contract_date_start": "string (iso-8601 datetime)",
      "delivery_contract_date_start_type": "string",
      "delivery_contract_date_end": "string (iso-8601 datetime)",
      "delivery_contract_date_end_type": "string",
      "delivery_contact_is_personal": "boolean",
      "delivery_email_1": "string",
      "delivery_email_2": "string",
      "delivery_email_3": "string",
      "delivery_working_time_start": "string",
      "delivery_working_time_end": "string",
      "delivery_estimate_timeframe": "string",
      "delivery_estimate_reason": "string",
      "delivery_estimate_date_status": "string",
      "delivery_estimate_date_status_timestamp": "string (iso-8601 datetime)",
      "transit_time_estimated_min": "integer",
      "transit_time_estimated_max": "integer",
      "exclusivity_expiration_time": "string (iso-8601 datetime)",
      "posted_externally_time": "string (iso-8601 datetime)",
      "accept_time": "string (iso-8601 datetime)",
      "assign_time": "string (iso-8601 datetime)",
      "last_change_time": "string (iso-8601 datetime)",
      "distance": "integer",
      "last_dispatch_generate_time": "string (iso-8601 datetime)",
      "last_dispatch_generate_user_email": "string",
      "listed_price": "number",
      "payment_on_pickup": "number",
      "payment_on_pickup_method": "string",
      "payment_on_delivery": "number",
      "payment_on_delivery_method": "string",
      "total_payment_to_carrier": "number",
      "payables": "number",
      "receivables": "number",
      "payment_term_business_days": "string",
      "payment_term_begins": "string",
      "payment_method": "string",
      "payment_notes": "string",
      "actual_payment_on_pickup_method": "string",
      "actual_payment_on_delivery_method": "string",
      "customer_name": "string",
      "customer_contact": "string",
      "customer_address": "string",
      "customer_city": "string",
      "customer_state": "string",
      "customer_zip": "string",
      "customer_contact_is_personal": "boolean",
      "customer_email": "string",
      "customer_email_2": "string",
      "customer_email_3": "string",
      "customer_phone_1": "string",
      "customer_phone_1_notes": "string",
      "customer_phone_1_type": "string",
      "customer_phone_2": "string",
      "customer_phone_2_notes": "string",
      "customer_phone_2_type": "string",
      "customer_phone_3": "string",
      "customer_phone_3_notes": "string",
      "customer_phone_3_type": "string",
      "customer_working_time_start": "string (iso-8601 datetime)",
      "customer_working_time_end": "string (iso-8601 datetime)",
      "accepted": "boolean",
      "force_driver_assignment": "boolean",
      "labels": [
        "string"
      ],
      "can_be_booked": "boolean",
      "uship_code": "string",
      "demo": "boolean",
      "shipper_load_id": "string",
      "external_trip_id": "string",
      "instructions": "string",
      "specific_load_requirements": "string",
      "driver_instructions": "string",
      "status": "string",
      "first_available_date": "string (iso-8601 datetime)",
      "enclosed_trailer": "boolean",
      "dispatch_date": "string (iso-8601 datetime)",
      "create_time": "string (iso-8601 datetime)",
      "update_time": "string (iso-8601 datetime)",
      "requested_bol_address_pickup": "string",
      "requested_bol_address_delivery": "string",
      "seen_by_driver_time": "string (iso-8601 datetime)",
      "flags": [
        "string"
      ],
      "resolution": "string",
      "expiration_time": "string (iso-8601 datetime)",
      "invoice_time": "string (iso-8601 datetime)",
      "damages_type": "string",
      "star_rating": "integer",
      "star_rating_expiration_time": "string (iso-8601 datetime)",
      "source": "string",
      "source_sync_status": "string",
      "performance": "boolean",
      "shipper_meta": "any",
      "posted_on_cd": "integer",
      "truck_number_required": "boolean",
      "truck_number": "string",
      "carrier": "string",
      "dispatcher": "string",
      "demo_owner": "string",
      "active_change": "string",
      "active_revision": "string",
      "driver": "string",
      "trip": "string",
      "broker_id": "string",
      "broker_user_management_id": "string",
      "shipper_id": "string",
      "shipper_user_management_id": "string",
      "carrier_id": "string",
      "carrier_user_management_id": "string",
      "dispatcher_id": "string",
      "dispatcher_user_management_id": "string",
      "demo_owner_id": "string",
      "demo_owner_user_management_id": "string",
      "active_change_id": "string",
      "active_revision_id": "string",
      "driver_id": "string",
      "driver_user_management_id": "string",
      "trip_id": "string",
      "virtual_trip_id": "string",
      "virtual_trip_name": "string",
      "cancel_reason": "string",
      "decline_reason": "string",
      "internal_load_id": "string",
      "public_tracking_id": "string",
      "carrier_name": "string",
      "carrier_phone_number": "string",
      "carrier_email": "string",
      "public_tracking_link": "string",
      "preferred_only": "boolean",
      "posted_to_carriers_user_management_id": [
        "string"
      ],
      "pickup_working_hours": "string",
      "delivery_working_hours": "string",
      "payment_term_calendar_days": "integer",
      "other_reason_text": "string",
      "shipper_vip_level": "string",
      "parent_order_id": "string",
      "has_sub_orders": "boolean",
      "collect_payment": "boolean",
      "geofence_enabled": "boolean",
      "atg_enabled": "boolean",
      "atg_fields_masked": "boolean",
      "atg_driver_code": "string",
      "delivery_address_not_correct": "boolean",
      "payment_state": "string",
      "pickup_contact_note": "string",
      "delivery_contact_note": "string",
      "specific_public_posting_notes": "string",
      "driver_ids_participated_in_booking": [
        "string"
      ]
    },
    "driveaway": {
      "expirationTime": "string (iso-8601 datetime)",
      "state": "string (enum: CANCELLED|SHIPPER_CANCELLED|DECLINED|ACTIVE|DELIVERED|ARCHIVED)",
      "driver": {
        "id": "string",
        "name": "string",
        "companyName": "string",
        "address": "string",
        "city": "string",
        "state": "string",
        "zip": "string",
        "email": "string",
        "phone": "string",
        "phoneNotes": "string",
        "notes": "string",
        "active": "boolean",
        "enforceTermsAndConditions": "boolean"
      },
      "publicKey": "string"
    },
    "shippingItems": [
      {
        "id": "string",
        "vehicle": {
          "vehicleId": "string",
          "type": "string",
          "model": "string",
          "originalModel": "string",
          "year": "integer",
          "make": "string",
          "vehicleType": "string",
          "rearAxle": "string",
          "bodyType": "string",
          "bodySubtype": "string",
          "approxBedLength": "string",
          "image": "string",
          "fuelTypes": [
            "string"
          ],
          "specifications": {
            "<string>": "any"
          },
          "msrp": "integer"
        },
        "route": {
          "distance": {
            "kilometers": "number (decimal)",
            "label": "string",
            "shortLabel": "string"
          },
          "items": [
            {
              "address": "<AddressDto (depth-cap)>",
              "timeFrame": "<TimeFrameValueDto (depth-cap)>"
            }
          ]
        },
        "pickupContact": {
          "id": "string",
          "firstName": "string",
          "lastName": "string",
          "phoneNumber": "string",
          "primaryPhoneNotes": "string",
          "secondaryPhone": "string",
          "secondaryPhoneNotes": "string",
          "thirdPhone": "string",
          "thirdPhoneNotes": "string",
          "workingHours": "string",
          "companyName": "string",
          "streetAddress": "string",
          "locationId": "string",
          "city": "string",
          "state": "string",
          "zipCode": "string",
          "emailAddress": "string"
        },
        "deliveryContact": {
          "id": "string",
          "firstName": "string",
          "lastName": "string",
          "phoneNumber": "string",
          "primaryPhoneNotes": "string",
          "secondaryPhone": "string",
          "secondaryPhoneNotes": "string",
          "thirdPhone": "string",
          "thirdPhoneNotes": "string",
          "workingHours": "string",
          "companyName": "string",
          "streetAddress": "string",
          "locationId": "string",
          "city": "string",
          "state": "string",
          "zipCode": "string",
          "emailAddress": "string"
        },
        "customer": {
          "id": "string",
          "firstName": "string",
          "lastName": "string",
          "phoneNumber": "string",
          "primaryPhoneNotes": "string",
          "secondaryPhone": "string",
          "secondaryPhoneNotes": "string",
          "thirdPhone": "string",
          "thirdPhoneNotes": "string",
          "workingHours": "string",
          "companyName": "string",
          "streetAddress": "string",
          "locationId": "string",
          "city": "string",
          "state": "string",
          "zipCode": "string",
          "emailAddress": "string"
        },
        "attachments": [
          {
            "id": "string",
            "url": "string",
            "file": "string",
            "image": {
              "full_size": "string",
              "thumbnail": "string"
            },
            "damages": [
              {
                "id": "string",
                "url": "string",
                "type": "string",
                "segment": "string",
                "timestamp": "string (iso-8601 datetime)",
                "location": "<AddressLocationDto (depth-cap)>",
                "attachment": "string",
                "attachment_id": "string"
              }
            ],
            "load": "string",
            "order": "string",
            "creator": "string",
            "segment": "string",
            "converted_timestamp": "string",
            "creator_company_id": "string",
            "creator_company_user_management_id": "string",
            "is_shared_with_shipper": "boolean",
            "type": "string",
            "original_file": "string",
            "height": "string",
            "width": "string",
            "active": "boolean",
            "share_with_driver": "boolean",
            "share_with_shipper": "boolean",
            "location": {
              "type": "string",
              "coordinates": [
                "number"
              ]
            },
            "location_address": "string",
            "comments": "string",
            "create_time": "string (iso-8601 datetime)",
            "timestamp": "string (iso-8601 datetime)",
            "timezone": "string",
            "area": "string",
            "description": "string",
            "vehicle": "string",
            "load_id": "string",
            "order_id": "string",
            "creator_id": "string",
            "creator_user_management_id": "string",
            "vehicle_id": "string",
            "driver_only": "boolean"
          }
        ],
        "routeName": "string",
        "routeOrder": "integer",
        "carrierPayInCents": "integer (long)",
        "checkedInAt": "string (iso-8601 datetime)",
        "contractPricing": {
          "type": "string (enum: AUTO|OVERRIDDEN)",
          "calculation": {
            "basePrice": "number (decimal)",
            "totalPrice": "number (decimal)",
            "lineItems": [
              "<LineItemCalculationDto (depth-cap)>"
            ],
            "distance": "number (decimal)",
            "pricePerMile": "number (decimal)"
          }
        },
        "shipperExternalId": "string",
        "generateCustomerInvoice": "boolean",
        "allowDriverEdits": "boolean",
        "status": "string (enum: NEW|DISPATCHED|DRY_RUN_PENDING|DRY_RUN|PICKED_UP|DELIVERED|ARCHIVED)",
        "m22Damages": [
          {
            "id": "string",
            "type": "string",
            "area": "string",
            "vehicle_id": "string",
            "inspection_type": "string",
            "severity": "string"
          }
        ],
        "driveawayDriver": {
          "id": "string",
          "name": "string",
          "companyName": "string",
          "address": "string",
          "city": "string",
          "state": "string",
          "zip": "string",
          "email": "string",
          "phone": "string",
          "phoneNotes": "string",
          "notes": "string",
          "active": "boolean",
          "enforceTermsAndConditions": "boolean"
        }
      }
    ],
    "contractPricing": {
      "type": "string (enum: AUTO|OVERRIDDEN)",
      "calculation": {
        "basePrice": "number (decimal)",
        "totalPrice": "number (decimal)",
        "lineItems": [
          {
            "type": "<LineItemTypeEnum (depth-cap)>",
            "description": "string",
            "title": "string",
            "price": "number (decimal)"
          }
        ],
        "distance": "number (decimal)",
        "pricePerMile": "number (decimal)"
      }
    },
    "orderInformation": {
      "id": "string",
      "refId": "string",
      "orderId": "string",
      "selectedQuoteId": "string",
      "selectedQuoteRateType": "string",
      "providerId": "string",
      "providerName": "string",
      "providerLogoUrl": "string"
    },
    "extRateCalculationId": "string",
    "centralDispatchId": "string",
    "postToCentralDispatch": "boolean",
    "centralDispatchAction": "string (enum: POST|UN_POST|RE_POST)",
    "carrier": {
      "id": "string",
      "name": "string",
      "isUsingContractPricing": "boolean",
      "usDotNumber": "string",
      "logoUrl": "string",
      "active": "boolean",
      "createdAt": "string (iso-8601 datetime)",
      "lastModified": "string (iso-8601 datetime)",
      "externalId": "string"
    },
    "driver": {
      "id": "string",
      "name": "string",
      "email": "string",
      "phone": "string",
      "additionalPhone": "string",
      "lbExternalId": "string",
      "profilePictureUrl": "string",
      "userManagementId": "string"
    },
    "carrierOffers": [
      {
        "offer": "string"
      }
    ],
    "pickupSignatureRequired": "boolean",
    "deliverySignatureRequired": "boolean",
    "externalDestination": "string (enum: PUBLIC_LOADBOARD|PRIVATE_LOADBOARD)",
    "undispatchReason": {
      "value": "string",
      "type": "string (enum: DECLINE)"
    }
  },
  "timestamp": "string (iso-8601 datetime)",
  "statuses": [
    {
      "status": "string (enum: NEW|PENDING_POSTING|POSTED|PENDING_CLAIM|CARRIER_PENDING|DISPATCHED|DRY_RUN_PENDING|DRY_RUN|...)",
      "active": "boolean",
      "lastModified": "string (iso-8601 datetime)"
    }
  ],
  "changedFields": [
    "string"
  ],
  "actor": {
    "id": "string",
    "name": "string",
    "owner": "boolean",
    "street": "string",
    "city": "string",
    "state": "string",
    "zipCode": "string",
    "email": "string",
    "phoneNumber": "string",
    "company": {
      "url": "string",
      "id": "string",
      "features": [
        "string"
      ],
      "labels": {
        "<string>": "any"
      },
      "mandatory_tac": "string",
      "is_broker": "boolean",
      "exclusivity_enabled": "boolean",
      "inspection_configuration": {
        "level": "integer",
        "roof_photo": "boolean",
        "odometer_photo": "boolean",
        "custom_photos": [
          {
            "id": "string",
            "area": "string",
            "description": "string",
            "_localPhotoUri": "string"
          }
        ]
      },
      "billing": {
        "company": "integer",
        "next_invoice_number": "integer",
        "invoice_prefix": "string",
        "invoice_enabled": "boolean",
        "accounting_email": "string",
        "accounting_phone_1": "string",
        "accounting_phone_1_notes": "string",
        "accounting_phone_1_type": "string",
        "accounting_phone_2": "string",
        "accounting_phone_2_notes": "string",
        "accounting_phone_2_type": "string",
        "accounting_phone_3": "string",
        "accounting_phone_3_notes": "string",
        "accounting_phone_3_type": "string",
        "accounting_address": "string",
        "accounting_city": "string",
        "accounting_state": "string",
        "accounting_zip": "string",
        "factoring_name": "string",
        "factoring_address": "string",
        "factoring_city": "string",
        "factoring_state": "string",
        "factoring_zip": "string",
        "factoring_phone": "string",
        "factoring_email": "string",
        "factoring_payment_terms_business_days": "string",
        "customer_message": "string",
        "default_to_factoring_company": "boolean"
      },
      "compliance_status": "string",
      "compliance_instabook": "boolean",
      "compliance_link_id": "string",
      "compliance_notes": "string",
      "slug": "string",
      "name": "string",
      "is_shipper": "boolean",
      "is_carrier": "boolean",
      "is_single_owner_operator": "boolean",
      "dot_number": "integer",
      "mc_number": "string",
      "address": "string",
      "city": "string",
      "state": "string",
      "zip": "string",
      "logo": "string",
      "email": "string",
      "phone_1": "string",
      "phone_1_notes": "string",
      "phone_1_type": "string",
      "phone_2": "string",
      "phone_2_notes": "string",
      "phone_2_type": "string",
      "phone_3": "string",
      "phone_3_notes": "string",
      "phone_3_type": "string",
      "accounting_email": "string",
      "accounting_phone_1": "string",
      "accounting_phone_1_notes": "string",
      "accounting_phone_1_type": "string",
      "accounting_phone_2": "string",
      "accounting_phone_2_notes": "string",
      "accounting_phone_2_type": "string",
      "accounting_phone_3": "string",
      "accounting_phone_3_notes": "string",
      "accounting_phone_3_type": "string",
      "accounting_address": "string",
      "accounting_city": "string",
      "accounting_state": "string",
      "accounting_zip": "string",
      "terms_of_service": "string",
      "test": "boolean",
      "cd_uid": "string",
      "create_time": "string",
      "update_time": "string",
      "internal_link_format": "string",
      "invoice_enabled": "boolean",
      "email_notifications_enabled": "boolean",
      "hide_user_list": "boolean",
      "invoice_prefix": "string",
      "next_invoice_number": "integer",
      "type": "string",
      "type_description": "string",
      "auto_verified": "boolean",
      "user_management_id": "string",
      "company_owner": "string",
      "company_owner_id": "string"
    },
    "profilePictureUrl": "string",
    "active": "boolean",
    "roles": [
      "string (enum: ACCOUNTANT|DISPATCHER|DRIVER|SUPERVISOR)"
    ],
    "primaryRole": "string (enum: ACCOUNTANT|DISPATCHER|DRIVER|SUPERVISOR)"
  }
}
```


## Drift check
- **shared-with-producer:** `true` —
  producer and consumer reference the same DTO class (no static drift detected).
- Field-value drift cannot be detected statically.

## Evidence
- Consumer site: `invoices/services/src/main/java/cars/ship/invoices/listeners/PostingPubSubListener.java:L32`
- DTO source: `posting-backend/posting-dtos/src/main/java/cars/ship/posting/dtos/pubsub/LoadLegMsgPubSubDto.java`
- Topic registry row: [../event-catalog.md](../event-catalog.md)
