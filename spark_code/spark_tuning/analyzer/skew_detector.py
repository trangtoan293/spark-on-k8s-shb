"""
Skew Detector

Detects data skew in partitions which causes unbalanced task execution.
"""

import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col, count, spark_partition_id


@dataclass
class SkewInfo:
    """Information about detected data skew."""
    partition_id: int
    record_count: int
    percentage: float
    is_skewed: bool


class SkewDetector:
    """
    Detect data skew in DataFrames and partitions.
    
    Data skew occurs when data is unevenly distributed across partitions,
    causing some tasks to process significantly more data than others.
    
    Best Practices:
        - Partition size variance should be < 3x
        - Max partition should be < 200MB for optimal performance
        - Use salting for heavily skewed keys
        - Enable AQE skew join optimization
    """
    
    # Skew threshold: partition > 3x median size
    SKEW_THRESHOLD = 3.0
    
    def __init__(self, spark: SparkSession):
        """Initialize skew detector."""
        self.spark = spark
        self.logger = logging.getLogger(__name__)
    
    def detect_skew(self, df: DataFrame, sample_fraction: float = 0.1) -> Tuple[bool, List[SkewInfo]]:
        """
        Detect data skew in DataFrame partitions.
        
        Args:
            df: DataFrame to analyze
            sample_fraction: Fraction of data to sample (0.1 = 10%)
            
        Returns:
            Tuple of (has_skew: bool, skew_info: List[SkewInfo])
            
        Example:
            detector = SkewDetector(spark)
            has_skew, info = detector.detect_skew(df)
            if has_skew:
                print("Data skew detected!")
                detector.print_skew_analysis(info)
        """
        try:
            # Count records per partition
            partition_counts = (
                df.sample(sample_fraction)
                .withColumn("partition_id", spark_partition_id())
                .groupBy("partition_id")
                .count()
                .collect()
            )
            
            if not partition_counts:
                return False, []
            
            # Calculate statistics
            counts = [row['count'] for row in partition_counts]
            total_records = sum(counts)
            avg_count = total_records / len(counts)
            max_count = max(counts)
            
            # Detect skew: max partition > 3x average
            has_skew = max_count > (avg_count * self.SKEW_THRESHOLD)
            
            # Build skew info
            skew_info = []
            for row in partition_counts:
                part_id = row['partition_id']
                part_count = row['count']
                percentage = (part_count / total_records * 100) if total_records > 0 else 0
                is_skewed = part_count > (avg_count * self.SKEW_THRESHOLD)
                
                skew_info.append(SkewInfo(
                    partition_id=part_id,
                    record_count=part_count,
                    percentage=percentage,
                    is_skewed=is_skewed
                ))
            
            return has_skew, skew_info
            
        except Exception as e:
            self.logger.error(f"Failed to detect skew: {e}")
            return False, []
    
    def suggest_skew_solutions(self, df: DataFrame, skew_column: Optional[str] = None) -> List[str]:
        """
        Suggest solutions for data skew.
        
        Args:
            df: DataFrame with skew
            skew_column: Column causing skew (if known)
            
        Returns:
            List of recommendations
        """
        recommendations = [
            "1. Use salting technique to distribute skewed keys:",
            "   - Add random salt prefix to skewed keys",
            "   - Example: df.withColumn('salted_key', concat(col('key'), lit('_'), (rand() * 10).cast('int')))",
            "",
            "2. Enable Adaptive Query Execution (AQE) with skew join optimization:",
            "   - spark.conf.set('spark.sql.adaptive.enabled', 'true')",
            "   - spark.conf.set('spark.sql.adaptive.skewJoin.enabled', 'true')",
            "",
            "3. Increase partition count to redistribute data:",
            "   - df.repartition(N) or df.repartition('key_column')",
            "",
            "4. Use broadcast join for small tables to avoid shuffle:",
            "   - large_df.join(broadcast(small_df), 'key')",
            "",
            "5. Filter out or handle null values separately if causing skew:",
            "   - Process nulls in separate DataFrame and union results"
        ]
        
        return recommendations
    
    def print_skew_analysis(self, skew_info: List[SkewInfo]) -> None:
        """Print skew analysis results."""
        if not skew_info:
            print("\nNo skew information available.\n")
            return
        
        print("\n" + "="*80)
        print("DATA SKEW ANALYSIS")
        print("="*80)
        
        total_records = sum(info.record_count for info in skew_info)
        avg_records = total_records / len(skew_info)
        
        print(f"\nTotal partitions: {len(skew_info)}")
        print(f"Total records: {total_records:,}")
        print(f"Average records per partition: {avg_records:,.0f}")
        
        # Show skewed partitions
        skewed = [info for info in skew_info if info.is_skewed]
        if skewed:
            print(f"\n🔴 Skewed partitions detected: {len(skewed)}")
            print("\nTop skewed partitions:")
            for info in sorted(skewed, key=lambda x: x.record_count, reverse=True)[:5]:
                ratio = info.record_count / avg_records
                print(f"  Partition {info.partition_id}: {info.record_count:,} records ({info.percentage:.1f}%, {ratio:.1f}x average)")
        else:
            print("\n✅ No significant skew detected!")
        
        print("="*80 + "\n")
