"""Optimized Oracle utilities for better performance"""
from typing import Optional, Tuple
from urllib.parse import quote_plus

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import col, current_timestamp, max as spark_max, lit
from pyspark.sql.types import LongType

from .configs import oracle_config
from .logging import get_logger

log = get_logger(__name__)

SCN_COL = "CDC_SCN"


def build_oracle_jdbc_url() -> str:
    """Build Oracle JDBC URL from config"""
    cfg = oracle_config()
    log.info(f"Using Oracle JDBC: {cfg.safe_url}")
    return cfg.jdbc_url


def check_new_data_exists(
    spark: SparkSession, 
    oracle_table: str, 
    last_scn: Optional[int]
) -> Tuple[bool, Optional[int]]:
    """
    Check if new data exists WITHOUT reading full table.
    Returns (has_new_data, max_scn_in_source)
    
    Performance: Only queries MAX(ORA_ROWSCN), not full table scan.
    """
    jdbc_url = build_oracle_jdbc_url()
    cfg = oracle_config()
    
    # Query only max SCN - very fast!
    if last_scn:
        query = f"""
        (SELECT MAX(ORA_ROWSCN) AS MAX_SCN, COUNT(*) AS CNT
         FROM {oracle_table} 
         WHERE ORA_ROWSCN > {last_scn}) t
        """
    else:
        query = f"""
        (SELECT MAX(ORA_ROWSCN) AS MAX_SCN, COUNT(*) AS CNT
         FROM {oracle_table}) t
        """
    
    options = {
        "url": jdbc_url,
        "dbtable": query,
        "user": cfg.username,
        "password": cfg.password,
        "driver": "oracle.jdbc.driver.OracleDriver",
    }
    
    result = spark.read.format("jdbc").options(**options).load().collect()[0]
    max_scn = result["MAX_SCN"]
    count = result["CNT"]
    
    if count == 0 or max_scn is None:
        log.info("No new data detected (fast check)")
        return False, last_scn
    
    log.info(f"New data detected: {count} rows, max SCN: {max_scn}")
    return True, int(max_scn)


def read_oracle_incremental_optimized(
    spark: SparkSession, 
    oracle_table: str, 
    last_scn: Optional[int]
) -> DataFrame:
    """
    Read Oracle incremental data with optimized settings.
    
    Args:
        spark: Spark session
        oracle_table: Source table name
        last_scn: Last checkpoint SCN
        
    Note: JDBC partitioning removed to avoid complexity.
    Use increased fetchsize for better performance instead.
    """
    jdbc_url = build_oracle_jdbc_url()
    cfg = oracle_config()
    
    if last_scn:
        query = f"""
        (SELECT a.*, a.ORA_ROWSCN AS {SCN_COL}
         FROM {oracle_table} a
         WHERE a.ORA_ROWSCN > {last_scn}
         ) t
        """
        log.info(f"Incremental read WHERE ORA_ROWSCN > {last_scn}")
    else:
        query = f"""
        (SELECT a.*, a.ORA_ROWSCN AS {SCN_COL}
         FROM {oracle_table} a
         ) t
        """
        log.info("Initial full read (no checkpoint found)")

    options = {
        "url": jdbc_url,
        "dbtable": query,
        "user": cfg.username,
        "password": cfg.password,
        "driver": "oracle.jdbc.driver.OracleDriver",
        "fetchsize": "10000",  # Increased from 5000 for better performance
        "queryTimeout": "600",
    }
    
    log.info(f"Reading Oracle with fetchsize={options['fetchsize']}")
    df = spark.read.format("jdbc").options(**options).load()
    return df.withColumn("_cdc_checkpoint_scn", col(SCN_COL).cast(LongType())) \
             .withColumn("_cdc_extracted_at", current_timestamp()) \
             .withColumn("_source_system", lit("oracle")) \
             .withColumn("_source_table", lit(oracle_table))


def get_max_scn_from_df(df: DataFrame) -> Optional[int]:
    """
    Extract max SCN from DataFrame efficiently.
    Uses single aggregation instead of collect().
    """
    result = df.agg(spark_max(col("_cdc_checkpoint_scn")).alias("max_scn")).collect()[0]["max_scn"]
    return int(result) if result is not None else None
