from datetime import datetime
from typing import Optional
import uuid

from pyspark.sql import SparkSession
from pyspark.sql.functions import col

CONTROL_DB = "system"
CHECKPOINT_TABLE = f"{CONTROL_DB}.oracle_scn_checkpoint"
JOB_LOG_TABLE = f"{CONTROL_DB}.job_run_logs"


def ensure_control_tables(spark: SparkSession) -> None:
    spark.sql(f"CREATE DATABASE IF NOT EXISTS {CONTROL_DB}")
    spark.sql(
        f"""
        CREATE TABLE IF NOT EXISTS {CHECKPOINT_TABLE} (
          source_table STRING NOT NULL,
          last_scn BIGINT,
          updated_at TIMESTAMP,
          PRIMARY KEY (source_table) NOT ENFORCED
        ) USING iceberg
        """
    )
    spark.sql(
        f"""
        CREATE TABLE IF NOT EXISTS {JOB_LOG_TABLE} (
          job_id STRING,
          source_table STRING,
          iceberg_table STRING,
          status STRING,
          rows_processed BIGINT,
          max_scn BIGINT,
          start_time TIMESTAMP,
          end_time TIMESTAMP,
          error_message STRING
        ) USING iceberg
        """
    )


def get_last_scn_table(spark: SparkSession, source_table: str) -> Optional[int]:
    try:
        df = (
            spark.table(CHECKPOINT_TABLE)
            .where(col("source_table") == source_table)
            .select("last_scn")
        )
        rows = df.limit(1).collect()
        if not rows:
            return None
        val = rows[0][0]
        return int(val) if val is not None else None
    except Exception:
        return None


def save_last_scn_table(spark: SparkSession, source_table: str, scn: int) -> None:
    spark.sql(
        f"""
        MERGE INTO {CHECKPOINT_TABLE} t
        USING (
          SELECT '{source_table}' AS source_table,
                 {int(scn)} AS last_scn,
                 current_timestamp() AS updated_at
        ) s
        ON t.source_table = s.source_table
        WHEN MATCHED THEN UPDATE SET last_scn = s.last_scn, updated_at = s.updated_at
        WHEN NOT MATCHED THEN INSERT (source_table, last_scn, updated_at)
        VALUES (s.source_table, s.last_scn, s.updated_at)
        """
    )


def insert_job_log(
    spark: SparkSession,
    source_table: str,
    iceberg_table: str,
    status: str,
    rows_processed: Optional[int],
    max_scn: Optional[int],
    start_time: datetime,
    end_time: datetime,
    error_message: Optional[str] = None,
) -> None:
    data = [
        {
            "job_id": str(uuid.uuid4()),
            "source_table": source_table,
            "iceberg_table": iceberg_table,
            "status": status,
            "rows_processed": int(rows_processed) if rows_processed is not None else None,
            "max_scn": int(max_scn) if max_scn is not None else None,
            "start_time": start_time,
            "end_time": end_time,
            "error_message": (error_message[:500] if error_message else None),
        }
    ]
    spark.createDataFrame(data).write.mode("append").format("iceberg").saveAsTable(
        JOB_LOG_TABLE
    )


# JSON fallback helpers
CHECKPOINT_SUBDIR = "scn_checkpoint"


def get_last_scn_json(
    spark: SparkSession, checkpoint_location: str, table_name: str
) -> Optional[int]:
    path = f"{checkpoint_location}/{CHECKPOINT_SUBDIR}/{table_name}.json"
    try:
        df = spark.read.option("multiline", "true").json(path)
        if df.count() == 0:
            return None
        v = df.select("last_scn").collect()[0][0]
        return int(v) if v is not None else None
    except Exception:
        return None


def save_last_scn_json(
    spark: SparkSession, checkpoint_location: str, table_name: str, scn: int
) -> None:
    path = f"{checkpoint_location}/{CHECKPOINT_SUBDIR}/{table_name}.json"
    data = [
        {
            "table_name": table_name,
            "last_scn": int(scn),
            "updated_at": datetime.utcnow().isoformat(),
            "checkpoint_type": "ora_rowscn",
        }
    ]
    (
        spark.createDataFrame(data)
        .coalesce(1)
        .write.mode("overwrite")
        .option("multiline", "true")
        .json(path)
    )
