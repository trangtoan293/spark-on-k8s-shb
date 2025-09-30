# Spark Performance Tuning Guide

## 📖 Overview

This repository includes a comprehensive `spark_tuning` package for monitoring, analyzing, and optimizing Apache Spark jobs running on Kubernetes.

## 🎯 Package Structure

```
spark_code/spark_tuning/
├── __init__.py                    # Main package exports
├── README.md                      # Detailed documentation
├── monitoring/                    # Real-time monitoring
│   ├── metrics_collector.py      # Collect Spark metrics
│   ├── performance_profiler.py   # Profile operations
│   └── resource_tracker.py       # Track resource usage & alerts
├── optimization/                  # Query & code optimization
│   ├── query_optimizer.py        # Analyze queries
│   ├── code_analyzer.py          # Static code analysis
│   └── transformation_optimizer.py
├── analyzer/                      # Advanced analysis
│   ├── bottleneck_detector.py    # Identify bottlenecks
│   ├── skew_detector.py          # Detect data skew
│   └── memory_analyzer.py        # Memory analysis
├── config/                        # Configuration generation
│   ├── config_generator.py       # Generate optimal configs
│   └── optimal_configs.py        # Pre-defined configs
└── examples/                      # Usage examples
    └── basic_usage.py
```

## 🚀 Quick Start

### 1. Basic Monitoring

```python
from pyspark.sql import SparkSession
from spark_tuning import MetricsCollector

spark = SparkSession.builder.appName("MyApp").getOrCreate()
collector = MetricsCollector(spark)

# Your Spark job here
df = spark.read.parquet("input/")
result = df.groupBy("key").count()
result.write.parquet("output/")

# Print metrics summary
collector.print_summary()
```

### 2. Performance Profiling

```python
from spark_tuning import PerformanceProfiler

profiler = PerformanceProfiler(spark)

# Profile a specific operation
@profiler.profile_function("data_transformation")
def transform_data(df):
    return df.filter(...).groupBy(...).agg(...)

result = transform_data(df)
profiler.print_profile_summary()
```

### 3. Query Optimization

```python
from spark_tuning import QueryOptimizer

optimizer = QueryOptimizer(spark)
recommendations = optimizer.analyze_dataframe(df, "my_query")
optimizer.print_recommendations(recommendations)
```

### 4. Complete Integration Example

See `spark_code/examples/tuning_integration_example.py` for a full example of integrating spark_tuning with existing Oracle to Iceberg pipeline.

## 📊 Key Features

### Monitoring Module

**MetricsCollector**
- Collects executor, stage, and job metrics
- Exports metrics to JSON for analysis
- Compatible with Prometheus/Grafana

**PerformanceProfiler**
- Profiles DataFrame actions and transformations
- Identifies slow operations
- Analyzes execution plans automatically

**ResourceTracker**
- Monitors memory, CPU, and disk usage
- Generates alerts for resource issues (OOM, GC pressure)
- Tracks task failures and executor losses

### Optimization Module

**QueryOptimizer**
- Detects Cartesian products
- Recommends broadcast joins
- Identifies filter pushdown opportunities
- Analyzes shuffle operations
- Checks partitioning strategies

**CodeAnalyzer**
- Detects anti-patterns (`.collect()`, unnecessary `.count()`)
- Identifies inefficient UDFs
- Finds row iteration issues

### Analyzer Module

**BottleneckDetector**
- Identifies shuffle bottlenecks
- Detects GC pressure (>10% execution time)
- Finds disk spill issues
- Analyzes task skew

**SkewDetector**
- Detects data skew in partitions
- Suggests salting and repartitioning strategies
- Recommends AQE skew join optimization

**MemoryAnalyzer**
- Analyzes memory configuration
- Provides workload-specific tuning (caching/shuffling)
- Recommends optimal memory fractions

### Configuration Module

**ConfigGenerator**
- Generates optimal configs based on cluster resources
- Adjusts for workload type (batch, streaming, ML)
- Kubernetes-specific configurations

**OptimalConfigs**
- Pre-defined configs for common scenarios:
  - Small clusters
  - Large clusters
  - Streaming workloads
  - ML workloads
  - Kubernetes deployments

## 🔧 Integration with Existing Jobs

### Method 1: Minimal Integration (Monitoring Only)

Add monitoring to existing jobs without changing business logic:

```python
# At the start of your job
from spark_tuning import MetricsCollector, ResourceTracker

collector = MetricsCollector(spark)
tracker = ResourceTracker(spark, enable_alerts=True)

# Your existing code unchanged
# ...

# At the end
collector.print_summary()
tracker.print_resource_summary()
```

### Method 2: Enhanced Integration (Profiling)

Profile specific operations:

```python
from spark_tuning import PerformanceProfiler

profiler = PerformanceProfiler(spark)

# Wrap expensive operations
@profiler.profile_function("oracle_read")
def read_from_oracle():
    return oracle_reader.read_table(...)

@profiler.profile_function("iceberg_write")
def write_to_iceberg(df):
    df.writeTo(...).createOrReplace()

# Business logic
df = read_from_oracle()
write_to_iceberg(df)

# Review performance
profiler.print_profile_summary()
```

