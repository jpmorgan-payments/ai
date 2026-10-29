# Java reference

## Recommended libraries

- **JWT signing**: `io.jsonwebtoken:jjwt-api` + `jjwt-impl` + `jjwt-jackson` (most common in JVM merchant codebases). Alternative: `com.nimbusds:nimbus-jose-jwt`.
- **HTTP**: Java 11+ `java.net.http.HttpClient` (no extra dependency). Alternatives: OkHttp, Apache HttpClient — use whichever the project already has.

## Reference module

Replace `<DEFAULT_TTL_SEC>` with the chosen JWT TTL in seconds (e.g. `28800` for 8h, `15552000` for 6 months). Adjust the `package` declaration to match your project layout.

```java
// JpmAuth.java
package com.example.auth;

import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;

import java.net.URI;
import java.net.URLEncoder;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.KeyFactory;
import java.security.PrivateKey;
import java.security.spec.PKCS8EncodedKeySpec;
import java.time.Instant;
import java.util.Base64;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.atomic.AtomicReference;
import java.util.concurrent.locks.ReentrantLock;

public final class JpmAuth {
  private static final String TOKEN_URL = "https://idag2.jpmorganchase.com/adfs/oauth2/token";
  private static final long REFRESH_BUFFER_SEC = 30;

  private record Cached(String token, long expiresAtEpochSec) {}

  private static final AtomicReference<Cached> CACHE = new AtomicReference<>(null);
  private static final ReentrantLock LOCK = new ReentrantLock();
  private static final HttpClient CLIENT = HttpClient.newHttpClient();

  public static String getAccessToken() throws Exception {
    long now = Instant.now().getEpochSecond();
    Cached c = CACHE.get();
    if (c != null && c.expiresAtEpochSec - REFRESH_BUFFER_SEC > now) {
      return c.token;
    }
    LOCK.lock();
    try {
      // Re-check under the lock — another thread may have refreshed.
      now = Instant.now().getEpochSecond();
      c = CACHE.get();
      if (c != null && c.expiresAtEpochSec - REFRESH_BUFFER_SEC > now) {
        return c.token;
      }
      Cached fresh = refresh();
      CACHE.set(fresh);
      return fresh.token;
    } finally {
      LOCK.unlock();
    }
  }

  private static Cached refresh() throws Exception {
    String clientId = required("JPM_CLIENT_ID");
    String keyPath  = required("JPM_PRIVATE_KEY_PATH");
    String thumb    = required("JPM_CERT_THUMBPRINT").replace(":", "").toUpperCase();
    String resource = required("JPM_RESOURCE_ID");
    long jwtTtlSec  = Long.parseLong(System.getenv().getOrDefault("JPM_JWT_TTL_SEC", "<DEFAULT_TTL_SEC>"));

    String jws = buildJwt(clientId, keyPath, thumb, jwtTtlSec);

    String body =
        "grant_type=client_credentials"
        + "&client_id=" + URLEncoder.encode(clientId, StandardCharsets.UTF_8)
        + "&resource=" + URLEncoder.encode(resource, StandardCharsets.UTF_8)
        + "&client_assertion_type=urn%3Aietf%3Aparams%3Aoauth%3Aclient-assertion-type%3Ajwt-bearer"
        + "&client_assertion=" + URLEncoder.encode(jws, StandardCharsets.UTF_8);

    HttpResponse<String> resp = CLIENT.send(
        HttpRequest.newBuilder(URI.create(TOKEN_URL))
            .header("Content-Type", "application/x-www-form-urlencoded")
            .POST(HttpRequest.BodyPublishers.ofString(body))
            .build(),
        HttpResponse.BodyHandlers.ofString());

    if (resp.statusCode() != 200) {
      throw new RuntimeException(
          "JPM token exchange failed (" + resp.statusCode() + "): " + resp.body());
    }

    String json = resp.body();
    String accessToken = extractString(json, "access_token");
    long expiresIn = Long.parseLong(extractNumber(json, "expires_in"));
    return new Cached(accessToken, Instant.now().getEpochSecond() + expiresIn);
  }

  private static String buildJwt(String clientId, String keyPath, String thumbprint, long ttlSec)
      throws Exception {
    PrivateKey key = loadPrivateKey(keyPath);
    Instant now = Instant.now();
    Map<String, Object> headers = new HashMap<>();
    headers.put("typ", "JWT");
    headers.put("kid", thumbprint);
    return Jwts.builder()
        .setHeaderParams(headers)
        .setIssuer(clientId)
        .setSubject(clientId)
        .setAudience(TOKEN_URL)
        .setIssuedAt(Date.from(now))
        .setExpiration(Date.from(now.plusSeconds(ttlSec)))
        .setId(now.toEpochMilli() + "-" + Long.toHexString((long) (Math.random() * 1e12)))
        .signWith(key, SignatureAlgorithm.RS256)
        .compact();
  }

  // Assumes a PKCS#8 PEM. If the key starts with "-----BEGIN RSA PRIVATE KEY-----" (PKCS#1),
  // convert with: openssl pkcs8 -topk8 -in key.pem -out key-pkcs8.pem -nocrypt
  private static PrivateKey loadPrivateKey(String path) throws Exception {
    String pem = Files.readString(Path.of(path))
        .replaceAll("-----BEGIN [A-Z ]+-----", "")
        .replaceAll("-----END [A-Z ]+-----", "")
        .replaceAll("\\s+", "");
    byte[] der = Base64.getDecoder().decode(pem);
    return KeyFactory.getInstance("RSA").generatePrivate(new PKCS8EncodedKeySpec(der));
  }

  private static String required(String name) {
    String v = System.getenv(name);
    if (v == null || v.isEmpty()) throw new RuntimeException("Missing env var: " + name);
    return v;
  }

  // Tiny ad-hoc JSON helpers — replace with Jackson/Gson if either is on the classpath.
  private static String extractString(String json, String key) {
    int i = json.indexOf("\"" + key + "\"");
    if (i < 0) throw new RuntimeException("Missing field in token response: " + key);
    int colon = json.indexOf(':', i);
    int start = colon + 1;
    while (start < json.length() && Character.isWhitespace(json.charAt(start))) start++;
    if (json.charAt(start) != '"') throw new RuntimeException("Expected string for " + key);
    int end = json.indexOf('"', start + 1);
    return json.substring(start + 1, end);
  }

  private static String extractNumber(String json, String key) {
    int i = json.indexOf("\"" + key + "\"");
    if (i < 0) throw new RuntimeException("Missing field in token response: " + key);
    int colon = json.indexOf(':', i);
    int start = colon + 1;
    while (start < json.length() && Character.isWhitespace(json.charAt(start))) start++;
    int end = start;
    while (end < json.length() && "0123456789".indexOf(json.charAt(end)) >= 0) end++;
    return json.substring(start, end);
  }
}
```

