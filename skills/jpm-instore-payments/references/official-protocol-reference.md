# In-Store Semi-Integrated Protocol — Official Reference

**Authoritative protocol source of truth** for generating POS→terminal integration
code. Every fact here is transcribed from the J.P. Morgan Payments Developer Portal
*In-Store Payments → Payment Terminal Application* documentation. The shared terminal
and operation catalogue lives in
`../../jpm-instore-get-started/references/terminals-and-operations.md`. Canonical
LLM-friendly source links are centralized in `pdp-source-pages.md`.

> This is the **public POS contract** for the J.P. Morgan Payment Terminal
> Application (the Android card-present app that runs on the terminal). It is what an
> external POS must send and expect. Do not invent operations, envelopes, or fields —
> if something is not in this reference, confirm it with your J.P. Morgan integration
> agent before relying on it.

---
## 1. Transport & connectivity

| Property | Value |
|---|---|
| Transport | WebSocket over TLS (`wss://`) |
| Port | **8442** (get-started uses `8442`; some doc code samples show `8443` for a same-device loopback — prefer `8442` unless told otherwise) |
| Security | TLS with **mutual authentication (mTLS)** — certificates on both the terminal and the POS. Certificate operations are `GenerateCsr` / `ImportCertificate` / `InstallTrustCertificate` (§9). |
| Format | JSON. **Case sensitive.** Escape `\n`, `\t`, `\"`, `\\` inside strings; other escape sequences are not supported. |
| Amounts | Integer **cents**, sent as numeric strings. Two implied decimals: `"50000"` = $500.00, `"500"` = $5.00. |
| Connection lifecycle | Keep the connection **open for the duration of a single operation** (simple or complex). Between operations you may disconnect and reconnect as needed. |
| On connection loss during a `Transaction` | If lost **before** the terminal contacts the host → the transaction is cancelled, terminal returns to idle. If lost **after/while** contacting the host → the terminal **automatically reverses** an approved transaction, then returns to idle. |

There is **one** `Transaction` operation; its `type` field selects the transaction.
The terminal does **not** expose one endpoint per transaction type.

---

## 2. Message model

Every message — request, response, and notification — is a JSON object with an
`operation` field.

- **Simple operation:** one request → one response. The response echoes the same
  `operation` value.
- **Complex operation:** one request → zero or more asynchronous **`Status`**
  notifications → one final response. The final response echoes the request's
  `operation` value, which signals completion. `Transaction`, `Display`,
  `GetSignature`, and `ReadCard` are complex.

There is **no** `ReadyApiResponse`, `TransactionApiStatus`, `UpdateApiStatus`, or
`ApiResponse` envelope. A response is identified by its echoed `operation` value; the
outcome is in the `result` field (and, for transactions, the `approval` field).

### Status notifications (asynchronous progress)

During a complex operation the terminal streams status messages:

```json
{ "operation": "Status", "context": "Communication", "result": "20" }
```

- `context` = the screen/phase (see §7).
- `result` = a **context-specific** status code (see §7). These are **not** the same
  numbers as the operation result codes in §6.
- **Do not drive business logic from `Status` result codes.** They are for
  troubleshooting and UI hints (e.g. "cardholder is on the PIN entry screen"). Use the
  **final command response's `result`** for the authoritative outcome.

### Readiness

The application signals readiness with a `Status` notification of context
`Maintenance`, result `101` ("application started"). **The POS waits for `101` before
sending a transaction.** Contexts `102`/`103` mean the app is entering/exiting
maintenance (installing an update) — wait for these to resolve before queueing
commands.

---

## 3. Operations catalogue

See the shared terminal and operation catalogue at `../../jpm-instore-get-started/references/terminals-and-operations.md` for supported terminal operations and their transaction types. Certificate operations are covered in §9.

---

## 4. Card transaction types (`type` on `Transaction`)

See `../../jpm-instore-get-started/references/terminals-and-operations.md` for the supported card and gift-card transaction types. See §12 for settlement request fields.

---

## 5. Request fields

### 5.1 Common `Transaction` request fields

