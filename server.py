#!/usr/bin/env python3
"""Dynamic MonarchMoney MCP Server - Automatically exposes all MonarchMoney methods as MCP tools."""

import os
import sys

# Support for bundled dependencies if vendor directory exists
script_dir = os.path.dirname(os.path.abspath(__file__))
vendor_dir = os.path.join(script_dir, 'vendor')
if os.path.exists(vendor_dir):
    sys.path.insert(0, vendor_dir)

import asyncio
import json
import inspect
from typing import Any, Dict, Optional, List
from datetime import datetime, date
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.server.models import InitializationOptions
from mcp.types import ServerCapabilities
from mcp.types import Tool, TextContent
from monarchmoney import MonarchMoney, OptimizedMonarchMoney


def convert_dates_to_strings(obj: Any) -> Any:
    """Recursively convert all date/datetime objects to ISO format strings."""
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {key: convert_dates_to_strings(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_dates_to_strings(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_dates_to_strings(item) for item in obj)
    else:
        return obj


def get_method_schema(method) -> Dict[str, Any]:
    """Generate JSON schema for a method's parameters."""
    sig = inspect.signature(method)
    properties = {}
    required = []
    
    for name, param in sig.parameters.items():
        if name == 'self':
            continue
            
        prop = {"type": "string"}  # Default to string
        
        # Try to infer type from annotation
        if param.annotation != inspect.Parameter.empty:
            if param.annotation in [int, float]:
                prop["type"] = "number"
            elif param.annotation == bool:
                prop["type"] = "boolean"
            elif param.annotation == list:
                prop["type"] = "array"
            elif param.annotation == dict:
                prop["type"] = "object"
        
        # Handle date parameters and special optimizations
        if 'date' in name.lower():
            prop["description"] = f"{name.replace('_', ' ').title()} in YYYY-MM-DD format"
        elif name == "detail_level":
            prop["type"] = "string"
            prop["enum"] = ["basic", "balance", "full"]
            prop["description"] = "Account detail level: 'basic' (minimal fields), 'balance' (with balances), 'full' (all fields)"
        else:
            prop["description"] = f"{name.replace('_', ' ').title()}"
        
        properties[name] = prop
        
        # Required if no default value
        if param.default == inspect.Parameter.empty:
            required.append(name)
    
    return {
        "type": "object",
        "properties": properties,
        "required": required,
        "additionalProperties": False
    }


# Initialize the MCP server
server = Server("monarch-money-mcp-enhanced")
mm_client: Optional[OptimizedMonarchMoney] = None
session_file = Path.home() / ".monarchmoney_session"

# Load environment variables from .env file before changing directories
project_dir = Path(__file__).parent
env_file = project_dir / ".env"
if env_file.exists():
    print(f"📄 Loading environment from {env_file}", file=sys.stderr)
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and '=' in line and not line.startswith('#'):
                key, value = line.split('=', 1)
                # Remove quotes if present
                value = value.strip('"\'')
                os.environ[key] = value
                if 'PASSWORD' in key or 'SECRET' in key:
                    print(f"   Set {key}={'*' * len(value)}", file=sys.stderr)
                else:
                    print(f"   Set {key}={value}", file=sys.stderr)

# Change to a writable directory for session storage
import tempfile
temp_dir = Path(tempfile.gettempdir()) / "monarch-mcp"
temp_dir.mkdir(exist_ok=True)
os.chdir(temp_dir)


async def initialize_client():
    """Initialize the MonarchMoney client with authentication."""
    global mm_client

    # Environment variables should already be loaded from .env file at module import time

    email = os.getenv("MONARCH_EMAIL")
    password = os.getenv("MONARCH_PASSWORD")
    mfa_secret = os.getenv("MONARCH_MFA_SECRET")

    if not email or not password:
        raise ValueError("MONARCH_EMAIL and MONARCH_PASSWORD environment variables are required")
    
    # Clean up any corrupted session files before initialization
    force_login = os.getenv("MONARCH_FORCE_LOGIN", "").lower() in ("true", "1", "yes")
    
    # Always check for and clean up corrupted .mm session files
    try:
        mm_dir = Path(".mm")
        if mm_dir.exists():
            # Check if the session file is corrupted
            session_pickle = mm_dir / "mm_session.pickle"
            if session_pickle.exists():
                try:
                    # Try to read the file to see if it's corrupted
                    with open(session_pickle, 'r') as f:
                        content = f.read()
                        if not content.strip():  # Empty file
                            print("Found empty session file, cleaning up", file=sys.stderr)
                            raise ValueError("Empty session file")
                        json.loads(content)  # Try to parse as JSON
                except (json.JSONDecodeError, ValueError, UnicodeDecodeError) as e:
                    print(f"Found corrupted session file, cleaning up: {e}", file=sys.stderr)
                    import shutil
                    shutil.rmtree(mm_dir)
                    if session_file.exists():
                        session_file.unlink()
    except Exception as e:
        print(f"Error during session cleanup: {e}", file=sys.stderr)
    
    # Force clean if requested
    if force_login:
        try:
            if session_file.exists():
                session_file.unlink()
        except:
            pass
        try:
            import shutil
            mm_dir = Path(".mm")
            if mm_dir.exists():
                shutil.rmtree(mm_dir)
        except:
            pass
    
    # Use OptimizedMonarchMoney with enhanced performance optimizations
    mm_client = OptimizedMonarchMoney(
        cache_enabled=True,
        deduplicate_requests=True,
        cache_ttl_overrides={
            "GetAccounts": 240,  # Cache accounts for 4 minutes (optimized)
            "GetTransactions": 120,  # Cache transactions for 2 minutes (optimized)
            "GetCategories": 604800,  # Cache categories for 7 days (static data)
            "GetGoals": 600,  # Cache goals for 10 minutes
            "GetBudget": 300,  # Cache budget for 5 minutes
            "GetMerchants": 14400,  # Cache merchants for 4 hours (optimized)
            "GetAccountTypes": 604800,  # Cache account types for 7 days (static)
            "GetInstitutions": 86400,  # Cache institutions for 1 day (semi-static)
            "GetUserProfile": 86400,  # Cache user profile for 1 day
            "GetSettings": 86400,  # Cache settings for 1 day
            "GetRecurringTransactions": 3600,  # Cache recurring transactions for 1 hour
            "GetHoldings": 300,  # Cache holdings for 5 minutes
            "GetNetWorthHistory": 1800,  # Cache net worth history for 30 minutes
        }
    )
    
    # Try to load existing session first, but handle corrupted session files
    force_login = os.getenv("MONARCH_FORCE_LOGIN", "").lower() in ("true", "1", "yes")
    
    if session_file.exists() and not force_login:
        try:
            mm_client.load_session(str(session_file))
            # Test if session is still valid
            await mm_client.get_accounts()
            # Loaded existing session successfully
            return
        except Exception as e:
            # Existing session invalid or corrupted, clean up and login fresh
            print(f"Session load failed, cleaning up: {e}", file=sys.stderr)
            try:
                session_file.unlink()  # Remove corrupted session file
            except:
                pass
            # Remove .mm directory if it exists (contains cached session data)
            try:
                import shutil
                mm_dir = Path(".mm")
                if mm_dir.exists():
                    shutil.rmtree(mm_dir)
            except:
                pass
    
    # Login with credentials
    if mfa_secret:
        await mm_client.login(email, password, mfa_secret_key=mfa_secret)
    else:
        await mm_client.login(email, password)
    
    # Save session for future use
    mm_client.save_session(str(session_file))
    # Logged in and saved session


@server.list_tools()
async def list_tools() -> List[Tool]:
    """Dynamically generate tools from all public MonarchMoney methods."""
    if not mm_client:
        await initialize_client()
    
    tools = []
    
    # Get all public methods from MonarchMoney class
    for method_name in dir(MonarchMoney):
        if method_name.startswith('_'):
            continue
            
        method = getattr(MonarchMoney, method_name)
        if not callable(method):
            continue
            
        # Skip certain methods that aren't useful as tools
        skip_methods = {
            'load_session', 'save_session', 'delete_session', 'set_token',
            'set_timeout', 'multi_factor_authenticate', 'login', 'interactive_login',
            'get_cache_metrics', 'preload_cache'  # Performance methods exposed separately
        }
        if method_name in skip_methods:
            continue
        
        # Generate description
        docstring = inspect.getdoc(method) or f"Execute {method_name.replace('_', ' ')}"
        description = docstring.split('\n')[0]  # Use first line of docstring
        
        # Generate schema
        schema = get_method_schema(method)

        # Add detail_level parameter to get_accounts for query variants
        if method_name == "get_accounts":
            schema["properties"]["detail_level"] = {
                "type": "string",
                "enum": ["basic", "balance", "full"],
                "description": "Account detail level: 'basic' (minimal fields), 'balance' (with balances), 'full' (all fields). Defaults to 'full'."
            }

        tools.append(Tool(
            name=method_name,
            description=description,
            inputSchema=schema
        ))

    # Add performance monitoring tools
    tools.extend([
        Tool(
            name="get_cache_metrics",
            description="Get cache performance metrics including hit rates and API calls saved",
            inputSchema={"type": "object", "properties": {}, "required": [], "additionalProperties": False}
        ),
        Tool(
            name="preload_cache",
            description="Preload cache with commonly used data for improved performance",
            inputSchema={
                "type": "object",
                "properties": {
                    "context": {
                        "type": "string",
                        "enum": ["dashboard", "investments", "transactions", "all"],
                        "description": "Context for cache preloading: dashboard (accounts+recent), investments (holdings), transactions (categories+merchants), all (everything)"
                    }
                },
                "required": [],
                "additionalProperties": False
            }
        )
    ])

    return tools


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Dynamically execute any MonarchMoney method."""
    if not mm_client:
        return [TextContent(type="text", text="Error: MonarchMoney client not initialized")]
    
    try:
        # Handle performance monitoring methods
        if name == "get_cache_metrics":
            if hasattr(mm_client, 'get_cache_metrics'):
                result = mm_client.get_cache_metrics()
                return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
            else:
                return [TextContent(type="text", text="Cache metrics not available")]

        if name == "preload_cache":
            if hasattr(mm_client, 'preload_cache'):
                context = arguments.get("context", "dashboard")
                result = await mm_client.preload_cache(context)
                return [TextContent(type="text", text=f"Cache preloaded for context: {context}. Items loaded: {result}")]
            else:
                return [TextContent(type="text", text="Cache preloading not available")]

        # Check if method exists
        if not hasattr(mm_client, name):
            return [TextContent(type="text", text=f"Error: Method '{name}' not found")]

        method = getattr(mm_client, name)
        if not callable(method):
            return [TextContent(type="text", text=f"Error: '{name}' is not callable")]
        
        # Convert date strings to date objects for date parameters
        processed_args = {}
        for key, value in arguments.items():
            if isinstance(value, str) and 'date' in key.lower():
                try:
                    processed_args[key] = datetime.strptime(value, "%Y-%m-%d").date()
                except ValueError:
                    processed_args[key] = value
            else:
                processed_args[key] = value

        # Use optimized query variants for get_accounts when detail_level is specified
        if name == "get_accounts" and "detail_level" in processed_args:
            detail_level = processed_args.pop("detail_level")
            if detail_level == "basic":
                method = getattr(mm_client, "get_accounts_basic", method)
            elif detail_level == "balance":
                method = getattr(mm_client, "get_accounts_balance_only", method)

        # Execute the method
        if asyncio.iscoroutinefunction(method):
            result = await method(**processed_args)
        else:
            result = method(**processed_args)
        
        # Convert dates to strings for serialization
        result = convert_dates_to_strings(result)
        
        return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
    
    except Exception as e:
        return [TextContent(type="text", text=f"Error executing {name}: {str(e)}")]


async def main():
    """Main entry point for the server."""
    # Initialize the MonarchMoney client
    try:
        await initialize_client()
        # Initialized client with dynamic tools
    except Exception as e:
        # Failed to initialize MonarchMoney client - log to stderr for MCP debugging
        import sys
        print(f"Failed to initialize MonarchMoney client: {e}", file=sys.stderr)
        return
    
    # Run the MCP server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream, 
            write_stream,
            InitializationOptions(
                server_name="monarch-money-mcp-enhanced",
                server_version="0.11.0",
                capabilities=ServerCapabilities(
                    tools={}
                )
            )
        )


def run():
    """Entry point for the MCP server"""
    asyncio.run(main())

if __name__ == "__main__":
    run()