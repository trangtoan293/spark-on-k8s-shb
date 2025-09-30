# MySQL to Iceberg Setup Guide

## Overview

This guide explains how to set up MySQL CDC (Change Data Capture) to Iceberg using the new centralized configuration system.

## Architecture

```
MySQL Database
    ↓ (JDBC with ID-based CDC)
Spark Application (mysql_to_iceberg.py)
    ↓ (MERGE operation)
Iceberg Table (S3/MinIO)
    ↓ (Checkpoint tracking)
Control Tables (etladmin.cdc_checkpoint, etladmin.job_run_logs)
```

## Environment Variables

### Required MySQL Variables

```bash
# MySQL Connection
export MYSQL_HOST="mysql.example.com"
export MYSQL_PORT="3306"                    # Optional, default: 3306
export MYSQL_DATABASE="production"
export MYSQL_USERNAME="etl_user"
export MYSQL_PASSWORD="secure_password"
```

### Required Control Variables

```bash
# Control Tables (shared with Oracle)
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

### Optional Logging Variables

```bash
# Logging Configuration
export LOG_LEVEL="INFO"                     # Options: DEBUG|INFO|WARN|ERROR
export LOG_FORMAT="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
```

## Usage

### Basic Usage (ID-based CDC)

```bash
python spark_code/mysql_to_iceberg.py \
  --mysql-table customers \
  --iceberg-table integration.customers \
  --primary-key id \
  --id-column id
```

### Advanced Usage

```bash
# With custom ID column
python spark_code/mysql_to_iceberg.py \
  --mysql-table orders \
  --iceberg-table integration.orders \
  --primary-key order_id \
  --id-column order_id

# With composite primary key
python spark_code/mysql_to_iceberg.py \
  --mysql-table order_items \
  --iceberg-table integration.order_items \
  --primary-key "order_id,item_id" \
  --id-column item_id

# With JSON checkpoint backend
python spark_code/mysql_to_iceberg.py \
  --mysql-table products \
  --iceberg-table integration.products \
  --primary-key product_id \
  --id-column product_id \
  --checkpoint-backend json \
  --checkpoint-location s3a://data/checkpoints/mysql
```

## CDC Strategies

### 1. ID-based CDC (Recommended)

Best for tables with auto-increment primary keys.

**Requirements:**
- Table has an auto-increment ID column
- ID values are monotonically increasing
- No ID reuse after deletion

**Example:**
```sql
CREATE TABLE customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Usage:**
```bash
python mysql_to_iceberg.py \
  --mysql-table customers \
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
    name VARCHAR(100),
    price DECIMAL(10,2),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

**Note:** For timestamp-based CDC, use `read_mysql_with_timestamp_cdc()` function directly or extend the script.

## Performance Optimizations

The MySQL loader includes several optimizations:

### 1. Fast Pre-check
```python
# Only queries MAX(id) and COUNT(*) - very fast!
has_new_data, max_id = check_new_data_exists_mysql(spark, table, last_id)
```

**Benefit:** Avoids reading full table when no new data exists.

### 2. Increased Fetchsize
```python
options = {
    "fetchsize": "10000"  # Up from 5000 default
}
```

**Benefit:** Fewer round trips to MySQL, better throughput.

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
    last_scn BIGINT,              -- Stores last ID for MySQL
    updated_at TIMESTAMP
) USING iceberg;

ALTER TABLE etladmin.cdc_checkpoint 
SET IDENTIFIER FIELDS source_table;
```

### JSON Backend

Checkpoints stored in S3/MinIO as JSON files.

**Advantages:**
- ✅ Simple file-based storage
- ✅ Easy to inspect manually
- ✅ No database dependencies

**Location:**
```
s3a://data/checkpoints/mysql/scn_checkpoint/{table_name}.json
```

## Job Logging

All job runs are logged to: `etladmin.job_run_logs`

