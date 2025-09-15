## monarch-money-mcp-enhanced v0.9.3

This release automatically synchronizes the MCP server version with the latest `monarchmoney-enhanced` library.

### Changes
- Updated `monarchmoney-enhanced` from `0.9.2` to `0.9.3`
- MCP server version synchronized to `0.9.3`
- All MonarchMoney methods are automatically exposed as MCP tools
- No manual intervention required - the server dynamically adapts to library changes

### New Features
Any new methods added to `monarchmoney-enhanced` v0.9.3 are automatically available as MCP tools.

### Installation

#### Option 1: Claude Desktop Extension (Recommended)
1. Download the `monarch-money-enhanced-0.9.3.mcpb` file from this release
2. Double-click the `.mcpb` file to install in Claude Desktop
3. Configure your Monarch Money credentials in Claude Desktop settings
4. Enable the extension

#### Option 2: Manual Installation  
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
