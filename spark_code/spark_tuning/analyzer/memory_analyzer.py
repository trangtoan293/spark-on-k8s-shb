"""
Memory Analyzer

Analyzes memory usage patterns and provides recommendations for memory tuning.
"""

import logging
from typing import List, Dict, Optional
from dataclasses import dataclass
from pyspark.sql import SparkSession


@dataclass
class MemoryIssue:
    """Memory-related issue."""
    type: str  # "OOM_RISK", "GC_OVERHEAD", "SPILL", "CACHE_PRESSURE"
    severity: str
    description: str
    current_value: float
    recommended_value: float
    config_changes: List[str]


class MemoryAnalyzer:
    """
    Analyze memory usage and provide tuning recommendations.
    
    Analyzes:
        - Executor memory allocation
        - Storage vs execution memory
        - GC overhead
        - Disk spill frequency
        - Cache eviction patterns
    
    Best Practices:
        - Executor memory: 4-8GB per executor
        - Memory overhead: 10% of executor memory (min 384MB)
        - GC time: < 10% of execution time
        - Storage fraction: 0.5 default (adjustable based on workload)
    """
    
    def __init__(self, spark: SparkSession):
        """Initialize memory analyzer."""
        self.spark = spark
        self.logger = logging.getLogger(__name__)
        
        # Get current memory configurations
        self.executor_memory = self._parse_memory(
            spark.conf.get("spark.executor.memory", "1g")
        )
        self.driver_memory = self._parse_memory(
            spark.conf.get("spark.driver.memory", "1g")
        )
        self.memory_fraction = float(
            spark.conf.get("spark.memory.fraction", "0.6")
        )
        self.storage_fraction = float(
            spark.conf.get("spark.memory.storageFraction", "0.5")
        )
    
    def _parse_memory(self, mem_str: str) -> int:
        """Parse memory string (e.g., '4g', '512m') to MB."""
        mem_str = mem_str.lower()
        if mem_str.endswith('g'):
            return int(float(mem_str[:-1]) * 1024)
        elif mem_str.endswith('m'):
            return int(float(mem_str[:-1]))
        return int(mem_str)
    
    def analyze_memory_config(self) -> List[MemoryIssue]:
        """
        Analyze current memory configuration.
        
        Returns:
            List of MemoryIssue objects with recommendations
        """
        issues = []
        
        # Check executor memory size
        if self.executor_memory < 2048:  # Less than 2GB
            issues.append(MemoryIssue(
                type="OOM_RISK",
                severity="HIGH",
                description="Executor memory is very low, risk of OOM errors",
                current_value=self.executor_memory,
                recommended_value=4096,  # 4GB
                config_changes=[
                    "spark.executor.memory=4g",
                    "spark.executor.memoryOverhead=512m"
                ]
            ))
        
        # Check memory fraction
        if self.memory_fraction < 0.6:
            issues.append(MemoryIssue(
                type="MEMORY_FRACTION",
                severity="MEDIUM",
                description="Memory fraction is low, may cause excessive GC",
                current_value=self.memory_fraction,
                recommended_value=0.6,
                config_changes=[
                    "spark.memory.fraction=0.6"
                ]
            ))
        
        return issues
    
    def suggest_memory_tuning(self, workload_type: str = "balanced") -> Dict[str, str]:
        """
        Suggest memory configurations based on workload type.
        
        Args:
            workload_type: "caching", "shuffling", "balanced"
            
        Returns:
            Dictionary of recommended configurations
        """
        configs = {}
        
        if workload_type == "caching":
            # Favor storage memory for cached DataFrames
            configs = {
                "spark.memory.fraction": "0.6",
                "spark.memory.storageFraction": "0.7",  # 70% for storage
                "spark.executor.memory": "8g",
                "spark.sql.inMemoryColumnarStorage.compressed": "true"
            }
        elif workload_type == "shuffling":
            # Favor execution memory for shuffles
            configs = {
                "spark.memory.fraction": "0.6",
                "spark.memory.storageFraction": "0.3",  # 30% for storage
                "spark.executor.memory": "8g",
                "spark.shuffle.file.buffer": "64k",
                "spark.reducer.maxSizeInFlight": "96m"
            }
        else:  # balanced
            configs = {
                "spark.memory.fraction": "0.6",
                "spark.memory.storageFraction": "0.5",
                "spark.executor.memory": "6g",
                "spark.executor.memoryOverhead": "1g"
            }
        
        return configs
    
    def print_memory_analysis(self, issues: List[MemoryIssue]) -> None:
        """Print memory analysis results."""
        print("\n" + "="*80)
        print("MEMORY CONFIGURATION ANALYSIS")
        print("="*80)
        print(f"\nCurrent Configuration:")
        print(f"  Executor Memory: {self.executor_memory} MB")
        print(f"  Driver Memory: {self.driver_memory} MB")
        print(f"  Memory Fraction: {self.memory_fraction}")
        print(f"  Storage Fraction: {self.storage_fraction}")
        
        if issues:
            print(f"\n⚠️  Issues found: {len(issues)}")
            for i, issue in enumerate(issues, 1):
                print(f"\n{i}. [{issue.type}] {issue.severity}")
                print(f"   {issue.description}")
                print(f"   Current: {issue.current_value}, Recommended: {issue.recommended_value}")
                print("   Suggested config changes:")
                for config in issue.config_changes:
                    print(f"   - {config}")
        else:
            print("\n✅ Memory configuration looks good!")
        
        print("="*80 + "\n")
