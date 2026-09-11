# In-Store Network Readiness Checklist

The POS connects to the terminal over a **TLS WebSocket** on the local network:

```
wss://<terminal-ip>:8442
```

Port **8442** is the terminal's WebSocket listening port (the real terminal contract). Work through each item below before attempting a connection. This is the material behind Step 4 of `jpm-instore-get-started`.

## 1. Terminal IP addressing

| Check | Why it matters |
|---|---|
| Terminal has a **stable IP** (static or DHCP reservation) | The POS targets the terminal by IP; a changing IP breaks the connection. |
| Terminal and POS are on the **same LAN / VLAN** (or a routable path exists) | Semi-integrated is a *local* connection — it is not intended to traverse the public internet. |

Record the terminal IP in your config file (`JPM_TERMINAL_HOST` in `instore.env`, or `jpm.terminal.host` in `local.properties` for Android).

## 2. Reachability

- From the POS host, confirm the terminal IP is reachable on the network (same subnet or a routed path).
- If the POS and terminal are on isolated VLANs, ensure an explicit route/allow rule exists between them.

## 3. Firewall

| Rule | Direction |
|---|---|
| Allow TCP **8442** between the POS host and the terminal | POS → terminal (client to server) |

- Host-based firewalls on the POS machine and any network firewall/segmentation between POS and terminal must permit **8442**.
- If a security appliance does TLS inspection/interception on the segment, it can break the terminal's certificate trust — exclude the terminal ↔ POS path from interception.

## 4. Port

- Confirm **8442** is not blocked, remapped, or already in use by another service on the terminal's address.
- Do not assume a different port — the terminal listens on 8442 for the semi-integrated WebSocket.

## 5. TLS

- The transport is **`wss://` (TLS 1.2)** — plaintext `ws://` is only used by a local mock during early testing.
- The POS client must **trust the terminal's certificate** (or be configured with the trust material provided during onboarding).
- Never disable certificate validation in production code. A permissive trust manager is acceptable **only** against a local mock during development and must never ship to PROD.

## Quick verification

Once the above pass, the POS should be able to open the socket and receive the terminal's readiness `Status` notification (`{"operation":"Status","context":"Maintenance","result":"101"}`) on connect. If the socket opens but no readiness `Status` arrives, re-check TLS trust and that the terminal application is running. If the socket never opens, re-check IP, reachability, firewall, and port.

> Connectivity working in your lab does **not** equal production readiness. Go-live is gated by J.P. Morgan validation — keep that as a tracked step.

---

## References

LLM-friendly (markdown) source pages on the J.P. Morgan Payments Developer Portal:

- [Core concepts (connectivity, security, environments)](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fin-store-payments%2F3coreconcepts-instorepay.md)
- [Certificate handling (TLS/mTLS)](https://developer.payments.jpmorgan.com/docs/commerce/in-store-payments/capabilities/payment-terminal-application/certificate-handling)
