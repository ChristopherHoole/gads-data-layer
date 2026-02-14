"""
Benchmark dashboard query performance.
Tests key operations before and after optimization.
"""

import sys
import duckdb
from pathlib import Path
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.performance_monitor import PerformanceTimer, benchmark


def test_dashboard_queries(db_path: str = "warehouse.duckdb"):
    """
    Test common dashboard queries.

    Args:
        db_path: Path to DuckDB database
    """
    print("=" * 80)
    print("DASHBOARD QUERY BENCHMARKS")
    print("=" * 80)
    print()

    conn = duckdb.connect(db_path, read_only=True)
    customer_id = "9999999999"  # Synthetic test client

    # Test 1: Dashboard stats query (no indexes)
    print("1. Dashboard Stats Query")
    with PerformanceTimer("  Without indexes"):
        result = conn.execute(
            """
            SELECT 
                COUNT(DISTINCT campaign_id) as active_campaigns,
                SUM(cost_micros) / 1000000 as total_spend,
                SUM(conversions) as total_conversions,
                SUM(conversions_value) / NULLIF(SUM(cost_micros), 0) as avg_roas
            FROM analytics.campaign_daily
            WHERE customer_id = ?
              AND snapshot_date >= CURRENT_DATE - 30
        """,
            [customer_id],
        ).fetchone()
    print(f"     Result: {result[0]} campaigns, £{result[1]:.2f} spend")
    print()

    # Test 2: Recent changes query (benefits from idx_change_log_executed_at)
    print("2. Recent Changes Query")
    with PerformanceTimer("  Without indexes"):
        result = conn.execute(
            """
            SELECT 
                change_date,
                campaign_id,
                lever,
                old_value,
                new_value,
                change_pct,
                rule_id
            FROM analytics.change_log
            WHERE customer_id = ?
            ORDER BY executed_at DESC
            LIMIT 50
        """,
            [customer_id],
        ).fetchall()
    print(f"     Result: {len(result)} changes")
    print()

    # Test 3: Campaign performance query (benefits from idx_campaign_daily_customer_date)
    print("3. Campaign Performance Query")
    with PerformanceTimer("  Without indexes"):
        result = conn.execute(
            """
            SELECT 
                campaign_id,
                snapshot_date,
                cost_micros / 1000000 as spend,
                conversions,
                conversions_value
            FROM analytics.campaign_daily
            WHERE customer_id = ?
              AND snapshot_date >= CURRENT_DATE - 7
            ORDER BY snapshot_date DESC, campaign_id
        """,
            [customer_id],
        ).fetchall()
    print(f"     Result: {len(result)} rows")
    print()

    # Test 4: Cooldown check query (benefits from idx_change_log_cooldown)
    print("4. Cooldown Check Query")
    campaign_id = "3001"
    with PerformanceTimer("  Without indexes"):
        result = conn.execute(
            """
            SELECT COUNT(*) 
            FROM analytics.change_log
            WHERE customer_id = ?
              AND campaign_id = ?
              AND lever = 'budget'
              AND change_date >= CURRENT_DATE - 7
        """,
            [customer_id, campaign_id],
        ).fetchone()
    print(f"     Result: {result[0]} recent budget changes")
    print()

    # Test 5: Full table scan (shows impact of no indexes)
    print("5. Full Table Scan (All Changes)")
    with PerformanceTimer("  Without indexes"):
        result = conn.execute("""
            SELECT COUNT(*) 
            FROM analytics.change_log
        """).fetchone()
    print(f"     Result: {result[0]} total changes")
    print()

    conn.close()

    print("=" * 80)
    print("COMPLETE")
    print("=" * 80)


def test_cache_performance():
    """Test caching performance improvements."""
    print("\n" + "=" * 80)
    print("CACHE PERFORMANCE TEST")
    print("=" * 80)
    print()

    from act_dashboard.cache import cached, cache

    # Clear cache
    cache.clear()

    @cached(ttl=60, key_prefix="test")
    def expensive_operation(n: int) -> int:
        """Simulate expensive operation."""
        time.sleep(0.1)  # 100ms operation
        return n * 2

    # First call - cache miss
    print("1. First call (cache miss):")
    with PerformanceTimer("   Duration"):
        result = expensive_operation(42)
    print(f"   Result: {result}")
    print()

    # Second call - cache hit
    print("2. Second call (cache hit):")
    with PerformanceTimer("   Duration"):
        result = expensive_operation(42)
    print(f"   Result: {result}")
    print()

    # Calculate speedup
    print("Expected speedup: ~1000x (from 100ms to <1ms)")
    print()

    cache.clear()


def test_pagination_performance(db_path: str = "warehouse.duckdb"):
    """Test pagination query performance."""
    print("\n" + "=" * 80)
    print("PAGINATION PERFORMANCE TEST")
    print("=" * 80)
    print()

    conn = duckdb.connect(db_path, read_only=True)
    customer_id = "9999999999"

    # Test 1: Load all changes (no pagination)
    print("1. Load ALL changes (no pagination):")
    with PerformanceTimer("   Duration"):
        result = conn.execute(
            """
            SELECT * FROM analytics.change_log
            WHERE customer_id = ?
            ORDER BY executed_at DESC
        """,
            [customer_id],
        ).fetchall()
    print(f"   Rows: {len(result)}")
    print()

    # Test 2: Load first page only (50 rows)
    print("2. Load FIRST PAGE only (50 rows):")
    with PerformanceTimer("   Duration"):
        result = conn.execute(
            """
            SELECT * FROM analytics.change_log
            WHERE customer_id = ?
            ORDER BY executed_at DESC
            LIMIT 50
        """,
            [customer_id],
        ).fetchall()
    print(f"   Rows: {len(result)}")
    print()

    conn.close()


if __name__ == "__main__":
    db_path = sys.argv[1] if len(sys.argv) > 1 else "warehouse.duckdb"

    # Run all benchmarks
    test_dashboard_queries(db_path)
    test_cache_performance()
    test_pagination_performance(db_path)
