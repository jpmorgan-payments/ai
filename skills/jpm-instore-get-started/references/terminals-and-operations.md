# Supported Terminals & Operations Catalogue

This is the single catalogue for supported Ingenico AXIUM terminals, terminal operations, and transaction types used by the in-store skills. Keep model names, operation names, support status, and transaction types here. Workflow skills may group these choices for their user prompts, but must link here instead of maintaining a separate list.

## Supported Ingenico AXIUM terminal models

The PDP terminal docs currently list the following Ingenico AXIUM models. These skills implement the **semi-integrated** WebSocket model in v1.

| Model | Semi-integrated | Notes |
| --- | --- | --- |
| **RX7000** | Yes | Countertop AXIUM. |
| **RX5000** | Yes | Countertop AXIUM. |
| **DX4000** | Yes | Countertop / portable AXIUM with built-in printer. |
| **DX8000** | Yes | Portable / handheld AXIUM with built-in printer. |

- **Semi-integrated terminals:** RX7000, RX5000, DX4000, DX8000.

> Treat any model not listed in the PDP terminal docs as WIP until confirmed with your J.P. Morgan contact.

## Terminal operations

Operations available to a semi-integrated POS. Operations marked \* are listed as semi-integrated only in the PDP API operations table.

| `operation` | Kind | Purpose |
| --- | --- | --- |
| `Transaction` | complex | Execute a card or gift-card financial operation. `type` selects the transaction (Sale, Authorization, Refund, Void, etc. - see transaction types below). Streams `Status` notifications during processing; the final response carries `result` and `approval`. |
| `Cancel` \* | simple | Cancel an outstanding complex `Display` or `Transaction` operation before it reaches an uncancellable stage. A `Transaction` cannot be cancelled once host communication begins; let it complete, then `VOID` if needed. |
| `LastTransaction` | simple | Return details of the last transaction sent to the payment host. **The recovery primitive** after a connection loss. |
| `SetParameter` | simple | Set one or more parameters (uses a `parameters` array). |
| `GetParameter` | simple | Read one or more parameters (uses a `parameters` array). |
| `Display` \* | complex | Show a short message to the cardholder. Fields: `text` (required), `timeout` (seconds; `0`/omitted = until cancelled/replaced). |
| `PrintLastReceipt` | simple | Reprint the last (attempted) receipt. |
| `PrintText` \* | simple | Print custom text on terminals with a physical printer. Field: `text` (full text to print; line breaks with `\n`). |
| `Restart` | simple | Restart/reboot the terminal app. |
| `GetInformation` | simple | Return device identity/health in an `information` object (serial, model, firmware, battery, versions). Use `firmwareVersion` to confirm software version. |
| `LineItems` \* | simple | Display a basket. Fields: `title`, `lineItems[]` (`left`/`right`), `subTotals[]` (up to 3), `totals[]` (up to 2). Screen stays until the next command. |
| `GetSignature` | complex | Prompt for and capture a signature. Optional `disclaimer`. Returns `signatureData` (base64/BCD). |
| `ReadCard` | complex | Prompt a card read. `cardType` `0` = non-banking (returns cleartext track data; never use for payment-card capture), `1` = banking (buffers card, returns `readCardID` to pass to a later `Transaction`; requires parameter `PROVAMT` > 0). Optional `timeout`. |
| `Status` | - | **Notification only** (terminal to POS). There is no `Status` request. |
| `GetTransactions` \* | simple | Query the current batch by category (`type`: `ALL_SALES`, `ALL_AUTHORIZATIONS`, `ALL_REFUNDS`, `ALL_UNADJUSTED`, `ALL_SAF`). Returns `records[]`. |

Certificate operations - `GenerateCsr`, `ImportCertificate`, `InstallTrustCertificate` - are described in the protocol reference's certificates section.

> **Not part of the public POS contract:** there is no `TransactionLookup`, `UploadAllSAF`, `GetReport`, `ProxyStatus`, `GetBatteryStatus`, `SetDeploymentId`, `GetTipAmount`, `GetInput`, `GetAgreement`, `DisplayQRCode`, or `CheckForUpdates` operation. (`GetBatteryStatus` info comes from `GetInformation`; SAF status comes from `GetTransactions type=ALL_SAF`; recovery is `LastTransaction`.)

## Card transaction types (`type` on `Transaction`)

| `type` | ISO msg | Purpose |
| --- | --- | --- |
| `SALE` | 1200 | Authorize **and** capture a card-present sale. |
| `AUTHORIZATION` | 1100 | Authorization only, no capture. Complete later with `COMPLETION` (or auto-capture / `VOID`). |
| `COMPLETION` | 1200 | Capture a prior `AUTHORIZATION`. Requires `originalAuthCode`. |
| `FORCE_SALE` | 1200 | Capture an approved **voice** authorization. Requires `originalAuthCode`. |
| `MOTO_SALE` | 1200 | Mail/telephone-order sale (card-not-present). Requires `order`. |
| `REFUND` | 1200 | Credit the cardholder. Refunds can be card-presented (fresh card swipe/tap) or credential-on-file (using `cardToken` from a prior sale). Gating refunds with cashier/manager auth is recommended. |
| `STATUS_CHECK` | 1100 | Zero-dollar authorization to check account status. Cannot be auto-reversed. |
| `VOID` | 1400 | Reverse a sale/refund/auth **still in the open batch**. Requires `originalAuthCode`. |
| `BALANCE_INQUIRY` | 1100 | Retrieve the cardholder account balance. |
| `SETTLEMENT` | - | Close the batch on the host (host-capture). |

`transactionType` (printable, for UI) values: `SALE`, `FORCE SALE`, `REFUND`, `AUTHORIZATION`/`PRE-AUTH`, `STATUS CHECK`, `MOTO SALE`/`MOTO`, `VOID`, `COMPLETION`/`PRE-AUTH COMPLETION`, `BALANCE INQUIRY`, `CLOSE BATCH`/`SETTLEMENT`. Use `type` for logic, `transactionType` for display.

### Gift card transaction types

| `type` | Purpose |
| --- | --- |
| `GC_REDEMPTION` | Redeem value (supports tip + partial redemption + cash-out). |
| `GC_ISSUANCE` | Issue / add value to a card. |
| `GC_ACTIVATION` | Activate a new card. |
| `GC_BALANCE_INQUIRY` | Check remaining balance. |
| `GC_DEACTIVATION` | Deactivate and cash out remaining balance. |
| `GC_REACTIVATION` | Reactivate a deactivated card. |
| `GC_FORCE_REDEMPTION` | Capture a phone-authorized redemption. Requires `originalAuthCode`. |
| `GC_FORCE_ISSUANCE` | Capture a phone-authorized issuance. Requires `originalAuthCode`. |
| `GC_FORCE_ACTIVATION` | Capture a phone-authorized activation. Requires `originalAuthCode`. |

Gift `transactionType` printable values are `GIFT CARD REDEMPTION`, `GIFT CARD ISSUANCE`, `GIFT CARD ACTIVATION`, `GIFT CARD BALANCE INQUIRY`, `GIFT CARD DEACTIVATION`, `GIFT CARD REACTIVATION`, `GIFT CARD ADD TIP`.
