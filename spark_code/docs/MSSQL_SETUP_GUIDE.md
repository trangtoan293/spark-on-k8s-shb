## MS SQL Server to Iceberg Setup Guide

## Overview

This guide explains how to set up MS SQL Server CDC (Change Data Capture) to Iceberg using the centralized configuration system.

## Architecture

```
MS SQL Server Database
    ↓ (JDBC with ID-based or Change Tracking CDC)
Spark Application (mssql_to_iceberg.py)
    ↓ (MERGE operation)
Iceberg Table (S3/MinIO)
    ↓ (Checkpoint tracking)
Control Tables (etladmin.cdc_checkpoint, etladmin.job_run_logs)
```

## Environment Variables

### Required MS SQL Server Variables

```bash
# MS SQL Server Connection
export MSSQL_HOST="mssql.example.com"
export MSSQL_PORT="1433"                    # Optional, default: 1433
export MSSQL_DATABASE="production"
export MSSQL_USERNAME="etl_user"
export MSSQL_PASSWORD="secure_password"
```

### Required Control Variables

```bash
# Control Tables (shared with Oracle/MySQL)
export CONTROL_DB="etladmin"                # Optional, default: etladmin
export CHECKPOINT_TABLE="cdc_checkpoint"    # Optional, default: cdc_checkpoint
export JOB_LOG_TABLE="job_run_logs"         # Optional, default: job_run_logs
```

### Optional Checkpoint Variables

```bash
# Checkpoint Backend
export CHECKPOINT_BACKEND="table"           # Options: table|json, default: table
export CHECKPOINT_LOCATION="s3a://data/checkpoints"  # For JSON backend
```

## Usage

### Basic Usage (ID-based CDC)

```bash
python spark_code/mssql_to_iceberg.py \
  --mssql-table dbo.customers \
  --iceberg-table integration.customers \
  --primary-key id \
  --id-column id
```

### Advanced Usage

```bash
# With schema prefix
python spark_code/mssql_to_iceberg.py \
  --mssql-table sales.orders \
  --iceberg-table integration.orders \
  --primary-key order_id \
  --id-column order_id

# With composite primary key
python spark_code/mssql_to_iceberg.py \
  --mssql-table dbo.order_items \
  --iceberg-table integration.order_items \
  --primary-key "order_id,item_id" \
  --id-column item_id

# With JSON checkpoint backend
python spark_code/mssql_to_iceberg.py \
  --mssql-table dbo.products \
  --iceberg-table integration.products \
  --primary-key product_id \
  --id-column product_id \
  --checkpoint-backend json \
  --checkpoint-location s3a://data/checkpoints/mssql
```

## CDC Strategies

### 1. ID-based CDC (Recommended for Simple Cases)

Best for tables with IDENTITY primary keys.

**Requirements:**
- Table has an IDENTITY column
- ID values are monotonically increasing
- No ID reuse after deletion

**Example:**
```sql
CREATE TABLE customers (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(100),
    email NVARCHAR(100),
    created_at DATETIME2 DEFAULT GETDATE()
);
```

**Usage:**
```bash
python mssql_to_iceberg.py \
  --mssql-table dbo.customers \
  --iceberg-table integration.customers \
  --primary-key id \
  --id-column id
```

### 2. Timestamp-based CDC

Best for tables with `updated_at` timestamp columns.

**Requirements:**
- Table has `updated_at` or similar timestamp column
- Timestamp updated on every row change
- Timezone consistency

**Example:**
```sql
CREATE TABLE products (
    product_id INT PRIMARY KEY,
    name NVARCHAR(100),
    price DECIMAL(10,2),
    updated_at DATETIME2 DEFAULT GETDATE()
);

-- Create trigger to update timestamp
CREATE TRIGGER trg_products_update
ON products
AFTER UPDATE
AS
BEGIN
    UPDATE products
    SET updated_at = GETDATE()
    WHERE product_id IN (SELECT product_id FROM inserted);
END;
```

**Note:** For timestamp-based CDC, use `read_mssql_with_timestamp_cdc()` function directly or extend the script.

### 3. Change Tracking (Recommended for Production)

MS SQL Server's built-in Change Tracking feature - most efficient for CDC.

**Requirements:**
- SQL Server 2008 or later
- Change Tracking enabled on database and table
- Tracks INSERT, UPDATE, DELETE operations

**Setup:**
```sql
-- Enable Change Tracking on database
ALTER DATABASE [YourDatabase] 
SET CHANGE_TRACKING = ON  
(CHANGE_RETENTION = 2 DAYS, AUTO_CLEANUP = ON);

-- Enable Change Tracking on table
ALTER TABLE [dbo].[customers] 
ENABLE CHANGE_TRACKING  
WITH (TRACK_COLUMNS_UPDATED = ON);

-- Check Change Tracking status
SELECT 
    t.name AS table_name,
    ct.is_track_columns_updated_on,
    DB_NAME() AS database_name
FROM sys.change_tracking_tables ct
INNER JOIN sys.tables t ON t.object_id = ct.object_id;
```

