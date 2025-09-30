"""
Config Generator

Generates optimal Spark configurations based on cluster resources and workload characteristics.
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from pyspark.sql import SparkSession


@dataclass
class ClusterResources:
    """Cluster resource specifications."""
    num_executors: int
    cores_per_executor: int
    memory_per_executor_gb: int
    total_cores: int
    total_memory_gb: int


@dataclass
class WorkloadProfile:
    """Workload characteristics."""
    type: str  # "streaming", "batch", "ml", "sql"
    data_size_gb: float
    has_shuffles: bool
    has_caching: bool
    has_joins: bool
    expected_duration_minutes: int


class ConfigGenerator:
    """
    Generate optimal Spark configurations for different scenarios.
    
    Considers:
        - Cluster resources (cores, memory)
        - Workload type (streaming, batch, ML, SQL)
        - Data characteristics (size, partitions)
        - Performance goals (throughput, latency)
    
    Best Practices Applied:
        - Executor sizing: 4-8GB, 4-6 cores per executor
        - Dynamic allocation for variable workloads
        - AQE for SQL workloads
        - Tuned shuffle partitions based on data size
        - Appropriate memory fractions for workload type
    """
    
    # Optimal executor configurations
    OPTIMAL_EXECUTOR_CORES = 5
    OPTIMAL_EXECUTOR_MEMORY_GB = 6
    MEMORY_OVERHEAD_FRACTION = 0.10
    
    def __init__(self, spark: Optional[SparkSession] = None):
        """Initialize config generator."""
        self.spark = spark
        self.logger = logging.getLogger(__name__)
    
    def generate_configs(
        self,
        cluster: ClusterResources,
        workload: WorkloadProfile
    ) -> Dict[str, str]:
        """
        Generate optimal Spark configurations.
        
        Args:
            cluster: Cluster resource specifications
            workload: Workload characteristics
            
        Returns:
            Dictionary of Spark configuration key-value pairs
            
        Example:
            cluster = ClusterResources(
                num_executors=10,
                cores_per_executor=4,
                memory_per_executor_gb=8,
                total_cores=40,
                total_memory_gb=80
            )
            workload = WorkloadProfile(
                type="batch",
                data_size_gb=100,
                has_shuffles=True,
                has_caching=True,
                has_joins=True,
                expected_duration_minutes=30
            )
            configs = generator.generate_configs(cluster, workload)
        """
        configs = {}
        
        # Base configurations
        configs.update(self._generate_base_configs())
        
        # Executor configurations
        configs.update(self._generate_executor_configs(cluster))
        
        # Memory configurations
        configs.update(self._generate_memory_configs(workload))
        
        # Shuffle configurations
        if workload.has_shuffles:
            configs.update(self._generate_shuffle_configs(cluster, workload))
        
        # SQL configurations
        if workload.type in ["batch", "sql"]:
            configs.update(self._generate_sql_configs(workload))
        
        # Caching configurations
        if workload.has_caching:
            configs.update(self._generate_cache_configs())
        
        # Dynamic allocation
        configs.update(self._generate_dynamic_allocation_configs(cluster))
        
        return configs
    
    def _generate_base_configs(self) -> Dict[str, str]:
        """Generate base Spark configurations."""
        return {
            # Serialization (Kryo is faster)
            "spark.serializer": "org.apache.spark.serializer.KryoSerializer",
            "spark.kryoserializer.buffer.max": "512m",
            
            # Network
            "spark.network.timeout": "800s",
            "spark.executor.heartbeatInterval": "60s",
            
            # Speculation (retry slow tasks)
            "spark.speculation": "true",
            "spark.speculation.multiplier": "3",
            "spark.speculation.quantile": "0.9",
            
            # Task retries
            "spark.task.maxFailures": "4",
        }
    
    def _generate_executor_configs(self, cluster: ClusterResources) -> Dict[str, str]:
        """Generate executor-related configurations."""
        # Calculate optimal number of executors
        # Leave 1 core for driver and OS
        available_cores = cluster.total_cores - 1
        num_executors = available_cores // self.OPTIMAL_EXECUTOR_CORES
        
        executor_memory = min(
            cluster.memory_per_executor_gb,
            self.OPTIMAL_EXECUTOR_MEMORY_GB
        )
        
        memory_overhead = max(
            int(executor_memory * self.MEMORY_OVERHEAD_FRACTION),
            384  # Minimum 384MB
        )
        
        return {
            "spark.executor.instances": str(num_executors),
            "spark.executor.cores": str(self.OPTIMAL_EXECUTOR_CORES),
            "spark.executor.memory": f"{executor_memory}g",
            "spark.executor.memoryOverhead": f"{memory_overhead}m",
            "spark.driver.memory": "4g",
            "spark.driver.memoryOverhead": "512m",
        }
    
    def _generate_memory_configs(self, workload: WorkloadProfile) -> Dict[str, str]:
        """Generate memory-related configurations."""
        # Adjust storage fraction based on workload
        if workload.has_caching:
            storage_fraction = "0.6"  # More storage for cached data
        else:
            storage_fraction = "0.4"  # More execution memory
        
        return {
            "spark.memory.fraction": "0.6",
            "spark.memory.storageFraction": storage_fraction,
            "spark.memory.offHeap.enabled": "false",  # Use on-heap by default
        }
    
    def _generate_shuffle_configs(
        self,
        cluster: ClusterResources,
        workload: WorkloadProfile
    ) -> Dict[str, str]:
        """Generate shuffle-related configurations."""
        # Calculate optimal shuffle partitions
        # Rule: ~128MB per partition
        data_size_mb = workload.data_size_gb * 1024
        shuffle_partitions = max(
            int(data_size_mb / 128),
            cluster.total_cores * 2,  # At least 2x cores
            200  # Minimum 200
        )
        
        return {
            "spark.sql.shuffle.partitions": str(shuffle_partitions),
            "spark.shuffle.compress": "true",
            "spark.shuffle.spill.compress": "true",
            "spark.shuffle.file.buffer": "64k",
            "spark.reducer.maxSizeInFlight": "96m",
            "spark.shuffle.io.maxRetries": "5",
            "spark.shuffle.io.retryWait": "30s",
        }
    
    def _generate_sql_configs(self, workload: WorkloadProfile) -> Dict[str, str]:
        """Generate SQL-related configurations."""
        configs = {
            # Adaptive Query Execution (AQE)
            "spark.sql.adaptive.enabled": "true",
            "spark.sql.adaptive.coalescePartitions.enabled": "true",
            "spark.sql.adaptive.skewJoin.enabled": "true",
            "spark.sql.adaptive.localShuffleReader.enabled": "true",
            
            # Broadcast join threshold
            "spark.sql.autoBroadcastJoinThreshold": "10485760",  # 10MB
            
            # Parquet optimizations
            "spark.sql.parquet.filterPushdown": "true",
            "spark.sql.parquet.mergeSchema": "false",
            "spark.hadoop.parquet.enable.summary-metadata": "false",
        }
        
        if workload.has_joins:
            configs.update({
                # Join optimizations
                "spark.sql.adaptive.advisoryPartitionSizeInBytes": "64m",
                "spark.sql.adaptive.skewJoin.skewedPartitionFactor": "5",
                "spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes": "256m",
            })
        
        return configs
    
    def _generate_cache_configs(self) -> Dict[str, str]:
        """Generate caching-related configurations."""
        return {
            "spark.sql.inMemoryColumnarStorage.compressed": "true",
            "spark.sql.inMemoryColumnarStorage.batchSize": "10000",
        }
    
    def _generate_dynamic_allocation_configs(self, cluster: ClusterResources) -> Dict[str, str]:
        """Generate dynamic allocation configurations."""
        max_executors = cluster.num_executors
        min_executors = max(1, max_executors // 4)  # 25% of max
        
        return {
            "spark.dynamicAllocation.enabled": "true",
            "spark.dynamicAllocation.minExecutors": str(min_executors),
            "spark.dynamicAllocation.maxExecutors": str(max_executors),
            "spark.dynamicAllocation.initialExecutors": str(min_executors),
            "spark.dynamicAllocation.executorIdleTimeout": "60s",
            "spark.dynamicAllocation.schedulerBacklogTimeout": "1s",
        }
    
    def generate_k8s_configs(self, namespace: str = "spark") -> Dict[str, str]:
        """
        Generate Kubernetes-specific Spark configurations.
        
        Args:
            namespace: Kubernetes namespace
            
        Returns:
            Dictionary of K8s-specific configurations
        """
        return {
            "spark.kubernetes.namespace": namespace,
            "spark.kubernetes.authenticate.driver.serviceAccountName": "spark",
            "spark.kubernetes.container.image.pullPolicy": "IfNotPresent",
            "spark.kubernetes.executor.deleteOnTermination": "true",
            "spark.kubernetes.executor.podNamePrefix": "spark-exec",
            "spark.kubernetes.allocation.batch.size": "5",
            
            # Resource requests/limits
            "spark.kubernetes.executor.request.cores": "1",
            "spark.kubernetes.executor.limit.cores": str(self.OPTIMAL_EXECUTOR_CORES),
            
            # Pod templates for advanced configs
            "spark.kubernetes.driver.label.spark-role": "driver",
            "spark.kubernetes.executor.label.spark-role": "executor",
        }
    
    def print_configs(self, configs: Dict[str, str]) -> None:
        """Print configurations in a readable format."""
        print("\n" + "="*80)
        print("RECOMMENDED SPARK CONFIGURATIONS")
        print("="*80)
        
        # Group by category
        categories = {
            "Executor": ["spark.executor.", "spark.driver."],
            "Memory": ["spark.memory.", "spark.sql.inMemory"],
            "Shuffle": ["spark.shuffle.", "spark.reducer."],
            "SQL": ["spark.sql."],
            "Dynamic Allocation": ["spark.dynamicAllocation."],
            "Kubernetes": ["spark.kubernetes."],
            "Other": []
        }
        
        for category, prefixes in categories.items():
            category_configs = {}
            for key, value in configs.items():
                if prefixes:
                    if any(key.startswith(p) for p in prefixes):
                        category_configs[key] = value
                else:
                    # "Other" category gets remaining configs
                    if not any(key.startswith(p) for cat_prefixes in categories.values() 
                              if cat_prefixes for p in cat_prefixes):
                        category_configs[key] = value
            
            if category_configs:
                print(f"\n{category}:")
                for key, value in sorted(category_configs.items()):
                    print(f"  {key} = {value}")
        
        print("\n" + "="*80)
        print("Apply these configs using:")
        print("  spark-submit --conf key=value ...")
        print("  or in SparkSession.builder.config(key, value)")
        print("="*80 + "\n")
