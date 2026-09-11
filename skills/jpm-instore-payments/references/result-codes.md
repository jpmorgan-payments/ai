# Result Codes & Recovery

Use this as the quick check. The full result/status model lives in the official
protocol reference, sections 2, 6, and 7.

## Read responses

- Responses echo the request `operation`. Readiness/progress are pushed as
  `Status` notifications; readiness is `context: "Maintenance"`, `result: "101"`.
- `result` is a numeric string. Common values: `"0"` OK, `"3"` bad message, `"4"`
  invalid reference/key, `"5"` busy, `"10"` timeout, `"11"`/`"12"` cancelled,
  `"17"` card declined, `"19"` host declined.
- For transactions, the financial outcome is `approval`, not `result`.

A decline is a completed `Transaction` response with `result: "0"` and
`approval: "declined"`. Treat only non-`"0"` results or socket failures as errors;
act/print approved receipts only when `approval === "approved"`.

## Recover safely

Transactions are not idempotent. If the socket drops or a UI timeout leaves the state
unclear:

1. Mark the client not-ready and stop waiting on the in-flight request.
2. Reconnect, wait for `Status` `Maintenance`/`101`, then re-`SetParameter HWVENDORID`.
3. Send `LastTransaction` (or `GetTransactions`) to resolve whether the transaction
   reached the host. There is no `TransactionLookup` operation.
4. Reconcile if it completed; resend only if it never ran.

Serialize sends. `result: "5"` means the terminal is busy with another operation.

## References

- Full result/status model: the official protocol reference (sections 2, 6, and 7).
