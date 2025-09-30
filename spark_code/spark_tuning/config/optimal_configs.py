"""
Optimal Configs

Pre-defined optimal configurations for common scenarios.
"""

from typing import Dict


class OptimalConfigs:
    """
    Pre-defined optimal Spark configurations for common scenarios.
    
    Based on Apache Spark 3.5+ best practices and real-world production experience.
    """
    
    @staticmethod
    def get_small_cluster_config() -> Dict[str, str]:
        """
        Configuration for small clusters (< 10 nodes, < 100GB data).
        
        Use case: Development, testing, small production workloads
        """
        return {
            "spark.executor.instances": "4",
            "spark.executor.cores": "4",
            "spark.executor.memory": "4g",
            "spark.executor.memoryOverhead": "512m",
            "spark.driver.memory": "2g",
            "spark.sql.shuffle.partitions": "100",
            "spark.default.parallelism": "16",
            "spark.sql.adaptive.enabled": "true",
            "spark.sql.adaptive.coalescePartitions.enabled": "true",
        }
    
    @staticmethod
    def get_large_cluster_config() -> Dict[str, str]:
        """
        Configuration for large clusters (> 50 nodes, > 1TB data).
        
        Use case: Large-scale data processing, ETL pipelines
        """
        return {
            "spark.executor.instances": "50",
            "spark.executor.cores": "5",
            "spark.executor.memory": "10g",
            "spark.executor.memoryOverhead": "2g",
            "spark.driver.memory": "8g",
            "spark.driver.memoryOverhead": "1g",
            "spark.sql.shuffle.partitions": "2000",
            "spark.default.parallelism": "250",
            "spark.sql.adaptive.enabled": "true",
            "spark.sql.adaptive.coalescePartitions.enabled": "true",
            "spark.sql.adaptive.skewJoin.enabled": "true",
            "spark.dynamicAllocation.enabled": "true",
            "spark.dynamicAllocation.minExecutors": "10",
            "spark.dynamicAllocation.maxExecutors": "100",
        }
    
    @staticmethod
    def get_streaming_config() -> Dict[str, str]:
        """
        Configuration for Spark Streaming workloads.
        
        Use case: Real-time processing, low-latency requirements
        """
        return {
            "spark.streaming.backpressure.enabled": "true",
            "spark.streaming.kafka.maxRatePerPartition": "1000",
            "spark.streaming.stopGracefullyOnShutdown": "true",
            "spark.sql.adaptive.enabled": "false",  # Not recommended for streaming
            "spark.executor.cores": "4",
            "spark.executor.memory": "6g",
            "spark.memory.fraction": "0.7",
            "spark.memory.storageFraction": "0.3",
        }
    
    @staticmethod
    def get_ml_config() -> Dict[str, str]:
        """
        Configuration for Machine Learning workloads.
        
        Use case: MLlib, model training, feature engineering
        """
        return {
            "spark.executor.cores": "8",
            "spark.executor.memory": "16g",
            "spark.executor.memoryOverhead": "3g",
            "spark.driver.memory": "16g",
            "spark.memory.fraction": "0.8",
            "spark.memory.storageFraction": "0.5",
            "spark.serializer": "org.apache.spark.serializer.KryoSerializer",
            "spark.kryoserializer.buffer.max": "1024m",
            "spark.sql.execution.arrow.pyspark.enabled": "true",
            "spark.python.worker.memory": "2g",
        }
    
    @staticmethod
    def get_k8s_config() -> Dict[str, str]:
        """
        Configuration for Kubernetes deployments.
        
        Use case: Running Spark on Kubernetes clusters
        """
        return {
            "spark.kubernetes.namespace": "spark",
            "spark.kubernetes.authenticate.driver.serviceAccountName": "spark",
            "spark.kubernetes.container.image.pullPolicy": "IfNotPresent",
            "spark.kubernetes.executor.deleteOnTermination": "true",
            "spark.kubernetes.allocation.batch.size": "10",
            "spark.dynamicAllocation.enabled": "true",
            "spark.dynamicAllocation.shuffleTracking.enabled": "true",
            "spark.executor.cores": "4",
            "spark.executor.memory": "6g",
            "spark.executor.memoryOverhead": "1g",
            "spark.kubernetes.executor.request.cores": "2",
            "spark.kubernetes.executor.limit.cores": "4",
        }