| Field | Type / limit | Notes |
|---|---|---|
| `operation` | string | Always `"Transaction"`. Mandatory. |
| `type` | string | A transaction type from §4. Mandatory. |
| `requestedAmount` | string cents | Amount, two implied decimals. Mandatory (except `SETTLEMENT`, `STATUS_CHECK`, `BALANCE_INQUIRY`, `VOID`). |
| `reference` | ≤ 12 alphanumeric | POS-generated reference. If omitted, the terminal generates one. Response echoes it (echo max 15). |
| `invoice` | ≤ 6 numeric | Invoice number. |
| `customer` | ≤ 8 alphanumeric | Customer number. |
| `ticket` | ≤ 8 alphanumeric | Ticket number. |
| `purchase` | ≤ 8 alphanumeric | Purchase number. |
| `order` | ≤ 9 alphanumeric | Order number. **Mandatory for `MOTO_SALE`.** |
| `originalAuthCode` | alphanumeric | The auth code from the original authorization. **Mandatory for `COMPLETION`, `FORCE_SALE`, `VOID`, `GC_FORCE_*`.** |
| `tipAmount` | string cents | If provided, the terminal does **not** prompt for tip. |
| `taxAmount` | string cents | Overrides `TAXPERCENT` calculation. |
| `cashbackAmount` | string cents | Additional cash back (SALE). |
| `cardToken` | string | Credential-on-file token (COMPLETION/REFUND). |
| `expDate` | `YYMM` | Manually captured expiry. If sent, the terminal does **not** prompt for card entry. |
| `zip`, `address` | string | AVS. `zip` required for Amex commercial. |
| `lastFour` | 4 digits | Fraud control — compared against the captured card. |
| `isDebit` | `0`/`1` | Force debit/credit for swiped sales (else prompted). |
| `duplicateCheck` | `0`/`1` | `1` = reject if the last transaction matches card+amount. |
| `storedCredential` | `0`/`1`/`2` | Refund CIT/MIT: `0`=neither, `1`=CIT, `2`=MIT (both need `cardToken`+`expDate`). |

> **POS reference fields** (`reference`, `invoice`, `customer`, `ticket`, `purchase`, `order`) are echoed back in responses for POS reconciliation only and do not flow to JPMC settlement reporting. Only `uniqueTransactionId` (first 22 chars, left-justified) reaches settlement.

| `uniqueTransactionId` | ≤ 22 alphanumeric (effective) | POS-supplied unique ID for reporting. Only the first 22 characters (left-justified) are used in JPMC settlement reporting; if omitted the terminal generates one. |
| `printReceipt` | `0`/`1` | `1` = print on the terminal, `0`/omitted = do not print (default). |
| `dccOriginalCurrency` | ISO 4217 (e.g. `EUR`) | REFUND only — currency of the original DCC sale (§10). |
| `parameters` | array | Per-transaction parameter overrides, e.g. tip prompt config or `HWVENDORID` (§8). |

### 5.2 Gift card request fields

Same core fields, plus:

| Field | Type | Notes |
|---|---|---|
| `cashOutInd` | `0`/`1` | Redemption — `1` = cash out remaining balance. |
| `giftReference` | ≤ 15 alphanumeric | Extra reference, included in host messages/receipts. |
| `paymentType` | `0`/`1`/`2`/`3` | Tender used: cash / credit / debit / complimentary. |
| `originalAuthCode` | alphanumeric | Mandatory for `GC_FORCE_*`. |

---

## 6. Response fields & result codes

### 6.1 Key response fields

Responses echo `operation` (`Transaction`) and `type`, plus:

