# Notifications API — Reference

> Authoritative contract lives on PDP. Refer to the [Notifications API documentation](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Foptimization-protection%2Fcapabilities%2Fnotifications%2Foverview.md).
> Use the [Notifications Bruno collection](https://github.com/jpmorgan-payments/api-collections/tree/main/merchant-services/Notifications)
> for supported API requests, headers, payloads, and responses. Confirm base URL and exact shapes
> against the live PDP docs when in doubt.

## Base URL (never hardcode)

Read the base URL (host only) from an environment variable — this is the CAT environment endpoint:

```env
# Notifications API host for CAT (scheme + host, no trailing slash).
JPM_NOTIFICATIONS_API_URL=https://mns-aws-cat.jpmchase.com
```

Resolve request paths from the live PDP documentation or the Notifications Bruno collection. Do not
hardcode a path version in generated code.

## Authentication

Reuse the `getAccessToken()` auth module from `jpm-oauth`. Configure the Bruno collection with the
token and CAT base URL; do not print or persist tokens in generated artifacts.

## Operations Not in the Bruno Collection

The pasted Bruno collection does not include these PDP operations. Refer to the linked PDP pages for
their request and response schemas; do not duplicate those schemas here.

| Operation | Service endpoint | PDP reference |
| --- | --- | --- |
| Retrieve webhook-verification status | `GET /v1/subscriptions/verifications/{requestId}` | [Webhook verification](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Foptimization-protection%2Fcapabilities%2Fnotifications%2Fwebhook-verification.md) |
| Retrieve stored notifications (by ID or filters) | `GET /v1/notifications/{notificationId}` or `GET /v1/notifications` | [Retrieve notifications](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Foptimization-protection%2Fcapabilities%2Fnotifications%2Fhow-to%2Fretrieve-notifications.md) |

### Request Guidance for Uncovered Operations

- **Verification status:** use the `requestId` returned when creating or updating the subscription; a
  subscription remains unavailable for POST, PUT, and DELETE while its verification is pending.
- **Stored notifications:** retrieve by notification ID (from webhook delivery or notification list),
  or filter by `startdate` and `enddate` (`YYYY-MM-DD` format), plus optional `status` (`SENT`,
  `FAILED`, or `PENDING`). Follow `nextPageURL` for pagination. See the linked PDP documentation
  for the complete request and response contract.

---

## Notification Types

Refer to the [Notification types](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Foptimization-protection%2Fcapabilities%2Fnotifications%2Fnotification-types.md)
documentation for the authoritative list of types, sub-types, channel availability, and limited
availability notes. Do not duplicate the notification catalog in this project.

Use the relevant Bruno subscription request after choosing types and sub-types from PDP.
