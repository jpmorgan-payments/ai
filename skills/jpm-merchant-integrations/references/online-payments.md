# Online Payments

The Online Payments APIs allow you to accept web and mobile payments across a variety of regions and countries. Manage the entire payments lifecycle for multiple methods of payments, including recurring payments, chargebacks, transfers, and third-party services.

For additional information, refer to the [Online Payments API documentation](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fonline-payments%2Fonline-payments.md)

## When to Use

- Build recurring billing and subscription management experiences
- Process payments and manage the payment lifecycle for card, wallet, local, and alternative methods of payment
- Integrate with third-party services for payments, payouts, and more

## Authentication

Authentication is handled by the merchant's auth module (set up via the `jpm-oauth` skill). Import `getAccessToken` (or your language's equivalent) from that module and use it as `Authorization: Bearer <token>` on every Online Payments API call. Do **not** reimplement OAuth here — the auth module already caches tokens correctly per JPM guidance.

## How Online Payments works

``` mermaid
flowchart LR
    subgraph Merchant["🏪 Merchant"]
    end

    subgraph JPM["J.P.Morgan\nCommerce Platform\necommerce/Card not present"]
        API["Online Payments API"]
        NAPI["Notifications API"]
        API -.-> NAPI
    end

    subgraph GCPN["💳 Global card payment\nnetworks"]
    end

    subgraph LPN["💳 Local payment\nnetworks"]
    end

    subgraph FI["🏛️ Financial institutions"]
    end

    Merchant <-.-> API
    NAPI -.-> Merchant
    API <-.-> GCPN
    API -.-> LPN
    API -.-> FI

    style Merchant fill:#fff,stroke:#1a7a8a,color:#000
    style JPM fill:#1a7a8a,stroke:#1a7a8a,color:#fff
    style API fill:#d4f0f0,stroke:#1a7a8a,color:#000
    style NAPI fill:#fff,stroke:#1a7a8a,color:#000
    style GCPN fill:#fff,stroke:#1a7a8a,color:#000
    style LPN fill:#fff,stroke:#1a7a8a,color:#000
    style FI fill:#fff,stroke:#1a7a8a,color:#000
```

[How it works: Online Payments API](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fonline-payments%2Fcapabilities%2Fonline-payments%2Foverview.md)

## Relevant Documentation

#### Online Payments

- [Support](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fonline-payments%2Fsupport.md)
- [Testing](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fonline-payments%2Ftesting.md) Test your payment integration with pre-determined outcomes using test card data for Online Payments. Simulate various scenarios for 3-D Secure, network tokens, and alternative payment methods.
- [Core concepts](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fonline-payments%2Fcore-concepts.md) Review the core concepts for Online Payments and Checkout APIs on J.P. Morgan's Payments Developer Portal, covering payment lifecycle, security, integration, and environment reliability.
- [Getting started](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fonline-payments%2Fgetting-started.md) Get started with J.P. Morgan's Online Payments APIs: create a developer account, set up a workspace, apply for a live account, and integrate with our payment processing services.
- [Online Payments](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fonline-payments%2Fonline-payments.md)

##### Online Payments

- [Online Payments](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fonline-payments%2Fcapabilities%2Fonline-payments%2Foverview.md)  Learn how the Online Payments API works and the benefits of integration to seamlessly accept, process, and settle online payments on the Payments Developer Portal.

###### Payment methods

- [WeChat Pay](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fonline-payments%2Fcapabilities%2Fonline-payments%2Fpayment-methods%2Fwechat-pay.md) Accept mobile payments with WeChat Pay via J.P. Morgan's Online Payments API. Supports EUR and USD. Integrate now for seamless transactions through the WeChat Pay digital wallet.
- [Trustly](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fonline-payments%2Fcapabilities%2Fonline-payments%2Fpayment-methods%2Ftrustly.md) Boost revenue with Trustly's real-time bank transfers, reducing fees without leaving your site. Available in Europe through J.P. Morgan's Online Payments API.
- [SEPA](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fonline-payments%2Fcapabilities%2Fonline-payments%2Fpayment-methods%2Fsepa.md) Process payments securely in EUR across multiple countries by enabling SEPA direct debits for European consumers with the J.P. Morgan Online Payments API on the Payments Developer Portal.
- [Paze](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fonline-payments%2Fcapabilities%2Fonline-payments%2Fpayment-methods%2Fpaze.md) Offer seamless payments and a smooth checkout experience with Paze, a digital wallet supported by J.P. Morgan's Online Payments API.
- [PayPal](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fonline-payments%2Fcapabilities%2Fonline-payments%2Fpayment-methods%2Fpaypal.md) Enable quick and convenient online payments with PayPal, offered through J.P. Morgan's Online Payments API in the Payments Developer Portal.
- [iDEAL](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fonline-payments%2Fcapabilities%2Fonline-payments%2Fpayment-methods%2Fideal.md) iDEAL enables secure bank transfers for Dutch consumers via their own banks. Integrate iDEAL with J.P. Morgan's Online Payments API for seamless payments in EUR.
- [Google Pay](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fonline-payments%2Fcapabilities%2Fonline-payments%2Fpayment-methods%2Fgoogle-pay.md) Enable seamless transactions with digital wallet Google Pay through J.P. Morgan's Online Payments API on the Payments Developer Portal.
- [Apple Pay](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fonline-payments%2Fcapabilities%2Fonline-payments%2Fpayment-methods%2Fapple-pay.md) Learn more about how to enable secure payments with Apple Pay on iOS devices with the J.P. Morgan Online Payments API on Payments Developer Portal.
- [Alipay](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fonline-payments%2Fcapabilities%2Fonline-payments%2Fpayment-methods%2Falipay.md) Integrate Alipay to offer Chinese consumers seamless eWallet payments with the J.P. Morgan Online Payments API on the Payments Developer Portal.
- [ACH](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fonline-payments%2Fcapabilities%2Fonline-payments%2Fpayment-methods%2Fach.md) Provide cost-effective direct debits from US bank accounts through ACH/eCheck payments with J.P. Morgan's Online Payments API. Ideal for payroll, bills, and subscriptions.
- [Cards](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fonline-payments%2Fcapabilities%2Fonline-payments%2Fpayment-methods%2Fcards.md) Explore card transaction support by region, authentication options, and advanced features like sub-merchant data and level 3 details with J.P. Morgan's Online Payments API.
- [Payment methods](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fonline-payments%2Fcapabilities%2Fonline-payments%2Fpayment-methods%2Fpayment-methods-overview.md) Explore the payment methods supported by J.P. Morgan's Online Payments API, including cards, wallets, and alternative payments. Check availability by region and currency.

###### Payment enhancements

- [Tokenization](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fonline-payments%2Fcapabilities%2Fonline-payments%2Fpayment-enhancements%2Ftokenization.md) Discover how you can enhance security with J.P. Morgan's tokenization solutions through the Online Payments API. Replace sensitive card data with tokens for recurring and card-on-file transactions.
- [Stored payments](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fonline-payments%2Fcapabilities%2Fonline-payments%2Fpayment-enhancements%2Fstored-payments.md) Learn how to store cardholder-initiated payments for seamless transactions with the J.P. Morgan Online Payments API. Store credentials securely and let consumers use cards on file for quick purchases.
- [Recurring payments](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fonline-payments%2Fcapabilities%2Fonline-payments%2Fpayment-enhancements%2Frecurring-payments.md) Discover how to set up recurring payments for seamless transactions, securely store payment information, and automate regular payments with the J.P. Morgan Online Payments API.
- [Real-Time Account Updater](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fonline-payments%2Fcapabilities%2Fonline-payments%2Fpayment-enhancements%2Faccount-updater.md) Discover how to enhance payment processing with Real-Time Account Updater (RTAU) for Visa cards with the J.P. Morgan Online Payments API on the Payments Developer Portal.
- [Fraud prevention](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fonline-payments%2Fcapabilities%2Fonline-payments%2Fpayment-enhancements%2Ffraud-tools.md) Discover how to prevent fraud by analyzing transactions for risk evaluation with the J.P. Morgan Online Payments API on the Payments Developer Portal. Review fraud check responses and status codes.
- [Encryption](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fonline-payments%2Fcapabilities%2Fonline-payments%2Fpayment-enhancements%2Fencryption.md) Learn how to enhance security with page encryption, reducing PCI scope by encrypting card data in real-time transactions with the J.P. Morgan Online Payments API on the Payments Developer Portal.
- [Direct Pay](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fonline-payments%2Fcapabilities%2Fonline-payments%2Fpayment-enhancements%2Fdirect-pay.md) Learn how Direct Pay enables real-time P2P and B2C payments for Visa and Mastercard with the J.P. Morgan Online Payments API on Payments Developer Portal.
- [Consumer profile management](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fonline-payments%2Fcapabilities%2Fonline-payments%2Fpayment-enhancements%2Fconsumer-profile-management.md) Learn how to manage consumer profiles with the J.P. Morgan Online Payments API. Create, store, and update profiles securely for seamless transactions and recurring payments.
- [3-D Secure](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fonline-payments%2Fcapabilities%2Fonline-payments%2Fpayment-enhancements%2F3d-secure.md) Learn how you can enhance security with 3-D Secure (3DS) for cardholder authentication with the J.P. Morgan Online Payments API. Reduce fraud, shift cost liability, and meet EU/UK SCA requirements.
- [Payment enhancements](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fonline-payments%2Fcapabilities%2Fonline-payments%2Fpayment-enhancements%2Fpayment-enhancement-overview.md) Enhance your payment solutions with the J.P. Morgan Online Payments API. Integrate features like fraud prevention, encryption, tokenization and more, available across various regions.

###### How To

- [Obtain a fraud score](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fonline-payments%2Fcapabilities%2Fonline-payments%2Fhow-to%2Fget-a-fraud-score.md) Utilize Safetech fraud scoring to assess transaction risk with J.P. Morgan's Online Payments API. Generate fraud scores, analyze risk, and enhance fraud prevention strategies.
- [Update a payment](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fonline-payments%2Fcapabilities%2Fonline-payments%2Fhow-to%2Fupdate-a-payment.md) Learn how to make updates to existing payments, such as voiding a payment or partially reversing a payment, through the Online Payments API in the J.P Morgan Payments Developer Portal.
- [Refund a payment](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fonline-payments%2Fcapabilities%2Fonline-payments%2Fhow-to%2Frefund-a-payment.md) Learn how to issue payment refunds with the Online Payments API on J.P. Morgan's Payments Developer Portal, including full, partial, standalone, and multi-capture refunds.
- [Authorize and capture a payment](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fonline-payments%2Fcapabilities%2Fonline-payments%2Fhow-to%2Fauthorize-and-capture-a-payment.md) Learn how to authorize and capture payments with J.P. Morgan's Online Payments API on the Payments Developer Portal, including immediate, delayed, and manual captures.
- [Verify a payment method](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fonline-payments%2Fcapabilities%2Fonline-payments%2Fhow-to%2Fverify-a-payment.md) Learn how to verify a payment method without holding funds from the consumer's account through the Online Payments API on the J.P.Morgan Payments Developer Portal.

