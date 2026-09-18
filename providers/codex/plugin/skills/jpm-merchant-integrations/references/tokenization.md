# Tokenization

> **Scaffold — endpoint details are placeholders.** Fill from `https://developer.payments.jpmorgan.com/` (Tokenization) before using in production.

## Overview

Tokenization swaps a card PAN for a merchant-scoped token. The token can be used in subsequent Online Payments calls in place of the PAN — reducing PCI scope and letting the merchant store the token instead of card data.

Use this when:
- You want to reduce PCI scope (CDE shrinkage from SAQ-D to SAQ-A-EP territory).
- You don't need the broader profile model from Consumer Profile Management — just card → token.
- You're migrating an existing card vault and need bulk tokenization, not just one-at-a-time API calls.

## Modes

- **Online (API)** — one-at-a-time card→token swap via REST. Fits checkout flows.
- **Bulk (MFTS)** — file-based: upload an encrypted card file via Managed File Transfer Services, receive a token file back. Fits migrations and large batch jobs. **Requires bulk encryption keys and an MFTS account in addition to OAuth.**

## Prerequisites

- Auth module + `getAccessToken()` already wired (see `../SKILL.md` Step 1).
- For online mode: nothing else.
- **For bulk mode:** MFTS file transfer account, bulk encryption keys provisioned by JPM, and a secure environment to encrypt the card file before upload.

## Base URLs

| Env | URL | Env var |
|-----|-----|---------|
| CAT | `https://api-tokens-cat.payments.jpmorgan.com` | `JPM_TOKENIZATION_URL` |
| PROD | `https://api.merchant.jpmorgan.com/payments/v1` | `JPM_TOKENIZATION_URL` |

The portal also documents `https://api-test.merchant.jpmorgan.com/payments/v1` as a CAT/test host — likely a tenant-specific or alternate stack. Use whichever the merchant's RM directs them to; default to the value above.

MFTS hostnames (for bulk mode) are **not published on the portal** — they're provisioned per-merchant by the relationship manager during MFTS onboarding. See the bulk mode section below.

Async events for tokens (state changes, card details updates, bulk-update completions) arrive via the Notifications API under the `tokenLifecycleNotification` family — see `jpm-notifications`.

## Core endpoints

Bearer auth + UUID `request-id` + `merchant-id` headers across all endpoints.

### Token creation — two distinct flows

- **`POST {{token_url}}/tokens`** — *Network token* creation. Full body: card details + device fingerprinting + risk signals + presentation mode. Use for ECOM where you have device/risk context and want issuer-level network tokenization with rich approval workflows.
- **`POST {{token_url}}/acquirerToken`** — *Safetech (acquirer) token* creation. Minimal body — card only. Use when you don't have device/risk context (back-office, file imports) or you just need an acquirer-side token, not a network token. **Different response shape:** acquirer tokens return `tokenInformation.acquirerTokenNumber` instead of `tokenInformation.tokenNumber`.

### Token retrieval

- **`GET {{token_url}}/tokens/{tokenReferenceIdentifier}`** — token info / current state.
- **`GET {{token_url}}/tokens/{tokenReferenceIdentifier}/details`** — detailed metadata (scheme, masked card, expiry).
- **`GET {{token_url}}/tokens/{tokenReferenceIdentifier}/assets/{assetReferenceIdentifier}`** — fetch token-bound assets (logos, compliance metadata).
- **`GET {{token_url}}/tokens/{tokenReferenceIdentifier}/lifecycle-states`** — current and historical lifecycle state.

### Lifecycle + usage

- **`PATCH {{token_url}}/tokens/{tokenReferenceIdentifier}/lifecycle-states`** — change state (activate / suspend / delete) with a reason.
- **`POST  {{token_url}}/cryptograms`** — generate a fresh cryptogram (DTVV) from a stored token for use in authorization.

### Health

- **`GET {{token_url}}/healthcheck`**

### Bulk mode (MFTS)

File-based, not a single REST call. Combines two REST endpoints (for key exchange) with an SFTP transfer (for the file itself).

**REST endpoints for key exchange:**
- **`GET  {{token_url}}/bulk-tokens/encryption-key`** — returns JPM's PGP public key (`firmPublicKeyText`) used by the merchant to encrypt the outbound card file.
- **`POST {{token_url}}/bulk-tokens/encryption-key`** — register the merchant's own PGP public key so JPM can encrypt the response token file before delivery.

**File transfer (MFTS):** SFTP hosts and credentials are provisioned per merchant by the JPM relationship manager during MFTS onboarding — not on the portal. The merchant receives an inbound folder (upload path) and outbound folder (download path).

**File format:**
- Encoding: CSV (comma-separated), GPG-encrypted, extension `.csv.gpg`.
- Filename convention:
  - Request: `MerchantId-MerchantFileIdentifier-YYYYMMDD.csv.gpg`
  - Response: `MerchantId-MerchantFileIdentifier-YYYYMMDD_<S|D>.csv.gpg` (`S` = standard, `D` = detail)
- Record structure: three row types keyed by the first field.
  - **Header (`0`)** — fields: `Indicator=0`, `MerchantId` (12), `Date` (YYYYMMDD), `ResponseFileType` (`S` or `D`), `RequestType` (e.g. `PAN2NWT`).
  - **Detail (`1`)** — 10 fields, including `Indicator=1`, PAN (16), expiry (MMYY), `presentationModes` (e.g. `ECOM`), telephone, email, IP, `accountholderRefId` (max 24 for Visa), `submerchantId`, `tokenRequestorId` (36).
  - **Trailer (`9`)** — fields: `Indicator=9`, `RecordCount` (8 digits).
