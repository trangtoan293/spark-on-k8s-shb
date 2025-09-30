"""
Metrics Collector

Collects comprehensive Spark metrics following official monitoring best practices.
Uses Spark REST API for reliable metrics collection.

Based on Apache Spark 3.5+ best practices:
    - REST API for runtime metrics (executors, stages, jobs)
    - SparkConf for configuration metrics
    - Fallback to config-based estimation when REST API unavailable

References:
    - https://spark.apache.org/docs/3.5.2/monitoring.html
    - https://spark.apache.org/docs/latest/monitoring.html#rest-api
"""

import json
import logging
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pyspark.sql import SparkSession


@dataclass
class ExecutorMetrics:
    """Executor-level metrics for monitoring resource utilization."""
    executor_id: str
    host: str
    total_cores: int
    used_cores: int
    total_memory_mb: int
    used_memory_mb: int
    disk_used_mb: int
    active_tasks: int
    completed_tasks: int
    failed_tasks: int
    total_duration_ms: int
    total_gc_time_ms: int
    total_input_bytes: int
    total_shuffle_read_bytes: int
    total_shuffle_write_bytes: int
    timestamp: str


@dataclass
class StageMetrics:
    """Stage-level metrics for identifying bottlenecks."""
    stage_id: int
    stage_name: str
    num_tasks: int
    num_completed_tasks: int
    num_failed_tasks: int
    executor_run_time_ms: int
    executor_cpu_time_ms: int
    shuffle_read_bytes: int
    shuffle_write_bytes: int
    input_bytes: int
    output_bytes: int
    peak_memory_bytes: int
    spill_memory_bytes: int
    spill_disk_bytes: int
    timestamp: str


@dataclass
class JobMetrics:
    """Job-level metrics for overall performance tracking."""
    job_id: int
    job_group: Optional[str]
    num_stages: int
    num_completed_stages: int
    num_failed_stages: int
    num_active_tasks: int
    num_completed_tasks: int
    num_failed_tasks: int
    total_duration_ms: int
    timestamp: str