---

## Payment Lifecycle Workflows

### Authorize and Capture Flow

``` mermaid
flowchart TD
    A["Authorize Payment"] --> B{captureMethod?}
    B -->|NOW| C["Auth + Capture in one step"]
    B -->|DELAYED| D["Auth only — auto-captured later"]
    B -->|MANUAL| E["Auth only — you capture explicitly"]
    E --> F["POST /payments/{transactionId}/captures"]
    F --> G{Capture type?}
    G -->|Full| H["Capture full authorized amount"]
    G -->|Partial| I["Capture partial amount\n+ isAmountFinal: true"]
    G -->|Multi| J["Multiple captures against\nsame authorization"]
    C --> K["Payment Complete"]
    D --> K
    H --> K
    I --> K
    J --> K
```

**Capture methods explained:**

| `captureMethod` | Behavior |
|---|---|
| `NOW` | Authorization and capture happen in a single request. Funds are settled immediately. |
| `DELAYED` | Authorization is placed; capture happens automatically at settlement time. |
| `MANUAL` | Authorization is placed; you must explicitly capture via a separate API call. Use for split shipments or when the final amount is unknown at auth time. |

### Void and Refund Flow

``` mermaid
flowchart TD
    A["Authorized / Captured Payment"] --> B{Before settlement?}
    B -->|Yes| C{Void type?}
    C -->|Full void| D["PATCH /payments/{transactionId}\n{ isVoid: true }"]
    C -->|Partial reversal| E["PATCH /payments/{transactionId}\n{ captureMethod: NOW, amount: reducedAmount }"]
    B -->|No — already settled| F{Refund method?}
    F -->|By transaction ID| G["POST /refunds\nwith transactionReferenceId"]
    F -->|By card number| H["POST /refunds\nwith card accountNumber"]
    D --> I["Funds released"]
    E --> I
    G --> J["Refund processed"]
    H --> J
```

### Incremental Authorization Flow

Use incremental authorization when the original authorized amount needs to increase (e.g., hotel stay extended, additional items added).

``` mermaid
flowchart LR
    A["Initial Auth\nisAmountFinal: false"] --> B["PATCH /payments/{transactionId}\n{ amount: additionalAmount }"]
    B --> C["Updated authorization total"]
    C --> D["Capture when ready"]
```

> **Note:** The initial authorization should be `CARDHOLDER`-initiated with `isAmountFinal: false`. The incremental auth maps to message type `MINC`.

---

## Sample Requests

### Authorize and Capture Now (Card)

One-step authorization and capture for a card payment.

```http
POST /payments
Content-Type: application/json
Authorization: Bearer {access_token}
request-id: {unique-uuid}
merchant-id: {your-merchant-id}
```

```json
{
  "captureMethod": "NOW",
  "amount": 10000,
  "currency": "USD",
  "merchantOrderNumber": "1711500000",
  "merchant": {
    "merchantSoftware": {
      "companyName": "Your Company",
      "productName": "Your Product",
      "version": "2.0"
    }
  },
  "paymentMethodType": {
    "card": {
      "accountNumber": "4470051300000000003",
      "expiry": {
        "month": 5,
        "year": 2027
      },
      "cvv": 411
    }
  },
  "accountHolder": {
    "fullName": "Jane Doe",
    "billingAddress": {
      "line1": "123 Main Street",
      "city": "Tampa",
      "state": "FL",
      "postalCode": "33626"
    }
  },
  "initiatorType": "CARDHOLDER",
  "accountOnFile": "NOT_STORED",
  "isAmountFinal": true
}
```

### Authorize Only — Manual Capture

Two-step flow: authorize first, then capture later when ready to fulfill.

**Step 1 — Authorize:**

```http
POST /payments
```

```json
{
  "captureMethod": "MANUAL",
  "amount": 10000,
  "currency": "USD",
  "merchantOrderNumber": "1711500001",
  "merchant": {
    "merchantSoftware": {
      "companyName": "Your Company",
      "productName": "Your Product",
      "version": "2.0"
    }
  },
  "paymentMethodType": {
    "card": {
      "accountNumber": "371144371144376",
      "expiry": {
        "month": 5,
        "year": 2027
      },
      "cvv": 4111
    }
  },
  "accountHolder": {
    "fullName": "Jane Doe",
    "billingAddress": {
      "line1": "123 Main Street",
      "city": "Tampa",
      "state": "FL",
      "postalCode": "33626"
    }
  },
  "isAmountFinal": true
}
```

**Step 2 — Full capture:**

```http
POST /payments/{transactionId}/captures
```

```json
{
  "captureMethod": "NOW"
}
```

**Step 2 (alt) — Partial capture:**

```json
{
  "captureMethod": "NOW",
  "amount": 5000,
  "isAmountFinal": true
}
```

**Step 2 (alt) — Multi-capture:**

```json
{
  "amount": 7500,
  "multiCapture": {
    "multiCaptureSequenceNumber": 2,
    "multiCaptureRecordCount": 2,
    "isFinalCapture": false
  }
}
```

### Void a Payment

**Full void** (before settlement):

```http
PATCH /payments/{transactionId}
```

```json
{
  "isVoid": true
}
```

**Partial reversal** (reduce the authorized amount):

```json
{
  "captureMethod": "NOW",
  "amount": 5000
}
```

### Refund a Payment

**Refund by transaction ID** (linked refund):

```http
POST /refunds
```

```json
{
  "merchant": {
    "merchantSoftware": {
      "companyName": "Your Company",
      "productName": "Your Product",
      "version": "2.0"
    }
  },
  "amount": 100,
  "currency": "USD",
  "paymentMethodType": {
    "transactionReference": {
      "transactionReferenceId": "{original-transactionId}"
    }
  }
}
```

**Standalone refund by card number** (unlinked):

```json
{
  "merchant": {
    "merchantSoftware": {
      "companyName": "Your Company",
      "productName": "Your Product",
      "version": "2.0"
    }
  },
  "amount": 100,
  "currency": "USD",
  "paymentMethodType": {
    "card": {
      "accountNumber": "4777779999999990",
      "expiry": {
        "month": 12,
        "year": 2025
      },
      "cvv": 411
    }
  }
}
```

### Incremental Authorization

Increase the authorized amount on an existing transaction (e.g., hotel extended stay):

```http
PATCH /payments/{transactionId}
```

```json
{
  "amount": 5000
}
```

### Retrieve a Payment

```http
GET /payments/{transactionId}
Content-Type: application/json
Authorization: Bearer {access_token}
request-id: {unique-uuid}
merchant-id: {your-merchant-id}
```

### ACH / eCheck Payment

```http
POST /payments
```

```json
{
  "captureMethod": "NOW",
  "amount": 10000,
  "currency": "USD",
  "statementDescriptor": "Statement Descriptor",
  "merchant": {
    "merchantSoftware": {
      "companyName": "Payment Company",
      "productName": "Application Name",
      "version": "2.0"
    },
    "softMerchant": {
      "merchantPurchaseDescription": "Purchase Description"
    }
  },
  "paymentMethodType": {
    "ach": {
      "accountNumber": "0888271156",
      "financialInstitutionRoutingNumber": "122000247",
      "accountType": "CHECKING"
    }
  },
  "accountHolder": {
    "firstName": "Jane",
    "lastName": "Doe"
  }
}
```

### SEPA Direct Debit Payment

```http
POST /payments
```

```json
{
  "captureMethod": "NOW",
  "amount": 100,
  "currency": "EUR",
  "merchantOrderNumber": "1711500002",
  "merchant": {
    "merchantSoftware": {
      "companyName": "Your Company",
      "productName": "Your Product",
      "version": "2.0"
    }
  },
  "paymentMethodType": {
    "sepa": {
      "internationalBankAccountNumber": "DE62370400440554416800",
      "internationalBusinessIdentifierCode": "COBADEFFXXX"
    }
  },
  "accountHolder": {
    "firstName": "Jane",
    "lastName": "Doe",
    "fullName": "Jane Doe",
    "billingAddress": {
      "line1": "123 Hauptstrasse",
      "city": "Berlin",
      "state": "BE",
      "countryCode": "USA",
      "postalCode": "10115"
    }
  },
  "initiatorType": "CARDHOLDER",
  "accountOnFile": "NOT_STORED",
  "isAmountFinal": true
}
```

### PayPal Payment (Local Payment Method)

```http
POST /payments
```

```json
{
  "amount": 680,
  "currency": "EUR",
  "merchantOrderNumber": "1711500003",
  "statementDescriptor": "Order description",
  "merchant": {
    "merchantSoftware": {
      "companyName": "Your Company",
      "productName": "Your Product",
      "version": "2.0"
    }
  },
  "paymentMethodType": {
    "paypal": {
      "preferredLanguage": "en-US",
      "redirectedPayment": {
        "merchantReturnUrl": "https://yoursite.com/payment-complete"
      }
    }
  },
  "accountHolder": {
    "fullName": "Jane Doe",
    "email": "jane.doe@email.com",
    "billingAddress": {
      "line1": "123 Main Street",
      "postalCode": "92126",
      "countryCode": "USA",
      "state": "CA",
      "city": "San Diego"
    }
  },
  "shipTo": {
    "fullName": "Jane Doe",
    "shippingAddress": {
      "line1": "123 Main Street",
      "postalCode": "92126",
      "countryCode": "USA",
      "state": "CA",
      "city": "San Diego"
    }
  }
}
```

### Google Pay Payment

```http
POST /payments
```

```json
{
  "captureMethod": "NOW",
  "amount": 100,
  "isAmountFinal": true,
  "currency": "USD",
  "initiatorType": "CARDHOLDER",
  "accountOnFile": "NOT_STORED",
  "merchant": {
    "merchantSoftware": {
      "companyName": "Your Company",
      "productName": "Your Product",
      "version": "2.0"
    },
    "merchantCategoryCode": 5945
  },
  "paymentMethodType": {
    "googlepay": {
      "latLong": "1,1",
      "encryptedPaymentBundle": {
        "encryptedPayload": "{encrypted-payload-from-google-pay-sdk}",
        "encryptedPaymentHeader": {
          "ephemeralPublicKey": "{ephemeral-public-key}"
        },
        "signature": "{signature}",
        "protocolVersion": "ECv1"
      }
    }
  }
}
```

### Consumer Profile Create (Card on File)

Create a consumer profile while processing a payment for future stored credential use:

