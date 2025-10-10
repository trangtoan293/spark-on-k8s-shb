#!/usr/bin/env python3
"""
MS SQL Server -> Iceberg incremental loader (WITH TUNING)
============================================

Purpose:
- Incremental loader for MS SQL Server -> Iceberg using ID-based CDC.
- Similar to Oracle/MySQL loaders but optimized for MS SQL Server.
- **NEW**: Integrated spark_tuning for monitoring and optimization

Requirements (via environment variables):
- MSSQL_HOST, MSSQL_PORT, MSSQL_DATABASE, MSSQL_USERNAME, MSSQL_PASSWORD
- CONTROL_DB, CHECKPOINT_TABLE, JOB_LOG_TABLE

Usage:
  python mssql_to_iceberg.py \
    --mssql-table <dbo.TABLE_NAME> \
    --iceberg-table <db.table> \
    --primary-key <ID or "ID1,ID2"> \
    --id-column <id_column_name> \
    --checkpoint-backend table

Notes:
- This job runs one incremental batch per execution.
- Supports checkpoint backends: table (default) or JSON file.
- Performs a single MERGE into the target Iceberg table.
- Supports MS SQL Server Change Tracking feature.
"""

import os
import argparse
from datetime import datetime
from typing import Optional, Any

from pyspark.sql.functions import col, max as spark_max, unix_timestamp, from_unixtime

