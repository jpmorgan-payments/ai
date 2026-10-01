# Sample Checkout App using J.P. Morgan Drop-in UI Checkout Component

This a single file sample application demonstrating how to integrate the J.P. Morgan Checkout API using the Drop-in UI component.

```js
// ════════════════════════════════════════════════════════════════════
// J.P. Morgan Drop-in Checkout — SINGLE-FILE SAMPLE
// ════════════════════════════════════════════════════════════════════
//
// Everything in one file: config, server, and inline HTML/JS.
// Run with:  npm install express undici && node server.js
// Open:      http://localhost:3000
//
// FLOW OVERVIEW
// ─────────────
// 1. AUTH — Server authenticates with JPM via OAuth2
//    (client_credentials + JWT assertion) → gets Bearer token.
//
// 2. CHECKOUT INTENT — Server creates a checkout session via
//    POST /v1/checkout/intent → receives checkoutSessionToken.
//
// 3. DROP-IN UI — Browser loads the JPM Drop-in UI script,
//    mounts it with the token. The Drop-in renders a payment
//    form, encrypts card data, and submits directly to JPM.
//    Your server never touches card data.
//
// 4. PAYMENT EVENTS — The Drop-in fires PaymentSuccess or
//    PaymentUnsuccessful events via its subscribe() callback.
//
// 5. VERIFICATION — After PaymentSuccess, the browser calls
//    the server's notifications endpoint, which queries
//    GET /v1/checkout/notifications to verify the transaction.
//
// ════════════════════════════════════════════════════════════════════

const express = require("express");
const crypto = require("crypto");
const { fetch, ProxyAgent } = require("undici");

// Auth module created by the `jpm-oauth` skill. Adjust the path to
// match where it was generated in your project. Provides a cached
// `getAccessToken()` that handles the OAuth2 client_credentials +
// JWT assertion flow against IDAnywhere — never re-implement that
// inline; the imported function already caches and refreshes per
// JPM guidance.
const { getAccessToken } = require("./auth/jpmAuth");

const app = express();
app.use(express.json());

// ══════════════════════════════════════════════════════════════════
// CONFIGURATION — Checkout-specific values
// ══════════════════════════════════════════════════════════════════
// JPM auth (clientId, cert, key, thumbprint, resource_id) is owned
// by the auth module above — those vars live in `.env` and are
// read by `getAccessToken()` at runtime.
const CONFIG = {
  MERCHANT_ID: process.env.JPM_MERCHANT_ID,
  CHECKOUT_API_URL:
    process.env.JPM_CHECKOUT_API_URL ??
    "https://merchant-api.checkout-cat.merchant.jpmorgan.com/v1",

  // Optional: corporate proxy for the Checkout API
  HTTPS_PROXY: process.env.HTTPS_PROXY ?? "",
};
// ══════════════════════════════════════════════════════════════════

// ── Proxy dispatcher ─────────────────────────────────────────────
// If you're behind a corporate proxy, set HTTPS_PROXY in your env.
const proxyDispatcher = CONFIG.HTTPS_PROXY
  ? new ProxyAgent(CONFIG.HTTPS_PROXY)
  : undefined;

// ── Helper: generate a short unique ID (max 22 chars) ────────────
// JPM requires merchantOrderNumber and requestId to be ≤ 22 chars.
// We use crypto.randomUUID(), strip dashes, and take 22 characters.
function shortId() {
  return crypto.randomUUID().replace(/-/g, "").slice(0, 22);
}

// ══════════════════════════════════════════════════════════════════
// STEP 2 — Create Checkout Session (Checkout Intent)
// ══════════════════════════════════════════════════════════════════
//
// POST /api/create-checkout-session
//
// The browser calls this endpoint with { amount } in the body.
// The server:
//   a) Gets an OAuth2 Bearer token (Step 1, cached)
//   b) Calls POST /v1/checkout/intent with the cart details
//   c) Returns { checkoutSessionToken, merchantOrderNumber }
//
// The checkoutSessionToken is what the Drop-in UI needs to render
// the payment form. The merchantOrderNumber is used later to verify
// the transaction via the notifications API.
//
// CRITICAL CONSTRAINTS:
//   • merchantId header — must be camelCase (not kebab-case)
//   • requestId header — must be camelCase, max 22 chars
//   • merchantOrderNumber — max 22 chars
//   • totalTransactionAmount — integer in cents (not dollars)
// ══════════════════════════════════════════════════════════════════
app.post("/api/create-checkout-session", async (req, res) => {
  try {
    const { amount } = req.body;
    const accessToken = await getAccessToken();
    const merchantOrderNumber = shortId();
    const requestId = shortId();

    const payload = {
      merchantOrderNumber,
      currencyCode: "USD",
      cart: { totalTransactionAmount: amount },
      consumer: {
        email: "customer@example.com",
        billingAddress: {
          recipientFullName: "John Smith",
          line1: "1 Main St",
          city: "San Francisco",
          state: "CA",
          country: "US",
          postalCode: "95000",
        },
      },
      checkoutOptions: {
        authorization: { authorizationType: "AUTH_METHOD_CART_AMOUNT" },
        capture: { captureMethod: "CAPTURE_METHOD_NOW" },
        consumerProfileOptions: { isSaveConsumerProfile: "false" },
      },
    };

    const intentRes = await fetch(
      `${CONFIG.CHECKOUT_API_URL}/checkout/intent`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${accessToken}`,
          merchantId: CONFIG.MERCHANT_ID, // camelCase — NOT "merchant-id"
          requestId, // camelCase, ≤22 chars
        },
        body: JSON.stringify(payload),
        dispatcher: proxyDispatcher,
      }
    );

    if (!intentRes.ok) {
      const text = await intentRes.text();
      throw new Error(`Checkout intent failed (${intentRes.status}): ${text}`);
    }

    const data = await intentRes.json();

    // Return the token and order number to the browser
    res.json({
      checkoutSessionToken: data.checkoutSessionToken,
      merchantOrderNumber,
    });
  } catch (err) {
    console.error("create-checkout-session error:", err);
    res.status(500).json({ error: err.message });
  }
});

