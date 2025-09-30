"""MySQL utilities for CDC and incremental loading"""
from typing import Optional, Tuple
from urllib.parse import quote_plus

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import col, current_timestamp, max as spark_max, lit
from pyspark.sql.types import LongType

from .configs import mysql_config
from .logging import get_logger

log = get_logger(__name__)


def build_mysql_jdbc_url() -> str:
    """Build MySQL JDBC URL from config."""
    cfg = mysql_config()
    log.info(f"Using MySQL JDBC: {cfg.safe_url}")
    return cfg.jdbc_url


def check_new_data_exists_mysql(
    spark: SparkSession, 
    mysql_table: str, 
    last_id: Optional[int],
    id_column: str = "id"
) -> Tuple[bool, Optional[int]]:
    """
    Check if new data exists in MySQL WITHOUT reading full table.
    Returns (has_new_data, max_id_in_source)
    
    Performance: Only queries MAX(id) and COUNT(*), not full table scan.
    
    Args:
        spark: Spark session
        mysql_table: Source table name
        last_id: Last checkpoint ID
        id_column: Name of the ID column (default: 'id')
    """
    jdbc_url = build_mysql_jdbc_url()
    cfg = mysql_config()
    
    # Query only max ID - very fast!
    if last_id:
        query = f"""
        (SELECT MAX({id_column}) AS MAX_ID, COUNT(*) AS CNT
         FROM {mysql_table} 
         WHERE {id_column} > {last_id}) t
        """
    else:
        query = f"""
        (SELECT MAX({id_column}) AS MAX_ID, COUNT(*) AS CNT
         FROM {mysql_table}) t
        """
    
    options = {
        "url": jdbc_url,
        "dbtable": query,
        "user": cfg.username,
        "password": cfg.password,
        "driver": "com.mysql.cj.jdbc.Driver",
    }
    
    result = spark.read.format("jdbc").options(**options).load().collect()[0]
    max_id = result["MAX_ID"]
    count = result["CNT"]
    
    if count == 0 or max_id is None:
        log.info("No new data detected (fast check)")
        return False, last_id
    
    log.info(f"New data detected: {count} rows, max ID: {max_id}")
    return True, int(max_id)


def read_mysql_incremental(
    spark: SparkSession, 
    mysql_table: str, 
    last_id: Optional[int],
    id_column: str = "id"
) -> DataFrame:
    """
    Read MySQL incremental data with optimized settings.
    
    Args:
        spark: Spark session
        mysql_table: Source table name
        last_id: Last checkpoint ID
        id_column: Name of the ID column for incremental reads
        
    Note: Uses increased fetchsize for better performance.
    """
    jdbc_url = build_mysql_jdbc_url()
    cfg = mysql_config()
    
    if last_id:
        query = f"""
        (SELECT a.*, a.{id_column} AS _cdc_checkpoint_id
         FROM {mysql_table} a
         WHERE a.{id_column} > {last_id}
         ORDER BY a.{id_column}) t
        """
        log.info(f"Incremental read WHERE {id_column} > {last_id}")
    else:
        query = f"""
        (SELECT a.*, a.{id_column} AS _cdc_checkpoint_id
         FROM {mysql_table} a
         ORDER BY a.{id_column}) t
        """
        log.info("Initial full read (no checkpoint found)")

    options = {
        "url": jdbc_url,
        "dbtable": query,
        "user": cfg.username,
        "password": cfg.password,
        "driver": "com.mysql.cj.jdbc.Driver",
        "fetchsize": "10000",  # Increased for better performance
        "queryTimeout": "600",
    }
    
    log.info(f"Reading MySQL with fetchsize={options['fetchsize']}")
    df = spark.read.format("jdbc").options(**options).load()
    return df.withColumn("_cdc_checkpoint_id", col("_cdc_checkpoint_id").cast(LongType())) \
             .withColumn("_cdc_extracted_at", current_timestamp()) \
             .withColumn("_source_system", lit("mysql")) \
             .withColumn("_source_table", lit(mysql_table))


def read_mysql_with_timestamp_cdc(
    spark: SparkSession,
    mysql_table: str,
    last_timestamp: Optional[str],
    timestamp_column: str = "updated_at"
) -> DataFrame:
    """
    Read MySQL data using timestamp-based CDC.
    
    Args:
        spark: Spark session
        mysql_table: Source table name
        last_timestamp: Last checkpoint timestamp (ISO format)
        timestamp_column: Name of the timestamp column
    """
    jdbc_url = build_mysql_jdbc_url()
    cfg = mysql_config()
    
    if last_timestamp:
        query = f"""
        (SELECT a.*
         FROM {mysql_table} a
         WHERE a.{timestamp_column} > '{last_timestamp}'
         ORDER BY a.{timestamp_column}) t
        """
        log.info(f"Incremental read WHERE {timestamp_column} > '{last_timestamp}'")
    else:
        query = f"""
        (SELECT a.*
         FROM {mysql_table} a
         ORDER BY a.{timestamp_column}) t
        """
        log.info("Initial full read (no checkpoint found)")

    options = {
        "url": jdbc_url,
        "dbtable": query,
        "user": cfg.username,
        "password": cfg.password,
        "driver": "com.mysql.cj.jdbc.Driver",
        "fetchsize": "10000",
        "queryTimeout": "600",
    }
    
    df = spark.read.format("jdbc").options(**options).load()
    return df.withColumn("_cdc_extracted_at", current_timestamp()) \
             .withColumn("_source_system", lit("mysql")) \
             .withColumn("_source_table", lit(mysql_table))


def get_max_id_from_df(df: DataFrame, id_column: str = "_cdc_checkpoint_id") -> Optional[int]:
    """
    Extract max ID from DataFrame efficiently.
    Uses single aggregation instead of collect().
    """
    result = df.agg(spark_max(col(id_column)).alias("max_id")).collect()[0]["max_id"]
    return int(result) if result is not None else None