### Method 3: Full Integration (Optimization)

Apply optimizations based on analysis:

```python
from spark_tuning import QueryOptimizer, SkewDetector, OptimalConfigs

# 1. Apply optimal configs at session creation
configs = OptimalConfigs.get_k8s_config()
for key, value in configs.items():
    spark.conf.set(key, value)

# 2. Analyze queries
optimizer = QueryOptimizer(spark)
recommendations = optimizer.analyze_dataframe(df)

# 3. Check for skew
skew_detector = SkewDetector(spark)
has_skew, info = skew_detector.detect_skew(df)

# 4. Apply fixes based on findings
if has_skew:
    solutions = skew_detector.suggest_skew_solutions(df)
    # Apply salting, repartitioning, etc.
```

## 📈 Best Practices

### For Kubernetes Deployments

```python
from spark_tuning.config import ConfigGenerator, ClusterResources, WorkloadProfile

# Define your cluster
cluster = ClusterResources(
    num_executors=20,
    cores_per_executor=4,
    memory_per_executor_gb=8,
    total_cores=80,
    total_memory_gb=160
)

# Define your workload
workload = WorkloadProfile(
    type="batch",
    data_size_gb=500,
    has_shuffles=True,
    has_caching=True,
    has_joins=True,
    expected_duration_minutes=60
)

# Generate optimal configs
generator = ConfigGenerator()
configs = generator.generate_configs(cluster, workload)

# Apply to SparkApplication YAML or SparkSession
```

### Critical Metrics to Monitor

1. **Memory Utilization**: Should stay < 85%
2. **GC Time**: Should be < 10% of execution time
3. **Task Failure Rate**: Should be < 5%
4. **Shuffle Size**: Monitor for excessive data movement
5. **Disk Spill**: Should be zero for optimal performance

### Common Issues and Solutions

#### OOM Errors
```python
# 1. Analyze current config
from spark_tuning.analyzer import MemoryAnalyzer
analyzer = MemoryAnalyzer(spark)
issues = analyzer.analyze_memory_config()

# 2. Apply recommendations
spark.conf.set("spark.executor.memory", "8g")
spark.conf.set("spark.executor.memoryOverhead", "2g")

# 3. Use spill-to-disk for large datasets
df.persist(StorageLevel.MEMORY_AND_DISK)
```

#### Slow Joins
```python
# 1. Analyze join strategy
from spark_tuning import QueryOptimizer
optimizer = QueryOptimizer(spark)
recommendations = optimizer.analyze_dataframe(joined_df)

# 2. Apply broadcast for small tables
from pyspark.sql.functions import broadcast
result = large_df.join(broadcast(small_df), "key")

# 3. Enable AQE
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")
```

#### Data Skew
```python
# 1. Detect skew
from spark_tuning.analyzer import SkewDetector
detector = SkewDetector(spark)
has_skew, info = detector.detect_skew(df)

# 2. Apply salting
from pyspark.sql.functions import rand, concat, lit
df_salted = df.withColumn(
    "salted_key",
    concat(col("key"), lit("_"), (rand() * 10).cast("int"))
)
```

## 🎓 Learning Resources

### Package Documentation
- `/spark_code/spark_tuning/README.md` - Comprehensive package documentation
- `/spark_code/spark_tuning/examples/basic_usage.py` - Usage examples
- `/spark_code/examples/tuning_integration_example.py` - Integration example

### Apache Spark Resources
- [Spark Performance Tuning Guide](https://spark.apache.org/docs/latest/tuning.html)
- [Spark Monitoring](https://spark.apache.org/docs/latest/monitoring.html)
- [Spark SQL Performance](https://spark.apache.org/docs/latest/sql-performance-tuning.html)

### Research Papers & Articles
Based on best practices from:
- Apache Spark official documentation
- Production experience from large-scale deployments
- IBM Developer best practices
- Databricks optimization guides

## 🔍 Troubleshooting

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("spark_tuning")
logger.setLevel(logging.DEBUG)
```

### Export Detailed Metrics

```python
collector = MetricsCollector(spark)
collector.export_to_json("/tmp/spark_metrics_detailed.json")
```

### View Execution Plans

```python
df.explain(mode="extended")  # Show full execution plan
df.explain(mode="cost")      # Show with cost estimates
```

## 📝 Next Steps

1. **Try Examples**: Run `spark_code/spark_tuning/examples/basic_usage.py`
2. **Integrate Gradually**: Start with monitoring, then add profiling
3. **Analyze Existing Jobs**: Use post-execution analysis tools
4. **Apply Optimizations**: Implement recommendations based on findings
5. **Monitor Continuously**: Set up regular metrics collection

## 🤝 Contributing

Improvements welcome! Follow these guidelines:
- Use Apache Spark best practices
- Add tests for new features
- Update documentation
- Follow existing code style

## 📄 License

MIT License - See LICENSE file for details.
