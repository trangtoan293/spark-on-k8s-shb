# JDBC Partitioning in Spark - Why We Removed It

## Problem

When using JDBC partitioning in Spark, you encountered this error:

```
pyspark.errors.exceptions.captured.IllegalArgumentException: 
requirement failed: When reading JDBC data sources, users need to specify 
all or none for the following options: 'partitionColumn', 'lowerBound', 
'upperBound', and 'numPartitions'
```

## Root Cause

Spark JDBC requires **ALL 4 parameters** for partitioning:

```python
# ❌ WRONG - Partial parameters cause error
options = {
    "partitionColumn": "ORA_ROWSCN",
    "numPartitions": "4"
    # Missing: lowerBound, upperBound
}
```

```python
# ✅ CORRECT - All 4 parameters required
options = {
    "partitionColumn": "ORA_ROWSCN",
    "lowerBound": "1000000",      # Minimum SCN value
    "upperBound": "2000000",      # Maximum SCN value
    "numPartitions": "4"
}
```

## Why Partitioning is Complex for Oracle CDC

### **1. Dynamic SCN Range**
- SCN values change constantly
- Hard to predict `lowerBound` and `upperBound`
- Would need extra query to get MIN/MAX SCN first

### **2. Uneven Distribution**
- SCN values may not be evenly distributed
- Some partitions could be empty, others overloaded
- Defeats the purpose of parallelization

### **3. Additional Overhead**
```python
# Would need this extra query first:
min_max_query = f"""
(SELECT MIN(ORA_ROWSCN) as MIN_SCN, MAX(ORA_ROWSCN) as MAX_SCN
 FROM {table}
 WHERE ORA_ROWSCN > {last_scn}) t
"""
# Then use results for lowerBound/upperBound
# More complexity, more queries, questionable benefit
```

## Our Solution: Simplified Optimization

Instead of complex partitioning, we use **simpler, more effective optimizations**:

### ✅ **1. Increased Fetchsize**
```python
options = {
    "fetchsize": "10000"  # Up from 5000 default
}
```
**Benefit:** Fewer round trips to Oracle, better throughput

### ✅ **2. Fast Pre-check**
```python
# Query only MAX(ORA_ROWSCN) and COUNT(*)
# Avoids reading full table when no new data
has_new_data, max_scn = check_new_data_exists(spark, table, last_scn)
```
**Benefit:** Skip entire read operation if no changes

### ✅ **3. DataFrame Caching**
```python
df.cache()
row_count = df.count()
# Reuse cached data for subsequent operations
```
**Benefit:** Avoid re-reading data multiple times

### ✅ **4. Optimized Checkpoint**
```python
# Reuse max_scn from pre-check
max_scn = max_scn_in_source  # Already have it!
```
**Benefit:** No need to scan DataFrame again

## Performance Comparison

| Approach | Complexity | Setup Queries | Benefit |
|----------|-----------|---------------|---------|
| **JDBC Partitioning** | High | 2-3 queries | Moderate (if data is large and evenly distributed) |
| **Increased Fetchsize** | Low | 0 queries | Good (always helps) |
| **Fast Pre-check** | Low | 1 query | Excellent (avoids full read) |
| **Caching** | Low | 0 queries | Good (for multiple operations) |

## When to Use JDBC Partitioning

JDBC partitioning is beneficial when:

1. ✅ Reading **very large tables** (millions of rows)
2. ✅ Partition column has **known, stable range** (e.g., ID from 1 to 1000000)
3. ✅ Data is **evenly distributed** across range
4. ✅ You have **multiple executors** to parallelize

For **incremental CDC with SCN**, these conditions rarely apply:
- ❌ Incremental reads are usually small (only changed rows)
- ❌ SCN range is dynamic and unpredictable
- ❌ Distribution may be uneven (burst of changes)

## Recommended Approach

For Oracle CDC with ORA_ROWSCN, stick with our simplified optimization:

```bash
python oracle_to_iceberg_optimized.py \
  --oracle-table SCHEMA.TABLE \
  --iceberg-table integration.customers \
  --primary-key ID
```

**No partition parameters needed!** The optimizations are automatic:
- ✅ Fast pre-check (MAX/COUNT query)
- ✅ Increased fetchsize (10000)
- ✅ DataFrame caching
- ✅ Efficient checkpoint reuse

## If You Really Need Partitioning

If your use case requires JDBC partitioning (e.g., initial full load of huge table), you can add it manually:

```python
# Get SCN range first
min_scn_query = f"(SELECT MIN(ORA_ROWSCN) as m FROM {table}) t"
max_scn_query = f"(SELECT MAX(ORA_ROWSCN) as m FROM {table}) t"

min_scn = spark.read.jdbc(..., min_scn_query).collect()[0][0]
max_scn = spark.read.jdbc(..., max_scn_query).collect()[0][0]

# Then use for partitioning
options = {
    "partitionColumn": "ORA_ROWSCN",
    "lowerBound": str(min_scn),
    "upperBound": str(max_scn),
    "numPartitions": "8"
}
```

But for **incremental CDC**, this adds more overhead than benefit.

## References

- [Spark JDBC Data Source Documentation](https://spark.apache.org/docs/latest/sql-data-sources-jdbc.html)
- [JDBC Partitioning Best Practices](https://spark.apache.org/docs/latest/sql-performance-tuning.html)

## Related Files

- `spark_code/utils/oracle_optimized.py` - Simplified without partitioning
- `spark_code/oracle_to_iceberg_optimized.py` - Uses simplified approach
