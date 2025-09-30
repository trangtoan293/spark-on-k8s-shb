#!/usr/bin/env python3
"""
Oracle -> Iceberg incremental loader (OPTIMIZED + TUNED)
=========================================================

Performance improvements over simple version:
1. Fast pre-check: Query MAX(ORA_ROWSCN) before reading full data
2. Increased fetchsize: 10000 rows per fetch (vs 5000 default)
3. Cached operations: Reuse DataFrames efficiently
4. Optimized checkpointing: Avoid redundant operations
5. **NEW**: Integrated spark_tuning for monitoring and optimization

Usage:
  python oracle_to_iceberg.py \
    --oracle-table <SCHEMA.TABLE> \
    --iceberg-table <db.table> \
    --primary-key <ID or "ID1,ID2"> \
    --checkpoint-location s3a://data/checkpoints/oracle-optimized \
    --enable-tuning  # Enable performance monitoring

Version: 2.1.0 - Added spark_tuning integration
"""

import os
import argparse
from datetime import datetime
from typing import Optional
from pyspark.sql.functions import col, max as spark_max

from utils.logging import get_logger
from utils.spark import create_spark, ensure_db_exists, ensure_table_exists
from utils.oracle import (
    check_new_data_exists,
    read_oracle_incremental_optimized,
    get_max_scn_from_df
)
from utils.checkpoint import (
    ensure_control_tables,
    get_last_scn_table,
    save_last_scn_table,
    get_last_scn_json,
    save_last_scn_json,
    insert_job_log,
)
from utils.merge import merge_simple

# Import spark_tuning for performance monitoring
from spark_tuning import (
    MetricsCollector,
    PerformanceProfiler,
    QueryOptimizer,
    SkewDetector,
    ResourceTracker,
    OptimalConfigs
)

log = get_logger("oracle_to_iceberg_optimized")


