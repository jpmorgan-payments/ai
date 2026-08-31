# Node / TypeScript reference

## Recommended libraries

Reuse what's already in `package.json`. If neither category is present, install:

- **JWT signing**: `jsonwebtoken` (matches the JPM Bruno sample and SDK). For ESM-first / no-deps preference, `jose` is a fine substitute.
- **HTTP**: native `fetch` (Node 18+). If the project already uses `axios`, `node-fetch`, `undici`, or `got`, use that instead.

## Reference module (TypeScript, Node 18+, ESM)

Replace `<DEFAULT_TTL_SEC>` with the chosen JWT TTL in seconds (e.g. `28800` for 8h, `15552000` for 6 months).

```typescript
// jpmAuth.ts
import { readFileSync } from 'node:fs';
import jwt from 'jsonwebtoken';

const TOKEN_URL = 'https://idag2.jpmorganchase.com/adfs/oauth2/token';
const REFRESH_BUFFER_SEC = 30;

interface TokenCache {
  accessToken: string;
  expiresAt: number; // epoch seconds
}

let cache: TokenCache | null = null;
let inFlight: Promise<string> | null = null;

function readConfig() {
  const {
    JPM_CLIENT_ID: clientId,
    JPM_PRIVATE_KEY_PATH: keyPath,
    JPM_CERT_THUMBPRINT: rawThumbprint,
    JPM_RESOURCE_ID: resourceId,
    JPM_JWT_TTL_SEC: ttlStr,
  } = process.env;

  if (!clientId || !keyPath || !rawThumbprint || !resourceId) {
    throw new Error(
      'Missing JPM_* env vars. Required: JPM_CLIENT_ID, JPM_PRIVATE_KEY_PATH, JPM_CERT_THUMBPRINT, JPM_RESOURCE_ID.',
    );
  }
  return {
    clientId,
    keyPath,
    thumbprint: rawThumbprint.replace(/:/g, '').toUpperCase(),
    resourceId,
    jwtTtlSec: ttlStr ? parseInt(ttlStr, 10) : <DEFAULT_TTL_SEC>,
  };
}

function buildJWT(c: ReturnType<typeof readConfig>): string {
  const now = Math.floor(Date.now() / 1000);
  const payload = {
    iss: c.clientId,
    sub: c.clientId,
    aud: TOKEN_URL,
    iat: now,
    exp: now + c.jwtTtlSec,
    jti: `${now}-${Math.random().toString(36).slice(2, 10)}`,
  };
  const privateKey = readFileSync(c.keyPath);
  return jwt.sign(payload, privateKey, {
    algorithm: 'RS256',
    header: { typ: 'JWT', alg: 'RS256', kid: c.thumbprint },
  });
}

async function exchange(jws: string, c: ReturnType<typeof readConfig>): Promise<TokenCache> {
  const body = new URLSearchParams({
    grant_type: 'client_credentials',
    client_id: c.clientId,
    resource: c.resourceId,
    client_assertion_type: 'urn:ietf:params:oauth:client-assertion-type:jwt-bearer',
    client_assertion: jws,
  });
  const res = await fetch(TOKEN_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`JPM token exchange failed (${res.status}): ${text}`);
  }
  const json = (await res.json()) as { access_token: string; expires_in: number };
  return {
    accessToken: json.access_token,
    expiresAt: Math.floor(Date.now() / 1000) + json.expires_in,
  };
}

export async function getAccessToken(): Promise<string> {
  const now = Math.floor(Date.now() / 1000);
  if (cache && cache.expiresAt - REFRESH_BUFFER_SEC > now) {
    return cache.accessToken;
  }
  if (inFlight) return inFlight;

  const c = readConfig();
  inFlight = (async () => {
    try {
      const jws = buildJWT(c);
      cache = await exchange(jws, c);
      return cache.accessToken;
    } finally {
      inFlight = null;
    }
  })();
  return inFlight;
}
```

## Usage

```typescript
import { getAccessToken } from './jpmAuth.js';

const token = await getAccessToken();
const res = await fetch('https://api-ms-test.payments.jpmorgan.com/api/v2/...', {
  headers: { Authorization: `Bearer ${token}` },
});
```

## Adapting

- **CommonJS**: `const jwt = require('jsonwebtoken');` and `module.exports = { getAccessToken };` (drop the `import`/`export` keywords).
- **axios**: replace the `fetch` block with `const { data } = await axios.post(TOKEN_URL, body, { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } });` and use `data.access_token` / `data.expires_in`.
- **`jose` instead of `jsonwebtoken`**: `await new SignJWT(payload).setProtectedHeader({ alg: 'RS256', typ: 'JWT', kid: c.thumbprint }).sign(await importPKCS8(privateKey.toString(), 'RS256'))`.

## Notes
- The `inFlight` mutex prevents thundering-herd token exchanges when many callers hit a cold cache simultaneously.
- The cache is per-process. In a Node cluster (forked workers) each worker has its own cache — that's fine; no cross-process sharing needed.
- If your private key is encrypted (passphrase-protected), pass `{ key: readFileSync(c.keyPath), passphrase: process.env.JPM_KEY_PASSPHRASE }` instead of `readFileSync(c.keyPath)` to `jwt.sign`.
