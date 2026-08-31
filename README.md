# J.P. Morgan Payments Developer Portal — Merchant Integrations Agent Skills

A set of [Agent Skills](https://agentskills.io/) that give GitHub Copilot, Claude Code, Cursor, and other Agent harnesses procedural knowledge of J.P. Morgan's Payments Developer Portal (PDP) APIs. They provide a conversational experience that walks you from getting started with J.P. Morgan Payments APIs to integrating with new ones and expanding your integration — without you having to re-read the docs.

## Disclaimer

> **Use at Your Own Risk.** The code and instructions provided in this repository are intended for reference purposes only. The maintainers of this repository do not assume any responsibility for any issues, damages, or losses that may arise from the use of this code or instructions.

These skills rely on AI agents to produce code, and **all generated code must be reviewed and verified by a qualified engineer before being deployed to production**. AI-generated code can contain subtle correctness, security, or compliance defects.

---

## What's Inside

This repository ships **three Agent Skills** that chain together. Each also works on its own.

| Skill | Path | Purpose |
| ----- | ---- | ------- |
| `jpm-integrations-get-started` | [`skills/jpm-integrations-get-started/`](skills/jpm-integrations-get-started/SKILL.md) | Get started with J.P. Morgan Payments — disclaimer acknowledgment, goal triage, credential check, and `.env` setup |
| `jpm-oauth` | [`skills/jpm-oauth/`](skills/jpm-oauth/SKILL.md) | Generates a working OAuth (JWT signing + IDAnywhere token exchange) module in your project, with token caching baked in |
| `jpm-merchant-integrations` | [`skills/jpm-merchant-integrations/`](skills/jpm-merchant-integrations/SKILL.md) | Walks you through one API integration at a time — Checkout or Online Payments — and helps you expand by adding new APIs over time |

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
| **Online Payments** | `skills/jpm-merchant-integrations/references/online-payments.md` | Full payment lifecycle (auth, capture, void, refund), card / wallet / APM methods, 3-D Secure |

More APIs (Tokenization, Reporting, and others) are planned for future releases.

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

After install, run `/plugin` to confirm it's listed and `/skills` to see the three `jpm-*` skills.

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

> **Tip:** You can invoke a skill explicitly via its slash command (for example, `/jpm-integrations-get-started`, `/jpm-oauth`, or `/jpm-merchant-integrations`) — works the same in both Claude Code and GitHub Copilot. Otherwise, any prompt that matches the skill's `description` field triggers it automatically.

---

## Usage

### Full walkthrough (recommended)

Start with the first skill — it hands off automatically through the full sequence:

```text
/jpm-integrations-get-started
```

`jpm-integrations-get-started` → `jpm-oauth` → `jpm-merchant-integrations`

### Individual skills

| Goal | Slash command |
| ---- | ------------- |
| Onboarding & `.env` setup | `/jpm-integrations-get-started` |
| Generate OAuth module | `/jpm-oauth` |
| Integrate Checkout or Online Payments | `/jpm-merchant-integrations` |

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
├── skills/                           # the three agent skills
│   ├── jpm-integrations-get-started/
│   ├── jpm-oauth/
│   └── jpm-merchant-integrations/
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
