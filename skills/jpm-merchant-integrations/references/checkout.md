# Checkout

Checkout is a pre-built solution that allows you to accept online payments securely on your website.

## When to Use

- Build a new checkout or payment page with JPM Drop-in Checkout UI
- Add payment acceptance to an existing application
- Understand the JPM Drop-in UI architecture and API surface

## How Checkout works

``` mermaid
flowchart LR
    A["🖥️ Your customer decides to\nbuy or checkout on your site"] -.-> B["📋 Hosted Payments opens in\nthe Payment section"]
    B -.-> C["💳 The customer enters their\npayment details"]
    C -.-> D["🔒 Payment details are\ncaptured, encrypted, and\nsent to the payment gateway"]
    D -.-> E["🔍 Encryption, fraud analysis,\ntokenization, and then\nroute to payment networks"]
    E -.-> F["📱 Payment confirmation\nis sent to you"]
    F -.-> G["👤 Customer profile is created\nand stored"]
    G -.-> H["📨 Notifications are sent to you"]

    style A fill:#1a7a8a,stroke:#1a7a8a,color:#fff
    style B fill:#fff,stroke:#1a7a8a,color:#000
    style C fill:#fff,stroke:#1a7a8a,color:#000
    style D fill:#fff,stroke:#1a7a8a,color:#000
    style E fill:#fff,stroke:#1a7a8a,color:#000
    style F fill:#1a7a8a,stroke:#1a7a8a,color:#fff
    style G fill:#fff,stroke:#1a7a8a,color:#000
    style H fill:#1a7a8a,stroke:#1a7a8a,color:#fff

```

### Create a Checkout Session

Checkout sessions allow your consumer to initiate a purchase on your web app. The checkout session token you receive is what allows you to utilize the capabilities of the Checkout API, such as Drop-in UI and Hosted Payments Page (HPP).

### How it works

1. The consumer initiates a checkout with your server via their browser.

2. Your server then sends an authentication request via the Checkout API.

3. If authentication is successful, an accessToken (bearer token) is sent in response to your server.

4. Your server then creates a checkout session by sending a POST request to the /checkout/intent endpoint, using the accessToken, the merchant ID, an order reference, and a cart object.

5. The Checkout API sends the checkoutSessionToken as a response to your server, which is then sent to the consumer’s browser.

6. The webpage loads the checkout feature you chose (Drop-in UI or HPP) and initializes it with the checkoutSessionToken.

The following settings can help you better utilize the Checkout API for your business needs.

### Checkout session scenarios and settings

| Setting | Scenario description |
| --- | --- |
| Set authorizationType = TOKENIZE_ONLY | Use this to get the tokens for the cards or bank accounts without going through Zero Dollar Authorization (ZDA). |
| Set captureMethod = CAPTURE_METHOD_MANUAL | Use this to authorize and manually capture a payment via the Payments API. Learn more about how to [authorize and capture a payment](/docs/commerce/online-payments/capabilities/online-payments/how-to/auth-and-capture-payment). |
| Set captureMethod = CAPTURE_METHOD_NOW | Use this to authorize and automatically capture a payment. |
| Set isSaveConsumerProfile = true | Use this to store consumer details so they don’t have to re-enter the information next time. When set to true, Payments API makes a call to consumer profile to either create a new profile or retrieve an existing profile at the time of making the payment. |

Your server exposes an endpoint that the frontend calls to get a `checkoutSessionToken`. This endpoint authenticates with JPM and creates a checkout intent.

**Pseudocode — create checkout session endpoint:**

