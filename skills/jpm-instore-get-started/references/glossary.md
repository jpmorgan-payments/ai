# Beginner Glossary — In-Store Payments

New to card-present payments? Meet **Ultimate LLC** — a small cafe-and-apparel business. Dana (operations owner) decided to accept in-store payments; Priya (POS developer) is doing the integration; Marcus (cashier) and Sofia (store manager) use it every day. The terms below are exactly what Priya has to learn.

| Term | Meaning |
|---|---|
| **Card-present / in-store** | The physical card, phone, or watch is tapped, inserted, or swiped at a terminal — as opposed to an online/e-commerce payment. |
| **Payment Terminal Application** | J.P. Morgan's pre-certified app that runs on the Ingenico terminal and talks to the card and the payment network. Priya does **not** build this — she talks to it. |
| **POS** | Point-of-sale software — the register/checkout system Marcus uses. For Ultimate LLC this is "UltimatePOS". |
| **Semi-integrated** | The POS and terminal are **separate**. The POS sends requests (like "SALE $5.00") to the terminal over a WebSocket, and the terminal handles the card. This is the primary v1 model. |
| **On-device** | The full checkout app runs *on the terminal itself*. Conceptual only for v1. |
| **SDK** | A software development kit that hides lower-level terminal/API details. Conceptual only for v1. |
| **WebSocket / WSS** | A persistent, two-way connection between POS and terminal. `wss://` means it's secured with TLS. The terminal listens on **port 8442**. |
| **TLS** | Transport-layer security — the encryption that makes `ws://` into `wss://`. |
| **HWVENDORID** | A mandatory identifier J.P. Morgan assigns Ultimate LLC. Priya must set it via `SetParameter` at startup or the terminal rejects transactions. |
| **Amount in cents** | Money is sent as an integer number of cents. `$10.00` = `1000`. Getting this wrong charges the wrong amount. |
| **Store and Forward (SAF)** | If the internet hiccups, the terminal can approve within configured limits and forward the transaction later. |
| **DCC** | Dynamic Currency Conversion — lets a foreign cardholder pay in their home currency. The terminal presents the choice. |
| **Settlement** | Batching the day's captured transactions to move the money. Sofia does this at nightly close. |
| **CAT** | Customer Acceptance Testing — J.P. Morgan's test environment. You validate here before PROD. |
| **Validation** | J.P. Morgan's go-live gate: they run a worksheet on real hardware before Ultimate LLC can take live payments. |

## The Ultimate LLC journey, end to end

1. **Decide & onboard** — Dana signs up; J.P. Morgan provisions terminals and issues the HWVENDORID, certificate, and validation worksheet.
2. **Get started** — Priya runs `jpm-instore-get-started` (this skill's family): triage, network check, and a language-appropriate config file (`instore.env`, or `local.properties` for Android).
3. **Build** — `jpm-instore-payments`: SALE, tip, AUTH→COMPLETION, REFUND, VOID, gift cards, line items, SAF, DCC, settlement — one operation at a time.
4. **Certify & launch** — J.P. Morgan runs the validation worksheet on real hardware; go-live is scheduled.
5. **Operate & scale** — busy Saturdays, nightly close, then reuse the same integration across more stores.

Every term above appears in the other in-store skills. When one confuses you, come back here.

---

## References

LLM-friendly (markdown) source pages on the J.P. Morgan Payments Developer Portal:

- [In-Store Payments overview](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fin-store-payments%2F1overview-instorepay.md)
- [Core concepts (key identifiers, WebSocket API)](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fin-store-payments%2F3coreconcepts-instorepay.md)
