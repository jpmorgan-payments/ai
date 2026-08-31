---
name: jpm-oauth
description: Implement J.P. Morgan Payments OAuth authentication (JWT signing + IDAnywhere token exchange) in a merchant project. Use this skill when a merchant has their clientId, certificate, private key, and SHA-1 thumbprint and wants to generate the auth code in their codebase — typically right after running jpm-integrations-get-started. Produces a language-specific auth module with built-in token caching that follows JPM guidance against regenerating tokens per request. Supports Node/TypeScript, Python, and Java idiomatically; for other languages, translates from the canonical algorithm. Asks for target environment (CAT or PROD) and JWT TTL (default 6 months for CAT, 8h for PROD per JPM guidance); the resource_id is read from the merchant's `.env` at runtime rather than collected interactively.
---

# JPM OAuth implementation

Generate JWT-signing + access-token-exchange code that follows JPM's IDAnywhere OAuth contract. The generated module caches the access token until just before its server-set expiry, so the merchant's app reuses one token across many API calls instead of regenerating per request.

This skill is typically invoked from the end of `jpm-integrations-get-started` (its Step 4). When run standalone, it gathers the same inputs interactively.

## Step 1 — Verify prerequisites

The merchant must have all four of:
- **clientId** (e.g. `CC-123456-D12992-232222-TEST`)
- **certificate path** (PEM `.cer` from JPM)
- **private key path** (PEM key paired with the certificate)
- **SHA-1 thumbprint** of the cert (40 hex chars; colons optional — code will normalize)

If you arrived from `jpm-integrations-get-started`, these are already in conversation context — use them.

If invoked standalone:
1. Ask the user where the credentials live: file paths, an `.env`, or in conversation.
2. If anything is missing, tell the user to run `jpm-integrations-get-started` first and exit. Do **not** invent placeholder values.

## Step 2 — Environment

Ask:
- Question: "Which JPM environment are you targeting?"
- Header: "Environment"
- Options:
  - "CAT (test)"
  - "PROD"
  - "Both — generate code that switches via env var"

Do **not** prompt the user for the `resource_id`. The generated module reads it from the `JPM_RESOURCE_ID` environment variable at runtime, and the intake skill's `.env.example` already includes that key with a comment pointing the user at the JPM onboarding email (where the value lives). Just remind the user in your wrap-up to fill `JPM_RESOURCE_ID` in their `.env` before running the auth module — and that CAT and PROD have different `resource_id` values, so the right one must be in the `.env` for the environment they're targeting.

## Step 3 — Education and JWT TTL

Show the user this guidance verbatim before asking the TTL question:

> **Two TTLs to know about:**
>
> - **Access token TTL** — set by JPM's IDAnywhere server, returned as `expires_in` (seconds) in every token response. The generated module reads this value and reuses the access token across requests until shortly before it expires. Don't treat it as fixed — server-side defaults can change.
>
> - **JWT TTL** — client-controlled (you pick). The JWT is the credential you hand to IDAnywhere to *get* an access token. JPM's guidance: **8 hours for PROD**; longer is fine for **CAT** (the JPM Bruno sample uses 6 months).
>
> **Anti-pattern to avoid**: generating a fresh JWT *and* a fresh access token on every API call (think of it like running a card auth on a brand-new payment instrument every transaction — wasteful and slow). The access token is reusable until expiry. The generated module caches it in memory and only refreshes it when within ~30s of expiry. Call `getAccessToken()` once per outbound request and let the cache do its job.

Then ask, with default options that depend on the environment chosen in Step 2:

- Question: "How long should JWTs be valid?"
- Header: "JWT TTL"
- Options for **PROD** or **Both**:
  - "8 hours (JPM recommended for PROD)"
  - "1 hour"
  - "Custom"
- Options for **CAT** only:
  - "6 months (matches JPM sample)"
  - "8 hours"
  - "Custom"

If "Custom", prompt free text. Accept forms like `8h`, `30d`, `6mo`, `3600s`. Convert to seconds before generating code.

## Step 4 — Language and libraries

If you arrived from `jpm-integrations-get-started` Step 4, the language and HTTP / JWT libraries the merchant chose are in conversation context. Confirm in one sentence ("Generating Python with `httpx` and `pyjwt` — sound right?") and proceed. If they say no, re-ask.

If invoked standalone, run the same detection logic the intake skill uses: look in the user's CWD for `package.json`, `pyproject.toml`/`requirements.txt`, `pom.xml`, `build.gradle*`, `go.mod`, `Cargo.toml`, `Gemfile`, `composer.json`, `*.csproj`. If a manifest is found and contains an HTTP client and a JWT library, just announce. Otherwise prompt for the gaps only.

## Step 5 — Output location

Ask the user where the auth module should live:

- Question: "Where should I put the auth module?"
- Header: "Output path"
- Options:
  - "Inside the project source tree" — pick a default by language (e.g. `src/auth/jpmAuth.ts` for Node/TS, `<project_pkg>/auth/jpm.py` for Python, `src/main/java/<pkg>/auth/JpmAuth.java` for Java). Confirm the exact path with the user before writing.
  - "A new top-level folder" — e.g. `./jpm-auth/`. Useful for keeping the integration cleanly separated from the rest of the codebase.
  - "Custom path" — prompt free text.

Always echo the final path back to the user and wait for confirmation before any `Write` call.

## Step 6 — Generate the code

1. Read `references/algorithm.md` (always — it's the canonical spec).
2. Read `references/<language>.md` if one exists for the target language. Bundled: `node.md`, `python.md`, `java.md`. For other languages, translate the algorithm idiomatically using the user's chosen libs.
3. Generate two artifacts:
   - **Auth module** — exports a `getAccessToken()` function (or language-equivalent name) with built-in caching and an in-flight mutex.
   - **Usage example** — a short snippet showing the module wired into one outbound API call (e.g. a Bearer header on a Checkout API request). Place it as a comment block at the bottom of the auth module, or as a sibling `example.<ext>` file if the user prefers that layout.
4. Replace any `<DEFAULT_TTL_SEC>` placeholders in the reference code with the actual TTL chosen in Step 3, expressed in seconds (e.g. `28800` for 8h, `15552000` for 6 months).
5. Write the file(s) to the path confirmed in Step 5.

If "Both" was chosen in Step 2, the generated code reads `JPM_RESOURCE_ID` from the environment so the same binary works in CAT or PROD by swapping the `.env`. There's no per-environment branching in the source.

## Step 7 — Update env files and wrap up

The generated module reads these env vars at runtime:

- `JPM_CLIENT_ID`
- `JPM_PRIVATE_KEY_PATH`
- `JPM_CERT_THUMBPRINT` *(SHA-1 hex; colons OK — code strips them)*
- `JPM_RESOURCE_ID`
- `JPM_JWT_TTL_SEC` *(optional — defaults to the value baked into the generated code)*

Plus optionally `JPM_CERT_PATH` if anything else in the project also reads the cert directly.

### Extend the merchant's env files

Look in the user's CWD for `.env.example` and `.env`. The intake skill's 3b branch typically created `.env.example` with only the first three credential vars; this step fills in the rest.

- **`.env.example` exists**: for each of `JPM_CERT_THUMBPRINT`, `JPM_RESOURCE_ID`, `JPM_JWT_TTL_SEC` whose key is **not already present**, append a placeholder line (`<KEY>=`). Don't write real values into `.env.example` — keep it a template. Tell the user which keys were added.

- **`.env` exists** (and `.env.example` does not, or the user wants both updated): ask `AskUserQuestion` ("Append missing keys to `.env`?" / "Yes, append placeholders" / "No, I'll handle it"). If yes, append only keys that are missing — never overwrite existing values.

- **Neither file exists**: skip the file edit and just list the variable names in the wrap-up message so the user can wire them into whatever config mechanism they use.

Whenever you mention these vars to the user, surface the actual values you have from this conversation — the SHA-1 thumbprint computed by the intake skill and the JWT TTL chosen in Step 3 — so they can copy-paste rather than re-derive. Show the thumbprint in the no-colons uppercase form the JWT header expects. For `JPM_RESOURCE_ID`, point the user at the comment already in `.env.example` (it explains that the value comes from the JPM onboarding email and that CAT and PROD differ) — don't ask them for it.

### Wrap up

Show the user:
- The path(s) of the auth module file(s) written.
- A summary of which env files were updated and which keys still need values.
- A one-line usage example in their language (e.g. `const token = await getAccessToken();`).
- A reminder: the cache is in-memory and per-process. In a multi-process deployment (forked Node cluster, gunicorn workers, multiple JVMs) each process gets its own cache — that's normal and fine; no cross-process sharing needed.

Then proceed to Step 8.

## Step 8 — Offer to start integrating an API

Auth is now wired up. Ask whether the user wants to keep going into API integration in this same session:

- Question: "Auth is in place. Want to integrate a J.P. Morgan Payments API now?"
- Header: "Integrate API?"
- Options:
  - "Yes — pick an API to integrate (Checkout or Online Payments)"
  - "No — I'll come back later"

If **Yes**, invoke the `jpm-merchant-integrations` skill via the Skill tool. It picks up from here using the auth module path and credentials context already in conversation, so the user won't be re-asked anything they've already answered.

If **No**, exit cleanly. The user can run `jpm-merchant-integrations` later when they're ready.

## Rules

- Never inline real credentials (clientId, key contents, thumbprint, resource_id) into the generated code. The module reads everything from environment variables at runtime.
- The generated module **must** cache the access token. Do not generate code that signs a fresh JWT and exchanges a token on every call.
- Strip colons from the thumbprint when constructing the JWT `kid` header — JPM's IDAnywhere expects uppercase hex with no separators.
- Use RS256 only. Do not offer alternatives.
- Confirm the output path with the user before writing. Don't drop unsolicited files into their source tree.