``` pseudocode
endpoint POST /api/create-checkout-session:
    amount = request.body.amount  // in smallest currency unit (cents)
    accessToken = getAccessToken()
    merchantOrderNumber = generate unique ID (max 22 chars)
    requestId = generate unique ID (max 22 chars)

    payload = {
        merchantOrderNumber: merchantOrderNumber,
        currencyCode: "USD",
        cart: { totalTransactionAmount: amount },
        consumer: {
            email: "customer@example.com",
            billingAddress: {
                recipientFullName: "John Smith",
                line1: "1 Main St",
                city: "San Francisco",
                state: "CA",
                country: "US",
                postalCode: "95000"
            }
        },
        checkoutOptions: {
            authorization: { authorizationType: "AUTH_METHOD_CART_AMOUNT" },
            capture: { captureMethod: "CAPTURE_METHOD_NOW" },
            consumerProfileOptions: { isSaveConsumerProfile: "false" }
        }
    }

    response = HTTP POST to {JPM_CHECKOUT_API_URL}/checkout/intent
        headers:
            Content-Type: application/json
            Authorization: Bearer {accessToken}
            merchantId: {JPM_MERCHANT_ID}        // camelCase!
            requestId: {requestId}                // camelCase, max 22 chars!
        body: JSON(payload)
        (use proxy agent if behind corporate proxy)

    data = parse JSON response
    return { checkoutSessionToken: data.checkoutSessionToken, merchantOrderNumber }
```

**Sample checkout intent request:**

```http
POST https://merchant-api.checkout-cat.merchant.jpmorgan.com/v1/checkout/intent
Content-Type: application/json
Authorization: Bearer eyJ0eXAiOiJKV1Qi…
merchantId: 996897591058
requestId: cffbe6dbfb94bce8a1b2c3

{
  "merchantOrderNumber": "1773250868",
  "currencyCode": "USD",
  "cart": {
    "totalTransactionAmount": 4999
  },
  "consumer": {
    "email": "customer@example.com",
    "billingAddress": {
      "recipientFullName": "John Smith",
      "line1": "1 Main St",
      "city": "San Francisco",
      "state": "CA",
      "country": "US",
      "postalCode": "95000"
    }
  },
  "checkoutOptions": {
    "authorization": { "authorizationType": "AUTH_METHOD_CART_AMOUNT" },
    "capture": { "captureMethod": "CAPTURE_METHOD_NOW" },
    "consumerProfileOptions": { "isSaveConsumerProfile": "false" }
  }
}
```

**Sample checkout intent response:**

```json
{
  "checkoutSessionToken": "eyJraWQiOiIzMDEyZWU1ZC1iMDE2LTQ4ZDEt…",
  "merchantOrderNumber": "1773250868"
}
```

Your backend server returns the `checkoutSessionToken` back to your web app, where it will be used to render the Checkout form using the JavaScript library.

[Documentation](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fonline-payments%2Fcapabilities%2Fcheckout%2Fhow-to%2Fcreate-a-checkout-session.md)

## Critical Field Constraints

| Field | Constraint | Common Mistake |
| ------- | ----------- | ---------------- |
| `merchantId` header | **camelCase** | `merchant-id` (kebab-case) → 400 |
| `requestId` header | **camelCase**, max **22 chars** | Full UUID (36 chars) → 400 |
| `merchantOrderNumber` | Max **22 chars** | Long UUID → 400 |
| `totalTransactionAmount` | Integer, **smallest currency unit** (cents) | Float dollars → wrong amount |
| `currencyCode` | ISO 4217 uppercase (`USD`, `EUR`) | Lowercase → rejected |

## Payment Methods

- [Payment methods](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fonline-payments%2Fcapabilities%2Fcheckout%2Fpayment-methods.md) Discover the wide range of payment methods that the J.P. Morgan Checkout API supports on the Payments Developer Portal.

## EU Local Payment Methods

- [EU local payment methods](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fonline-payments%2Fcapabilities%2Fcheckout%2Feu-local-payment-methods.md) Discover the wide range of EU local payment methods that the J.P. Morgan Checkout API supports on the Payments Developer Portal.

## Drop-in UI

Drop-in UI is a complete, ready-made payment UI that offers a quick and easy way to securely accept payments. You can customize your Checkout form to fit stylistically into your current checkout experience by using the Checkout Settings page in the Commerce Center portal, or by using JavaScript to modify basic styles or the full theme object.

