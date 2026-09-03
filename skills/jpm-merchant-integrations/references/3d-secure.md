# 3-D Secure (Standalone)

3-D Secure (3DS) shifts liability for fraudulent CNP card transactions from the merchant to the issuer by authenticating the cardholder with their bank during checkout. This reference covers **standalone 3DS** — invoking authentication separately from the payment authorization, so a merchant can use the resulting cryptogram with the existing Online Payments flow (or another acquirer).

## Read the documentation first

The J.P. Morgan Payments Developer Portal is the **authoritative source** for 3DS request/response schemas, field enums, and flow behavior. Fetch these before implementing; the rest of this file is integration guidance layered on top of them, and defers to the docs on any conflict.

##### 3-D Secure

- [3-D Secure](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Foptimization-protection%2Fcapabilities%2F3-d-secure%2F3-d-secure.md) Use our 3-D Secure (3DS) API to reduce payment risk and provide control over the cardholder authentication process. Ideal for regions with 3DS mandates.

###### How To

- [Request a 3-D Secure (3DS) authentication](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Foptimization-protection%2Fcapabilities%2F3-d-secure%2Fhow-to%2Fprocess-a-standalone-authentication.md) Review the 3DS authentication process: initiate, collect browser data, and handle issuer challenges to enhance security and streamline payments with our 3-D Secure API.

## When to use

Use this when:

- You're processing CNP card payments in regions with SCA / PSD2-style mandates.
- You want issuer liability shift on cross-border or high-risk transactions.
- You want 3DS *decoupled* from payment authorization (e.g., authenticate at order placement, capture later).

If 3DS is invoked inline as part of an Online Payments authorization, see `online-payments.md` instead — there's a `threeDS` field on the payment request that bundles both calls.

## Prerequisites

- Auth module + `getAccessToken()` already wired (see `../SKILL.md` Step 1).
- Card details available at the moment of authentication. The **PAN and expiry are required** — they identify the card to the directory server, and the Prepare sample below sends both. **CVV is not** part of 3DS; it belongs to the subsequent authorization, not the authentication. The cardholder browser context is required as well (see "The two browser round-trips").
- Frontend able to host the issuer's challenge UI (iframe / redirect) when a step-up is required.

## Base URLs

| Env | URL | Env var |
|-----|-----|---------|
| CAT | `https://api-ms-test.payments.jpmorgan.com/api/v2` | `JPM_3DS_URL` |
| PROD | `https://api-ms.payments.jpmorgan.com/api/v2` | `JPM_3DS_URL` |

3DS shares the host root with Online Payments and Account Updater (Optimization & Protection family). The path prefix is `/authentications`.

**No webhook events.** 3DS is a synchronous request/response API — the cryptogram comes back in the Perform response (or after the issuer challenge callback). Do not look for 3DS events in `jpm-notifications`; none are published.

## Core endpoints

- **`POST {{3ds_url}}/authentications`** — *Prepare*: submit card + amount + addresses → returns `authenticationId` + `transactionId`.
- **`POST {{3ds_url}}/authentications/{authenticationId}`** — *Perform*: submit full risk / browser / account context → returns the 3DS result (frictionless cryptogram, or a challenge to render in the browser). Omit `threeDSRequestorAuthenticationInfo.threeDSChallengeType` and let the issuer decide; only set it deliberately (`"CHALLENGE_REQUESTED"` forces step-up, `"NO_CHALLENGE"` requests frictionless and should not be a default).
- **`GET  {{3ds_url}}/authentications/{authenticationId}`** — *Results*: read the final authentication outcome after a challenge completes. Response carries `authenticationResult.threeDomainSecureCompletion.threeDSAuthenticationValue` (CAVV) and `.electronicCommerceIndicator` (ECI) — the values you ultimately pass to Online Payments authorization. For a frictionless result these already come back on the Perform response; the GET is how you retrieve them once a challenge round-trip has finished.
- **`GET  {{3ds_url}}/authentications/healthcheck`** — Health probe only. Returns service liveness; it does **not** carry a cryptogram.

All requests need bearer auth, a UUID `request-id` header, and a `merchant-id` header.

## Sample requests

### Prepare — `POST {{3ds_url}}/authentications`

```json
{
  "authenticationPaymentMethodType": {
    "card": {
      "accountNumber": "5424184049821670",
      "expiry": { "month": 5, "year": 2027 }
    }
  },
  "amount": 54500,
  "currency": "EUR",
  "authenticationAccount": {
    "email": "shopper@example.com",
    "firstName": "Jane", "lastName": "Doe",
    "phone": { "countryCode": 1, "phoneNumber": "8137221122" },
    "billingAddress": { "line1": "...", "city": "Clearwater", "state": "FL", "postalCode": "33607", "countryCode": "USA" }
  },
  "shippingAddress": { "line1": "...", "city": "...", "state": "FL", "postalCode": "33607", "countryCode": "USA" },
  "threeDSMethodMerchantNotificationUrl": "https://merchant.example.com/3ds-method-callback",
  "authenticationType": "AUTHENTICATION"
}
```

