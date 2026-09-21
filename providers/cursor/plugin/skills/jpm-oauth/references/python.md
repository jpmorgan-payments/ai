# Python reference

## Recommended libraries

- **JWT signing**: `pyjwt[crypto]` (`pip install 'pyjwt[crypto]'`). Alternative: `python-jose[cryptography]`.
- **HTTP**: `httpx` (sync or async, modern). Alternative: `requests` (sync only, ubiquitous).

## Reference module

Replace `<DEFAULT_TTL_SEC>` with the chosen JWT TTL in seconds (e.g. `28800` for 8h, `15552000` for 6 months).

```python
# jpm_auth.py
import os
import time
import threading
from pathlib import Path
from secrets import token_hex

import jwt as pyjwt
import httpx

TOKEN_URL = "https://idag2.jpmorganchase.com/adfs/oauth2/token"
REFRESH_BUFFER_SEC = 30


class _Cache:
    access_token: str | None = None
    expires_at: int = 0


_cache = _Cache()
_lock = threading.Lock()


def _read_config():
    client_id = os.environ.get("JPM_CLIENT_ID")
    key_path = os.environ.get("JPM_PRIVATE_KEY_PATH")
    raw_thumbprint = os.environ.get("JPM_CERT_THUMBPRINT")
    resource_id = os.environ.get("JPM_RESOURCE_ID")
    ttl = int(os.environ.get("JPM_JWT_TTL_SEC", <DEFAULT_TTL_SEC>))

    if not all([client_id, key_path, raw_thumbprint, resource_id]):
        raise RuntimeError(
            "Missing JPM_* env vars. Required: JPM_CLIENT_ID, "
            "JPM_PRIVATE_KEY_PATH, JPM_CERT_THUMBPRINT, JPM_RESOURCE_ID."
        )

    return {
        "client_id": client_id,
        "key_path": key_path,
        "thumbprint": raw_thumbprint.replace(":", "").upper(),
        "resource_id": resource_id,
        "jwt_ttl_sec": ttl,
    }


def _build_jwt(cfg) -> str:
    now = int(time.time())
    payload = {
        "iss": cfg["client_id"],
        "sub": cfg["client_id"],
        "aud": TOKEN_URL,
        "iat": now,
        "exp": now + cfg["jwt_ttl_sec"],
        "jti": f"{now}-{token_hex(4)}",
    }
    private_key = Path(cfg["key_path"]).read_bytes()
    return pyjwt.encode(
        payload,
        private_key,
        algorithm="RS256",
        headers={"typ": "JWT", "alg": "RS256", "kid": cfg["thumbprint"]},
    )


def _exchange(jws: str, cfg) -> tuple[str, int]:
    resp = httpx.post(
        TOKEN_URL,
        data={
            "grant_type": "client_credentials",
            "client_id": cfg["client_id"],
            "resource": cfg["resource_id"],
            "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            "client_assertion": jws,
        },
        timeout=30.0,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"JPM token exchange failed ({resp.status_code}): {resp.text}")
    body = resp.json()
    return body["access_token"], int(body["expires_in"])


def get_access_token() -> str:
    now = int(time.time())
    if _cache.access_token and _cache.expires_at - REFRESH_BUFFER_SEC > now:
        return _cache.access_token

    with _lock:
        # Re-check under the lock — another thread may have refreshed.
        now = int(time.time())
        if _cache.access_token and _cache.expires_at - REFRESH_BUFFER_SEC > now:
            return _cache.access_token

        cfg = _read_config()
        jws = _build_jwt(cfg)
        token, expires_in = _exchange(jws, cfg)
        _cache.access_token = token
        _cache.expires_at = int(time.time()) + expires_in
        return token
```

## Usage

```python
from jpm_auth import get_access_token
import httpx

token = get_access_token()
resp = httpx.get(
    "https://api-ms-test.payments.jpmorgan.com/api/v2/...",
    headers={"Authorization": f"Bearer {token}"},
)
```

## Adapting

- **`requests` instead of `httpx`**: replace `httpx.post(...)` with `requests.post(TOKEN_URL, data=..., timeout=30)` — same kwargs apart from `timeout`.
- **asyncio**: swap `threading.Lock` for `asyncio.Lock`, `httpx.post` for `await httpx.AsyncClient().post`, and make `get_access_token` async.
- **`python-jose` instead of `pyjwt`**: `from jose import jwt as jose_jwt; jose_jwt.encode(payload, key_pem, algorithm="RS256", headers={...})`.

## Notes
- The lock makes `get_access_token` thread-safe under WSGI workers (gunicorn `--threads`, uWSGI, etc.).
- For multi-process workers (`gunicorn -w N`) each process has its own cache. That's normal — no cross-process sharing needed.
- If your private key is encrypted (passphrase-protected), pass it through `cryptography.hazmat.primitives.serialization.load_pem_private_key(pem, password=...)` and feed the resulting key object to `pyjwt.encode`.