### Flow Diagram

Here's a diagram that illustrates the Drop-In user interface (UI) process flow:

``` mermaid
sequenceDiagram
    participant B as Browser
    participant MS as Merchant Server
    participant UI as Drop in UI Bundle
    participant CB as Checkout Backend

    B->>MS: 1. User initiates checkout
    MS->>CB: 2. Authenticate - Cert -
    CB-->>MS: 3. accessToken
    MS->>CB: 4. SetupCheckoutIntent<br/>- accessToken, merchantID,<br/>orderReference, cart -
    CB-->>MS: 5. checkoutSessionToken
    MS-->>B: 6. checkoutSessionToken
    B->>UI: 7. DropInUI - checkoutSessionToken - .mount()
    UI-->>B: 8. Render Checkout Form
    B->>UI: 9. User Clicks Pay
    UI->>CB: 10. Pay - checkout form data -
    CB-->>UI: 11. PayResult
    UI-->>B: 12. Announce success or error result
    MS->>CB: 13. Notifications - start & end date,<br/>merchant order number -
```

for customizations read:[Drop-in UI](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fonline-payments%2Fcapabilities%2Fcheckout%2Fdrop-in-ui.md)

### Sample Implementation

Step 1: Set Up Environment Variables

```env
# ─── Checkout API ─────────────────────────────────────────────────
JPM_MERCHANT_ID=<your-merchant-id>
JPM_CHECKOUT_API_URL=https://merchant-api.checkout-cat.merchant.jpmorgan.com/v1
```

> Auth env vars (`JPM_CLIENT_ID`, `JPM_PRIVATE_KEY_PATH`, `JPM_CERT_THUMBPRINT`, `JPM_RESOURCE_ID`, `JPM_JWT_TTL_SEC`) are owned by the auth module set up via the `jpm-oauth` skill — they're already in your `.env`. Don't duplicate them here.

