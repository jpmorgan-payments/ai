# Webhook Handler — Receiver Guardrails, Templates & Signature Verification

## Fit the merchant's codebase first (applies to all generated code)

Don't paste the skeletons verbatim. **First read and understand the merchant's existing codebase**,
then write code that fits it while keeping every guardrail below:

- Detect their language, framework, and app entry point; reuse their routing, middleware, dependency
  injection, config/secrets loading, logging, error handling, and their existing queue / DB / dedup store.
- Reuse the `getAccessToken()` auth module from `jpm-oauth` rather than adding new auth or HTTP clients.
- Match their conventions (naming, formatting, module layout, async style) so the code looks native to the project.
- Apply the guardrails and payload/handshake rules from this file on top of their patterns.

**Infrastructure & network — check and call out changes.** The callback URL must be publicly reachable
and **whitelisted**. Account for the merchant's firewall, security groups, corporate proxy, WAF, load
balancer, and API gateway, and explicitly flag any infrastructure or network change they must make
before it works — e.g. exposing/allowlisting the `/webhooks/jpmc` route, TLS certificate, DNS, and any
inbound IP allowlist for JPM's delivery. Never assume the endpoint is reachable.

> This "understand the codebase first + mind infra/network" principle applies to **every** piece of code
> this skill generates (webhook receiver, subscription client, signature verification) — not just this file.

## Required guardrails