| Field | Meaning |
|---|---|
| `result` | **Operation result code** (numeric string, §6.2). `"0"` = the operation ran (gathered payment info + reached the host). It does **not** mean approved. |
| `approval` | `"approved"` / `"declined"`. **The financial outcome.** Errors and cancellations return `declined`. |
| `authCode` | Host approval code (approved transactions). |
| `responseCode` | Host response code (`"00"` on approval). |
| `hostError` | Host numeric decline code (`"00000"` when approved). |
| `errorMessage` | Host decline description. |
| `account` | Format-preserving masked PAN (first 6 + last 4 real; middle modified). Display-only. |
| `cardBrand` | e.g. `VISA`, `MASTERCARD`, `DISCOVER`, `AMERICAN EXPRESS`, `JCB`, `DINERS`, `MAESTRO`, `INTERAC`, `UNION PAY`. |
| `cardToken` | Credential-on-file token. |
| `entryMode` | `Manual`, `Swiped`, `FSwiped`, `EMV`, `Chip`, `Tap`, `Contactless`, `COF`, `None`. |
| `requestedAmount`, `subTotalAmount`, `taxAmount`, `tipAmount`, `surchargeAmount`, `cashBackAmount`, `totalAmount` | Amounts, cents. |
| `dueAmount` | On a partial authorization: `totalAmount` − amount approved by the issuer. |
| `authorizedAmount` | Amount approved by the issuer. |
| `balance` | Account/gift balance if returned. |
| `transactionID` | Terminal transaction id. |
| `batchNumber`, `batchJulianDay` | Batch identity. |
| `traceNumber` | Host trace (EBT/debit). |
| `cvm` | `NO CVM`, `Signature`, `PIN Verified`, `PIN and Signature`. |
| `signatureRequired` | `yes`/`no` (present when a signature is required and not captured electronically). |
| `signatureData` | Base64 PNG of a captured signature. |
| `merchantReceipt`, `cardholderReceipt` | Pre-formatted receipt text. |
| `uniqueTransactionId` | Echo or generated (first 22 chars used for reporting). |
| `dccIndicator`, `dccBillingCurrency`, `dccBillingAmount`, `dccExchangeRate`, `dccProvider`, `dccMarkup` | DCC fields (§10). |
| `PARData`, EMV tags (`AC`, `AID`, `ARC`, `IAD`, `TSI`, `TVR`, `emvTags[]`) | EMV/receipt data. |

> `result: "0"` + `approval: "approved"` ⇒ act/print an approved receipt.
> `result: "0"` + `approval: "declined"` ⇒ a valid **completed** decline, **not** a
> transport error. Only a non-`"0"` `result` (or a socket failure) is an error.

### 6.2 Operation result codes (`result`)

| Code | Meaning |
|---|---|
| `0` | OK — the operation ran (check `approval` for the financial outcome). |
| `1` | Application error (internal failure: thread/file/comm). |
| `2` | Card error (contact card removed/failed). |
| `3` | Message error (invalid/missing field, malformed request). |
| `4` | Invalid reference or key (VOID reference not in batch, or bad parameter key). |
| `5` | Busy (another operation in progress — never overlap). |
| `6` | PIN debit key error (no PIN debit key injected). |
| `7` | PIN encryption error (PIN hardware / >1M txns). |
| `8` | P2PE key error. |
| `9` | Card removed during processing. |
| `10` | Timeout on the user interface. |
| `11` | Cancelled by user (cancel key on a cancellable screen). |
| `12` | Cancelled by a POS `Cancel` operation. |
| `13` | Cancel not available. |
| `14` | Nothing to cancel. |
| `15` | Parse error on the incoming request. |
| `17` | Declined by the card. |
| `19` | Declined by the payment host. |
| `20` | Pre-condition failed before reaching the host. |
| `21` | Connection to the host failed. |
| `22` | Sending request to the host failed. |
| `23` | Host response could not be processed. |
| `24` | Invalid host response. |
| `25` | Invalid clerk identification. |
| `26` | Fraud control validation failed (account number mismatch). |
| `27` | Printer not operational. |
| `28` | Card is not supported. |
| `29` | Debit refund error. |
| `31`–`40` | SAF errors (max amount/count/cumulative, entry mode, mask, type, CVM, international, not supported, CIT). |
| `41`–`43` | AVS no-match (address / ZIP / both). |
| `70`–`72` | Printer: cover open / paper jam / not supported. |
| `80`–`95` | Terminal/kernel: not operational, not connected, in progress, missing creds, key injection, EMV config, security, low battery, MAC, key sync, config, network, pending params, kernel. |
| `97` | No data found for the request. |
| `98` | Not implemented. |
| `99` | Unknown error (catch-all). |

Simple operations reuse the relevant subset (e.g. `SetParameter`/`GetParameter`
return per-key `result` values `0`/`1`/`3`/`4`/`5`). Certificate operations return an
**integer** `result` (`0` success, `1` error, `3` invalid, `5` busy) — see §9.

---

## 7. Status notification contexts

`{ "operation": "Status", "context": "<context>", "result": "<code>" }` — asynchronous
during complex operations. Result codes are **context-specific** and for UI/debug only.

