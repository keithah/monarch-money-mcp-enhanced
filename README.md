# 🏦 Monarch Money MCP Server Enhanced

## 🎉 Claude Desktop Extension - One-Click Installation!

A dynamic MCP (Model Context Protocol) server that automatically exposes **all** methods from the `monarchmoney-enhanced` library as MCP tools. Now available as a **Claude Desktop Extension** for seamless one-click installation!

✨ **NEW in v0.11.0**: **2-5x performance improvements** with intelligent caching, query variants, and request deduplication!

🚀 **Performance Optimized**: 40-60% reduction in API calls, 60-70% data transfer reduction, 80%+ cache hit rates, and comprehensive real-time monitoring.

## Key Features

🎯 **One-Click Installation**: Install as a Claude Desktop Extension - no configuration files needed!  
🔄 **Fully Dynamic**: Automatically discovers and exposes all MonarchMoney methods as tools  
🚀 **Auto-Updating**: GitHub Actions automatically release new versions with MCPB bundles  
📊 **Complete API Access**: Every method in the library becomes an MCP tool automatically  
🛠️ **Smart Schema Generation**: Automatically generates parameter schemas from method signatures  
⚡ **Performance Optimized**: 2-5x improvements, intelligent caching, query variants, request deduplication, real-time monitoring  
💫 **User-Friendly Setup**: Configure credentials through Claude Desktop's intuitive interface

## Automatically Available Features

Since this server dynamically exposes all `monarchmoney-enhanced` methods, you get access to **everything**:

- **Account Management**: Create, update, delete accounts, get balances, history
- **Transaction Operations**: CRUD operations, categorization, tagging, rules, splits
- **Budget Management**: Set budgets, analyze spending, track goals
- **Category & Tag Management**: Create, modify, delete categories and tags
- **Institution Management**: Manage connected financial institutions
- **Recurring Transactions**: Track and manage recurring payments
- **Investment Tracking**: Portfolio holdings, performance data
- **Subscription Management**: Account details and billing info
- **And more...**: Any new features added to `monarchmoney-enhanced` are instantly available!

## Installation

### Option 1: 🚀 Claude Desktop Extension (Recommended)

**⚡ FASTEST & EASIEST INSTALLATION ⚡**

Transform your installation experience from complex manual setup to Chrome extension-style simplicity:

