# Account Updater

> **Scaffold — endpoint details are placeholders.** Fill from `https://developer.payments.jpmorgan.com/` (Account Updater) before using in production.

## Overview

Account Updater keeps stored card credentials current as issuers reissue, replace, or close cards. It returns updated PAN / expiry information so that recurring charges, subscriptions, and stored-credential MIT transactions don't fail on a stale card.

Use this when:
- You store cards on file for recurring billing or one-click checkout.
- You're seeing avoidable `expired_card` or `invalid_card_number` declines on returning customers.
- You need to align stored credentials with the latest network state (Visa AU / Mastercard ABU).

## Modes

Two integration shapes:
- **Inquiry mode** — synchronous: pass a card, get the latest known state back.
- **Card-registration mode** — async: register cards once, then receive `card.updated` webhook events as issuers push changes. **The webhook payload carries only *masked* card data** — to obtain the updated card details you must call the GET endpoint after each notification. This mode therefore requires **both** `jpm-notifications` (to receive events) **and** the Account Updater GET endpoint (to retrieve the full result). Wire up `jpm-notifications` first.

## Prerequisites

- Auth module + `getAccessToken()` already wired (see `../SKILL.md` Step 1).
- A secure store for cards on file (PCI scope — use Tokenization if you can to avoid storing PANs directly; see `tokenization.md`).
- **For card-registration mode only:** `jpm-notifications` skill applied, with a webhook endpoint hosted and signature verification working. You will also integrate the Account Updater **GET** endpoint — the notification payload is masked, so the GET call is how you retrieve the actual updated card details.

## Base URLs

| Env | URL | Env var |
|-----|-----|---------|
| CAT | `https://api-ms-test.payments.jpmorgan.com/api/v1` | `JPM_ACCOUNT_UPDATER_URL` |
| PROD | `https://api-ms.payments.jpmorgan.com/api/v1` | `JPM_ACCOUNT_UPDATER_URL` |

Account Updater shares the host root with Online Payments / 3DS / Wallet Decryptions (Optimization & Protection family), but lives at the `v1` path prefix where they use `v2`. Use a dedicated env var so a future host split doesn't require a code change.

## Core endpoints

All three card networks (Visa, Mastercard, Discover) share the same endpoint shape — the API routes by BIN, not by network in the URL.

- **`POST {{accountupdater_url}}/account-updates`** — submit one card. Body shape differs by intent:
  - **One-time inquiry** — omit `cardAccountAction`. Returns current network state without registering for ongoing updates.
  - **Register** — set `cardAccountAction: "REGISTER"` and include `merchantRecordIdentifier`. Subscribes the card for ongoing updates (delivered via `jpm-notifications`).
  - **Unregister** — set `cardAccountAction: "UNREGISTER"`.
- **`GET  {{accountupdater_url}}/account-updates/{requestId}`** — retrieve the result/status of a prior submission. The `requestId` comes from the response of the original POST.
- **`GET  {{accountupdater_url}}/healthcheck/account-updates`** — service health probe.

For card-registration mode, async updates arrive via the Notifications API under the `accountUpdateNotification` family (subscription type `AccountUpdaterStatus`). See `jpm-notifications` for wiring up the webhook receiver. **The notification payload only contains masked card information** — it signals *that* an update occurred but not the full updated PAN/expiry. To read the actual updated card details, call `GET /account-updates/{requestId}` after receiving the notification.

Response capture pattern: every POST returns `requestId` + `responseId`. Save both — `requestId` is the lookup key for the GET call. In registration mode, persist `requestId` against your card-on-file record so you can call the GET endpoint when the matching `accountUpdateNotification` arrives.

## Sample requests
### Register a Visa card

```json
POST {{accountupdater_url}}/account-updates
{
  "accountInformation": {
    "cardNumber": "4111111111111111",
    "expiry": { "month": 9, "year": 2032 }
  },
  "cardAccountAction": "REGISTER",
  "merchantRecordIdentifier": "<your-stable-card-record-id>"
}
```

