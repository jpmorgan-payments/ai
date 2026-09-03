---
name: jpm-merchant-integrations
description: Implement J.P. Morgan Payments API integrations in a merchant project once OAuth authentication is in place. Use this skill after a merchant has completed JPM onboarding and wired up authentication (typically right after `jpm-oauth`) and is ready to integrate one of the supported APIs — Checkout, Online Payments, Tokenization, 3-D Secure, or Account Updater. For inbound webhook handling, use the companion `jpm-notifications` skill instead. Recommends implementing one API at a time, reusing the credentials and auth module already wired into the project.
metadata:
  version: 2.0.0
---

# JPM Merchant API Integrations

Guide a merchant through integrating one of the supported J.P. Morgan Payments APIs. Authentication is assumed to be in place — if it isn't, point the user at `jpm-integrations-get-started` (which hands off to `jpm-oauth`) and exit. For inbound webhooks, hand off to `jpm-notifications`.

## Step 1 — Confirm prerequisites

The merchant should already have:
- Validated credentials (clientId, cert path, private key path, SHA-1 thumbprint, resource_id)
- An auth module in their project that exposes a `getAccessToken()` function (or its language equivalent)

If you arrived here from `jpm-oauth`, both are already known — the auth module's path is in conversation context. Use it directly.

If invoked standalone, ask:
- Question: "Is JPM authentication already wired up in this project?"
- Header: "Auth ready?"
- Options:
  - "Yes — I already have a working `getAccessToken()` (or equivalent)"
  - "No — I haven't set up auth yet"

If **No**: tell the user to run `jpm-integrations-get-started` first (it will hand off to `jpm-oauth`), then come back here. Exit.

If **Yes** but the auth module path isn't in conversation context, ask where the module lives so the integration code can import from it.

## Step 2 — Pick one API to integrate

It is recommended to implement **one API at a time**. Each has its own request shapes, error semantics, and test scenarios.

Ask:
- Question: "Which API would you like to integrate first?"
- Header: "API"
- Options:
  - "Checkout" — drop-in payment UI you embed in your checkout page. Fastest to ship when you don't need a fully custom UI.
  - "Online Payments" — direct REST processing for card, wallet, and alternative payment methods. Use when you want full control over the UI and flow.
  - "Tokenization" — swap card numbers for JPM-issued tokens to reduce PCI scope. Online (per-card) and bulk (MFTS file) modes.
  - "3-D Secure" — standalone cardholder authentication for liability shift, decoupled from authorization.
  - "Account Updater" — keep stored cards current as issuers reissue them. Inquiry mode (sync) or card-registration mode (async via webhooks).

**If the merchant chose Account Updater, ask the mode question first — before the free-text description below.** Account Updater's two modes have different prerequisites and integration shapes, so the mode must be pinned down up front:
- Question: "Which Account Updater mode do you want to integrate?"
- Header: "AU mode"
- Options:
  - "Card-registration mode — async: register cards, receive `accountUpdateNotification` webhooks, then GET the updated details"
  - "Inquiry mode — sync: submit a card, get its latest known state back"

Carry the chosen mode into the description prompt and Step 3. Only after the mode is selected, ask the free-text description below.

Once chosen, ask the user (free text):

> "Briefly describe what you're building or migrating — e.g. 'a simple checkout page for a single product', 'migrating from Stripe Elements'. A sentence or two is enough."

Carry this description into Step 3 so the implementation, file structure, and code comments are tailored to the merchant's actual use case rather than a generic reference build.

**3-D Secure flow — ask only if the chosen API is Online Payments and the integration involves 3-D Secure** (the user mentioned 3DS, SCA / PSD2, or cardholder authentication / liability shift, or their description implies it). Skip it for Checkout (the Checkout platform performs 3DS automatically) and for Online Payments integrations that don't use 3DS. When 3DS is in scope, the merchant must pick how it's performed:

- Question: "How should 3-D Secure cardholder authentication be performed?"
- Header: "3DS flow"
- Options:
  - "Orchestrated" — JPM runs the full 3DS authentication inline as part of the Online Payments authorization (you send `browserInfo` + `paymentAuthenticationRequest`; JPM handles the challenge round-trip). Least integration work.
  - "Passthrough" — you authenticate 3DS externally (your own MPI or another provider) and pass the resulting cryptogram (CAVV / ECI / DS transaction ID) into the payment's `authentication.threeDS` block, where the DS transaction ID maps to `authenticationTransactionId`.
  - "API (standalone)" — you call JPM's standalone 3DS API to authenticate as a separate step, then feed the resulting cryptogram into the Online Payments authorization.

Remember the answer as `threeDSFlow` and carry it into Step 3. Orchestrated and Passthrough are documented in `references/online-payments.md` (the "Auth-Capture with Orchestrated 3DS" and "Auth-Capture with Passthrough 3DS" sections); API (standalone) is documented in `references/3d-secure.md`.

