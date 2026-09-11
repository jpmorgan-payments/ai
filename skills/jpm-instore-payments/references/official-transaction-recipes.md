# Official Transaction Recipes — Semi-Integrated POS

Exact request/response shapes per operation, transcribed from the J.P. Morgan Payments
Developer Portal. All amounts are **cents** (also known as minor units; numeric strings, two implied decimals).
The full field/result-code/status model and parameter keys are documented in the
official protocol reference and the configuration parameters reference. Source pages: References section below.

**First, once per session — set the hardware vendor ID (mandatory):**
```json
{ "operation": "SetParameter",
  "parameters": [ { "key": "HWVENDORID", "value": "<from your config file>" } ] }
```
Wait for the readiness `Status` (`context: "Maintenance"`, `result: "101"`), then send
this `SetParameter` request as the **first POS-sent terminal operation**. Do not send
`GetInformation`, `Display`, `ReadCard`, or `Transaction` before it. Responses **echo
the request `operation`**; `result` is a numeric string; a transaction's financial
outcome is in `approval`.

---

## Contents

- [1. Sale](#1-sale)
- [2. Sale with tip](#2-sale-with-tip)
- [3. Authorization → Completion](#3-authorization--completion)
- [4. Force sale (voice authorization)](#4-force-sale-voice-authorization)
- [5. Refund](#5-refund)
- [6. Void](#6-void)
- [7. MOTO sale](#7-moto-sale)
- [8. Status check / balance inquiry](#8-status-check--balance-inquiry)
- [9. Gift cards](#9-gift-cards)
- [10. Line items (basket display)](#10-line-items-basket-display)
- [11. Display a message](#11-display-a-message)
- [12. Capture a signature](#12-capture-a-signature)
- [13. Read a card (banking or non-PCI)](#13-read-a-card-banking-or-non-pci)
- [14. Print](#14-print)
- [15. Settlement & batch queries](#15-settlement--batch-queries)
- [16. Cancel an in-flight operation](#16-cancel-an-in-flight-operation)
- [17. Recovery (never blindly retry)](#17-recovery-never-blindly-retry)
- [18. Terminal identity / health](#18-terminal-identity--health)
- [19. Restart terminal app](#19-restart-terminal-app)
- [20. Certificate handling](#20-certificate-handling)
- [References](#references)

---

## 1. Sale

```json
{ "operation": "Transaction", "type": "SALE", "requestedAmount": "500", "printReceipt": "1" }
```
- Complex: the terminal streams `Status` notifications (`CardPrompt` → `PaymentType`/
  `ApplicationSelection`/`PINEntry` → `Confirmation` → `Communication` → `Approval`),
  then the final response echoes `operation: "Transaction"`.
- Approved when `result: "0"` **and** `approval: "approved"`. Read `authCode`,
  `cardBrand`, `account` (masked), `totalAmount`, `transactionID`.
- **Edge cases:** decline (`result: "0"`, `approval: "declined"` — do not print an
  approved receipt); `result: "5"` (busy — an operation is in flight); `result: "10"`
  (UI timeout); host failures `result: "19"`–`"24"`.

Optional fields: `reference` (≤12), `invoice` (≤6), `taxAmount`, `cashbackAmount`,
`isDebit`, `duplicateCheck`, `lastFour`, `uniqueTransactionId`.

## 2. Sale with tip

The terminal owns the tip prompt. Configure it via the transaction's `parameters`
array (per-transaction override of the `TIP`/`TIPPERC*`/`TIPAMT*` parameters).

**Terminal prompts for tip (suggested percentages):**
```json
{ "operation": "Transaction", "type": "SALE", "requestedAmount": "1000", "printReceipt": "1",
  "parameters": [
    { "key": "TIP", "value": "1" },
    { "key": "TIPPERC1", "value": "15000" },
    { "key": "TIPPERC2", "value": "20000" },
    { "key": "TIPPERC3", "value": "25000" }
  ] }
```
`TIPPERC1=15000` displays a 15% suggestion; `TIPAMT1=500` would display a $5.00
suggestion. Read `tipAmount` and `totalAmount` from the response.

**Suppress the prompt and send a known tip:** include `"tipAmount": "100"` — the
terminal then does not prompt.

**Turn the prompt off:** `{ "key": "TIP", "value": "0" }`.

## 3. Authorization → Completion

**Authorize:**
```json
{ "operation": "Transaction", "type": "AUTHORIZATION", "requestedAmount": "600" }
```
Keep the returned `authCode` (and `reference`/`transactionID`).

**Complete (capture):**
```json
{ "operation": "Transaction", "type": "COMPLETION",
  "requestedAmount": "600", "originalAuthCode": "006838" }
```
- `originalAuthCode` is **mandatory**. The completion amount may differ from the auth.
- **Edge cases:** completing an already-completed/voided auth fails.

## 4. Force sale (voice authorization)

```json
{ "operation": "Transaction", "type": "FORCE_SALE",
  "requestedAmount": "700", "originalAuthCode": "016555" }
```
Captures a previously approved voice authorization. `originalAuthCode` is mandatory.

## 5. Refund

Link each refund to an existing transaction and amount within your POS rather than
allowing free-form amount entry; gate with cashier/manager auth to reduce fraud.
No `originalAuthCode` is required for a refund.
```json
{ "operation": "Transaction", "type": "REFUND", "requestedAmount": "2500", "printReceipt": "1" }
```
**Credential-on-file (tokenized) refund:**
```json
{ "operation": "Transaction", "type": "REFUND", "requestedAmount": "2520",
  "cardToken": "2223603006060329", "expDate": "2512", "storedCredential": "1" }
```
`storedCredential: "1"` = CIT (customer-initiated; customer must be present). `storedCredential: "2"` (MIT, merchant-initiated) is not currently supported through the terminal.
**DCC refund:** add `"dccOriginalCurrency": "EUR"` to refund in the original currency.

## 6. Void

Reverses a sale/refund/auth **still in the open batch**.
```json
{ "operation": "Transaction", "type": "VOID", "originalAuthCode": "411922" }
```
- `originalAuthCode` is mandatory; works only before settlement (after settlement, use
  `REFUND`).
- **Edge cases:** voiding a settled/already-voided transaction fails (`result: "4"`
  invalid reference).

## 7. MOTO sale

```json
{ "operation": "Transaction", "type": "MOTO_SALE", "requestedAmount": "200", "order": "ABCD1234" }
```
`order` (≤9 alphanumeric) is mandatory. Card-not-present; authorized online.

## 8. Status check / balance inquiry

**Status check** (zero-dollar auth):
```json
{ "operation": "Transaction", "type": "STATUS_CHECK" }
```
**Balance inquiry:**
```json
{ "operation": "Transaction", "type": "BALANCE_INQUIRY" }
```
Read `balance` from the response.

## 9. Gift cards

**Activation (activate a new card):**
```json
{ "operation": "Transaction", "type": "GC_ACTIVATION", "requestedAmount": "2000" }
```
**Issuance / add value:**
```json
{ "operation": "Transaction", "type": "GC_ISSUANCE", "requestedAmount": "1000" }
```
**Redemption (spend):**
```json
{ "operation": "Transaction", "type": "GC_REDEMPTION", "requestedAmount": "500" }
```
**Balance inquiry:**
```json
{ "operation": "Transaction", "type": "GC_BALANCE_INQUIRY" }
```
**Deactivation / reactivation:** `GC_DEACTIVATION` (cash out) / `GC_REACTIVATION`.
**Force variants** (phone-authorized): `GC_FORCE_REDEMPTION`/`GC_FORCE_ISSUANCE`/
`GC_FORCE_ACTIVATION` — add `originalAuthCode`.

Read `balance` (remaining), `authCode`, `dueAmount` (on partial redemption). Optional
gift fields: `giftReference` (≤15), `paymentType` (`0`cash/`1`credit/`2`debit/
`3`complimentary), `cashOutInd` (redemption). **Split tender:** redeem what the gift
card covers, read the approved amount, then run a `SALE` for the remainder; repeat.

## 10. Line items (basket display)

Not a transaction. The screen stays until the next command.
```json
{ "operation": "LineItems",
  "title": "SHOPPING BASKET",
  "lineItems": [
    { "left": "1 x Orange Juice", "right": "$2.50" },
    { "left": "Discount", "right": "-$0.50" }
  ],
  "subTotals": [ { "left": "Sub Total:", "right": "$2.00" } ],
  "totals": [ { "left": "Total:", "right": "$2.00" }, { "left": "Points:", "right": "200" } ] }
```
`left`/`right` are display strings (format the currency yourself). `subTotals` ≤ 3,
`totals` ≤ 2. Send before the `SALE` so the basket is visible during payment.

## 11. Display a message

```json
{ "operation": "Display", "text": "Thank you!\nPlease show your ID to the cashier.", "timeout": "6" }
```
Complex: resolves on the echoed `Display` response (`result: "10"` timeout, `"12"`
cancelled). `timeout` `0`/omitted keeps the message until cancelled or replaced.

## 12. Capture a signature

```json
{ "operation": "GetSignature", "disclaimer": "You agree to sign this form" }
```
Returns `signatureData` (base64 PNG) on `result: "0"`.

## 13. Read a card (banking or non-PCI)

```json
{ "operation": "ReadCard", "cardType": "1", "timeout": "0" }
```
- `cardType: "1"` (**banking**) — buffers a payment card and returns `readCardID`;
  pass it to a subsequent `Transaction`. Requires parameter `PROVAMT` > 0. PCI rules
  apply; do not log or persist any returned card data.
- `cardType: "0"` (**non-PCI / non-banking**) — for gift cards, employee/loyalty cards,
  or other non-payment-card use cases. Returns cleartext `track1Data`/`track2Data`.
  Because these are not PCI-scoped cards, the POS is not prohibited from logging or
  persisting the returned track data, though care is still advised. Never use `cardType
  "0"` for payment-card capture.

> *Note: the response field is named `readCardID` (uppercase ID) — this is an
> inconsistency in the API; do not normalize to `readCardId` in code that consumes
> the response.*

## 14. Print

**Custom text** (printer-equipped terminals):
```json
{ "operation": "PrintText", "text": " Line1\n Line2\n" }
```
`result: "72"` = out of paper / mechanical problem.

**Reprint last receipt:**
```json
{ "operation": "PrintLastReceipt" }
```

## 15. Settlement & batch queries

**List the batch (compare to POS totals):**
```json
{ "operation": "GetTransactions", "type": "ALL_SALES" }
```
`type` ∈ `ALL_SALES`, `ALL_AUTHORIZATIONS`, `ALL_REFUNDS`, `ALL_UNADJUSTED`, `ALL_SAF`.
Returns `records[]`.

**Settle (close the batch):**
```json
{ "operation": "Transaction", "type": "SETTLEMENT" }
```
The terminal confirms the host summary and produces the Settlement Report. Settle once
per batch (host auto-settles at a predefined time by default).

## 16. Cancel an in-flight operation

```json
{ "operation": "Cancel" }
```
Cancels any in-flight **complex** operation — `Display`, `ReadCard`, `GetSignature`, or
`Transaction` — before it reaches an uncancellable stage. For bank card or gift card
`Transaction` operations, cancellation is not possible once host communication has
begun; let it complete, then `VOID` if needed (only `SALE`, `AUTHORIZATION`, and
`REFUND` support void; gift card void support is coming). Cancelled complex operations
return a response with `result: "12"`.

## 17. Recovery (never blindly retry)

After a dropped connection: reconnect, wait for the readiness `Status`
(`Maintenance`/`101`), re-`SetParameter HWVENDORID`, then determine the true state:
```json
{ "operation": "LastTransaction" }
```
Reconcile against the returned transaction **before** deciding to re-send. There is no
`TransactionLookup` operation; use `LastTransaction` (or `GetTransactions`).

## 18. Terminal identity / health

```json
{ "operation": "GetInformation" }
```
Returns an `information` object (`serialNumber`, `model`, `firmwareVersion`,
`batteryPercent`, `isCharging`, version fields). Use it for startup checks; battery
info comes from here (there is no separate battery-status operation).

## 19. Restart terminal app

```json
{ "operation": "Restart" }
```
The terminal returns the response, delays briefly, shuts down open connections, and
restarts the app. After restart, reconnect, wait for readiness `Status`
(`Maintenance`/`101`), and set `HWVENDORID` again before sending transactions.

## 20. Certificate handling

Certificate operations return integer `result` values (`0` success, `1` error, `3`
invalid/missing field, `5` busy). Do not log certificate PEM bodies or private keys.

**Generate a CSR:**
```json
{ "operation": "GenerateCsr",
  "commonName": "terminal.example.com",
  "subjectAltNames": [ { "type": "ip", "value": "192.168.1.10" } ],
  "organization": "Merchant Name",
  "organizationalUnit": "Store 001",
  "country": "US",
  "state": "FL",
  "locality": "Tampa",
  "keyUse": "replace" }
```
Returns `csr` as PEM text for signing by the configured CA.

**Import the signed device certificate:**
```json
{ "operation": "ImportCertificate",
  "commonName": "terminal.example.com",
  "certificate": "-----BEGIN CERTIFICATE-----...-----END CERTIFICATE-----",
  "alias": "terminal-wss",
  "keyUse": "replace" }
```

**Install a trust certificate:**
```json
{ "operation": "InstallTrustCertificate",
  "alias": "merchant-root-ca",
  "certificate": "-----BEGIN CERTIFICATE-----...-----END CERTIFICATE-----" }
```

Encode newline and carriage-return characters in certificate strings as `\u000A` /
`\u000D` or escaped `\\n` / `\\r` when sending JSON.

---

## References

LLM-friendly (markdown) source pages on the J.P. Morgan Payments Developer Portal.
Full field/result-code model: see the official protocol reference.

- [Card transactions (SALE, AUTH, COMPLETION, FORCE_SALE, MOTO, REFUND, STATUS_CHECK, VOID, BALANCE_INQUIRY)](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fin-store-payments%2Fcapabilities%2Fpayment-terminal-application%2Fcard-transactions.md)
- [Gift card transactions](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fin-store-payments%2Fcapabilities%2Fpayment-terminal-application%2Fgiftcard-transactions.md)
- [Setup and management (LineItems, Display, GetSignature, ReadCard, GetTransactions, LastTransaction, PrintText, Cancel, GetInformation, Restart)](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fin-store-payments%2Fcapabilities%2Fpayment-terminal-application%2Fsetup-and-management.md)
- [Certificate handling](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fin-store-payments%2Fcapabilities%2Fpayment-terminal-application%2Fcertificate-handling.md)
- [Settlement](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fin-store-payments%2Fcapabilities%2Fpayment-terminal-application%2Fsettlement.md)
- [Store and Forward (ALL_SAF query)](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fin-store-payments%2Fcapabilities%2Fpayment-terminal-application%2Fstore-and-forward.md)
- [Dynamic Currency Conversion (refund `dccOriginalCurrency`)](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fin-store-payments%2Fcapabilities%2Fpayment-terminal-application%2Fdynamic-currency-conversion.md)
- [Status messages](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fin-store-payments%2Fcapabilities%2Fpayment-terminal-application%2Fstatus-messages.md)
