"""Comprehensive test suite for MCP server functionality."""

import asyncio
import json
import os
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import toml

import server


class TestMCPServer:
    """Test suite for MCP server core functionality."""

    @pytest.fixture
    def mock_env(self):
        """Mock environment variables for testing."""
        with patch.dict(os.environ, {
            'MONARCH_EMAIL': 'test@example.com',
            'MONARCH_PASSWORD': 'test_password',
            'MONARCH_MFA_SECRET': 'test_mfa_secret'
        }):
            yield

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            old_cwd = os.getcwd()
            os.chdir(tmp_dir)
            yield Path(tmp_dir)
            os.chdir(old_cwd)

    @pytest.fixture
    def mock_client(self):
        """Create mock MonarchMoney client."""
        mock = AsyncMock()
        mock.login = AsyncMock()
        mock.save_session = AsyncMock()
        mock.get_accounts = AsyncMock(return_value=[])
        mock.get_cache_metrics = MagicMock(return_value={
            "cache_hit_rate": 0.85,
            "api_calls_saved": 150
        })
        mock.preload_cache = AsyncMock(return_value=5)
        return mock

    @pytest.mark.asyncio
    async def test_server_initialization(self, mock_env, temp_dir, mock_client):
        """Test server initialization with proper configuration."""
        with patch('server.OptimizedMonarchMoney') as mock_optimized:
            mock_optimized.return_value = mock_client

            await server.initialize_client()

            # Verify OptimizedMonarchMoney was called with correct config
            mock_optimized.assert_called_once()
            call_args = mock_optimized.call_args

            assert call_args[1]['cache_enabled'] is True
            assert call_args[1]['deduplicate_requests'] is True

            # Check optimized cache configuration
            ttl_overrides = call_args[1]['cache_ttl_overrides']
            assert ttl_overrides['GetAccounts'] == 240
            assert ttl_overrides['GetTransactions'] == 120
            assert ttl_overrides['GetCategories'] == 604800

    @pytest.mark.asyncio
    async def test_tool_discovery(self, mock_client):
        """Test that tools are properly discovered and configured."""
        server.mm_client = mock_client

        tools = await server.list_tools()

        assert len(tools) > 0
        tool_names = [tool.name for tool in tools]

        # Check core MonarchMoney methods are available
        assert any('get_accounts' in name for name in tool_names)
        assert any('get_transactions' in name for name in tool_names)

        # Check performance monitoring tools
        assert 'get_cache_metrics' in tool_names
        assert 'preload_cache' in tool_names

    @pytest.mark.asyncio
    async def test_get_accounts_query_variants(self, mock_client):
        """Test get_accounts query variants functionality."""
        server.mm_client = mock_client

        # Add variant methods to mock
        mock_client.get_accounts_basic = AsyncMock(return_value={"basic": "data"})
        mock_client.get_accounts_balance_only = AsyncMock(return_value={"balance": "data"})

        tools = await server.list_tools()
        get_accounts_tool = next((t for t in tools if t.name == "get_accounts"), None)

        assert get_accounts_tool is not None

        # Check detail_level parameter exists
        properties = get_accounts_tool.inputSchema.get("properties", {})
        assert "detail_level" in properties

        detail_level_prop = properties["detail_level"]
        assert detail_level_prop["type"] == "string"
        assert set(detail_level_prop["enum"]) == {"basic", "balance", "full"}

    @pytest.mark.asyncio
    async def test_query_variant_execution(self, mock_client):
        """Test execution of query variants."""
        server.mm_client = mock_client

        # Setup variant methods
        mock_client.get_accounts_basic = AsyncMock(return_value={"type": "basic"})
        mock_client.get_accounts_balance_only = AsyncMock(return_value={"type": "balance"})
        mock_client.get_accounts = AsyncMock(return_value={"type": "full"})

        # Test basic variant
        result = await server.call_tool("get_accounts", {"detail_level": "basic"})
        mock_client.get_accounts_basic.assert_called_once()
        assert "basic" in result[0].text

        # Test balance variant
        mock_client.reset_mock()
        result = await server.call_tool("get_accounts", {"detail_level": "balance"})
        mock_client.get_accounts_balance_only.assert_called_once()
        assert "balance" in result[0].text

    @pytest.mark.asyncio
    async def test_performance_metrics_tool(self, mock_client):
        """Test cache metrics tool."""
        server.mm_client = mock_client

        result = await server.call_tool("get_cache_metrics", {})
        mock_client.get_cache_metrics.assert_called_once()

        response_data = json.loads(result[0].text)
        assert response_data["cache_hit_rate"] == 0.85
        assert response_data["api_calls_saved"] == 150

    @pytest.mark.asyncio
    async def test_cache_preloading_tool(self, mock_client):
        """Test cache preloading tool."""
        server.mm_client = mock_client

        result = await server.call_tool("preload_cache", {"context": "dashboard"})
        mock_client.preload_cache.assert_called_once_with("dashboard")

        assert "dashboard" in result[0].text
        assert "5" in result[0].text

    @pytest.mark.asyncio
    async def test_graceful_fallback(self, mock_client):
        """Test graceful fallback when optimization methods are missing."""
        # Remove optimization methods to simulate older client
        del mock_client.get_cache_metrics
        del mock_client.preload_cache

        server.mm_client = mock_client

        # Test cache metrics fallback
        result = await server.call_tool("get_cache_metrics", {})
        assert "not available" in result[0].text

        # Test preload cache fallback
        result = await server.call_tool("preload_cache", {"context": "dashboard"})
        assert "not available" in result[0].text

    @pytest.mark.asyncio
    async def test_error_handling(self, mock_client):
        """Test error handling for invalid tool calls."""
        # Create a proper mock that doesn't have the invalid method
        mock_without_method = AsyncMock()
        delattr(mock_without_method, 'invalid_method')
        server.mm_client = mock_without_method

        # Test non-existent method
        result = await server.call_tool("invalid_method", {})
        assert "not found" in result[0].text

        # Test with uninitialized client
        server.mm_client = None
        result = await server.call_tool("get_accounts", {})
        assert "not initialized" in result[0].text

    def test_version_consistency(self):
        """Test that versions are consistent across files."""
        import os
        pyproject_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "pyproject.toml")
        pyproject = toml.load(pyproject_path)
        project_version = pyproject["project"]["version"]

        # Check that server version matches
        # Note: This would be checked in the initialization options during runtime
        assert project_version == "0.11.0"

    @pytest.mark.asyncio
    async def test_date_parameter_conversion(self, mock_client):
        """Test that date parameters are properly converted."""
        server.mm_client = mock_client
        mock_client.get_transactions = AsyncMock(return_value=[])

        # Mock the method to capture the converted arguments
        original_call_tool = server.call_tool
        captured_args = {}

        async def capture_args(name, arguments):
            captured_args.update(arguments)
            return await original_call_tool(name, arguments)

        with patch.object(server, 'call_tool', side_effect=capture_args):
            await server.call_tool("get_transactions", {
                "start_date": "2024-01-01",
                "end_date": "2024-12-31"
            })

    @pytest.mark.asyncio
    async def test_session_management(self, mock_env, temp_dir, mock_client):
        """Test session file management and cleanup."""
        with patch('server.OptimizedMonarchMoney') as mock_optimized:
            mock_optimized.return_value = mock_client

            # Test with force login
            with patch.dict(os.environ, {'MONARCH_FORCE_LOGIN': 'true'}):
                await server.initialize_client()

            # Verify session methods were called
            mock_client.save_session.assert_called()


