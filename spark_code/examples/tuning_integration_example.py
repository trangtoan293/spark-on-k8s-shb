"""
Integration Example: Using Spark Tuning with Existing Oracle to Iceberg Job

Shows how to integrate spark_tuning package into existing data pipeline jobs.
"""

import os
import sys
from pyspark.sql import SparkSession

# Add spark_code to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from spark_tuning import (
    MetricsCollector,
    PerformanceProfiler,
    QueryOptimizer,
    ResourceTracker,
    OptimalConfigs
)
from utils.oracle import OracleReader
from utils.configs import load_env_config


def create_optimized_spark_session(app_name: str) -> SparkSession:
    """
    Create SparkSession with optimal configurations.
    
    Uses pre-defined Kubernetes configurations from spark_tuning package.
    """
    # Get optimal K8s configs
    optimal_configs = OptimalConfigs.get_k8s_config()
    
    # Create session with configs
    builder = SparkSession.builder.appName(app_name)
    
    # Apply optimal configs
    for key, value in optimal_configs.items():
        builder = builder.config(key, value)
    
    # Add Iceberg and Oracle specific configs
    builder = builder.config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")
    builder = builder.config("spark.sql.catalog.spark_catalog", "org.apache.iceberg.spark.SparkSessionCatalog")
    
    return builder.getOrCreate()


def monitored_oracle_to_iceberg():
    """
    Enhanced version of oracle_to_iceberg with monitoring and optimization.
    """
    print("\n" + "="*80)
    print("ORACLE TO ICEBERG - WITH MONITORING & OPTIMIZATION")
    print("="*80)
    
    # 1. Create optimized Spark session
    spark = create_optimized_spark_session("OracleToIceberg_Optimized")
    
    # 2. Initialize monitoring tools
    collector = MetricsCollector(spark)
    profiler = PerformanceProfiler(spark, auto_analyze=True)
    optimizer = QueryOptimizer(spark)
    tracker = ResourceTracker(spark, enable_alerts=True)
    
    print("\n✅ Monitoring tools initialized")
    
    # 3. Load configuration
    config = load_env_config()
    oracle_config = config["oracle"]
    iceberg_config = config["iceberg"]
    
    # 4. Capture initial resource state
    print("\n📊 Capturing initial resource state...")
    initial_snapshot = tracker.capture_snapshot()
    
    # 5. Read from Oracle with profiling
    print(f"\n📖 Reading from Oracle: {oracle_config['table']}")
    oracle_reader = OracleReader(spark, oracle_config)
    
    @profiler.profile_function("oracle_read")
    def read_oracle_data():
        return oracle_reader.read_table(
            table_name=oracle_config['table'],
            partition_column=oracle_config.get('partition_column'),
            num_partitions=oracle_config.get('num_partitions', 10)
        )
    
    df = read_oracle_data()
    
    # 6. Analyze the query
    print("\n🔍 Analyzing query optimization opportunities...")
    recommendations = optimizer.analyze_dataframe(df, "oracle_read")
    if recommendations:
        optimizer.print_recommendations(recommendations)
    
    # 7. Check for data skew
    from spark_tuning.analyzer import SkewDetector
    skew_detector = SkewDetector(spark)
    
    print("\n🔍 Checking for data skew...")
    has_skew, skew_info = skew_detector.detect_skew(df, sample_fraction=0.1)
    if has_skew:
        print("⚠️  Data skew detected!")
        skew_detector.print_skew_analysis(skew_info)
    
    # 8. Write to Iceberg with profiling
    print(f"\n💾 Writing to Iceberg: {iceberg_config['table']}")
    
    @profiler.profile_function("iceberg_write")
    def write_to_iceberg():
        df.writeTo(iceberg_config['table']) \
          .using("iceberg") \
          .tableProperty("write.format.default", "parquet") \
          .tableProperty("write.parquet.compression-codec", "snappy") \
          .createOrReplace()
    
    write_to_iceberg()
    
    # 9. Capture final resource state
    print("\n📊 Capturing final resource state...")
    final_snapshot = tracker.capture_snapshot()
    tracker.print_resource_summary()
    
    # 10. Print comprehensive summary
    print("\n" + "="*80)
    print("JOB EXECUTION SUMMARY")
    print("="*80)
    
    # Metrics
    collector.print_summary()
    
    # Performance profile
    profiler.print_profile_summary()
    
    # Resource alerts
    alerts = tracker.get_active_alerts()
    if alerts:
        print("\n⚠️  ALERTS GENERATED:")
        for alert in alerts:
            print(f"\n{alert.severity} - {alert.category}: {alert.message}")
            if alert.recommendations:
                print("Recommendations:")
                for rec in alert.recommendations[:3]:  # Top 3
                    print(f"  - {rec}")
    
    # 11. Export metrics for analysis
    metrics_file = "/tmp/oracle_to_iceberg_metrics.json"
    collector.export_to_json(metrics_file)
    print(f"\n📊 Detailed metrics exported to: {metrics_file}")
    
    print("\n" + "="*80)
    print("✅ Job completed with monitoring!")
    print("="*80)


def analyze_existing_job_performance():
    """
    Analyze performance of an existing Spark job without modifying it.
    
    Uses post-execution analysis from Spark UI metrics.
    """
    print("\n" + "="*80)
    print("POST-EXECUTION PERFORMANCE ANALYSIS")
    print("="*80)
    
    spark = SparkSession.builder.appName("PerformanceAnalysis").getOrCreate()
    
    # Initialize analyzers
    from spark_tuning.analyzer import BottleneckDetector, MemoryAnalyzer
    
    bottleneck_detector = BottleneckDetector(spark)
    memory_analyzer = MemoryAnalyzer(spark)
    
    # Detect bottlenecks
    print("\n🔍 Analyzing bottlenecks...")
    bottlenecks = bottleneck_detector.detect_bottlenecks()
    bottleneck_detector.print_bottlenecks(bottlenecks)
    
    # Analyze memory configuration
    print("\n🔍 Analyzing memory configuration...")
    memory_issues = memory_analyzer.analyze_memory_config()
    memory_analyzer.print_memory_analysis(memory_issues)
    
    # Get tuning recommendations
    print("\n💡 Memory tuning recommendations for different workloads:")
    
    workload_types = ["caching", "shuffling", "balanced"]
    for workload_type in workload_types:
        print(f"\n{workload_type.upper()} workload:")
        configs = memory_analyzer.suggest_memory_tuning(workload_type)
        for key, value in list(configs.items())[:5]:  # Show first 5
            print(f"  {key} = {value}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Spark Tuning Integration Examples")
    parser.add_argument(
        "--mode",
        choices=["monitored_job", "analyze"],
        default="monitored_job",
        help="Run mode: monitored_job or analyze"
    )
    
    args = parser.parse_args()
    
    if args.mode == "monitored_job":
        monitored_oracle_to_iceberg()
    elif args.mode == "analyze":
        analyze_existing_job_performance()
    
    print("\n✨ Integration example completed!")