def main():
    p = argparse.ArgumentParser(description="Optimized Oracle -> Iceberg incremental (ORA_ROWSCN)")
    p.add_argument("--oracle-table", required=True, help="Source table, e.g. SCHEMA.TABLE")
    p.add_argument("--iceberg-table", required=True, help="Target Iceberg table, e.g. integration.customers")
    p.add_argument("--primary-key", default="ID", help="Primary key or comma-separated composite key")
    p.add_argument("--checkpoint-location", default="s3a://data/checkpoints/oracle-optimized", help="Checkpoint base path")
    p.add_argument("--checkpoint-backend", choices=["table", "json"], default=os.getenv("CHECKPOINT_BACKEND", "table"), help="Where to store last SCN")
    p.add_argument("--enable-tuning", action="store_true", help="Enable spark_tuning monitoring and optimization")
    p.add_argument("--export-metrics", help="Export tuning metrics to JSON file")
    args = p.parse_args()

    spark = create_spark("oracle-to-iceberg-optimized")

    # Initialize tuning tools if enabled
    collector = profiler = optimizer = skew_detector = tracker = None
    
    if args.enable_tuning:
        log.info("=== Spark Tuning Enabled ===")
        collector = MetricsCollector(spark)
        profiler = PerformanceProfiler(spark, auto_analyze=True)
        optimizer = QueryOptimizer(spark)
        skew_detector = SkewDetector(spark)
        tracker = ResourceTracker(spark, enable_alerts=True)
        tracker.capture_snapshot()  # Initial snapshot

    try:
        # Ensure control tables and decide backend
        ensure_control_tables(spark)
        use_table = (args.checkpoint_backend == "table")

        last_scn = (
            get_last_scn_table(spark, args.oracle_table)
            if use_table
            else get_last_scn_json(spark, args.checkpoint_location, args.oracle_table)
        )

        job_start = datetime.utcnow()
        
        # OPTIMIZATION 1: Fast pre-check without reading full table
        log.info("=== OPTIMIZATION: Fast data check ===")
        has_new_data, max_scn_in_source = check_new_data_exists(spark, args.oracle_table, last_scn)
        
        if not has_new_data:
            log.info("No new data detected (fast check). Exiting.")
            insert_job_log(
                spark,
                source_system="oracle",
                source_table=args.oracle_table,
                iceberg_table=args.iceberg_table,
                status="NOOP",
                rows_processed=0,
                max_scn=last_scn,
                start_time=job_start,
                end_time=datetime.utcnow(),
            )
            return

        # OPTIMIZATION 2: Optimized read with increased fetchsize
        log.info("=== OPTIMIZATION: Reading with optimized settings ===")
        
        if profiler:
            @profiler.profile_function("oracle_read")
            def read_data():
                return read_oracle_incremental_optimized(spark, args.oracle_table, last_scn)
            df = read_data()
        else:
            df = read_oracle_incremental_optimized(spark, args.oracle_table, last_scn)
        
        # OPTIMIZATION 3: Cache DataFrame for reuse
        df.cache()
        
        if profiler:
            count_result = profiler.profile_dataframe_action(df, "count", df.count)
            row_count = count_result.num_rows
        else:
            row_count = df.count()
        
        log.info(f"Read {row_count} rows from Oracle")
        
        # Check for data skew if tuning enabled
        if args.enable_tuning and skew_detector and row_count > 10000:
            log.info("=== Checking for data skew ===")
            has_skew, skew_info = skew_detector.detect_skew(df, sample_fraction=0.1)
            if has_skew:
                log.warning("⚠️  Data skew detected!")
                skew_detector.print_skew_analysis(skew_info)
                solutions = skew_detector.suggest_skew_solutions(df)
                log.info("Skew solutions available in tuning report")

        # Ensure DB/table exists
        ensure_db_exists(spark, args.iceberg_table)
        ensure_table_exists(spark, args.iceberg_table, df)
        
        # Analyze query optimization opportunities if tuning enabled
        if args.enable_tuning and optimizer:
            log.info("=== Analyzing query optimization ===")
            recommendations = optimizer.analyze_dataframe(df, "oracle_source")
            if recommendations:
                log.info("Query optimization recommendations available in tuning report")

        # OPTIMIZATION 4: Get max SCN efficiently (already have it from pre-check!)
        max_scn = max_scn_in_source  # Reuse from fast check
        log.info(f"Max SCN from fast check: {max_scn}")

        # Perform MERGE
        if profiler:
            @profiler.profile_function("iceberg_merge")
            def do_merge():
                merge_simple(spark, df, args.iceberg_table, args.primary_key)
            do_merge()
        else:
            merge_simple(spark, df, args.iceberg_table, args.primary_key)

        # Update checkpoint
        if max_scn is not None:
            if use_table:
                save_last_scn_table(spark, args.oracle_table, int(max_scn))
            else:
                save_last_scn_json(spark, args.checkpoint_location, args.oracle_table, int(max_scn))
            log.info(f"Completed incremental merge. New checkpoint SCN: {max_scn}")

        # Job run log (SUCCESS)
        insert_job_log(
            spark,
            source_system="oracle",
            source_table=args.oracle_table,
            iceberg_table=args.iceberg_table,
            status="SUCCESS",
            rows_processed=row_count,
            max_scn=max_scn,
            start_time=job_start,
            end_time=datetime.utcnow(),
        )
        
        # Cleanup
        df.unpersist()
        
        # Print tuning report if enabled
        if args.enable_tuning:
            log.info("\n" + "="*80)
            log.info("SPARK TUNING REPORT - Oracle to Iceberg")
            log.info("="*80)
            
            if collector:
                collector.print_summary()
            
            if profiler:
                profiler.print_profile_summary()
            
            if optimizer and 'recommendations' in locals():
                optimizer.print_recommendations(recommendations)
            
            if tracker:
                tracker.capture_snapshot()
                tracker.print_resource_summary()
                
                alerts = tracker.get_active_alerts("CRITICAL")
                if alerts:
                    log.warning(f"\n🔴 {len(alerts)} CRITICAL ALERTS")
                    for alert in alerts[:3]:
                        log.warning(f"  {alert.category}: {alert.message}")
            
            if args.export_metrics and collector:
                collector.export_to_json(args.export_metrics)
                log.info(f"\n📊 Metrics exported to: {args.export_metrics}")
        
    except Exception as e:
        # Job run log (FAILED)
        try:
            insert_job_log(
                spark,
                source_system="oracle",
                source_table=args.oracle_table,
                iceberg_table=args.iceberg_table,
                status="FAILED",
                rows_processed=None,
                max_scn=None,
                start_time=job_start if 'job_start' in locals() else datetime.utcnow(),
                end_time=datetime.utcnow(),
                error_message=str(e),
            )
        except Exception:
            pass
        raise
    finally:
        spark.stop()
        log.info("Spark stopped")


if __name__ == "__main__":
    main()
