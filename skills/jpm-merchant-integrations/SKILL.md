---
name: jpm-merchant-integrations
description: Implement J.P. Morgan Payments API integrations in a merchant project once OAuth authentication is in place. Use this skill after a merchant has completed JPM onboarding and wired up authentication (typically right after `jpm-oauth`) and is ready to integrate one of the two currently-supported APIs — Checkout (drop-in payment UI) or Online Payments (direct card / wallet / APM processing). Recommends implementing one API at a time, reusing the credentials and auth module already wired into the project.
metadata:
  version: 2.0.0
---

# JPM Merchant API Integrations

Guide a merchant through integrating one of the two supported J.P. Morgan Payments APIs (Checkout and Online Payments). Authentication is assumed to be in place — if it isn't, point the user at `jpm-integrations-get-started` (which hands off to `jpm-oauth`) and exit.

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

JPM's guidance — and ours — is to implement **one API at a time**. Each has its own request shapes, error semantics, and test scenarios. Bundling both into one change set makes it harder to isolate failures, slows down PR review, and tends to delay shipping either of them. Better path: ship Checkout, prove it in CAT, then open a separate change for Online Payments.

Ask:
- Question: "Which API would you like to integrate first?"
- Header: "API"
- Options:
  - "Checkout — drop-in payment UI" — pre-built UI you embed in your checkout page; styling via Commerce Center or JS. Fastest to ship if you don't need a fully custom UI.
  - "Online Payments — direct API processing" — card, wallet, local, and alternative payment methods via direct REST calls. Use when you want full control over the UI and flow.

Once chosen, ask the user (free text):

> "Briefly describe what you're building or migrating — e.g. 'a simple checkout page for a single product', 'migrating from Stripe Elements'. A sentence or two is enough."

Carry this description into Step 3 so the implementation, file structure, and code comments are tailored to the merchant's actual use case rather than a generic reference build.

Once chosen, read the corresponding reference file from this skill's directory:

- Checkout → `references/checkout.md` (also consult `examples/checkout-sample-app.md` if the merchant wants a complete reference build)
- Online Payments → `references/online-payments.md`

If the user asks for a different API (Tokenization, Reporting, In-Store Payments, Pay by Bank, Push to Card, Global Payments, Wire, US RTP, Embedded, 3-D Secure, Consumer Profile, Notifications, etc.), tell them this skill doesn't yet cover that API in the initial release and offer to integrate Checkout or Online Payments instead. Don't try to invent the integration from scratch.

## Step 3 — Implement the chosen API

Follow the steps in the chosen reference file. Cross-cutting principles that apply to all four:

- **Reuse the existing auth module.** Every JPM API call needs `Authorization: Bearer <access_token>` from the merchant's `getAccessToken()`. Import that function — do not re-implement token fetching inside the integration code. The auth module already caches correctly; bypassing it is exactly the per-call-token anti-pattern `jpm-oauth` warned against.
- **Use environment-aware base URLs.** Base URLs differ between CAT and PROD and sometimes between sub-services within an environment. Read them from env vars (e.g. `JPM_CHECKOUT_URL`, `JPM_ONLINE_URL`) rather than hardcoding. The reference file for each API lists the URLs that apply.
- **Confirm output paths before writing.** Default to a sibling folder of the auth module (`src/checkout/`, `src/payments/`, etc.) but offer "new top-level folder" and "custom path" alternatives, the same way `jpm-oauth` did.
- **Smoke test in CAT before PROD.** Each reference includes a minimal end-to-end test recipe — run it with the merchant's CAT credentials before any PROD config change.

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
- Only the two APIs listed in Step 2 (Checkout and Online Payments) are supported in the initial release. For anything else, defer politely and offer one of the two instead.
- Don't write CAT credentials into PROD config or vice versa. The auth module reads from env vars, so the merchant flips environments by switching `.env` files — never by editing source.