from utils.logging import get_logger
from utils.spark import create_spark, ensure_db_exists, ensure_table_exists
from utils.mssql import (
    check_new_data_exists_mssql,
    read_mssql_incremental,
    read_mssql_with_timestamp_cdc,
    get_max_id_from_df
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
from utils.configs import checkpoint_config

# Import spark_tuning
from spark_tuning import (
    MetricsCollector,
    PerformanceProfiler,
    SkewDetector,
    ResourceTracker
)

log = get_logger("mssql_to_iceberg")


def main():
    p = argparse.ArgumentParser(description="MS SQL Server -> Iceberg incremental loader")
    p.add_argument("--mssql-table", required=True, help="Source MS SQL table name (e.g., dbo.customers)")
    p.add_argument("--iceberg-table", required=True, help="Target Iceberg table, e.g. integration.customers")
    p.add_argument("--primary-key", required=True, help="Primary key or comma-separated composite key for MERGE")
    p.add_argument("--cdc-method", choices=["id", "timestamp"], default="id", help="CDC method: 'id' (default) or 'timestamp'")
    p.add_argument("--id-column", default="id", help="Column for 'id' based CDC (must be numeric)")
    p.add_argument("--timestamp-column", default="updated_at", help="Column for 'timestamp' based CDC (must be datetime/timestamp)")
    p.add_argument("--checkpoint-location", default="s3a://data/checkpoints/mssql", help="Checkpoint base path")
    p.add_argument("--checkpoint-backend", choices=["table", "json"], default=None, help="Where to store last ID")
    p.add_argument("--enable-tuning", action="store_true", help="Enable spark_tuning monitoring")
    p.add_argument("--export-metrics", help="Export metrics to JSON")
    args = p.parse_args()

    spark = create_spark("mssql-to-iceberg")

    # Initialize tuning tools
    collector = profiler = skew_detector = tracker = None
    if args.enable_tuning:
        log.info("=== Spark Tuning Enabled ===")
        collector = MetricsCollector(spark)
        profiler = PerformanceProfiler(spark, auto_analyze=True)
        skew_detector = SkewDetector(spark)
        tracker = ResourceTracker(spark, enable_alerts=True)
        tracker.capture_snapshot()

    try:
        # Ensure control tables and decide backend
        ensure_control_tables(spark)
        
        # Use checkpoint backend from args or environment
        if args.checkpoint_backend:
            use_table = (args.checkpoint_backend == "table")
        else:
            ckpt_cfg = checkpoint_config()
            use_table = ckpt_cfg.is_table_backend

        # Get last checkpoint value (will be an integer)
        last_checkpoint_val = (
            get_last_scn_table(spark, args.mssql_table)
            if use_table
            else get_last_scn_json(spark, args.checkpoint_location, args.mssql_table)
        )

        job_start = datetime.utcnow()
        row_count = 0
        df = None
        max_checkpoint_val: Optional[int] = None

        if args.cdc_method == "id":
            # --- ID-based CDC (for numeric columns) ---
            last_id = last_checkpoint_val
            log.info(f"=== Using ID-based CDC with column '{args.id_column}' ===")
            
            # Fast pre-check
            has_new_data, max_id_in_source = check_new_data_exists_mssql(
                spark, args.mssql_table, last_id, args.id_column
            )
            
            if not has_new_data:
                log.info("No new data detected (fast check). Exiting.")
                insert_job_log(spark, source_system="mssql", source_table=args.mssql_table, iceberg_table=args.iceberg_table, status="NOOP", rows_processed=0, max_scn=last_id, start_time=job_start, end_time=datetime.utcnow())
                return

            # Read data
            if profiler:
                @profiler.profile_function("mssql_read_id")
                def read_data_id():
                    return read_mssql_incremental(spark, args.mssql_table, last_id, args.id_column)
                df = read_data_id()
            else:
                df = read_mssql_incremental(spark, args.mssql_table, last_id, args.id_column)
            
            max_checkpoint_val = max_id_in_source

        elif args.cdc_method == "timestamp":
            # --- Timestamp-based CDC (for datetime columns) ---
            last_ts_epoch = last_checkpoint_val
            last_timestamp_str = None
            if last_ts_epoch:
                # Convert epoch seconds back to a 'YYYY-MM-DD HH:MI:SS.sss' string for the SQL query
                last_timestamp_str = spark.createDataFrame([(last_ts_epoch,)], ["ts_epoch"]) \
                    .select(from_unixtime(col("ts_epoch"), "yyyy-MM-dd HH:mm:ss.SSS").alias("ts_str")) \
                    .collect()[0]["ts_str"]
            
            log.info(f"=== Using Timestamp-based CDC with column '{args.timestamp_column}' ===")
            log.info(f"Last checkpoint timestamp: {last_timestamp_str or 'None'}")

            # Read data using the timestamp string
            if profiler:
                @profiler.profile_function("mssql_read_timestamp")
                def read_data_ts():
                    return read_mssql_with_timestamp_cdc(spark, args.mssql_table, last_timestamp_str, args.timestamp_column)
                df = read_data_ts()
            else:
                df = read_mssql_with_timestamp_cdc(spark, args.mssql_table, last_timestamp_str, args.timestamp_column)

            if df.rdd.isEmpty():
                log.info("No new data detected. Exiting.")
                insert_job_log(spark, source_system="mssql", source_table=args.mssql_table, iceberg_table=args.iceberg_table, status="NOOP", rows_processed=0, max_scn=last_ts_epoch, start_time=job_start, end_time=datetime.utcnow())
                return

            # Create the numeric checkpoint column for the MERGE logic
            df = df.withColumn("_cdc_checkpoint_id", unix_timestamp(col(args.timestamp_column)).cast("long"))
            
            # Find the max timestamp from the new data and convert it to an epoch integer for the next checkpoint
            max_timestamp = df.agg(spark_max(col(args.timestamp_column))).collect()[0][0]
            if max_timestamp:
                max_checkpoint_val = spark.createDataFrame([(max_timestamp,)], ["ts"]) \
                    .select(unix_timestamp(col("ts")).alias("epoch")) \
                    .collect()[0]["epoch"]

        # OPTIMIZATION 3: Cache DataFrame for reuse
        df.cache()
        
        if profiler:
            count_result = profiler.profile_dataframe_action(df, "count", df.count)
            row_count = df.count() # Re-count after action
        else:
            row_count = df.count()
        
        log.info(f"Read {row_count} rows from MS SQL Server")

        if row_count == 0:
            log.info("No new rows to process after caching. Exiting.")
            insert_job_log(
                spark,
                source_system="mssql",
                source_table=args.mssql_table,
                iceberg_table=args.iceberg_table,
                status="NOOP",
                rows_processed=0,
                max_scn=last_checkpoint_val,
                start_time=job_start,
                end_time=datetime.utcnow(),
            )
            df.unpersist()
            return
        
        # Check skew
        if args.enable_tuning and skew_detector and row_count > 10000:
            has_skew, skew_info = skew_detector.detect_skew(df, sample_fraction=0.1)
            if has_skew:
                log.warning("⚠️  Data skew detected!")
                skew_detector.print_skew_analysis(skew_info)

        # Ensure DB/table exists
        ensure_db_exists(spark, args.iceberg_table)
        ensure_table_exists(spark, args.iceberg_table, df)

        # Log the max checkpoint value
        log.info(f"Max checkpoint value for this run: {max_checkpoint_val}")

        # Perform MERGE
        if profiler:
            @profiler.profile_function("iceberg_merge")
            def do_merge():
                merge_simple(spark, df, args.iceberg_table, args.primary_key)
            do_merge()
        else:
            merge_simple(spark, df, args.iceberg_table, args.primary_key)

        # Update checkpoint
        if max_checkpoint_val is not None:
            if use_table:
                save_last_scn_table(spark, args.mssql_table, int(max_checkpoint_val))
            else:
                save_last_scn_json(spark, args.checkpoint_location, args.mssql_table, int(max_checkpoint_val))
            log.info(f"Completed incremental merge. New checkpoint value: {max_checkpoint_val}")

        # Job run log (SUCCESS)
        insert_job_log(
            spark,
            source_system="mssql",
            source_table=args.mssql_table,
            iceberg_table=args.iceberg_table,
            status="SUCCESS",
            rows_processed=row_count,
            max_scn=max_checkpoint_val,
            start_time=job_start,
            end_time=datetime.utcnow(),
        )
        
        # Cleanup
        df.unpersist()
        
        # Print tuning report
        if args.enable_tuning:
            log.info("\n" + "="*80)
            log.info("SPARK TUNING REPORT - MS SQL to Iceberg")
            log.info("="*80)
            if collector:
                collector.print_summary()
            if profiler:
                profiler.print_profile_summary()
            if tracker:
                tracker.capture_snapshot()
                tracker.print_resource_summary()
            if args.export_metrics and collector:
                collector.export_to_json(args.export_metrics)
                log.info(f"📊 Metrics exported to: {args.export_metrics}")
        
    except Exception as e:
        # Job run log (FAILED)
        try:
            insert_job_log(
                spark,
                source_system="mssql",
                source_table=args.mssql_table,
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