**Usage:**
```python
# Use read_mssql_with_change_tracking() function
from utils.mssql import read_mssql_with_change_tracking

df = read_mssql_with_change_tracking(
    spark, 
    "dbo.customers", 
    last_version=12345
)
```

**Benefits:**
- ✅ Minimal overhead (< 5% performance impact)
- ✅ Tracks all changes (INSERT/UPDATE/DELETE)
- ✅ No triggers needed
- ✅ Built-in cleanup mechanism
- ✅ Version-based tracking (more reliable than timestamps)

## Performance Optimizations

The MS SQL Server loader includes several optimizations:

### 1. Fast Pre-check
```python
# Only queries MAX(id) and COUNT(*) - very fast!
has_new_data, max_id = check_new_data_exists_mssql(spark, table, last_id)
```

**Benefit:** Avoids reading full table when no new data exists.

### 2. Increased Fetchsize
```python
options = {
    "fetchsize": "10000"  # Up from default
}
```

**Benefit:** Fewer round trips to MS SQL Server, better throughput.

### 3. DataFrame Caching
```python
df.cache()
row_count = df.count()
# Reuse cached data for subsequent operations
```

**Benefit:** Avoid re-reading data multiple times.

### 4. Reuse Max ID
```python
max_id = max_id_in_source  # Already have it from pre-check!
```

**Benefit:** No need to scan DataFrame again.

## Checkpoint Management

### Table Backend (Default)

Checkpoints stored in Iceberg table: `etladmin.cdc_checkpoint`

**Advantages:**
- ✅ ACID transactions
- ✅ No external dependencies
- ✅ Automatic schema evolution
- ✅ Query checkpoint history with SQL

**Schema:**
```sql
CREATE TABLE etladmin.cdc_checkpoint (
    source_table STRING NOT NULL,
    last_scn BIGINT,              -- Stores last ID for MS SQL
    updated_at TIMESTAMP
) USING iceberg;

ALTER TABLE etladmin.cdc_checkpoint 
SET IDENTIFIER FIELDS source_table;
```

### JSON Backend

Checkpoints stored in S3/MinIO as JSON files.

**Location:**
```
s3a://data/checkpoints/mssql/scn_checkpoint/{table_name}.json
```

## Job Logging

All job runs are logged to: `etladmin.job_run_logs`

**Query job history:**
```sql
SELECT * FROM etladmin.job_run_logs 
WHERE source_table = 'dbo.customers' 
ORDER BY start_time DESC 
LIMIT 10;
```

## Comparison: MS SQL vs Oracle vs MySQL

| Feature | MS SQL Server | Oracle | MySQL |
|---------|---------------|--------|-------|
| **CDC Method** | ID/Timestamp/Change Tracking | ORA_ROWSCN (SCN) | ID/Timestamp |
| **ID Column** | IDENTITY INT | ORA_ROWSCN | AUTO_INCREMENT INT |
| **JDBC Driver** | `com.microsoft.sqlserver.jdbc.SQLServerDriver` | `oracle.jdbc.driver.OracleDriver` | `com.mysql.cj.jdbc.Driver` |
| **Default Port** | 1433 | 1521 | 3306 |
| **Connection String** | `jdbc:sqlserver://host:port;databaseName=db` | `jdbc:oracle:thin:@//host:port/service` | `jdbc:mysql://host:port/db` |
| **Built-in CDC** | ✅ Change Tracking | ✅ ORA_ROWSCN | ❌ No |
| **Schema Support** | ✅ dbo.table | ✅ SCHEMA.TABLE | ❌ Database only |
| **Checkpoint Table** | Shared `etladmin.cdc_checkpoint` | Shared | Shared |

## Centralized Configuration

All configurations are now centralized in `utils/configs.py`:

```python
from utils.configs import (
    mssql_config,      # MS SQL Server connection config
    oracle_config,     # Oracle connection config
    mysql_config,      # MySQL connection config
    control_config,    # Control tables config
    checkpoint_config, # Checkpoint backend config
)

# Get MS SQL Server config
cfg = mssql_config()
print(cfg.jdbc_url)    # Full JDBC URL
print(cfg.safe_url)    # Masked credentials

# Get control config
ctrl = control_config()
print(ctrl.full_checkpoint_table)  # etladmin.cdc_checkpoint
print(ctrl.full_job_log_table)     # etladmin.job_run_logs
```

## Troubleshooting

### Issue: MS SQL Server JDBC Driver Not Found

**Error:**
```
java.lang.ClassNotFoundException: com.microsoft.sqlserver.jdbc.SQLServerDriver
```

**Solution:**
Add MS SQL Server JDBC driver to Spark:
```bash
spark-submit \
  --jars /path/to/mssql-jdbc-12.4.2.jre11.jar \
  mssql_to_iceberg.py ...
```

Or in SparkApplication YAML:
```yaml
spec:
  deps:
    jars:
      - s3a://jars/mssql-jdbc-12.4.2.jre11.jar
```

**Download:**
https://learn.microsoft.com/en-us/sql/connect/jdbc/download-microsoft-jdbc-driver-for-sql-server