class TestMCPProtocolCompliance:
    """Test MCP protocol compliance."""

    def test_server_configuration(self):
        """Test that server is properly configured for MCP."""
        from mcp.server import Server

        assert isinstance(server.server, Server)
        assert server.server.name == "monarch-money-mcp-enhanced"

    @pytest.mark.asyncio
    async def test_tool_schema_validation(self):
        """Test that all tools have valid schemas."""
        # Mock client to avoid actual initialization
        server.mm_client = AsyncMock()

        tools = await server.list_tools()

        for tool in tools:
            # Each tool should have required fields
            assert hasattr(tool, 'name')
            assert hasattr(tool, 'description')
            assert hasattr(tool, 'inputSchema')

            # Schema should be valid JSON schema
            schema = tool.inputSchema
            assert isinstance(schema, dict)
            assert schema.get("type") == "object"
            assert "properties" in schema
            assert "required" in schema
            assert "additionalProperties" in schema

    @pytest.mark.asyncio
    async def test_tool_execution_response_format(self):
        """Test that tool responses follow MCP format."""
        from mcp.types import TextContent

        mock_client = AsyncMock()
        mock_client.get_accounts = AsyncMock(return_value={"accounts": []})
        server.mm_client = mock_client

        result = await server.call_tool("get_accounts", {})

        # Should return list of TextContent
        assert isinstance(result, list)
        assert len(result) > 0
        assert all(isinstance(item, TextContent) for item in result)
        assert all(item.type == "text" for item in result)