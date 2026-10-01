# JPM IDAnywhere OAuth — language-agnostic spec

The auth flow is OAuth 2.0 client credentials with a signed JWT as the client assertion (RFC 7523).

## Token endpoint

Same URL for CAT and PROD:

```
POST https://idag2.jpmorganchase.com/adfs/oauth2/token
Content-Type: application/x-www-form-urlencoded
```

The CAT vs PROD distinction is encoded in the `resource` field and the credentials, not the URL.

## Request body (form-urlencoded)

| Field | Value |
|---|---|
| `grant_type` | `client_credentials` |
| `client_id` | the merchant's clientId, e.g. `CC-000000-A000000-000000-PROD` |
| `resource` | the resource_id from the JPM onboarding email, e.g. `JPMC:URI:RS-000000-00000-HelixAPIEntitlementsCAT-PROD` |
| `client_assertion_type` | `urn:ietf:params:oauth:client-assertion-type:jwt-bearer` (literal) |
| `client_assertion` | the signed JWT, see below |

## JWT (the `client_assertion`)

**Header:**
```json
{
  "typ": "JWT",
  "alg": "RS256",
  "kid": "<SHA-1 thumbprint of the cert, uppercase hex, NO colons>"
}
```

The `kid` is the cert's SHA-1 fingerprint as a 40-character uppercase hex string. If your tooling produced colon-separated output (e.g. `E6:B8:4D:...`), strip the colons before signing.

**Payload:**
```json
{
  "iss": "<clientId>",
  "sub": "<clientId>",
  "aud": "https://idag2.jpmorganchase.com/adfs/oauth2/token",
  "iat": <epoch seconds, now>,
  "exp": <epoch seconds, now + JWT TTL>,
  "jti": "<unique per JWT — timestamp + random suffix is fine>"
}
```

`iss` and `sub` are both the clientId. `aud` is the token endpoint URL exactly as shown. `jti` must be unique per JWT — a timestamp plus a few random characters works.

**Signature:** RS256, using the merchant's PEM-encoded RSA private key. The cert and key were issued together during onboarding; the public key in the cert verifies the JWT signature on JPM's side, which is why the `kid` thumbprint is the lookup key.

## Response

Success (HTTP 200) returns JSON:

```json
{
  "access_token": "<token string>",
  "expires_in": 3600,
  "token_type": "bearer"
}
```

`expires_in` is seconds. **Treat it as authoritative** — it's set by JPM and may change. Do not hardcode an access-token TTL.

Failure modes worth catching:
- HTTP 400 with `error: "invalid_grant"` (or ADFS code `MSIS9622`) → JWT is malformed or signed wrong. Most common cause: wrong `kid` (still has colons, lowercase, or refers to the wrong cert). Second most common: wrong `aud` value, or the wrong private key for the cert in question.
- HTTP 401 / 403 → entitlements not granted on the IDAHO/SNOW side. Have the merchant check with their RM that the entitlement ticket completed (see the "Add Entitlements via SERVICE NOW" section of the JPM onboarding doc).

## Caching pattern (required)

The merchant's app should:

1. On first call, generate a JWT, exchange it for an access token, store the access token plus an absolute expiry time (`now + expires_in`).
2. On every subsequent call to `getAccessToken()`:
   - If the cached token is still valid (i.e. `now + buffer < expiresAt`, with `buffer ≈ 30s` for clock skew), return it.
   - Otherwise generate a fresh JWT, exchange, update the cache, return.
3. Guard against the thundering-herd case: if many callers hit a cold cache simultaneously, only one should perform the exchange. Use a mutex / in-flight promise / lock.

The JWT itself can be reused across multiple token exchanges as long as it's still valid (within its `exp`). For simplicity, most implementations regenerate it on each exchange — that's fine because exchanges are rare (once per `expires_in`, typically once per hour).

## Resource IDs by environment

The resource_id encodes both the API surface and the environment. Examples (the merchant's RM provides the exact string in the onboarding email):

- CAT entitlements:  `JPMC:URI:RS-000000-<FID>-HelixAPIEntitlementsCAT-PROD`
- PROD entitlements: `JPMC:URI:RS-000000-<FID>-HelixAPIEntitlements-PROD`

Note that some merchants get distinct resource IDs per API (Checkout, Reporting, Tokenization, etc.). Treat the resource_id as a string the merchant configures via env var — never hardcode in source.
