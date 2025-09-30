"""
Basic Usage Examples for Spark Tuning Package

Demonstrates common use cases for monitoring and optimizing Spark applications.
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum, count, broadcast
from spark_tuning import (
    MetricsCollector,
    PerformanceProfiler,
    QueryOptimizer,
    SkewDetector,
    ResourceTracker,
    ConfigGenerator,
    OptimalConfigs
)


def example_1_basic_monitoring():
    """Example 1: Basic metrics collection and monitoring."""
    print("\n" + "="*80)
    print("EXAMPLE 1: Basic Monitoring")
    print("="*80)
    
    spark = SparkSession.builder.appName("BasicMonitoring").getOrCreate()
    
    # Create sample data
    df = spark.range(0, 10000000).selectExpr("id", "id % 100 as category", "id * 2 as value")
    
    # Initialize metrics collector
    collector = MetricsCollector(spark)
    
    # Perform some operations
    result = df.groupBy("category").agg(sum("value").alias("total"))
    result.count()
    
    # Collect and display metrics
    collector.print_summary()
    
    # Export metrics to file
    collector.export_to_json("/tmp/spark_metrics.json")
    print("\n✅ Metrics exported to /tmp/spark_metrics.json")


def example_2_performance_profiling():
    """Example 2: Profile operations to find bottlenecks."""
    print("\n" + "="*80)
    print("EXAMPLE 2: Performance Profiling")
    print("="*80)
    
    spark = SparkSession.builder.appName("PerformanceProfiling").getOrCreate()
    
    df = spark.range(0, 5000000).selectExpr("id", "id % 1000 as group_key", "rand() * 100 as amount")
    
    # Initialize profiler
    profiler = PerformanceProfiler(spark, auto_analyze=True)
    
    # Profile a transformation
    @profiler.profile_function("aggregation")
    def aggregate_data(df):
        return df.groupBy("group_key").agg(
            count("*").alias("count"),
            sum("amount").alias("total_amount")
        )
    
    result = aggregate_data(df)
    
    # Profile the action
    profiler.profile_dataframe_action(result, "count", result.count)
    
    # Show results
    profiler.print_profile_summary()


def example_3_query_optimization():
    """Example 3: Analyze queries for optimization opportunities."""
    print("\n" + "="*80)
    print("EXAMPLE 3: Query Optimization")
    print("="*80)
    
    spark = SparkSession.builder.appName("QueryOptimization").getOrCreate()
    
    # Create sample tables
    df1 = spark.range(0, 1000000).selectExpr("id", "id % 100 as key", "rand() * 1000 as value1")
    df2 = spark.range(0, 100).selectExpr("id as key", "id * 10 as value2")
    
    # Join operation (should recommend broadcast join)
    result = df1.join(df2, "key")
    
    # Analyze the query
    optimizer = QueryOptimizer(spark)
    recommendations = optimizer.analyze_dataframe(result, "join_query")
    
    # Print recommendations
    optimizer.print_recommendations(recommendations)
    
    # Apply optimization (broadcast small table)
    print("\n📝 Applying broadcast join optimization...")
    optimized_result = df1.join(broadcast(df2), "key")
    
    # Analyze optimized query
    recommendations = optimizer.analyze_dataframe(optimized_result, "optimized_join")
    optimizer.print_recommendations(recommendations)


def example_4_skew_detection():
    """Example 4: Detect and handle data skew."""
    print("\n" + "="*80)
    print("EXAMPLE 4: Data Skew Detection")
    print("="*80)
    
    spark = SparkSession.builder.appName("SkewDetection").getOrCreate()
    
    # Create skewed data (one partition much larger)
    from pyspark.sql.functions import when, rand
    df = spark.range(0, 1000000).selectExpr(
        "id",
        "CASE WHEN id % 100 = 0 THEN 'hot_key' ELSE CAST(id % 10 as STRING) END as partition_key",
        "rand() * 100 as value"
    )
    
    # Detect skew
    detector = SkewDetector(spark)
    has_skew, skew_info = detector.detect_skew(df.repartition("partition_key"), sample_fraction=0.1)
    
    if has_skew:
        print("\n⚠️  Data skew detected!")
        detector.print_skew_analysis(skew_info)
        
        # Get solutions
        solutions = detector.suggest_skew_solutions(df, "partition_key")
        print("\n💡 Suggested Solutions:")
        for solution in solutions:
            print(solution)


def example_5_resource_monitoring():
    """Example 5: Monitor resource utilization and get alerts."""
    print("\n" + "="*80)
    print("EXAMPLE 5: Resource Monitoring")
    print("="*80)
    
    spark = SparkSession.builder.appName("ResourceMonitoring").getOrCreate()
    
    # Initialize tracker with alerts
    tracker = ResourceTracker(spark, enable_alerts=True)
    
    # Perform some work
    df = spark.range(0, 10000000).selectExpr("id", "id % 1000 as key", "rand() * 1000 as value")
    df.groupBy("key").agg(sum("value")).count()
    
    # Capture resource snapshot
    snapshot = tracker.capture_snapshot()
    
    # Print resource summary
    tracker.print_resource_summary()
    
    # Check for alerts
    critical_alerts = tracker.get_active_alerts("CRITICAL")
    if critical_alerts:
        print("\n🔴 CRITICAL ALERTS:")
        for alert in critical_alerts:
            print(f"\n{alert.category}: {alert.message}")
            print("Recommendations:")
            for rec in alert.recommendations:
                print(f"  - {rec}")


def example_6_config_generation():
    """Example 6: Generate optimal configurations."""
    print("\n" + "="*80)
    print("EXAMPLE 6: Configuration Generation")
    print("="*80)
    
    from spark_tuning.config import ClusterResources, WorkloadProfile
    
    # Define cluster resources
    cluster = ClusterResources(
        num_executors=20,
        cores_per_executor=4,
        memory_per_executor_gb=8,
        total_cores=80,
        total_memory_gb=160
    )
    
    # Define workload characteristics
    workload = WorkloadProfile(
        type="batch",
        data_size_gb=500,
        has_shuffles=True,
        has_caching=True,
        has_joins=True,
        expected_duration_minutes=60
    )
    
    # Generate configs
    generator = ConfigGenerator()
    configs = generator.generate_configs(cluster, workload)
    
    # Print configurations
    generator.print_configs(configs)
    
    # Get pre-defined configs
    print("\n📋 Pre-defined Kubernetes Configuration:")
    k8s_configs = OptimalConfigs.get_k8s_config()
    for key, value in k8s_configs.items():
        print(f"  {key} = {value}")


def example_7_complete_workflow():
    """Example 7: Complete monitoring and optimization workflow."""
    print("\n" + "="*80)
    print("EXAMPLE 7: Complete Workflow")
    print("="*80)
    
    # 1. Initialize with optimal configs
    spark = SparkSession.builder.appName("CompleteWorkflow")
    configs = OptimalConfigs.get_k8s_config()
    for key, value in list(configs.items())[:5]:  # Apply first 5 for demo
        spark = spark.config(key, value)
    spark = spark.getOrCreate()
    
    # 2. Initialize all tools
    collector = MetricsCollector(spark)
    profiler = PerformanceProfiler(spark)
    optimizer = QueryOptimizer(spark)
    tracker = ResourceTracker(spark, enable_alerts=True)
    
    # 3. Load and process data
    df = spark.range(0, 1000000).selectExpr("id", "id % 100 as category", "rand() * 1000 as value")
    
    # 4. Profile transformation
    @profiler.profile_function("data_transformation")
    def transform_data(df):
        return df.filter(col("value") > 500).groupBy("category").agg(sum("value").alias("total"))
    
    result = transform_data(df)
    
    # 5. Analyze query
    recommendations = optimizer.analyze_dataframe(result, "main_query")
    
    # 6. Execute with monitoring
    tracker.capture_snapshot()
    profiler.profile_dataframe_action(result, "final_count", result.count)
    
    # 7. Print all summaries
    print("\n" + "="*80)
    print("WORKFLOW SUMMARY")
    print("="*80)
    
    collector.print_summary()
    profiler.print_profile_summary()
    optimizer.print_recommendations(recommendations)
    tracker.print_resource_summary()


if __name__ == "__main__":
    print("\n" + "="*80)
    print("SPARK TUNING PACKAGE - USAGE EXAMPLES")
    print("="*80)
    
    # Run examples
    examples = [
        ("Basic Monitoring", example_1_basic_monitoring),
        ("Performance Profiling", example_2_performance_profiling),
        ("Query Optimization", example_3_query_optimization),
        ("Skew Detection", example_4_skew_detection),
        ("Resource Monitoring", example_5_resource_monitoring),
        ("Config Generation", example_6_config_generation),
        ("Complete Workflow", example_7_complete_workflow),
    ]
    
    print("\nAvailable examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")
    
    print("\nRunning all examples...")
    for name, func in examples:
        try:
            func()
        except Exception as e:
            print(f"\n❌ Error in {name}: {e}")
    
    print("\n" + "="*80)
    print("✅ Examples completed!")
    print("="*80)