Response captures: `transactionId`, `authenticationId` (treat as the case ID for the Perform call).

### Perform — `POST {{3ds_url}}/authentications/{authenticationId}`

Trimmed shape (full body has ~30 sub-objects covering account, prior auth, purchase risk, browser, addresses, message extensions):

```json
{
  "accountType": "CREDIT",
  "channelType": "BROWSER",
  "messageType": "PAYMENT_AUTHENTICATION",
  "threeDSChallengeMerchantNotificationUrl": "https://merchant.example.com/3ds-challenge-callback",
  "authenticationSupportUrl": "https://merchant.example.com/3ds-support",
  "threeDSRequestorAuthenticationInfo": {
    "threeDSAuthenticationTimestamp": "2023-08-21T15:12:12Z",
    "requestorAuthenticationMethod": "REQUESTOR_CRED",
    "authenticationPurpose": "PAYMENT_TRANSACTION"
  },
  "threeDSPurchaseInfo": {
    "purchaseDate": "2023-08-21T15:12:12Z",
    "threeDomainSecureTransactionType": "CHECK"
  },
  "browserInfo": {
    "deviceIPAddress": "192.168.1.11",
    "browserLanguage": "en",
    "browserUserAgent": "Mozilla/5.0 ...",
    "javaScriptEnabled": true
  },
  "authenticationAccount": { "...same shape as Prepare..." },
  "shippingAddress": { "...same shape as Prepare..." }
}
```

**Let the issuer decide.** Omit `threeDSRequestorAuthenticationInfo.threeDSChallengeType` (as above) so the issuer's ACS chooses frictionless or challenge from the risk signals — this is the correct default for SCA. Only set it deliberately: `"CHALLENGE_REQUESTED"` forces a step-up, `"NO_CHALLENGE"` *requests* frictionless. Do **not** hard-code `"NO_CHALLENGE"` as a default: it silently asks the issuer to skip authentication and defeats the purpose of running 3DS. The issuer can override either hint (e.g. PSD2 mandates), so your app must handle both outcomes regardless of what it requested.

## Reference flow

Follow [Request a 3-D Secure (3DS) authentication](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Foptimization-protection%2Fcapabilities%2F3-d-secure%2Fhow-to%2Fprocess-a-standalone-authentication.md) for the authoritative step-by-step walkthrough (initiate, collect browser data, handle issuer challenges). At a glance it is: **Prepare** → **3DS Method** (browser) → **Perform** → (optional issuer **challenge** in the browser) → **GET results** → pass the cryptogram to authorization.

**3DS is not a pure server-to-server flow.** Two of the steps run in the cardholder's browser via hidden/visible iframes, and the ACS reports their completion back to your server through notification callbacks. A backend-only Prepare→Perform loop will *not* produce a valid cryptogram for a real SCA transaction — it only ever yields the frictionless subset and typically stalls on `425 / DATA_COLLECTION_IN_PROGRESS` because the 3DS Method never ran. You must implement the browser round-trip below.

### The two browser round-trips

Both are the same pattern: your server hands the frontend a target URL + a payload, the frontend auto-submits a `POST` form inside an iframe (same-origin `srcDoc`, posting cross-origin to the ACS), and the ACS redirects the iframe to *your* notification URL when done. That callback page runs `window.parent.postMessage(...)` so the SPA knows the step finished, then the flow continues.

1. **3DS Method (hidden, device-data collection).** In the **Prepare** request send `threeDSMethodMerchantNotificationUrl`. If the Prepare response contains `authenticationResult.threeDomainSecureCreation.threeDSMethodUrl` + `.threeDSMethodDataForm`, post them from a hidden iframe:

   ```html
   <!-- form action = threeDSMethodUrl -->
   <input type="hidden" name="threeDSMethodData" value="{threeDSMethodDataForm}">
   ```

   The ACS finishes (≤10s), redirects the iframe to your `threeDSMethodMerchantNotificationUrl`; that page `postMessage`s the SPA, which then calls **Perform**. If the Prepare response omits the method fields, skip straight to Perform.

2. **Challenge (visible, cardholder step-up).** In the **Perform** request send `threeDSChallengeMerchantNotificationUrl`. If the Perform response has `authenticationResult.threeDomainSecureChallenge.threeDSTransactionStatus === "C"`, post the challenge into a **visible** iframe the cardholder interacts with:

   ```html
   <!-- form action = authenticationResult.threeDomainSecureChallenge.threeDSAcsUrl -->
   <input type="hidden" name="creq" value="{threeDomainSecureChallenge.threeDSChallengeRequest}">
   ```

   When the cardholder finishes, the ACS redirects the iframe to your `threeDSChallengeMerchantNotificationUrl`; that page `postMessage`s the SPA, which then calls **GET results** (`GET /authentications/{authenticationId}`) to read the final CAVV/ECI. A frictionless Perform (no `"C"` status) already carries the cryptogram — no challenge iframe needed.

