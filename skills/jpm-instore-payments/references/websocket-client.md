# Minimal WebSocket Client - In-Store Semi-Integrated Terminal

Match the public terminal contract in the official protocol reference: responses echo the
request `operation`, progress/readiness arrives as `Status`, result codes are numeric
strings, transaction outcome is `approval`, and `SetParameter`/`GetParameter` use a
`parameters` array.

A self-contained POS client for the semi-integrated terminal protocol. It opens one `wss://` connection to the terminal on **port 8442**, sends JSON envelopes discriminated by an `operation` field, and resolves each request on the matching terminal message.

- Every request resolves on the response that **echoes its `operation`** value.
- Asynchronous progress + readiness arrive as `Status` notifications (`operation:"Status"`, `context`, `result`), surfaced via `onStatus`; readiness is `context:"Maintenance"`, `result:"101"`.
- After readiness, the first POS-sent terminal operation is `SetParameter` for `HWVENDORID`.
- A non-`"0"` `result` (numeric string) is surfaced as an error; a transaction's financial outcome is in `approval`.

All monetary amounts are **cents** (integer/numeric string): `$5.00` = `500`.

> **The envelope contract is language-agnostic.** The Node.js and Kotlin/Android snippets below are worked examples. Generate your client in the language chosen in the skill (`language`), keeping the same operations, field names, match rules, and cents amounts. Any WebSocket library works.

## Node.js (`ws`)

```bash
npm install ws
```