```http
POST /payments
```

```json
{
  "captureMethod": "NOW",
  "amount": 100,
  "currency": "USD",
  "merchant": {
    "merchantSoftware": {
      "companyName": "Your Company",
      "productName": "Your Product",
      "version": "2.0"
    }
  },
  "paymentMethodType": {
    "card": {
      "accountNumber": "341134126510168",
      "expiry": {
        "month": 12,
        "year": 2027
      },
      "cvv": 4111
    }
  },
  "accountHolder": {
    "fullName": "Jane Doe",
    "billingAddress": {
      "line1": "123 Main Street",
      "city": "Tampa",
      "state": "FL",
      "postalCode": "33626"
    },
    "consumerProfileInfo": {
      "consumerProfileRequestType": "CREATE"
    }
  },
  "initiatorType": "CARDHOLDER",
  "accountOnFile": "TO_BE_STORED"
}
```

### Use Consumer Profile

Pay using a previously created consumer profile:

```http
POST /payments
```

```json
{
  "captureMethod": "NOW",
  "amount": 10000,
  "currency": "USD",
  "merchantOrderNumber": "1711500004",
  "merchant": {
    "merchantSoftware": {
      "companyName": "Your Company",
      "productName": "Your Product",
      "version": "2.0"
    }
  },
  "paymentMethodType": {
    "consumerProfile": {
      "consumerProfileId": "{consumer-profile-id}"
    }
  },
  "accountHolder": {
    "fullName": "Jane Doe",
    "billingAddress": {
      "line1": "123 Main Street",
      "city": "Tampa",
      "state": "FL",
      "postalCode": "33626"
    }
  },
  "initiatorType": "CARDHOLDER",
  "accountOnFile": "STORED",
  "isAmountFinal": true
}
```

### Safetech Fraud Check

Run a fraud score check before or instead of processing a payment:

```http
POST /fraudcheck
```

```json
{
  "amount": 10000,
  "currency": "USD",
  "fraudScore": {
    "cardholderBrowserInformation": "cardholderBrowserInformation",
    "isFraudRuleReturn": true,
    "sessionId": "unique-session-id",
    "fencibleItemAmount": 1230,
    "aNITelephoneNumber": "5131234567"
  },
  "accountHolder": {
    "deviceIPAddress": "127.0.0.1",
    "driverLicenseNumber": "T000-000-0000",
    "email": "customer@example.com",
    "fullName": "Jane Doe",
    "referenceId": "unique-reference-id",
    "consumerIdCreationDate": "2027-08-02",
    "phone": {
      "countryCode": 1,
      "phoneNumber": "8888888888"
    },
    "billingAddress": {
      "line1": "123 Main Street",
      "city": "Tampa",
      "state": "FL",
      "postalCode": "33626"
    }
  },
  "paymentMethodType": {
    "card": {
      "expiry": {
        "month": 12,
        "year": 2027
      },
      "cvv": 411,
      "accountNumber": "4777779999999990"
    }
  },
  "shipTo": {
    "shippingAddress": {
      "line1": "123 Main Street",
      "city": "Tampa",
      "state": "FL",
      "postalCode": "33626"
    },
    "shippingDescription": "C"
  },
  "merchant": {
    "merchantSoftware": {
      "companyName": "Your Company",
      "productName": "Your Product",
      "version": "2.0"
    }
  }
}
```

### Auth-Capture with Passthrough 3DS

Pass 3DS authentication results you obtained externally to the payment request:

```http
POST /payments
```

```json
{
  "captureMethod": "NOW",
  "amount": 54500,
  "currency": "EUR",
  "merchantOrderNumber": "1711500030",
  "merchant": {
    "merchantSoftware": {
      "companyName": "Your Company",
      "productName": "Your Product",
      "version": "2.0"
    }
  },
  "paymentMethodType": {
    "card": {
      "accountNumber": "5424184049821670",
      "expiry": {
        "month": 5,
        "year": 2027
      },
      "cvv": 123,
      "authentication": {
        "threeDS": {
          "authenticationTransactionId": "{3ds-auth-transaction-id}",
          "authenticationValue": "JAmi21makAifmwqo2120cjq1AAA="
        },
        "electronicCommerceIndicator": "05"
      }
    }
  },
  "accountHolder": {
    "fullName": "Jane Doe",
    "billingAddress": {
      "line1": "123 Main Street",
      "city": "Tampa",
      "state": "FL",
      "postalCode": "33626"
    }
  },
  "initiatorType": "CARDHOLDER",
  "accountOnFile": "NOT_STORED",
  "isAmountFinal": true
}
```

### Auth-Capture with Orchestrated 3DS

Let JPM orchestrate the 3DS authentication flow. Requires `browserInfo` and `paymentAuthenticationRequest`:

```http
POST /payments
```

```json
{
  "captureMethod": "NOW",
  "amount": 3000,
  "currency": "EUR",
  "isAmountFinal": true,
  "initiatorType": "CARDHOLDER",
  "paymentMethodType": {
    "card": {
      "accountNumber": "5112345112345114",
      "expiry": {
        "month": 5,
        "year": 2040
      },
      "cvv": "123",
      "paymentAuthenticationRequest": {
        "authenticationReturnUrl": "https://yoursite.com/3ds-postback",
        "authenticationSupportUrl": "https://yoursite.com/3ds-postback",
        "threeDSAccountAdditionalInfo": {
          "consumerAccountCreateLength": "NO_ACCOUNT",
          "consumerAccountCreateTimestamp": "2026-05-29T00:00:00Z",
          "consumerAccountUpdateLength": "CURRENT_TXN",
          "consumerAccountUpdateTimestamp": "2026-05-29T00:00:00Z",
          "consumerAccountPasswordUpdateTimestamp": "2026-05-29T00:00:00Z",
          "consumerAccountPasswordChangeLength": "NO_CHANGE",
          "consumerAccountShippingAddressLength": "CURRENT_TXN_CHANGE",
          "consumerAccountFirstShippingDate": "2026-05-29T00:00:00Z",
          "twentyFourHoursTransactionCount": 0,
          "previousYearTransactionCount": 0,
          "consumerAccount24HoursAddCardCount": 0,
          "sixMonthTransactionCount": 0,
          "consumerAccountSuspiciousActivityIndicator": true,
          "consumerAccountShipNameIdenticalIndicator": true,
          "consumerPaymentAccountLength": "NO_ACCOUNT",
          "consumerPaymentAccountEnrollmentDate": "2026-05-29T00:00:00Z",
          "consumerAccountAddressIdenticalIndicator": true
        },
        "threeDSRequestorAuthenticationInfo": {
          "threeDSAuthenticationTimestamp": "2026-05-29T00:00:00Z",
          "threeDSAuthenticationData": "",
          "threeDSChallengeType": "NO_CHALLENGE",
          "requestorAuthenticationMethod": "REQUESTOR_CRED",
          "authenticationPurpose": "PAYMENT_TRANSACTION"
        },
        "threeDSRequestorPriorAuthenticationInfo": {
          "priorAcsTransactionId": "VOGXpZvTlCmBUyPnnZfmsGDKqxRsRwPovkAE",
          "authenticationMethod": "FRICTIONLESS"
        },
        "threeDSPurchaseInfo": {
          "purchaseDate": "2026-05-29T00:00:00Z",
          "recurringAuthorizationDayCount": 0,
          "threeDomainSecureTransactionType": "CHECK"
        },
        "threeDSPurchaseRisk": {
          "shipmentType": "CARDHOLDER_ADDRESS",
          "deliveryTimeframe": "SAME_DAY",
          "orderEmailAddress": "",
          "productRepurchaseIndicator": true,
          "productAvailabilityCode": "AVAILABLE",
          "preOrderDate": "2026-05-29T00:00:00Z",
          "purchasedPrepaidCardTotalAmount": 0,
          "purchasedPrepaidCardCount": 0,
          "prepaidCardCurrency": "USD"
        }
      }
    }
  },
  "accountHolder": {
    "firstName": "Jane",
    "lastName": "Doe",
    "email": "jane.doe@example.com",
    "mobile": {
      "countryCode": 1,
      "phoneNumber": "8888888888"
    },
    "phone": {
      "countryCode": 1,
      "phoneNumber": "8888888888"
    },
    "billingAddress": {
      "line1": "123 Main Street",
      "city": "Tampa",
      "state": "FL",
      "countryCode": "USA",
      "postalCode": "33626"
    }
  },
  "merchant": {
    "merchantSoftware": {
      "companyName": "Your Company",
      "productName": "Your Product",
      "version": "2.0"
    }
  },
  "browserInfo": {
    "browserAcceptHeader": "application/json",
    "deviceIPAddress": "192.168.1.1",
    "browserLanguage": "en",
    "browserColorDepth": "8",
    "browserScreenHeight": "1",
    "browserScreenWidth": "1",
    "deviceLocalTimeZone": 1,
    "browserUserAgent": "Mozilla/5.0",
    "challengeWindowSize": "250_400",
    "javaEnabled": true,
    "javaScriptEnabled": true
  }
}
```

### Paze Payment (Bundle)

Process a Paze wallet payment using the encrypted bundle from the Paze SDK:

```http
POST /payments
```

```json
{
  "captureMethod": "NOW",
  "amount": 100000,
  "isAmountFinal": true,
  "currency": "USD",
  "initiatorType": "CARDHOLDER",
  "accountOnFile": "NOT_STORED",
  "merchant": {
    "merchantSoftware": {
      "companyName": "Your Company",
      "productName": "Your Product",
      "version": "2.0"
    }
  },
  "paymentMethodType": {
    "paze": {
      "encryptedPaymentBundle": {
        "encryptedPayload": "{encrypted-jwt-payload-from-paze-sdk}"
      }
    }
  }
}
```

### Paze CDPT (Card Data Passthrough)

Process a Paze payment using decrypted card data with device token:

```http
POST /payments
```

```json
{
  "captureMethod": "NOW",
  "amount": 2100,
  "currency": "USD",
  "merchant": {
    "merchantSoftware": {
      "companyName": "Your Company",
      "productName": "Your Product",
      "version": "2.0"
    }
  },
  "paymentMethodType": {
    "card": {
      "accountNumberType": "DEVICE_TOKEN",
      "accountNumber": "4559551252257141",
      "expiry": {
        "month": 1,
        "year": 2029
      },
      "walletProvider": "PAZE",
      "authentication": {
        "electronicCommerceIndicator": 5,
        "tokenAuthenticationValue": "AwAAAAAASNLECc0AAAAAgSYAAAA="
      }
    }
  },
  "accountHolder": {
    "firstName": "Jane",
    "lastName": "Doe",
    "fullName": "Jane Doe",
    "billingAddress": {
      "line1": "123 Main Street",
      "city": "Tampa",
      "state": "FL",
      "countryCode": "USA",
      "postalCode": "33626"
    }
  },
  "merchantOrderNumber": "1711500031",
  "initiatorType": "CARDHOLDER"
}
```

