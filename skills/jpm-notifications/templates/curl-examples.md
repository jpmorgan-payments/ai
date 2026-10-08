# Notifications API Terminal Requests

Use these commands for terminal-based API calls. Consult the
[Notifications Bruno collection](https://github.com/jpmorgan-payments/api-collections/tree/main/merchant-services/Notifications)
for the current request shapes and update the placeholders before executing any mutation.

```bash
export JPM_NOTIFICATIONS_API_URL="https://mns-aws-cat.jpmchase.com"
export JPM_ACCESS_TOKEN="<token from getAccessToken()>"
export MERCHANT_ID="MERCH-12345"
export ENTITY_TYPE="MERCHANT"
```

## Read-only requests

```bash
# Notification types
curl -sS "$JPM_NOTIFICATIONS_API_URL/v1/notificationTypes" -H "Authorization: Bearer $JPM_ACCESS_TOKEN" -H "request-id: $(uuidgen)"

# Public keys (JWKS)
curl -sS "$JPM_NOTIFICATIONS_API_URL/v1/public-keys" -H "Authorization: Bearer $JPM_ACCESS_TOKEN" -H "request-id: $(uuidgen)" -H "merchant-id: $MERCHANT_ID" -H "entity-id: $MERCHANT_ID" -H "entity-type: $ENTITY_TYPE"

# Subscriptions for an entity
curl -sS "$JPM_NOTIFICATIONS_API_URL/v1/subscriptions" -H "Authorization: Bearer $JPM_ACCESS_TOKEN" -H "request-id: $(uuidgen)" -H "merchant-id: $MERCHANT_ID" -H "entity-id: $MERCHANT_ID" -H "entity-type: $ENTITY_TYPE"

# Stored notifications by date and status (not in Bruno)
curl -sS "$JPM_NOTIFICATIONS_API_URL/v1/notifications?startdate=2026-02-01&enddate=2026-02-28&status=SENT" -H "Authorization: Bearer $JPM_ACCESS_TOKEN" -H "request-id: $(uuidgen)" -H "entity-id: $MERCHANT_ID" -H "entity-type: $ENTITY_TYPE"
```

## Mutating requests

Use the matching Bruno request body as the starting point, preview the final request with secrets
masked, and get merchant confirmation before `POST`, `PUT`, or `DELETE`.

```bash
# Create a subscription
curl -sS -X POST "$JPM_NOTIFICATIONS_API_URL/v1/subscriptions" -H "Authorization: Bearer $JPM_ACCESS_TOKEN" -H "Content-Type: application/json" -H "request-id: $(uuidgen)" -H "merchant-id: $MERCHANT_ID" -H "entity-id: $MERCHANT_ID" -H "entity-type: $ENTITY_TYPE" --data @subscription-request.json

# Delete a subscription
curl -sS -X DELETE "$JPM_NOTIFICATIONS_API_URL/v1/subscriptions/REPLACE_WITH_SUBSCRIPTION_ID" -H "Authorization: Bearer $JPM_ACCESS_TOKEN" -H "Content-Type: application/json" -H "request-id: $(uuidgen)" -H "merchant-id: $MERCHANT_ID" -H "entity-id: $MERCHANT_ID" -H "entity-type: $ENTITY_TYPE"
```

> In PowerShell, use `Invoke-RestMethod` with a headers hashtable and `[guid]::NewGuid()` for a
> request ID.
