from typing import List
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import col
from .logging import get_logger

log = get_logger(__name__)


def merge_simple(spark: SparkSession, source_df: DataFrame, iceberg_table: str, primary_key: str) -> None:
    """
    Simple MERGE using equality on key(s) and checkpoint gating.
    
    - Filters rows with NULL keys, drops duplicates by keys
    - Detects checkpoint column automatically (_cdc_checkpoint_scn for Oracle, _cdc_checkpoint_id for MySQL/MS SQL)
    - Updates when source checkpoint > target checkpoint
    - Inserts when not matched
    """
    keys: List[str] = [k.strip() for k in primary_key.split(",") if k.strip()]
    if not keys:
        raise ValueError("primary_key must not be empty")

    cond = col(keys[0]).isNotNull()
    for k in keys[1:]:
        cond = cond & col(k).isNotNull()

    clean_df = source_df.filter(cond).dropDuplicates(keys)
    if clean_df.count() == 0:
        log.info("No valid rows to merge")
        return

    temp_view = "src_updates"
    clean_df.createOrReplaceTempView(temp_view)

    # Detect checkpoint column (Oracle uses _cdc_checkpoint_scn, MySQL/MS SQL use _cdc_checkpoint_id)
    checkpoint_col = None
    if "_cdc_checkpoint_scn" in source_df.columns:
        checkpoint_col = "_cdc_checkpoint_scn"
        log.info("Detected Oracle checkpoint column: _cdc_checkpoint_scn")
    elif "_cdc_checkpoint_id" in source_df.columns:
        checkpoint_col = "_cdc_checkpoint_id"
        log.info("Detected MySQL/MS SQL checkpoint column: _cdc_checkpoint_id")
    else:
        raise ValueError("No checkpoint column found (_cdc_checkpoint_scn or _cdc_checkpoint_id)")

    join_cond = " AND ".join([f"t.{k} = s.{k}" for k in keys])

    merge_sql = f"""
    MERGE INTO {iceberg_table} AS t
    USING (SELECT * FROM {temp_view}) AS s
    ON {join_cond}
    WHEN MATCHED AND s.{checkpoint_col} > COALESCE(t.{checkpoint_col}, 0) THEN UPDATE SET *
    WHEN NOT MATCHED THEN INSERT *
    """
    log.info(f"Running MERGE with checkpoint column: {checkpoint_col}")
    spark.sql(merge_sql).show(0)