Step 2: Server — Authentication
Import `getAccessToken` (or your project's language equivalent) from the auth module that the `jpm-oauth` skill wrote into your project. Do **not** reimplement token fetching inline — the imported function already caches and refreshes the access token per JPM guidance.

Step 3: Server — Create Checkout Session Endpoint
Follow the pseudocode in the "Create a Checkout Session" section above to implement your checkout session.

Step 4: Frontend — Load the Drop-in UI Script

Add the Drop-in UI script to your HTML. The script registers a global `DropInUI` class — no npm package needed.

```html
<!-- Add to your HTML <head> -->
<!-- CAT (pre-prod) -->
<script type="module" src="https://checkout-cat.merchant.jpmorgan.com/drop-in-ui.mjs"></script>
<!-- Production -->
<script type="module" src="https://checkout.merchant.jpmorgan.com/drop-in-ui.mjs"></script>
```

The `type="module"` is required — the Drop-in UI is an ES module.

Step 5:  Frontend — Mount the Drop-in UI and Handle Events
The Drop-in UI renders a complete payment form (card inputs, submit button) inside a container element you provide. It handles card encryption and payment submission internally.

**Your HTML just needs an empty container element:**

```html
<div id="dropin-container"></div>
```

**Pseudocode — mount Drop-in UI and handle events:**

``` pseudocode
// 1. Call your server to create a checkout session
response = HTTP POST /api/create-checkout-session { amount: 4999 }
{ checkoutSessionToken, merchantOrderNumber } = response

// 2. Wait for the Drop-in UI script to load (it's async)
wait until window.DropInUI is defined (poll or use load event)

// 3. Create and mount the Drop-in UI
dropin = new DropInUI({ checkoutSessionToken })
dropin.mount("dropin-container")   // ID of a <div> in your page

// 4. Subscribe to payment lifecycle events
dropin.subscribe(function(event):
    if event.message == "MountSuccess":
        // Payment form is rendered, hide loading spinner
    if event.namespace == "payment" and event.level == "info":
        if event.message == "PaymentSuccess":
            // Navigate to success page, pass merchantOrderNumber
        if event.message == "PaymentUnsuccessful":
            // Show error, consumer can retry
)

// 5. On page teardown / navigation away, clean up:
dropin.unmount()
```

**Drop-in UI event bus messages:**

| Level | Message | When |
| ------- | --------- | ------ |
| `info` | `MountSuccess` | Form rendered successfully |
| `info` | `PaymentSuccess` | Payment completed |
| `info` | `PaymentUnsuccessful` | Payment failed (consumer can retry) |
| `info` | `PaymentPending` | Pending resolution (async methods) |
| `error` | `PaymentError` | Payment request failed |
| `error` | `UnknownError` | Unrecoverable error |

**Framework-specific notes:**

- **React / Vue / Angular**: Mount the Drop-in UI in a lifecycle hook (e.g., `useEffect`, `onMounted`, `ngOnInit`). Use a guard flag to prevent double-initialization if your framework double-mounts in dev mode (e.g., React StrictMode). Clean up with `dropin.unmount()` in the teardown/cleanup function.
- **Vanilla JS / server-rendered HTML**: Mount after `DOMContentLoaded` or after fetching the session token. No special considerations.
- **Controlled submit** (use your own button instead of the Drop-in's): pass `controlledSubmit: true` to the constructor, then call `dropin.submit()` when the user clicks your button.

Step 6: Server — Payment Verification via Notifications

fter the frontend receives a `PaymentSuccess` event, verify the transaction on the server side using the notifications API.

**Pseudocode — notifications endpoint:**

``` pseudocode
endpoint GET /api/notifications/{merchantOrderNumber}:
    accessToken = getAccessToken()

    // JPM requires periodStart within the last 30 days.
    // Use 29 days to avoid boundary precision issues.
    periodEnd   = now as ISO 8601
    periodStart = (now - 29 days) as ISO 8601

    url = {JPM_CHECKOUT_API_URL}/checkout/notifications
        ?merchantOrderNumber={merchantOrderNumber}
        &periodStart={periodStart}
        &periodEnd={periodEnd}

    response = HTTP GET to url
        headers:
            Content-Type: application/json
            Authorization: Bearer {accessToken}
            merchantId: {JPM_MERCHANT_ID}
            requestId: {generate unique ID, max 22 chars}
        (use proxy agent if behind corporate proxy)

    return parse JSON response
```

**Sample notifications request:**

```http
GET https://merchant-api.checkout-cat.merchant.jpmorgan.com/v1/checkout/notifications
  ?merchantOrderNumber=1773254924869
  &periodStart=2026-02-10T18:20:53Z
  &periodEnd=2026-03-11T18:20:53Z
Content-Type: application/json
Authorization: Bearer eyJ0eXAiOiJKV1Qi…
merchantId: 996897591058
requestId: 5512281667746c1b1234
```

**Sample notifications response:**

```json
{
  "nextPageToken": "",
  "messages": [
    {
      "tokenNotification": {
        "responseCode": "APPROVED",
        "responseMessage": "Transaction approved by Issuer",
        "merchantOrderNumber": "1773254924869",
        "requestId": "02f8594c36ed4cbc853ae5",
        "token": "4242427761124242",
        "tokenType": "TOKEN_TYPE_ACQUIRER",
        "checkoutReference": "1773254924869",
        "fraudCheckStatus": "FRAUD_CHECK_STATUS_APPROVED",
        "status": "STATUS_SUCCESS"
      },
      "messageInfo": {
        "receiptHandle": "",
        "messageId": "9d8d7442-0a89-4c71-8c31-2ee58815405f"
      },
      "createdAt": "2026-03-11T18:49:06.768315Z",
      "merchantOrderNumber": "1773254924869",
      "requestId": "02f8594c36ed4cbc853ae5"
    },
    {
      "orderNotification": {
        "mitTransactionReference": "016070692164427",
        "totalAmount": {
          "currencyCode": "USD",
          "decimalCount": 2,
          "amount": "4999"
        },
        "fraudCheckResult": {
          "deviceDataUsed": true,
          "fraudCheckStatus": "FRAUD_CHECK_STATUS_APPROVED"
        },
        "accountHolder": {
          "billingAddress": {
            "country": "US",
            "postalCode": "95000",
            "recipientFullName": "John Smith",
            "line1": "1 Main St",
            "city": "San Francisco",
            "state": "CA"
          }
        },
        "transactionTimestamp": "2026-03-11T18:49:06.521Z",
        "paymentMethod": {
          "approvalCode": "tst419",
          "maskedAccountNumber": "424242XXXXXX4242",
          "card": {
            "cardTypeName": "VISA",
            "last4CardNumber": "4242",
            "expiry": { "month": 12, "year": 2029 },
            "networkResponse": {
              "cardVerificationResult": "MATCH",
              "addressVerificationResult": "ADDRESS_POSTALCODE_MATCH"
            },
            "cardType": "VI"
          },
          "paymentMethodType": "PAYMENT_METHOD_TYPE_CODE_CARD"
        },
        "checkoutReference": "1773254924869",
        "status": "STATUS_SUCCESS",
        "responseCode": "APPROVED",
        "responseMessage": "Transaction approved by Issuer",
        "merchantOrderNumber": "1773254924869",
        "transactionReference": "3dcac25e-fe06-4892-b09e-13140ce44f29",
        "last4OfCardPan": "4242"
      },
      "messageInfo": {
        "receiptHandle": "",
        "messageId": "ea2595ec-300e-4ae0-80a1-c0f18968374e"
      },
      "createdAt": "2026-03-11T18:49:06.778239Z",
      "merchantOrderNumber": "1773254924869",
      "requestId": "02f8594c36ed4cbc853ae5"
    }
  ]
}
```

**Key fields in the notifications response:**

| Field | Where | Meaning |
| ------- | ------- | --------- |
| `orderNotification.status` | `STATUS_SUCCESS` | Payment completed |
| `orderNotification.responseCode` | `APPROVED` | Issuer approved |
| `orderNotification.totalAmount.amount` | `"4999"` | Amount in cents (string) |
| `orderNotification.paymentMethod.maskedAccountNumber` | `424242XXXXXX4242` | Masked card |
| `orderNotification.paymentMethod.approvalCode` | `tst419` | Issuer approval code |
| `orderNotification.transactionReference` | UUID | Use for refunds/queries |
| `tokenNotification.token` | `4242427761124242` | Acquirer token |
| `tokenNotification.fraudCheckStatus` | `FRAUD_CHECK_STATUS_APPROVED` | Fraud screening result |

Step 7 (Optional): Verify success:

After the Drop-in UI fires `PaymentSuccess`, navigate to a success page. Pass the `merchantOrderNumber` (via client-side routing state, query params, or however your framework handles navigation). On the success page, call your server's notifications endpoint to verify and display transaction details.

**Pseudocode — success page:**

``` pseudocode
on page load:
    merchantOrderNumber = get from navigation state or query params
    if merchantOrderNumber exists:
        notification = HTTP GET /api/notifications/{merchantOrderNumber}
        display transaction details from notification response
```

## Implementation Checklist

- [ ] Set Checkout-specific env vars (`JPM_MERCHANT_ID`, `JPM_CHECKOUT_API_URL`). Auth env vars are already set by `jpm-oauth`.
- [ ] Server: import `getAccessToken` from the auth module created by `jpm-oauth` (do NOT re-implement OAuth here)
- [ ] Server: implement `POST /api/create-checkout-session` endpoint
- [ ] Server: implement `GET /api/notifications/{merchantOrderNumber}` endpoint
- [ ] Frontend: add Drop-in UI `<script type="module">` tag to HTML
- [ ] Frontend: create a checkout page with `<div id="dropin-container">`
- [ ] Frontend: call server for session token, mount Drop-in UI, subscribe to events
- [ ] Frontend: create a success page that verifies payment via notifications
- [ ] Handle framework-specific double-initialization (e.g., React StrictMode guard) if applicable
- [ ] Configure proxy agent if behind a corporate firewall
- [ ] Ensure dev proxy config routes `/api` to your backend if running frontend and backend on different ports

## Implementation Example

For a complete sample implementation of the Checkout API using Drop-in UI, see the [Checkout Sample App](examples/checkout-sample-app.md).

## Additional Documentation

- [Drop-in UI](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fonline-payments%2Fcapabilities%2Fcheckout%2Fdrop-in-ui.md) Integrate Drop-in UI for a seamless payment experience you can customize with the J.P. Morgan Checkout API. Supports real-time updates and secure transactions.
- [Tokenization of payment data](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fonline-payments%2Fcapabilities%2Fcheckout%2Ftokenization-of-payment-data.md) Stay updated on orders, tokens, and profiles with the J.P. Morgan Checkout Tokenization API on the Payments Developer Portal. Review how the API works and the supported tokenization types.
- [Notifications](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fonline-payments%2Fcapabilities%2Fcheckout%2Fnotifications.md) Stay updated on orders, tokens, and profiles with the J.P. Morgan Checkout Notifications API on the Payments Developer Portal. Review how the API works and the supported notification types.
- [Fraud prevention](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fonline-payments%2Fcapabilities%2Fcheckout%2Ffraud-prevention.md) Find out about J.P. Morgan's Safetech fraud tools to secure transactions by screening for risks and offering flexible options to optimize fraud prevention. Available through the Checkout API.
- [Soft merchant descriptors](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fonline-payments%2Fcapabilities%2Fcheckout%2Fsoft-merchant-descriptors.md) Enhance transaction clarity with soft merchant data, allowing consumers to easily identify charges and merchants to reduce disputes. Supported through the J.P. Morgan Checkout API on Developer Portal.
- [Level 2 and Level 3 data](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fonline-payments%2Fcapabilities%2Fcheckout%2Flevel-2-and-level-3-data.md) Learn how to send Level 2 and Level 3 data to qualify for lower interchange fees on commercial cards through the J.P. Morgan Checkout API on Payments Developer Portal.
- [Consumer profile management](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fonline-payments%2Fcapabilities%2Fcheckout%2Fconsumer-profile-management.md) Create, store, update, and maintain consumer profiles, as well as payment card information with J.P. Morgan during Checkout.
- [3DS authentication](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fonline-payments%2Fcapabilities%2Fcheckout%2F3ds-authentication.md) Discover how 3D Secure (3DS) enhances payment security by authenticating cardholders before authorization and reducing fraud with the J.P. Morgan Checkout API on Payments Developer Portal.
- [Pay by Link](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fonline-payments%2Fcapabilities%2Fcheckout%2Fpay-by-link.md) Pay by Link lets you collect payments via a shared link, bypassing the need for store visits. Easily create links using J.P. Morgan's Commerce Center or Checkout API on the Payments Developer Portal.
- [Hosted Payment Page](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fonline-payments%2Fcapabilities%2Fcheckout%2Fhosted-payment.md) The Hosted Payment Page through J.P. Morgan's Checkout API offers a secure portal for accepting payments without managing your own gateway. Learn more on Payments Developer Portal.
- [EU local payment methods](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fonline-payments%2Fcapabilities%2Fcheckout%2Feu-local-payment-methods.md) Discover the wide range of EU local payment methods that the J.P. Morgan Checkout API supports on the Payments Developer Portal.
- [Payment methods](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fonline-payments%2Fcapabilities%2Fcheckout%2Fpayment-methods.md) Discover the wide range of payment methods that the J.P. Morgan Checkout API supports on the Payments Developer Portal.
- [Checkout](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fonline-payments%2Fcapabilities%2Fcheckout%2Foverview.md) Learn how to securely accept online payments with the J.P. Morgan Checkout API. Integrate easily with Drop-in UI, Hosted Payment Page or Pay by Link.
