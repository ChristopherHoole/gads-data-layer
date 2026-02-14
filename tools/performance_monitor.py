"""
Performance monitoring and benchmarking tools.
"""

import time
import statistics
from typing import Callable, List, Dict, Any
from functools import wraps
import logging

logger = logging.getLogger(__name__)


class PerformanceTimer:
    """Context manager for timing code blocks."""

    def __init__(self, name: str, log_result: bool = True):
        """
        Initialize timer.

        Args:
            name: Name of the operation being timed
            log_result: Whether to log the result automatically
        """
        self.name = name
        self.log_result = log_result
        self.start_time = None
        self.end_time = None
        self.duration = None

    def __enter__(self):
        """Start timer."""
        self.start_time = time.time()
        return self

    def __exit__(self, *args):
        """Stop timer and optionally log."""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time

        if self.log_result:
            logger.info(f"{self.name}: {self.duration:.3f}s")


def timed(func: Callable) -> Callable:
    """
    Decorator to time function execution.

    Usage:
        @timed
        def slow_function():
            time.sleep(1)
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start

        logger.info(f"{func.__name__}: {duration:.3f}s")
        return result

    return wrapper


def benchmark(
    func: Callable, iterations: int = 10, warmup: int = 2
) -> Dict[str, float]:
    """
    Benchmark a function by running it multiple times.

    Args:
        func: Function to benchmark (should take no arguments)
        iterations: Number of times to run function
        warmup: Number of warmup runs (not counted in stats)

    Returns:
        Dict with timing statistics
    """
    print(f"Benchmarking {func.__name__}...")
    print(f"  Warmup: {warmup} runs")
    print(f"  Iterations: {iterations} runs")

    # Warmup runs
    for i in range(warmup):
        func()

    # Timed runs
    times = []
    for i in range(iterations):
        start = time.time()
        func()
        duration = time.time() - start
        times.append(duration)
        print(f"  Run {i+1}: {duration:.3f}s")

    # Calculate statistics
    stats = {
        "mean": statistics.mean(times),
        "median": statistics.median(times),
        "min": min(times),
        "max": max(times),
        "stdev": statistics.stdev(times) if len(times) > 1 else 0,
        "iterations": iterations,
    }

    print(f"\nResults:")
    print(f"  Mean:   {stats['mean']:.3f}s")
    print(f"  Median: {stats['median']:.3f}s")
    print(f"  Min:    {stats['min']:.3f}s")
    print(f"  Max:    {stats['max']:.3f}s")
    print(f"  StdDev: {stats['stdev']:.3f}s")

    return stats


def compare_performance(
    baseline_func: Callable,
    optimized_func: Callable,
    iterations: int = 10,
    warmup: int = 2,
) -> Dict[str, Any]:
    """
    Compare performance of two functions.

    Args:
        baseline_func: Original/baseline function
        optimized_func: Optimized function
        iterations: Number of iterations per function
        warmup: Number of warmup runs

    Returns:
        Dict with comparison results
    """
    print("=" * 80)
    print("PERFORMANCE COMPARISON")
    print("=" * 80)
    print()

    # Benchmark baseline
    print("BASELINE:")
    baseline_stats = benchmark(baseline_func, iterations, warmup)
    print()

    # Benchmark optimized
    print("OPTIMIZED:")
    optimized_stats = benchmark(optimized_func, iterations, warmup)
    print()

    # Calculate improvement
    improvement = (
        (baseline_stats["mean"] - optimized_stats["mean"]) / baseline_stats["mean"]
    ) * 100
    speedup = baseline_stats["mean"] / optimized_stats["mean"]

    print("=" * 80)
    print("COMPARISON:")
    print(f"  Baseline:  {baseline_stats['mean']:.3f}s")
    print(f"  Optimized: {optimized_stats['mean']:.3f}s")
    print(f"  Improvement: {improvement:+.1f}%")
    print(f"  Speedup: {speedup:.2f}x")
    print("=" * 80)

    return {
        "baseline": baseline_stats,
        "optimized": optimized_stats,
        "improvement_pct": improvement,
        "speedup": speedup,
    }


class QueryProfiler:
    """Profile database queries to identify slow queries."""

    def __init__(self):
        """Initialize profiler."""
        self.queries = []

    def profile_query(self, query: str, params: tuple = None):
        """
        Profile a single query execution.

        Returns:
            Context manager that times the query
        """

        class QueryTimer:
            def __init__(self, profiler, query, params):
                self.profiler = profiler
                self.query = query
                self.params = params
                self.start_time = None
                self.duration = None

            def __enter__(self):
                self.start_time = time.time()
                return self

            def __exit__(self, *args):
                self.duration = time.time() - self.start_time

                # Record query
                self.profiler.queries.append(
                    {
                        "query": self.query,
                        "params": self.params,
                        "duration": self.duration,
                        "timestamp": time.time(),
                    }
                )

                # Log slow queries (>100ms)
                if self.duration > 0.1:
                    logger.warning(
                        f"Slow query ({self.duration:.3f}s): {self.query[:100]}..."
                    )

        return QueryTimer(self, query, params)

    def get_slow_queries(self, threshold: float = 0.1) -> List[Dict]:
        """
        Get queries slower than threshold.

        Args:
            threshold: Minimum duration in seconds

        Returns:
            List of slow queries sorted by duration (slowest first)
        """
        slow = [q for q in self.queries if q["duration"] >= threshold]
        return sorted(slow, key=lambda q: q["duration"], reverse=True)

    def get_stats(self) -> Dict[str, Any]:
        """Get profiling statistics."""
        if not self.queries:
            return {
                "total_queries": 0,
                "total_time": 0,
                "mean_time": 0,
                "median_time": 0,
                "slowest_query": None,
            }

        durations = [q["duration"] for q in self.queries]

        return {
            "total_queries": len(self.queries),
            "total_time": sum(durations),
            "mean_time": statistics.mean(durations),
            "median_time": statistics.median(durations),
            "slowest_query": max(self.queries, key=lambda q: q["duration"]),
        }

    def print_summary(self):
        """Print profiling summary."""
        stats = self.get_stats()

        print("\n" + "=" * 80)
        print("QUERY PROFILING SUMMARY")
        print("=" * 80)
        print(f"Total Queries: {stats['total_queries']}")
        print(f"Total Time: {stats['total_time']:.3f}s")
        print(f"Mean Time: {stats['mean_time']:.3f}s")
        print(f"Median Time: {stats['median_time']:.3f}s")

        if stats["slowest_query"]:
            print(f"\nSlowest Query ({stats['slowest_query']['duration']:.3f}s):")
            print(f"  {stats['slowest_query']['query'][:100]}...")

        slow_queries = self.get_slow_queries(0.1)
        if slow_queries:
            print(f"\nSlow Queries (>100ms): {len(slow_queries)}")
            for i, q in enumerate(slow_queries[:5], 1):
                print(f"  {i}. {q['duration']:.3f}s: {q['query'][:80]}...")

        print("=" * 80 + "\n")