### Unregister (Visa)

```json
POST {{accountupdater_url}}/account-updates
{
  "accountInformation": {
    "cardNumber": "4111111111111119",
    "expiry": { "month": 9, "year": 2032 }
  },
  "cardAccountAction": "UNREGISTER"
}
```

### One-time inquiry (Discover) — note: no `cardAccountAction` field

```json
POST {{accountupdater_url}}/account-updates
{
  "accountInformation": {
    "cardNumber": "6011111111111111",
    "expiry": { "month": 8, "year": 2026 }
  }
}
```

### Retrieve result by request ID

```
GET {{accountupdater_url}}/account-updates/{requestId}
```

No body. The `{requestId}` was returned by the original POST.

### Test card BINs by network

| Network | Card prefix | Example test card |
|---------|-------------|-------------------|
| Visa | 4xxx | `4111111111111111` |
| Mastercard | 5xxx | `5111111111111113` |
| Discover | 6xxx | `6011111111111111` |

## Reference flow

### One-time inquiry mode (sync)
1. Run on a schedule (daily batch) against cards-on-file.
2. For each card, POST to `/account-updates` **without** `cardAccountAction`.
3. Capture `requestId` from the response.
4. Optionally GET `/account-updates/{requestId}` to retrieve a richer view of the result.
5. Update your store on `match-update`; mark dead on `match-closed`.

### Card-registration mode (async)

Registration mode has **three integration points** — all three are required for the flow to work end to end:

**Step 1 — Subscribe to Account Updater events (Notifications API).** Wire up `jpm-notifications` so your webhook endpoint receives `accountUpdateNotification` events (subscription type `AccountUpdaterStatus`). This is the async delivery channel for issuer-pushed changes.

**Step 2 — Register cards (POST endpoint).** On card-on-file creation, POST to `/account-updates` with `cardAccountAction: "REGISTER"` and a stable `merchantRecordIdentifier` so you can correlate webhook events back to your customer. Persist the returned `requestId` against that card record. On card removal, POST again with `cardAccountAction: "UNREGISTER"`.

**Step 3 — Retrieve updated card details (GET endpoint).** When an `accountUpdateNotification` arrives, **it carries only masked card information** — it tells you *an update happened* but not the new PAN/expiry. Call `GET /account-updates/{requestId}` (using the `requestId` you persisted in Step 2, or the one referenced in the notification) to fetch the full updated card details, then update your card-on-file store. **Skipping this step means you never actually receive the updated card data — the notification alone is not enough.**

## CAT smoke test

Test cards above (Visa `4111111111111111`, Mastercard `5111111111111113`, Discover `6011111111111111`) are the BIN-level smoke set. JPM's portal publishes additional scenario cards under the Account Updater testing page — cross-reference for cards that deterministically return `match-update`, `match-closed`, `contact-cardholder`, and `no-match`.

For registration mode, exercise all three steps in CAT before flipping PROD: (1) confirm your webhook endpoint is subscribed and reachable, (2) register a CAT card via `POST /account-updates` with `cardAccountAction: "REGISTER"` and confirm the corresponding `accountUpdateNotification` lands on your CAT webhook endpoint, then (3) call `GET /account-updates/{requestId}` and confirm you get back the full (unmasked) updated card details — not just the masked payload from the notification.

## Common pitfalls

- Treating `no-match` as "card is fine" — it just means no update was pushed this cycle. Don't reset the card's "last verified" timestamp on `no-match`.
- Running inquiry mode too frequently — networks rate-limit and may charge per inquiry. Daily batches are usually enough.
- Forgetting to wire `jpm-notifications` before registration mode → events silently dropped.
- **Treating the notification payload as the source of updated card data.** It's masked — it only signals that an update occurred. You must call `GET /account-updates/{requestId}` to retrieve the actual updated PAN/expiry. Registration mode without the GET step is incomplete.
- Not persisting `requestId` at registration time → no lookup key to call the GET endpoint when the notification arrives.