```javascript
// terminalClient.mjs
import { WebSocket } from 'ws';

export class TerminalClient {
  // Real terminal: wss://<host>:8442
  constructor(url = 'wss://127.0.0.1:8442', { rejectUnauthorized = true } = {}) {
    this.url = url;
    this.rejectUnauthorized = rejectUnauthorized; // set false ONLY for a local self-signed test certificate
    this.ws = null;
    this.ready = false;
    this.readyInfo = null;
    this._waiters = [];        // { match(msg)->bool, resolve, reject }
    this._statusListeners = [];
  }

  connect() {
    return new Promise((resolve, reject) => {
      // rejectUnauthorized:false is a DEVELOPMENT-ONLY shortcut for a self-signed
      // test cert. Production MUST trust the real terminal certificate.
      this.ws = new WebSocket(this.url, { rejectUnauthorized: this.rejectUnauthorized });
      this.ws.on('error', reject);
      this.ws.on('close', () => { this.ready = false; });
      this.ws.on('message', (raw) => {
        let msg;
        try { msg = JSON.parse(raw.toString()); } catch { return; }

        // Asynchronous progress + readiness arrive as Status notifications:
        // { operation: 'Status', context: '...', result: '...' }
        if (msg.operation === 'Status') {
          // Readiness: context Maintenance, result '101' (app started).
          if (msg.context === 'Maintenance' && String(msg.result) === '101') {
            this.ready = true;
            this.readyInfo = msg;
            resolve(msg);
          }
          // Surface every Status notification for UI/debug; never resolve a request.
          this._statusListeners.forEach((cb) => cb(msg));
          return;
        }
        // A response echoes the request's `operation`. Resolve the first matching waiter.
        const idx = this._waiters.findIndex((w) => w.match(msg));
        if (idx !== -1) {
          const [w] = this._waiters.splice(idx, 1);
          w.resolve(msg);
        }
      });
    });
  }

  onStatus(cb) { this._statusListeners.push(cb); }
  close() { this.ws?.close(); }

  _send(envelope, matchFn) {
    return new Promise((resolve, reject) => {
      if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
        return reject(new Error('socket_not_open'));
      }
      this._waiters.push({
        match: matchFn,
        resolve: (msg) => {
          // `result` is a NUMERIC string; "0" means the operation ran. A non-"0"
          // result is an operation error (NOT a decline — a decline is a resolved
          // Transaction with approval:"declined").
          if (msg.result !== undefined && String(msg.result) !== '0') {
            const e = new Error(msg.errorMessage || msg.hostMessage || `result ${msg.result}`);
            e.result = String(msg.result);
            e.payload = msg;
            return reject(e);
          }
          resolve(msg);
        },
        reject,
      });
      this.ws.send(JSON.stringify(envelope));
    });
  }

  // --- Transaction: response echoes operation:"Transaction" ---
  // amount is in cents. A declined result is a RESOLVED response with
  // approval:"declined" (result:"0") — it is NOT thrown.
  transaction(fields) {
    const env = { operation: 'Transaction', ...fields };
    return this._send(env, (m) => m.operation === 'Transaction');
  }
  sale({ amount, reference, tipAmount, printReceipt = '1' }) {
    return this.transaction({
      type: 'SALE',
      requestedAmount: String(amount),
      ...(reference && { reference }),
      ...(tipAmount != null && { tipAmount: String(tipAmount) }),
      printReceipt,
    });
  }
  refund({ amount, reference, cardToken, expDate, printReceipt = '1' }) {
    return this.transaction({
      type: 'REFUND', requestedAmount: String(amount),
      ...(reference && { reference }),
      ...(cardToken && { cardToken, ...(expDate && { expDate }), storedCredential: '1' }),
      printReceipt,
    });
  }
  auth(a)       { return this.transaction({ type: 'AUTHORIZATION', requestedAmount: String(a.amount), ...(a.reference && { reference: a.reference }) }); }
  completion(a) { return this.transaction({ type: 'COMPLETION', requestedAmount: String(a.amount), originalAuthCode: a.originalAuthCode }); }
  voidTxn(a)    { return this.transaction({ type: 'VOID', originalAuthCode: a.originalAuthCode }); }
  forceSale(a)  { return this.transaction({ type: 'FORCE_SALE', requestedAmount: String(a.amount), originalAuthCode: a.originalAuthCode }); }
  motoSale(a)   { return this.transaction({ type: 'MOTO_SALE', requestedAmount: String(a.amount), order: a.order }); }
  statusCheck(fields = {})   { return this.transaction({ type: 'STATUS_CHECK', ...fields }); }
  balanceInquiry(fields = {}) { return this.transaction({ type: 'BALANCE_INQUIRY', ...fields }); }

  // --- Generic operations: resolve on the matching echoed operation ---
  _op(operation, extra = {}) {
    return this._send({ operation, ...extra }, (m) => m.operation === operation);
  }
  getInformation()          { return this._op('GetInformation'); }
  // SetParameter/GetParameter take a `parameters` ARRAY of {key,value} objects
  // (per the official docs), NOT a top-level key/value pair.
  setParameter(key, value)  { return this._op('SetParameter', { parameters: [{ key, value }] }); }
  getParameter(key)         { return this._op('GetParameter', { parameters: [{ key }] }); }
  settle()                  { return this.transaction({ type: 'SETTLEMENT' }); }
  getTransactions(type = 'ALL_SALES') { return this._op('GetTransactions', { type }); }
  lastTransaction()         { return this._op('LastTransaction'); }
  getSaf()                  { return this._op('GetTransactions', { type: 'ALL_SAF' }); } // SAF queue
  printText(text)           { return this._op('PrintText', { text }); }
  lineItems({ title, lineItems, subTotals, totals }) { return this._op('LineItems', { title, lineItems, ...(subTotals && { subTotals }), ...(totals && { totals }) }); }
  readCard({ cardType = '1', timeout = '0' } = {}) { return this._op('ReadCard', { cardType, timeout }); }
  cancel()                  { return this._op('Cancel'); }
  restart()                 { return this._op('Restart'); }
  generateCsr(fields)       { return this._op('GenerateCsr', fields); }
  importCertificate(fields) { return this._op('ImportCertificate', fields); }
  installTrustCertificate(fields) { return this._op('InstallTrustCertificate', fields); }
}
```

### Walk one lifecycle

```javascript
import { TerminalClient } from './terminalClient.mjs';

const client = new TerminalClient('wss://127.0.0.1:8442', { rejectUnauthorized: false });
client.onStatus((s) => console.log('progress:', s.type, s.message ?? ''));

await client.connect();                       // waits for readiness Status (Maintenance/101)
console.log('ready:', client.readyInfo);

await client.setParameter('HWVENDORID', process.env.JPM_HWVENDORID); // MANDATORY first POS-sent operation
await client.getInformation();                // read-only sanity check after HWVENDORID

const sale = await client.sale({ amount: 500, printReceipt: '1' });   // $5.00
console.log('approved:', sale.approval === 'approved', 'auth:', sale.authCode, 'brand:', sale.cardBrand);

client.close();
```

## Kotlin / Android (real terminal shape)

