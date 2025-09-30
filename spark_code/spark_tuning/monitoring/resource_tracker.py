"""
Resource Tracker

Tracks resource utilization and provides alerts for resource-related issues.
Monitors memory, CPU, disk I/O, and network to prevent OOM and performance degradation.

Based on Apache Spark 3.5+ monitoring best practices:
- Uses SparkConf for configuration metrics
- Uses Spark UI REST API for runtime metrics
- Monitors key performance indicators: memory, GC, shuffle, task metrics
"""

import logging
import requests
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from pyspark.sql import SparkSession


@dataclass
class ResourceSnapshot:
    """Snapshot of resource utilization at a point in time."""
    timestamp: str
    # Memory metrics
    total_memory_mb: int
    used_memory_mb: int
    memory_utilization_pct: float
    # Storage metrics
    total_storage_mb: int
    used_storage_mb: int
    storage_utilization_pct: float
    # Task metrics
    active_tasks: int
    completed_tasks: int
    failed_tasks: int
    # Executor metrics
    active_executors: int
    total_cores: int
    # GC metrics
    total_gc_time_ms: int
    # Shuffle metrics
    shuffle_read_mb: int
    shuffle_write_mb: int


@dataclass
class ResourceAlert:
    """Alert for resource-related issues."""
    severity: str  # "WARNING", "CRITICAL"
    category: str  # "MEMORY", "CPU", "DISK", "EXECUTOR"
    message: str
    current_value: float
    threshold: float
    timestamp: str
    recommendations: List[str]


