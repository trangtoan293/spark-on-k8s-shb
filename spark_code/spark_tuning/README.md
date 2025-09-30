# Spark Tuning Package

Comprehensive toolkit for monitoring, analyzing, and optimizing Apache Spark applications.

## 📋 Overview

This package provides production-ready tools for:

- **Monitoring**: Real-time metrics collection and performance profiling
- **Optimization**: Query and code analysis with actionable recommendations
- **Analysis**: Bottleneck detection, data skew identification, memory analysis
- **Configuration**: Optimal Spark configurations for different environments

Built following Apache Spark 3.5+ best practices and battle-tested in production environments.

## 🚀 Quick Start

```python
from pyspark.sql import SparkSession
from spark_tuning import (
    MetricsCollector,
    PerformanceProfiler,
    QueryOptimizer,
    SkewDetector,
    ConfigGenerator
)

# Initialize Spark
spark = SparkSession.builder.appName("MyApp").getOrCreate()

# Monitor metrics
collector = MetricsCollector(spark)
collector.print_summary()

# Profile operations
profiler = PerformanceProfiler(spark)
result = profiler.profile_dataframe_action(df, "count", df.count)
profiler.print_profile_summary()

# Optimize queries
optimizer = QueryOptimizer(spark)
recommendations = optimizer.analyze_dataframe(df)
optimizer.print_recommendations(recommendations)

# Detect data skew
skew_detector = SkewDetector(spark)
has_skew, info = skew_detector.detect_skew(df)
if has_skew:
    skew_detector.print_skew_analysis(info)
```

## 📦 Modules

### 1. Monitoring Module

#### MetricsCollector
Collects comprehensive Spark metrics from executors, stages, and jobs.

```python
from spark_tuning.monitoring import MetricsCollector

collector = MetricsCollector(spark)

# Collect executor metrics
executor_metrics = collector.collect_executor_metrics()

# Collect stage metrics
stage_metrics = collector.collect_stage_metrics()

# Get complete summary
summary = collector.get_metrics_summary()

# Export to file
collector.export_to_json("metrics_report.json")
```

#### PerformanceProfiler
Profiles operations and identifies slow queries.

```python
from spark_tuning.monitoring import PerformanceProfiler

profiler = PerformanceProfiler(spark)

# Profile an action
result = profiler.profile_dataframe_action(
    df=my_dataframe,
    action_name="user_aggregation",
    action_func=lambda: my_dataframe.count()
)

# Use as decorator
@profiler.profile_function("transform_data")
def transform_data(df):
    return df.filter(...).groupBy(...)

# Get slowest operations
slow_ops = profiler.get_slowest_operations(top_n=5)
```

#### ResourceTracker
Monitors resource utilization and generates alerts.

```python
from spark_tuning.monitoring import ResourceTracker

tracker = ResourceTracker(spark, enable_alerts=True)

# Capture resource snapshot
snapshot = tracker.capture_snapshot()

# Get alerts
critical_alerts = tracker.get_active_alerts("CRITICAL")
for alert in critical_alerts:
    print(f"{alert.category}: {alert.message}")
    for rec in alert.recommendations:
        print(f"  - {rec}")

# Print summary
tracker.print_resource_summary()
```

### 2. Optimization Module

#### QueryOptimizer
Analyzes queries and provides optimization recommendations.

```python
from spark_tuning.optimization import QueryOptimizer

optimizer = QueryOptimizer(spark)

# Analyze a DataFrame
recommendations = optimizer.analyze_dataframe(df, "sales_data")

# Print recommendations
optimizer.print_recommendations(recommendations)

# Apply recommendations (example)
for rec in recommendations:
    if rec.severity == "HIGH":
        print(f"CRITICAL: {rec.issue}")
        print(f"Fix: {rec.recommendation}")
```

**Detects:**
- Cartesian products (cross joins)
- Inefficient join strategies
- Missing broadcast joins
- Filter pushdown issues
- Excessive shuffles
- Suboptimal partitioning

#### CodeAnalyzer
Static analysis for Spark code anti-patterns.

```python
from spark_tuning.optimization import CodeAnalyzer

analyzer = CodeAnalyzer()

# Analyze code
with open("my_spark_job.py") as f:
    code = f.read()
    
issues = analyzer.analyze_code(code, "my_spark_job.py")
for issue in issues:
    print(f"{issue.severity}: {issue.issue}")
    print(f"  -> {issue.recommendation}")
```

