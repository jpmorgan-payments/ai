# JPM Webhooks Reference

Implementation details for receiving JPM webhook events: subscription management, signing-key fetch, signature verification (EC default, RSA optional), optional mTLS, event catalog, and de-duplication.

## Base host

The Notifications service has its own host — separate from Online Payments, Disputes, and the rest.

| Env | URL | Env var |
|-----|-----|---------|
| CAT | `https://mns-aws-cat.jpmchase.com/v1` | `JPM_NOTIFICATIONS_URL` |
| PROD | `https://mns-aws.jpmchase.com/v1` | `JPM_NOTIFICATIONS_URL` |

Every request needs bearer auth + UUID `request-id` + `merchant-id`. Most subscription endpoints additionally require `entity-type: MERCHANT` and `entity-id: {{merchant-id}}` headers — the API uses these to scope queries.

## Subscription management

Subscriptions describe **what events to deliver where**.

```json
{
  "recipientDetails": {
    "firstName": "...", "lastName": "...",
    "emailAddress": "...",
    "telephoneNumber": "...", "telephoneCountryCode": "+1"
  },
  "notifications": {
    "paymentUpdateNotification": ["All"]
  },
  "callbackURL": "https://your-webhook-endpoint.example.com/callback",
  "subscriptionChannels": ["WEBHOOK"],
  "securityPreferences": {
    "signingAlgorithm": "EC",
    "mTLSEnabled": false
  }
}
```

- `notifications` is a **map** of notification family → list of subscription types. `["All"]` subscribes to every subscription type in that family.
- `subscriptionChannels`: `WEBHOOK` is the relevant value for this skill.
- `securityPreferences.signingAlgorithm`: `EC` (default, P-256 SHA-256) or `RSA` (3072-bit key).
- `securityPreferences.mTLSEnabled`: if `true`, the merchant must share their TLS server certificate with JPM during onboarding so JPM can present a matching client cert.

### Endpoints

- **`POST   {{notif_url}}/subscriptions`** — create a subscription. Returns `subscriptionId`.
- **`GET    {{notif_url}}/subscriptions`** — read.
  - With `subscription-id` header → returns one subscription.
  - Without it → returns all subscriptions for the entity.
- **`PUT    {{notif_url}}/subscriptions/{subscriptionId}`** — update. Partial updates allowed (omit `recipientDetails` if not changing).
- **`DELETE {{notif_url}}/subscriptions/{subscriptionId}`** — remove.

### Sample — create a subscription

```json
POST {{notif_url}}/subscriptions
Headers: entity-type: MERCHANT, entity-id: {{merchant-id}}, request-id: <uuid>, merchant-id: {{merchant-id}}

{
  "recipientDetails": {
    "firstName": "Ops",
    "lastName": "Webhook",
    "emailAddress": "ops@merchant.example.com",
    "telephoneNumber": "800-980-9890",
    "telephoneCountryCode": "+1"
  },
  "notifications": {
    "paymentUpdateNotification": ["All"]
  },
  "callbackURL": "https://merchant.example.com/jpm/webhook",
  "subscriptionChannels": ["WEBHOOK"],
  "securityPreferences": { "signingAlgorithm": "EC", "mTLSEnabled": false }
}
```

## Discover available event types

- **`GET {{notif_url}}/notificationTypes`** — returns the catalog of notification families and subscription types you can subscribe to. Use this to drive a UI or seed your `notifications` map rather than hardcoding.

## Public signing key fetch

- **`GET {{notif_url}}/publicKeys`** — returns the public key used to sign delivered webhook payloads.
- Required header: `signingAlgorithm: EC` (or `RSA` if your subscription is configured for RSA).
- Standard `entity-type` / `entity-id` / `request-id` / `merchant-id` headers also required.

**This endpoint returns a single key, not a JWKS document.** Cache it on startup, and refresh whenever verification fails or when the key referenced in the inbound `Key-ID` header doesn't match your cache. JPM rotates keys on a 365-day cadence per the portal; treat the cache as TTL-bounded, not permanent.

## Health check

- **`GET {{notif_url}}/healthcheck/notification-subscriptions`**

## Signature verification

JPM sends three headers on every webhook POST:

| Header | Meaning |
|---|---|
| `Signature` | Base64-encoded signature over the raw request body |
| `Key-ID` | Identifier of the public key used to sign (use this to look up / refresh your cached key) |
| `Signing-Algorithm` | Algorithm in use — `EC` (P-256 SHA-256) or `RSA` (3072-bit key) |

**Algorithm details (from portal):**
- **EC (default):** verify using `SHA256withECDSA` against the EC P-256 public key.
- **RSA (alternate):** RSA-SHA256, 3072-bit key.

**Pseudo-code:**

```
def verify(request):
    algo          = config.SIGNING_ALGORITHM               # "EC" or "RSA", from YOUR config
    sig_b64       = request.headers["Signature"]
    key_id        = request.headers["Key-ID"]
    raw_body      = request.raw_bytes                      # NOT request.json() — must be raw

    # Cross-check only. Never let the request choose the verifier.
    if request.headers.get("Signing-Algorithm") not in (None, algo):
        return 401

    pubkey        = key_cache.get(key_id) or fetch_and_cache(key_id, algo)

    if algo == "EC":
        ok = ecdsa_sha256_verify(pubkey, raw_body, base64_decode(sig_b64))
    else:
        ok = rsa_sha256_verify(pubkey, raw_body, base64_decode(sig_b64))

    if not ok:
        return 401
    return 200
```

**Critical:** verify against raw bytes. If your framework parses JSON and you re-serialize, whitespace differences break verification.

## De-duplication 

