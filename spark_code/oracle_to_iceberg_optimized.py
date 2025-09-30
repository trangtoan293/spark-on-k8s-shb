#!/usr/bin/env python3
"""
Oracle -> Iceberg incremental loader (OPTIMIZED version)
=========================================================

Performance improvements over simple version:
1. Fast pre-check: Query MAX(ORA_ROWSCN) before reading full data
2. Partitioned reads: Parallel JDBC reads for large datasets
3. Cached operations: Reuse DataFrames efficiently
4. Optimized checkpointing: Avoid redundant operations

Usage:
  python oracle_to_iceberg_optimized.py \
    --oracle-table <SCHEMA.TABLE> \
    --iceberg-table <db.table> \
    --primary-key <ID or "ID1,ID2"> \
    --checkpoint-location s3a://data/checkpoints/oracle-optimized \
    --num-partitions 8  # For parallel reads

Version: 2.0.0 - Performance optimized
"""

import os
import argparse
from datetime import datetime
from typing import Optional

from pyspark.sql.functions import col, max as spark_max

from spark_code.utils.logging import get_logger
from spark_code.utils.spark import create_spark, ensure_db_exists, ensure_table_exists
from spark_code.utils.oracle_optimized import (
    check_new_data_exists,
    read_oracle_incremental_optimized,
    get_max_scn_from_df
)
from spark_code.utils.checkpoint import (
    ensure_control_tables,
    get_last_scn_table,
    save_last_scn_table,
    get_last_scn_json,
    save_last_scn_json,
    insert_job_log,
)
from spark_code.utils.merge import merge_simple

log = get_logger("oracle_to_iceberg_optimized")


def main():
    p = argparse.ArgumentParser(description="Optimized Oracle -> Iceberg incremental (ORA_ROWSCN)")
    p.add_argument("--oracle-table", required=True, help="Source table, e.g. SCHEMA.TABLE")
    p.add_argument("--iceberg-table", required=True, help="Target Iceberg table, e.g. integration.customers")
    p.add_argument("--primary-key", default="ID", help="Primary key or comma-separated composite key")
    p.add_argument("--checkpoint-location", default="s3a://data/checkpoints/oracle-optimized", help="Checkpoint base path")
    p.add_argument("--checkpoint-backend", choices=["table", "json"], default=os.getenv("CHECKPOINT_BACKEND", "table"), help="Where to store last SCN")
    p.add_argument("--num-partitions", type=int, default=4, help="Number of partitions for parallel JDBC reads")
    p.add_argument("--partition-column", default="ORA_ROWSCN", help="Column for partitioning reads")
    args = p.parse_args()

    spark = create_spark("oracle-to-iceberg-optimized")

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
                source_table=args.oracle_table,
                iceberg_table=args.iceberg_table,
                status="NOOP",
                rows_processed=0,
                max_scn=last_scn,
                start_time=job_start,
                end_time=datetime.utcnow(),
            )
            return

        # OPTIMIZATION 2: Partitioned read for parallel processing
        log.info("=== OPTIMIZATION: Partitioned read ===")
        df = read_oracle_incremental_optimized(
            spark, 
            args.oracle_table, 
            last_scn,
            partition_column=args.partition_column if args.num_partitions > 1 else None,
            num_partitions=args.num_partitions
        )
        
        # OPTIMIZATION 3: Cache DataFrame for reuse
        df.cache()
        row_count = df.count()
        log.info(f"Read {row_count} rows from Oracle")

        # Ensure DB/table exists
        ensure_db_exists(spark, args.iceberg_table)
        ensure_table_exists(spark, args.iceberg_table, df)

        # OPTIMIZATION 4: Get max SCN efficiently (already have it from pre-check!)
        max_scn = max_scn_in_source  # Reuse from fast check
        log.info(f"Max SCN from fast check: {max_scn}")

        # Perform MERGE
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
        
    except Exception as e:
        # Job run log (FAILED)
        try:
            insert_job_log(
                spark,
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