### Health Benefit Payment (HSA / IIAS)

Process a healthcare payment with Health Savings Account (HSA) or Inventory Information Approval System (IIAS) data:

```http
POST /payments
```

```json
{
  "captureMethod": "NOW",
  "amount": 10000,
  "currency": "USD",
  "retailAddenda": {
    "healthcareData": {
      "totalHealthcareAmount": 10000,
      "totalPrescriptionAmount": 10000,
      "isIIAS": true
    }
  },
  "initiatorType": "CARDHOLDER",
  "accountOnFile": "TO_BE_STORED",
  "merchantOrderNumber": "1711500032",
  "paymentMethodType": {
    "card": {
      "accountNumber": "4777779999999990",
      "expiry": {
        "month": 12,
        "year": 2027
      },
      "isBillPayment": false
    }
  },
  "accountHolder": {
    "fullName": "Jane Doe",
    "billingAddress": {
      "line1": "123 Main Street",
      "city": "Tampa",
      "state": "FL",
      "postalCode": "33626"
    }
  },
  "merchant": {
    "merchantSoftware": {
      "companyName": "Your Company",
      "productName": "Your Product",
      "version": "2.0"
    }
  },
  "partialAuthorizationSupport": "NOT_SUPPORTED",
  "isAmountFinal": false
}
```

### Using Safetech Token

Authorize using a Safetech token (tokenized card number) instead of a raw PAN:

```http
POST /payments
```

```json
{
  "captureMethod": "MANUAL",
  "amount": 10000,
  "currency": "USD",
  "merchantOrderNumber": "1711500033",
  "merchant": {
    "merchantSoftware": {
      "companyName": "Your Company",
      "productName": "Your Product",
      "version": "2.0"
    }
  },
  "paymentMethodType": {
    "card": {
      "accountNumberType": "SAFETECH_TOKEN",
      "accountNumber": "371144334284376",
      "expiry": {
        "month": 5,
        "year": 2027
      }
    }
  },
  "accountHolder": {
    "fullName": "Jane Doe",
    "billingAddress": {
      "line1": "123 Main Street",
      "city": "Tampa",
      "state": "FL",
      "postalCode": "33626"
    }
  },
  "initiatorType": "CARDHOLDER",
  "accountOnFile": "NOT_STORED",
  "isAmountFinal": true
}
```

### Using PIE (Page Encryption)

Authorize using Safetech Page Encryption to reduce PCI scope. The encrypted card data comes from the client-side PIE JavaScript library:

```http
POST /payments
```

```json
{
  "captureMethod": "MANUAL",
  "amount": 100,
  "currency": "USD",
  "merchant": {
    "merchantSoftware": {
      "companyName": "Your Company",
      "productName": "Your Product",
      "version": "2.0"
    }
  },
  "paymentMethodType": {
    "card": {
      "accountNumberType": "SAFETECH_PAGE_ENCRYPTION",
      "accountNumber": "{pie-encrypted-account-number}",
      "cvv": "{pie-encrypted-cvv}",
      "encryptionIntegrityCheck": "{integrity-check-value}",
      "expiry": {
        "month": 5,
        "year": 2040
      }
    }
  },
  "initiatorType": "CARDHOLDER",
  "accountOnFile": "NOT_STORED",
  "isAmountFinal": true,
  "accountHolder": {
    "fullName": "Jane Doe",
    "billingAddress": {
      "line1": "123 Main Street",
      "city": "Tampa",
      "state": "FL",
      "postalCode": "33626"
    }
  }
}
```

### Soft & Sub Merchant

Payment with soft merchant descriptor and sub-merchant supplemental data (for payment facilitators / marketplaces):

```http
POST /payments
```

```json
{
  "captureMethod": "MANUAL",
  "amount": 1550,
  "currency": "USD",
  "statementDescriptor": "Marketplace Purchase",
  "initiatorType": "CARDHOLDER",
  "accountOnFile": "STORED",
  "paymentMethodType": {
    "card": {
      "accountNumber": "4444444444444448",
      "expiry": {
        "month": 12,
        "year": 2027
      },
      "cvv": 111
    }
  },
  "recurring": {
    "recurringSequence": "FIRST"
  },
  "merchant": {
    "merchantSoftware": {
      "companyName": "Your Company",
      "productName": "Your Product",
      "version": "2.0"
    },
    "merchantCategoryCode": "5945",
    "softMerchant": {
      "name": "Sub Merchant Name",
      "phone": "8135551234",
      "email": "submerchant@example.com",
      "url": "payments.jpmorgan.com",
      "address": {
        "line1": "123 Main Street",
        "city": "Tampa",
        "state": "FL",
        "countryCode": "USA",
        "postalCode": "33626"
      },
      "merchantPurchaseDescription": "Digital goods purchase"
    }
  },
  "subMerchantSupplementalData": {
    "merchantIdentification": {
      "sellerIdentifier": "SELLER123",
      "serviceEntitlementNumber": "SEN456",
      "subMerchantId": "SUB789"
    }
  }
}
```

### Pinless Debit

Process a PINless debit card transaction (used for bill payments and ecommerce on debit networks):

```http
POST /payments
```

```json
{
  "captureMethod": "MANUAL",
  "amount": 10000,
  "currency": "USD",
  "statementDescriptor": "pulse-merchant",
  "initiatorType": "CARDHOLDER",
  "accountOnFile": "STORED",
  "paymentMethodType": {
    "card": {
      "accountNumber": "4935550000000006",
      "expiry": {
        "month": 12,
        "year": 2027
      },
      "cvv": 411
    }
  },
  "accountHolder": {
    "fullName": "Jane Doe",
    "billingAddress": {
      "line1": "123 Main Street",
      "city": "Tampa",
      "state": "FL",
      "postalCode": "33626"
    }
  },
  "merchant": {
    "merchantSoftware": {
      "companyName": "Your Company",
      "productName": "Your Product",
      "version": "2.0"
    }
  }
}
```

### Partial Authorization

Request where partial authorization is supported (e.g., prepaid card with insufficient balance):

```http
POST /payments
```

```json
{
  "captureMethod": "NOW",
  "amount": 10000,
  "currency": "USD",
  "merchantOrderNumber": "1711500034",
  "merchant": {
    "merchantSoftware": {
      "companyName": "Your Company",
      "productName": "Your Product",
      "version": "2.0"
    }
  },
  "paymentMethodType": {
    "card": {
      "accountNumber": "5555555555555565",
      "expiry": {
        "month": 5,
        "year": 2027
      },
      "cvv": 411
    }
  },
  "accountHolder": {
    "fullName": "Jane Doe",
    "billingAddress": {
      "line1": "123 Main Street",
      "city": "Tampa",
      "state": "FL",
      "postalCode": "33626"
    }
  },
  "partialAuthorizationSupport": "SUPPORTED"
}
```

### Delayed Capture

Authorization with delayed auto-capture at settlement time:

```http
POST /payments
```

```json
{
  "captureMethod": "DELAYED",
  "amount": 10000,
  "currency": "USD",
  "merchantOrderNumber": "1711500035",
  "merchant": {
    "merchantSoftware": {
      "companyName": "Your Company",
      "productName": "Your Product",
      "version": "2.0"
    }
  },
  "paymentMethodType": {
    "card": {
      "accountNumber": "371144371144376",
      "expiry": {
        "month": 5,
        "year": 2027
      },
      "cvv": 4111
    }
  },
  "accountHolder": {
    "fullName": "Jane Doe",
    "billingAddress": {
      "line1": "123 Main Street",
      "city": "Tampa",
      "state": "FL",
      "postalCode": "33626"
    }
  },
  "initiatorType": "CARDHOLDER",
  "accountOnFile": "NOT_STORED",
  "isAmountFinal": true
}
```

### Network Tokens

Use a network token (DPAN) instead of the raw PAN. Available for Visa, Mastercard, and Amex. The `accountNumberType` must be `NETWORK_TOKEN`, and CIT transactions require `authentication` with a `tokenAuthenticationValue` (cryptogram).

**CIT with Network Token (Visa):**

```http
POST /payments
```

```json
{
  "captureMethod": "NOW",
  "amount": 10000,
  "currency": "USD",
  "merchantOrderNumber": "1711500040",
  "merchant": {
    "merchantSoftware": {
      "companyName": "Your Company",
      "productName": "Your Product",
      "version": "2.0"
    }
  },
  "paymentMethodType": {
    "card": {
      "accountNumberType": "NETWORK_TOKEN",
      "accountNumber": "4761220000000237",
      "expiry": {
        "month": 5,
        "year": 2027
      },
      "authentication": {
        "electronicCommerceIndicator": "7",
        "tokenAuthenticationValue": "BwAQADQFcAEAABNZIAVwEMO4oio="
      }
    }
  },
  "initiatorType": "CARDHOLDER",
  "accountOnFile": "STORED"
}
```

**MIT with Network Token (Visa):**

```json
{
  "captureMethod": "NOW",
  "amount": 10000,
  "currency": "USD",
  "merchantOrderNumber": "1711500041",
  "merchant": {
    "merchantSoftware": {
      "companyName": "Your Company",
      "productName": "Your Product",
      "version": "2.0"
    }
  },
  "paymentMethodType": {
    "card": {
      "accountNumberType": "NETWORK_TOKEN",
      "accountNumber": "4761220000000237",
      "originalNetworkTransactionId": "{networkTransactionId-from-initial-CIT}",
      "expiry": {
        "month": 5,
        "year": 2027
      }
    }
  },
  "initiatorType": "MERCHANT",
  "accountOnFile": "STORED"
}
```

**MIT Recurring with Network Token (Visa):**

```json
{
  "captureMethod": "NOW",
  "amount": 10000,
  "currency": "USD",
  "merchantOrderNumber": "1711500042",
  "merchant": {
    "merchantSoftware": {
      "companyName": "Your Company",
      "productName": "Your Product",
      "version": "2.0"
    }
  },
  "paymentMethodType": {
    "card": {
      "accountNumberType": "NETWORK_TOKEN",
      "accountNumber": "4761220000000237",
      "originalNetworkTransactionId": "{networkTransactionId-from-initial-CIT}",
      "expiry": {
        "month": 5,
        "year": 2027
      }
    }
  },
  "initiatorType": "MERCHANT",
  "accountOnFile": "STORED",
  "recurring": {
    "recurringSequence": "SUBSEQUENT"
  }
}
```

> **Note:** For Amex CIT, include `cvv` (4-digit) and `electronicCommerceIndicator: "7"` without `tokenAuthenticationValue`. For Mastercard and Visa CIT, include the `tokenAuthenticationValue` cryptogram.

