# J.P. Morgan Model Context Protocol Server for Payments Developer Portal Documentation

A Model Context Protocol (MCP) server that provides seamless access to J.P. Morgan's Payment Developer Portal (PDP) documentation and resources. This server enables developers to search, read, and discover payment API documentation through AI-powered interfaces like GitHub Copilot.

## Overview

This MCP server acts as a bridge between your development environment and the J.P. Morgan Payment Developer Portal, allowing you to:

- Access comprehensive payment API documentation
- Search for specific payment solutions and features
- Discover related content and resources
- Get contextual help while coding payment integrations


## Features

This MCP server provides three core capabilities to enhance your development experience:

- **📚 Read Documentation**: Fetch and convert PDP API documentation pages to markdown format for easy consumption
- **🔍 Search Documentation**: Find relevant documentation using the official PDP Search API
- **🔗 Related Content**: Discover related pages and resources for comprehensive understanding


## Prerequisites

Ensure your development environment meets these requirements:

- **Python**: Version 3.10 or newer
- **Package Manager**: `uv` or `pip`
- **Development Tools**: Git and Node.js (required for MCP Inspector testing)


## Installation

Choose your preferred installation method:

### Option 1: Using uv (Recommended)

`uv` provides faster dependency resolution and better environment management:

1. **Install uv**:
   ```bash
   pip install uv
   ```

2. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd mcp-for-api-documentation
   uv venv
   uv pip install -e .
   ```

### Option 2: Using pip

For traditional Python environments:

```bash
pip install git+<repository-url>
```

> **Note**: Replace `<repository-url>` with the actual repository URL when available.

## Usage

### Running the Server

Start the MCP server directly as a Python module:

```bash
cd mcp-for-api-documentation
python -m jpmc.mcp_for_api_documentation.server
```

### Local Testing and Development

Test the server locally using either package manager:

#### Testing with uv

**Standalone server**:
```bash
uv --directory <path-to-project> run jpmc.mcp_for_api_documentation
```

**With MCP Inspector** (for interactive testing):
```bash
npx @modelcontextprotocol/inspector uv --directory <path-to-project> run jpmc.mcp_for_api_documentation
```

#### Testing with pip

**Environment setup**:
```bash
cd <path-to-project>
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

**Install dependencies**:
```bash
pip install "markdownify>=1.1.0" "mcp[cli]>=1.11.0" "pydantic>=2.10.6" "httpx>=0.27.0" "loguru>=0.7.0" "beautifulsoup4>=4.12.0"
```

**Run server**:
```bash
# Standalone
python -m jpmc.mcp_for_api_documentation.server

# With MCP Inspector
npx @modelcontextprotocol/inspector python -m jpmc.mcp_for_api_documentation.server
```


## Integration with MCP Clients

Configure the MCP server with your preferred MCP client (e.g., GitHub Copilot in VS Code or IntelliJ IDEA):

### Configuration Example

```json
{
  "mcpServers": {
    "jpmc.mcp_for_api_documentation": {
      "command": "uv",
      "args": [
        "--directory",
        "<path-to-this-py-project>",
        "run",
        "jpmc.mcp_for_api_documentation"
      ],
      "env": {
        "FASTMCP_LOG_LEVEL": "ERROR"
      }
    }
  }
}
```

### Configuration Notes

⚠️ **Important**: Adjust the configuration based on your environment:

1. **Command Path**: Use the absolute path for `uv`, or substitute `"python"` if `uv` is unavailable
2. **Corporate Networks**: Add `"HTTP_PROXY": "your-proxy-url"` to the `env` section if behind a proxy
3. **Project Path**: Replace `<path-to-this-py-project>` with the actual path to your installation

### Alternative Configuration (using Python directly)

```json
{
  "mcpServers": {
    "jpmc.mcp_for_api_documentation": {
      "command": "python",
      "args": [
        "-m",
        "jpmc.mcp_for_api_documentation.server"
      ],
      "cwd": "<path-to-this-py-project>",
      "env": {
        "FASTMCP_LOG_LEVEL": "ERROR"
      }
    }
  }
}
```

## Available Tools

The server provides three tools for accessing J.P. Morgan Payments API documentation:

### 🔍 search_documentation

Search across all PDP API documentation using the official Search API.

**Function Signature:**
```python
search_documentation(
    search_phrase: str,  # The phrase to search for
    limit: int = 10      # Maximum number of results (1-50, default: 10)
) -> List[SearchResult]  # Returns matching document references
```

**Example Usage:**
```python
# Search for checkout documentation
results = search_documentation("checkout session", limit=5)
```

### 📖 read_documentation

Fetch and convert a specific PDP documentation page to markdown format.

**Function Signature:**
```python
read_documentation(
    url: str            # URL of the documentation page to read
) -> str                # Returns markdown-formatted content
```

**Example Usage:**
```python
# Read a specific documentation page
content = read_documentation("https://developer.payments.jpmorgan.com/docs/commerce/...")
```

### 🔗 related

Discover related content recommendations for a specific documentation page.

**Function Signature:**
```python
related(
    url: str             # URL of the documentation page
) -> List[RecommendationResult]  # Returns related document references
```

**Example Usage:**
```python
# Find related pages
related_docs = related("https://developer.payments.jpmorgan.com/docs/commerce/...")
```

## Example Use Cases

Here are practical examples of how to interact with the MCP server through your AI assistant:

### 📚 Documentation Discovery
```
"Look up checkout-related documents, citing the sources"
```
```
"Find documentation about payment methods"
```
```
"Search for information about webhooks and event notifications"
```

### 🔗 Content Exploration
```
"Get related pages for https://developer.payments.jpmorgan.com/docs/commerce/optimization-protection/capabilities/consumer-profile-management/payment-methods"
```
```
"Show me similar documentation to the current page I'm reading"
```

### 🛠️ API Implementation Help
```
"I want to add a product to the merchant catalog, can you help me format the API request?"
```
```
"I want to setup a checkout intent session, can you help me format the API request?"
```
```
"I want to create a payment link, help me format the API request"
```
```
"I am a merchant developer, I want to create a JPMC checkout setup intent call using Python. My merchant ID is <MERCHANT_ID>"
```

### 🔍 Troubleshooting and Support
```
"How do I handle payment failures in the checkout process?"
```
```
"What are the required fields for creating a payment session?"
```
```
"Show me examples of webhook payload structures"
```


## Development

Contributors and developers must use the following steps to run tests and validate changes.

### Setting Up Development Environment

1. **Clone and install in development mode**:
   ```bash
   git clone <repository-url>
   cd mcp-for-api-documentation
   pip install -e ".[dev]"
   ```

2. **Run tests**:
   ```bash
   pytest tests/
   ```

### Environment Variables

Configure the following environment variables as needed:

| Variable | Description | Default |
|----------|-------------|---------|
| `HTTP_PROXY` | HTTP proxy server URL | None |
| `HTTPS_PROXY` | HTTPS proxy server URL | None |
| `FASTMCP_LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | WARNING |

### Testing with Different Configurations

**Test with proxy**:
```bash
HTTP_PROXY=http://proxy.company.com:8080 python -m jpmc.mcp_for_api_documentation.server
```

**Test with debug logging**:
```bash
FASTMCP_LOG_LEVEL=DEBUG python -m jpmc.mcp_for_api_documentation.server
```


## License

This project is licensed under the Apache License 2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE) files for details.

---

**Questions or feedback?** Please reach out through the repository's issue tracker or contact the J.P. Morgan Payments Developer Portal team.