**Schema:**
```sql
CREATE TABLE etladmin.job_run_logs (
    job_id STRING NOT NULL,
    source_table STRING,
    iceberg_table STRING,
    status STRING,              -- SUCCESS|FAILED|NOOP
    rows_processed BIGINT,
    max_scn BIGINT,             -- Last ID processed
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    error_message STRING
) USING iceberg;
```

**Query job history:**
```sql
SELECT * FROM etladmin.job_run_logs 
WHERE source_table = 'customers' 
ORDER BY start_time DESC 
LIMIT 10;
```

## Comparison: MySQL vs Oracle

| Feature | MySQL | Oracle |
|---------|-------|--------|
| **CDC Method** | ID-based or Timestamp | ORA_ROWSCN (SCN-based) |
| **ID Column** | Auto-increment INT | ORA_ROWSCN (system column) |
| **JDBC Driver** | `com.mysql.cj.jdbc.Driver` | `oracle.jdbc.driver.OracleDriver` |
| **Default Port** | 3306 | 1521 |
| **Connection String** | `jdbc:mysql://host:port/db` | `jdbc:oracle:thin:@//host:port/service` |
| **Checkpoint Table** | Shared `etladmin.cdc_checkpoint` | Shared `etladmin.cdc_checkpoint` |
| **Performance** | Similar (10000 fetchsize) | Similar (10000 fetchsize) |

## Centralized Configuration

All configurations are now centralized in `utils/configs.py`:

```python
from utils.configs import (
    mysql_config,      # MySQL connection config
    oracle_config,     # Oracle connection config
    control_config,    # Control tables config
    checkpoint_config, # Checkpoint backend config
)

# Get MySQL config
cfg = mysql_config()
print(cfg.jdbc_url)    # Full JDBC URL
print(cfg.safe_url)    # Masked credentials

# Get control config
ctrl = control_config()
print(ctrl.full_checkpoint_table)  # etladmin.cdc_checkpoint
print(ctrl.full_job_log_table)     # etladmin.job_run_logs
```

## Troubleshooting

### Issue: MySQL JDBC Driver Not Found

**Error:**
```
java.lang.ClassNotFoundException: com.mysql.cj.jdbc.Driver
```

**Solution:**
Add MySQL JDBC driver to Spark:
```bash
spark-submit \
  --jars /path/to/mysql-connector-java-8.0.33.jar \
  mysql_to_iceberg.py ...
```

Or in SparkApplication YAML:
```yaml
spec:
  deps:
    jars:
      - s3a://jars/mysql-connector-java-8.0.33.jar
```

### Issue: Connection Timeout

**Error:**
```
Communications link failure
```

**Solution:**
1. Check MySQL host/port are correct
2. Verify network connectivity
3. Check firewall rules
4. Increase `queryTimeout` in code

### Issue: Checkpoint Not Updating

**Symptoms:**
- Job runs successfully but reads same data again
- Checkpoint table shows old values

**Solution:**
1. Check MERGE operation completed successfully
2. Verify `max_id` is being captured correctly
3. Check control table permissions
4. Review job logs for errors

## Scheduling

### Kubernetes CronJob

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: mysql-customers-to-iceberg
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
            - name: MYSQL_HOST
              value: "mysql.prod.svc.cluster.local"
            - name: MYSQL_DATABASE
              value: "production"
            - name: MYSQL_USERNAME
              valueFrom:
                secretKeyRef:
                  name: mysql-credentials
                  key: username
            - name: MYSQL_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: mysql-credentials
                  key: password
            command:
            - python
            - /app/mysql_to_iceberg.py
            - --mysql-table=customers
            - --iceberg-table=integration.customers
            - --primary-key=id
```

## Related Files

- `spark_code/mysql_to_iceberg.py` - Main MySQL loader script
- `spark_code/utils/mysql.py` - MySQL utility functions
- `spark_code/utils/configs.py` - Centralized configuration
- `spark_code/utils/checkpoint.py` - Checkpoint management
- `spark_code/utils/merge.py` - MERGE operation utilities
