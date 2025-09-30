"""
Spark Tuning Package

A comprehensive package for monitoring, analyzing, and optimizing Apache Spark jobs.
Follows Apache Spark 3.5+ best practices and provides actionable insights for performance tuning.

Modules:
    - monitoring: Real-time metrics collection and performance profiling
    - optimization: Code and query optimization recommendations
    - analyzer: Bottleneck detection and data skew analysis
    - config: Optimal Spark configuration generation
"""

from spark_tuning.monitoring import MetricsCollector, PerformanceProfiler, ResourceTracker
from spark_tuning.optimization import CodeAnalyzer, QueryOptimizer, TransformationOptimizer
from spark_tuning.analyzer import BottleneckDetector, SkewDetector, MemoryAnalyzer
from spark_tuning.config import ConfigGenerator, OptimalConfigs

__version__ = "1.0.0"
__all__ = [
    # Monitoring
    "MetricsCollector",
    "PerformanceProfiler",
    "ResourceTracker",
    # Optimization
    "CodeAnalyzer",
    "QueryOptimizer",
    "TransformationOptimizer",
    # Analysis
    "BottleneckDetector",
    "SkewDetector",
    "MemoryAnalyzer",
    # Configuration
    "ConfigGenerator",
    "OptimalConfigs",
]