### Device Tokens

Use a device token (e.g., from Apple Pay or Google Pay tokenized in-app). Set `accountNumberType` to `DEVICE_TOKEN`:

**CIT with Device Token:**

```json
{
  "captureMethod": "NOW",
  "amount": 10000,
  "currency": "USD",
  "merchantOrderNumber": "1711500043",
  "merchant": {
    "merchantSoftware": {
      "companyName": "Your Company",
      "productName": "Your Product",
      "version": "2.0"
    }
  },
  "paymentMethodType": {
    "card": {
      "accountNumberType": "DEVICE_TOKEN",
      "accountNumber": "6011016011016011",
      "expiry": {
        "month": 5,
        "year": 2027
      },
      "authentication": {
        "electronicCommerceIndicator": "7",
        "tokenAuthenticationValue": "BwAQADQFcAEAABNZIAVwEMO4oio="
      }
    }
  },
  "initiatorType": "CARDHOLDER",
  "accountOnFile": "STORED"
}
```

**MIT with Device Token:**

```json
{
  "captureMethod": "NOW",
  "amount": 10000,
  "currency": "USD",
  "merchantOrderNumber": "1711500044",
  "merchant": {
    "merchantSoftware": {
      "companyName": "Your Company",
      "productName": "Your Product",
      "version": "2.0"
    }
  },
  "paymentMethodType": {
    "card": {
      "accountNumberType": "DEVICE_TOKEN",
      "accountNumber": "373953192351004",
      "originalNetworkTransactionId": "{networkTransactionId-from-initial-CIT}",
      "expiry": {
        "month": 5,
        "year": 2027
      }
    }
  },
  "initiatorType": "MERCHANT",
  "accountOnFile": "STORED"
}
```

### Real-Time Account Updater (RTAU)

Request updated card details (new account number or expiry) in real-time with a payment. Add `accountUpdater.requestAccountUpdater: true` to the card object. Requires `merchantCategoryCode` on the merchant:

```http
POST /payments
```

```json
{
  "captureMethod": "NOW",
  "amount": 1000,
  "currency": "USD",
  "initiatorType": "CARDHOLDER",
  "accountOnFile": "STORED",
  "merchant": {
    "merchantSoftware": {
      "companyName": "Your Company",
      "productName": "Your Product",
      "version": "2.0"
    },
    "merchantCategoryCode": "5945"
  },
  "paymentMethodType": {
    "card": {
      "accountNumberType": "PAN",
      "accountNumber": "4112344112344113",
      "expiry": {
        "month": 5,
        "year": 2027
      },
      "cvv": 411,
      "accountUpdater": {
        "requestAccountUpdater": true
      }
    }
  },
  "accountHolder": {
    "email": "jane.doe@example.com",
    "phone": {
      "phoneNumber": "8888888888"
    },
    "billingAddress": {
      "line1": "123 Main Street",
      "line2": "Apt 4B",
      "state": "FL",
      "city": "Tampa",
      "postalCode": "33626",
      "countryCode": "USA"
    },
    "firstName": "Jane",
    "lastName": "Doe"
  }
}
```

> **RTAU responses** return updated card info in `paymentMethodType.card.accountUpdater` with fields like `accountUpdaterStatus` (`NEW_ACCOUNT`, `NEW_EXPIRY`, `NEW_ACCOUNT_AND_EXPIRY`, `MATCH_NO_UPDATE`, `CONTACT_CARDHOLDER`, `CLOSED_ACCOUNT`), `updatedAccountNumber`, and `updatedExpiry`.

### Carte Bancaire (CB MOP)

French domestic card network routing. Add `preferredPaymentNetworkRoutingCode: "CB"` and `preferredRoutingInitiatorCode` to route through the CB network:

```http
POST /payments
```

```json
{
  "captureMethod": "NOW",
  "amount": 5000,
  "currency": "EUR",
  "merchantOrderNumber": "1711500050",
  "merchant": {
    "merchantSoftware": {
      "companyName": "Your Company",
      "productName": "Your Product",
      "version": "2.0"
    }
  },
  "paymentMethodType": {
    "card": {
      "accountNumber": "5341027900000001",
      "expiry": {
        "month": 4,
        "year": 2026
      },
      "cvv": 123,
      "preferredPaymentNetworkRoutingCode": "CB",
      "preferredRoutingInitiatorCode": "CONSUMER"
    }
  },
  "accountHolder": {
    "fullName": "Jane Doe",
    "billingAddress": {
      "line1": "123 Main Street",
      "city": "Paris",
      "state": "IDF",
      "postalCode": "75001"
    }
  },
  "isAmountFinal": true
}
```

**CB MOP with MIT (subsequent recurring):**

```json
{
  "captureMethod": "NOW",
  "amount": 5000,
  "currency": "EUR",
  "initiatorType": "MERCHANT",
  "accountOnFile": "STORED",
  "isAmountFinal": true,
  "merchant": {
    "merchantSoftware": {
      "companyName": "Your Company",
      "productName": "Your Product",
      "version": "2.0"
    }
  },
  "recurring": {
    "recurringSequence": "SUBSEQUENT",
    "recurringNumber": 2
  },
  "paymentMethodType": {
    "card": {
      "originalNetworkTransactionId": "{networkTransactionId-from-initial-CIT}",
      "accountNumber": "4347214204298088",
      "expiry": {
        "month": 5,
        "year": 2025
      },
      "cvv": 123,
      "isBillPayment": true,
      "preferredPaymentNetworkRoutingCode": "CB",
      "preferredRoutingInitiatorCode": "MERCHANT"
    }
  },
  "merchantOrderNumber": "1711500051",
  "accountHolder": {
    "referenceId": "customer-reference-id"
  }
}
```

---

## Stored Credentials: CIT / MIT Reference

Stored credential transactions use a combination of `initiatorType`, `accountOnFile`, `recurring`, `isAmountFinal`, and `authorizationPurpose` fields to indicate who initiated the transaction and how credentials are being used. Getting these fields right is critical for proper network compliance (Visa, Mastercard, Discover, etc.).

### Key Fields

| Field | Values | Description |
|---|---|---|
| `initiatorType` | `CARDHOLDER`, `MERCHANT` | Who initiated the transaction |
| `accountOnFile` | `NOT_STORED`, `TO_BE_STORED`, `STORED` | Credential storage state |
| `recurring.recurringSequence` | `FIRST`, `SUBSEQUENT` | Position in a recurring series |
| `isAmountFinal` | `true`, `false` | Whether the authorized amount is final |
| `authorizationPurpose` | `DELAYED_CHARGE`, `NO_SHOW`, `RESUBMISSION`, `REAUTHORIZATION` | Special MIT authorization purposes |
| `recurring.isVariableAmount` | `true`, `false` | Whether amount varies per billing cycle (Mastercard CREV/MREV) |

### CIT/MIT Decision Flow

``` mermaid
flowchart TD
    A["Payment Request"] --> B{Who initiates?}
    B -->|Cardholder present / active| C["initiatorType: CARDHOLDER"]
    B -->|Merchant / system / background| D["initiatorType: MERCHANT"]

    C --> E{Storing credentials?}
    E -->|Not storing| F["accountOnFile: NOT_STORED\n→ CGEN"]
    E -->|First time storing| G{Recurring?}
    E -->|Already stored| H{Recurring?}

    G -->|No| I["accountOnFile: TO_BE_STORED\n→ CSTO"]
    G -->|First in series| J["accountOnFile: TO_BE_STORED\nrecurringSequence: FIRST\n→ CREC"]
    G -->|Variable amount MC| J2["accountOnFile: TO_BE_STORED\nrecurringSequence: FIRST\nisVariableAmount: true\n→ CREV"]

    H -->|No, one-time use| K{Amount final?}
    H -->|First in new series| L["accountOnFile: STORED\nrecurringSequence: FIRST\n→ CREC"]
    H -->|Subsequent in series| M["accountOnFile: STORED\nrecurringSequence: SUBSEQUENT\n→ CUSE"]

    K -->|Yes| N["accountOnFile: STORED\n→ CUSE"]
    K -->|No — estimated| O["accountOnFile: STORED\nisAmountFinal: false\n→ CEST"]

    D --> P{Purpose?}
    P -->|Unscheduled charge| Q["accountOnFile: STORED\n→ MUSE"]
    P -->|Subsequent recurring| R["accountOnFile: STORED\nrecurringSequence: SUBSEQUENT\n→ MREC"]
    P -->|Variable recurring MC| R2["accountOnFile: STORED\nrecurringSequence: SUBSEQUENT\nisVariableAmount: true\n→ MREV"]
    P -->|Delayed charge| S["accountOnFile: STORED\nauthorizationPurpose: DELAYED_CHARGE\n→ MDEL"]
    P -->|No show| T["accountOnFile: STORED\nauthorizationPurpose: NO_SHOW\n→ MNOS"]
    P -->|Resubmission| U["accountOnFile: STORED\nauthorizationPurpose: RESUBMISSION\n→ MRSB"]
    P -->|Reauthorization| V["accountOnFile: STORED\nauthorizationPurpose: REAUTHORIZATION\n→ MRAU"]
```

---

### Cardholder-Initiated Transactions (CIT)

#### CGEN — One-time purchase, credentials not stored

> Cardholder places an order for a one-time transaction and chooses not to store credentials.

```json
{
  "captureMethod": "NOW",
  "amount": 100,
  "currency": "USD",
  "merchantOrderNumber": "1711500010",
  "merchant": {
    "merchantSoftware": {
      "companyName": "Your Company",
      "productName": "Your Product",
      "version": "2.0"
    }
  },
  "paymentMethodType": {
    "card": {
      "accountNumberType": "PAN",
      "accountNumber": "4055018101463717",
      "expiry": { "month": 5, "year": 2027 },
      "cvv": 411
    }
  },
  "accountHolder": {
    "fullName": "Jane Doe",
    "billingAddress": {
      "line1": "123 Main Street",
      "city": "Tampa",
      "state": "FL",
      "postalCode": "33626"
    }
  },
  "initiatorType": "CARDHOLDER",
  "accountOnFile": "NOT_STORED",
  "isAmountFinal": true
}
```

#### CSTO — First purchase, storing credentials for future use

> Cardholder places an order and chooses to store their credentials for the first time.

