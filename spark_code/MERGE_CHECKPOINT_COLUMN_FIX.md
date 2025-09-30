# MERGE Checkpoint Column Detection Fix

## Problem

The MERGE operation was hardcoded to use `_cdc_checkpoint_scn` (Oracle's checkpoint column), causing failures when merging data from MySQL or MS SQL Server which use `_cdc_checkpoint_id`.

### Error Message
```
pyspark.errors.exceptions.captured.AnalysisException: 
[UNRESOLVED_COLUMN.WITH_SUGGESTION] A column or function parameter with name 
`s`.`_cdc_checkpoint_scn` cannot be resolved. 
Did you mean one of the following? [`s`.`_cdc_checkpoint_id`, ...]
```

### Root Cause

The `merge_simple()` function had hardcoded checkpoint column:

```python
# ❌ WRONG - Hardcoded Oracle column
merge_sql = f"""
MERGE INTO {iceberg_table} AS t
USING (SELECT * FROM {temp_view}) AS s
ON {join_cond}
WHEN MATCHED AND s._cdc_checkpoint_scn > COALESCE(t._cdc_checkpoint_scn, 0) THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *
"""
```

This failed for MySQL/MS SQL data which has `_cdc_checkpoint_id` instead.

## Solution

Automatically detect the checkpoint column from the source DataFrame.

### ✅ **Fixed Logic**

```python
# Detect checkpoint column dynamically
checkpoint_col = None
if "_cdc_checkpoint_scn" in source_df.columns:
    checkpoint_col = "_cdc_checkpoint_scn"  # Oracle
    log.info("Detected Oracle checkpoint column: _cdc_checkpoint_scn")
elif "_cdc_checkpoint_id" in source_df.columns:
    checkpoint_col = "_cdc_checkpoint_id"   # MySQL/MS SQL
    log.info("Detected MySQL/MS SQL checkpoint column: _cdc_checkpoint_id")
else:
    raise ValueError("No checkpoint column found")

# Use detected column in MERGE
merge_sql = f"""
MERGE INTO {iceberg_table} AS t
USING (SELECT * FROM {temp_view}) AS s
ON {join_cond}
WHEN MATCHED AND s.{checkpoint_col} > COALESCE(t.{checkpoint_col}, 0) THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *
"""
```

## Checkpoint Columns by Database

| Database | Checkpoint Column | Description |
|----------|------------------|-------------|
| **Oracle** | `_cdc_checkpoint_scn` | System Change Number (SCN) |
| **MySQL** | `_cdc_checkpoint_id` | Auto-increment ID |
| **MS SQL Server** | `_cdc_checkpoint_id` | IDENTITY column ID |

## Code Changes

### `utils/merge.py` - Updated `merge_simple()`

**Before:**
```python
def merge_simple(spark: SparkSession, source_df: DataFrame, iceberg_table: str, primary_key: str) -> None:
    """Simple MERGE using equality on key(s) and SCN gating."""
    # ... setup code ...
    
    # ❌ Hardcoded Oracle column
    merge_sql = f"""
    MERGE INTO {iceberg_table} AS t
    USING (SELECT * FROM {temp_view}) AS s
    ON {join_cond}
    WHEN MATCHED AND s._cdc_checkpoint_scn > COALESCE(t._cdc_checkpoint_scn, 0) THEN UPDATE SET *
    WHEN NOT MATCHED THEN INSERT *
    """
```

**After:**
```python
def merge_simple(spark: SparkSession, source_df: DataFrame, iceberg_table: str, primary_key: str) -> None:
    """
    Simple MERGE using equality on key(s) and checkpoint gating.
    - Detects checkpoint column automatically
    """
    # ... setup code ...
    
    # ✅ Detect checkpoint column
    checkpoint_col = None
    if "_cdc_checkpoint_scn" in source_df.columns:
        checkpoint_col = "_cdc_checkpoint_scn"
        log.info("Detected Oracle checkpoint column: _cdc_checkpoint_scn")
    elif "_cdc_checkpoint_id" in source_df.columns:
        checkpoint_col = "_cdc_checkpoint_id"
        log.info("Detected MySQL/MS SQL checkpoint column: _cdc_checkpoint_id")
    else:
        raise ValueError("No checkpoint column found (_cdc_checkpoint_scn or _cdc_checkpoint_id)")
    
    # ✅ Use detected column
    merge_sql = f"""
    MERGE INTO {iceberg_table} AS t
    USING (SELECT * FROM {temp_view}) AS s
    ON {join_cond}
    WHEN MATCHED AND s.{checkpoint_col} > COALESCE(t.{checkpoint_col}, 0) THEN UPDATE SET *
    WHEN NOT MATCHED THEN INSERT *
    """
    log.info(f"Running MERGE with checkpoint column: {checkpoint_col}")
```

## How It Works

### 1. **Column Detection**

The function checks which checkpoint column exists in the source DataFrame:

```python
if "_cdc_checkpoint_scn" in source_df.columns:
    checkpoint_col = "_cdc_checkpoint_scn"  # Oracle
elif "_cdc_checkpoint_id" in source_df.columns:
    checkpoint_col = "_cdc_checkpoint_id"   # MySQL/MS SQL
else:
    raise ValueError("No checkpoint column found")
```

### 2. **Dynamic MERGE Query**

The MERGE query uses the detected column:

```sql
-- For Oracle data
WHEN MATCHED AND s._cdc_checkpoint_scn > COALESCE(t._cdc_checkpoint_scn, 0) THEN UPDATE SET *

-- For MySQL/MS SQL data
WHEN MATCHED AND s._cdc_checkpoint_id > COALESCE(t._cdc_checkpoint_id, 0) THEN UPDATE SET *
```

### 3. **Logging**

Clear logs show which checkpoint column is being used:

```
2025-09-30 08:56:53 [INFO] utils.merge - Detected MySQL/MS SQL checkpoint column: _cdc_checkpoint_id
2025-09-30 08:56:53 [INFO] utils.merge - Running MERGE with checkpoint column: _cdc_checkpoint_id
```

## Testing

### Oracle Data
```bash
python spark_code/oracle_to_iceberg.py \
  --oracle-table HR.CUSTOMERS \
  --iceberg-table integration.customers \
  --primary-key ID

# ✅ Logs show: Detected Oracle checkpoint column: _cdc_checkpoint_scn
# ✅ MERGE uses: s._cdc_checkpoint_scn > COALESCE(t._cdc_checkpoint_scn, 0)
```

### MySQL Data
```bash
python spark_code/mysql_to_iceberg.py \
  --mysql-table customers \
  --iceberg-table integration.customers \
  --primary-key id

# ✅ Logs show: Detected MySQL/MS SQL checkpoint column: _cdc_checkpoint_id
# ✅ MERGE uses: s._cdc_checkpoint_id > COALESCE(t._cdc_checkpoint_id, 0)
```

### MS SQL Data
```bash
python spark_code/mssql_to_iceberg.py \
  --mssql-table dbo.customers \
  --iceberg-table integration.customers \
  --primary-key id

# ✅ Logs show: Detected MySQL/MS SQL checkpoint column: _cdc_checkpoint_id
# ✅ MERGE uses: s._cdc_checkpoint_id > COALESCE(t._cdc_checkpoint_id, 0)
```

## Benefits

### ✅ **1. Multi-Database Support**
- Works with Oracle, MySQL, and MS SQL Server
- No code changes needed per database
- Automatic detection

### ✅ **2. Error Prevention**
- Fails fast if checkpoint column is missing
- Clear error message
- No silent failures

### ✅ **3. Maintainability**
- Single merge function for all databases
- No duplicate code
- Easy to extend for new databases

### ✅ **4. Observability**
- Logs show which checkpoint column is used
- Easy to debug
- Clear audit trail

## Edge Cases Handled

### 1. **Missing Checkpoint Column**
```python
# If DataFrame has neither checkpoint column
raise ValueError("No checkpoint column found (_cdc_checkpoint_scn or _cdc_checkpoint_id)")
```

### 2. **Both Columns Present** (Shouldn't happen)
```python
# Oracle column takes precedence
if "_cdc_checkpoint_scn" in source_df.columns:
    checkpoint_col = "_cdc_checkpoint_scn"  # Use this first
elif "_cdc_checkpoint_id" in source_df.columns:
    checkpoint_col = "_cdc_checkpoint_id"   # Fallback
```

### 3. **Empty DataFrame**
```python
# Already handled before checkpoint detection
if clean_df.count() == 0:
    log.info("No valid rows to merge")
    return
```

## MERGE Logic

The MERGE operation works the same way for all databases:

```sql
MERGE INTO {iceberg_table} AS t
USING (SELECT * FROM {temp_view}) AS s
ON {join_condition}
WHEN MATCHED AND s.{checkpoint_col} > COALESCE(t.{checkpoint_col}, 0) THEN 
    UPDATE SET *
WHEN NOT MATCHED THEN 
    INSERT *
```

**Key Points:**
- **MATCHED**: Update only if source checkpoint > target checkpoint (prevents stale updates)
- **NOT MATCHED**: Insert new rows
- **COALESCE(..., 0)**: Handle NULL checkpoints in target table

## Related Files

- `spark_code/utils/merge.py` - Fixed merge logic
- `spark_code/utils/oracle.py` - Adds `_cdc_checkpoint_scn`
- `spark_code/utils/mysql.py` - Adds `_cdc_checkpoint_id`
- `spark_code/utils/mssql.py` - Adds `_cdc_checkpoint_id`

## Compliance

This fix follows project standards:

- ✅ **[SF] Simplicity First** - Simple column detection logic
- ✅ **[DRY] Don't Repeat Yourself** - Single merge function for all databases
- ✅ **[CA] Clean Architecture** - Clear separation of concerns
- ✅ **[REH] Robust Error Handling** - Fails fast with clear error
- ✅ **[RP] Readability Priority** - Clear logs and comments
