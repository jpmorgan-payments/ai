# J.P. Morgan Payments Developer Portal — Merchant Integrations Agent Skills

A set of [Agent Skills](https://agentskills.io/) that give GitHub Copilot, Claude Code, Cursor, and other Agent harnesses procedural knowledge of J.P. Morgan's Payments Developer Portal (PDP) APIs. They provide a conversational experience that walks you from getting started with J.P. Morgan Payments APIs to integrating with new ones and expanding your integration — without you having to re-read the docs.

## Disclaimer

> **Use at Your Own Risk.** The code and instructions provided in this repository are intended for reference purposes only. The maintainers of this repository do not assume any responsibility for any issues, damages, or losses that may arise from the use of this code or instructions.

These skills rely on AI agents to produce code, and **all generated code must be reviewed and verified by a qualified engineer before being deployed to production**. AI-generated code can contain subtle correctness, security, or compliance defects.

> **Early access.** Account Updater, Tokenization, 3-D Secure, and `jpm-notifications` are early access — expect to do additional testing and validation before relying on them.

---

## What's Inside

This repository ships **seven Agent Skills** across two tracks — online and in-store. Within each track the skills chain together, and each also works on its own.

### Online integrations

| Skill | Path | Purpose |
| ----- | ---- | ------- |
| `jpm-integrations-get-started` | [`skills/jpm-integrations-get-started/`](skills/jpm-integrations-get-started/SKILL.md) | Get started with J.P. Morgan Payments — disclaimer acknowledgment, goal triage, credential check, and `.env` setup |
| `jpm-oauth` | [`skills/jpm-oauth/`](skills/jpm-oauth/SKILL.md) | Generates a working OAuth (JWT signing + IDAnywhere token exchange) module in your project, with token caching baked in |
| `jpm-merchant-integrations` | [`skills/jpm-merchant-integrations/`](skills/jpm-merchant-integrations/SKILL.md) | Walks you through one API integration at a time — Checkout or Online Payments — and helps you expand by adding new APIs over time |
| `jpm-csr` | [`skills/jpm-csr/`](skills/jpm-csr/SKILL.md) | **Standalone onboarding helper** (independent of the chain above) — generates a Certificate Signing Request (CSR) + private key to send to your J.P. Morgan Relationship Manager for client ID provisioning. Run it before onboarding if you don't yet have credentials |
| `jpm-notifications` | [`skills/jpm-notifications/`](skills/jpm-notifications/SKILL.md) | **Companion** to `jpm-merchant-integrations` — receive and verify inbound JPM webhook events (signature verification, optional mTLS, de-duplication) instead of polling. Assumes auth is already set up via `jpm-oauth` |

### In-store integrations

| Skill | Path | Purpose |
| ----- | ---- | ------- |
| `jpm-instore-get-started` | [`skills/jpm-instore-get-started/`](skills/jpm-instore-get-started/SKILL.md) | Conversational intake for a card-present integration against the J.P. Morgan Payments Terminal Application on Ingenico AXIUM terminals — triages new build vs. migration, runs a network questionnaire, and sets up an `instore.env` |
| `jpm-instore-payments` | [`skills/jpm-instore-payments/`](skills/jpm-instore-payments/SKILL.md) | Implements the semi-integrated terminal integration one operation at a time — setup/management, certificate operations, and payment operations such as sale, refund, void, gift cards, SAF, DCC, and settlement |

Each skill folder is composed of three layers:

| Layer | Path | Purpose |
| ----- | ---- | ------- |
| **SKILL.md** | `SKILL.md` | Entry point — the playbook the agent follows |
| **References** | `references/` | Per-API deep dives with flow diagrams, endpoint tables, field constraints, and sample requests |
| **Examples / Templates / Scripts** | `examples/`, `templates/`, `scripts/` | Reference samples and helpers the skill points to during execution |

### API Coverage

| API | Reference File | What It Covers |
| --- | -------------- | -------------- |
| **Checkout** | `skills/jpm-merchant-integrations/references/checkout.md` | Drop-in UI, Hosted Payments Page, checkout sessions, capture methods, field constraints |
| **Online Payments** | `skills/jpm-merchant-integrations/references/online-payments.md` | Full payment lifecycle (auth, capture, void, refund), card / wallet / APM methods, inline 3-D Secure |
| **Tokenization** | `skills/jpm-merchant-integrations/references/tokenization.md` | Swap a card PAN for a merchant-scoped token to reduce PCI scope and store tokens instead of card data |
| **3-D Secure (Standalone)** | `skills/jpm-merchant-integrations/references/3d-secure.md` | Standalone 3DS authentication (use the inline `threeDS` field in Online Payments when bundling with an auth) |
| **Account Updater** | `skills/jpm-merchant-integrations/references/account-updater.md` | Keep stored cards current as issuers reissue them — inquiry mode (sync) or card-registration mode (async, via `jpm-notifications`) |
| **In-Store (semi-integrated terminal)** | `skills/jpm-instore-payments/references/official-protocol-reference.md` | Semi-integrated WebSocket protocol, terminal operations, transaction types, result codes, SAF / DCC / settlement, certificate operations |

More APIs (Reporting and others) are planned for future releases.

---

## Installation

The skills are written in the open [Agent Skills](https://agentskills.io/) format and load in any compatible Agent harness. Below are the install paths:

### Skills CLI

[`npx skills`](https://www.skills.sh/) detects your Agent harness and installs into the right directory automatically:

```bash
npx skills add jpmorgan-payments/pdp-skills
```

### Claude Code

The fastest path is the Claude Code plugin manager — this repository ships as a plugin with a marketplace manifest at the root.

#### Plugin install

Inside Claude Code, run:

```text
/plugin marketplace add https://github.com/jpmorgan-payments/pdp-skills
/plugin install jpm-payments-skills@jpm-payments-skills
```

After install, run `/plugin` to confirm it's listed and `/skills` to see the seven `jpm-*` skills.

To update later:

```text
/plugin update jpm-payments-skills
```

#### Manual install

If you'd rather copy the skills directly into your project, Claude Code auto-discovers any skills under `.claude/skills/`:

```bash
git clone https://github.com/jpmorgan-payments/pdp-skills /tmp/jpm-skills
mkdir -p .claude/skills
cp -r /tmp/jpm-skills/skills/jpm-* .claude/skills/
```

For a user-level install (every Claude Code project sees the skills), copy into `~/.claude/skills/` instead.

### GitHub Copilot

GitHub Copilot automatically discovers skills placed in `.github/skills/` at the root of your repository. No extra configuration is needed.

```bash
git clone https://github.com/jpmorgan-payments/pdp-skills /tmp/jpm-skills
mkdir -p .github/skills
cp -r /tmp/jpm-skills/skills/jpm-* .github/skills/
```

Open your project in VS Code or a JetBrains IDE with GitHub Copilot Chat enabled, then start asking questions. Copilot loads the relevant skill automatically when your prompt matches the skill's `description` field.

> **Tip:** You can invoke a skill explicitly via its slash command (for example, `/jpm-integrations-get-started`, `/jpm-oauth`, `/jpm-merchant-integrations`, `/jpm-instore-get-started`, or `/jpm-instore-payments`) — works the same in both Claude Code and GitHub Copilot. Otherwise, any prompt that matches the skill's `description` field triggers it automatically.

---

## Usage

### Full walkthrough (recommended)

Start with the first skill in your track — it hands off automatically through the full sequence:

```text
/jpm-integrations-get-started
```

`jpm-integrations-get-started` → `jpm-oauth` → `jpm-merchant-integrations`

For an in-store (card-present) integration, start with:

```text
/jpm-instore-get-started
```

`jpm-instore-get-started` → `jpm-instore-payments`

### Individual skills

| Goal | Slash command |
| ---- | ------------- |
| Generate a CSR + private key for onboarding | `/jpm-csr` |
| Onboarding & `.env` setup | `/jpm-integrations-get-started` |
| Generate OAuth module | `/jpm-oauth` |
| Integrate Checkout or Online Payments | `/jpm-merchant-integrations` |
| Receive & verify webhook events | `/jpm-notifications` |
| In-store onboarding & `instore.env` setup | `/jpm-instore-get-started` |
| Integrate in-store terminal operations | `/jpm-instore-payments` |

> Each skill checks its own prerequisites and will tell you what to run first if anything is missing.

---

## Repo Structure

```
.
├── .claude-plugin/                   # Claude Code plugin manifest + marketplace listing
│   ├── plugin.json
│   └── marketplace.json
├── .github/
│   └── workflows/                    # daily GitHub traffic-metrics collection
├── skills/                           # the seven agent skills
│   ├── jpm-integrations-get-started/
│   ├── jpm-oauth/
│   ├── jpm-merchant-integrations/
│   ├── jpm-csr/
│   ├── jpm-notifications/
│   ├── jpm-instore-get-started/
│   └── jpm-instore-payments/
├── LICENSE
└── README.md
```

---

## Contributing to JPMC Projects

Only valid contributors are able to provide contributions to this repository.

If this is your first time contributing to JPMC codebases you will need to fill out our Contribution Licence Agreement (CLA). More information can be found at: <https://github.com/jpmorganchase/.github/blob/main/CONTRIBUTING.md>

---

## License

This project is licensed under the Apache License 2.0 — see the [LICENSE](LICENSE) file for details.
