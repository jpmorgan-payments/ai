# Subscriptions, Security Preferences & Testing

## Subscriptions

Create and manage notification subscriptions. Delivery is **WEBHOOK-only**. Refer to the
[Subscribe to notifications](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Foptimization-protection%2Fcapabilities%2Fnotifications%2Fhow-to%2Fsubscribe-to-notifications.md) and
[Security preferences](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Foptimization-protection%2Fcapabilities%2Fnotifications%2Fsecurity-preferences.md) documentation.
Use the [Notifications Bruno collection](https://github.com/jpmorgan-payments/api-collections/tree/main/merchant-services/Notifications)
for subscription requests, headers, payloads, responses, and security-preference examples.

### Subscription workflow

Use the appropriate Bruno request as the starting point. Use `chosen_types` from Phase 1 and collect
only values that cannot be inferred from the merchant's project. For security preferences, ask whether
JPM must authenticate to the merchant's webhook, then select the matching Bruno example.

> **Preview before sending.** Show the configured request with secrets masked as `****` and get
> explicit confirmation before any create, update, or delete operation.

### Confirm & verification lifecycle

After create, the subscription is **not active immediately** — it goes through webhook verification:

1. Status starts `PENDING_VERIFICATION` (no POST/PUT/DELETE allowed while pending).
2. JPM delivers a verification webhook (`type: SubscriptionVerification`, `subtype: WebhookVerification`)
   to your `callbackURL`. Your endpoint **must accept it and return 200 or 201**.
3. On success the status becomes `ACTIVATED` (usually within 2–3 hours); otherwise `FAILED_VERIFICATION`.

Check status using the webhook-verification operation listed in
[api-and-types.md](api-and-types.md). After it activates, use the Bruno collection to retrieve the subscription
and summarize only: subscription ID, active types, callback URL, channel, status. Then suggest testing
(see §Testing & Troubleshooting below).

## Testing, Troubleshooting & Go-Live

Refer to the [Testing](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Foptimization-protection%2Fcapabilities%2Fnotifications%2Ftesting.md) documentation.

## Test the receiver end-to-end

1. Confirm the endpoint is reachable and returns **200 within 5s** (see
   [webhook-handler.md](webhook-handler.md)).
2. Verify signature handling with a real signed sample (see
   [webhook-handler.md §Signature Verification](webhook-handler.md)).
3. In CAT, subscribe with a real `callbackURL` and generate the event that triggers the
   notification type you subscribed to. Remember the callback becomes active after a ~60-minute buffer.
4. If you miss a delivery, use the stored-notification operations in [api-and-types.md](api-and-types.md).

## Delivery failure diagnosis

| Symptom | Likely cause | Action |
| --- | --- | --- |
| Connection refused | Endpoint not running / DNS | Verify the server is up and the URL is public |
| Timeout | Slow handler or firewall | Return 200 fast + process async; open firewall |
| HTTP 4xx | Auth/validation in handler | Check handler logic; 401 only for bad signatures |
| HTTP 5xx | Server error | Check server logs; fix and rely on platform retry |
| No delivery at all | Callback in 60-min buffer, or wrong `callbackURL` | Wait out the buffer; re-check the subscription's `callbackURL` |

## Platform retry schedule (JPM side)

If a webhook isn't delivered successfully, JPM retries automatically:

1. **Initial attempt.**
2. **SQS retries:** 2 more attempts at 15-minute intervals.
3. **Dead-letter (DLQ):** further attempts over the next ~2 days at 24-hour intervals.

Total ≈ 1 initial + 2 SQS + DLQ retries. Design your handler to be idempotent (duplicates will
arrive) and to return 200 quickly so deliveries aren't marked failed.

## Retrieve stored notifications

Use the stored-notification operations in [api-and-types.md](api-and-types.md) to recover
notifications your endpoint missed while it was down. These requests are not in the Bruno collection.

## Go-live checklist

Before pointing a production subscription at your endpoint, verify:

- [ ] Receiver returns 200/201 within 5s under load
- [ ] Signature verification is live (not stubbed)
- [ ] Idempotency store is production-grade (Redis or DB, not in-memory)
- [ ] Dead-letter queue and alerting are wired up
- [ ] Callback URL is publicly reachable over HTTPS with a valid TLS cert
- [ ] Endpoint is registered in all required IaC and security/auth config layers
- [ ] Subscription tested in CAT with real events before promoting to PROD
- [ ] No tokens or secrets committed to source control

## Infrastructure & Network Readiness

Before JPM can deliver notifications to your endpoint, review your infrastructure to ensure inbound HTTPS traffic from JPM can reach your webhook handler. The exact changes depend on your environment setup (on-premise, cloud, hybrid, load balancers, proxies, WAF, etc.). Consider these areas:

- **Inbound connectivity**: Ensure your callback domain accepts inbound HTTPS traffic from the internet. Depending on your setup, this may involve firewall rules, security group settings, network ACLs, or proxy/load-balancer configuration.
- **Domain & DNS**: Your callback domain must resolve correctly and route to your endpoint.
- **TLS/HTTPS**: Your callback URL must use HTTPS with a valid, non-expired TLS certificate.
- **Path routing**: If you have load balancers, reverse proxies, API gateways, or WAF in front of your endpoint, ensure they route the webhook path (e.g., `/webhooks/jpmc`) to your handler without blocking or redirecting traffic.
- **Endpoint verification**: After deployment, JPM will send a verification webhook. If it fails, review connectivity (network, firewall, DNS, proxy settings) and TLS certificate validity.

**Note:** The exact infrastructure changes required are specific to your environment. Work with your infrastructure or DevOps team to review and update your network configuration based on your architecture.
