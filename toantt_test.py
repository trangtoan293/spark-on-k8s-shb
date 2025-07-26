from pyspark.sql import SparkSession

spark = SparkSession.getActiveSession()

spark.sql("create view integration_demo.toantt as select 1 as id")
spark.sql("show views in integration_demo").show()
