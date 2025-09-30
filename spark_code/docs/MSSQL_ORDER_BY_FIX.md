# MS SQL Server ORDER BY in Subquery Fix

## Problem

MS SQL Server does not allow `ORDER BY` in subqueries (derived tables) unless `TOP`, `OFFSET`, or `FOR XML` is also specified.

### Error Message
```
com.microsoft.sqlserver.jdbc.SQLServerException: 
The ORDER BY clause is invalid in views, inline functions, derived tables, 
subqueries, and common table expressions, unless TOP, OFFSET or FOR XML is also specified.
```

### Root Cause

The original query had `ORDER BY` in the subquery:

```sql
-- ❌ WRONG - MS SQL Server doesn't allow this
(SELECT a.*, a.id AS _cdc_checkpoint_id
 FROM dbo.customers a
 WHERE a.id > 12345
 ORDER BY a.id) t  -- ❌ ORDER BY not allowed here
```

## Solution

Remove `ORDER BY` from the subquery. Spark can handle sorting if needed.

### ✅ **Fixed Query**

```sql
-- ✅ CORRECT - No ORDER BY in subquery
(SELECT a.*, a.id AS _cdc_checkpoint_id
 FROM dbo.customers a
 WHERE a.id > 12345) t  -- ✅ No ORDER BY
```

## Why This Works

1. **ORDER BY in subquery is unnecessary**
   - JDBC reads data in batches (fetchsize)
   - Order is not guaranteed across batches anyway
   - Spark can sort DataFrame if needed: `df.orderBy("id")`

2. **Performance is the same or better**
   - Removing ORDER BY can actually improve performance
   - MS SQL Server doesn't need to sort before sending data
   - Spark's distributed sorting is often more efficient

3. **Data integrity is maintained**
   - WHERE clause ensures we only get new records
   - Checkpoint tracking works the same way
   - No data loss or duplication

## Code Changes

### `utils/mssql.py` - `read_mssql_incremental()`

**Before:**
```python
if last_id:
    query = f"""
    (SELECT a.*, a.{id_column} AS _cdc_checkpoint_id
     FROM {mssql_table} a
     WHERE a.{id_column} > {last_id}
     ORDER BY a.{id_column}) t  # ❌ Error
    """
```

**After:**
```python
if last_id:
    query = f"""
    (SELECT a.*, a.{id_column} AS _cdc_checkpoint_id
     FROM {mssql_table} a
     WHERE a.{id_column} > {last_id}) t  # ✅ Fixed
    """
```

### `utils/mssql.py` - `read_mssql_with_timestamp_cdc()`

**Before:**
```python
if last_timestamp:
    query = f"""
    (SELECT a.*
     FROM {mssql_table} a
     WHERE a.{timestamp_column} > '{last_timestamp}'
     ORDER BY a.{timestamp_column}) t  # ❌ Error
    """
```

**After:**
```python
if last_timestamp:
    query = f"""
    (SELECT a.*
     FROM {mssql_table} a
     WHERE a.{timestamp_column} > '{last_timestamp}') t  # ✅ Fixed
    """
```

## Alternative Solutions (Not Used)

### Option 1: Use TOP 100 PERCENT (Workaround)

```sql
-- Works but deprecated and unnecessary
(SELECT TOP 100 PERCENT a.*, a.id AS _cdc_checkpoint_id
 FROM dbo.customers a
 WHERE a.id > 12345
 ORDER BY a.id) t
```

**Why not used:**
- `TOP 100 PERCENT` is deprecated in newer SQL Server versions
- Adds unnecessary complexity
- No real benefit over removing ORDER BY

### Option 2: Use OFFSET 0 ROWS (Workaround)

```sql
-- Works but adds overhead
(SELECT a.*, a.id AS _cdc_checkpoint_id
 FROM dbo.customers a
 WHERE a.id > 12345
 ORDER BY a.id
 OFFSET 0 ROWS) t
```

**Why not used:**
- Adds parsing and execution overhead
- More complex query plan
- No benefit over removing ORDER BY

### Option 3: Sort in Spark (If Needed)

```python
# If you really need sorted data
df = read_mssql_incremental(spark, table, last_id)
df = df.orderBy("_cdc_checkpoint_id")  # Sort in Spark if needed
```

**When to use:**
- Only if downstream processing requires sorted data
- Spark's distributed sorting is efficient
- Can sort on multiple columns easily

## Database-Specific Behavior

| Database | ORDER BY in Subquery | Notes |
|----------|---------------------|-------|
| **MS SQL Server** | ❌ Not allowed | Requires TOP/OFFSET/FOR XML |
| **Oracle** | ✅ Allowed | No restrictions |
| **MySQL** | ✅ Allowed | No restrictions |
| **PostgreSQL** | ✅ Allowed | No restrictions |

## Testing

### Before Fix
```bash
python spark_code/mssql_to_iceberg.py \
  --mssql-table dbo.customers \
  --iceberg-table integration.customers \
  --primary-key id

# ❌ Error: ORDER BY clause is invalid in derived tables
```

### After Fix
```bash
python spark_code/mssql_to_iceberg.py \
  --mssql-table dbo.customers \
  --iceberg-table integration.customers \
  --primary-key id

# ✅ Works! Data ingested successfully
```

## Impact

### ✅ **No Negative Impact**

- Data integrity: ✅ Same
- Performance: ✅ Same or better
- Functionality: ✅ Same
- Checkpoint tracking: ✅ Same

### ✅ **Positive Impact**

- MS SQL Server compatibility: ✅ Fixed
- Query complexity: ✅ Simpler
- Performance: ✅ Potentially faster (no sorting overhead)

## Best Practices

### 1. **Don't rely on ORDER BY in JDBC reads**
```python
# ❌ BAD - Assumes data comes in order
df = read_mssql_incremental(spark, table, last_id)
first_row = df.first()  # Order not guaranteed

# ✅ GOOD - Explicitly sort if needed
df = read_mssql_incremental(spark, table, last_id)
df = df.orderBy("id")
first_row = df.first()  # Order guaranteed
```

### 2. **Use WHERE clause for filtering, not ORDER BY**
```python
# ✅ GOOD - WHERE clause ensures we get right data
query = f"SELECT * FROM table WHERE id > {last_id}"

# ❌ BAD - ORDER BY doesn't filter data
query = f"SELECT * FROM table ORDER BY id"
```

### 3. **Let Spark handle sorting**
```python
# ✅ GOOD - Spark's distributed sorting
df = read_mssql_incremental(spark, table, last_id)
df = df.orderBy("id").coalesce(1)  # Sort and write to single file

# ❌ BAD - Database sorting in subquery
# (Not possible in MS SQL anyway)
```

## Related Files

- `spark_code/utils/mssql.py` - Fixed ORDER BY in subqueries
- `spark_code/mssql_to_iceberg.py` - Uses fixed utilities
- `spark_code/MSSQL_SETUP_GUIDE.md` - MS SQL Server setup guide

## References

- [MS SQL Server ORDER BY Restrictions](https://learn.microsoft.com/en-us/sql/t-sql/queries/select-order-by-clause-transact-sql)
- [Spark JDBC Data Source](https://spark.apache.org/docs/latest/sql-data-sources-jdbc.html)

## Compliance

This fix follows project standards:

- ✅ **[SF] Simplicity First** - Simpler query without ORDER BY
- ✅ **[ISA] Industry Standards** - Follows MS SQL Server rules
- ✅ **[PA] Performance Awareness** - No performance degradation
- ✅ **[CA] Clean Architecture** - Fixed at utility level
