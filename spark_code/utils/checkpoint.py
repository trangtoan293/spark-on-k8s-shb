from datetime import datetime
from typing import Optional
import uuid

from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.sql.types import (
    StructType, StructField, StringType, LongType, TimestampType
)

CONTROL_DB = "etladmin"
CHECKPOINT_TABLE = f"{CONTROL_DB}.oracle_scn_checkpoint"
JOB_LOG_TABLE = f"{CONTROL_DB}.job_run_logs"


def ensure_control_tables(spark: SparkSession) -> None:
    """Create control tables for checkpoint and job logging.
    
    Note: Iceberg with Spark SQL does not support PRIMARY KEY in CREATE TABLE.
    Instead, use ALTER TABLE SET IDENTIFIER FIELDS after table creation.
    """
    spark.sql(f"CREATE DATABASE IF NOT EXISTS {CONTROL_DB}")
    
    # Create checkpoint table
    spark.sql(
        f"""
        CREATE TABLE IF NOT EXISTS {CHECKPOINT_TABLE} (
          source_table STRING NOT NULL,
          last_scn BIGINT,
          updated_at TIMESTAMP
        ) USING iceberg
        TBLPROPERTIES (
          'format-version' = '2',
          'write.upsert.enabled' = 'true'
        )
        """
    )
    
    # Set identifier fields (equivalent to PRIMARY KEY)
    try:
        spark.sql(
            f"ALTER TABLE {CHECKPOINT_TABLE} SET IDENTIFIER FIELDS source_table"
        )
    except Exception:
        # Table might already have identifier fields set
        pass
    
    # Create job log table
    spark.sql(
        f"""
        CREATE TABLE IF NOT EXISTS {JOB_LOG_TABLE} (
          job_id STRING NOT NULL,
          source_table STRING,
          iceberg_table STRING,
          status STRING,
          rows_processed BIGINT,
          max_scn BIGINT,
          start_time TIMESTAMP,
          end_time TIMESTAMP,
          error_message STRING
        ) USING iceberg
        TBLPROPERTIES (
          'format-version' = '2'
        )
        """
    )
    
    # Set identifier fields for job log
    try:
        spark.sql(
            f"ALTER TABLE {JOB_LOG_TABLE} SET IDENTIFIER FIELDS job_id"
        )
    except Exception:
        pass


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
    """Insert job log with explicit schema to avoid Spark inference issues."""
    
    # Define explicit schema to handle None values
    schema = StructType([
        StructField("job_id", StringType(), False),
        StructField("source_table", StringType(), True),
        StructField("iceberg_table", StringType(), True),
        StructField("status", StringType(), True),
        StructField("rows_processed", LongType(), True),
        StructField("max_scn", LongType(), True),
        StructField("start_time", TimestampType(), True),
        StructField("end_time", TimestampType(), True),
        StructField("error_message", StringType(), True),
    ])
    
    # Prepare data as tuple (matches schema order)
    data = [(
        str(uuid.uuid4()),
        source_table,
        iceberg_table,
        status,
        int(rows_processed) if rows_processed is not None else None,
        int(max_scn) if max_scn is not None else None,
        start_time,
        end_time,
        error_message[:500] if error_message else None,
    )]
    
    # Create DataFrame with explicit schema
    spark.createDataFrame(data, schema).write.mode("append").format("iceberg").saveAsTable(
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
