---
name: jpm-instore-payments
description: Implement a J.P. Morgan in-store (card-present) semi-integrated integration one operation at a time, against an Ingenico AXIUM terminal over a TLS WebSocket. Use this skill after jpm-instore-get-started when the developer is ready to build terminal operations — setup and management first (Cancel, Display, GetInformation, GetParameter, GetSignature, GetTransactions, LastTransaction, LineItems, PrintLastReceipt, PrintText, ReadCard, Restart, SetParameter), certificate operations (GenerateCsr, ImportCertificate, InstallTrustCertificate), then payment operations such as sale, tip/gratuity, authorization and completion, force sale, MOTO sale, refund, void, status check, balance inquiry, gift cards, Store-and-Forward, DCC, settlement, and reporting. Requires SetParameter HWVENDORID as the first POS-sent terminal operation after readiness, enforces cents amount formatting, keeps all card interaction terminal-driven with no card data on the POS, uses environment-aware configuration, and runs a CAT smoke test before any production change.
---

# JPM In-Store — Payments

Implement the in-store integration **one operation at a time** against the semi-integrated terminal. Each operation is a JSON envelope over the `wss://<host>:8442` WebSocket, discriminated by an `operation` field; transactions carry a `type`. This skill confirms prerequisites, enforces the invariants, and walks a chosen operation end to end using the reference files.

> **Authoritative protocol:** `references/official-protocol-reference.md` (transport, message model, operations, transaction types, fields, result codes, status contexts, SAF/DCC/settlement/certs, recovery, security).
> **Per-operation recipes:** `references/official-transaction-recipes.md`.
> **Parameters:** `references/configuration-parameters.md`.
> **Receipts/logging:** `references/receipt-and-pos-logging.md`.
> **Client scaffold:** `references/websocket-client.md` (match envelopes to the official reference).
> **Result codes & recovery:** `references/result-codes.md`.
> **PDP sources:** `references/pdp-source-pages.md` (canonical LLM-friendly links; load when verifying or refreshing local reference material).

## Step 1 — Confirm prerequisites

The developer should already have:
- Completed `jpm-instore-get-started` — a config file with the terminal host, `8442` port, HWVENDORID, and environment. For most stacks this is an `instore.env` (`JPM_TERMINAL_HOST`, `JPM_TERMINAL_PORT=8442`, `JPM_HWVENDORID`, `JPM_ENV`); for **Kotlin/Java (Android)** it's `local.properties` (`jpm.terminal.host`, `jpm.terminal.port=8442`, `jpm.hwvendorid`, `jpm.env`) surfaced via `BuildConfig`.
- A reachable terminal you can connect to and exchange messages with.
- Validation/test artifacts from onboarding: test terminal access, EMV test cards for formal testing, network validation status, validation worksheet, and validation contact.
- A WebSocket client that connects, waits for the readiness `Status` (`context: "Maintenance"`, `result: "101"`), and resolves each request on the response that **echoes the request `operation`** (transactions carry the outcome in `approval`).

If invoked standalone, ask:
- Question: "Can your POS already open a `wss://<terminal-ip>:8442` connection to the terminal and exchange a message with it?"
- Header: "Connection ready?"
- Options:
  - "Yes — I can connect and send/receive"
  - "No — not yet"

If **No**: route the user to `jpm-instore-get-started` to complete connectivity setup, and exit.

**Target language.** If a `language` was already chosen in `jpm-instore-get-started`, reuse it and don't re-ask. Otherwise detect it from the project's dependency manifest (`package.json` → JavaScript/TypeScript; `requirements.txt`/`pyproject.toml`/`Pipfile`/`setup.py` → Python; `pom.xml` → Java; `build.gradle`/`build.gradle.kts` → Kotlin/Java; `go.mod` → Go; `Cargo.toml` → Rust; `Gemfile` → Ruby; `composer.json` → PHP; `*.csproj`/`*.fsproj` → .NET) and only ask if you can't infer it:
- Question: "Which programming language should I generate the terminal operations in?"
- Header: "Language"
- Options:
  - "JavaScript / TypeScript (Node.js)"
  - "Kotlin / Java (Android)"
  - "Python"
  - "C# / .NET"
  - "Other — tell me which"

Generate every operation in this `language`, mirroring the envelopes in `references/official-transaction-recipes.md` exactly.

## Step 2 — SetParameter HWVENDORID (mandatory first POS-sent operation)

After the socket opens and the terminal sends readiness `Status` (`context: "Maintenance"`, `result: "101"`), the POS must set the `HWVENDORID` the terminal expects **before sending any other terminal operation**:

```json
{ "operation": "SetParameter", "parameters": [ { "key": "HWVENDORID", "value": "<HWVENDORID from your config file>" } ] }
```

- Resolves on a `SetParameter` response echoing the request, with per-key `result: "0"`.
- **Read the value from your config file at runtime — never hardcode it** in source (`instore.env` via your env loader, or `local.properties` via `BuildConfig` on Android).
- Forgetting this is the #1 cause of a terminal rejecting requests. Make it the first POS-sent terminal operation after the readiness `Status` (`Maintenance`/`101`).

