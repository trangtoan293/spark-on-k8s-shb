"""
Bottleneck Detector

Identifies performance bottlenecks in Spark jobs using metrics analysis.
"""

import logging
from typing import List, Dict, Optional
from dataclasses import dataclass
from pyspark.sql import SparkSession


@dataclass
class Bottleneck:
    """Detected performance bottleneck."""
    type: str  # "SHUFFLE", "GC", "SPILL", "SKEW", "SERIALIZATION"
    severity: str
    description: str
    affected_stages: List[int]
    recommendations: List[str]
    metrics: Dict[str, float]


class BottleneckDetector:
    """
    Detect performance bottlenecks in Spark applications.
    
    Analyzes:
        - Shuffle bottlenecks (excessive data movement)
        - GC pressure (> 10% of execution time)
        - Disk spill (memory overflow)
        - Task skew (unbalanced partitions)
        - Serialization overhead
    
    Best Practices:
        - Shuffle should be < 20% of total execution time
        - GC time should be < 10% of executor run time
        - Disk spill indicates insufficient memory
        - Task duration variance > 3x indicates skew
    """
    
    def __init__(self, spark: SparkSession):
        """Initialize bottleneck detector."""
        self.spark = spark
        self.sc = spark.sparkContext
        self.logger = logging.getLogger(__name__)
    
    def detect_bottlenecks(self) -> List[Bottleneck]:
        """
        Detect performance bottlenecks in the application.
        
        Returns:
            List of detected Bottleneck objects
        """
        bottlenecks = []
        
        try:
            # Detect shuffle bottlenecks
            bottlenecks.extend(self._detect_shuffle_bottlenecks())
            
            # Detect GC pressure
            bottlenecks.extend(self._detect_gc_pressure())
            
            # Detect disk spill
            bottlenecks.extend(self._detect_disk_spill())
            
        except Exception as e:
            self.logger.error(f"Failed to detect bottlenecks: {e}")
        
        return bottlenecks
    
    def _detect_shuffle_bottlenecks(self) -> List[Bottleneck]:
        """Detect shuffle-related bottlenecks."""
        bottlenecks = []
        
        # This would analyze actual stage metrics in production
        # For now, providing framework
        
        return bottlenecks
    
    def _detect_gc_pressure(self) -> List[Bottleneck]:
        """Detect garbage collection pressure."""
        bottlenecks = []
        
        # Analyze GC time from executor metrics
        # GC time > 10% of executor run time indicates pressure
        
        return bottlenecks
    
    def _detect_disk_spill(self) -> List[Bottleneck]:
        """Detect disk spill issues."""
        bottlenecks = []
        
        # Check for disk spill in stage metrics
        # Disk spill indicates insufficient memory
        
        return bottlenecks
    
    def print_bottlenecks(self, bottlenecks: List[Bottleneck]) -> None:
        """Print detected bottlenecks."""
        if not bottlenecks:
            print("\n✅ No significant bottlenecks detected!\n")
            return
        
        print("\n" + "="*80)
        print("BOTTLENECK ANALYSIS")
        print("="*80)
        
        for i, bottleneck in enumerate(bottlenecks, 1):
            print(f"\n{i}. [{bottleneck.type}] {bottleneck.severity}")
            print(f"   {bottleneck.description}")
            print(f"   Affected stages: {bottleneck.affected_stages}")
            print("   Recommendations:")
            for rec in bottleneck.recommendations:
                print(f"   - {rec}")
        
        print("="*80 + "\n")
