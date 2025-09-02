## monarch-money-mcp-enhanced v0.2.5

This release automatically synchronizes the MCP server version with the latest `monarchmoney-enhanced` library.

### Changes
- Updated `monarchmoney-enhanced` from `` to `0.2.5`
- MCP server version synchronized to `0.2.5`
- All MonarchMoney methods are automatically exposed as MCP tools
- No manual intervention required - the server dynamically adapts to library changes

### New Features
Any new methods added to `monarchmoney-enhanced` v0.2.5 are automatically available as MCP tools.

### Installation
Update your Claude Desktop configuration:
```json
{
  "mcpServers": {
    "monarch-money-enhanced": {
      "command": "/path/to/uv",
      "args": ["--directory", "/path/to/monarch-money-mcp-enhanced", "run", "python", "server.py"],
      "env": {
        "MONARCH_EMAIL": "your-email@example.com",
        "MONARCH_PASSWORD": "your-password",
        "MONARCH_MFA_SECRET": "your-mfa-secret"
      }
    }
  }
}
```