- Encoding & line endings: portal does not state explicitly. Assume UTF-8 / Unix LF unless told otherwise.
- Size limits: REST bulk mode caps at ~6 MB / ~32k records per call. MFTS supports up to ~1 GB / ~1M records per file.

## Sample requests

### Create a network token (rich context)

Trimmed shape (the full body has ~85 lines including device geolocation, risk history, and presentation modes):

```json
POST {{token_url}}/tokens
{
  "accountInformation": {
    "cardNumber": "4111111111111111",
    "cardExpiry": { "month": 12, "year": 2027 },
    "cardVerificationNumber": "123",
    "billingAddress": { "...": "..." }
  },
  "device": {
    "deviceType": "MOBILE",
    "deviceIP": "192.168.1.11",
    "locale": "en-US",
    "operatingSystem": "iOS"
  },
  "riskInformation": {
    "walletRiskScore": "...",
    "cardRiskScore": "...",
    "deviceRiskScore": "..."
  },
  "presentationModes": ["ECOM"],
  "recommendationPath": "APPROVED"
}
```

Response captures: `tokenInformation.tokenNumber`, `tokenInformation.tokenReferenceIdentifier`.

### Create a Safetech (acquirer) token — minimal

```json
POST {{token_url}}/acquirerToken
{
  "accountInformation": {
    "cardNumber": "379296848452209002",
    "cardSource": "KEY_ENTERED"
  }
}
```

Response captures: `tokenInformation.acquirerTokenNumber`, `identifier` (use as `tokenReferenceIdentifier` for subsequent calls).

### Request a cryptogram for a stored token (use at authorization time)

```json
POST {{token_url}}/cryptograms
{
  "paymentOrder": {
    "amounts": { "amount": 1234, "currency": "USD" },
    "device": { "deviceType": "DESKTOP", "deviceIP": "...", "locale": "en-US" },
    "initiatedBy": "CARDHOLDER",
    "transactionType": "ECOMMERCE"
  },
  "paymentInstrument": {
    "accountholderName": "Jane Doe",
    "tokenReferenceIdentifier": "{tokenReferenceIdentifier}",
    "tokenNumber": "{tokenNumber}",
    "electronicCommerceIndicator": "02",
    "expiry": { "month": 12, "year": 2027 }
  },
  "tokenCryptogramType": "DTVV"
}
```

Response captures: `transactionId`, `paymentInstrument.tokenAuthenticationValue` (the cryptogram to pass to Online Payments), `paymentInstrument.tokenNumber`.

### Change lifecycle state (delete shown)

```json
PATCH {{token_url}}/tokens/{tokenReferenceIdentifier}/lifecycle-states
{
  "paymentInstrument": {
    "lifecycleManagementAction": {
      "stateChangeReason": "DELETE",
      "stateChangeReasonText": "Consumer suspended subscription"
    }
  }
}
```

Other `stateChangeReason` values follow the same shape: typically `ACTIVATE`, `SUSPEND`, `DELETE`.

### Get token info / lifecycle / assets

```
GET {{token_url}}/tokens/{tokenReferenceIdentifier}
GET {{token_url}}/tokens/{tokenReferenceIdentifier}/details
GET {{token_url}}/tokens/{tokenReferenceIdentifier}/lifecycle-states
GET {{token_url}}/tokens/{tokenReferenceIdentifier}/assets/{assetReferenceIdentifier}
```

No body on any of these.

## Reference flow

### Online (network token)
1. Collect card details (ideally via Checkout drop-in / hosted field so PAN never touches your server).
2. POST `/tokens` with card + device + risk context.
3. Store `tokenReferenceIdentifier` + `tokenNumber`; discard PAN immediately.
4. At checkout time, POST `/cryptograms` with the stored token + current transaction details → receive `tokenAuthenticationValue`.
5. Pass `{tokenReferenceIdentifier, tokenNumber, tokenAuthenticationValue}` to Online Payments as a network-tokenized authorization.

### Online (Safetech / acquirer token)
1. POST `/acquirerToken` with just the card.
2. Store the returned `acquirerTokenNumber` + `tokenReferenceIdentifier`.
3. Pass to Online Payments as an acquirer-tokenized authorization (different field set than network tokens).

### Bulk
1. Export card vault → encrypt with bulk public key → upload to MFTS → decrypt token file from MFTS outbound → map tokens back to customer records → purge original PAN store.

## CAT smoke test

JPM publishes a Tokenization testing page on developer.payments.jpmorgan.com with canonical test card numbers — cross-reference for the current scenarios. Minimum smoke:

- Tokenize a CAT card via `POST /tokens` (or `POST /acquirerToken` for the Safetech flow).
- Use the resulting `tokenReferenceIdentifier` + `tokenNumber` in an Online Payments authorization → confirm approval.
- Generate a cryptogram for the stored token via `POST /cryptograms` → use the returned `tokenAuthenticationValue` in a follow-up authorization.
- Run a lifecycle state change (`PATCH /tokens/{id}/lifecycle-states` with `stateChangeReason: "DELETE"`).
- For bulk mode: `GET /bulk-tokens/encryption-key`, encrypt a small (≤10 card) test file, upload to MFTS CAT folder, confirm the response token file is delivered to your outbound folder.

## Common pitfalls

- Storing the returned token *and* the PAN — defeats the purpose. Discard PAN immediately after tokenization.
- Mixing CAT tokens with PROD tokens — they're not interchangeable.
- Bulk mode without MFTS keys provisioned → uploads silently fail at the gateway.
