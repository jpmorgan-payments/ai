# Receipt Requirements & POS Logging

Use this reference whenever generated POS code prints, stores, forwards, or validates receipt or log data. The terminal can return `merchantReceipt` and `cardholderReceipt` strings and can print on supported hardware, but any POS-side receipt or logging behavior still has to follow the official rules.

## Receipt rules to preserve

- Offer the cardholder a receipt for every transaction, including success, error, decline, refund, void, reversal, and gift card flows.
- Label receipt fields clearly. Do not abbreviate labels unless the result remains easy to understand.
- Never print the expiration date unless fully truncated. Never print full PAN, PIN, CVV, or track data.
- Include the required merchant, terminal/lane, date/time, payment brand, masked account, transaction type, entry method, amount, approval/decline code, and applicable trace/batch identifiers for the rail.
- If a balance is returned, including zero balance, display or print it when the rail requires it.
- For partial approvals, present the approved amount as the transaction amount and preserve the requested/due amount where useful for reconciliation.
- For DCC accepted transactions, include exchange rate, mark-up, transaction amount in billing currency, provider, and approved disclosure text. Do not change DCC disclosures without J.P. Morgan approval.
- For gift cards, include remaining balance for approved and declined transactions, calculate partial redemption/deactivation amounts from `dueAmount`, and include required disclaimers when value changes.
- For Quebec merchant locations, the cardholder copy must be in the cardholder language. Outside Quebec, use the merchant or cardholder language as applicable.

## POS logging requirements

Log enough to support J.P. Morgan troubleshooting without expanding PCI scope:

- Session management: connection target, secure/non-secure mode, connection establishment timestamp, connection context, closure reason, closure impact, and session duration.
- Transaction lifecycle: operation start, request metadata, streamed `Status` contexts/results, final response, approval/decline outcome, and recovery actions.
- Transaction fields: masked account only, card brand, approval, authCode, authorizedAmount, date/time, hostError, responseCode, transactionID, reference, batchNumber, and operation/type.
- Error handling: connection exceptions, non-transaction API errors, result codes, retry/recovery attempts, and operator-visible impact.
- Certificate management: certificate operation name, alias/commonName, result, renewal/expiration events, and security-impact notes. Do not log certificate contents, private keys, or secrets.
- Retention: define how long POS logs are retained, when they are purged/archived, and how archived logs are protected.

Never log full PAN, PIN, CVV, track data, private keys, certificate PEM bodies, full `HWVENDORID`, or values read from your config file (`instore.env`, or `local.properties`/`BuildConfig` on Android). Mask identifiers when possible and keep request/response logs PCI-safe.

## Validation evidence

For formal validation, keep PCI-safe evidence for the flows under test: test terminal/CAT run logs, receipt samples, approval and decline/error paths, paired reversible operations, AVS/CVD scenarios where used, official test amount scenarios, and broken-connection recovery using `LastTransaction`.