## Usage

```java
String token = JpmAuth.getAccessToken();
HttpRequest req = HttpRequest.newBuilder(URI.create("https://api-ms-test.payments.jpmorgan.com/api/v2/..."))
    .header("Authorization", "Bearer " + token)
    .GET().build();
```

## Adapting

- **Spring**: wrap `JpmAuth` as a `@Component` (keep cache `static` or scope to the singleton bean). Inject env via `@Value("${JPM_CLIENT_ID}")` etc. instead of `System.getenv`.
- **Jackson on the classpath**: replace `extractString` / `extractNumber` with `objectMapper.readTree(json).get("access_token").asText()` — drops the ad-hoc parser entirely.
- **Nimbus JOSE+JWT instead of jjwt**: `JWSObject jws = new JWSObject(new JWSHeader.Builder(JWSAlgorithm.RS256).type(JOSEObjectType.JWT).keyID(thumbprint).build(), new Payload(claims.toString())); jws.sign(new RSASSASigner(key));`
- **OkHttp instead of `HttpClient`**: use `RequestBody.create(body, MediaType.get("application/x-www-form-urlencoded"))` and `client.newCall(req).execute()`.

## Notes
- The double-check pattern under `LOCK` is what makes the cache thread-safe — needed because servlet containers and reactive frameworks both run many threads against the same singleton.
- `AtomicReference` reads outside the lock are safe for the fast path (token is still valid). Writes always happen under the lock.
- The PKCS#8 loader is the common case for PEM keys generated by modern openssl. For older PKCS#1 keys (`-----BEGIN RSA PRIVATE KEY-----`), either convert once with the openssl command in the comment, or use BouncyCastle's `PEMParser` to handle both.
- If your private key is encrypted, replace the loader with `EncryptedPrivateKeyInfo` + a passphrase from `JPM_KEY_PASSPHRASE`.
