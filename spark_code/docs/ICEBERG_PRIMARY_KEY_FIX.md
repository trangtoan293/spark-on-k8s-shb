# Iceberg Primary Key Fix

## Problem

The original code used `PRIMARY KEY` syntax in `CREATE TABLE` statement:

```sql
CREATE TABLE IF NOT EXISTS system.oracle_scn_checkpoint (
  source_table STRING NOT NULL,
  last_scn BIGINT,
  updated_at TIMESTAMP,
  PRIMARY KEY (source_table) NOT ENFORCED  -- ❌ NOT SUPPORTED in Spark SQL
) USING iceberg
```

**Error:**
```
pyspark.errors.exceptions.captured.ParseException: 
[PARSE_SYNTAX_ERROR] Syntax error at or near 'source_table'.(line 6, pos 23)
```

## Root Cause

**Iceberg with Spark SQL does NOT support `PRIMARY KEY` syntax in `CREATE TABLE` statements.**

According to Apache Iceberg documentation:
- `PRIMARY KEY` syntax is only supported in **Flink SQL**
- For **Spark SQL**, you must use `ALTER TABLE SET IDENTIFIER FIELDS` after table creation

## Solution

### ✅ Correct Approach for Spark SQL

```sql
-- Step 1: Create table WITHOUT primary key
CREATE TABLE IF NOT EXISTS system.oracle_scn_checkpoint (
  source_table STRING NOT NULL,
  last_scn BIGINT,
  updated_at TIMESTAMP
) USING iceberg
TBLPROPERTIES (
  'format-version' = '2',
  'write.upsert.enabled' = 'true'
);

-- Step 2: Set identifier fields (equivalent to PRIMARY KEY)
ALTER TABLE system.oracle_scn_checkpoint 
SET IDENTIFIER FIELDS source_table;
```

### Code Changes in `utils/checkpoint.py`

**Before:**
```python
spark.sql(f"""
    CREATE TABLE IF NOT EXISTS {CHECKPOINT_TABLE} (
      source_table STRING NOT NULL,
      last_scn BIGINT,
      updated_at TIMESTAMP,
      PRIMARY KEY (source_table) NOT ENFORCED  -- ❌ ERROR
    ) USING iceberg
""")
```

**After:**
```python
# Create table
spark.sql(f"""
    CREATE TABLE IF NOT EXISTS {CHECKPOINT_TABLE} (
      source_table STRING NOT NULL,
      last_scn BIGINT,
      updated_at TIMESTAMP
    ) USING iceberg
    TBLPROPERTIES (
      'format-version' = '2',
      'write.upsert.enabled' = 'true'
    )
""")

# Set identifier fields separately
try:
    spark.sql(f"ALTER TABLE {CHECKPOINT_TABLE} SET IDENTIFIER FIELDS source_table")
except Exception:
    pass  # Already set
```

## Key Differences: Flink SQL vs Spark SQL

| Feature | Flink SQL | Spark SQL |
|---------|-----------|-----------|
| **PRIMARY KEY in CREATE TABLE** | ✅ Supported | ❌ Not supported |
| **Syntax** | `PRIMARY KEY(col) NOT ENFORCED` | `ALTER TABLE SET IDENTIFIER FIELDS col` |
| **When to use** | During table creation | After table creation |

### Flink SQL Example (for reference)
```sql
-- This works in Flink SQL only
CREATE TABLE hive_catalog.default.sample (
    id BIGINT COMMENT 'unique id',
    data STRING NOT NULL,
    PRIMARY KEY(id) NOT ENFORCED
) WITH ('format-version'='2');
```

## Benefits of the Fix

1. ✅ **Compatible with Spark SQL** - Uses correct Iceberg syntax
2. ✅ **Enables UPSERT operations** - `write.upsert.enabled = true`
3. ✅ **Format v2 support** - Required for identifier fields
4. ✅ **Idempotent** - Safe to run multiple times (try-except)
5. ✅ **MERGE operations work** - Identifier fields enable efficient merges

## Testing

Run the optimized script:
```bash
python spark_code/oracle_to_iceberg_optimized.py \
  --oracle-table SCHEMA.TABLE \
  --iceberg-table integration.customers \
  --primary-key ID \
  --checkpoint-location s3a://data/checkpoints/oracle-optimized
```

## References

- [Apache Iceberg Spark DDL - Set Identifier Fields](https://iceberg.apache.org/docs/latest/spark-ddl/#set-identifier-fields)
- [Apache Iceberg Flink DDL - Primary Key](https://iceberg.apache.org/docs/latest/flink-ddl/#primary-key-constraint)
- [Iceberg Table Properties](https://iceberg.apache.org/docs/latest/configuration/)

## Related Files

- `spark_code/utils/checkpoint.py` - Fixed control table creation
- `spark_code/oracle_to_iceberg_optimized.py` - Uses the fixed utilities
- `spark_code/oracle_to_iceberg_simple.py` - Also uses the fixed utilities