#### TransformationOptimizer
Optimizes DataFrame transformations.

```python
from spark_tuning.optimization import TransformationOptimizer

optimizer = TransformationOptimizer(spark)

# Get optimization tips
tip = optimizer.suggest_optimization("groupBy")
print(tip.optimized_approach)
```

### 3. Analyzer Module

#### BottleneckDetector
Identifies performance bottlenecks.

```python
from spark_tuning.analyzer import BottleneckDetector

detector = BottleneckDetector(spark)

# Detect bottlenecks
bottlenecks = detector.detect_bottlenecks()
detector.print_bottlenecks(bottlenecks)
```

**Detects:**
- Shuffle bottlenecks
- GC pressure (>10% execution time)
- Disk spill
- Task skew
- Serialization overhead

#### SkewDetector
Detects and analyzes data skew.

```python
from spark_tuning.analyzer import SkewDetector

detector = SkewDetector(spark)

# Check for skew
has_skew, skew_info = detector.detect_skew(df, sample_fraction=0.1)

if has_skew:
    detector.print_skew_analysis(skew_info)
    solutions = detector.suggest_skew_solutions(df, skew_column="user_id")
    for solution in solutions:
        print(solution)
```

#### MemoryAnalyzer
Analyzes memory configuration and usage.

```python
from spark_tuning.analyzer import MemoryAnalyzer

analyzer = MemoryAnalyzer(spark)

# Analyze current config
issues = analyzer.analyze_memory_config()
analyzer.print_memory_analysis(issues)

# Get tuning suggestions
configs = analyzer.suggest_memory_tuning(workload_type="caching")
for key, value in configs.items():
    print(f"{key} = {value}")
```

### 4. Configuration Module

#### ConfigGenerator
Generates optimal configurations.

```python
from spark_tuning.config import ConfigGenerator, ClusterResources, WorkloadProfile

generator = ConfigGenerator(spark)

# Define cluster resources
cluster = ClusterResources(
    num_executors=20,
    cores_per_executor=4,
    memory_per_executor_gb=8,
    total_cores=80,
    total_memory_gb=160
)

# Define workload
workload = WorkloadProfile(
    type="batch",
    data_size_gb=500,
    has_shuffles=True,
    has_caching=True,
    has_joins=True,
    expected_duration_minutes=60
)

# Generate configs
configs = generator.generate_configs(cluster, workload)
generator.print_configs(configs)

# For Kubernetes
k8s_configs = generator.generate_k8s_configs(namespace="spark")
```

#### OptimalConfigs
Pre-defined configurations for common scenarios.

```python
from spark_tuning.config import OptimalConfigs

# Small cluster
configs = OptimalConfigs.get_small_cluster_config()

# Large cluster
configs = OptimalConfigs.get_large_cluster_config()

# Streaming workload
configs = OptimalConfigs.get_streaming_config()

# Machine Learning
configs = OptimalConfigs.get_ml_config()

# Kubernetes
configs = OptimalConfigs.get_k8s_config()

# Apply configs
for key, value in configs.items():
    spark.conf.set(key, value)
```

## 🎯 Complete Workflow Example

```python
from pyspark.sql import SparkSession
from spark_tuning import *

# 1. Initialize with optimal configs
from spark_tuning.config import OptimalConfigs

spark = SparkSession.builder.appName("OptimizedApp")
configs = OptimalConfigs.get_k8s_config()
for key, value in configs.items():
    spark = spark.config(key, value)
spark = spark.getOrCreate()

# 2. Load data
df = spark.read.parquet("s3a://bucket/data/")

# 3. Monitor initial state
tracker = ResourceTracker(spark, enable_alerts=True)
snapshot = tracker.capture_snapshot()

# 4. Check for data skew
skew_detector = SkewDetector(spark)
has_skew, info = skew_detector.detect_skew(df)
if has_skew:
    print("⚠️ Data skew detected!")
    skew_detector.print_skew_analysis(info)

# 5. Optimize query
optimizer = QueryOptimizer(spark)
recommendations = optimizer.analyze_dataframe(df, "input_data")
optimizer.print_recommendations(recommendations)

# 6. Profile transformations
profiler = PerformanceProfiler(spark)

@profiler.profile_function("main_transformation")
def process_data(df):
    return (df
        .filter(col("status") == "active")
        .groupBy("user_id")
        .agg(sum("amount").alias("total"))
    )

result = process_data(df)

# 7. Execute with profiling
profiler.profile_dataframe_action(result, "write", lambda: result.write.parquet("output/"))

# 8. Analyze results
profiler.print_profile_summary()
collector = MetricsCollector(spark)
collector.print_summary()

# 9. Check for bottlenecks
detector = BottleneckDetector(spark)
bottlenecks = detector.detect_bottlenecks()
detector.print_bottlenecks(bottlenecks)
```

