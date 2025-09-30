from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import col
from .logging import get_logger

log = get_logger(__name__)


def create_spark(app_name: str = "oracle-to-iceberg-simple") -> SparkSession:
    """Create a Spark session with minimal, safe defaults.
    Leave storage/catalog options to deployment (ConfigMap/Secrets).
    """
    builder = (
        SparkSession.builder.appName(app_name)
        .config("spark.sql.adaptive.enabled", "true")
        .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
    )
    spark = builder.getOrCreate()
    spark.sparkContext.setLogLevel("WARN")
    return spark


def ensure_db_exists(spark: SparkSession, iceberg_table: str) -> None:
    if "." in iceberg_table:
        db = iceberg_table.split(".")[0]
        spark.sql(f"CREATE DATABASE IF NOT EXISTS {db}")
        log.info(f"Database ensured: {db}")


def ensure_table_exists(spark: SparkSession, iceberg_table: str, source_df: DataFrame) -> None:
    try:
        spark.sql(f"DESCRIBE TABLE {iceberg_table}")
        log.info(f"Table exists: {iceberg_table}")
    except Exception:
        log.info(f"Creating table: {iceberg_table}")
        source_df.limit(1).write \
            .format("iceberg").mode("overwrite") \
            .option("format-version", "2") \
            .option("write.upsert.enabled", "true") \
            .saveAsTable(iceberg_table)
