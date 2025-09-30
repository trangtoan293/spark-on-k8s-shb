from typing import Optional
from urllib.parse import quote_plus

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import col, current_timestamp
from pyspark.sql.types import LongType

from .configs import oracle_config
from .logging import get_logger

log = get_logger(__name__)

SCN_COL = "CDC_SCN"


def build_oracle_jdbc_url() -> str:
    cfg = oracle_config()
    user = quote_plus(cfg["username"])
    pwd = quote_plus(cfg["password"])
    host = cfg["host"]
    port = cfg["port"]
    service = cfg["service"]
    safe_url = f"jdbc:oracle:thin:***:***@//{host}:{port}/{service}"
    log.info(f"Using Oracle JDBC: {safe_url}")
    return f"jdbc:oracle:thin:{user}/{pwd}@//{host}:{port}/{service}"


def read_oracle_incremental(
    spark: SparkSession, oracle_table: str, last_scn: Optional[int]
) -> DataFrame:
    jdbc_url = build_oracle_jdbc_url()
    if last_scn:
        query = f"""
        (SELECT a.*, a.ORA_ROWSCN AS {SCN_COL}
         FROM {oracle_table} a
         WHERE a.ORA_ROWSCN > {last_scn}
         ORDER BY a.ORA_ROWSCN) t
        """
        log.info(f"Incremental read WHERE ORA_ROWSCN > {last_scn}")
    else:
        query = f"""
        (SELECT a.*, a.ORA_ROWSCN AS {SCN_COL}
         FROM {oracle_table} a
         ORDER BY a.ORA_ROWSCN) t
        """
        log.info("Initial full read (no checkpoint found)")

    cfg = oracle_config()
    options = {
        "url": jdbc_url,
        "dbtable": query,
        "user": cfg["username"],
        "password": cfg["password"],
        "driver": "oracle.jdbc.driver.OracleDriver",
        "fetchsize": "5000",
        "queryTimeout": "600",
    }
    df = spark.read.format("jdbc").options(**options).load()
    return df.withColumn("_cdc_checkpoint_scn", col(SCN_COL).cast(LongType())) \
             .withColumn("_cdc_extracted_at", current_timestamp())