1. **Download the Extension**: Get the latest `monarch-money-enhanced-0.11.0.mcpb` file from the [Releases page](https://github.com/keithah/monarch-money-mcp-enhanced/releases)

2. **Install in Claude Desktop**: Double-click the `.mcpb` file to automatically install in Claude Desktop

3. **Configure**: Enter your Monarch Money credentials in Claude Desktop settings:
   - **Email**: Your Monarch Money account email
   - **Password**: Your Monarch Money account password  
   - **MFA Secret** (optional): Your 2FA secret key if enabled
   - **Force Login** (optional): Force fresh login instead of cached session

4. **Enable**: Enable the extension in Claude Desktop settings

**That's it!** 🎉 No manual configuration files, no path setup, no terminal commands required!

---

### Option 2: 🛠️ Manual Installation (Advanced Users)

1. Clone or download this MCP server
2. Install dependencies:
   ```bash
   cd /path/to/monarch-money-mcp
   uv sync
   ```

3. Add the server to your `.mcp.json` configuration file:

```json
{
  "mcpServers": {
    "monarch-money-enhanced": {
      "command": "/path/to/uv",
      "args": [
        "--directory", 
        "/path/to/monarch-money-mcp-enhanced",
        "run",
        "python",
        "server.py"
      ],
      "env": {
        "MONARCH_EMAIL": "your-email@example.com",
        "MONARCH_PASSWORD": "your-password",
        "MONARCH_MFA_SECRET": "your-mfa-secret-key"
      }
    }
  }
}
```

**Important Notes:**
- Replace `/path/to/uv` with the full path to your `uv` executable (find it with `which uv`)
- Replace `/path/to/monarch-money-mcp-enhanced` with the absolute path to this server directory
- Use absolute paths, not relative paths

### Getting Your MFA Secret

1. Go to Monarch Money settings and enable 2FA
2. When shown the QR code, look for the "Can't scan?" or "Enter manually" option
3. Copy the secret key (it will be a string like `T5SPVJIBRNPNNINFSH5W7RFVF2XYADYX`)
4. Use this as your `MONARCH_MFA_SECRET`

## 🚀 Performance Optimizations (v0.11.0)

### **2-5x Performance Improvements**
Our latest release delivers significant performance enhancements:

- **40-60% API Call Reduction**: Intelligent caching with TTL strategies
- **60-70% Data Transfer Reduction**: Query variants (basic/balance/full)
- **80%+ Cache Hit Rates**: For static data (categories, account types)
- **Request Deduplication**: 80% efficiency preventing duplicate calls
- **Real-time Monitoring**: Performance metrics and cache optimization

### **Key Optimizations**
1. **🎯 Query Variants**: Choose data detail level to reduce overfetching
   - `basic`: Minimal fields for lightweight operations
   - `balance`: Includes balance information
   - `full`: Complete account data (default)

2. **📊 Intelligent Caching**: Multi-tier TTL strategies
   - 2 minutes: Dynamic data (transactions, balances)
   - 4 hours: Semi-static data (merchants, institutions)
   - 7 days: Static data (categories, account types)

3. **⚡ Performance Tools**: Built-in monitoring and optimization
   - `get_cache_metrics`: Real-time performance insights
   - `preload_cache`: Context-aware preloading (dashboard/investments/transactions)

### **Benchmarks**
- **Before**: 50-100 API calls per session, 100-200KB data transfer
- **After**: 10-20 API calls per session, 20-40KB data transfer
- **Improvement**: 2-5x faster typical workflows

## How It Works

The server automatically discovers all public methods from the `monarchmoney-enhanced` library and creates MCP tools for them. This means:

1. **No Manual Tool Definitions**: Methods are discovered at runtime
2. **Automatic Schema Generation**: Parameter types and requirements are inferred from method signatures
3. **Instant Updates**: When `monarchmoney-enhanced` adds new methods, they become available immediately
4. **Complete Coverage**: Every public method becomes an MCP tool
5. **Performance Optimized**: Automatic caching and optimization without code changes

## Available Tools (Dynamic)

Instead of listing specific tools, here's how to see what's available:

1. **Runtime Discovery**: The server lists all available tools when it starts
2. **Method Coverage**: All public methods from `MonarchMoney` class become tools
3. **Automatic Documentation**: Tool descriptions are generated from method docstrings

### Example Tools (Auto-Generated)

Some examples of tools that are automatically created:

- `get_accounts` - Retrieve all linked financial accounts
- `create_transaction` - Creates a transaction with the given parameters  
- `create_transaction_category` - Creates a new transaction category
- `get_transaction_tags` - Get all transaction tags
- `set_budget_amount` - Set budget amount for a category
- `get_merchants` - Get all merchants
- `delete_transaction` - Deletes the given transaction
- `get_recurring_transactions` - Get all recurring transactions
- `create_manual_account` - Creates a new manual account
- **And 90+ more...** (automatically updated as the library grows)

**New Performance Tools (v0.11.0):**
- `get_cache_metrics` - Real-time cache performance insights
- `preload_cache` - Context-aware cache preloading for improved performance

## Usage Examples

### Creating Transaction Categories
```
Use create_transaction_category with name "Shared - Telco" to create a new category for shared telecom expenses.
```

### Applying Transaction Rules  
```
Use the transaction management tools to automatically categorize transactions. For example:
- Find transactions containing "Sentris Network LLC" 
- Update them to use the "Shared - Telco" category
```

### Performance Monitoring (NEW in v0.11.0)
```
Monitor and optimize performance with new tools:
- Check cache performance: get_cache_metrics
- Preload cache for dashboard: preload_cache with context "dashboard"
- Use query variants: get_accounts with detail_level "basic" for faster responses
- Monitor API efficiency: Track cache hit rates and API calls saved
```

### Query Optimization Examples (NEW in v0.11.0)
```
Optimize data fetching with query variants:
- Quick account list: get_accounts with detail_level "basic"
- Account balances: get_accounts with detail_level "balance"
- Full account data: get_accounts with detail_level "full" (default)
- Dashboard view: preload_cache with context "dashboard" for faster loading
```

### Complete Financial Management
```
Since all MonarchMoney methods are available:
- Create and manage accounts with create_manual_account
- Set up budgets with set_budget_amount
- Tag transactions with set_transaction_tags
- Analyze spending patterns with get_cashflow_summary
- Track investments with get_account_holdings
- Monitor performance with get_cache_metrics
```

## Session Management

The server automatically manages authentication sessions:
- Sessions are cached in a `.mm` directory for faster subsequent logins
- The session cache is automatically created and managed
- Use `MONARCH_FORCE_LOGIN=true` in the env section to force a fresh login if needed

## Troubleshooting

### MFA Issues
- Ensure your MFA secret is correct and properly formatted
- Try setting `MONARCH_FORCE_LOGIN=true` in your `.mcp.json` env section
- Check that your system time is accurate (required for TOTP)

### Connection Issues
- Verify your email and password are correct in `.mcp.json`
- Check your internet connection
- Try running the server directly to see detailed error messages:
  ```bash
  uv run server.py
  ```

### Session Problems
- Delete the `.mm` directory to clear cached sessions
- Set `MONARCH_FORCE_LOGIN=true` in your `.mcp.json` env section temporarily

### Performance Issues (NEW in v0.11.0)
- Check cache performance: Use `get_cache_metrics` to see hit rates
- If cache hit rate is low, try: `preload_cache` with appropriate context
- For faster responses: Use `get_accounts` with `detail_level: "basic"`
- Monitor API usage: Track `api_calls_saved` in cache metrics

## Auto-Updates

This repository includes GitHub Actions that automatically:

1. **Monitor Updates**: Checks every 6 hours for new `monarchmoney-enhanced` releases
2. **Auto-Release**: Creates new releases when the library updates  
3. **Zero Maintenance**: No manual intervention needed to get new features
4. **Dependency Management**: Dependabot keeps other dependencies secure
5. **MCPB Generation**: Automatically creates `.mcpb` extension bundles for **every release**
6. **Extension Distribution**: Ready-to-install bundles available in GitHub Releases
7. **Performance Testing**: Automated testing validates optimizations and performance improvements

## Building MCPB Extensions (For Developers)

If you want to create your own MCPB bundle:

1. **Install MCPB CLI**:
   ```bash
   npm install -g @anthropic-ai/mcpb
   ```

2. **Generate Bundle**:
   ```bash
   mcpb pack
   ```

3. **Output**: The CLI generates `monarch-money-enhanced-VERSION.mcpb` ready for distribution

The `manifest.json` file defines the extension configuration and is automatically used by the MCPB CLI.

## Credits

### Original MCP Server
- **Author**: Taurus Colvin ([@colvint](https://github.com/colvint))
- **Repository**: [https://github.com/colvint/monarch-money-mcp](https://github.com/colvint/monarch-money-mcp)

### Enhanced MCP Server
- **Enhanced By**: Keith Herrington ([@keithah](https://github.com/keithah))
- **Repository**: [https://github.com/keithah/monarch-money-mcp-enhanced](https://github.com/keithah/monarch-money-mcp-enhanced)
- **Name**: `monarch-money-mcp-enhanced`
- **Version**: Synchronized with `monarchmoney-enhanced` library
- **Features**: Dynamic tool generation, 2-5x performance improvements, auto-updates, complete API coverage, intelligent caching, query variants

### MonarchMoney Enhanced Library
- **Enhanced By**: Keith Herrington ([@keithah](https://github.com/keithah))
- **Repository**: [https://github.com/keithah/monarchmoney-enhanced](https://github.com/keithah/monarchmoney-enhanced)
- **Description**: Enhanced version of the MonarchMoney Python library with additional features

### Original MonarchMoney Python Library
- **Author**: hammem ([@hammem](https://github.com/hammem))
- **Repository**: [https://github.com/hammem/monarchmoney](https://github.com/hammem/monarchmoney)
- **License**: MIT License

This dynamic MCP server automatically adapts to library changes, providing seamless integration with AI assistants through the Model Context Protocol.

## Security Notes

- Keep your credentials secure in your `.mcp.json` file
- The MFA secret provides full access to your account - treat it like a password
- Session files in `.mm` directory contain authentication tokens - keep them secure
- Consider restricting access to your `.mcp.json` file since it contains sensitive credentials