The real terminal is reached the same way from an Android POS. The in-repo reference is `apps/shellapp/src/semi/.../POSWebsocketClientService.kt`. The essentials:

```kotlin
val serverUri = URI.create("wss://127.0.0.1:8442")

val client = object : WebSocketClient(serverUri) {
    override fun onOpen(handshake: ServerHandshake?) { /* wait for readiness Status (Maintenance/101) */ }
    override fun onMessage(message: String?) { /* parse JSON, dispatch by "operation" */ }
    override fun onClose(code: Int, reason: String?, remote: Boolean) { /* mark disconnected */ }
    override fun onError(ex: Exception?) { /* log + recover */ }
}.apply {
    // DEV-ONLY permissive trust manager for a self-signed test cert.
    // Production must trust the real terminal certificate.
    setSocketFactory(devSslContext().socketFactory)
}
client.connect()

// Send a SALE:
client.send("""{"operation":"Transaction","type":"SALE","requestedAmount":"500","printReceipt":"1"}""")
```

Do all socket I/O off the UI thread and keep the UI responsive.

## Envelope quick reference

| Operation | Send envelope | Resolves on |
| --- | --- | --- |
| Readiness (pushed) | — (terminal sends on connect) | `Status` `Maintenance`/`"101"` |
| Terminal info | `{"operation":"GetInformation"}` | echoes `GetInformation` |
| Set HWVENDORID | `{"operation":"SetParameter","parameters":[{"key":"HWVENDORID","value":"…"}]}` | echoes `SetParameter` |
| Get parameter | `{"operation":"GetParameter","parameters":[{"key":"…"}]}` | echoes `GetParameter` |
| Sale | `{"operation":"Transaction","type":"SALE","requestedAmount":"500","printReceipt":"1"}` | echoes `Transaction` |
| Force sale | `{"operation":"Transaction","type":"FORCE_SALE","requestedAmount":"700","originalAuthCode":"…"}` | echoes `Transaction` |
| MOTO sale | `{"operation":"Transaction","type":"MOTO_SALE","requestedAmount":"200","order":"ABCD1234"}` | echoes `Transaction` |
| Refund | `{"operation":"Transaction","type":"REFUND","requestedAmount":"500"}` | echoes `Transaction` |
| Void | `{"operation":"Transaction","type":"VOID","originalAuthCode":"…"}` | echoes `Transaction` |
| Completion | `{"operation":"Transaction","type":"COMPLETION","requestedAmount":"600","originalAuthCode":"…"}` | echoes `Transaction` |
| Status check | `{"operation":"Transaction","type":"STATUS_CHECK"}` | echoes `Transaction` |
| Balance inquiry | `{"operation":"Transaction","type":"BALANCE_INQUIRY"}` | echoes `Transaction` |
| Last transaction | `{"operation":"LastTransaction"}` | echoes `LastTransaction` |
| Get transactions | `{"operation":"GetTransactions","type":"ALL_SALES"}` | echoes `GetTransactions` |
| SAF queue | `{"operation":"GetTransactions","type":"ALL_SAF"}` | echoes `GetTransactions` |
| Settlement | `{"operation":"Transaction","type":"SETTLEMENT"}` | echoes `Transaction` |
| Read card | `{"operation":"ReadCard","cardType":"1","timeout":"0"}` | echoes `ReadCard` |
| Restart | `{"operation":"Restart"}` | echoes `Restart`, then reconnect after reboot |
| Generate CSR | `{"operation":"GenerateCsr",...}` | echoes `GenerateCsr` |
| Import certificate | `{"operation":"ImportCertificate",...}` | echoes `ImportCertificate` |
| Install trust certificate | `{"operation":"InstallTrustCertificate",...}` | echoes `InstallTrustCertificate` |
| Progress (pushed) | — | `Status` (stream) |

> Field names mirror the public terminal contract: amounts as `requestedAmount` (cents), `printReceipt` `"0"`/`"1"`, optional `reference` (≤12), `tipAmount`, `invoice` (≤6); `originalAuthCode` links VOID/COMPLETION. Responses echo the request `operation`; a transaction's outcome is in `approval`; `result` is a numeric string. See the official protocol reference and the official transaction recipes for the full field and operation catalogue.
> For `ReadCard`, use `cardType:"1"` for banking-card buffering. `cardType:"0"` returns cleartext non-banking track data (gift/employee cards) and must not be generated for payment-card capture.
