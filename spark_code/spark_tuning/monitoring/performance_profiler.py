"""
Performance Profiler

Profiles Spark job performance and identifies optimization opportunities.
Analyzes execution plans, task durations, and resource utilization patterns.
"""

import time
import logging
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, asdict
from functools import wraps
from pyspark.sql import SparkSession, DataFrame


@dataclass
class ProfileResult:
    """Result of a performance profiling session."""
    operation_name: str
    duration_seconds: float
    num_partitions: Optional[int]
    num_rows: Optional[int]
    data_size_mb: Optional[float]
    execution_plan: Optional[str]
    recommendations: List[str]
    timestamp: str


class PerformanceProfiler:
    """
    Profile Spark operations and provide optimization recommendations.
    
    Tracks execution time, data volume, partition counts, and analyzes
    execution plans to identify performance bottlenecks.
    
    Best Practices Applied:
        - Minimal instrumentation overhead
        - Lazy evaluation awareness
        - Action vs transformation tracking
        - Execution plan analysis
    """
    
    def __init__(self, spark: SparkSession, auto_analyze: bool = True):
        """
        Initialize performance profiler.
        
        Args:
            spark: Active SparkSession
            auto_analyze: Automatically analyze execution plans
        """
        self.spark = spark
        self.logger = logging.getLogger(__name__)
        self.auto_analyze = auto_analyze
        self.profile_history: List[ProfileResult] = []
    
    def profile_dataframe_action(
        self, 
        df: DataFrame, 
        action_name: str = "action",
        action_func: Optional[Callable] = None
    ) -> ProfileResult:
        """
        Profile a DataFrame action (count, collect, write, etc.).
        
        Args:
            df: DataFrame to profile
            action_name: Name of the action for reporting
            action_func: Optional action function to execute (e.g., df.count)
            
        Returns:
            ProfileResult with timing and recommendations
            
        Example:
            profiler = PerformanceProfiler(spark)
            result = profiler.profile_dataframe_action(df, "count", df.count)
        """
        import time
        from datetime import datetime
        
        start_time = time.time()
        num_partitions = df.rdd.getNumPartitions()
        
        # Get execution plan before action
        execution_plan = None
        if self.auto_analyze:
            try:
                execution_plan = df._jdf.queryExecution().toString()
            except Exception as e:
                self.logger.warning(f"Could not retrieve execution plan: {e}")
        
        # Execute action if provided
        result_value = None
        if action_func:
            result_value = action_func()
        
        duration = time.time() - start_time
        
        # Analyze and generate recommendations
        recommendations = self._analyze_profile(
            duration=duration,
            num_partitions=num_partitions,
            execution_plan=execution_plan
        )
        
        profile_result = ProfileResult(
            operation_name=action_name,
            duration_seconds=duration,
            num_partitions=num_partitions,
            num_rows=result_value if isinstance(result_value, int) else None,
            data_size_mb=None,
            execution_plan=execution_plan,
            recommendations=recommendations,
            timestamp=datetime.utcnow().isoformat()
        )
        
        self.profile_history.append(profile_result)
        return profile_result
    
    def profile_function(self, func_name: str):
        """
        Decorator to profile any Spark function.
        
        Args:
            func_name: Name of the function for reporting
            
        Example:
            profiler = PerformanceProfiler(spark)
            
            @profiler.profile_function("data_transformation")
            def transform_data(df):
                return df.filter(...).groupBy(...)
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                from datetime import datetime
                start_time = time.time()
                
                result = func(*args, **kwargs)
                
                duration = time.time() - start_time
                
                profile_result = ProfileResult(
                    operation_name=func_name,
                    duration_seconds=duration,
                    num_partitions=None,
                    num_rows=None,
                    data_size_mb=None,
                    execution_plan=None,
                    recommendations=[],
                    timestamp=datetime.utcnow().isoformat()
                )
                
                self.profile_history.append(profile_result)
                self.logger.info(
                    f"Function '{func_name}' completed in {duration:.2f}s"
                )
                
                return result
            return wrapper
        return decorator
    
    def _analyze_profile(
        self,
        duration: float,
        num_partitions: Optional[int],
        execution_plan: Optional[str]
    ) -> List[str]:
        """
        Analyze profile data and generate recommendations.
        
        Args:
            duration: Execution duration in seconds
            num_partitions: Number of partitions
            execution_plan: Spark execution plan
            
        Returns:
            List of optimization recommendations
        """
        recommendations = []
        
        # Check partition count
        if num_partitions:
            if num_partitions < 10:
                recommendations.append(
                    f"Low partition count ({num_partitions}). "
                    "Consider increasing parallelism with repartition() or coalesce()."
                )
            elif num_partitions > 10000:
                recommendations.append(
                    f"Very high partition count ({num_partitions}). "
                    "This may cause excessive task scheduling overhead. "
                    "Consider reducing partitions with coalesce()."
                )
        
        # Analyze execution plan
        if execution_plan:
            # Check for shuffle operations
            if "Exchange" in execution_plan:
                shuffle_count = execution_plan.count("Exchange")
                if shuffle_count > 3:
                    recommendations.append(
                        f"Multiple shuffle operations detected ({shuffle_count}). "
                        "Consider:\n"
                        "  - Using broadcast joins for small tables\n"
                        "  - Reducing groupBy/join operations\n"
                        "  - Pre-partitioning data by join keys"
                    )
            
            # Check for CartesianProduct
            if "CartesianProduct" in execution_plan:
                recommendations.append(
                    "Cartesian product detected! This is very expensive. "
                    "Add proper join conditions or filters."
                )
            
            # Check for sort operations
            if "Sort" in execution_plan:
                sort_count = execution_plan.count("Sort")
                if sort_count > 2:
                    recommendations.append(
                        f"Multiple sort operations ({sort_count}). "
                        "Consider reducing orderBy operations or using sortWithinPartitions()."
                    )
        
        # Duration-based recommendations
        if duration > 60:
            recommendations.append(
                f"Long execution time ({duration:.1f}s). Review execution plan "
                "and consider caching intermediate results with df.cache()."
            )
        
        return recommendations
    
    def get_slowest_operations(self, top_n: int = 5) -> List[ProfileResult]:
        """
        Get the slowest profiled operations.
        
        Args:
            top_n: Number of slowest operations to return
            
        Returns:
            List of ProfileResult objects sorted by duration
        """
        sorted_results = sorted(
            self.profile_history,
            key=lambda x: x.duration_seconds,
            reverse=True
        )
        return sorted_results[:top_n]
    
    def print_profile_summary(self) -> None:
        """Print summary of all profiled operations."""
        if not self.profile_history:
            print("No profile data available.")
            return
        
        print("\n" + "="*80)
        print("PERFORMANCE PROFILE SUMMARY")
        print("="*80)
        print(f"Total operations profiled: {len(self.profile_history)}")
        
        total_time = sum(p.duration_seconds for p in self.profile_history)
        print(f"Total execution time: {total_time:.2f}s")
        
        print("\nSlowest operations:")
        for i, result in enumerate(self.get_slowest_operations(5), 1):
            print(f"\n{i}. {result.operation_name}")
            print(f"   Duration: {result.duration_seconds:.2f}s")
            if result.num_partitions:
                print(f"   Partitions: {result.num_partitions}")
            if result.recommendations:
                print("   Recommendations:")
                for rec in result.recommendations:
                    print(f"   - {rec}")
        
        print("="*80 + "\n")
    
    def clear_history(self) -> None:
        """Clear profiling history."""
        self.profile_history.clear()
        self.logger.info("Profile history cleared")
