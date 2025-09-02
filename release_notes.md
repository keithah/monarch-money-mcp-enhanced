## Auto-Release v0.2.1

This release automatically updates the MCP server to work with the latest `monarchmoney-enhanced` library.

### Changes
- Updated `monarchmoney-enhanced` from `` to `0.2.1`
- All MonarchMoney methods are automatically exposed as MCP tools
- No manual intervention required - the server dynamically adapts to library changes

### New Features
Any new methods added to `monarchmoney-enhanced` v0.2.1 are automatically available as MCP tools.

### Installation
Update your Claude Desktop configuration to use this latest version:
```json
{
  "mcpServers": {
    "monarch-money": {
      "command": "/path/to/uv",
      "args": ["--directory", "/path/to/monarch-money-mcp", "run", "python", "server.py"],
      "env": {
        "MONARCH_EMAIL": "your-email@example.com",
        "MONARCH_PASSWORD": "your-password",
        "MONARCH_MFA_SECRET": "your-mfa-secret"
      }
    }
  }
}
```
