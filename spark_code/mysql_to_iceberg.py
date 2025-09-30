#!/usr/bin/env python3
"""
MySQL -> Iceberg incremental loader
====================================

Purpose:
- Incremental loader for MySQL -> Iceberg using ID-based CDC.
- Similar to Oracle loader but optimized for MySQL.
- Supports both ID-based and timestamp-based CDC.

Requirements (via environment variables):
- MYSQL_HOST, MYSQL_PORT, MYSQL_DATABASE, MYSQL_USERNAME, MYSQL_PASSWORD
- CONTROL_DB, CHECKPOINT_TABLE, JOB_LOG_TABLE

Usage:
  python mysql_to_iceberg.py \
    --mysql-table <TABLE_NAME> \
    --iceberg-table <db.table> \
    --primary-key <ID or "ID1,ID2"> \
    --id-column <id_column_name> \
    --checkpoint-backend table

Notes:
- This job runs one incremental batch per execution.
- Supports checkpoint backends: table (default) or JSON file.
- Performs a single MERGE into the target Iceberg table.
"""

import os
import argparse
from datetime import datetime
from typing import Optional

from pyspark.sql.functions import col, max as spark_max

from utils.logging import get_logger
from utils.spark import create_spark, ensure_db_exists, ensure_table_exists
from utils.mysql import (
    check_new_data_exists_mysql,
    read_mysql_incremental,
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

log = get_logger("mysql_to_iceberg")


def main():
    p = argparse.ArgumentParser(description="MySQL -> Iceberg incremental loader")
    p.add_argument("--mysql-table", required=True, help="Source MySQL table name")
    p.add_argument("--iceberg-table", required=True, help="Target Iceberg table, e.g. integration.customers")
    p.add_argument("--primary-key", default="id", help="Primary key or comma-separated composite key")
    p.add_argument("--id-column", default="id", help="ID column for incremental CDC (default: id)")
    p.add_argument("--checkpoint-location", default="s3a://data/checkpoints/mysql", help="Checkpoint base path")
    p.add_argument("--checkpoint-backend", choices=["table", "json"], default=None, help="Where to store last ID")
    args = p.parse_args()

    spark = create_spark("mysql-to-iceberg")

    try:
        # Ensure control tables and decide backend
        ensure_control_tables(spark)
        
        # Use checkpoint backend from args or environment
        if args.checkpoint_backend:
            use_table = (args.checkpoint_backend == "table")
        else:
            ckpt_cfg = checkpoint_config()
            use_table = ckpt_cfg.is_table_backend

        # Get last checkpoint (using same table as Oracle for simplicity)
        last_id = (
            get_last_scn_table(spark, args.mysql_table)
            if use_table
            else get_last_scn_json(spark, args.checkpoint_location, args.mysql_table)
        )

        job_start = datetime.utcnow()
        
        # OPTIMIZATION 1: Fast pre-check without reading full table
        log.info("=== OPTIMIZATION: Fast data check ===")
        has_new_data, max_id_in_source = check_new_data_exists_mysql(
            spark, args.mysql_table, last_id, args.id_column
        )
        
        if not has_new_data:
            log.info("No new data detected (fast check). Exiting.")
            insert_job_log(
                spark,
                source_system="mysql",
                source_table=args.mysql_table,
                iceberg_table=args.iceberg_table,
                status="NOOP",
                rows_processed=0,
                max_scn=last_id,
                start_time=job_start,
                end_time=datetime.utcnow(),
            )
            return

        # OPTIMIZATION 2: Optimized read with increased fetchsize
        log.info("=== OPTIMIZATION: Reading with optimized settings ===")
        df = read_mysql_incremental(
            spark, 
            args.mysql_table, 
            last_id,
            args.id_column
        )
        
        # OPTIMIZATION 3: Cache DataFrame for reuse
        df.cache()
        row_count = df.count()
        log.info(f"Read {row_count} rows from MySQL")

        # Ensure DB/table exists
        ensure_db_exists(spark, args.iceberg_table)
        ensure_table_exists(spark, args.iceberg_table, df)

        # OPTIMIZATION 4: Get max ID efficiently (already have it from pre-check!)
        max_id = max_id_in_source  # Reuse from fast check
        log.info(f"Max ID from fast check: {max_id}")

        # Perform MERGE
        merge_simple(spark, df, args.iceberg_table, args.primary_key)

        # Update checkpoint
        if max_id is not None:
            if use_table:
                save_last_scn_table(spark, args.mysql_table, int(max_id))
            else:
                save_last_scn_json(spark, args.checkpoint_location, args.mysql_table, int(max_id))
            log.info(f"Completed incremental merge. New checkpoint ID: {max_id}")

        # Job run log (SUCCESS)
        insert_job_log(
            spark,
            source_system="mysql",
            source_table=args.mysql_table,
            iceberg_table=args.iceberg_table,
            status="SUCCESS",
            rows_processed=row_count,
            max_scn=max_id,
            start_time=job_start,
            end_time=datetime.utcnow(),
        )
        
        # Cleanup
        df.unpersist()
        
    except Exception as e:
        # Job run log (FAILED)
        try:
            insert_job_log(
                spark,
                source_system="mysql",
                source_table=args.mysql_table,
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
