# Spark Schema Inference Fix

## Problem

When inserting job logs, Spark failed with:

```
pyspark.errors.exceptions.base.PySparkValueError: [CANNOT_DETERMINE_TYPE] 
Some of types cannot be determined after inferring.
```

This occurred in the `insert_job_log()` function when calling:
```python
spark.createDataFrame(data).write.mode("append").format("iceberg").saveAsTable(...)
```

## Root Cause

**Spark cannot infer schema when dictionary contains `None` values.**

### ❌ **Problematic Code**

```python
data = [{
    "job_id": str(uuid.uuid4()),
    "source_table": source_table,
    "iceberg_table": iceberg_table,
    "status": status,
    "rows_processed": int(rows_processed) if rows_processed is not None else None,  # ⚠️ Can be None
    "max_scn": int(max_scn) if max_scn is not None else None,  # ⚠️ Can be None
    "start_time": start_time,
    "end_time": end_time,
    "error_message": (error_message[:500] if error_message else None),  # ⚠️ Can be None
}]

# ❌ Spark tries to infer schema but fails with None values
spark.createDataFrame(data)
```

**Why it fails:**
- When `rows_processed=None`, Spark doesn't know if it should be `IntegerType`, `LongType`, `StringType`, etc.
- Same issue with `max_scn=None` and `error_message=None`
- Spark's schema inference requires at least one non-null value to determine type

## Solution: Explicit Schema Definition

### ✅ **Fixed Code**

```python
from pyspark.sql.types import (
    StructType, StructField, StringType, LongType, TimestampType
)

# Define explicit schema
schema = StructType([
    StructField("job_id", StringType(), False),           # NOT NULL
    StructField("source_table", StringType(), True),      # Nullable
    StructField("iceberg_table", StringType(), True),     # Nullable
    StructField("status", StringType(), True),            # Nullable
    StructField("rows_processed", LongType(), True),      # Nullable - can be None
    StructField("max_scn", LongType(), True),             # Nullable - can be None
    StructField("start_time", TimestampType(), True),     # Nullable
    StructField("end_time", TimestampType(), True),       # Nullable
    StructField("error_message", StringType(), True),     # Nullable - can be None
])

# Prepare data as tuple (matches schema order)
data = [(
    str(uuid.uuid4()),
    source_table,
    iceberg_table,
    status,
    int(rows_processed) if rows_processed is not None else None,
    int(max_scn) if max_scn is not None else None,
    start_time,
    end_time,
    error_message[:500] if error_message else None,
)]

# ✅ Create DataFrame with explicit schema
spark.createDataFrame(data, schema).write.mode("append").format("iceberg").saveAsTable(...)
```

## Key Changes

### 1. **Import Schema Types**
```python
from pyspark.sql.types import (
    StructType, StructField, StringType, LongType, TimestampType
)
```

### 2. **Define Explicit Schema**
- Each field has explicit type
- Nullable flag (`True`/`False`) for each field
- `job_id` is NOT NULL (False), others are nullable (True)

### 3. **Use Tuple Instead of Dictionary**
```python
# ❌ BEFORE: Dictionary (requires inference)
data = [{"field1": value1, "field2": value2}]

# ✅ AFTER: Tuple (matches schema order)
data = [(value1, value2)]
```

### 4. **Pass Schema to createDataFrame**
```python
spark.createDataFrame(data, schema)  # ✅ Explicit schema
```

## Benefits

| Aspect | Before | After |
|--------|--------|-------|
| **Schema inference** | ❌ Fails with None | ✅ Explicit, always works |
| **Performance** | Slower (inference) | Faster (no inference) |
| **Type safety** | ❌ Unpredictable | ✅ Guaranteed types |
| **Debugging** | Hard to trace | Clear schema definition |
| **Nullable handling** | ❌ Breaks | ✅ Properly handled |

## When to Use Explicit Schema

Use explicit schema when:

1. ✅ Data contains **None/null values**
2. ✅ You need **type guarantees** (e.g., LongType vs IntegerType)
3. ✅ Writing to **Iceberg/Delta tables** with strict schema
4. ✅ **Performance matters** (skip inference overhead)
5. ✅ Working with **production data pipelines**

Use schema inference when:
- ❌ Quick prototyping/testing
- ❌ All values are non-null
- ❌ Schema changes frequently

## Common Pitfall: Dictionary vs Tuple

### ❌ **Wrong: Dictionary with wrong order**
```python
data = [{"field2": value2, "field1": value1}]  # Order doesn't matter
spark.createDataFrame(data, schema)  # ❌ May fail or mismatch
```

### ✅ **Correct: Tuple with schema order**
```python
# Schema: field1, field2
data = [(value1, value2)]  # ✅ Must match schema order!
spark.createDataFrame(data, schema)
```

## Testing the Fix

Run the optimized pipeline:
```bash
python spark_code/oracle_to_iceberg_optimized.py \
  --oracle-table SCHEMA.TABLE \
  --iceberg-table integration.customers \
  --primary-key ID
```

**Expected behavior:**
- ✅ Job log inserted successfully
- ✅ No schema inference errors
- ✅ Null values handled correctly

## Related Spark Documentation

- [PySpark SQL Types](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/data_types.html)
- [DataFrame Creation](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.SparkSession.createDataFrame.html)
- [Schema Definition](https://spark.apache.org/docs/latest/sql-ref-datatypes.html)

## Related Files

- `spark_code/utils/checkpoint.py` - Fixed `insert_job_log()` function
- `spark_code/oracle_to_iceberg_optimized.py` - Uses the fixed function
- `spark_code/oracle_to_iceberg_simple.py` - Also uses the fixed function