// ══════════════════════════════════════════════════════════════════
// STEP 3 — Payment Verification via Notifications
// ══════════════════════════════════════════════════════════════════
//
// GET /api/notifications/:merchantOrderNumber
//
// After the Drop-in UI fires PaymentSuccess on the client, the
// browser calls this endpoint to verify the transaction server-side.
//
// The server calls:
//   GET /v1/checkout/notifications
//     ?merchantOrderNumber=<order>
//     &periodStart=<29 days ago>   ← must be within 30 days
//     &periodEnd=<now>
//
// The response contains an array of messages with:
//   • orderNotification — transaction details (status, amount, card, etc.)
//   • tokenNotification — acquirer token and fraud check result
//
// IMPORTANT: Never trust the client-side PaymentSuccess event alone.
// Always verify on the server via this notifications API.
// ══════════════════════════════════════════════════════════════════
app.get("/api/notifications/:merchantOrderNumber", async (req, res) => {
  try {
    const { merchantOrderNumber } = req.params;
    const accessToken = await getAccessToken();
    const requestId = shortId();

    // Use 29 days (not 30) to avoid precision boundary errors
    const periodEnd = new Date().toISOString();
    const periodStart = new Date(Date.now() - 29 * 24 * 60 * 60 * 1000).toISOString();

    const url =
      `${CONFIG.CHECKOUT_API_URL}/checkout/notifications` +
      `?merchantOrderNumber=${encodeURIComponent(merchantOrderNumber)}` +
      `&periodStart=${periodStart}` +
      `&periodEnd=${periodEnd}`;

    const nRes = await fetch(url, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${accessToken}`,
        merchantId: CONFIG.MERCHANT_ID,
        requestId,
      },
      dispatcher: proxyDispatcher,
    });

    if (!nRes.ok) {
      const text = await nRes.text();
      throw new Error(`Notifications failed (${nRes.status}): ${text}`);
    }

    const data = await nRes.json();
    res.json(data);
  } catch (err) {
    console.error("notifications error:", err);
    res.status(500).json({ error: err.message });
  }
});

// ══════════════════════════════════════════════════════════════════
// INLINE HTML — Served for all non-API routes
// ══════════════════════════════════════════════════════════════════
//
// The entire frontend lives in this template string: HTML, CSS,
// and client-side JS. No separate files needed.
// ══════════════════════════════════════════════════════════════════
const HTML = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>J.P. Morgan Drop-in Checkout &mdash; Single-File Demo</title>

  <!--
    Load the JPM Drop-in UI script (ES module).
    This registers the global DropInUI class.
    The URL must match the environment used for the checkout intent
    (CAT script = CAT API, production script = production API).
  -->
  <script type="module" src="https://checkout-cat.merchant.jpmorgan.com/drop-in-ui.mjs"><\/script>

  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: #f5f5f5;
      color: #1a1a1a;
      line-height: 1.6;
    }

    header {
      background: #0a2540;
      color: #fff;
      padding: 1.5rem 2rem;
      text-align: center;
    }
    header h1 { font-size: 1.5rem; font-weight: 600; }
    header p  { font-size: 0.875rem; opacity: 0.8; margin-top: 0.25rem; }

    main {
      max-width: 600px;
      margin: 2rem auto;
      padding: 0 1rem;
    }

    .screen { display: none; }
    .screen.active { display: block; }

    .product-card {
      background: #fff;
      border-radius: 12px;
      padding: 2rem;
      box-shadow: 0 2px 8px rgba(0,0,0,0.08);
      text-align: center;
    }
    .product-card h2 { font-size: 1.25rem; margin-bottom: 0.5rem; }
    .product-card .price { font-size: 2rem; font-weight: 700; color: #0a2540; }
    .product-card p { color: #555; margin: 0.5rem 0 1.5rem; }

    button.pay-btn {
      background: #0a2540;
      color: #fff;
      border: none;
      border-radius: 8px;
      padding: 0.875rem 2rem;
      font-size: 1rem;
      cursor: pointer;
      transition: background 0.2s;
    }
    button.pay-btn:hover { background: #163a5f; }
    button.pay-btn:disabled { opacity: 0.5; cursor: not-allowed; }

    .checkout-wrapper {
      background: #fff;
      border-radius: 12px;
      padding: 2rem;
      box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    .checkout-wrapper h2 { margin-bottom: 1rem; }

    #dropin-container { min-height: 200px; position: relative; }

    .spinner { text-align: center; padding: 3rem 0; color: #888; }

    .back-link {
      display: inline-block;
      margin-bottom: 1rem;
      color: #0a2540;
      text-decoration: none;
      font-size: 0.875rem;
    }
    .back-link:hover { text-decoration: underline; }

    .success-card {
      background: #fff;
      border-radius: 12px;
      padding: 2rem;
      box-shadow: 0 2px 8px rgba(0,0,0,0.08);
      text-align: center;
    }
    .success-card .checkmark { font-size: 3rem; color: #22c55e; margin-bottom: 0.5rem; }
    .success-card h2 { color: #22c55e; margin-bottom: 1rem; }

    .details-table { width: 100%; text-align: left; border-collapse: collapse; margin-top: 1rem; }
    .details-table th,
    .details-table td { padding: 0.5rem 0.75rem; border-bottom: 1px solid #eee; font-size: 0.875rem; }
    .details-table th { color: #888; font-weight: 500; width: 40%; }

    .error-msg {
      background: #fef2f2;
      color: #dc2626;
      border: 1px solid #fecaca;
      border-radius: 8px;
      padding: 1rem;
      margin-top: 1rem;
      font-size: 0.875rem;
    }
  </style>
</head>
<body>
  <header>
    <h1>J.P. Morgan Drop-in Checkout</h1>
    <p>Single-file integration sample</p>
  </header>

  <main>
    <!-- SCREEN 1 — PRODUCT: simple card with a "Pay Now" button -->
    <div id="screen-product" class="screen active">
      <div class="product-card">
        <h2>Premium Widget</h2>
        <div class="price">$49.99</div>
        <p>A beautifully crafted widget for demonstration purposes.</p>
        <button class="pay-btn" id="btn-pay">Pay Now</button>
      </div>
    </div>

    <!-- SCREEN 2 — CHECKOUT: Drop-in UI mounts inside #dropin-container -->
    <div id="screen-checkout" class="screen">
      <a href="#" class="back-link" id="btn-back">&larr; Back to product</a>
      <div class="checkout-wrapper">
        <h2>Checkout &mdash; $49.99</h2>
        <div id="dropin-container">
          <div class="spinner" id="checkout-spinner">Loading payment form&hellip;</div>
        </div>
      </div>
    </div>

    <!-- SCREEN 3 — SUCCESS: verified transaction details -->
    <div id="screen-success" class="screen">
      <div class="success-card">
        <div class="checkmark">&check;</div>
        <h2>Payment Successful!</h2>
        <p id="success-message">Verifying transaction details&hellip;</p>
        <table class="details-table" id="details-table" style="display:none;">
          <tbody id="details-body"></tbody>
        </table>
        <div id="verification-error" class="error-msg" style="display:none;"></div>
        <button class="pay-btn" style="margin-top:1.5rem;" onclick="location.reload()">
          Start Over
        </button>
      </div>
    </div>
  </main>

  <script>
    (function () {
      "use strict";

      // Amount in cents ($49.99 = 4999). JPM expects the smallest currency unit.
      var AMOUNT_CENTS = 4999;

      var screenProduct  = document.getElementById("screen-product");
      var screenCheckout = document.getElementById("screen-checkout");
      var screenSuccess  = document.getElementById("screen-success");
      var btnPay         = document.getElementById("btn-pay");
      var btnBack        = document.getElementById("btn-back");
      var spinner        = document.getElementById("checkout-spinner");
      var successMessage = document.getElementById("success-message");
      var detailsTable   = document.getElementById("details-table");
      var detailsBody    = document.getElementById("details-body");
      var verifyError    = document.getElementById("verification-error");
      var dropinInstance  = null;

      function showScreen(screen) {
        screenProduct.classList.remove("active");
        screenCheckout.classList.remove("active");
        screenSuccess.classList.remove("active");
        screen.classList.add("active");
      }

      // ────────────────────────────────────────────────────────────
      // BROWSER STEP A — Request a checkout session from our server.
      //
      // The server authenticates with JPM (OAuth2) and creates a
      // checkout intent, returning { checkoutSessionToken, merchantOrderNumber }.
      // ────────────────────────────────────────────────────────────
      async function createCheckoutSession() {
        var res = await fetch("/api/create-checkout-session", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ amount: AMOUNT_CENTS }),
        });
        if (!res.ok) {
          var err = await res.json().catch(function () { return {}; });
          throw new Error(err.error || "Server returned " + res.status);
        }
        return res.json();
      }

      // ────────────────────────────────────────────────────────────
      // BROWSER STEP B — Mount the JPM Drop-in UI.
      //
      // 1. Wait for DropInUI to load (async ES module).
      // 2. Create instance with the checkoutSessionToken.
      // 3. Mount into #dropin-container — JPM renders the card form.
      // 4. Subscribe to lifecycle events.
      // ────────────────────────────────────────────────────────────
      async function mountDropInUI(token, orderNumber) {
        await waitForDropInUI();

        var dropin = new window.DropInUI({ checkoutSessionToken: token });
        dropin.mount("dropin-container");
        dropinInstance = dropin;

        // ──────────────────────────────────────────────────────────
        // BROWSER STEP C — Handle Drop-in UI events.
        //
        // Key events:
        //   MountSuccess        — form rendered, hide spinner
        //   PaymentSuccess      — payment done, verify server-side
        //   PaymentUnsuccessful — declined, user can retry
        //   PaymentError        — request-level error
        //   UnknownError        — unrecoverable
        // ──────────────────────────────────────────────────────────
        dropin.subscribe(function (event) {
          console.log("[Drop-in event]", event);

          if (event.message === "MountSuccess") {
            spinner.style.display = "none";
          }

          if (event.namespace === "payment" && event.level === "info") {
            if (event.message === "PaymentSuccess") {
              unmountDropIn();
              showScreen(screenSuccess);
              verifyPayment(orderNumber);
            }
            if (event.message === "PaymentUnsuccessful") {
              console.warn("Payment unsuccessful — user can retry.");
            }
          }

          if (event.level === "error") {
            console.error("Drop-in error:", event.message, event);
          }
        });
      }

      function waitForDropInUI() {
        return new Promise(function (resolve, reject) {
          if (window.DropInUI) return resolve();
          var attempts = 0;
          var iv = setInterval(function () {
            attempts++;
            if (window.DropInUI) { clearInterval(iv); resolve(); }
            else if (attempts > 100) { clearInterval(iv); reject(new Error("Drop-in UI script failed to load.")); }
          }, 100);
        });
      }

      function unmountDropIn() {
        if (dropinInstance) { dropinInstance.unmount(); dropinInstance = null; }
      }

      // ────────────────────────────────────────────────────────────
      // BROWSER STEP D — Verify the payment via notifications API.
      //
      // After PaymentSuccess, calls the server which queries
      // GET /v1/checkout/notifications to confirm the transaction.
      //
      // IMPORTANT: Never trust the client-side event alone.
      // Always verify on the server.
      // ────────────────────────────────────────────────────────────
      async function verifyPayment(merchantOrderNumber) {
        try {
          var res = await fetch("/api/notifications/" + encodeURIComponent(merchantOrderNumber));
          if (!res.ok) throw new Error("Verification failed: " + res.status);

          var data = await res.json();
          console.log("[Notifications]", data);

          var orderMsg = null;
          if (data.messages) {
            for (var i = 0; i < data.messages.length; i++) {
              if (data.messages[i].orderNotification) {
                orderMsg = data.messages[i].orderNotification;
                break;
              }
            }
          }

          if (orderMsg && orderMsg.status === "STATUS_SUCCESS") {
            successMessage.textContent = "Transaction verified successfully.";
            displayDetails(orderMsg);
          } else if (orderMsg) {
            successMessage.textContent = "Payment status: " + (orderMsg.responseCode || "UNKNOWN");
          } else {
            successMessage.textContent = "Payment completed! Verification details are being processed.";
          }
        } catch (err) {
          console.error("Verification error:", err);
          verifyError.style.display = "block";
          verifyError.textContent = "Could not verify transaction: " + err.message;
        }
      }

      function displayDetails(order) {
        var pm = order.paymentMethod || {};
        var rows = [
          ["Status",          order.responseCode],
          ["Message",         order.responseMessage],
          ["Order Number",    order.merchantOrderNumber],
          ["Transaction Ref", order.transactionReference],
          ["Card",            pm.maskedAccountNumber],
          ["Card Type",       pm.card ? pm.card.cardTypeName : null],
          ["Approval Code",   pm.approvalCode],
          ["Amount",          order.totalAmount ? "$" + (parseInt(order.totalAmount.amount, 10) / 100).toFixed(2) : null],
          ["Timestamp",       order.transactionTimestamp ? new Date(order.transactionTimestamp).toLocaleString() : null],
        ];
        detailsBody.innerHTML = "";
        for (var i = 0; i < rows.length; i++) {
          var tr = document.createElement("tr");
          var th = document.createElement("th"); th.textContent = rows[i][0];
          var td = document.createElement("td"); td.textContent = rows[i][1] || "\\u2014";
          tr.appendChild(th); tr.appendChild(td);
          detailsBody.appendChild(tr);
        }
        detailsTable.style.display = "table";
      }

      // ── Wire up buttons ──────────────────────────────────────────
      btnPay.addEventListener("click", async function () {
        btnPay.disabled = true;
        btnPay.textContent = "Loading\\u2026";
        try {
          var session = await createCheckoutSession();
          showScreen(screenCheckout);
          spinner.style.display = "block";
          await mountDropInUI(session.checkoutSessionToken, session.merchantOrderNumber);
        } catch (err) {
          console.error("Checkout setup error:", err);
          alert("Failed to start checkout: " + err.message);
        } finally {
          btnPay.disabled = false;
          btnPay.textContent = "Pay Now";
        }
      });

      btnBack.addEventListener("click", function (e) {
        e.preventDefault();
        unmountDropIn();
        document.getElementById("dropin-container").innerHTML =
          '<div class="spinner" id="checkout-spinner">Loading payment form&hellip;</div>';
        showScreen(screenProduct);
      });
    })();
  <\/script>
</body>
</html>`;

// Serve the inline HTML for all non-API routes
app.get("*", (_req, res) => {
  res.setHeader("Content-Type", "text/html");
  res.send(HTML);
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () =>
  console.log(`Single-file checkout running → http://localhost:${PORT}`)
);

```
