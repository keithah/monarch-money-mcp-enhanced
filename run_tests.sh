#!/bin/bash

# Test runner script for MCP performance validation
# This script helps you run all tests with proper error handling

set -e  # Exit on any error

echo "🧪 MCP Server Performance Test Suite"
echo "===================================="

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "Please copy .env.example to .env and add your MonarchMoney credentials:"
    echo "  cp .env.example .env"
    echo "  # Edit .env with your credentials"
    exit 1
fi

# Check if uv is available
if ! command -v /Users/keith/Library/Python/3.9/bin/uv &> /dev/null; then
    echo "❌ uv not found at expected path"
    echo "Please check your uv installation"
    exit 1
fi

echo "📦 Installing dependencies..."
/Users/keith/Library/Python/3.9/bin/uv sync --all-extras

echo ""
echo "🏥 Running health check..."
if /Users/keith/Library/Python/3.9/bin/uv run python monitor_production_metrics.py --mode health; then
    echo "✅ Health check passed!"
else
    echo "❌ Health check failed - check your credentials and connection"
    exit 1
fi

echo ""
echo "🚀 Running comprehensive performance tests..."
if /Users/keith/Library/Python/3.9/bin/uv run python test_live_performance.py; then
    echo "✅ Performance tests completed!"

    echo ""
    echo "📊 Test Results Summary:"
    if [ -f "performance_test_results.json" ]; then
        echo "Detailed results saved to: performance_test_results.json"

        # Extract key metrics if jq is available
        if command -v jq &> /dev/null; then
            echo ""
            echo "🎯 Key Performance Metrics:"

            # Query variants performance
            if jq -e '.query_variants.status == "success"' performance_test_results.json > /dev/null; then
                echo "  Query Variants:"
                jq -r '"    Basic query data reduction: " + (.query_variants.basic_size_reduction | tostring) + "%"' performance_test_results.json
                jq -r '"    Balance query data reduction: " + (.query_variants.balance_size_reduction | tostring) + "%"' performance_test_results.json
            fi

            # Cache performance
            if jq -e '.cache_performance.status == "success"' performance_test_results.json > /dev/null; then
                echo "  Cache Performance:"
                jq -r '"    Hit rate: " + (.cache_performance.final_metrics.cache_hit_rate * 100 | tostring) + "%"' performance_test_results.json 2>/dev/null || echo "    Hit rate: Data not available"
                jq -r '"    API calls saved: " + (.cache_performance.final_metrics.api_calls_saved | tostring)' performance_test_results.json 2>/dev/null || echo "    API calls saved: Data not available"
            fi

            # Workflow performance
            if jq -e '.real_world_workflow.status == "success"' performance_test_results.json > /dev/null; then
                echo "  Real-world Workflow:"
                jq -r '"    Total time: " + (.real_world_workflow.total_time | tostring) + "s"' performance_test_results.json
                jq -r '"    Average operation: " + (.real_world_workflow.average_time | tostring) + "s"' performance_test_results.json
            fi
        fi
    fi

    echo ""
    echo "🎉 All tests completed successfully!"
    echo "Review the detailed results in performance_test_results.json"

else
    echo "❌ Performance tests failed"
    exit 1
fi