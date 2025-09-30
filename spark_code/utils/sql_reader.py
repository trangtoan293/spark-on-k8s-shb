"""SQL File Reader Utility - Reads SQL from local, volume, or S3/MinIO sources"""
import os
from typing import Optional
from pyspark.sql import SparkSession
from .logging import get_logger

log = get_logger(__name__)


def read_sql_file(spark: SparkSession, file_path: str) -> str:
    """
    Read SQL content from multiple sources: local, K8s volume, or S3/MinIO.
    
    Args:
        spark: Active Spark session
        file_path: Path to SQL file (local, S3, or volume path)
        
    Returns:
        SQL content as string
        
    Raises:
        FileNotFoundError: If file not found in any location
    """
    log.info(f"Reading SQL file: {file_path}")
    
    # Try local file first
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        log.info(f"✓ Read SQL file locally: {len(content)} characters")
        return content
    
    # Try K8s mounted volume
    volume_path = f"/opt/spark/work-dir/{os.path.basename(file_path)}"
    if os.path.exists(volume_path):
        with open(volume_path, 'r', encoding='utf-8') as f:
            content = f.read()
        log.info(f"✓ Read SQL file from volume: {len(content)} characters")
        return content
    
    # Try S3/MinIO using Spark
    try:
        sql_df = spark.read.text(file_path)
        rows = sql_df.collect()
        content = '\n'.join([row.value for row in rows])
        log.info(f"✓ Read SQL file from S3: {len(content)} characters")
        return content
    except Exception as s3_error:
        log.warning(f"Failed to read from S3: {s3_error}")
    
    raise FileNotFoundError(f"SQL file not found in any location: {file_path}")
