from typing import List
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import col
from .logging import get_logger

log = get_logger(__name__)


def merge_simple(spark: SparkSession, source_df: DataFrame, iceberg_table: str, primary_key: str) -> None:
    """Simple MERGE using equality on key(s) and SCN gating.
    - Filters rows with NULL keys, drops duplicates by keys
    - Updates when source._cdc_checkpoint_scn > target._cdc_checkpoint_scn
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

    join_cond = " AND ".join([f"t.{k} = s.{k}" for k in keys])

    merge_sql = f"""
    MERGE INTO {iceberg_table} AS t
    USING (SELECT * FROM {temp_view}) AS s
    ON {join_cond}
    WHEN MATCHED AND s._cdc_checkpoint_scn > COALESCE(t._cdc_checkpoint_scn, 0) THEN UPDATE SET *
    WHEN NOT MATCHED THEN INSERT *
    """
    log.info("Running MERGE")
    spark.sql(merge_sql).show(0)
