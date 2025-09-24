#!/usr/bin/env python3
"""
Live performance testing script for MCP server optimizations.

This script tests the MCP server with a real MonarchMoney account to validate:
1. Performance improvements from v0.11.0 optimizations
2. Query variants effectiveness
3. Cache performance metrics
4. Real-world functionality

Usage:
    1. Copy .env.example to .env and fill in your credentials
    2. Run: uv run python test_live_performance.py
"""

import asyncio
import json
import os
import time
from pathlib import Path
from typing import Dict, Any

import server


class LivePerformanceTest:
    """Test MCP server performance with live MonarchMoney account."""

    def __init__(self):
        self.results = {}
        self.start_time = None

    async def setup(self):
        """Initialize the MCP server with live credentials."""
        print("🚀 Setting up live MonarchMoney connection...")

        # Load environment variables from .env file
        env_file = Path(".env")
        if env_file.exists():
            print(f"📄 Loading environment from {env_file.absolute()}")
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line and '=' in line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        # Remove quotes if present
                        value = value.strip('"\'')
                        os.environ[key] = value
                        print(f"   Set {key}={'*' * len(value) if 'PASSWORD' in key or 'SECRET' in key else value}")
        else:
            print(f"❌ .env file not found at {env_file.absolute()}")
            print("Please create .env file with your MonarchMoney credentials")

        # Verify credentials are provided
        email = os.getenv("MONARCH_EMAIL")
        password = os.getenv("MONARCH_PASSWORD")

        if not email or not password:
            raise ValueError(
                "Please provide MONARCH_EMAIL and MONARCH_PASSWORD in .env file. "
                "Copy .env.example to .env and fill in your credentials."
            )

        print(f"📧 Using email: {email}")

        # Initialize the server
        await server.initialize_client()
        print("✅ Server initialized successfully")

    async def test_basic_functionality(self):
        """Test basic MCP functionality works."""
        print("\n📋 Testing basic functionality...")

        try:
            # Test tool discovery
            tools = await server.list_tools()
            print(f"✅ Found {len(tools)} tools")

            # Test basic account retrieval
            result = await server.call_tool("get_accounts", {})
            accounts_data = json.loads(result[0].text)
            print(f"✅ Retrieved {len(accounts_data)} accounts")

            self.results["basic_functionality"] = {
                "tools_count": len(tools),
                "accounts_count": len(accounts_data),
                "status": "success"
            }

        except Exception as e:
            print(f"❌ Basic functionality test failed: {e}")
            self.results["basic_functionality"] = {"status": "failed", "error": str(e)}

    async def test_query_variants_performance(self):
        """Test query variants performance improvements."""
        print("\n⚡ Testing query variants performance...")

        try:
            # Test full query (baseline)
            start_time = time.time()
            result_full = await server.call_tool("get_accounts", {"detail_level": "full"})
            full_time = time.time() - start_time
            full_size = len(result_full[0].text)

            # Test basic query (optimized)
            start_time = time.time()
            result_basic = await server.call_tool("get_accounts", {"detail_level": "basic"})
            basic_time = time.time() - start_time
            basic_size = len(result_basic[0].text)

            # Test balance query (optimized)
            start_time = time.time()
            result_balance = await server.call_tool("get_accounts", {"detail_level": "balance"})
            balance_time = time.time() - start_time
            balance_size = len(result_balance[0].text)

            # Calculate improvements
            basic_size_reduction = ((full_size - basic_size) / full_size) * 100
            balance_size_reduction = ((full_size - balance_size) / full_size) * 100
            basic_time_improvement = ((full_time - basic_time) / full_time) * 100
            balance_time_improvement = ((full_time - balance_time) / full_time) * 100

            print(f"📊 Query Performance Results:")
            print(f"   Full query:    {full_time:.3f}s, {full_size:,} bytes")
            print(f"   Basic query:   {basic_time:.3f}s, {basic_size:,} bytes ({basic_size_reduction:.1f}% reduction)")
            print(f"   Balance query: {balance_time:.3f}s, {balance_size:,} bytes ({balance_size_reduction:.1f}% reduction)")

            self.results["query_variants"] = {
                "full_time": full_time,
                "basic_time": basic_time,
                "balance_time": balance_time,
                "full_size": full_size,
                "basic_size": basic_size,
                "balance_size": balance_size,
                "basic_size_reduction": basic_size_reduction,
                "balance_size_reduction": balance_size_reduction,
                "basic_time_improvement": basic_time_improvement,
                "balance_time_improvement": balance_time_improvement,
                "status": "success"
            }

        except Exception as e:
            print(f"❌ Query variants test failed: {e}")
            self.results["query_variants"] = {"status": "failed", "error": str(e)}

    async def test_cache_performance(self):
        """Test cache performance metrics."""
        print("\n📈 Testing cache performance...")

        try:
            # Get initial cache metrics
            initial_metrics = await server.call_tool("get_cache_metrics", {})
            initial_data = json.loads(initial_metrics[0].text)
            print(f"📊 Initial cache metrics: {initial_data}")

            # Perform several operations to populate cache
            operations = [
                ("get_accounts", {}),
                ("get_transaction_categories", {}),
                ("get_accounts", {}),  # Should hit cache
                ("get_transaction_categories", {}),  # Should hit cache
            ]

            for op_name, args in operations:
                await server.call_tool(op_name, args)
                await asyncio.sleep(0.1)  # Small delay between operations

            # Get final cache metrics
            final_metrics = await server.call_tool("get_cache_metrics", {})
            final_data = json.loads(final_metrics[0].text)
            print(f"📊 Final cache metrics: {final_data}")

            # Calculate improvements
            if "cache_hit_rate" in final_data and "api_calls_saved" in final_data:
                hit_rate = final_data.get("cache_hit_rate", 0)
                calls_saved = final_data.get("api_calls_saved", 0)
                print(f"✅ Cache hit rate: {hit_rate:.1%}")
                print(f"✅ API calls saved: {calls_saved}")

            self.results["cache_performance"] = {
                "initial_metrics": initial_data,
                "final_metrics": final_data,
                "status": "success"
            }

        except Exception as e:
            print(f"❌ Cache performance test failed: {e}")
            self.results["cache_performance"] = {"status": "failed", "error": str(e)}

    async def test_preloading_effectiveness(self):
        """Test cache preloading effectiveness."""
        print("\n🚀 Testing cache preloading...")

        try:
            # Test different preloading contexts
            contexts = ["dashboard", "investments", "transactions"]
            preload_results = {}

            for context in contexts:
                start_time = time.time()
                result = await server.call_tool("preload_cache", {"context": context})
                preload_time = time.time() - start_time

                print(f"✅ Preloaded {context}: {result[0].text} ({preload_time:.3f}s)")
                preload_results[context] = {
                    "time": preload_time,
                    "result": result[0].text
                }

            self.results["preloading"] = {
                "contexts": preload_results,
                "status": "success"
            }

        except Exception as e:
            print(f"❌ Cache preloading test failed: {e}")
            self.results["preloading"] = {"status": "failed", "error": str(e)}

    async def test_real_world_workflow(self):
        """Test a realistic user workflow."""
        print("\n🏃 Testing real-world workflow simulation...")

        try:
            workflow_start = time.time()

            # Simulate typical user workflow
            workflow_operations = [
                ("get_accounts", {"detail_level": "balance"}),  # Dashboard view
                ("get_transaction_categories", {}),             # Setup for transaction filtering
                ("get_transactions", {"limit": 10}),           # Recent transactions
                ("get_budgets", {}),                           # Budget overview
                ("get_accounts", {"detail_level": "basic"}),   # Quick account check (cached)
            ]

            operation_times = []
            for i, (op_name, args) in enumerate(workflow_operations):
                op_start = time.time()
                result = await server.call_tool(op_name, args)
                op_time = time.time() - op_start
                operation_times.append(op_time)

                print(f"   Step {i+1}: {op_name} ({op_time:.3f}s)")

            total_workflow_time = time.time() - workflow_start
            average_op_time = sum(operation_times) / len(operation_times)

            print(f"✅ Workflow completed in {total_workflow_time:.3f}s")
            print(f"   Average operation time: {average_op_time:.3f}s")

            self.results["real_world_workflow"] = {
                "total_time": total_workflow_time,
                "operation_times": operation_times,
                "average_time": average_op_time,
                "status": "success"
            }

        except Exception as e:
            print(f"❌ Real-world workflow test failed: {e}")
            self.results["real_world_workflow"] = {"status": "failed", "error": str(e)}

    def generate_report(self):
        """Generate performance test report."""
        print("\n" + "="*60)
        print("📊 PERFORMANCE TEST REPORT")
        print("="*60)

        # Overall summary
        successful_tests = sum(1 for test in self.results.values() if test.get("status") == "success")
        total_tests = len(self.results)

        print(f"\n✅ Tests passed: {successful_tests}/{total_tests}")

        # Query variants summary
        if self.results.get("query_variants", {}).get("status") == "success":
            qv = self.results["query_variants"]
            print(f"\n🔍 Query Variants Performance:")
            print(f"   Basic query data reduction: {qv['basic_size_reduction']:.1f}%")
            print(f"   Balance query data reduction: {qv['balance_size_reduction']:.1f}%")
            print(f"   Time improvements: {qv['basic_time_improvement']:.1f}% (basic), {qv['balance_time_improvement']:.1f}% (balance)")

        # Cache performance summary
        if self.results.get("cache_performance", {}).get("status") == "success":
            cp = self.results["cache_performance"]
            final_metrics = cp["final_metrics"]
            if "cache_hit_rate" in final_metrics:
                print(f"\n📈 Cache Performance:")
                print(f"   Hit rate: {final_metrics['cache_hit_rate']:.1%}")
                print(f"   API calls saved: {final_metrics.get('api_calls_saved', 0)}")

        # Workflow performance
        if self.results.get("real_world_workflow", {}).get("status") == "success":
            wf = self.results["real_world_workflow"]
            print(f"\n🏃 Real-world Workflow:")
            print(f"   Total time: {wf['total_time']:.3f}s")
            print(f"   Average operation: {wf['average_time']:.3f}s")

        print("\n" + "="*60)

    async def run_all_tests(self):
        """Run complete performance test suite."""
        print("🧪 Starting live performance tests...")
        self.start_time = time.time()

        try:
            await self.setup()
            await self.test_basic_functionality()
            await self.test_query_variants_performance()
            await self.test_cache_performance()
            await self.test_preloading_effectiveness()
            await self.test_real_world_workflow()

        except Exception as e:
            print(f"❌ Test setup failed: {e}")
            return False

        total_time = time.time() - self.start_time
        print(f"\n⏱️  Total test time: {total_time:.3f}s")

        self.generate_report()

        # Save detailed results
        with open("performance_test_results.json", "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"\n💾 Detailed results saved to performance_test_results.json")

        return True


async def main():
    """Run live performance tests."""
    tester = LivePerformanceTest()
    success = await tester.run_all_tests()
    return success


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        exit(1)
    except Exception as e:
        print(f"❌ Tests failed: {e}")
        exit(1)