The JPM portal does **not** document a webhook timestamp header or a recommended skew window — do not invent timestamp-based replay rejection. Instead, **de-duplicate by `notificationId`** on the payload body:

- Each delivered event carries a `notificationId` (UUID) in its body.
- Keep a short-TTL store of seen `notificationId`s (Redis with TTL ~24h, or an in-memory LRU for low-volume merchants).
- On receipt, look up the `notificationId`. If present → ack with 200 and stop. If absent → record it, then process.

Retries from JPM after a 2xx-but-slow handler will deliver the same `notificationId` again; this is the only documented mechanism to detect them.

## Optional: mTLS

If `securityPreferences.mTLSEnabled: true` is set on the subscription, JPM presents a client certificate on the TLS handshake to your webhook endpoint. The merchant must:

1. Share their **own** TLS server certificate with JPM during onboarding (so JPM can pin against it).
2. Validate the **JPM-presented** client certificate against JPM's CA chain on inbound requests.

JPM's CA chain for client cert validation is **not published on the portal** — it's provided through the RM / implementation engineer during mTLS setup. Ask the merchant's RM if it's not already in their integration packet. There is a general "J.P. Morgan Public Certificates" page at the portal, but it's not explicitly mapped to Notifications-mTLS; treat that as a fallback only.

## Optional: OAuth-protected webhook

If configured at subscription time, JPM includes an `Authorization: Bearer {token}` header on each delivered event. Validate the token as you would any JPM-issued JWT against JPM's signing key. This is a defense-in-depth layer on top of signature verification, not a replacement for it.

## Event catalog

JPM's event naming convention is **camelCase notification families containing subscription-type subtypes** — *not* dotted strings like `payment.captured`. Reference the actual names below when subscribing or branching in your handler.

| Notification family | Subscription types | Source API |
|---|---|---|
| `paymentUpdateNotification` | `All`, `PaymentApproved`, `PaymentDeclined`, `PaymentErrored`, `PaymentVoid`, `PaymentClosed` | Online Payments |
| `tokenLifecycleNotification` | `All`, `CardDetailsUpdate`, `TokenStateChange`, `TokenProvisionUpdate`, `BulkTokenUpdate` | Tokenization |
| `accountUpdateNotification` | `AccountUpdaterStatus` (plus Pay-by-Bank subtypes `AccountLinkSuccess`, `AccountLinkException`, `MicroDeposit*`) | Account Updater, Pay by Bank |
| `consumerProfileNotification` | `All`, `Created`, `PaymentMethodCreated`, `PaymentMethodDeleted`, `BulkConsumerProfileUpdateNotification` | Consumer Profile Management |
| `entityOnboardingNotification` | (digital onboarding subtypes) | Onboarding |
| `merchantStatusNotification` | (merchant status subtypes) | Onboarding |
| `payoutNotification` | (payout subtypes) | Payouts |
| `recurringProgramNotification` | `PlanUpdated`, `ConsumerCommunicationUpdated`, `PaymentApplied`, `PaymentNotApplied`, `ProgramUpdated` | Recurring billing |

**Not in the catalog:**
- **Disputes does not publish events through this API.** Poll the Disputes endpoints (`POST /disputes`, `POST /disputes/status-query`) instead. Disputes is not covered by `jpm-merchant-integrations` — see the Disputes API docs on the developer portal.
- **3-D Secure is synchronous-only** — no events. The CAVV / ECI comes back in the Perform response (or after the issuer challenge callback).

Per-event payload schemas live in the Notifications OAS on the portal (referenced as `/schemas/paymentUpdateNotification`, `/schemas/tokenLifecycleNotification`, etc.). Fetch and inspect the schema for any family you subscribe to before writing the handler — the field names and nesting differ across families.

## CAT smoke test

1. Register a CAT subscription via `POST /subscriptions` with `callbackURL` pointing at your endpoint (use a tunnel like ngrok if needed for local dev).
2. Fetch the public key: `GET /publicKeys` with `signingAlgorithm: EC` header. Cache it.
3. Trigger a CAT event upstream — for example, run a CAT Online Payments authorization to fire a `paymentUpdateNotification.PaymentApproved`.
4. Confirm: 2xx returned within JPM's timeout, signature verified using the cached key, event handed off to your async queue.
5. Force a verification failure (e.g., flip a byte in your cached key) and confirm you reject with 401.
6. Re-deliver the same event manually (or wait for a JPM retry) and confirm de-duplication by `notificationId` skips processing the second time.
7. If `mTLSEnabled: true`, confirm the JPM client cert validates against the CA chain provided by your RM.

## Common pitfalls

- **Wrong signature header.** It's `Signature` (with companion `Key-ID` and `Signing-Algorithm`). Not `X-Jpm-Signature` or anything custom.
- **Verifying against re-serialized JSON instead of raw bytes** — the #1 cause of failed verifications.
- **Caching the public key indefinitely** — JPM rotates keys on a 365-day cadence and may rotate sooner under incident response. Cache by `Key-ID` and refresh on miss / verification failure.
- **Synchronous downstream processing inside the handler** — causes timeout retries and duplicate deliveries.
- **Inventing timestamp-based replay rejection** — the portal doesn't document a timestamp header. De-dup by `notificationId`.
- **Assuming dotted event names** (`payment.captured`, `dispute.opened`) — JPM uses camelCase families + subscription types. Use the catalog above.
- **Subscribing to dispute events** — they don't exist in this API. Poll the Disputes endpoints.
- **Skipping mTLS validation when configured** — if you set `mTLSEnabled: true` but don't actually validate the JPM-presented cert, you've added complexity without a security benefit.