The notification URLs must be **absolute and browser-reachable**, and ideally same-origin with the SPA so the `postMessage` back to `window.parent` is trivial (e.g. serve the SPA and proxy `/api` to the backend from one origin).

### Securing the `postMessage` bridge

The ACS controls where the iframe navigates, so the SPA's `message` listener is reachable by any
page the ACS (or anything else) can load into a frame. Treat it as an untrusted input channel:

- **Send with an explicit target origin — never `"*"`.** On the callback page:
  ```js
  window.parent.postMessage({ type: "3ds-method-complete" }, "https://your-spa.example.com");
  ```
  Use a build-time constant for the SPA origin. `"*"` broadcasts to whatever ended up as the parent.
- **Check `event.origin` in the listener, before anything else.** An unchecked listener lets any
  framed page forge a "challenge complete" message and advance your checkout:
  ```js
  window.addEventListener("message", (event) => {
    if (event.origin !== "https://your-spa.example.com") return;   // reject, don't process
    if (event.source !== iframeEl.contentWindow) return;           // must be the iframe you opened
    // ...then handle event.data
  });
  ```
- **Carry no trust in the message payload.** The message is a *signal that a step finished*, not
  evidence that it succeeded. Never read a CAVV, ECI, or status out of `event.data` — always
  re-confirm server-side with `GET /authentications/{authenticationId}` and gate the authorization
  on what that returns.
- **Remove the listener once the flow resolves**, so a late or repeated message can't re-enter it.

### Session state across the steps

Prepare, Perform, and complete are **separate HTTP requests**, but the card + amount + account details captured at Prepare must survive until the final authorization. Hold them in server-side session state **keyed by `authenticationId`** (the value Prepare returns), and enforce it at complete time: look up the pending order, verify the GET-results CAVV is present, *then* authorize — never process the payment if authentication did not complete. Delete the session entry once the payment resolves. A single-process dev build can use an in-memory `Map`; production needs a real server-side session/cache with a short TTL (card data is transient and must not leak between shoppers).

The one step the doc does not cover, because it belongs to the payment API: feed the resulting CAVV (`authenticationResult.threeDomainSecureCompletion.threeDSAuthenticationValue`), ECI (`.electronicCommerceIndicator`), and the DS transaction ID into the Online Payments `authentication.threeDS` block — see `online-payments.md`. Note the field names differ across the two APIs: the DS transaction ID is sent to Online Payments as **`authenticationTransactionId`**, and the CAVV as `authenticationValue`.

## CAT smoke test

JPM's canonical test-card list is published at the Online Payments testing page on developer.payments.jpmorgan.com. **Outcomes are amount-driven, not PAN-driven** for most scenarios — a single test card can produce different 3DS results depending on the request amount. Cross-reference the Online Payments testing page for the current matrix.

Minimum smoke test:

- One request that returns **frictionless** (cryptogram on the Perform response, no challenge iframe).
- One request that returns a **challenge** → the visible ACS iframe renders, the cardholder completes it, the challenge callback fires, and GET results returns the CAVV.
- One request that returns a failed/declined authentication (and confirm the payment is **not** processed).

Then pass the resulting CAVV + ECI into an Online Payments authorization in CAT and confirm acceptance.

## Common pitfalls

- Implementing 3DS as a pure backend Prepare→Perform loop — it skips the browser 3DS Method + challenge iframes, so it stalls on `425 / DATA_COLLECTION_IN_PROGRESS` and never authenticates a real challenge. Run the browser round-trip.
- Hard-coding `threeDSChallengeType: "NO_CHALLENGE"` — silently defeats SCA. Omit it and let the issuer decide.
- Reading the cryptogram from `GET /authentications/healthcheck` — that's only a liveness probe. Use `GET /authentications/{authenticationId}`.
- Processing the payment when authentication did not complete — gate authorization on a present CAVV.
- Sending CAT cryptograms to PROD authorization (will fail with "invalid cryptogram"). Confirm both calls hit the same environment.
- Forgetting browser fingerprint fields → issuer downgrades to challenge unnecessarily.
- **`postMessage(..., "*")` or a listener with no `event.origin` check** — the ACS controls the iframe, so an unchecked bridge lets a framed page forge "authentication complete". Pin the target origin, verify `event.origin` and `event.source`, and confirm the outcome server-side.
- **Trusting the CAVV/ECI out of `event.data`** — the browser message is a completion signal only. Read the cryptogram from `GET /authentications/{authenticationId}` on the server.