```json
{
  "captureMethod": "NOW",
  "amount": 100,
  "currency": "USD",
  "merchantOrderNumber": "1711500011",
  "merchant": {
    "merchantSoftware": {
      "companyName": "Your Company",
      "productName": "Your Product",
      "version": "2.0"
    }
  },
  "paymentMethodType": {
    "card": {
      "accountNumberType": "PAN",
      "accountNumber": "4055018101463717",
      "expiry": { "month": 5, "year": 2027 },
      "cvv": 411
    }
  },
  "accountHolder": {
    "fullName": "Jane Doe",
    "billingAddress": {
      "line1": "123 Main Street",
      "city": "Tampa",
      "state": "FL",
      "postalCode": "33626"
    }
  },
  "initiatorType": "CARDHOLDER",
  "accountOnFile": "TO_BE_STORED"
}
```

#### CREC — First in a recurring series, storing credentials

> Cardholder signs up for recurring payments and stores credentials for the first time.

```json
{
  "captureMethod": "NOW",
  "amount": 100,
  "currency": "USD",
  "merchantOrderNumber": "1711500012",
  "merchant": {
    "merchantSoftware": {
      "companyName": "Your Company",
      "productName": "Your Product",
      "version": "2.0"
    }
  },
  "paymentMethodType": {
    "card": {
      "accountNumberType": "PAN",
      "accountNumber": "4055018101463717",
      "expiry": { "month": 5, "year": 2027 },
      "cvv": 411
    }
  },
  "accountHolder": {
    "fullName": "Jane Doe",
    "billingAddress": {
      "line1": "123 Main Street",
      "city": "Tampa",
      "state": "FL",
      "postalCode": "33626"
    }
  },
  "initiatorType": "CARDHOLDER",
  "accountOnFile": "TO_BE_STORED",
  "recurring": {
    "recurringSequence": "FIRST"
  }
}
```

Also applies when cardholder logs in and starts a new recurring series with already-stored credentials — use `accountOnFile: "STORED"` instead.

#### CUSE — Using previously stored credentials

> Cardholder logs into their account and uses credentials previously stored on file.

```json
{
  "captureMethod": "NOW",
  "amount": 100,
  "currency": "USD",
  "merchantOrderNumber": "1711500013",
  "merchant": {
    "merchantSoftware": {
      "companyName": "Your Company",
      "productName": "Your Product",
      "version": "2.0"
    }
  },
  "paymentMethodType": {
    "card": {
      "accountNumberType": "PAN",
      "accountNumber": "4055018101463717",
      "expiry": { "month": 5, "year": 2027 },
      "cvv": 411
    }
  },
  "accountHolder": {
    "fullName": "Jane Doe",
    "billingAddress": {
      "line1": "123 Main Street",
      "city": "Tampa",
      "state": "FL",
      "postalCode": "33626"
    }
  },
  "initiatorType": "CARDHOLDER",
  "accountOnFile": "STORED"
}
```

Also applies when a cardholder's recurring card was declined, the issue is resolved, and the cardholder logs back in to reprocess using the stored credential.

#### CEST — Estimated amount, using stored credentials

> Cardholder uses stored credentials for a purchase where the final amount is not yet known.

```json
{
  "captureMethod": "MANUAL",
  "amount": 10000,
  "currency": "USD",
  "merchantOrderNumber": "1711500014",
  "merchant": {
    "merchantSoftware": {
      "companyName": "Your Company",
      "productName": "Your Product",
      "version": "2.0"
    }
  },
  "paymentMethodType": {
    "card": {
      "accountNumberType": "PAN",
      "accountNumber": "4055018101463717",
      "expiry": { "month": 5, "year": 2027 },
      "cvv": 411
    }
  },
  "accountHolder": {
    "fullName": "Jane Doe",
    "billingAddress": {
      "line1": "123 Main Street",
      "city": "Tampa",
      "state": "FL",
      "postalCode": "33626"
    }
  },
  "initiatorType": "CARDHOLDER",
  "accountOnFile": "STORED",
  "isAmountFinal": false
}
```

#### CREV — Variable-amount recurring, first in series (Mastercard only)

> Cardholder stores credentials for a recurring subscription where the amount may vary cycle to cycle (e.g., utilities). Mastercard only.

```json
{
  "captureMethod": "NOW",
  "amount": 10000,
  "currency": "USD",
  "merchantOrderNumber": "1711500015",
  "merchant": {
    "merchantSoftware": {
      "companyName": "Your Company",
      "productName": "Your Product",
      "version": "2.0"
    }
  },
  "paymentMethodType": {
    "card": {
      "accountNumberType": "PAN",
      "accountNumber": "5111001521851777",
      "expiry": { "month": 5, "year": 2027 },
      "cvv": 411
    }
  },
  "accountHolder": {
    "fullName": "Jane Doe",
    "billingAddress": {
      "line1": "123 Main Street",
      "city": "Tampa",
      "state": "FL",
      "postalCode": "33626"
    }
  },
  "recurring": {
    "recurringSequence": "FIRST",
    "agreementId": "agreement-12345",
    "isVariableAmount": true
  },
  "initiatorType": "CARDHOLDER",
  "accountOnFile": "TO_BE_STORED"
}
```

---

### Merchant-Initiated Transactions (MIT)

> **Important:** For all merchant-initiated transactions, `accountOnFile` must be `STORED`. For Visa transactions, `originalNetworkTransactionId` is required (obtained from the initial cardholder-initiated transaction response at `paymentMethodType.card.networkResponse.networkTransactionId`).

#### MUSE — Unscheduled merchant-initiated charge

> Merchant charges a stored credential for an unscheduled reason (e.g., account top-up, threshold-based billing).

```json
{
  "captureMethod": "NOW",
  "amount": 10000,
  "currency": "USD",
  "merchantOrderNumber": "1711500020",
  "merchant": {
    "merchantSoftware": {
      "companyName": "Your Company",
      "productName": "Your Product",
      "version": "2.0"
    }
  },
  "paymentMethodType": {
    "card": {
      "accountNumberType": "PAN",
      "accountNumber": "4055018101463717",
      "originalNetworkTransactionId": "{networkTransactionId-from-initial-CIT}",
      "expiry": { "month": 5, "year": 2027 },
      "cvv": 411
    }
  },
  "accountHolder": {
    "fullName": "Jane Doe",
    "billingAddress": {
      "line1": "123 Main Street",
      "city": "Tampa",
      "state": "FL",
      "postalCode": "33626"
    }
  },
  "initiatorType": "MERCHANT",
  "accountOnFile": "STORED"
}
```

#### MREC — Subsequent recurring charge

> Merchant processes a subsequent recurring or installment transaction.

```json
{
  "captureMethod": "NOW",
  "amount": 100,
  "currency": "USD",
  "merchantOrderNumber": "1711500021",
  "merchant": {
    "merchantSoftware": {
      "companyName": "Your Company",
      "productName": "Your Product",
      "version": "2.0"
    }
  },
  "paymentMethodType": {
    "card": {
      "accountNumberType": "PAN",
      "accountNumber": "4055018101463717",
      "originalNetworkTransactionId": "{networkTransactionId-from-initial-CIT}",
      "expiry": { "month": 5, "year": 2027 },
      "cvv": 411
    }
  },
  "accountHolder": {
    "fullName": "Jane Doe",
    "billingAddress": {
      "line1": "123 Main Street",
      "city": "Tampa",
      "state": "FL",
      "postalCode": "33626"
    }
  },
  "initiatorType": "MERCHANT",
  "accountOnFile": "STORED",
  "recurring": {
    "recurringSequence": "SUBSEQUENT"
  }
}
```

#### MREV — Variable-amount recurring, subsequent (Mastercard only)

> Merchant processes a subsequent recurring charge where the amount varies (e.g., utilities billing). Mastercard only.

```json
{
  "captureMethod": "NOW",
  "amount": 10000,
  "currency": "USD",
  "merchantOrderNumber": "1711500022",
  "merchant": {
    "merchantSoftware": {
      "companyName": "Your Company",
      "productName": "Your Product",
      "version": "2.0"
    }
  },
  "paymentMethodType": {
    "card": {
      "accountNumber": "5111001521851777",
      "originalNetworkTransactionId": "{networkTransactionId-from-initial-CIT}",
      "expiry": { "month": 5, "year": 2027 },
      "cvv": 411
    }
  },
  "accountHolder": {
    "fullName": "Jane Doe",
    "billingAddress": {
      "line1": "123 Main Street",
      "city": "Tampa",
      "state": "FL",
      "postalCode": "33626"
    }
  },
  "recurring": {
    "recurringSequence": "SUBSEQUENT",
    "isVariableAmount": true
  },
  "initiatorType": "MERCHANT",
  "accountOnFile": "STORED"
}
```

#### MDEL — Delayed charge

> Cardholder has recurring payments and asks the merchant to delay billing. The merchant processes the delayed charge later.

```json
{
  "captureMethod": "NOW",
  "amount": 10000,
  "currency": "USD",
  "merchantOrderNumber": "1711500023",
  "merchant": {
    "merchantSoftware": {
      "companyName": "Your Company",
      "productName": "Your Product",
      "version": "2.0"
    }
  },
  "paymentMethodType": {
    "card": {
      "accountNumberType": "PAN",
      "accountNumber": "4055018101463717",
      "originalNetworkTransactionId": "{networkTransactionId-from-initial-CIT}",
      "expiry": { "month": 5, "year": 2027 },
      "cvv": 411
    }
  },
  "accountHolder": {
    "fullName": "Jane Doe",
    "billingAddress": {
      "line1": "123 Main Street",
      "city": "Tampa",
      "state": "FL",
      "postalCode": "33626"
    }
  },
  "initiatorType": "MERCHANT",
  "accountOnFile": "STORED",
  "authorizationPurpose": "DELAYED_CHARGE"
}
```

#### MNOS — No-show charge

> Cardholder had a scheduled appointment or reservation and did not show up. Merchant charges a no-show fee.

```json
{
  "captureMethod": "NOW",
  "amount": 10000,
  "currency": "USD",
  "merchantOrderNumber": "1711500024",
  "merchant": {
    "merchantSoftware": {
      "companyName": "Your Company",
      "productName": "Your Product",
      "version": "2.0"
    }
  },
  "paymentMethodType": {
    "card": {
      "accountNumberType": "PAN",
      "accountNumber": "4055018101463717",
      "originalNetworkTransactionId": "{networkTransactionId-from-initial-CIT}",
      "expiry": { "month": 5, "year": 2027 },
      "cvv": 411
    }
  },
  "accountHolder": {
    "fullName": "Jane Doe",
    "billingAddress": {
      "line1": "123 Main Street",
      "city": "Tampa",
      "state": "FL",
      "postalCode": "33626"
    }
  },
  "initiatorType": "MERCHANT",
  "accountOnFile": "STORED",
  "authorizationPurpose": "NO_SHOW"
}
```

#### MRSB — Resubmission

> Merchant received a decline due to insufficient funds after already shipping goods. Merchant resubmits at a later point.

