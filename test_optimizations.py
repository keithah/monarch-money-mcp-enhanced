#!/usr/bin/env python3
"""Test script for MCP server optimizations."""

import asyncio
import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import server


class TestMCPOptimizations:
    """Test suite for MCP server optimizations."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        os.chdir(self.temp_dir)

        # Mock environment variables
        self.env_patcher = patch.dict(os.environ, {
            'MONARCH_EMAIL': 'test@example.com',
            'MONARCH_PASSWORD': 'test_password',
            'MONARCH_MFA_SECRET': 'test_mfa_secret'
        })
        self.env_patcher.start()

    def tearDown(self):
        """Clean up test environment."""
        self.env_patcher.stop()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    async def test_optimized_cache_configuration(self):
        """Test that cache TTL overrides are properly configured."""
        # Mock OptimizedMonarchMoney
        mock_client = AsyncMock()
        mock_client.get_accounts = AsyncMock(return_value=[])

        with patch('server.OptimizedMonarchMoney') as mock_optimized:
            mock_optimized.return_value = mock_client

            await server.initialize_client()

            # Verify OptimizedMonarchMoney was called with correct parameters
            mock_optimized.assert_called_once()
            call_args = mock_optimized.call_args

            assert call_args[1]['cache_enabled'] is True
            assert call_args[1]['deduplicate_requests'] is True

            # Check optimized TTL settings
            ttl_overrides = call_args[1]['cache_ttl_overrides']
            assert ttl_overrides['GetAccounts'] == 240  # 4 minutes
            assert ttl_overrides['GetTransactions'] == 120  # 2 minutes
            assert ttl_overrides['GetCategories'] == 604800  # 7 days
            assert ttl_overrides['GetMerchants'] == 14400  # 4 hours

    async def test_query_variants_tool_generation(self):
        """Test that get_accounts tool includes detail_level parameter."""
        # Mock the client
        server.mm_client = AsyncMock()

        tools = await server.list_tools()

        # Find get_accounts tool
        get_accounts_tool = None
        for tool in tools:
            if tool.name == "get_accounts":
                get_accounts_tool = tool
                break

        assert get_accounts_tool is not None, "get_accounts tool not found"

        # Check that detail_level parameter is present
        properties = get_accounts_tool.inputSchema.get("properties", {})
        assert "detail_level" in properties

        detail_level_prop = properties["detail_level"]
        assert detail_level_prop["type"] == "string"
        assert set(detail_level_prop["enum"]) == {"basic", "balance", "full"}

    async def test_query_variants_execution(self):
        """Test that query variants are properly executed."""
        # Mock the client with variant methods
        mock_client = AsyncMock()
        mock_client.get_accounts_basic = AsyncMock(return_value={"basic": "data"})
        mock_client.get_accounts_balance_only = AsyncMock(return_value={"balance": "data"})
        mock_client.get_accounts = AsyncMock(return_value={"full": "data"})

        server.mm_client = mock_client

        # Test basic variant
        result = await server.call_tool("get_accounts", {"detail_level": "basic"})
        mock_client.get_accounts_basic.assert_called_once()
        assert '"basic": "data"' in result[0].text

        # Test balance variant
        mock_client.reset_mock()
        result = await server.call_tool("get_accounts", {"detail_level": "balance"})
        mock_client.get_accounts_balance_only.assert_called_once()
        assert '"balance": "data"' in result[0].text

    async def test_performance_monitoring_tools(self):
        """Test that performance monitoring tools are available."""
        server.mm_client = AsyncMock()

        tools = await server.list_tools()
        tool_names = [tool.name for tool in tools]

        assert "get_cache_metrics" in tool_names
        assert "preload_cache" in tool_names

    async def test_cache_metrics_execution(self):
        """Test cache metrics tool execution."""
        mock_client = AsyncMock()
        mock_client.get_cache_metrics = MagicMock(return_value={
            "cache_hit_rate": 0.85,
            "api_calls_saved": 150,
            "total_requests": 200
        })

        server.mm_client = mock_client

        result = await server.call_tool("get_cache_metrics", {})
        mock_client.get_cache_metrics.assert_called_once()

        response_data = json.loads(result[0].text)
        assert response_data["cache_hit_rate"] == 0.85
        assert response_data["api_calls_saved"] == 150

    async def test_cache_preloading_execution(self):
        """Test cache preloading tool execution."""
        mock_client = AsyncMock()
        mock_client.preload_cache = AsyncMock(return_value=5)

        server.mm_client = mock_client

        result = await server.call_tool("preload_cache", {"context": "dashboard"})
        mock_client.preload_cache.assert_called_once_with("dashboard")

        assert "dashboard" in result[0].text
        assert "5" in result[0].text

    async def test_graceful_fallback_missing_optimizations(self):
        """Test graceful fallback when optimization methods are missing."""
        mock_client = AsyncMock()
        # Don't add optimization methods to simulate older version
        del mock_client.get_cache_metrics
        del mock_client.preload_cache

        server.mm_client = mock_client

        # Test cache metrics fallback
        result = await server.call_tool("get_cache_metrics", {})
        assert "not available" in result[0].text

        # Test preload cache fallback
        result = await server.call_tool("preload_cache", {"context": "dashboard"})
        assert "not available" in result[0].text

    def run_test(self, test_method):
        """Helper to run async test methods."""
        self.setUp()
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(test_method())
        finally:
            self.tearDown()


def run_tests():
    """Run all optimization tests."""
    test_suite = TestMCPOptimizations()

    tests = [
        test_suite.test_optimized_cache_configuration,
        test_suite.test_query_variants_tool_generation,
        test_suite.test_query_variants_execution,
        test_suite.test_performance_monitoring_tools,
        test_suite.test_cache_metrics_execution,
        test_suite.test_cache_preloading_execution,
        test_suite.test_graceful_fallback_missing_optimizations,
    ]

    passed = 0
    failed = 0

    for test in tests:
        test_name = test.__name__
        try:
            print(f"Running {test_name}...", end=" ")
            test_suite.run_test(test)
            print("✅ PASSED")
            passed += 1
        except Exception as e:
            print(f"❌ FAILED: {e}")
            failed += 1

    print(f"\nTest Results: {passed} passed, {failed} failed")
    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)