Confirm the developer's startup path does this before Step 3. If their code sends any other terminal operation first — including `GetInformation`, `Display`, `ReadCard`, or `Transaction` — fix the ordering now.

## Step 3 — Pick one or more operations

Implement **one operation at a time** — each has its own request shape, result handling, and smoke test. Bundling them makes failures hard to isolate and slows review. You may select several here to queue them, but implement and smoke-test each sequentially.

**Always ask this — never skip or assume.** Even if the developer described a goal earlier in the conversation, explicitly present the operation menu below every time and wait for a selection before generating any operation code. Do not infer the operation set from context.

Ask (multiSelect):
- Question: "Which operation(s) do you want to implement? (Select all that apply — they'll be implemented one at a time.)"
- Header: "Operations"
- Options (multiSelect):
  - "Select all"
  - "Setup & management ops" — terminal readiness, parameters, display, line items, signature, batch queries, recovery, printing, card read, cancel, and restart
  - "Certificate handling" — GenerateCsr / ImportCertificate / InstallTrustCertificate
  - "Sale" — a simple purchase
  - "Sale + tip / gratuity" — sale with gratuity
  - "Authorization → Completion" — tab / delayed capture
  - "Force sale" — capture a prior voice authorization
  - "MOTO sale" — card-not-present mail/telephone order sale
  - "Refund" — return funds (linked or unlinked)
  - "Void" — reverse a same-batch transaction
  - "Status check / balance inquiry" — zero-dollar account check or balance retrieval
  - "Gift cards" — issuance / redemption / balance
  - "Store & Forward (SAF)" — offline approval + status
  - "DCC" — dynamic currency conversion
  - "Settlement & reports" — nightly close, GetTransactions, reports

If the user selects more than one, queue them and implement each in turn (Steps 4–5) before moving to the next. Then open `references/official-transaction-recipes.md` and follow the section matching the current choice. It gives the exact envelope, the fields to send, the response to expect, and edge cases.

If the user selects **"Setup & management ops"**, treat this as the first-class setup-management section from the official docs. **Always ask this follow-up — never skip it or pick operations on the developer's behalf.** Present the menu and wait for a selection, then handle each chosen operation one at a time like any other operation:
- Question: "Which setup/management operation(s)? (Select all that apply.)"
- Header: "Setup ops"
- Options (multiSelect):
  - "Select all"
  - "Cancel" — cancel an outstanding complex `Display`/`Transaction` before host communication
  - "Display" — show a short cardholder-facing message until timeout, cancel, replacement, or transaction start
  - "GetInformation" — device identity/health (serial, model, firmware, battery); good startup check
  - "GetParameter" — read one or more terminal parameters (`parameters` array)
  - "GetSignature" — capture a signature (`signatureData`, base64)
  - "GetTransactions" — query the current batch (`ALL_SALES`, `ALL_AUTHORIZATIONS`, `ALL_REFUNDS`, `ALL_UNADJUSTED`, `ALL_SAF`)
  - "LastTransaction" — resolve unknown state after a dropped connection before any resend
  - "LineItems" — show an open basket on the terminal until the next command
  - "PrintLastReceipt" — reprint the last printed or attempted receipt
  - "PrintText" — print custom text on printer-equipped terminals
  - "ReadCard" — buffer a banking card read (`readCardID`); non-banking cleartext track reads (gift/employee cards) require explicit justification and must never be used for payment-card capture
  - "Restart" — restart/reboot the terminal app, then reconnect and wait for readiness

> `SetParameter` is **not** a menu choice. Setting `HWVENDORID` via `SetParameter` is **required** and is already handled in Step 2 as the mandatory first POS-sent terminal operation. Additional `SetParameter` calls for other parameters follow the same shape as `GetParameter`.

If the user selects **"Certificate handling"**, ask a follow-up (multiSelect) to pick which certificate operation(s) to implement, then handle each one at a time:
- Question: "Which certificate operation(s)? (Select all that apply.)"
- Header: "Certificate ops"
- Options (multiSelect):
  - "Select all"
  - "GenerateCsr" — terminal generates a keypair and CSR
  - "ImportCertificate" — import the CA-signed device certificate
  - "InstallTrustCertificate" — install the root CA trust certificate

These are documented in `references/official-protocol-reference.md` (operations table + §8 parameters + §9 certificates) and `references/official-transaction-recipes.md` (§§ 10–20). `GetParameter` mirrors `SetParameter`'s `parameters`-array shape. `Cancel` is simple but may not complete immediately because the terminal may need time to back out of the active complex operation. `Display`, `GetSignature`, and `ReadCard` are complex and resolve only after timeout, cancel, or user/cardholder completion. `Restart` returns before the app is fully back online, so reconnect, wait for readiness, and set `HWVENDORID` again. Do **not** offer unsupported operations (`SetDeploymentId`, `GetTipAmount`, `GetInput`, `GetAgreement`, `DisplayQRCode`, `CheckForUpdates`, standalone `GetBatteryStatus` — battery comes from `GetInformation`).

