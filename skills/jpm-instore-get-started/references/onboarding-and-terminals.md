# Onboarding Artifacts & Supported Terminals

## What J.P. Morgan provisions

The Payment Terminal Application is **pre-certified and provisioned by J.P. Morgan** on the Ingenico AXIUM terminal. As the POS developer you do **not** build or install the payment app — you talk to it over the semi-integrated WebSocket. What you receive during onboarding:

| Artifact | Purpose | Where it's used |
|---|---|---|
| **HWVENDORID** | Mandatory identifier assigned by J.P. Morgan | Set at startup via `SetParameter` as the **first POS-sent terminal operation** after readiness. Stored in your config file as `JPM_HWVENDORID` (`instore.env`) or `jpm.hwvendorid` (`local.properties`, Android). |
| **TLS certificate / trust material** | Lets the POS trust the terminal's `wss://` endpoint | POS WebSocket client configuration. |
| **Supported terminal(s)** | The physical AXIUM device(s) | Card interaction happens here — never on the POS. |
| **Pre-configured test terminals** | Safe protocol testing before production | Proves send/receive, operation sequencing, and broken-connection behavior. Official validation still happens on real hardware. |
| **EMV test cards** | Required test inputs for card-present validation | Used with the official test scripts and amount/response scenarios. |
| **Validation worksheet** | The go-live checklist J.P. Morgan runs on real hardware | Gates production. Tracked, not optional. |
| **Implementation contact / RM** | Who to reach for onboarding and validation | Escalation + go-live scheduling. |
| **Production environment details** | URLs, IP address blocks, and production rollout details | Provided after successful validation; do not guess or self-provision. |

If any of these are missing, the developer is **not yet onboarded** — route them back to their J.P. Morgan implementation contact / Relationship Manager (Step 8 of `jpm-instore-get-started`).

## Validation readiness

- The integration agent coordinates test hardware and the validation worksheet.
- The developer orders or obtains the required EMV test card set before formal testing.
- Production environment details are provided only after successful validation.
- Any new payment API or significant payment-flow change after validation requires revalidation.

## Supported Ingenico AXIUM terminal models

See `terminals-and-operations.md` for the shared terminal and operation catalogue.

## The HWVENDORID rule

`HWVENDORID` is the single most common reason a terminal rejects requests in a new integration. It **must** be set via `SetParameter` at the start of every session, as the first POS-sent terminal operation after readiness. The `jpm-instore-payments` skill enforces this ordering; the config file (`instore.env`, or `local.properties` for Android) carries the value as a placeholder so it is never committed.

---

## References

LLM-friendly (markdown) source pages on the J.P. Morgan Payments Developer Portal:

- [Payment terminals overview (countertop / mobile / portable)](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fin-store-payments%2Fcapabilities%2Fpayment-terminals-overview.md)
- [Payment Terminal Application overview](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fin-store-payments%2Fcapabilities%2Fpayment-terminal-application%2Foverview-payment-terminal-app.md)
- [Configuration parameters (`HWVENDORID`)](https://developer.payments.jpmorgan.com/docs/commerce/in-store-payments/capabilities/payment-terminal-application/configuration-parameters)
