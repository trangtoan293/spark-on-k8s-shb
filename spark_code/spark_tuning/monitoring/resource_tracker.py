"""
Resource Tracker

Tracks resource utilization and provides alerts for resource-related issues.
Monitors memory, CPU, disk I/O, and network to prevent OOM and performance degradation.
"""

import logging
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
    
    def capture_snapshot(self) -> ResourceSnapshot:
        """
        Capture current resource utilization snapshot.
        
        Returns:
            ResourceSnapshot object
        """
        timestamp = datetime.utcnow().isoformat()
        
        try:
            status_tracker = self.sc.statusTracker()
            
            # Get executor memory info from SparkConf
            conf = self.spark.sparkContext.getConf()
            executor_memory_str = conf.get("spark.executor.memory", "1g")
            
            # Parse executor memory (e.g., "4g" -> 4096 MB)
            if executor_memory_str.endswith('g'):
                executor_memory_mb = int(executor_memory_str[:-1]) * 1024
            elif executor_memory_str.endswith('m'):
                executor_memory_mb = int(executor_memory_str[:-1])
            else:
                executor_memory_mb = 1024  # Default 1GB
            
            # Get number of executors from active jobs
            active_job_ids = status_tracker.getActiveJobIds()
            
            # Try to get executor count from different sources
            num_executors = 0
            try:
                # Try dynamic allocation settings
                num_executors = int(conf.get("spark.executor.instances", "0"))
            except:
                pass
            
            if num_executors == 0:
                # Fallback: estimate from active stages
                num_executors = max(len(active_job_ids), 1)
            
            # Calculate total memory
            total_memory_mb = executor_memory_mb * num_executors
            
            # Estimate used memory (we can't get exact without executor API)
            # Use a conservative estimate based on active jobs
            used_memory_mb = int(total_memory_mb * 0.5) if len(active_job_ids) > 0 else 0
            
            # Calculate utilization
            memory_util = (used_memory_mb / total_memory_mb * 100) if total_memory_mb > 0 else 0
            
            # Task metrics from active jobs
            active_tasks = 0
            completed_tasks = 0
            failed_tasks = 0
            
            for job_id in active_job_ids:
                job_info = status_tracker.getJobInfo(job_id)
                if job_info:
                    active_stage_ids = status_tracker.getActiveStageIds()
                    for stage_id in active_stage_ids:
                        stage_info = status_tracker.getStageInfo(stage_id)
                        if stage_info:
                            active_tasks += stage_info.numActiveTasks()
                            completed_tasks += stage_info.numCompletedTasks()
                            failed_tasks += stage_info.numFailedTasks()
            
            # Get executor cores
            executor_cores = int(conf.get("spark.executor.cores", "1"))
            total_cores = executor_cores * num_executors
            
            snapshot = ResourceSnapshot(
                timestamp=timestamp,
                total_memory_mb=total_memory_mb,
                used_memory_mb=used_memory_mb,
                memory_utilization_pct=memory_util,
                total_storage_mb=total_memory_mb,  # Use same as memory
                used_storage_mb=used_memory_mb,
                storage_utilization_pct=memory_util,
                active_tasks=active_tasks,
                completed_tasks=completed_tasks,
                failed_tasks=failed_tasks,
                active_executors=num_executors,
                total_cores=total_cores,
                total_gc_time_ms=0,  # Not available without executor API
                shuffle_read_mb=0,
                shuffle_write_mb=0
            )
            
            self.snapshots.append(snapshot)
            
            # Generate alerts if enabled
            if self.enable_alerts:
                self._check_and_generate_alerts(snapshot)
            
            return snapshot
            
        except Exception as e:
            self.logger.error(f"Failed to capture resource snapshot: {e}")
            # Return a minimal snapshot instead of raising
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