```json
{
  "captureMethod": "NOW",
  "amount": 10000,
  "currency": "USD",
  "merchantOrderNumber": "1711500025",
  "merchant": {
    "merchantSoftware": {
      "companyName": "Your Company",
      "productName": "Your Product",
      "version": "2.0"
    }
  },
  "paymentMethodType": {
    "card": {
      "accountNumberType": "PAN",
      "accountNumber": "4055018101463717",
      "originalNetworkTransactionId": "{networkTransactionId-from-initial-CIT}",
      "expiry": { "month": 5, "year": 2027 },
      "cvv": 411
    }
  },
  "accountHolder": {
    "fullName": "Jane Doe",
    "billingAddress": {
      "line1": "123 Main Street",
      "city": "Tampa",
      "state": "FL",
      "postalCode": "33626"
    }
  },
  "initiatorType": "MERCHANT",
  "accountOnFile": "STORED",
  "authorizationPurpose": "RESUBMISSION"
}
```

#### MRAU — Reauthorization

> Merchant needs to reauthorize a transaction (e.g., original authorization expired due to multiple shipments on a single order).

```json
{
  "captureMethod": "NOW",
  "amount": 10000,
  "currency": "USD",
  "merchantOrderNumber": "1711500026",
  "merchant": {
    "merchantSoftware": {
      "companyName": "Your Company",
      "productName": "Your Product",
      "version": "2.0"
    }
  },
  "paymentMethodType": {
    "card": {
      "accountNumberType": "PAN",
      "accountNumber": "4055018101463717",
      "originalNetworkTransactionId": "{networkTransactionId-from-initial-CIT}",
      "expiry": { "month": 5, "year": 2027 },
      "cvv": 411
    }
  },
  "accountHolder": {
    "fullName": "Jane Doe",
    "billingAddress": {
      "line1": "123 Main Street",
      "city": "Tampa",
      "state": "FL",
      "postalCode": "33626"
    }
  },
  "initiatorType": "MERCHANT",
  "accountOnFile": "STORED",
  "authorizationPurpose": "REAUTHORIZATION"
}
```

---

### CIT/MIT Quick Reference Table

#### Cardholder-Initiated Transactions

| Use Case | `initiatorType` | `accountOnFile` | `recurringSequence` | `isAmountFinal` | Message Type |
|---|---|---|---|---|---|
| One-time purchase, not storing credentials | `CARDHOLDER` | `NOT_STORED` | — | `true` | CGEN |
| First purchase, storing credentials | `CARDHOLDER` | `TO_BE_STORED` | — | `true` | CSTO |
| First recurring, storing credentials | `CARDHOLDER` | `TO_BE_STORED` | `FIRST` | `true` | CREC |
| First variable recurring (MC only) | `CARDHOLDER` | `TO_BE_STORED` | `FIRST` | — | CREV |
| Using stored credential, one-time | `CARDHOLDER` | `STORED` | — | `true` | CUSE |
| Stored credential, new recurring series | `CARDHOLDER` | `STORED` | `FIRST` | `true`/`false` | CREC |
| Stored credential, subsequent recurring | `CARDHOLDER` | `STORED` | `SUBSEQUENT` | `true` | CUSE |
| Stored credential, estimated amount | `CARDHOLDER` | `STORED` | — | `false` | CEST |
| Installment (first) | `CARDHOLDER` | `STORED` | — | — | CINS |

#### Merchant-Initiated Transactions

| Use Case | `initiatorType` | `accountOnFile` | `recurringSequence` | `authorizationPurpose` | Message Type |
|---|---|---|---|---|---|
| Unscheduled charge | `MERCHANT` | `STORED` | — | — | MUSE |
| Subsequent recurring | `MERCHANT` | `STORED` | `SUBSEQUENT` | — | MREC |
| Variable recurring (MC only) | `MERCHANT` | `STORED` | `SUBSEQUENT` | — | MREV |
| Delayed charge | `MERCHANT` | `STORED` | — | `DELAYED_CHARGE` | MDEL |
| No-show | `MERCHANT` | `STORED` | — | `NO_SHOW` | MNOS |
| Resubmission | `MERCHANT` | `STORED` | — | `RESUBMISSION` | MRSB |
| Reauthorization | `MERCHANT` | `STORED` | — | `REAUTHORIZATION` | MRAU |
| Incremental auth | (system) | — | — | — | MINC |

### CIT/MIT Validation Rules

- **Cardholder + Recurring:** `accountOnFile` cannot be `NOT_STORED` — it must be `TO_BE_STORED` or `STORED`.
- **Merchant initiated:** `accountOnFile` must be `STORED`.
- **Visa MIT:** `originalNetworkTransactionId` is required on the card object.
- **Discover token MIT (MREC):** `originalNetworkTransactionId` is required.
- **Incremental auth (MINC):** The initial authorization should be `CARDHOLDER`-initiated with `isAmountFinal: false`. The increment is sent via `PATCH /payments/{transactionId}`.
- **Variable amount recurring (CREV/MREV):** Mastercard only. Set `recurring.isVariableAmount: true` and include `recurring.agreementId`.

---

### Common CIT/MIT Workflows

#### Workflow 1: Subscription sign-up → recurring billing

``` mermaid
sequenceDiagram
    participant CH as Cardholder
    participant M as Merchant
    participant API as Online Payments API

    CH->>M: Signs up for subscription
    M->>API: POST /payments (CREC: CARDHOLDER, TO_BE_STORED, FIRST)
    API-->>M: transactionId + networkTransactionId
    Note over M: Store networkTransactionId for future MIT

    loop Monthly billing
        M->>API: POST /payments (MREC: MERCHANT, STORED, SUBSEQUENT + networkTransactionId)
        API-->>M: transactionId
    end
```

#### Workflow 2: Card on file → cardholder reuse

``` mermaid
sequenceDiagram
    participant CH as Cardholder
    participant M as Merchant
    participant API as Online Payments API

    CH->>M: First purchase, opts to save card
    M->>API: POST /payments (CSTO: CARDHOLDER, TO_BE_STORED)
    API-->>M: transactionId

    CH->>M: Returns later, uses saved card
    M->>API: POST /payments (CUSE: CARDHOLDER, STORED)
    API-->>M: transactionId
```

#### Workflow 3: Recurring decline → cardholder re-initiates

``` mermaid
sequenceDiagram
    participant CH as Cardholder
    participant M as Merchant
    participant API as Online Payments API

    M->>API: POST /payments (MREC: MERCHANT, STORED, SUBSEQUENT)
    API-->>M: Decline (insufficient funds)
    M->>CH: Notification: card declined

    Note over CH: Resolves issue with card issuer

    CH->>M: Logs in, reprocesses payment
    M->>API: POST /payments (CUSE: CARDHOLDER, STORED)
    API-->>M: Approved
```

#### Workflow 4: Card verification → then recurring billing

``` mermaid
sequenceDiagram
    participant CH as Cardholder
    participant M as Merchant
    participant API as Online Payments API

    CH->>M: Signs up, adds card for future billing
    M->>API: POST /payments (amount: 0, CARDHOLDER, TO_BE_STORED) — Verification
    API-->>M: Verified + networkTransactionId
    Note over M: Card verified, no funds held

    loop Monthly billing
        M->>API: POST /payments (MREC: MERCHANT, STORED, SUBSEQUENT + networkTransactionId)
        API-->>M: transactionId
    end
```

#### Workflow 5: Hotel stay with incremental auth

``` mermaid
sequenceDiagram
    participant CH as Cardholder
    participant M as Hotel
    participant API as Online Payments API

    CH->>M: Checks in
    M->>API: POST /payments (CEST: CARDHOLDER, STORED, isAmountFinal: false)
    API-->>M: transactionId

    Note over CH: Extends stay / minibar charges

    M->>API: PATCH /payments/{transactionId} { amount: 5000 } — Incremental (MINC)
    API-->>M: Updated authorization

    CH->>M: Checks out
    M->>API: POST /payments/{transactionId}/captures — Final capture
    API-->>M: Captured
```

#### Workflow 6: Multi-shipment with reauthorization

``` mermaid
sequenceDiagram
    participant M as Merchant
    participant API as Online Payments API

    M->>API: POST /payments (CARDHOLDER, STORED, MANUAL capture)
    API-->>M: transactionId + networkTransactionId

    M->>API: POST /payments/{transactionId}/captures — Ship 1 (partial)
    API-->>M: Captured

    Note over M: Auth expires before final shipment

    M->>API: POST /payments (MRAU: MERCHANT, STORED, REAUTHORIZATION + networkTransactionId)
    API-->>M: New transactionId

    M->>API: POST /payments/{transactionId}/captures — Ship 2 (final)
    API-->>M: Captured
```

---

## Recurring Subscriptions Guide

This section provides end-to-end guidance for implementing recurring subscription billing using the Online Payments API with CIT/MIT stored credentials.

### Subscription Lifecycle Overview

``` mermaid
stateDiagram-v2
    [*] --> SignUp: Cardholder subscribes
    SignUp --> Active: Payment approved (CREC)
    Active --> Active: Recurring charge (MREC)
    Active --> PastDue: Charge declined
    PastDue --> Active: Retry succeeds (MREC/MRSB)
    PastDue --> Active: Cardholder re-initiates (CUSE)
    PastDue --> Cancelled: Max retries exceeded
    Active --> PlanChange: Cardholder upgrades/downgrades
    PlanChange --> Active: New amount applied (MREC)
    Active --> Cancelled: Cardholder cancels
    Cancelled --> [*]
```

### Step 1: Initial Subscription Sign-Up (CREC)

When a cardholder subscribes, process the first payment as a **cardholder-initiated, first-in-recurring-series** transaction. This stores the credential and establishes the recurring relationship with the card networks.

```http
POST /payments
Content-Type: application/json
Authorization: Bearer {access_token}
request-id: {unique-uuid}
merchant-id: {your-merchant-id}
```

```json
{
  "captureMethod": "NOW",
  "amount": 999,
  "currency": "USD",
  "merchantOrderNumber": "SUB-20260327-001",
  "merchant": {
    "merchantSoftware": {
      "companyName": "Your Company",
      "productName": "Your Product",
      "version": "2.0"
    }
  },
  "paymentMethodType": {
    "card": {
      "accountNumber": "4777779999999990",
      "expiry": {
        "month": 5,
        "year": 2027
      }
    }
  },
  "accountHolder": {
    "fullName": "Jane Doe",
    "billingAddress": {
      "line1": "123 Main Street",
      "city": "Tampa",
      "state": "FL",
      "postalCode": "33626"
    }
  },
  "initiatorType": "CARDHOLDER",
  "accountOnFile": "TO_BE_STORED",
  "recurring": {
    "recurringSequence": "FIRST"
  },
  "isAmountFinal": true
}
```

**Critical:** From the response, persist these values for all future merchant-initiated charges:

