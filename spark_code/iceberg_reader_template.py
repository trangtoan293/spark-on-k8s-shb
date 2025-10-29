#!/usr/bin/env python3
"""Iceberg Data Reader Template
===============================

Template để đọc dữ liệu từ Iceberg table và thực hiện transformation.
Cấu trúc này phù hợp làm mẫu cho các pipeline xử lý dữ liệu.

Usage:
    python iceberg_reader_template.py --table catalog.database.table_name
    python iceberg_reader_template.py --table catalog.database.table_name --result-table catalog.database.output_table
"""

from __future__ import annotations

import argparse
import sys
from typing import Optional

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col, monotonically_increasing_id
from pyspark.sql.types import DoubleType
from pyspark.sql.functions import udf

from rapidfuzz import fuzz

from utils.logging import get_logger
from utils.spark import create_spark

log = get_logger(__name__)


def _safe_ratio(left: object, right: object) -> float:
    """Tính toán fuzz.ratio an toàn cho các giá trị null."""
    if left is None or right is None:
        return 0.0

    try:
        return float(fuzz.ratio(str(left), str(right)))
    except Exception as exc:  # noqa: BLE001 - ghi nhận lỗi và trả về 0
        log.warning("Không thể tính fuzz.ratio cho giá trị %s và %s: %s", left, right, exc)
        return 0.0


ratio_udf = udf(_safe_ratio, DoubleType())


def read_from_iceberg(spark: SparkSession, table_name: str) -> DataFrame:
    """Đọc dữ liệu từ Iceberg table."""
    log.info("Đọc dữ liệu từ Iceberg table: %s", table_name)

    try:
        df = spark.read.format("iceberg").load(table_name)
        log.info("Đã đọc dữ liệu hiện tại của table")

        # Log thông tin cơ bản về DataFrame
        log.info("Số dòng: %s", f"{df.count():,}")
        log.info("Số cột: %d", len(df.columns))
        log.info("Các cột: %s", ", ".join(df.columns))

        return df

    except Exception as exc:  # noqa: BLE001 - ghi log chi tiết và chuyển tiếp
        log.error("Lỗi khi đọc dữ liệu từ Iceberg table %s: %s", table_name, exc)
        raise


def transform_data(df: DataFrame) -> DataFrame:
    """Thực hiện transformation trên dữ liệu bằng cách dò tìm bản ghi tương đồng."""
    log.info("Bắt đầu transformation dữ liệu - đối chiếu bản ghi tương tự dựa trên fuzz.ratio")

    required_columns = ["F_NAME", "M_NAME", "L_NAME", "D_O_B", "SEX_CD"]
    missing_columns = [column for column in required_columns if column not in df.columns]
    if missing_columns:
        raise ValueError(f"Thiếu các cột cần thiết trong DataFrame: {', '.join(missing_columns)}")

    # Chuẩn bị dữ liệu với khoá định danh cho từng bản ghi
    prepared_df = (
        df.select(*required_columns)
        .withColumn("record_id", monotonically_increasing_id())
    )

    left_alias = prepared_df.alias("left")
    right_alias = prepared_df.alias("right")

    # Chỉ so sánh cặp bản ghi có chung ngày sinh & giới tính để giảm tổ hợp
    join_condition = (
        (col("left.SEX_CD") == col("right.SEX_CD"))
        & (col("left.D_O_B") == col("right.D_O_B"))
        & (col("left.record_id") < col("right.record_id"))
    )

    candidate_pairs = left_alias.join(right_alias, join_condition, "inner")

    if candidate_pairs.rdd.isEmpty():
        log.info("Không tìm thấy cặp bản ghi nào để so sánh.")
        return candidate_pairs.select(
            col("left.record_id").alias("left_record_id"),
            col("right.record_id").alias("right_record_id"),
        )

    scored_pairs = (
        candidate_pairs
        .select(
            col("left.record_id").alias("left_record_id"),
            col("right.record_id").alias("right_record_id"),
            col("left.F_NAME").alias("left_F_NAME"),
            col("right.F_NAME").alias("right_F_NAME"),
            col("left.M_NAME").alias("left_M_NAME"),
            col("right.M_NAME").alias("right_M_NAME"),
            col("left.L_NAME").alias("left_L_NAME"),
            col("right.L_NAME").alias("right_L_NAME"),
            col("left.D_O_B").alias("left_D_O_B"),
            col("right.D_O_B").alias("right_D_O_B"),
            col("left.SEX_CD").alias("left_SEX_CD"),
            col("right.SEX_CD").alias("right_SEX_CD"),
            ratio_udf(col("left.F_NAME"), col("right.F_NAME")).alias("F_NAME_similarity"),
            ratio_udf(col("left.M_NAME"), col("right.M_NAME")).alias("M_NAME_similarity"),
            ratio_udf(col("left.L_NAME"), col("right.L_NAME")).alias("L_NAME_similarity"),
            ratio_udf(col("left.D_O_B"), col("right.D_O_B")).alias("D_O_B_similarity"),
            ratio_udf(col("left.SEX_CD"), col("right.SEX_CD")).alias("SEX_CD_similarity"),
        )
        .withColumn(
            "avg_similarity",
            (
                col("F_NAME_similarity")
                + col("M_NAME_similarity")
                + col("L_NAME_similarity")
                + col("D_O_B_similarity")
                + col("SEX_CD_similarity")
            )
            / 5.0,
        )
    )

    log.info("Đã tính xong hệ số tương đồng cho %s cặp bản ghi", scored_pairs.count())
    return scored_pairs


def process_iceberg_data(table_name: str, result_table_name: Optional[str] = None) -> DataFrame:
    """Pipeline hoàn chỉnh: đọc từ Iceberg -> transform -> output."""
    spark = create_spark("iceberg-reader")

    try:
        # Step 1: Đọc dữ liệu từ Iceberg
        source_df = read_from_iceberg(spark, table_name)

        # Step 2: Transformation
        result_df = transform_data(source_df)

        # Step 3: Save result to Iceberg table nếu được cấu hình
        if result_table_name:
            log.info("Ghi kết quả vào Iceberg table: %s", result_table_name)
            result_df.writeTo(result_table_name).createOrReplace()
        else:
            log.warning("Không có result_table_name, pipeline chỉ trả về DataFrame")

        return result_df

    except Exception as exc:  # noqa: BLE001 - ghi log chi tiết và chuyển tiếp
        log.error("Pipeline thất bại: %s", exc)
        raise
    finally:
        spark.stop()
        log.info("Spark session đã được đóng")


def main() -> None:
    """Entry point chạy pipeline từ dòng lệnh."""
    parser = argparse.ArgumentParser(description="Iceberg Data Reader Template")

    parser.add_argument(
        "--table",
        required=True,
        help="Iceberg table name (catalog.database.table)",
    )
    parser.add_argument(
        "--result-table",
        help="Tên Iceberg table kết quả (optional)",
    )

    args = parser.parse_args()

    try:
        process_iceberg_data(
            table_name=args.table,
            result_table_name=args.result_table,
        )
        log.info("Pipeline hoàn tất thành công!")
    except Exception as exc:  # noqa: BLE001 - ghi log chi tiết và trả mã lỗi phù hợp
        log.error("Execution failed: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