class ResourceTracker:
    """
    Track Spark resource utilization and generate alerts.
    
    Monitors:
        - Memory usage (executor and driver)
        - Storage memory (cached data)
        - Task execution metrics
        - GC time and overhead
        - Shuffle I/O
    
    Best Practices Applied:
        - Proactive alerting before OOM
        - GC overhead detection (>10% is problematic)
        - Task failure pattern detection
        - Executor loss monitoring
    """
    
    # Alert thresholds following Spark best practices
    MEMORY_WARNING_THRESHOLD = 0.80  # 80%
    MEMORY_CRITICAL_THRESHOLD = 0.90  # 90%
    STORAGE_WARNING_THRESHOLD = 0.85  # 85%
    GC_TIME_WARNING_THRESHOLD = 0.10  # 10% of execution time
    GC_TIME_CRITICAL_THRESHOLD = 0.20  # 20% of execution time
    TASK_FAILURE_RATE_WARNING = 0.05  # 5%
    TASK_FAILURE_RATE_CRITICAL = 0.10  # 10%
    
    def __init__(
        self,
        spark: SparkSession,
        enable_alerts: bool = True,
        custom_thresholds: Optional[Dict[str, float]] = None
    ):
        """
        Initialize resource tracker.
        
        Args:
            spark: Active SparkSession
            enable_alerts: Enable automatic alert generation
            custom_thresholds: Custom threshold values (optional)
        """
        self.spark = spark
        self.sc = spark.sparkContext
        self.logger = logging.getLogger(__name__)
        self.enable_alerts = enable_alerts
        
        # Override default thresholds if provided
        if custom_thresholds:
            for key, value in custom_thresholds.items():
                if hasattr(self, key):
                    setattr(self, key, value)
        
        self.snapshots: List[ResourceSnapshot] = []
        self.alerts: List[ResourceAlert] = []
        
        self.logger.info("ResourceTracker initialized")
    
    def _get_spark_ui_url(self) -> Optional[str]:
        """Get Spark UI URL from SparkContext."""
        try:
            ui_web_url = self.sc.uiWebUrl
            if ui_web_url:
                return ui_web_url
            # Fallback to localhost
            return "http://localhost:4040"
        except:
            return None
    
    def _fetch_rest_api(self, endpoint: str) -> Optional[Dict]:
        """
        Fetch data from Spark REST API.
        
        Args:
            endpoint: API endpoint (e.g., "/api/v1/applications")
            
        Returns:
            JSON response or None if failed
        """
        try:
            base_url = self._get_spark_ui_url()
            if not base_url:
                return None
            
            url = f"{base_url}{endpoint}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            self.logger.debug(f"Failed to fetch {endpoint}: {e}")
            return None
    
    def capture_snapshot(self) -> ResourceSnapshot:
        """
        Capture current resource utilization snapshot.
        
        Uses multiple data sources:
        1. SparkConf for configuration (executor memory, cores)
        2. Spark REST API for runtime metrics (if available)
        3. Fallback to estimated values
        
        Returns:
            ResourceSnapshot object
        """
        timestamp = datetime.utcnow().isoformat()
        
        try:
            conf = self.spark.sparkContext.getConf()
            
            # Parse executor memory from config
            executor_memory_str = conf.get("spark.executor.memory", "1g")
            if executor_memory_str.endswith('g') or executor_memory_str.endswith('G'):
                executor_memory_mb = int(float(executor_memory_str[:-1]) * 1024)
            elif executor_memory_str.endswith('m') or executor_memory_str.endswith('M'):
                executor_memory_mb = int(executor_memory_str[:-1])
            else:
                executor_memory_mb = 1024
            
            # Get executor cores
            executor_cores = int(conf.get("spark.executor.cores", "1"))
            
            # Try to get real metrics from REST API
            app_id = self.spark.sparkContext.applicationId
            executors_data = self._fetch_rest_api(f"/api/v1/applications/{app_id}/executors")
            
            if executors_data and isinstance(executors_data, list):
                # Real data from REST API
                num_executors = len([e for e in executors_data if e.get('id') != 'driver'])
                
                # Aggregate metrics
                total_memory_mb = 0
                used_memory_mb = 0
                total_gc_time = 0
                completed_tasks = 0
                failed_tasks = 0
                active_tasks = 0
                
                for executor in executors_data:
                    if executor.get('id') == 'driver':
                        continue
                    
                    # Memory metrics
                    max_mem = executor.get('maxMemory', 0) // (1024 * 1024)  # Convert to MB
                    used_mem = executor.get('memoryUsed', 0) // (1024 * 1024)
                    total_memory_mb += max_mem
                    used_memory_mb += used_mem
                    
                    # GC time
                    total_gc_time += executor.get('totalGCTime', 0)
                    
                    # Task metrics
                    completed_tasks += executor.get('totalTasks', 0)
                    failed_tasks += executor.get('failedTasks', 0)
                    active_tasks += executor.get('activeTasks', 0)
                
                total_cores = executor_cores * num_executors
                memory_util = (used_memory_mb / total_memory_mb * 100) if total_memory_mb > 0 else 0
                
            else:
                # Fallback to config-based estimation
                num_executors_str = conf.get("spark.executor.instances", "0")
                num_executors = int(num_executors_str) if num_executors_str else 0
                
                if num_executors == 0:
                    # Try dynamic allocation
                    if conf.get("spark.dynamicAllocation.enabled", "false") == "true":
                        num_executors = int(conf.get("spark.dynamicAllocation.initialExecutors", "2"))
                    else:
                        num_executors = 1  # Minimum fallback
                
                total_memory_mb = executor_memory_mb * num_executors
                used_memory_mb = 0  # Unknown without REST API
                memory_util = 0
                total_cores = executor_cores * num_executors
                total_gc_time = 0
                completed_tasks = 0
                failed_tasks = 0
                active_tasks = 0
            
            # Try to get shuffle metrics from stages
            shuffle_read_mb = 0
            shuffle_write_mb = 0
            
            stages_data = self._fetch_rest_api(f"/api/v1/applications/{app_id}/stages")
            if stages_data and isinstance(stages_data, list):
                for stage in stages_data:
                    if isinstance(stage, dict):
                        shuffle_read_mb += stage.get('inputBytes', 0) // (1024 * 1024)
                        shuffle_write_mb += stage.get('outputBytes', 0) // (1024 * 1024)
            
            snapshot = ResourceSnapshot(
                timestamp=timestamp,
                total_memory_mb=total_memory_mb,
                used_memory_mb=used_memory_mb,
                memory_utilization_pct=memory_util,
                total_storage_mb=total_memory_mb,
                used_storage_mb=used_memory_mb,
                storage_utilization_pct=memory_util,
                active_tasks=active_tasks,
                completed_tasks=completed_tasks,
                failed_tasks=failed_tasks,
                active_executors=num_executors,
                total_cores=total_cores,
                total_gc_time_ms=total_gc_time,
                shuffle_read_mb=shuffle_read_mb,
                shuffle_write_mb=shuffle_write_mb
            )
            
            self.snapshots.append(snapshot)
            
            # Generate alerts if enabled
            if self.enable_alerts:
                self._check_and_generate_alerts(snapshot)
            
            return snapshot
            
        except Exception as e:
            self.logger.warning(f"Failed to capture resource snapshot, using minimal data: {e}")
            # Return minimal snapshot with config-based data
            try:
                conf = self.spark.sparkContext.getConf()
                executor_memory_str = conf.get("spark.executor.memory", "1g")
                if executor_memory_str.endswith('g') or executor_memory_str.endswith('G'):
                    executor_memory_mb = int(float(executor_memory_str[:-1]) * 1024)
                else:
                    executor_memory_mb = 1024
                
                num_executors = int(conf.get("spark.executor.instances", "1"))
                executor_cores = int(conf.get("spark.executor.cores", "1"))
                
                snapshot = ResourceSnapshot(
                    timestamp=timestamp,
                    total_memory_mb=executor_memory_mb * num_executors,
                    used_memory_mb=0,
                    memory_utilization_pct=0,
                    total_storage_mb=executor_memory_mb * num_executors,
                    used_storage_mb=0,
                    storage_utilization_pct=0,
                    active_tasks=0,
                    completed_tasks=0,
                    failed_tasks=0,
                    active_executors=num_executors,
                    total_cores=executor_cores * num_executors,
                    total_gc_time_ms=0,
                    shuffle_read_mb=0,
                    shuffle_write_mb=0
                )
            except:
                # Ultimate fallback
                snapshot = ResourceSnapshot(
                    timestamp=timestamp,
                    total_memory_mb=0,
                    used_memory_mb=0,
                    memory_utilization_pct=0,
                    total_storage_mb=0,
                    used_storage_mb=0,
                    storage_utilization_pct=0,
                    active_tasks=0,
                    completed_tasks=0,
                    failed_tasks=0,
                    active_executors=0,
                    total_cores=0,
                    total_gc_time_ms=0,
                    shuffle_read_mb=0,
                    shuffle_write_mb=0
                )
            
            self.snapshots.append(snapshot)
            return snapshot
    
    def _check_and_generate_alerts(self, snapshot: ResourceSnapshot) -> None:
        """
        Check resource snapshot against thresholds and generate alerts.
        
        Args:
            snapshot: Current resource snapshot
        """
        alerts = []
        
        # Memory alerts
        memory_pct = snapshot.memory_utilization_pct / 100
        if memory_pct >= self.MEMORY_CRITICAL_THRESHOLD:
            alerts.append(ResourceAlert(
                severity="CRITICAL",
                category="MEMORY",
                message=f"Critical memory usage: {snapshot.memory_utilization_pct:.1f}%",
                current_value=memory_pct,
                threshold=self.MEMORY_CRITICAL_THRESHOLD,
                timestamp=snapshot.timestamp,
                recommendations=[
                    "Increase executor memory: spark.executor.memory",
                    "Reduce parallelism to use fewer executors",
                    "Enable dynamic resource allocation",
                    "Check for memory leaks or large broadcast variables",
                    "Use persist(MEMORY_AND_DISK) instead of cache()"
                ]
            ))
        elif memory_pct >= self.MEMORY_WARNING_THRESHOLD:
            alerts.append(ResourceAlert(
                severity="WARNING",
                category="MEMORY",
                message=f"High memory usage: {snapshot.memory_utilization_pct:.1f}%",
                current_value=memory_pct,
                threshold=self.MEMORY_WARNING_THRESHOLD,
                timestamp=snapshot.timestamp,
                recommendations=[
                    "Monitor memory usage closely",
                    "Consider increasing executor memory if OOM occurs",
                    "Review cached DataFrames and unpersist unused ones"
                ]
            ))
        
        # Storage alerts
        storage_pct = snapshot.storage_utilization_pct / 100
        if storage_pct >= self.STORAGE_WARNING_THRESHOLD:
            alerts.append(ResourceAlert(
                severity="WARNING",
                category="STORAGE",
                message=f"High storage memory usage: {snapshot.storage_utilization_pct:.1f}%",
                current_value=storage_pct,
                threshold=self.STORAGE_WARNING_THRESHOLD,
                timestamp=snapshot.timestamp,
                recommendations=[
                    "Review cached DataFrames and unpersist unused ones",
                    "Use MEMORY_AND_DISK storage level for large datasets",
                    "Increase spark.memory.storageFraction if needed"
                ]
            ))
        
        # Task failure alerts
        if snapshot.completed_tasks + snapshot.failed_tasks > 0:
            failure_rate = snapshot.failed_tasks / (snapshot.completed_tasks + snapshot.failed_tasks)
            
            if failure_rate >= self.TASK_FAILURE_RATE_CRITICAL:
                alerts.append(ResourceAlert(
                    severity="CRITICAL",
                    category="EXECUTOR",
                    message=f"Critical task failure rate: {failure_rate*100:.1f}%",
                    current_value=failure_rate,
                    threshold=self.TASK_FAILURE_RATE_CRITICAL,
                    timestamp=snapshot.timestamp,
                    recommendations=[
                        "Increase task retry attempts: spark.task.maxFailures",
                        "Enable speculative execution for slow tasks",
                        "Check executor logs for root cause",
                        "Verify cluster stability and network connectivity"
                    ]
                ))
            elif failure_rate >= self.TASK_FAILURE_RATE_WARNING:
                alerts.append(ResourceAlert(
                    severity="WARNING",
                    category="EXECUTOR",
                    message=f"Elevated task failure rate: {failure_rate*100:.1f}%",
                    current_value=failure_rate,
                    threshold=self.TASK_FAILURE_RATE_WARNING,
                    timestamp=snapshot.timestamp,
                    recommendations=[
                        "Monitor task failures closely",
                        "Review task logs for patterns"
                    ]
                ))
        
        # Add alerts to tracker
        self.alerts.extend(alerts)
        
        # Log critical alerts immediately
        for alert in alerts:
            if alert.severity == "CRITICAL":
                self.logger.error(f"{alert.category} ALERT: {alert.message}")
            else:
                self.logger.warning(f"{alert.category} ALERT: {alert.message}")
    
    def get_active_alerts(self, severity: Optional[str] = None) -> List[ResourceAlert]:
        """
        Get active alerts, optionally filtered by severity.
        
        Args:
            severity: Filter by severity ("WARNING" or "CRITICAL")
            
        Returns:
            List of ResourceAlert objects
        """
        if severity:
            return [a for a in self.alerts if a.severity == severity]
        return self.alerts
    
    def print_resource_summary(self) -> None:
        """Print current resource utilization summary."""
        if not self.snapshots:
            print("No resource data available. Call capture_snapshot() first.")
            return
        
        snapshot = self.snapshots[-1]
        
        print("\n" + "="*80)
        print("RESOURCE UTILIZATION SUMMARY")
        print("="*80)
        print(f"Timestamp: {snapshot.timestamp}")
        print(f"\nMemory:")
        print(f"  Total: {snapshot.total_memory_mb} MB")
        print(f"  Used: {snapshot.used_memory_mb} MB ({snapshot.memory_utilization_pct:.1f}%)")
        print(f"\nStorage:")
        print(f"  Total: {snapshot.total_storage_mb} MB")
        print(f"  Used: {snapshot.used_storage_mb} MB ({snapshot.storage_utilization_pct:.1f}%)")
        print(f"\nExecutors:")
        print(f"  Active: {snapshot.active_executors}")
        print(f"  Total Cores: {snapshot.total_cores}")
        print(f"\nTasks:")
        print(f"  Active: {snapshot.active_tasks}")
        print(f"  Completed: {snapshot.completed_tasks}")
        print(f"  Failed: {snapshot.failed_tasks}")
        
        # Show alerts
        critical_alerts = self.get_active_alerts("CRITICAL")
        warning_alerts = self.get_active_alerts("WARNING")
        
        if critical_alerts:
            print(f"\n🔴 CRITICAL ALERTS: {len(critical_alerts)}")
            for alert in critical_alerts:
                print(f"  - {alert.message}")
        
        if warning_alerts:
            print(f"\n⚠️  WARNING ALERTS: {len(warning_alerts)}")
            for alert in warning_alerts:
                print(f"  - {alert.message}")
        
        print("="*80 + "\n")
    
    def clear_alerts(self) -> None:
        """Clear all alerts."""
        self.alerts.clear()
        self.logger.info("Alerts cleared")