| `context` | Occurs when | Notable `result` codes |
|---|---|---|
| `Maintenance` | Any time | `101` app started (ready), `102` entering maintenance, `103` exiting maintenance |
| `CardPrompt` | Prompting for card | `51` shown, `32` card accepted, `31` card failure, `37` fallback to MSR, `02` card error, `10` timeout, `11` cancelled |
| `PaymentType` | Credit/debit choice | `52` shown, `33` credit, `34` debit, `10`, `11` |
| `ApplicationSelection` | EMV app choice | `53` shown, `35` selected, `02`, `10`, `11` |
| `PINEntry` | PIN prompt | `55` shown, `36` PIN entered, `06` no debit key, `07` PIN hw error, `02`, `10`, `11` |
| `Signature` | Signature prompt | `56` shown, `14` declined by user, `10`, `11` |
| `Confirmation` | Amount confirmation | `57` shown, `40` accepted, `10`, `11` |
| `Communication` | Online authorization | `58` shown, `25` good host response, `19` declined by host, `20`–`24` host failures |
| `Approval` | Outcome screen | `59` shown, `10` timed out (expected) |
| `Display` | Generic message | `60` shown, `10` timed out (expected) |
| `Print` | Printing | `70` started, `71` completed, `72` paper/mechanical, `73` no-receipt option |
| `Generic` | Any time | `91` timer reset, `99` unknown error |

---

## 8. Parameters — `SetParameter` / `GetParameter`

Both use a `parameters` **array** of `{ "key", "value" }` objects (get uses `{ "key" }`
and returns `value`+per-key `result`). **This is not a top-level `key`/`value` pair.**

**Set HWVENDORID at startup (mandatory):**
```json
{ "operation": "SetParameter",
  "parameters": [ { "key": "HWVENDORID", "value": "ABCD1234" } ] }
```
Response:
```json
{ "operation": "SetParameter",
  "parameters": [ { "key": "HWVENDORID", "result": "0" } ] }
```

**Read parameters:**
```json
{ "operation": "GetParameter",
  "parameters": [ { "key": "HOST_IP" }, { "key": "HOST_PORT" } ] }
```

`HWVENDORID` is **mandatory** and assigned by J.P. Morgan. Set it at startup via
`SetParameter` as the first POS-sent operation after readiness. Alternatively, include
`HWVENDORID` in the `parameters` array of each individual request message if you
prefer not to use a startup `SetParameter`:

```json
{
  "operation": "Transaction",
  "type": "SALE",
  "requestedAmount": "500",
  "parameters": [
    {
      "key": "HWVENDORID",
      "value": "1234"
    }
  ]
}
```

Failing to provide it fails validation or declines transactions in production. See the
**configuration parameters** reference for the full parameter catalogue (tip, tax,
timeouts, SAF, DCC, receipt, merchant, communication).

---

## 9. Certificate handling (mTLS)

The POS drives certificate provisioning on the terminal. These operations return an
**integer** `result`.

| `operation` | Purpose | Key fields |
|---|---|---|
| `GenerateCsr` | Terminal generates a keypair + CSR | `commonName` (FQDN, req), `subjectAltNames[]`, `organization`, `organizationalUnit`, `country`, `state`, `locality`, `keyUse` (`replace`/`rotate`). Returns `csr` (PEM). |
| `ImportCertificate` | Import the CA-signed device cert | `commonName`, `certificate` (PEM), `alias`, `keyUse`. |
| `InstallTrustCertificate` | Install a root CA into the truststore | `alias` (unique), `certificate` (PEM). |

Encode special characters in CSR/cert strings (`\n`, `\r`) as `\u000A` etc. or with
double backslash. Result: `0` success, `1` error, `3` invalid/missing field, `5` busy.
Do not log certificate PEM bodies, private keys, or full identifiers while handling
certificate operations.

---

## 10. Dynamic Currency Conversion (DCC)

DCC is **terminal-driven** — do not build a DCC prompt on the POS.

- The terminal auto-detects a foreign-currency card and prompts the cardholder to pay
  in their billing currency or the local currency. Available for **Visa and
  Mastercard**; provider is **FEXCO**. The terminal waits **≤ 5 seconds** for a rate;
  after that it processes in the local currency.
- **No request changes** are needed on `SALE`, `AUTHORIZATION`, incremental
  authorization, or `COMPLETION`. For a **REFUND**, send `dccOriginalCurrency` (e.g. `"EUR"`) to refund
  in the original currency; otherwise the local currency is assumed.
