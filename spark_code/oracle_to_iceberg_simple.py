#!/usr/bin/env python3
"""
Oracle -> Iceberg incremental loader (simple, ORA_ROWSCN-based)
==============================================================

Purpose:
- Minimal, readable one-shot job for Oracle -> Iceberg using ORA_ROWSCN (SCN) as CDC.
- No streaming loop, no external config manager. Designed to be run on a schedule.

Requirements (via environment variables):
- ORACLE_HOST, ORACLE_PORT, ORACLE_SERVICE, ORACLE_USERNAME, ORACLE_PASSWORD

Usage:
  python oracle_to_iceberg_simple.py \
    --oracle-table <SCHEMA.TABLE> \
    --iceberg-table <db.table> \
    --primary-key <ID or "ID1,ID2"> \
    --checkpoint-location s3a://data/checkpoints/oracle-simple

Notes:
- This job only runs one incremental batch per execution.
- Supports checkpoint backends: table (default, Iceberg control table) or JSON file on object storage (`--checkpoint-backend table|json`).
- Performs a single MERGE into the target Iceberg table and then advances the SCN checkpoint.
"""

import os
import argparse
from datetime import datetime
from typing import Optional

from pyspark.sql.functions import col, max as spark_max

from spark_code.utils.logging import get_logger
from spark_code.utils.spark import create_spark, ensure_db_exists, ensure_table_exists
from spark_code.utils.oracle import read_oracle_incremental
from spark_code.utils.checkpoint import (
    ensure_control_tables,
    get_last_scn_table,
    save_last_scn_table,
    get_last_scn_json,
    save_last_scn_json,
    insert_job_log,
)
from spark_code.utils.merge import merge_simple

log = get_logger("oracle_to_iceberg_simple")


def main():
    p = argparse.ArgumentParser(description="Simple Oracle -> Iceberg incremental (ORA_ROWSCN)")
    p.add_argument("--oracle-table", required=True, help="Source table, e.g. SCHEMA.TABLE")
    p.add_argument("--iceberg-table", required=True, help="Target Iceberg table, e.g. integration.customers")
    p.add_argument("--primary-key", default="ID", help="Primary key or comma-separated composite key")
    p.add_argument("--checkpoint-location", default="s3a://data/checkpoints/oracle-simple", help="Checkpoint base path")
    p.add_argument("--checkpoint-backend", choices=["table", "json"], default=os.getenv("CHECKPOINT_BACKEND", "table"), help="Where to store last SCN (default: table)")
    args = p.parse_args()

    spark = create_spark()

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
        df = read_oracle_incremental(spark, args.oracle_table, last_scn)
        if df.count() == 0:
            log.info("No new data detected. Exiting.")
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

        # Ensure DB/table, then MERGE
        ensure_db_exists(spark, args.iceberg_table)
        ensure_table_exists(spark, args.iceberg_table, df)

        # Capture max SCN before merge for checkpoint
        max_scn = df.agg(spark_max(col("_cdc_checkpoint_scn")).alias("m")).collect()[0]["m"]

        merge_simple(spark, df, args.iceberg_table, args.primary_key)

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
            rows_processed=df.count(),
            max_scn=max_scn,
            start_time=job_start,
            end_time=datetime.utcnow(),
        )
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
            # Avoid masking original error if logging fails
            pass
        raise
    finally:
        spark.stop()
        log.info("Spark stopped")


if __name__ == "__main__":
    main()
