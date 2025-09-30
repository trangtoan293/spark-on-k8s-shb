"""
Query Optimizer

Analyzes Spark SQL queries and DataFrames for optimization opportunities.
Provides recommendations based on Apache Spark best practices and Catalyst optimizer insights.
"""

import logging
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from pyspark.sql import SparkSession, DataFrame


@dataclass
class QueryOptimization:
    """Optimization recommendation for a query."""
    category: str  # "JOIN", "FILTER", "AGGREGATION", "PARTITION", "CACHE"
    severity: str  # "HIGH", "MEDIUM", "LOW"
    issue: str
    recommendation: str
    estimated_impact: str
    code_example: Optional[str] = None


class QueryOptimizer:
    """
    Analyze and optimize Spark SQL queries and DataFrames.
    
    Analyzes:
        - Join strategies (broadcast vs shuffle)
        - Filter pushdown opportunities
        - Predicate pushdown
        - Partition pruning
        - Unnecessary shuffles
        - Caching opportunities
    
    Best Practices Applied:
        - Broadcast joins for small tables (<10MB)
        - Filter early and often
        - Avoid Cartesian products
        - Predicate pushdown to data sources
        - Partition pruning for partitioned tables
        - AQE (Adaptive Query Execution) recommendations
    """
    
    # Broadcast join threshold (10 MB default in Spark 3.x)
    BROADCAST_JOIN_THRESHOLD_MB = 10
    
    def __init__(self, spark: SparkSession):
        """
        Initialize query optimizer.
        
        Args:
            spark: Active SparkSession
        """
        self.spark = spark
        self.logger = logging.getLogger(__name__)
        
        # Get current Spark SQL configurations
        self.broadcast_threshold = int(
            spark.conf.get("spark.sql.autoBroadcastJoinThreshold", "10485760")
        ) / (1024 * 1024)  # Convert to MB
        
        self.adaptive_enabled = spark.conf.get(
            "spark.sql.adaptive.enabled", "true"
        ).lower() == "true"
        
        self.logger.info("QueryOptimizer initialized")
    
    def analyze_dataframe(self, df: DataFrame, df_name: str = "dataframe") -> List[QueryOptimization]:
        """
        Analyze a DataFrame and provide optimization recommendations.
        
        Args:
            df: DataFrame to analyze
            df_name: Name for reporting purposes
            
        Returns:
            List of QueryOptimization recommendations
            
        Example:
            optimizer = QueryOptimizer(spark)
            recommendations = optimizer.analyze_dataframe(my_df, "sales_data")
            for rec in recommendations:
                print(f"{rec.severity}: {rec.issue}")
                print(f"  → {rec.recommendation}")
        """
        recommendations = []
        
        try:
            # Get logical and physical plans
            logical_plan = df._jdf.queryExecution().logical().toString()
            physical_plan = df._jdf.queryExecution().executedPlan().toString()
            
            # Analyze for common issues
            recommendations.extend(self._check_joins(physical_plan, df_name))
            recommendations.extend(self._check_filters(logical_plan, physical_plan, df_name))
            recommendations.extend(self._check_shuffles(physical_plan, df_name))
            recommendations.extend(self._check_partitioning(df, df_name))
            recommendations.extend(self._check_caching_opportunity(df, df_name))
            
        except Exception as e:
            self.logger.error(f"Failed to analyze DataFrame: {e}")
        
        return recommendations
    
    def _check_joins(self, physical_plan: str, df_name: str) -> List[QueryOptimization]:
        """Check join operations for optimization opportunities."""
        recommendations = []
        
        # Check for Cartesian products
        if "CartesianProduct" in physical_plan:
            recommendations.append(QueryOptimization(
                category="JOIN",
                severity="HIGH",
                issue="Cartesian product detected (cross join without conditions)",
                recommendation=(
                    "Add proper join conditions to avoid Cartesian product. "
                    "This operation has O(n*m) complexity and is extremely expensive."
                ),
                estimated_impact="HIGH - Can cause job failure or hours of execution",
                code_example="""
# Bad: Cartesian product
df1.join(df2)

# Good: Join with condition
df1.join(df2, on="id", how="inner")
"""
            ))
        
        # Check for SortMergeJoin when broadcast might be better
        if "SortMergeJoin" in physical_plan and not "BroadcastHashJoin" in physical_plan:
            recommendations.append(QueryOptimization(
                category="JOIN",
                severity="MEDIUM",
                issue="Sort-merge join detected. Consider broadcast join if one side is small.",
                recommendation=(
                    f"If one table is smaller than {self.broadcast_threshold}MB, "
                    "use broadcast join to avoid shuffle. "
                    "Use spark.sql.autoBroadcastJoinThreshold or broadcast() hint."
                ),
                estimated_impact="MEDIUM - Can eliminate shuffle and reduce execution time by 50%+",
                code_example=f"""
from pyspark.sql.functions import broadcast

# Explicit broadcast hint for small table
large_df.join(broadcast(small_df), on="id")

# Or increase broadcast threshold
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", {self.BROADCAST_JOIN_THRESHOLD_MB * 2 * 1024 * 1024})
"""
            ))
        
        # Check for multiple joins
        join_count = physical_plan.count("Join")
        if join_count > 3:
            recommendations.append(QueryOptimization(
                category="JOIN",
                severity="MEDIUM",
                issue=f"Multiple join operations detected ({join_count})",
                recommendation=(
                    "Multiple joins can cause cascading shuffles. Consider:\n"
                    "  1. Pre-partitioning tables by join keys\n"
                    "  2. Using broadcast for small dimension tables\n"
                    "  3. Denormalizing data if joins are always performed together"
                ),
                estimated_impact="MEDIUM - Can reduce shuffle operations significantly",
                code_example="""
# Pre-partition by join key
df1 = df1.repartition("join_key")
df2 = df2.repartition("join_key")
result = df1.join(df2, on="join_key")

# Or broadcast small dimensions
fact_table.join(broadcast(dim1), "dim1_id").join(broadcast(dim2), "dim2_id")
"""
            ))
        
        return recommendations
    
    def _check_filters(self, logical_plan: str, physical_plan: str, df_name: str) -> List[QueryOptimization]:
        """Check filter operations for optimization opportunities."""
        recommendations = []
        
        # Check if filters come after joins (filter pushdown issue)
        if "Join" in physical_plan and "Filter" in physical_plan:
            join_index = physical_plan.index("Join")
            filter_indices = [i for i in range(len(physical_plan)) if physical_plan.startswith("Filter", i)]
            
            if filter_indices and any(idx > join_index for idx in filter_indices):
                recommendations.append(QueryOptimization(
                    category="FILTER",
                    severity="HIGH",
                    issue="Filter applied after join - potential filter pushdown issue",
                    recommendation=(
                        "Apply filters BEFORE joins to reduce data volume early. "
                        "Catalyst optimizer usually handles this, but explicit filtering helps readability and ensures optimization."
                    ),
                    estimated_impact="HIGH - Can reduce join input size by orders of magnitude",
                    code_example="""
# Bad: Filter after join
df1.join(df2, "id").filter(col("status") == "active")

# Good: Filter before join
df1_filtered = df1.filter(col("status") == "active")
df1_filtered.join(df2, "id")
"""
                ))
        
        # Check for complex filter expressions that might not push down
        if "UDF" in logical_plan and "Filter" in logical_plan:
            recommendations.append(QueryOptimization(
                category="FILTER",
                severity="MEDIUM",
                issue="UDF in filter prevents predicate pushdown",
                recommendation=(
                    "Replace UDFs with built-in Spark SQL functions in filters. "
                    "UDFs prevent predicate pushdown to data sources (Parquet, JDBC, etc.)."
                ),
                estimated_impact="MEDIUM - Can enable partition pruning and filter pushdown",
                code_example="""
# Bad: UDF prevents pushdown
from pyspark.sql.functions import udf
is_valid = udf(lambda x: x > 100, BooleanType())
df.filter(is_valid(col("value")))

# Good: Use built-in functions
df.filter(col("value") > 100)
"""
            ))
        
        return recommendations
    
    def _check_shuffles(self, physical_plan: str, df_name: str) -> List[QueryOptimization]:
        """Check for unnecessary shuffle operations."""
        recommendations = []
        
        shuffle_count = physical_plan.count("Exchange")
        
        if shuffle_count > 5:
            recommendations.append(QueryOptimization(
                category="PARTITION",
                severity="HIGH",
                issue=f"Excessive shuffle operations detected ({shuffle_count})",
                recommendation=(
                    "Multiple shuffles indicate:\n"
                    "  1. Multiple groupBy/join operations\n"
                    "  2. Repartitioning without coalescing\n"
                    "  3. Wide transformations on already partitioned data\n"
                    "Consider pre-partitioning data or using window functions instead of multiple groupBys."
                ),
                estimated_impact="HIGH - Shuffles are the most expensive Spark operations",
                code_example="""
# Bad: Multiple groupBys causing multiple shuffles
df.groupBy("a").count().groupBy("b").sum()

# Better: Single groupBy with window function
from pyspark.sql.window import Window
from pyspark.sql.functions import sum, count
window = Window.partitionBy("a", "b")
df.withColumn("cnt", count("*").over(window))
"""
            ))
        
        # Check for repartition after coalesce
        if "Repartition" in physical_plan and "Coalesce" in physical_plan:
            recommendations.append(QueryOptimization(
                category="PARTITION",
                severity="MEDIUM",
                issue="Both repartition and coalesce detected",
                recommendation=(
                    "Use either repartition() (full shuffle) or coalesce() (no shuffle), "
                    "but not both in sequence. Choose based on your needs:\n"
                    "  - repartition(): When you need to increase partitions or rebalance data\n"
                    "  - coalesce(): When you need to decrease partitions without full shuffle"
                ),
                estimated_impact="MEDIUM - Eliminate unnecessary shuffle",
                code_example="""
# Bad: Unnecessary shuffle
df.repartition(100).coalesce(50)

# Good: Choose one
df.coalesce(50)  # If decreasing partitions
# OR
df.repartition(100)  # If increasing or rebalancing
"""
            ))
        
        return recommendations
    
    def _check_partitioning(self, df: DataFrame, df_name: str) -> List[QueryOptimization]:
        """Check partitioning strategy."""
        recommendations = []
        
        try:
            num_partitions = df.rdd.getNumPartitions()
            
            # Check for too few partitions
            if num_partitions < 10:
                recommendations.append(QueryOptimization(
                    category="PARTITION",
                    severity="MEDIUM",
                    issue=f"Low partition count ({num_partitions}) may limit parallelism",
                    recommendation=(
                        "Increase partitions for better parallelism. "
                        f"Recommended: 2-3 partitions per CPU core. "
                        "Use repartition() or configure spark.sql.shuffle.partitions."
                    ),
                    estimated_impact="MEDIUM - Better resource utilization",
                    code_example=f"""
# Repartition explicitly
df = df.repartition(200)

# Or configure globally
spark.conf.set("spark.sql.shuffle.partitions", "200")
"""
                ))
            
            # Check for too many partitions
            elif num_partitions > 10000:
                recommendations.append(QueryOptimization(
                    category="PARTITION",
                    severity="HIGH",
                    issue=f"Excessive partition count ({num_partitions}) causes scheduling overhead",
                    recommendation=(
                        "Too many partitions create scheduling overhead. "
                        "Use coalesce() to reduce partitions. "
                        "Aim for partitions of 100MB-200MB each."
                    ),
                    estimated_impact="HIGH - Reduce task scheduling overhead",
                    code_example="""
# Reduce partitions
df = df.coalesce(500)

# Enable AQE to automatically coalesce partitions
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")
"""
                ))
        
        except Exception as e:
            self.logger.warning(f"Could not check partitioning: {e}")
        
        return recommendations
    
    def _check_caching_opportunity(self, df: DataFrame, df_name: str) -> List[QueryOptimization]:
        """Check if DataFrame should be cached."""
        recommendations = []
        
        # This is a heuristic - in real usage, you'd track DataFrame reuse
        recommendations.append(QueryOptimization(
            category="CACHE",
            severity="LOW",
            issue="Consider caching if this DataFrame is used multiple times",
            recommendation=(
                "If a DataFrame is used more than once (multiple actions), "
                "cache it to avoid recomputation. "
                "Use appropriate storage level based on data size and memory availability."
            ),
            estimated_impact="LOW to HIGH - Depends on reuse frequency",
            code_example="""
# Cache for multiple uses
df_cached = df.cache()
df_cached.count()  # First action computes and caches
df_cached.show()   # Second action uses cache

# Choose storage level based on needs
df.persist(StorageLevel.MEMORY_AND_DISK)  # Spill to disk if needed
df.persist(StorageLevel.MEMORY_ONLY)      # Keep only in memory

# Don't forget to unpersist when done
df.unpersist()
"""
        ))
        
        return recommendations
    
    def print_recommendations(self, recommendations: List[QueryOptimization]) -> None:
        """Print optimization recommendations in a readable format."""
        if not recommendations:
            print("\n✅ No optimization issues found!\n")
            return
        
        print("\n" + "="*80)
        print("QUERY OPTIMIZATION RECOMMENDATIONS")
        print("="*80)
        
        # Group by severity
        high = [r for r in recommendations if r.severity == "HIGH"]
        medium = [r for r in recommendations if r.severity == "MEDIUM"]
        low = [r for r in recommendations if r.severity == "LOW"]
        
        for severity, recs in [("HIGH", high), ("MEDIUM", medium), ("LOW", low)]:
            if recs:
                print(f"\n🔴 {severity} PRIORITY ({len(recs)} issues)")
                print("-" * 80)
                for i, rec in enumerate(recs, 1):
                    print(f"\n{i}. [{rec.category}] {rec.issue}")
                    print(f"   Recommendation: {rec.recommendation}")
                    print(f"   Impact: {rec.estimated_impact}")
                    if rec.code_example:
                        print(f"   Example:{rec.code_example}")
        
        print("\n" + "="*80 + "\n")
