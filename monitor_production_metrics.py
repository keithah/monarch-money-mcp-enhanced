#!/usr/bin/env python3
"""
Production monitoring script for MCP server performance.

This script can be used to monitor performance metrics in a production
MCP environment. It provides real-time monitoring and alerting capabilities.

Usage:
    uv run python monitor_production_metrics.py [options]
"""

import asyncio
import json
import time
import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional

import server


class ProductionMonitor:
    """Monitor MCP server performance in production."""

    def __init__(self, interval: int = 60, alert_threshold: float = 0.5):
        self.interval = interval  # Monitoring interval in seconds
        self.alert_threshold = alert_threshold  # Cache hit rate threshold for alerts
        self.metrics_history: List[Dict] = []
        self.running = False

    async def initialize(self):
        """Initialize the monitoring system."""
        print("🔍 Initializing production monitor...")

        # Environment variables should already be loaded by server module
        # Initialize the server if not already done
        if server.mm_client is None:
            await server.initialize_client()

        print("✅ Monitor initialized")

    async def collect_metrics(self) -> Optional[Dict]:
        """Collect current performance metrics."""
        try:
            # Get cache metrics
            metrics_result = await server.call_tool("get_cache_metrics", {})
            metrics_data = json.loads(metrics_result[0].text)

            # Add timestamp
            metrics_data["timestamp"] = datetime.now(timezone.utc).isoformat()
            metrics_data["unix_timestamp"] = time.time()

            return metrics_data

        except Exception as e:
            print(f"❌ Failed to collect metrics: {e}")
            return None

    def analyze_metrics(self, metrics: Dict) -> Dict:
        """Analyze metrics and generate insights."""
        analysis = {
            "timestamp": metrics["timestamp"],
            "alerts": [],
            "insights": [],
            "status": "healthy"
        }

        # Check cache hit rate
        hit_rate_raw = metrics.get("cache_hit_rate", 0)
        try:
            hit_rate = float(hit_rate_raw) if hit_rate_raw is not None else 0.0
        except (ValueError, TypeError):
            hit_rate = 0.0

        if hit_rate < self.alert_threshold:
            analysis["alerts"].append({
                "type": "low_cache_hit_rate",
                "message": f"Cache hit rate is {hit_rate:.1%}, below threshold of {self.alert_threshold:.1%}",
                "severity": "warning"
            })
            analysis["status"] = "warning"

        # Check for significant changes in metrics
        if len(self.metrics_history) > 0:
            prev_metrics = self.metrics_history[-1]

            # Check for drops in performance
            prev_hit_rate_raw = prev_metrics.get("cache_hit_rate", 0)
            try:
                prev_hit_rate = float(prev_hit_rate_raw) if prev_hit_rate_raw is not None else 0.0
            except (ValueError, TypeError):
                prev_hit_rate = 0.0

            if hit_rate < prev_hit_rate - 0.1:  # 10% drop
                analysis["alerts"].append({
                    "type": "performance_degradation",
                    "message": f"Cache hit rate dropped from {prev_hit_rate:.1%} to {hit_rate:.1%}",
                    "severity": "warning"
                })

        # Generate insights
        if hit_rate > 0.8:
            analysis["insights"].append("Excellent cache performance - API calls are being efficiently cached")
        elif hit_rate > 0.6:
            analysis["insights"].append("Good cache performance - consider optimizing frequently accessed data")
        else:
            analysis["insights"].append("Cache performance needs attention - review caching strategies")

        calls_saved = metrics.get("api_calls_saved", 0)
        if calls_saved > 100:
            analysis["insights"].append(f"Cache is saving significant API calls: {calls_saved}")

        return analysis

    def log_metrics(self, metrics: Dict, analysis: Dict):
        """Log metrics and analysis."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        print(f"\n📊 [{timestamp}] Performance Metrics:")

        # Handle cache hit rate safely
        hit_rate_raw = metrics.get('cache_hit_rate', 0)
        try:
            hit_rate = float(hit_rate_raw) if hit_rate_raw is not None else 0.0
            print(f"   Cache Hit Rate: {hit_rate:.1%}")
        except (ValueError, TypeError):
            print(f"   Cache Hit Rate: {hit_rate_raw} (invalid format)")

        print(f"   API Calls Saved: {metrics.get('api_calls_saved', 0)}")
        print(f"   Total Requests: {metrics.get('total_requests', 0)}")
        print(f"   Memory Usage: {metrics.get('cache_memory_usage', 'N/A')}")

        # Log alerts
        if analysis["alerts"]:
            print(f"   🚨 Alerts:")
            for alert in analysis["alerts"]:
                print(f"      {alert['severity'].upper()}: {alert['message']}")

        # Log insights
        if analysis["insights"]:
            print(f"   💡 Insights:")
            for insight in analysis["insights"]:
                print(f"      {insight}")

    def save_metrics_history(self):
        """Save metrics history to file."""
        history_file = Path("metrics_history.json")

        try:
            with open(history_file, "w") as f:
                json.dump(self.metrics_history, f, indent=2)
        except Exception as e:
            print(f"❌ Failed to save metrics history: {e}")

    async def generate_daily_report(self):
        """Generate daily performance report."""
        if not self.metrics_history:
            return

        print("\n" + "="*60)
        print("📈 DAILY PERFORMANCE REPORT")
        print("="*60)

        # Calculate daily averages
        today_metrics = [
            m for m in self.metrics_history
            if datetime.fromisoformat(m["timestamp"]).date() == datetime.now(timezone.utc).date()
        ]

        if not today_metrics:
            print("No metrics collected today")
            return

        avg_hit_rate = sum(m.get("cache_hit_rate", 0) for m in today_metrics) / len(today_metrics)
        total_calls_saved = sum(m.get("api_calls_saved", 0) for m in today_metrics)
        total_requests = sum(m.get("total_requests", 0) for m in today_metrics)

        print(f"📊 Daily Averages:")
        print(f"   Average Cache Hit Rate: {avg_hit_rate:.1%}")
        print(f"   Total API Calls Saved: {total_calls_saved}")
        print(f"   Total Requests: {total_requests}")

        # Performance trends
        if len(today_metrics) > 1:
            first_hit_rate = today_metrics[0].get("cache_hit_rate", 0)
            last_hit_rate = today_metrics[-1].get("cache_hit_rate", 0)
            trend = last_hit_rate - first_hit_rate

            if abs(trend) > 0.05:  # 5% change
                direction = "improved" if trend > 0 else "declined"
                print(f"   Performance Trend: {direction} by {abs(trend):.1%}")

        print("="*60)

    async def monitor_loop(self):
        """Main monitoring loop."""
        self.running = True
        last_daily_report = datetime.now(timezone.utc).date()

        print(f"🔍 Starting production monitoring (interval: {self.interval}s)")
        print(f"   Alert threshold: {self.alert_threshold:.1%} cache hit rate")

        while self.running:
            try:
                # Collect metrics
                metrics = await self.collect_metrics()
                if metrics:
                    # Analyze metrics
                    analysis = self.analyze_metrics(metrics)

                    # Store metrics
                    self.metrics_history.append(metrics)

                    # Keep only last 24 hours of metrics
                    cutoff_time = time.time() - (24 * 60 * 60)
                    self.metrics_history = [
                        m for m in self.metrics_history
                        if m.get("unix_timestamp", 0) > cutoff_time
                    ]

                    # Log current metrics
                    self.log_metrics(metrics, analysis)

                    # Save metrics history
                    self.save_metrics_history()

                    # Generate daily report if new day
                    current_date = datetime.now(timezone.utc).date()
                    if current_date > last_daily_report:
                        await self.generate_daily_report()
                        last_daily_report = current_date

                # Wait for next interval
                await asyncio.sleep(self.interval)

            except KeyboardInterrupt:
                print("\n🛑 Monitoring stopped by user")
                break
            except Exception as e:
                print(f"❌ Monitoring error: {e}")
                await asyncio.sleep(self.interval)

        self.running = False

    async def run_monitoring(self):
        """Run the production monitoring system."""
        await self.initialize()
        await self.monitor_loop()

    def stop_monitoring(self):
        """Stop the monitoring system."""
        self.running = False


async def run_health_check():
    """Run a one-time health check."""
    print("🏥 Running MCP server health check...")

    try:
        # Environment variables should already be loaded by server module
        # Just initialize the server
        await server.initialize_client()

        # Collect current metrics
        monitor = ProductionMonitor()
        metrics = await monitor.collect_metrics()

        if metrics:
            analysis = monitor.analyze_metrics(metrics)
            monitor.log_metrics(metrics, analysis)

            # Overall health status
            status = analysis["status"]
            print(f"\n🎯 Overall Health: {status.upper()}")

            if analysis["alerts"]:
                print("⚠️  Issues detected - review alerts above")
                return False
            else:
                print("✅ System is healthy")
                return True
        else:
            print("❌ Failed to collect metrics")
            return False

    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="MCP Server Production Monitor")
    parser.add_argument("--mode", choices=["monitor", "health"], default="health",
                      help="Mode: 'monitor' for continuous monitoring, 'health' for one-time check")
    parser.add_argument("--interval", type=int, default=60,
                      help="Monitoring interval in seconds (default: 60)")
    parser.add_argument("--threshold", type=float, default=0.5,
                      help="Cache hit rate alert threshold (default: 0.5)")

    args = parser.parse_args()

    try:
        if args.mode == "monitor":
            monitor = ProductionMonitor(interval=args.interval, alert_threshold=args.threshold)
            asyncio.run(monitor.run_monitoring())
        else:
            success = asyncio.run(run_health_check())
            exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
        exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()