- `transactionId` — reference for this transaction
- `paymentMethodType.card.networkResponse.networkTransactionId` — **required for Visa MIT**, recommended for all networks

### Step 2: Subsequent Recurring Charges (MREC)

Each billing cycle, the merchant system processes the charge without cardholder interaction. This is a **merchant-initiated, subsequent recurring** transaction.

```json
{
  "captureMethod": "NOW",
  "amount": 999,
  "currency": "USD",
  "merchantOrderNumber": "SUB-20260427-001",
  "merchant": {
    "merchantSoftware": {
      "companyName": "Your Company",
      "productName": "Your Product",
      "version": "2.0"
    }
  },
  "paymentMethodType": {
    "card": {
      "accountNumber": "4777779999999990",
      "originalNetworkTransactionId": "{networkTransactionId-from-step-1}",
      "expiry": {
        "month": 5,
        "year": 2027
      }
    }
  },
  "accountHolder": {
    "fullName": "Jane Doe",
    "billingAddress": {
      "line1": "123 Main Street",
      "city": "Tampa",
      "state": "FL",
      "postalCode": "33626"
    }
  },
  "initiatorType": "MERCHANT",
  "accountOnFile": "STORED",
  "recurring": {
    "recurringSequence": "SUBSEQUENT"
  },
  "isAmountFinal": true
}
```

> **Visa & Discover tokens:** `originalNetworkTransactionId` is required. For other networks it is optional but recommended.

### Step 3: Handling Declines and Retries

When a recurring charge is declined, you have two recovery paths:

#### Option A: Merchant resubmits later (MRSB)

If goods/services have already been delivered and the decline was due to insufficient funds, the merchant may resubmit:

```json
{
  "captureMethod": "NOW",
  "amount": 999,
  "currency": "USD",
  "initiatorType": "MERCHANT",
  "accountOnFile": "STORED",
  "authorizationPurpose": "RESUBMISSION",
  "paymentMethodType": {
    "card": {
      "accountNumber": "4777779999999990",
      "originalNetworkTransactionId": "{networkTransactionId-from-step-1}",
      "expiry": { "month": 5, "year": 2027 }
    }
  },
  "accountHolder": {
    "fullName": "Jane Doe",
    "billingAddress": {
      "line1": "123 Main Street",
      "city": "Tampa",
      "state": "FL",
      "postalCode": "33626"
    }
  }
}
```

#### Option B: Cardholder resolves and re-initiates (CUSE)

Notify the cardholder of the decline. After they resolve the issue with their issuer and log back in, process as a **cardholder-initiated stored credential** transaction:

```json
{
  "captureMethod": "NOW",
  "amount": 999,
  "currency": "USD",
  "initiatorType": "CARDHOLDER",
  "accountOnFile": "STORED",
  "isAmountFinal": true,
  "paymentMethodType": {
    "card": {
      "accountNumber": "4777779999999990",
      "expiry": { "month": 5, "year": 2027 }
    }
  },
  "accountHolder": {
    "fullName": "Jane Doe",
    "billingAddress": {
      "line1": "123 Main Street",
      "city": "Tampa",
      "state": "FL",
      "postalCode": "33626"
    }
  }
}
```

> **Note:** After a successful CUSE recovery, subsequent recurring charges continue as MREC using the same `originalNetworkTransactionId` from the original sign-up.

#### Recommended retry strategy

``` mermaid
flowchart TD
    A["MREC charge declined"] --> B["Wait & retry MREC\n(e.g., 3 days later)"]
    B -->|Approved| C["Resume normal billing"]
    B -->|Declined again| D["Notify cardholder"]
    D --> E{Cardholder resolves?}
    E -->|Yes — logs in| F["Process as CUSE"]
    F --> C
    E -->|No response| G["Retry MRSB\n(if goods already delivered)"]
    G -->|Approved| C
    G -->|Declined| H["Suspend / cancel subscription"]
```

### Variable-Amount Subscriptions (Mastercard CREV → MREV)

For subscriptions where the billing amount changes each cycle (e.g., usage-based billing, utilities), Mastercard requires specific variable-amount recurring indicators.

**Step 1 — Sign-up (CREV):**

```json
{
  "captureMethod": "NOW",
  "amount": 8500,
  "currency": "USD",
  "initiatorType": "CARDHOLDER",
  "accountOnFile": "TO_BE_STORED",
  "recurring": {
    "recurringSequence": "FIRST",
    "agreementId": "UTIL-AGR-78945",
    "isVariableAmount": true
  },
  "paymentMethodType": {
    "card": {
      "accountNumber": "5454545454545454",
      "expiry": { "month": 5, "year": 2027 }
    }
  },
  "accountHolder": {
    "fullName": "Jane Doe",
    "billingAddress": {
      "line1": "123 Main Street",
      "city": "Tampa",
      "state": "FL",
      "postalCode": "33626"
    }
  }
}
```

**Step 2 — Subsequent variable charges (MREV):**

```json
{
  "captureMethod": "NOW",
  "amount": 9200,
  "currency": "USD",
  "initiatorType": "MERCHANT",
  "accountOnFile": "STORED",
  "recurring": {
    "recurringSequence": "SUBSEQUENT",
    "agreementId": "UTIL-AGR-78945",
    "isVariableAmount": true
  },
  "paymentMethodType": {
    "card": {
      "accountNumber": "5454545454545454",
      "expiry": { "month": 5, "year": 2027 }
    }
  },
  "accountHolder": {
    "fullName": "Jane Doe",
    "billingAddress": {
      "line1": "123 Main Street",
      "city": "Tampa",
      "state": "FL",
      "postalCode": "33626"
    }
  }
}
```

> **Important:** `agreementId` must be the same across the entire recurring series. `isVariableAmount: true` is required for both the initial (CREV) and subsequent (MREV) transactions. This flow is Mastercard only.

### Subscription with Card Verification First

Some merchants verify the card without charging at sign-up, then begin recurring billing later. This is common for free trials.

``` mermaid
sequenceDiagram
    participant CH as Cardholder
    participant M as Merchant
    participant API as Online Payments API

    CH->>M: Starts free trial, enters card
    M->>API: POST /payments (amount: 0, CARDHOLDER, TO_BE_STORED, FIRST)
    API-->>M: Verified + networkTransactionId
    Note over M: No funds held — card validated only

    Note over M: Free trial period elapses

    M->>API: POST /payments (MREC: MERCHANT, STORED, SUBSEQUENT + networkTransactionId)
    API-->>M: First billable charge approved

    loop Ongoing billing
        M->>API: POST /payments (MREC)
        API-->>M: Approved
    end
```

**Verification request** (zero-amount authorization):

```json
{
  "captureMethod": "NOW",
  "amount": 0,
  "currency": "USD",
  "merchantOrderNumber": "TRIAL-20260327-001",
  "merchant": {
    "merchantSoftware": {
      "companyName": "Your Company",
      "productName": "Your Product",
      "version": "2.0"
    }
  },
  "paymentMethodType": {
    "card": {
      "accountNumber": "4777779999999990",
      "expiry": {
        "month": 5,
        "year": 2027
      }
    }
  },
  "accountHolder": {
    "fullName": "Jane Doe",
    "billingAddress": {
      "line1": "123 Main Street",
      "city": "Tampa",
      "state": "FL",
      "postalCode": "33626"
    }
  },
  "initiatorType": "CARDHOLDER",
  "accountOnFile": "TO_BE_STORED",
  "recurring": {
    "recurringSequence": "FIRST"
  }
}
```

### Plan Changes (Upgrade / Downgrade)

When a cardholder changes their subscription plan:

- If the cardholder is **logged in and actively making the change**, the next charge at the new amount is a **CUSE** (cardholder-initiated, stored credential).
- All subsequent automated charges at the new amount continue as **MREC** (merchant-initiated, subsequent recurring).
- The `originalNetworkTransactionId` from the original sign-up continues to be used.

``` mermaid
sequenceDiagram
    participant CH as Cardholder
    participant M as Merchant
    participant API as Online Payments API

    Note over CH, M: Currently on $9.99/month plan

    CH->>M: Upgrades to $19.99/month plan
    M->>API: POST /payments (CUSE: CARDHOLDER, STORED, amount: 1999)
    API-->>M: Approved (prorated or full new amount)

    loop Future billing at new rate
        M->>API: POST /payments (MREC: MERCHANT, STORED, SUBSEQUENT, amount: 1999)
        API-->>M: Approved
    end
```

### Delayed Recurring Charge (MDEL)

If a cardholder requests to delay their next billing (e.g., "pause my subscription for a week"), the merchant processes the delayed charge when ready:

```json
{
  "captureMethod": "NOW",
  "amount": 999,
  "currency": "USD",
  "initiatorType": "MERCHANT",
  "accountOnFile": "STORED",
  "authorizationPurpose": "DELAYED_CHARGE",
  "paymentMethodType": {
    "card": {
      "accountNumber": "4777779999999990",
      "originalNetworkTransactionId": "{networkTransactionId-from-sign-up}",
      "expiry": { "month": 5, "year": 2027 }
    }
  },
  "accountHolder": {
    "fullName": "Jane Doe",
    "billingAddress": {
      "line1": "123 Main Street",
      "city": "Tampa",
      "state": "FL",
      "postalCode": "33626"
    }
  }
}
```

### Recurring Subscription Field Reference

| Scenario | `initiatorType` | `accountOnFile` | `recurringSequence` | `isVariableAmount` | `authorizationPurpose` | Type |
|---|---|---|---|---|---|---|
| Sign-up (first charge) | `CARDHOLDER` | `TO_BE_STORED` | `FIRST` | — | — | CREC |
| Sign-up (variable, MC) | `CARDHOLDER` | `TO_BE_STORED` | `FIRST` | `true` | — | CREV |
| Sign-up (card on file exists) | `CARDHOLDER` | `STORED` | `FIRST` | — | — | CREC |
| Verification only (free trial) | `CARDHOLDER` | `TO_BE_STORED` | `FIRST` | — | — | CREC |
| Automated recurring charge | `MERCHANT` | `STORED` | `SUBSEQUENT` | — | — | MREC |
| Automated variable charge (MC) | `MERCHANT` | `STORED` | `SUBSEQUENT` | `true` | — | MREV |
| Cardholder re-initiates after decline | `CARDHOLDER` | `STORED` | — | — | — | CUSE |
| Merchant resubmits after decline | `MERCHANT` | `STORED` | — | — | `RESUBMISSION` | MRSB |
| Cardholder upgrades/downgrades plan | `CARDHOLDER` | `STORED` | — | — | — | CUSE |
| Merchant delays billing at cardholder request | `MERCHANT` | `STORED` | — | — | `DELAYED_CHARGE` | MDEL |