## Step 4 — Implement, enforcing the invariants

Follow the chosen reference section and generate the code **in the target `language` from Step 1** into the developer's project (confirm the path first; default to a sibling of the WebSocket client, e.g. `src/terminal/operations/`). Every operation MUST honor:

- **Amounts are cents.** `$10.00` = `1000`. Send as the terminal expects (`requestedAmount`, `tipAmount`, etc.). Never send dollars or floats — a format mistake charges the wrong amount. Validate before sending.
- **Terminal-driven flow.** The terminal owns the card prompt, PIN, tip prompt (where terminal-led), DCC disclosure, and signature. The POS sends intent and reads the result — it does not drive the card UX.
- **No card data on the POS.** Never send, request, store, or log PAN, PIN, CVV, track, or token data through the POS. Masked PANs in responses are display-only. For `ReadCard`, prefer `cardType: "1"` (banking card buffering); generate `cardType: "0"` only for an explicit non-banking use case (gift/employee cards — not PCI-scoped; must not be used for payment-card capture).
- **Environment-aware config.** Read host/port/HWVENDORID/env from your config file (`instore.env`, or `local.properties` via `BuildConfig` on Android); the environment value (`JPM_ENV` / `jpm.env`) selects CAT vs. PROD behavior. No hardcoded hosts or identifiers.
- **One in-flight operation.** Serialize sends; a second concurrent send returns `BUSY`.
- **Approval check.** Act/print only when `approval === "approved"`; a decline is a valid completed response, not an error (`references/result-codes.md`).
- **Receipts and POS logs.** If the POS prints, stores, or forwards receipt/log data, follow `references/receipt-and-pos-logging.md`; do not invent receipt content or log sensitive values.

## Step 5 — Smoke test before any production change

Before pointing at PROD or changing production config, run the operation end to end against your **test terminal or CAT environment**:

1. Connect → readiness `Status` (`Maintenance`/`101`).
2. `SetParameter HWVENDORID` as the first POS-sent terminal operation.
3. Run the operation with a realistic amount and reference.
4. Assert the expected response (echoing the request `operation`): approval path (`approval: "approved"`) **and** at least one decline/error path (`approval: "declined"` or a non-`"0"` `result`).
5. For reversible flows, verify the paired operation (auth→completion, sale→void, sale→refund).
6. For validation evidence, keep PCI-safe POS logs and receipt samples for the tested paths; include AVS/CVD and official test amount scenarios when they apply to the operation.

Only after the smoke test passes should the developer change any production configuration. Remind them: **go-live is gated by J.P. Morgan validation on real hardware** — the smoke test is necessary, not sufficient.

## Step 6 — Offer another, or exit with a summary

Ask:
- Question: "That operation works on your test terminal/CAT. Implement another?"
- Header: "More?"
- Options:
  - "Yes — pick another operation" → return to Step 3
  - "No — I'm done for now"

On exit, print a short summary: which operations are implemented, which are smoke-tested, and the remaining path to validation/go-live.

## Rules

- **'Select all' in multi-select questions** — When the user selects "Select all" from any multiSelect option list, treat it as if every other option in that list was selected.
- **`SetParameter HWVENDORID` is the first POS-sent terminal operation** after readiness every session, reconnect, and restart; value comes from your config file (`instore.env`, or `local.properties`/`BuildConfig` on Android), never hardcoded.
- **Amounts in cents**, validated before send. This invariant appears in generated code and in every recipe.
- **Card data never touches the POS.** No PAN/PIN/CVV/track/token through the POS; masked PANs are display-only; never log them.
- `ReadCard cardType: "0"` returns cleartext non-banking track data (gift/employee cards). Do not generate it for payment-card capture.
- Receipt and POS logging requirements are validation-sensitive; load `references/receipt-and-pos-logging.md` before generating receipt or log code.
- **Terminal-driven flow** — the POS sends intent and reads results; the terminal owns all card/customer interaction and disclosures (including DCC).
- **Environment-aware** — host, port (8442), HWVENDORID, and env come from your config file (`instore.env`, or `local.properties`/`BuildConfig` on Android); nothing hardcoded.
- **Never blindly retry.** On a dropped connection or a `result: "10"` timeout, resolve state with `LastTransaction` (or `GetTransactions`) before re-sending.
- **One operation at a time**, each smoke-tested against your test terminal/CAT before any production change.
- **Validation gates go-live** — always a tracked, explicit step; never presented as optional.
- Payment-related features added after validation require revalidation with J.P. Morgan.
- If asked for an operation not in `references/official-transaction-recipes.md`, say it isn't covered yet rather than inventing an envelope; check `references/official-protocol-reference.md` for whether the operation exists in the protocol.