- DCC response fields: `dccIndicator` (`0` not offered / `1` offered+opted-in / `2`
  offered+opted-out), `dccBillingCurrency`, `dccBillingAmount`, `dccExchangeRate`,
  `dccProvider`, `dccMarkup`, plus `currencyCode` (local) and `authorizedAmount`.
- Enable with parameter `DCCSUPPORT` (see the **configuration parameters** reference). Receipts must
  show exchange rate, mark-up, transaction amount, and the disclosure text — get any
  disclosure changes approved by J.P. Morgan.

---

## 11. Store and Forward (SAF)

SAF lets the terminal approve **credit sale/refund** transactions offline within
configured limits when host communication fails, then upload them when connectivity
returns (typically before the next transaction).

- **Candidates:** credit sale/refund only (not debit), when host comm fails, CVM other
  than online/offline PIN, and within the SAF amount/count limits.
- **States:** `Eligible` → `Processed` / `Declined` / `Failed`. A `Failed` SAF
  generates a reversal; pending reversals must clear before the SAF queue is processed.
- **Void within SAF:** only `Eligible` SAF sale/refund can be voided (it's deleted from
  the SAF batch); other voids during an outage are declined with a communications
  error.
- **Query the queue:** `GetTransactions` with `type: "ALL_SAF"` → `records[]` (all
  states). There is no separate SAF-status operation.
- Enable/limit with `SAF`, `SAFNUMBER`, `SAFSALETOTAL`, `SAFREFTOTAL`, `SAFSALEFLOOR`,
  `SAFREFMAX`, `SAFENTRY`, `SAFINTER` (see the **configuration parameters** reference).

---

## 12. Settlement (host capture)

Host-capture mode stores each transaction through the day. The host auto-settles at a
predefined time (default early AM; funds within ~48h). To settle manually:

```json
{ "operation": "Transaction", "type": "SETTLEMENT" }
```
The terminal prompts to confirm the host settlement summary and produces the
Settlement Report. Response carries `approval`, `batchNumber`, `batchJulianDay`,
`result`. In demo mode (`DEMOMODE=1`) settlement is not performed.

---

## 13. Automatic operations

- **Reversals** are automatic. A reversal record is created after a financial request
  goes online and is kept in memory until the host response arrives, the reversal is
  acknowledged, or it is explicitly deleted. Timeout reversals run before the next
  transaction with no POS notification.
- **Cardholder language** follows EMV tag `5F2D` filtered by terminal-supported
  languages (`LANG` default, `ENGVAR` for English variety).
- **Signature, duplicate check, tip, cash back, cash discount** are governed by
  parameters (`SIGSUP`/`SIGCAPTURE`, `DUPCHECK`, `TIP`/`TIPPERC*`/`STATICTIP`,
  `CASHBACK*`, `CASHDISC*`). See the **configuration parameters** reference.

---

## 14. Recovery — never blindly retry

Semi-integrated transactions are **not idempotent**; resending a `SALE` after a dropped
socket can double-charge. On a broken connection during a transaction:

1. **Reconnect** and wait for the readiness `Status`/`Maintenance` `101`. Re-set
   `HWVENDORID` if needed.
2. **Resolve the true state with `LastTransaction`** — it returns the last transaction
   sent to the host, so you can tell whether yours completed. (There is no
   `TransactionLookup` operation; `GetTransactions` can also enumerate the batch.)
3. **Only then** reconcile or, if it never ran, re-send.

The terminal also auto-reverses an approved transaction if the connection drops after
host communication, and runs timeout reversals automatically.

---

## 15. Security & PCI

- **mTLS** between POS and terminal (§9). TLS is case-sensitive JSON over `wss://`.
- **No cardholder data on the POS.** The terminal never returns clear PAN/PIN/CVV/
  track data to the POS through the payment flow; `account` is format-preserving masked
  and display-only. Never send, store, or log PAN/PIN/CVV/track/token data.
- **Terminal-driven UX.** The terminal owns card entry, PIN, tip prompts, DCC
  disclosure, and signature. The POS sends intent and reads results.
- **Receipt/logging requirements.** When generated code prints receipts or maintains
  POS logs, follow the **receipt and POS logging** reference and keep logs PCI-safe.
- PCI DSS requires a daily terminal reboot (parameter `REBTIME`, default 02:00 local) —
  the POS must tolerate the terminal dropping off the network for a reboot.
---

