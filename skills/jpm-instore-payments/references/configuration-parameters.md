# Configuration Parameters - Payment Terminal Application

Quick lookup for parameters a semi-integrated POS may read/write through
`GetParameter`/`SetParameter`. Both operations use a `parameters` array of
`{ "key", "value" }` objects; the official protocol reference (§8) documents the
wire shape. `API=Y` means POS-settable. `API=N` means provisioned remotely by J.P.
Morgan Terminal Management Service (TMS).

Before generating parameter code, fetch the current **Configuration parameters** page from `pdp-source-pages.md`. Use its `API` column to distinguish POS-settable values from values managed remotely by J.P. Morgan TMS; do not copy or infer parameter names, defaults, or ranges from memory.

## Notes

- `HWVENDORID` is mandatory and POS-settable. Set it once per session as the first POS-sent terminal operation after readiness.
- `PROVAMT` is required for `ReadCard cardType=1` to buffer a banking card; it must be
  greater than zero.
- Use `parameters` inside a `Transaction` to override prompt behavior for that one
  transaction, for example `TIP`/`TIPPERC*` for a sale with tip.
- Amounts are cents. Floats and time formats follow the official parameter docs.
- If a needed key is not listed here, fetch the portal source before inventing a
  setting or default.