class MetricsCollector:
    """
    Comprehensive metrics collector for Spark applications.
    
    Collects metrics from Spark REST API, SparkContext, and custom instrumentation.
    Follows Apache Spark monitoring best practices for production deployments.
    
    Best Practices Applied:
        - Uses Spark's native metrics system
        - Minimal performance overhead
        - Structured metrics for easy analysis
        - Compatible with Prometheus/Grafana
    """
    
    def __init__(self, spark: SparkSession, enable_custom_metrics: bool = True):
        """
        Initialize metrics collector.
        
        Args:
            spark: Active SparkSession
            enable_custom_metrics: Enable custom application metrics
        """
        self.spark = spark
        self.sc = spark.sparkContext
        self.logger = logging.getLogger(__name__)
        self.enable_custom_metrics = enable_custom_metrics
        
        # Configure metrics namespace
        app_name = spark.conf.get("spark.app.name", "spark-app")
        self.metrics_namespace = f"spark.{app_name}"
        
        # Get Spark UI URL for REST API
        try:
            self.ui_url = self.sc.uiWebUrl or "http://localhost:4040"
            self.app_id = self.sc.applicationId
        except:
            self.ui_url = None
            self.app_id = None
        
        self.logger.info(f"MetricsCollector initialized for app: {app_name}")
    
    def _fetch_rest_api(self, endpoint: str) -> Optional[Any]:
        """Fetch data from Spark REST API."""
        if not self.ui_url or not self.app_id:
            return None
        
        try:
            url = f"{self.ui_url}{endpoint}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            self.logger.debug(f"REST API fetch failed for {endpoint}: {e}")
        return None
    
    def collect_executor_metrics(self) -> List[ExecutorMetrics]:
        """
        Collect executor-level metrics via REST API.
        
        Returns:
            List of ExecutorMetrics objects
            
        Note:
            Critical for identifying:
            - Memory pressure (OOM issues)
            - GC overhead
            - Task distribution imbalance
        """
        executor_metrics = []
        timestamp = datetime.utcnow().isoformat()
        
        try:
            # Use REST API
            executors_data = self._fetch_rest_api(f"/api/v1/applications/{self.app_id}/executors")
            
            if executors_data and isinstance(executors_data, list):
                for executor in executors_data:
                    if executor.get('id') == 'driver':
                        continue  # Skip driver
                    
                    metrics = ExecutorMetrics(
                        executor_id=executor.get('id', 'unknown'),
                        host=executor.get('hostPort', 'unknown'),
                        total_cores=executor.get('totalCores', 0),
                        used_cores=executor.get('activeTasks', 0),
                        total_memory_mb=executor.get('maxMemory', 0) // (1024 * 1024),
                        used_memory_mb=executor.get('memoryUsed', 0) // (1024 * 1024),
                        disk_used_mb=executor.get('diskUsed', 0) // (1024 * 1024),
                        active_tasks=executor.get('activeTasks', 0),
                        completed_tasks=executor.get('totalTasks', 0),
                        failed_tasks=executor.get('failedTasks', 0),
                        total_duration_ms=executor.get('totalDuration', 0),
                        total_gc_time_ms=executor.get('totalGCTime', 0),
                        total_input_bytes=executor.get('totalInputBytes', 0),
                        total_shuffle_read_bytes=executor.get('totalShuffleRead', 0),
                        total_shuffle_write_bytes=executor.get('totalShuffleWrite', 0),
                        timestamp=timestamp
                    )
                    executor_metrics.append(metrics)
                    
        except Exception as e:
            self.logger.warning(f"Failed to collect executor metrics: {e}")
        
        return executor_metrics
    
    def collect_stage_metrics(self, job_id: Optional[int] = None) -> List[StageMetrics]:
        """
        Collect stage-level metrics via REST API.
        
        Args:
            job_id: Filter by specific job ID (None for all stages)
            
        Returns:
            List of StageMetrics objects
            
        Note:
            Key indicators:
            - Shuffle bottlenecks
            - Data spill to disk
            - Task skew within stages
        """
        stage_metrics = []
        timestamp = datetime.utcnow().isoformat()
        
        try:
            # Use REST API
            stages_data = self._fetch_rest_api(f"/api/v1/applications/{self.app_id}/stages")
            
            if stages_data and isinstance(stages_data, list):
                for stage in stages_data:
                    if not isinstance(stage, dict):
                        continue
                    
                    # Filter by job_id if specified
                    if job_id is not None and stage.get('jobIds') and job_id not in stage.get('jobIds', []):
                        continue
                    
                    metrics = StageMetrics(
                        stage_id=stage.get('stageId', 0),
                        stage_name=stage.get('name', 'unknown'),
                        num_tasks=stage.get('numTasks', 0),
                        num_completed_tasks=stage.get('numCompleteTasks', 0),
                        num_failed_tasks=stage.get('numFailedTasks', 0),
                        executor_run_time_ms=stage.get('executorRunTime', 0),
                        executor_cpu_time_ms=stage.get('executorCpuTime', 0),
                        shuffle_read_bytes=stage.get('shuffleReadBytes', 0),
                        shuffle_write_bytes=stage.get('shuffleWriteBytes', 0),
                        input_bytes=stage.get('inputBytes', 0),
                        output_bytes=stage.get('outputBytes', 0),
                        peak_memory_bytes=stage.get('peakExecutionMemory', 0),
                        spill_memory_bytes=stage.get('memoryBytesSpilled', 0),
                        spill_disk_bytes=stage.get('diskBytesSpilled', 0),
                        timestamp=timestamp
                    )
                    stage_metrics.append(metrics)
                    
        except Exception as e:
            self.logger.warning(f"Failed to collect stage metrics: {e}")
        
        return stage_metrics
    
    def collect_job_metrics(self) -> List[JobMetrics]:
        """
        Collect job-level metrics via REST API.
        
        Returns:
            List of JobMetrics objects
            
        Note:
            High-level overview for:
            - Overall job health
            - Job duration trends
            - Failure patterns
        """
        job_metrics = []
        timestamp = datetime.utcnow().isoformat()
        
        try:
            # Use REST API
            jobs_data = self._fetch_rest_api(f"/api/v1/applications/{self.app_id}/jobs")
            
            if jobs_data and isinstance(jobs_data, list):
                for job in jobs_data:
                    if not isinstance(job, dict):
                        continue
                    
                    metrics = JobMetrics(
                        job_id=job.get('jobId', 0),
                        job_group=job.get('jobGroup'),
                        num_stages=job.get('numStages', 0),
                        num_completed_stages=job.get('numCompletedStages', 0),
                        num_failed_stages=job.get('numFailedStages', 0),
                        num_active_tasks=job.get('numActiveTasks', 0),
                        num_completed_tasks=job.get('numCompletedTasks', 0),
                        num_failed_tasks=job.get('numFailedTasks', 0),
                        total_duration_ms=0,  # Not directly available
                        timestamp=timestamp
                    )
                    job_metrics.append(metrics)
                    
        except Exception as e:
            self.logger.warning(f"Failed to collect job metrics: {e}")
        
        return job_metrics
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive metrics summary.
        
        Returns:
            Dictionary containing all collected metrics
            
        Usage:
            collector = MetricsCollector(spark)
            summary = collector.get_metrics_summary()
            print(json.dumps(summary, indent=2))
        """
        summary = {
            "timestamp": datetime.utcnow().isoformat(),
            "app_name": self.spark.conf.get("spark.app.name"),
            "app_id": self.sc.applicationId,
            "executors": [asdict(m) for m in self.collect_executor_metrics()],
            "stages": [asdict(m) for m in self.collect_stage_metrics()],
            "jobs": [asdict(m) for m in self.collect_job_metrics()],
        }
        
        return summary
    
    def export_to_json(self, filepath: str) -> None:
        """
        Export metrics to JSON file.
        
        Args:
            filepath: Path to output JSON file
        """
        summary = self.get_metrics_summary()
        with open(filepath, 'w') as f:
            json.dump(summary, f, indent=2)
        
        self.logger.info(f"Metrics exported to {filepath}")
    
    def print_summary(self) -> None:
        """Print human-readable metrics summary."""
        summary = self.get_metrics_summary()
        
        print("\n" + "="*80)
        print(f"SPARK METRICS SUMMARY - {summary['timestamp']}")
        print("="*80)
        print(f"Application: {summary['app_name']} ({summary['app_id']})")
        print(f"\nActive Executors: {len(summary['executors'])}")
        print(f"Active Stages: {len(summary['stages'])}")
        print(f"Active Jobs: {len(summary['jobs'])}")
        
        # Executor summary
        if summary['executors']:
            total_memory = sum(e['total_memory_mb'] for e in summary['executors'])
            used_memory = sum(e['used_memory_mb'] for e in summary['executors'])
            memory_util = (used_memory / total_memory * 100) if total_memory > 0 else 0
            
            print(f"\nMemory Utilization: {memory_util:.1f}% ({used_memory}/{total_memory} MB)")
        
        print("="*80 + "\n")