### Issue: SSL/TLS Connection Error

**Error:**
```
The driver could not establish a secure connection to SQL Server
```

**Solution:**
The JDBC URL includes `encrypt=true;trustServerCertificate=true` by default.

For production, use proper SSL certificates:
```python
# In configs.py, modify jdbc_url property:
return f"jdbc:sqlserver://{self.host}:{self.port};databaseName={self.database};encrypt=true;trustServerCertificate=false;hostNameInCertificate=*.database.windows.net"
```

### Issue: Connection Timeout

**Error:**
```
The TCP/IP connection to the host has failed
```

**Solution:**
1. Check MS SQL Server host/port are correct
2. Verify network connectivity
3. Check firewall rules (port 1433)
4. Verify SQL Server is configured for TCP/IP connections:
   ```sql
   -- Check SQL Server configuration
   EXEC sp_configure 'remote access';
   ```

### Issue: Authentication Failed

**Error:**
```
Login failed for user 'etl_user'
```

**Solution:**
1. Verify credentials are correct
2. Check SQL Server authentication mode (Windows vs SQL Server)
3. Ensure user has proper permissions:
   ```sql
   -- Grant permissions
   USE [YourDatabase];
   GRANT SELECT ON SCHEMA::dbo TO etl_user;
   GRANT SELECT ON SCHEMA::sales TO etl_user;
   ```

### Issue: Change Tracking Not Working

**Symptoms:**
- No changes detected
- Version numbers not incrementing

**Solution:**
1. Verify Change Tracking is enabled:
   ```sql
   -- Check database level
   SELECT DB_NAME(), is_change_tracking_on 
   FROM sys.databases 
   WHERE name = 'YourDatabase';
   
   -- Check table level
   SELECT t.name, ct.is_track_columns_updated_on
   FROM sys.change_tracking_tables ct
   INNER JOIN sys.tables t ON t.object_id = ct.object_id;
   ```

2. Check retention period:
   ```sql
   SELECT change_retention_days 
   FROM sys.change_tracking_databases 
   WHERE database_id = DB_ID('YourDatabase');
   ```

## Scheduling

### Kubernetes CronJob

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: mssql-customers-to-iceberg
spec:
  schedule: "0 * * * *"  # Every hour
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: spark-submit
            image: spark:3.5.0
            env:
            - name: MSSQL_HOST
              value: "mssql.prod.svc.cluster.local"
            - name: MSSQL_DATABASE
              value: "production"
            - name: MSSQL_USERNAME
              valueFrom:
                secretKeyRef:
                  name: mssql-credentials
                  key: username
            - name: MSSQL_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: mssql-credentials
                  key: password
            command:
            - python
            - /app/mssql_to_iceberg.py
            - --mssql-table=dbo.customers
            - --iceberg-table=integration.customers
            - --primary-key=id
```

## Best Practices

### 1. Use Change Tracking for Production
- Most efficient CDC method
- Minimal performance impact
- Tracks all operations (INSERT/UPDATE/DELETE)

### 2. Schema Naming
- Always include schema prefix: `dbo.customers`, `sales.orders`
- Avoids ambiguity in multi-schema databases

### 3. Index Optimization
- Create index on CDC column (id, updated_at, etc.)
- Improves incremental query performance

```sql
-- Index on ID column
CREATE INDEX idx_customers_id ON dbo.customers(id);

-- Index on timestamp column
CREATE INDEX idx_products_updated_at ON dbo.products(updated_at);
```

### 4. Monitor Change Tracking Size
```sql
-- Check Change Tracking size
SELECT 
    t.name AS table_name,
    SUM(ps.reserved_page_count) * 8 / 1024.0 AS size_mb
FROM sys.dm_db_partition_stats ps
INNER JOIN sys.internal_tables it ON it.object_id = ps.object_id
INNER JOIN sys.change_tracking_tables ct ON ct.object_id = it.parent_object_id
INNER JOIN sys.tables t ON t.object_id = ct.object_id
GROUP BY t.name;
```

### 5. Retention Period
- Set appropriate retention period for Change Tracking
- Balance between storage and recovery needs
- Typically 2-7 days

```sql
-- Adjust retention period
ALTER DATABASE [YourDatabase] 
SET CHANGE_TRACKING (CHANGE_RETENTION = 7 DAYS);
```

## Related Files

- `spark_code/mssql_to_iceberg.py` - Main MS SQL Server loader script
- `spark_code/utils/mssql.py` - MS SQL Server utility functions
- `spark_code/utils/configs.py` - Centralized configuration
- `spark_code/utils/checkpoint.py` - Checkpoint management
- `spark_code/utils/merge.py` - MERGE operation utilities

## References

- [MS SQL Server JDBC Driver Documentation](https://learn.microsoft.com/en-us/sql/connect/jdbc/)
- [Change Tracking Documentation](https://learn.microsoft.com/en-us/sql/relational-databases/track-changes/about-change-tracking-sql-server)
- [Spark JDBC Data Source](https://spark.apache.org/docs/latest/sql-data-sources-jdbc.html)
