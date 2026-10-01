---
name: jpm-instore-get-started
description: Conversational intake for merchants building or migrating an in-store (card-present) POS integration to J.P. Morgan payment terminals (Ingenico AXIUM) over the semi-integrated WebSocket model. Triages onboarding status, network readiness, terminal models, and project config, then hands off to jpm-instore-payments.
---

# JPM In-Store — Get Started

Run a conversational intake for merchants getting started with an **in-store (card-present)** integration against the J.P. Morgan Payments Terminal Application. The primary v1 model is **semi-integrated**: the POS and the terminal are separate, and the POS sends payment requests to the terminal over a local **TLS WebSocket** (`wss://`) while all card interaction stays on the pre-certified terminal.

For the official product guide, use the LLM-friendly [In-Store Payments overview](https://developer.payments.jpmorgan.com/api/llm-content?path=en%2Fdocs%2Fcommerce%2Fin-store-payments%2F1overview-instorepay.md).

Follow the steps in order. Use `AskUserQuestion` for every multiple-choice question.

## Disclaimer (show before Step 1)

Before running the intake, show the user this disclaimer verbatim and wait for them to acknowledge before proceeding:

> **Disclaimer:** We do not assume any responsibility for any issues, damages, or losses that may arise from using the code generated or modified by this skill. These skills rely on AI agents to produce code, and all generated code should be carefully reviewed and verified by a qualified engineer before being deployed to a production environment. **Card data never touches the POS** — it stays inside the pre-certified terminal. Production go-live is gated by J.P. Morgan validation.

Use `AskUserQuestion`:
- Question: "Do you acknowledge the disclaimer above and want to proceed?"
- Header: "Acknowledge"
- Options:
  - "Yes — proceed"
  - "No — exit"

If **No**, exit this skill.

## Step 1 — Triage intent

Ask:
- Question: "What are you trying to do with J.P. Morgan In-Store Payments?"
- Header: "Goal"
- Options:
  - "Migrate an existing POS integration" — add J.P. Morgan payments to an existing POS or move from another provider
  - "Start a new POS integration" — build a new integration from scratch

Remember the answer as `intent`.

## Step 2 — Integration model

Ask:
- Question: "Which integration model are you targeting?"
- Header: "Model"
- Options:
  - "Semi-integrated (POS ↔ terminal over WebSocket)" — **recommended, the primary v1 model**
  - "On-device (checkout app runs on the terminal)" — conceptual only for v1

Remember as `model`.

- If **Semi-integrated**, continue to Step 3.
- If **On-device**, tell the user:

  > On-device checkout (your app running on the terminal itself) is not supported in v1 - these skills implement the semi-integrated WebSocket model only. On-device is planned for a future release, and I've noted your interest.

  Then ask:
  - Question: "Do you want to continue with the semi-integrated model, or exit?"
  - Header: "Continue?"
  - Options:
    - "Continue with semi-integrated" - build against the supported v1 model
    - "Exit - I need on-device" - stop here

  If **Exit - I need on-device**, print a one-line summary of the captured `intent` and requested on-device model, then exit this skill.

  If **Continue with semi-integrated**, record `model = semi-integrated (on-device requested)` and continue to Step 3.

## Step 3 — Onboarded?

The terminal is provisioned by J.P. Morgan. To run transactions and complete validation you need: your **HWVENDORID** (a mandatory identifier set at startup via `SetParameter`), the **POS client certificate and private key plus terminal trust material** for the mutual TLS WebSocket connection, pre-configured test terminal(s), required EMV test cards, and your assigned **validation artifacts** (go-live worksheet and validation contact).

Ask:
- Question: "Have you completed JPM in-store onboarding and received your HWVENDORID, POS client certificate/key, terminal trust material, test terminal access, EMV test cards, validation worksheet, and validation contact?"
- Header: "Onboarded?"
- Options:
  - "Yes — I have what I need"
  - "No — I'm missing one or more items"

If **No**, go to Step 8. If **Yes**, go to Step 4.

## Step 4 — Network readiness

The POS reaches the terminal over the local network on **port 8442** (`wss://<terminal-ip>:8442`). Walk the developer through `references/network-checklist.md` and capture the answers. Ask (free text is fine for each; group them):

1. **Terminal IP addressing** — is the terminal on a static IP or DHCP reservation on the same LAN/VLAN as the POS?
2. **Port & mutual TLS** — is TCP **port 8442** open between the POS and terminal (firewall allows it, not blocked or remapped), is the POS configured to present its client certificate/private key, and does it trust the terminal certificate for the `wss://` (TLS 1.2) connection?

Summarize the captured values back to the user (mask nothing here except never echo private keys). Flag any answer that would block connectivity and point to `references/network-checklist.md` for remediation.

## Step 5 — Capture terminal models

These skills implement the semi-integrated WebSocket model in v1. Read the **Supported Ingenico AXIUM terminal models** section in `references/terminals-and-operations.md` before asking the question below.

- Question: "Which terminal(s) are you integrating? (Select all that apply.)"
- Header: "Terminals"
- Options (multiSelect): Present every model in the authoritative terminal catalogue, preserving its model names and order.

Remember as `terminals`.

## Step 6 — Target language & configuration file

Before setting up config, capture the programming language the POS integration will be built in — the config store depends on it, and the downstream skills need it so they don't re-ask. Detect first, then ask only if you can't infer:

1. **Detect.** Look in the current working directory for a dependency manifest and stop at the first match: `package.json` → JavaScript/TypeScript; `requirements.txt`/`pyproject.toml`/`Pipfile`/`setup.py` → Python; `pom.xml` → Java (Maven); `build.gradle`/`build.gradle.kts` → Kotlin/Java (Android/Gradle); `go.mod` → Go; `Cargo.toml` → Rust; `Gemfile` → Ruby; `composer.json` → PHP; `*.csproj`/`*.fsproj` → .NET.
2. **Ask only if undetected:**
   - Question: "Which programming language will your POS integration be written in?"
   - Header: "Language"
   - Options:
     - "JavaScript / TypeScript (Node.js)"
     - "Kotlin / Java (Android)"
     - "Python"
     - "C# / .NET"
     - "Other — tell me which"

   If the user picks **Other**, ask which language (free text).

Remember the answer as `language` and carry it into the downstream skills so it isn't asked again.

**Pick the config store from `language`.** These skills never hardcode hosts or identifiers — they live in a per-project config file whose format depends on the stack:

- **Kotlin / Java (Android, Gradle project)** → use **`local.properties`** with dotted keys (`jpm.terminal.host`, `jpm.terminal.port`, `jpm.hwvendorid`, `jpm.env`). Android projects already gitignore `local.properties` by default, and the values are surfaced to app code as `BuildConfig` fields (read from `Properties` at build time). This is the idiomatic Android pattern — **Android apps do not use `.env` files.** Template: `templates/local.properties.jpm.example`.
- **Every other language (Node/TypeScript, Python, .NET, Go, and so on)** → use **`instore.env`** with `JPM_*` keys. Template: `templates/instore.env.example`.

Call the chosen file the **config file** below. Read its template (relative to this skill directory) to determine the variable names this integration expects. The corresponding `.example` file is `instore.env.example` for env-based stacks and `local.properties.jpm.example` for Android. For every branch, record `placeholderKeys`: expected variables that are missing, empty, or exactly `<fill-me>`, plus every variable that this step writes with `<fill-me>`. Pass this state to Step 7; list names only, never values.

Then look in the user's current working directory for the config file and branch on what you find. Do **not** ask the user "generate or update?" — the file's presence and contents determine the branch. Whenever an `.example` file is missing, copy the chosen skill template into the project root. Do not overwrite an existing project `.example` file.

### 6a — Config file exists and has every expected variable

Ensure the corresponding `.example` file exists as described above. Tell the user (one line): "Your `<config file>` already has all expected in-store variables — skipping setup." Go to Step 7.

### 6b — Config file exists but is missing one or more expected variables

List the missing variable names to the user (names only — never echo values from the existing file), then ask:

- Question: "I'll append the missing variables to your existing `<config file>` with placeholder values. Proceed?"
- Header: "Update config?"
- Options:
  - "Yes — add them"
  - "No — I'll handle it"

If **Yes**:
1. Append each missing variable as `<variable>=<fill-me>` to the bottom of the config file. Do **not** overwrite values the user has already set. For Android, append the `jpm.*` keys to `local.properties`; for every other stack, append the `JPM_*` keys to `instore.env`.
2. Ensure the config file is gitignored. For `instore.env`: read `.gitignore` in the project root and, if a line equal to `instore.env` is not present, append it (create `.gitignore` with that line if it doesn't exist). For `local.properties`: it's already gitignored in a standard Android project — confirm it's listed and only add it if missing.
3. Create the corresponding `.example` file from the skill template if it is missing. Do not overwrite an existing project `.example` file.
4. Confirm to the user which variables were added (by name only) and that the example file is available for the repository.

Go to Step 7 either way.

### 6c — No config file found

Ask:
- Question: "No `<config file>` found in the project. Create placeholder configuration and a committable example from the skill template?"
- Header: "Config setup"
- Options:
  - "Yes — create it"
  - "No — I'll create it myself"

If **Yes**:
1. Copy the chosen template into the user's current working directory as a committable `.example` sample — `templates/instore.env.example` → `instore.env.example` for env-based stacks, or `templates/local.properties.jpm.example` → `local.properties.jpm.example` for Android. Do not overwrite an existing project `.example` file.
2. For env-based stacks, create `instore.env` with every expected `JPM_*` key set to `<fill-me>`. Ensure it is gitignored (same rule as 6b step 2).
3. For Android, never create or recreate `local.properties`. Because it was not found on this branch, explain that Android Studio/Gradle must create or restore this project-specific file before its missing `jpm.*` keys can be appended; do not write a replacement file.
4. Tell the user what to do next:
   - **env-based stacks:** "Created `instore.env` with placeholder values and `instore.env.example` for your repo, and confirmed `instore.env` is gitignored. Fill in the terminal IP, HWVENDORID, and environment before running a transaction - don't commit `instore.env`."
   - **Android without `local.properties`:** "Created `local.properties.jpm.example` for your repo. Restore or create `local.properties` through Android Studio/Gradle, then append the `jpm.*` keys with placeholder values; never commit `local.properties`. Wire the values into `BuildConfig` in your `build.gradle(.kts)` - the sample shows how."

Go to Step 7 either way.

## Step 7 — Hand off

If `placeholderKeys` is non-empty, warn before asking the next question: "Before running a transaction, replace placeholder values for: `<placeholder key names>`." Do not include values in this warning.

The intake is complete. Ask where the user wants to go next:
- Question: "What would you like to do next?"
- Header: "Next"
- Options:
  - "Start building the integration" — implement real operations one at a time
  - "Nothing right now — exit"

- If **build**, hand off to `jpm-instore-payments`. Remind the user that `SetParameter HWVENDORID` is the mandatory first POS-sent terminal operation after readiness. Pass the target `language` in context.
- If **exit**, print a short summary of what was captured (intent, model, terminals, network readiness, config file, language) and exit.

## Step 8 — Not yet onboarded

Tell the user:

> In-store onboarding and terminal provisioning are handled by your J.P. Morgan implementation contact / Relationship Manager (RM). Please reach out to them to begin onboarding and to receive your **HWVENDORID**, the **POS client certificate/private key and terminal trust material**, your **supported AXIUM terminal(s)**, and the **validation worksheet** that gates go-live. Once you have them, run this skill again.
> You should also confirm test terminal access, required EMV test cards, network readiness, and your assigned validation contact before starting implementation.

Then exit.

## Rules

- **'Select all' in multi-select questions** — When the user selects "Select all" from any multiSelect option list, treat it as if every other option in that list was selected.
- Never write the HWVENDORID, certificate contents, or private key contents to any persistent file under your control. The only files this skill creates or modifies are the config-file sample (`instore.env.example` or `local.properties.jpm.example`, placeholders only), the user's config file (only with `<fill-me>` placeholders for new values — never overwriting existing values), and `.gitignore` (to ensure `instore.env` is ignored; confirm `local.properties` is ignored in Android projects). Never create or recreate Android's `local.properties`.
- **Card data never touches the POS.** It stays inside the pre-certified terminal. Never generate code or configuration that would send PAN/PIN/CVV/track data to the POS.
- Always mask identifiers when echoing them back (last 4 chars only). Never echo or log private keys or values already set in the user's config file.
- Confirm the file path before writing anything.
- The **semi-integrated WebSocket model on port 8442** is the only model these skills implement in v1. Mark on-device as future/WIP if asked.
- Production go-live is **gated by J.P. Morgan validation** — always present validation as an explicit, tracked step, never as optional.
- Payment-related changes after validation require revalidation with J.P. Morgan. Tell the developer to discuss new APIs or significant flow changes with their Relationship Manager / integration contact.
