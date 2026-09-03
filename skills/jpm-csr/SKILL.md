---
name: jpm-csr
description: Generate a Certificate Signing Request (CSR) and matching private key for JPM Payments API onboarding. Use this skill when a merchant needs to create a CSR to send to their JPM Relationship Manager (RM) for client ID provisioning via IDAHO/IDAnywhere, when generating a new key pair for JPM/Chase Orbital API authentication, or when preparing credentials before completing JPM onboarding. Supports CAT, PROD, or both environments at once and enforces the JPM rule that the CN must differ between CAT and PROD.
metadata:
  version: 1.0.0
---

# JPM CSR Generation

Generate one or two CSR + private-key pairs (CAT, PROD, or both) for JPM Payments API onboarding. Follow the steps in order. Use `AskUserQuestion` for every multiple-choice question.

## Step 1 — Pre-check

Run `openssl version` via Bash. If the command is not found, tell the user:

> openssl is not on PATH. Install it and re-run this skill:
> - Windows: use Git Bash (which bundles openssl) or install from https://slproweb.com/products/Win32OpenSSL.html
> - macOS: `brew install openssl`
> - Linux: `apt install openssl` (or your distro's equivalent)

Then exit.

## Step 2 — Which environment(s)?

Ask:
- Question: "Which environment(s) do you need a CSR for?"
- Header: "Environment"
- Options:
  - "CAT (test) only"
  - "PROD only"
  - "Both — CAT and PROD"

JPM requires a **separate CSR per environment** with a **different CN**. If the user picks "Both", you'll run the generation twice with different CNs but otherwise identical subject fields.

## Step 3 — Collect subject fields

For the first (or only) environment, prompt the user (free text), one at a time, for the six standard X.509 subject fields:

1. **C** — Country code (exactly 2 letters, ISO 3166, e.g. `US`)
2. **ST** — State/Province (e.g. `New York`)
3. **L** — Locality/City (e.g. `New York`)
4. **O** — Organization (e.g. `Acme Corp`)
5. **OU** — Organizational Unit (e.g. `Payments`)
6. **CN** — Common Name (must be unique per environment, e.g. `acme-corp-cat`)

Validate before generating:
- `C` must match `^[A-Za-z]{2}$`. If not, re-prompt. Uppercase it before use.
- All six fields must be non-empty.
- Reject any field containing a newline or a `"` character.

If the user chose "Both": after generating CAT, re-prompt for PROD using CAT's `C`/`ST`/`L`/`O`/`OU` as suggested defaults (the user can accept or change them) and require a **new** `CN` that differs from CAT's. If the user enters the same CN, re-prompt with a reminder that JPM requires distinct CNs.

## Step 4 — Output directory

Ask for an output directory (free text). Suggest defaults:
- Single env: `./jpm-csr/<env>/` (e.g. `./jpm-csr/cat/`)
- Both: `./jpm-csr/cat/` and `./jpm-csr/prod/`

**Validate the directory before using it — it is interpolated into shell commands in Step 5.**
Apply the same rules as the subject fields in Step 3, plus path-specific ones:

- Reject any value containing `"`, `'`, `` ` ``, `$`, `;`, `&`, `|`, `<`, `>`, `\`, a newline, or a
  tab. These break out of the quoting in Step 5 and execute arbitrary commands.
- Reject a value starting with `-` (it would be parsed as an openssl/mkdir flag).
- Reject an empty value.
- On rejection, re-prompt with the reason. Do not sanitize silently and do not proceed with a
  value that failed — an unvalidated path here is a command-injection sink, not a cosmetic issue.

The directory is created in Step 5 if it doesn't exist.

## Step 5 — Generate

Run these commands via Bash, once per environment. Substitute the collected values; uppercase `C` first.

**5a. Create the output directory and an OpenSSL config file.** Use a config file rather than `-subj` so values containing `/`, `,` or other special characters are handled safely.

```bash
mkdir -p "<out-dir>"

cat > "<out-dir>/csr.cnf" <<'EOF'
[req]
distinguished_name = dn
prompt = no

[dn]
C = <C>
ST = <ST>
L = <L>
O = <O>
OU = <OU>
CN = <CN>
EOF
```

Note: the `<<'EOF'` quoting prevents shell expansion inside the subject values. Write the literal values into the file — do not use shell variables.

**5b. Generate the key and CSR.**

```bash
openssl req -new \
  -newkey rsa:2048 \
  -nodes \
  -keyout "<out-dir>/privateKey.key" \
  -out "<out-dir>/certificateRequest.pem" \
  -config "<out-dir>/csr.cnf"
```

**5c. Lock down the key and remove the config file.**

```bash
chmod 600 "<out-dir>/privateKey.key" 2>/dev/null || true
rm -f "<out-dir>/csr.cnf"
```

**5d. Verify the subject is what the user asked for.**

```bash
openssl req -in "<out-dir>/certificateRequest.pem" -noout -subject
```

Show that subject line to the user. If it doesn't match the collected fields, delete both output files and report the mismatch.

If any command fails, delete `privateKey.key` and `certificateRequest.pem` if they were created, show the OpenSSL error to the user, and exit. Do not retry automatically.

## Step 6 — Protect the private key

After successful generation:

1. Read `.gitignore` in the project root. If a line equal to `**/privateKey.key` is not present, append it (with a leading comment line `# JPM private keys`). If `.gitignore` doesn't exist, create one with those two lines.
2. Show the user a summary per environment:
   - CSR (send to RM): `<csr path>`
   - Private key (keep secret, never commit, never email): `<key path>`
   - Subject: `C=<C>, ST=<ST>, L=<L>, O=<O>, OU=<OU>, CN=<CN>`

## Step 7 — Next steps

Tell the user:

> Send the **`certificateRequest.pem`** file to your Relationship Manager. They will use it to create your Client ID and return a `.pem` certificate plus your `clientId`. Onboarding typically takes 24–48 hours.
>
> Keep **`privateKey.key`** safe. You'll reference it later in your OAuth config along with the `.pem` your Relationship Manager sends back. Once you have all three (clientId, .pem, privateKey.key), run the `jpm-integrations-get-started` skill to validate them.

If the user generated for both environments, remind them the two CSRs go in **separate** IDAHO requests (CAT and PROD).

## Rules

- Never echo the contents of the generated private key — only its path.
- Never write subject fields, paths, or generated keys to a memory file.
- If openssl fails or validation rejects the inputs, exit cleanly — do not loop or auto-retry.
- The only files this skill creates are the CSR + key in the user's chosen output dir, and (if needed) a `.gitignore` line for `**/privateKey.key`. The temporary `csr.cnf` must be deleted in Step 5c.
- Never pass user-supplied values through unquoted shell expansion; write them literally into the quoted here-doc.
- Validate the output directory (Step 4) with the same rigor as the subject fields before it reaches any Bash command. It is interpolated into `mkdir`, the here-doc path, three `openssl` flags, and `rm -f`.
