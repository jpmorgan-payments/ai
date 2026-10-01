# J.P. Morgan Payments AI

One-stop AI toolkit for building, integrating, and scaling AI-powered products with J.P. Morgan Payments APIs.

This repository equips GitHub Copilot, Claude Code, Cursor, and other agent harnesses with working knowledge of the J.P. Morgan Payments APIs. Instead of context-switching to the docs, you describe what you want to build and your agent handles onboarding, authentication, and the integration itself.

> **Use at Your Own Risk.** The code and instructions in this repository are provided for reference purposes only. The maintainers do not assume responsibility for any issues, damages, or losses arising from their use. These tools rely on AI agents to produce code, and **all generated code must be reviewed and verified by a qualified engineer before being deployed to production.** AI-generated code can contain subtle correctness, security, or compliance defects.

---

## What's inside

| Component | Description |
| --------- | ----------- |
| **[Agent Skills](skills/README.md)** — [`skills/`](skills/) | Procedural playbooks that walk your agent through onboarding, OAuth, and API integration — Checkout, Online Payments, and more. |
| **[MCP Server](mcp/README.md)** — [`mcp/`](mcp/) | A Model Context Protocol server that puts the entire PDP documentation set at your agent's fingertips: search, read, and find related docs. |

Each component has its own README with full setup and usage instructions.

---

## Prerequisites

- A J.P. Morgan Payments developer account and access to the [Payments Developer Portal (PDP)](https://developer.payments.jpmorgan.com/).
- API credentials for your target environment (CAT or PROD): `clientId`, certificate, and private key. No credentials yet? Start with `/jpm-csr` to generate a CSR for your Relationship Manager.
- An agent harness: GitHub Copilot, Claude Code, Cursor, or another compatible client.

---

## Agent skills

[Agent skills](https://agentskills.io/) are instructions that agents can use to build faster and more accurately. J.P. Morgan Payments offers a collection of skills that give your agents working knowledge of the J.P. Morgan Payments APIs — onboarding, authentication, and integration.

If you use one of these popular agent harnesses, we recommend installing the official J.P. Morgan Payments plugins, which bundle every skill and update automatically.

### Claude Code

Run these commands in your project:

```text
/plugin marketplace add https://github.com/jpmorgan-payments/ai
/plugin install jpm-payments-skills@jpm-payments-skills
```

### Codex

Run these commands in your project:

```bash
codex plugin marketplace add jpmorgan-payments/ai
codex plugin add jpm-payments-skills@jpm-payments
```

### Cursor

Run this command in your project:

```text
/add-plugin jpm-payments-skills
```

## Manual installation

> Manually installed skills don't auto-update. Run `npx skills update -y` to get the latest versions.

Run this command in your project:

```bash
npx skills add jpmorgan-payments/ai
```

See the [Agent Skills README](skills/README.md) for GitHub Copilot, local installs, and per-skill detail.

---

## Troubleshooting

| Symptom | Likely cause | What to try |
| ------- | ------------ | ----------- |
| Slash command not recognized | Skills not installed, or agent not reloaded | Re-run the install command and reload your agent |
| `401` / `403` on API calls | Invalid or expired credentials, wrong environment | Verify `clientId`, key, and that you're targeting the correct CAT/PROD endpoint |
| Agent can't find API docs | MCP server not running or client not pointed at it | Confirm the local MCP server is running and registered in your client config |
| OAuth token errors | Certificate / private key mismatch | Re-check your key pair and certificate registration in the developer portal |

---

## Support

- Browse the per-component READMEs — [Agent Skills](skills/README.md) and [MCP Server](mcp/mcp-for-api-documentation/README.md) — for detailed setup and usage.
- For API-specific questions, consult the [Payments Developer Portal](https://developer.payments.jpmorgan.com/).
- For repository issues, open a GitHub issue.

---

## Contributing to JPMC Projects

Only valid contributors are able to provide contributions to this repository.

If this is your first time contributing to JPMC codebases you will need to fill out our Contribution Licence Agreement (CLA). More information can be found at: <https://github.com/jpmorganchase/.github/blob/main/CONTRIBUTING.md>

---

## License

This project is licensed under the Apache License 2.0 — see the [LICENSE](LICENSE) file for details.
