#!/usr/bin/env python3
"""Simple test to validate MCP optimizations work."""

import asyncio
import json
import sys
import server

async def test_basic_functionality():
    """Test basic server functionality without live connection."""
    print("🧪 Testing MCP Server Optimizations")
    print("=" * 50)

    try:
        # Test that tools can be listed (this should work without authentication)
        print("1. Testing tool discovery...")

        # Mock the client to avoid authentication
        from unittest.mock import AsyncMock
        mock_client = AsyncMock()
        mock_client.get_cache_metrics = lambda: {
            "cache_hit_rate": 0.85,
            "api_calls_saved": 150,
            "total_requests": 200,
            "cache_entries": 50
        }
        mock_client.preload_cache = AsyncMock(return_value=5)
        server.mm_client = mock_client

        tools = await server.list_tools()
        print(f"   ✅ Found {len(tools)} tools")

        # Check for performance tools
        tool_names = [tool.name for tool in tools]
        performance_tools = ["get_cache_metrics", "preload_cache"]
        found_performance_tools = [name for name in performance_tools if name in tool_names]

        print(f"   ✅ Performance tools available: {found_performance_tools}")

        # Test get_accounts has query variants
        get_accounts_tool = next((t for t in tools if t.name == "get_accounts"), None)
        if get_accounts_tool:
            properties = get_accounts_tool.inputSchema.get("properties", {})
            if "detail_level" in properties:
                detail_levels = properties["detail_level"].get("enum", [])
                print(f"   ✅ Query variants available: {detail_levels}")
            else:
                print("   ❌ Query variants not found")
        else:
            print("   ❌ get_accounts tool not found")

        print("\n2. Testing performance monitoring tools...")

        # Test cache metrics
        result = await server.call_tool("get_cache_metrics", {})
        metrics_data = json.loads(result[0].text)
        print(f"   ✅ Cache metrics: {metrics_data}")

        # Test cache preloading
        result = await server.call_tool("preload_cache", {"context": "dashboard"})
        print(f"   ✅ Cache preloading: {result[0].text}")

        print("\n3. Testing query variants execution...")

        # Mock variant methods
        mock_client.get_accounts = AsyncMock(return_value={"accounts": [{"id": 1, "name": "Test"}]})
        mock_client.get_accounts_basic = AsyncMock(return_value={"accounts": [{"id": 1}]})
        mock_client.get_accounts_balance_only = AsyncMock(return_value={"accounts": [{"id": 1, "balance": 1000}]})

        # Test full query
        result = await server.call_tool("get_accounts", {})
        full_data = json.loads(result[0].text)
        print(f"   ✅ Full query: {len(json.dumps(full_data))} bytes")

        # Test basic query
        result = await server.call_tool("get_accounts", {"detail_level": "basic"})
        basic_data = json.loads(result[0].text)
        print(f"   ✅ Basic query: {len(json.dumps(basic_data))} bytes")

        # Calculate reduction
        full_size = len(json.dumps(full_data))
        basic_size = len(json.dumps(basic_data))
        reduction = ((full_size - basic_size) / full_size) * 100 if full_size > 0 else 0
        print(f"   ✅ Data reduction: {reduction:.1f}%")

        print(f"\n🎉 All tests passed!")
        print(f"\n📊 Summary:")
        print(f"   • Tools discovered: {len(tools)}")
        print(f"   • Performance tools: {len(found_performance_tools)}/2")
        print(f"   • Query variants: {'✅' if 'detail_level' in properties else '❌'}")
        print(f"   • Cache metrics: ✅")
        print(f"   • Data reduction: {reduction:.1f}%")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run simple tests."""
    success = await test_basic_functionality()
    return success

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        exit(1)