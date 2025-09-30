# Data Lineage & Metadata Tracking

## Overview

All ingested data now includes source metadata columns to track data lineage and origin. This allows you to easily identify which database system and table each row came from.

## Metadata Columns Added to Data

Every row ingested into Iceberg tables now includes these metadata columns:

### **1. `_source_system`** (STRING)
- Database type: `oracle`, `mysql`, or `mssql`
- Identifies which database system the data came from
- Useful for multi-source data lakes

### **2. `_source_table`** (STRING)
- Original table name from source database
- Includes schema prefix for MS SQL (e.g., `dbo.customers`)
- Preserves full qualified name for Oracle (e.g., `SCHEMA.TABLE`)

### **3. `_cdc_checkpoint_scn` or `_cdc_checkpoint_id`** (BIGINT)
- Oracle: SCN (System Change Number)
- MySQL/MS SQL: ID value used for CDC
- Used for incremental loading checkpoint

### **4. `_cdc_extracted_at`** (TIMESTAMP)
- Timestamp when data was extracted from source
- UTC timezone
- Useful for tracking data freshness

## Example Data

### Oracle Source
```sql
SELECT 
    customer_id,
    name,
    email,
    _source_system,      -- 'oracle'
    _source_table,       -- 'HR.CUSTOMERS'
    _cdc_checkpoint_scn, -- 1332212
    _cdc_extracted_at    -- 2025-09-30 04:44:32
FROM integration.customers
WHERE _source_system = 'oracle';
```

### MySQL Source
```sql
SELECT 
    order_id,
    customer_id,
    total_amount,
    _source_system,      -- 'mysql'
    _source_table,       -- 'orders'
    _cdc_checkpoint_id,  -- 12345
    _cdc_extracted_at    -- 2025-09-30 05:30:15
FROM integration.orders
WHERE _source_system = 'mysql';
```

### MS SQL Source
```sql
SELECT 
    product_id,
    product_name,
    price,
    _source_system,      -- 'mssql'
    _source_table,       -- 'dbo.products'
    _cdc_checkpoint_id,  -- 98765
    _cdc_extracted_at    -- 2025-09-30 06:15:42
FROM integration.products
WHERE _source_system = 'mssql';
```

## Job Run Logs Enhancement

The `etladmin.job_run_logs` table now includes `source_system` column:

### Updated Schema
```sql
CREATE TABLE etladmin.job_run_logs (
    job_id STRING NOT NULL,
    source_system STRING,        -- NEW: 'oracle', 'mysql', 'mssql'
    source_table STRING,
    iceberg_table STRING,
    status STRING,
    rows_processed BIGINT,
    max_scn BIGINT,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    error_message STRING
) USING iceberg;
```

### Query Examples

**Find all Oracle ingestion jobs:**
```sql
SELECT 
    job_id,
    source_system,
    source_table,
    iceberg_table,
    status,
    rows_processed,
    start_time,
    end_time
FROM etladmin.job_run_logs
WHERE source_system = 'oracle'
ORDER BY start_time DESC;
```

**Compare ingestion performance across databases:**
```sql
SELECT 
    source_system,
    COUNT(*) as total_jobs,
    SUM(rows_processed) as total_rows,
    AVG(rows_processed) as avg_rows_per_job,
    AVG(UNIX_TIMESTAMP(end_time) - UNIX_TIMESTAMP(start_time)) as avg_duration_seconds
FROM etladmin.job_run_logs
WHERE status = 'SUCCESS'
GROUP BY source_system;
```

**Find failed jobs by source system:**
```sql
SELECT 
    source_system,
    source_table,
    iceberg_table,
    error_message,
    start_time
FROM etladmin.job_run_logs
WHERE status = 'FAILED'
ORDER BY start_time DESC
LIMIT 10;
```

**Track data lineage for a specific Iceberg table:**
```sql
SELECT 
    source_system,
    source_table,
    COUNT(*) as ingestion_count,
    SUM(rows_processed) as total_rows_ingested,
    MIN(start_time) as first_ingestion,
    MAX(start_time) as last_ingestion
FROM etladmin.job_run_logs
WHERE iceberg_table = 'integration.customers'
GROUP BY source_system, source_table;
```

## Use Cases

### 1. **Data Lineage Tracking**

Track where each row in your data lake came from:

```sql
-- Find all data from Oracle HR schema
SELECT * FROM integration.customers
WHERE _source_system = 'oracle' 
  AND _source_table LIKE 'HR.%';

-- Find data from multiple MySQL tables
SELECT 
    _source_table,
    COUNT(*) as row_count
FROM integration.orders
WHERE _source_system = 'mysql'
GROUP BY _source_table;
```

### 2. **Multi-Source Data Integration**

Combine data from multiple sources in one table:

```sql
-- Unified customer view from Oracle and MySQL
SELECT 
    customer_id,
    name,
    email,
    _source_system as origin_db,
    _source_table as origin_table,
    _cdc_extracted_at as last_updated
FROM integration.customers
WHERE _source_system IN ('oracle', 'mysql')
ORDER BY _cdc_extracted_at DESC;
```

### 3. **Data Freshness Monitoring**

