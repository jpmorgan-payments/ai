---
name: jpm-integrations-get-started
description: Triage and credential intake for merchants starting with J.P. Morgan Payments APIs. Use this skill when the user wants to migrate from another payment provider to JPM or start a new JPM integration from scratch. Sets up a .env file (generated fresh or updated in place) with the clientId, certificate path, and private key path that downstream skills will read at runtime. Does not persist credential contents.
---

# JPM Integrations — Get Started

Run a conversational intake for merchants getting started with J.P. Morgan Payments APIs. Follow the steps in order. Use `AskUserQuestion` for every multiple-choice question.

## Disclaimer (show before Step 1)

Before running the intake, show the user this disclaimer verbatim and wait for them to acknowledge before proceeding:

> **Disclaimer:** We do not assume any responsibility for any issues, damages, or losses that may arise from using the code generated or modified by this skill. These skills rely on AI agents to produce code, and all generated code should be carefully reviewed and verified by a qualified engineer before being deployed to a production environment.

Use `AskUserQuestion`:
- Question: "Do you acknowledge the disclaimer above and want to proceed?"
- Header: "Acknowledge"
- Options:
  - "Yes — proceed"
  - "No — exit"

If **No**, exit this skill.

## Step 1 — Triage intent

Ask:
- Question: "What are you trying to do with J.P. Morgan Payments?"
- Header: "Goal"
- Options:
  - "Migrate from another provider" — moving from a non-JPM processor (Stripe, Adyen, etc.)
  - "Start a new JPM integration" — greenfield project

Remember the answer as `intent`.

## Step 2 — Onboarded?

Ask:
- Question: "Have you completed JPM onboarding and received your clientId, certificate, and private key?"
- Header: "Onboarded?"
- Options:
  - "Yes — I have all three"
  - "No — not yet"

If **No**, go to Step 5. If **Yes**, go to Step 3.

## Step 3 — Set up the .env file

Read `templates/env.example` (relative to this skill directory) to determine the variable names this integration expects. Then look in the user's current working directory for a `.env` file and branch based on what you find. Do **not** ask the user "generate or update?" — the file's presence and contents determine the branch.

### 3a — `.env` exists and has every expected variable set

Tell the user (one line): "Your `.env` already has all expected JPM variables — skipping `.env` setup." Go to Step 4.

### 3b — `.env` exists but is missing one or more expected variables

List the missing variable names to the user (names only — never echo values from the existing file), then ask:

- Question: "I'll append the missing variables to your existing `.env` with placeholder values. Proceed?"
- Header: "Update .env?"
- Options:
  - "Yes — add them"
  - "No — I'll handle it"

If **Yes**:
1. Append each missing variable (with a placeholder value) to the bottom of `.env`. Do **not** overwrite values the user has already set.
2. Read `.gitignore` in the project root. If a line equal to `.env` is not present, append `.env` to it. If `.gitignore` doesn't exist, create one containing `.env`.
3. Confirm to the user which variables were added (by name only) and remind them to fill in any placeholders before running downstream skills.

Go to Step 4 either way.

### 3c — No `.env` found

Ask:

- Question: "No `.env` found in the project. Generate a sample one from the skill template?"
- Header: ".env setup"
- Options:
  - "Yes — generate sample"
  - "No — I'll create it myself"

If **Yes**:
1. Copy `templates/env.example` to `.env.example` in the user's current working directory.
2. Read `.gitignore` in the project root. If a line equal to `.env` is not present, append `.env` to it. If `.gitignore` doesn't exist, create one containing `.env`.
3. Tell the user: "Created `.env.example` in your project root and ensured `.env` is gitignored. Copy `.env.example` to `.env`, fill in the values, and do not commit `.env`. Downstream skills will read these at runtime."

Go to Step 4 either way.

## Step 4 — Implement auth?

This step runs after the `.env` has been generated or updated. The user has confirmed possession (or imminent possession via `.env`) of clientId + cert + key. Credential validation happens downstream when `jpm-oauth` (or the next skill that needs them) actually loads the `.env`.

Ask:
- Question: "Would you like me to implement the JPM OAuth flow now?"
- Header: "Implement auth?"
- Options:
  - "Yes — generate auth code"
  - "No — I'll do it later"

If **No**: exit.

If **Yes**:

1. **Detect language and libraries.** Look in the user's current working directory for a dependency manifest. Check in this order and stop at the first match:
   - `package.json` → JavaScript / TypeScript
   - `requirements.txt`, `pyproject.toml`, `Pipfile`, `setup.py` → Python
   - `pom.xml` → Java (Maven)
   - `build.gradle`, `build.gradle.kts` → Java / Kotlin (Gradle)
   - `go.mod` → Go
   - `Cargo.toml` → Rust
   - `Gemfile` → Ruby
   - `composer.json` → PHP
   - `*.csproj`, `*.fsproj` → .NET

   If a manifest is found, scan its dependencies for any HTTP client (axios, node-fetch, got, undici, requests, httpx, okhttp, reqwest, etc.) and any JWT/crypto library (jsonwebtoken, jose, pyjwt, jjwt, golang-jwt, etc.) the project already uses. The point of this scan is to reuse what's already there rather than introduce new dependencies.

2. **Decide whether to ask the user.** The principle: only ask for what you couldn't infer.
   - If language is detected **and** at least one HTTP client **and** a JWT library are already present in the manifest, do not ask — just announce: "Detected `<language>` with `<http-lib>` and `<jwt-lib>` — the auth implementation will use those."
   - Otherwise prompt the user (free text) for the gaps only:
     - Programming language (if not detected)
     - Preferred HTTP client (if none in manifest) — user can answer "any"
     - Preferred JWT library (if none in manifest) — user can answer "any"

3. **Hand off to `jpm-oauth`.** Invoke the `jpm-oauth` skill via the Skill tool. The OAuth skill picks up the conversation context — credentials location, SHA-1 thumbprint, integration intent from Step 1, and target stack (language + HTTP client + JWT library) — and only asks the user for what it doesn't already know (target environment CAT/PROD, JWT TTL, and output location for the generated code). The `resource_id` is read from `JPM_RESOURCE_ID` in the `.env` at runtime — the user fills it in using the comment already in `.env.example`, no question is asked. Exit this skill once `jpm-oauth` takes over.

## Step 5 — Not yet onboarded

<!-- TODO(content+legal): confirm exact wording with the content and legal teams before release. -->

Tell the user:

> JPM onboarding is handled by your Relationship Manager (RM). Please reach out to your RM to begin onboarding and to receive your clientId, certificate, and private key. Once you have them, run this skill again.

Then exit.

## Rules

- Never write clientId, cert contents, or private key contents to any persistent file under your control. The only files this skill creates or modifies are `.env.example` (placeholders only), the user's `.env` (only to append missing variable names with placeholder values — never overwriting existing values), and `.gitignore` (to ensure `.env` is ignored).
- Always mask the clientId when echoing it back (last 4 chars only).
- Never echo or log the contents of the private key, nor any value already set in the user's `.env`.