> **Special note if `threeDSFlow` is "Passthrough":** Passthrough does **not** perform any 3DS authentication itself — it only forwards a cryptogram (CAVV / ECI / DS transaction ID) that must already exist. Make this explicit to the user and establish which situation they're in **before** generating code:
>
> - **They already have external 3DS in place** (their own MPI or a third-party provider) → the integration just **connects** to it: wire the existing cryptogram source into the payment's `threeDS` block. Ask where those values come from so you can plug them in.
> - **They do not have external 3DS yet** → still generate the **complete** Online Payments (`/payments`) integration, but expose the authentication as an **unimplemented seam the merchant fills in later**. Concretely: emit a single authentication function (e.g. `authenticate(context): ThreeDSResult`) that the payment flow calls to obtain the cryptogram, and leave its body **unimplemented so it throws** a clear "3DS not implemented — integrate your MPI here" error. The rest of the integration (request shape, `threeDS` field mapping, validation, auth/proxy wiring) is fully built and compiles, so the app runs end-to-end up to the point of payment and then stops at that seam. Tell the user the payment side is done and they complete it by implementing that one function (or switching to "Orchestrated"/"API (standalone)", where JPM performs the authentication).

Once chosen, read the corresponding reference file from this skill's directory:

- Checkout → `references/checkout.md` (also consult `examples/checkout-sample-app.md` if the merchant wants a complete reference build)
- Online Payments → `references/online-payments.md` (if `threeDSFlow` is "API (standalone)", also read `references/3d-secure.md`)
- Tokenization → `references/tokenization.md`
- 3-D Secure → `references/3d-secure.md`
- Account Updater → `references/account-updater.md`

If the user asks for an API not listed above (Wallet Decryptions, Disputes, Consumer Profile Management, Reporting, In-Store Payments, Pay by Bank, Push to Card, Global Payments, Wire, US RTP, Embedded, Verifications, etc.), tell them this skill doesn't yet cover that API and offer one of the supported APIs instead. Don't try to invent the integration from scratch.

## Step 3 — Implement the chosen API

Follow the steps in the chosen reference file. If you captured a `threeDSFlow` in Step 2 (Online Payments + 3DS), implement that flow only — Orchestrated or Passthrough per the matching "Auth-Capture with … 3DS" section of `online-payments.md`, or standalone per `3d-secure.md` — rather than building all three. Cross-cutting principles that apply to all supported APIs:

- **Reuse the existing auth module.** Every JPM API call needs `Authorization: Bearer <access_token>` from the merchant's `getAccessToken()`. Import that function — do not re-implement token fetching inside the integration code. The auth module already caches correctly; bypassing it is exactly the per-call-token anti-pattern `jpm-oauth` warned against.
- **Use environment-aware base URLs.** Base URLs differ between CAT and PROD and sometimes between sub-services within an environment. Read them from env vars (e.g. `JPM_CHECKOUT_API_URL`, `JPM_ONLINE_API_URL`, `JPM_TOKENIZATION_URL`, `JPM_3DS_URL`, `JPM_ACCOUNT_UPDATER_URL`) rather than hardcoding. The reference file for each API lists the URLs that apply.
- **Confirm output paths before writing.** Default to a sibling folder of the auth module (`src/checkout/`, `src/payments/`, etc.) but offer "new top-level folder" and "custom path" alternatives, the same way `jpm-oauth` did.
- **Smoke test in CAT before PROD.** Each reference includes a minimal end-to-end test recipe — run it with the merchant's CAT credentials before any PROD config change.
- **Hand off to `jpm-notifications` for inbound webhooks.** Several of these APIs deliver state changes via the JPM Notifications API — Online Payments (`paymentUpdateNotification`), Tokenization (`tokenLifecycleNotification`), Account Updater registration mode (`accountUpdateNotification`). Don't try to build the receiver inside this skill's code — point the merchant at `jpm-notifications` so signature verification, key rotation, and mTLS are done correctly in one place. **For Account Updater registration mode, the webhook is only step 1 of 3:** the notification payload is masked, so after receiving it the merchant must call the Account Updater `GET /account-updates/{requestId}` endpoint to retrieve the actual updated card details. Wiring only the notification (and skipping the GET) leaves the flow incomplete. 3-D Secure is synchronous-only and has no webhook events either.
- **Passthrough 3DS is connect-only, not authenticate.** If `threeDSFlow` is "Passthrough", the code you generate consumes a pre-existing cryptogram; it does not authenticate the cardholder. Confirm the merchant either already has external 3DS to connect to, or understands they must implement that upstream 3DS logic themselves — see the "Special note" in Step 2.

## Step 4 — Offer to add another

Once the chosen API is implemented and the user confirms it's working in CAT:

Ask:
- Question: "That integration looks good. Want to add another JPM API now?"
- Header: "More?"
- Options:
  - "Yes — pick another"
  - "No — I'm done for now"

If **Yes**, return to Step 2 (the user picks a different API; skip Step 1, prerequisites are still satisfied).

If **No**, exit with a one-line summary of which APIs were integrated this session.

## Rules

- Do not re-implement OAuth inside the integration code. The merchant's auth module already handles token fetching with caching. Re-implementing it inline is what JPM's "don't generate tokens per call" guidance warns against.
- Confirm every output file path with the user before writing.
- Only the APIs listed in Step 2 are supported by this skill. For anything else (Reporting, In-Store, Pay by Bank, etc.), defer politely and offer a supported API instead. For inbound webhooks, hand off to `jpm-notifications`.
- Don't write CAT credentials into PROD config or vice versa. The auth module reads from env vars, so the merchant flips environments by switching `.env` files — never by editing source.
