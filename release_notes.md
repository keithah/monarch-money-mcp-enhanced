## monarch-money-mcp-enhanced v0.3.4

🎉 **Major GraphQL Fixes Release** - This release synchronizes with `monarchmoney-enhanced` v0.3.4 which fixes critical GraphQL parsing errors.

### Changes
- Updated `monarchmoney-enhanced` from `0.3.3` to `0.3.4`
- MCP server version synchronized to `0.3.4`
- All MonarchMoney methods are automatically exposed as MCP tools
- Critical GraphQL fixes now available through MCP interface

### Major Fixes Available via MCP
- ✅ `get_net_worth_history()` - Fixed GraphQL variable structure (366 data points)
- ✅ `create_amount_rule()` - Fixed GraphQL mutation response handling  
- ✅ `create_categorization_rule()` - Fixed GraphQL mutation response handling
- ✅ `create_transaction_rule()` - Added proper response data fields
- ✅ `update_transaction_rule()` - Fixed error handling and return data
- ✅ `apply_rules_to_existing_transactions()` - Now works via fixed rule functions
- ✅ `get_investment_performance()` - Confirmed working with portfolio data

### Impact
**Overall improvement:** From 1/6 working functions to 6/6 working functions in the underlying library.

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
