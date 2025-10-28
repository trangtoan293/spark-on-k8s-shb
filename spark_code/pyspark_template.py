#!/usr/bin/env python3
"""
Iceberg Data Reader Template
============================

Template để đọc dữ liệu từ Iceberg table và thực hiện transformation.
Cấu trúc này có thể được sử dụng làm mẫu cho các pipeline xử lý dữ liệu.

Usage:
    python iceberg_reader_template.py --table catalog.database.table_name
    python iceberg_reader_template.py --table catalog.database.table_name --output-path /path/to/output
"""

import sys
import argparse
from typing import Optional
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col

# Import utilities
from utils.logging import get_logger
from utils.spark import create_spark

log = get_logger(__name__)


def read_from_iceberg(
    spark: SparkSession,
    table_name: str
) -> DataFrame:
    """
    Đọc dữ liệu từ Iceberg table với các tùy chọn time travel
    
    Args:
        spark: Spark session
        table_name: Tên table theo định dạng catalog.database.table
    
    Returns:
        DataFrame: Dữ liệu từ Iceberg table
    """
    log.info(f"Đọc dữ liệu từ Iceberg table: {table_name}")
    
    try:
        
        df = spark.read.format("iceberg").load(table_name)
        log.info("Đ đọc dữ liệu hiện tại của table")
        
        # Log thông tin cơ bản về DataFrame
        log.info(f"Số dòng: {df.count():,}")
        log.info(f"Số cột: {len(df.columns)}")
        log.info(f"Các cột: {', '.join(df.columns)}")
        
        return df
        
    except Exception as e:
        log.error(f"Lỗi khi đọc dữ liệu từ Iceberg table {table_name}: {e}")
        raise


def transform_data(df: DataFrame) -> DataFrame:
    """
    Thực hiện transformation trên dữ liệu
    
    Args:
        df: DataFrame đầu vào từ Iceberg
    
    Returns:
        DataFrame: DataFrame sau khi transform
    """
    log.info("Bắt đầu transformation dữ liệu")
    
    # TODO: Thêm logic transformation tại đây
    # Ví dụ:
    # - Filter dữ liệu
    # - Add new columns
    # - Aggregations
    # - Joins với các table khác
    # - Data cleansing
    # - Business logic
    
    # Ví dụ cơ bản (có thể thay đổi):
    # transformed_df = df.filter(col("status") == "active") \
    #                   .withColumn("processed_at", current_timestamp()) \
    #                   .dropDuplicates()
    
    transformed_df = df  # Placeholder - thay bằng logic thực tế
    
    log.info("Hoàn thành transformation dữ liệu")
    return transformed_df


def process_iceberg_data(
    table_name: str,
    result_table_name: Optional[str] = None
) -> DataFrame:
    """
    Pipeline hoàn chỉnh: đọc từ Iceberg -> transform -> output
    
    Args:
        table_name: Tên Iceberg table
        result_table_name: Tên Iceberg table kết quả (optional)
    
    Returns:
        DataFrame: Kết quả cuối cùng
    """
    # Tạo Spark session
    spark = create_spark("iceberg-reader")
    
    try:
        # Step 1: Đọc dữ liệu từ Iceberg
        source_df = read_from_iceberg(
            spark, table_name
        )
        
        # Step 2: Transformation
        result_df = transform_data(source_df)
        
        # Step 3: Save result to iceberg table
        result_df.writeTo(result_table_name).createOrReplace()
        
        
    except Exception as e:
        log.error(f"Pipeline thất bại: {e}")
        raise
    finally:
        spark.stop()
        log.info("Spark session đã được đóng")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Iceberg Data Reader Template"
    )
    
    # Required arguments
    parser.add_argument("--table", required=True, 
                       help="Iceberg table name (catalog.database.table)")
    
    # Optional arguments
    parser.add_argument("--result-table", 
                            help="Tên Iceberg table kết quả (optional)")

    args = parser.parse_args()
    
    try:
        # Execute pipeline
        process_iceberg_data(
            table_name=args.table,
            result_table_name=args.result_table 
        )
        
        log.info("Pipeline hoàn tất thành công!")
        
    except Exception as e:
        log.error(f"Execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