Monitor how fresh your data is:

```sql
-- Check data freshness by source
SELECT 
    _source_system,
    _source_table,
    MAX(_cdc_extracted_at) as last_extraction,
    CURRENT_TIMESTAMP() as now,
    TIMESTAMPDIFF(HOUR, MAX(_cdc_extracted_at), CURRENT_TIMESTAMP()) as hours_since_last_update
FROM integration.customers
GROUP BY _source_system, _source_table;
```

### 4. **Audit & Compliance**

Prove data origin for compliance:

```sql
-- Audit trail: Show where sensitive data came from
SELECT 
    customer_id,
    email,
    _source_system,
    _source_table,
    _cdc_extracted_at,
    _cdc_checkpoint_scn
FROM integration.customers
WHERE email = 'sensitive@example.com';
```

### 5. **Troubleshooting**

Identify problematic source tables:

```sql
-- Find source tables with frequent failures
SELECT 
    source_system,
    source_table,
    COUNT(*) as failure_count,
    MAX(start_time) as last_failure,
    MAX(error_message) as last_error
FROM etladmin.job_run_logs
WHERE status = 'FAILED'
  AND start_time > CURRENT_TIMESTAMP() - INTERVAL 7 DAYS
GROUP BY source_system, source_table
ORDER BY failure_count DESC;
```

## Implementation Details

### Automatic Metadata Addition

Metadata is automatically added by the utility functions:

**Oracle (`utils/oracle.py`):**
```python
df = spark.read.format("jdbc").options(**options).load()
return df.withColumn("_cdc_checkpoint_scn", col(SCN_COL).cast(LongType())) \
         .withColumn("_cdc_extracted_at", current_timestamp()) \
         .withColumn("_source_system", lit("oracle")) \
         .withColumn("_source_table", lit(oracle_table))
```

**MySQL (`utils/mysql.py`):**
```python
df = spark.read.format("jdbc").options(**options).load()
return df.withColumn("_cdc_checkpoint_id", col("_cdc_checkpoint_id").cast(LongType())) \
         .withColumn("_cdc_extracted_at", current_timestamp()) \
         .withColumn("_source_system", lit("mysql")) \
         .withColumn("_source_table", lit(mysql_table))
```

**MS SQL (`utils/mssql.py`):**
```python
df = spark.read.format("jdbc").options(**options).load()
return df.withColumn("_cdc_checkpoint_id", col("_cdc_checkpoint_id").cast(LongType())) \
         .withColumn("_cdc_extracted_at", current_timestamp()) \
         .withColumn("_source_system", lit("mssql")) \
         .withColumn("_source_table", lit(mssql_table))
```

### Job Logging Enhancement

All ingestion scripts now pass `source_system` parameter:

```python
insert_job_log(
    spark,
    source_system="oracle",  # or "mysql", "mssql"
    source_table=args.oracle_table,
    iceberg_table=args.iceberg_table,
    status="SUCCESS",
    rows_processed=row_count,
    max_scn=max_scn,
    start_time=job_start,
    end_time=datetime.utcnow(),
)
```

## Benefits

### ✅ **Data Governance**
- Clear data lineage for compliance
- Audit trail for sensitive data
- Source attribution for all rows

### ✅ **Operational Visibility**
- Track ingestion performance by source
- Identify problematic source tables
- Monitor data freshness

### ✅ **Multi-Source Support**
- Combine data from Oracle, MySQL, MS SQL
- Distinguish between sources in unified tables
- Support for heterogeneous data lakes

### ✅ **Troubleshooting**
- Quickly identify source of data quality issues
- Track which source table caused failures
- Debug CDC issues with checkpoint values

### ✅ **Analytics**
- Analyze ingestion patterns
- Compare source system performance
- Track data growth by source

## Migration Notes

### For Existing Tables

If you have existing Iceberg tables without metadata columns, they will be automatically added on the next ingestion:

1. **Schema Evolution**: Iceberg supports schema evolution
2. **Null Values**: Existing rows will have NULL for new metadata columns
3. **New Data**: All new ingestions will include metadata

### Query Compatibility

Existing queries will continue to work:
- Metadata columns are prefixed with `_` (convention for system columns)
- SELECT * queries will include new columns
- Explicit column lists are unaffected

## Related Files

- `spark_code/utils/checkpoint.py` - Updated job logging schema
- `spark_code/utils/oracle.py` - Oracle metadata addition
- `spark_code/utils/mysql.py` - MySQL metadata addition
- `spark_code/utils/mssql.py` - MS SQL metadata addition
- `spark_code/oracle_to_iceberg.py` - Updated to pass source_system
- `spark_code/mysql_to_iceberg.py` - Updated to pass source_system
- `spark_code/mssql_to_iceberg.py` - Updated to pass source_system

## Compliance

This implementation follows project standards:

- ✅ **[SD] Strategic Documentation** - Comprehensive lineage tracking
- ✅ **[CA] Clean Architecture** - Metadata added at utility level
- ✅ **[ISA] Industry Standards** - Follows data governance best practices
- ✅ **[RP] Readability Priority** - Clear column naming with `_` prefix