## 📊 Best Practices

### Memory Configuration
```python
# For caching-heavy workloads
configs = {
    "spark.memory.fraction": "0.6",
    "spark.memory.storageFraction": "0.6",  # 60% for storage
    "spark.sql.inMemoryColumnarStorage.compressed": "true"
}

# For shuffle-heavy workloads
configs = {
    "spark.memory.fraction": "0.6",
    "spark.memory.storageFraction": "0.3",  # 30% for storage
    "spark.shuffle.spill.compress": "true"
}
```

### Executor Sizing
```python
# Optimal: 4-6 cores, 4-8GB per executor
configs = {
    "spark.executor.cores": "5",
    "spark.executor.memory": "6g",
    "spark.executor.memoryOverhead": "1g"
}
```

### Adaptive Query Execution
```python
# Enable AQE for SQL workloads
configs = {
    "spark.sql.adaptive.enabled": "true",
    "spark.sql.adaptive.coalescePartitions.enabled": "true",
    "spark.sql.adaptive.skewJoin.enabled": "true"
}
```

## 🐛 Troubleshooting

### OOM Errors
```python
# Analyze memory
analyzer = MemoryAnalyzer(spark)
issues = analyzer.analyze_memory_config()

# Increase executor memory
spark.conf.set("spark.executor.memory", "8g")
spark.conf.set("spark.executor.memoryOverhead", "2g")

# Use MEMORY_AND_DISK for caching
df.persist(StorageLevel.MEMORY_AND_DISK)
```

### Slow Jobs
```python
# Profile to find bottlenecks
profiler = PerformanceProfiler(spark)
slow_ops = profiler.get_slowest_operations()

# Check for skew
skew_detector = SkewDetector(spark)
has_skew, info = skew_detector.detect_skew(df)

# Optimize queries
optimizer = QueryOptimizer(spark)
recommendations = optimizer.analyze_dataframe(df)
```

### High Shuffle Cost
```python
# Use broadcast joins
from pyspark.sql.functions import broadcast
result = large_df.join(broadcast(small_df), "key")

# Reduce shuffle partitions for small data
spark.conf.set("spark.sql.shuffle.partitions", "100")

# Enable AQE
spark.conf.set("spark.sql.adaptive.enabled", "true")
```

## 📈 Metrics to Monitor

### Critical Metrics
- **Memory utilization**: < 85%
- **GC time**: < 10% of execution time
- **Task failure rate**: < 5%
- **Shuffle read/write**: Monitor size and duration

### Performance Indicators
- **Stage duration**: Look for outliers
- **Task skew**: Max task > 3x median
- **Disk spill**: Should be zero for optimal performance

## 🔧 Integration with Existing Code

```python
# Add to existing Spark jobs
from spark_tuning import MetricsCollector, PerformanceProfiler

# Wrap existing code
def existing_job(spark):
    # Add monitoring
    collector = MetricsCollector(spark)
    profiler = PerformanceProfiler(spark)
    
    # Your existing code
    df = spark.read.parquet("input/")
    result = df.filter(...).groupBy(...).agg(...)
    
    # Profile the write
    profiler.profile_dataframe_action(
        result, 
        "write_output", 
        lambda: result.write.parquet("output/")
    )
    
    # Print summary
    collector.print_summary()
    profiler.print_profile_summary()
```

## 📝 License

MIT License - See LICENSE file for details.

## 🤝 Contributing

Contributions welcome! Please follow Apache Spark coding standards and include tests.

## 📚 References

- [Apache Spark Performance Tuning](https://spark.apache.org/docs/latest/tuning.html)
- [Spark Monitoring and Instrumentation](https://spark.apache.org/docs/latest/monitoring.html)
- [Spark SQL Performance Tuning](https://spark.apache.org/docs/latest/sql-performance-tuning.html)