> **All guardrails are mandatory — none may be skipped or stubbed out silently.**
> If implementing any guardrail is blocked (e.g. the queue technology is unclear, there is no
> existing dedup store, the signature-verification module path is unknown, the raw-body capture
> mechanism isn't obvious in the framework), **stop and ask the merchant** before proceeding.
> Do not substitute a placeholder, omit the guardrail, or make a silent assumption.

1. **Fast 200 (< 5s) + async.** Acknowledge with HTTP 200 within 5 seconds, then process in the
   background. Never do DB writes, external calls, or other heavy processing inside the HTTP handler.
   `POST /webhooks/jpmc → verify signature → enqueue → 200` (worker processes off the queue).
2. **Idempotency by `notificationId`.** At-least-once delivery means duplicates happen. Track
   `notificationId` in a dedup store and skip if seen — but still return **200** for duplicates.
   - Low volume: in-memory set (24h TTL). Medium: Redis `SET`+`EXPIRE` (48h). High: DB unique
     constraint on `notificationId` (7d).
3. **Signature verification.** Verify the `signature` header over the **raw** body before processing;
   reject invalid with 401. See §Signature Verification below.
4. **Retry + dead-letter (your worker).** Exponential backoff (1m → 5m → 30m → give up), then move to
   a dead-letter store and alert ops.
5. **Correct status codes:** **200 or 201** = received (incl. duplicates and the verification webhook);
   only 200/201 count as success. 401 signature invalid (not retried); 500/connection-refused/timeout → JPM retries.
6. **Structured logging.** Log `notificationId`, type, sub-type, `signatureValid`, `isDuplicate`,
   `processingStatus`, timestamp.

## Payload shape

> **LIVE-DOC required.** Refer to the
> [Retrieve notifications](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Foptimization-protection%2Fcapabilities%2Fnotifications%2Fhow-to%2Fretrieve-notifications.md)
> documentation for the payload contract and a worked sample. Do not assume the shape from this file.

The two structural facts your routing depends on: `notificationType` and `notificationSubType` are
**top-level**, and there is **no generic payload envelope** — the type-specific body is a top-level
key named after the notification type, camelCased. Route on `notificationType` and read the matching
key.

## Subscription verification handshake (must handle)

Right after you create a subscription, JPM sends a **verification webhook** to your `callbackURL`:
`notificationType: SubscriptionVerification`, `notificationSubType: WebhookVerification`. Your
endpoint must accept it and return **200/201**, or the subscription becomes `FAILED_VERIFICATION`
and never activates. Refer to the
[Webhook verification](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Foptimization-protection%2Fcapabilities%2Fnotifications%2Fwebhook-verification.md)
documentation for the verification payload sample and the failure conditions.

### Verification handshake pseudocode (language-agnostic)

Implement this logic in your language of choice:

```pseudocode
// Handler receives a webhook POST
function handleWebhook(request):
  raw = request.rawBody  // Capture raw bytes for signature verification
  signature = request.header("signature")
  keyId = request.header("key-id")
  algorithm = request.header("signingAlgorithm")   // "EC" or "RSA" - advisory only

  // Step 1: Verify signature
  if not verifyJpmSignature(raw, signature, keyId, algorithm):
    return Response(status=401, body="invalid signature")
  
  // Step 2: Parse body
  body = JSON.parse(raw)
  notificationId = body.notificationId
  notificationType = body.notificationType
  notificationSubType = body.notificationSubType

  // Step 3: Check for subscription verification handshake
  if notificationType == "SubscriptionVerification" AND notificationSubType == "WebhookVerification":
    // subscriptionId is top-level; requestId is nested under subscriptionVerification
    subscriptionId = body.subscriptionId
    requestId = body.subscriptionVerification.webhookVerification.requestId
    
    // Log for debugging
    logger.info("Received verification webhook", {
      notificationId: notificationId,
      subscriptionId: subscriptionId,
      requestId: requestId
    })
    
    // Return 200 immediately — no business processing
    return Response(status=200, body="verification received")
  
  // Step 4: Deduplicate (track notificationId)
  if isDuplicate(notificationId):
    return Response(status=200, body="duplicate")
  
  // Step 5: Enqueue for processing
  enqueue(body)
  return Response(status=200, body="queued")
```

### Key points

- **Detect by type/subtype:** Check `notificationType == "SubscriptionVerification"` and
  `notificationSubType == "WebhookVerification"`.
- **Short-circuit to 200:** Return 200 immediately without further processing.
- **Field locations:** `subscriptionId` is top-level; `requestId` is nested at
  `subscriptionVerification.webhookVerification.requestId`.

Translate the pseudocode to your language using its native HTTP framework and crypto libraries. Adapt idempotency store, queue, and worker to the merchant's infrastructure. Keep the HTTP handler
thin — verify, dedupe, enqueue, 200.

## Post-implementation guardrail summary (required after every code write or plan)

After writing all code (or after presenting the plan), produce a summary table covering every
guardrail. Be explicit about what was implemented and what was assumed. Then ask for feedback.

**Format:**

| Guardrail | How implemented | Assumptions made |
| --- | --- | --- |
| Fast 200 + async | e.g. "enqueued to SQS, handler returns 200 immediately" | e.g. "assumed SQS queue already exists; used existing `QueueClient` from codebase" |
| Idempotency | e.g. "Redis SET+EXPIRE with 48h TTL using existing RedisTemplate bean" | e.g. "assumed Redis is available; reused `redisTemplate` from Spring context" |
| Signature verification | e.g. "calls `JpmSignature.verify()` on raw bytes before parsing" | e.g. "assumed public-key fetch is handled by existing `KeyStore` service" |
| Retry + dead-letter | e.g. "worker uses exponential backoff; DLQ is SQS dead-letter queue" | e.g. "assumed DLQ is already configured on the SQS queue" |
| Status codes | e.g. "200 for success and duplicates, 401 for bad signature, no 5xx swallowed" | none |
| Structured logging | e.g. "logs via existing `Logger` bean with `notificationId`, type, `signatureValid`, `isDuplicate`" | e.g. "used SLF4J logger matching existing log format" |
| Verification handshake | e.g. "short-circuits to 200 on `SubscriptionVerification/WebhookVerification` type" | none |

After the table, ask in plain text:

> "Here's how I implemented each guardrail and what I assumed. Does anything look wrong, or would
> you like to change how any of these are handled?"

Wait for the merchant's reply. If they want changes, update the relevant files and re-present only
the affected rows. Do not regenerate the entire table unless asked.

## Build verification (required after all files are written)

After writing every file, run the project's build or compile command to verify the code compiles
and passes static checks. Detect the build tool from the project (e.g. `mvn compile`, `gradle build`,
`npm run build`, `tsc`, `go build`, `cargo build`, `python -m py_compile`, or equivalent). Ask the
merchant for the build command if it cannot be determined from the project files.

- If the build **passes**: report "Build passed — no compile errors." and proceed.
- If the build **fails**: show the exact error output, fix the errors in the affected files, and
  re-run the build. Repeat until the build is clean before handing off to the merchant.

---

## Signature Verification

Every JPM notification webhook is signed. Verify it over the **raw** request body before processing.
Refer to the [Public keys](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Foptimization-protection%2Fcapabilities%2Fnotifications%2Fpublic-keys.md) and
[Webhook verification](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Foptimization-protection%2Fcapabilities%2Fnotifications%2Fwebhook-verification.md) documentation.

## Headers on every webhook

| Header | Meaning |
| --- | --- |
| `signature` | Base64-encoded signature over the raw body bytes |
| `key-id` | Which signing key was used — look it up by `kid` |
| `signingAlgorithm` | `EC` (default) or `RSA` — the key type, **advisory only** |
| `correlation-id` | Delivery correlation id — log it alongside `notificationId` |

> **Match header names case-insensitively.** HTTP header names are case-insensitive and PDP's
> public-keys page spells these `Signature`, `Key-ID`, and `Signing algorithm`. Read whatever your
> framework gives you rather than matching an exact literal.
>
> **`signingAlgorithm` carries a key type, not a JCA algorithm name.** Its value is `EC` or `RSA`,
> chosen by the merchant in the subscription's `securityPreferences` and defaulting to `EC`. Because
> the merchant already knows which they chose, and because every header on an unauthenticated
> endpoint is attacker-controlled, never let this header select the verifier — derive the algorithm
> from the key you looked up, and reject the request if the header disagrees.

## Procedure

1. Read the **raw** body bytes (before any JSON parse/reformat — re-serialization breaks the signature).
2. Fetch signing keys from `GET /v1/public-keys` (returns a **JWKS**) using the `jpm-oauth` Bearer
  token; cache by `kid` and honour each key's `exp`.
3. Look up the key whose `kid` equals the `key-id` header. Treat a cached key past its `exp` as absent.
4. Derive the algorithm from that key's `kty` — `EC` → `SHA256withECDSA`, `RSA` → `SHA256withRSA` —
  and verify the base64 `signature` over the raw bytes.
5. Reject (HTTP 401) and do not process if verification fails.

Show the merchant key ids/algorithms/expiry — never dump full key material.

> **Don't refetch keys on every unknown `key-id`.** The header is attacker-controlled and is read
> before the signature is checked, so a plain "cache miss → refetch" rule lets anyone trigger a token
> call and a key fetch on every request. Debounce the refresh, and negative-cache key ids you have
> already looked up and not found.

## Implementation pseudocode (language-agnostic)

Implement this logic in your language of choice using that language's standard crypto + JWK libraries:

```pseudocode
// Module-level caches
keyCache        = Map<kid, { publicKey, kty, exp }>
unknownKidCache = TTLSet<kid>   // kids already proven absent
lastRefreshAt   = 0

REFRESH_MIN_INTERVAL = 5 minutes   // hard floor between key fetches
NEGATIVE_TTL         = 10 minutes  // how long an unknown kid stays rejected

// Debounced. Returns false when a refresh was suppressed so callers fail closed.
function maybeRefreshKeys() -> boolean:
  if now() - lastRefreshAt < REFRESH_MIN_INTERVAL:
    return false
  lastRefreshAt = now()

  token = getAccessToken()  // from jpm-oauth
  response = HTTP.GET(
    url: "${JPM_NOTIFICATIONS_API_URL}/v1/public-keys",
    headers: {
      "Authorization": "Bearer " + token,
      "request-id": UUID()
    }
  )
  jwks = JSON.parse(response.body)  // { "keys": [ { kid, kty, ..., exp }, ... ] }

  keyCache.clear()
  for each jwk in jwks.keys:
    if jwk.exp is present and jwk.exp <= now():
      continue  // never cache an already-expired key
    keyCache[jwk.kid] = {
      publicKey: buildPublicKeyFromJWK(jwk),
      kty:       jwk.kty,
      exp:       jwk.exp
    }
  unknownKidCache.clear()  // a fresh key set may contain a previously-unknown kid
  return true

// Main verification function
function verifyJpmSignature(
  rawBodyBytes: byte[],
  signatureBase64: string,
  keyId: string,          // from the "key-id" header
  headerAlgorithm: string // from the "signingAlgorithm" header - advisory only
) -> boolean:

  if unknownKidCache.contains(keyId):
    return false  // already proven absent; do not refetch

  entry = keyCache.get(keyId)
  if entry is null or (entry.exp is present and entry.exp <= now()):
    if not maybeRefreshKeys():
      return false  // refresh debounced -> fail closed
    entry = keyCache.get(keyId)

  if entry is null:
    unknownKidCache.add(keyId, ttl: NEGATIVE_TTL)
    return false

  // The verifier is chosen from the key, never from the request.
  algorithm = (entry.kty == "RSA") ? "SHA256withRSA" : "SHA256withECDSA"
  if headerAlgorithm is present and headerAlgorithm != entry.kty:
    return false  // header disagrees with the key -> reject

  signatureBytes = Base64.decode(signatureBase64)

  try:
    // Platform-specific: verify(publicKey, algorithm, rawBodyBytes, signatureBytes)
    // Most languages provide: publicKey.verify(signature, raw, algorithm)
    return entry.publicKey.verify(
      signature: signatureBytes,
      data:      rawBodyBytes,
      algorithm: algorithm
    )
  catch:
    return false
```

## Language-specific implementation notes

- **Build the public key from the JWK:** Use your language's JWK library to parse the JWKS response
  from `GET /v1/public-keys` and construct a public-key object. Many languages have a `JWK.parse()`
  or equivalent that builds the key directly.
- **Verify the signature:** Call your language's cryptographic verify function over the **raw** body
  bytes using the algorithm (SHA256withECDSA for EC keys, SHA256withRSA for RSA keys).
- **EC signature encoding:** JPM uses standard EC signatures. If your language's verify function
  expects IEEE-P1363 format (r||s concatenated) but JPM sends DER-encoded, you may need to
  convert the signature format.

## Library recommendations by language

Implement the pseudocode above using these libraries for your language. All follow the same pattern:
fetch the JWKS, cache keys by `kid`, and verify the base64 signature over the raw bytes.

| Language | JWK parsing | Crypto verification |
| --- | --- | --- |
| Node.js | `node:crypto` + `jwk` format option | `createVerify(...).verify(key, signature)` |
| Python | `PyJWT`, `python-jose`, or `cryptography` | `ECDsa.verify()` or `RSA.verify()` |
| Java | `nimbus-jose-jwt` or `json-smart` | `Signature.getInstance(...).verify()` |
| Go | `github.com/lestrrat-go/jwx/v2/jwk` | `crypto/ecdsa` or `crypto/rsa` + `crypto/sha256` |
| Ruby | `jwt` gem (`JWT::JWK`) | `OpenSSL::PKey::EC` or `RSA#verify` |
| PHP | `web-token/jwt-framework` or `firebase/php-jwt` | `openssl_verify()` |
| C# / .NET | `Microsoft.IdentityModel.Tokens.JsonWebKey` | `ECDsa.VerifyData()` or `RSA.VerifyData()` |
