from pyspark.sql import SparkSession
from logging import getLogger

logger = getLogger(__name__)

try:
    spark = SparkSession.getActiveSession()
    if spark is None:
        logger.info("No active Spark session found, creating new one")
        spark = SparkSession.builder.appName("dbt-external-runner").getOrCreate()
    else:
        logger.info("Reusing existing Spark session")
    
    spark.sql("create view integration_demo.toantt as select 1 as id")
    spark.sql("show views in integration_demo").show()
except Exception as e:
    logger.warning(f"Spark session setup issue: {e}")
    spark = None
