# MS SQL JDBC Driver Configuration Fix

## Problem

Error when running `mssql_to_iceberg.py`:
```
java.lang.ClassNotFoundException: com.microsoft.sqlserver.jdbc.SQLServerDriver
```

**Root Cause:**
1. MS SQL JDBC driver not included in Spark classpath
2. Version `12.10.1` does not exist (typo)

## Solution

### Step 1: Use Correct Driver Version

For **Spark 3.5.1 with Java 11**, use:

```bash
MSSQL_JDBC_VERSION=12.8.1.jre11
```

**Available Versions:**
- Latest Stable: `12.8.1.jre11` (Recommended)
- Previous: `12.6.4.jre11`, `12.4.2.jre11`, `12.2.0.jre11`

**Version Format:**
- `.jre11` - For Java 11 (Spark 3.x default)
- `.jre8` - For Java 8 (legacy)

### Step 2: Download JDBC Driver

**Option A: Direct Download**
```bash
# Download from Microsoft
wget https://go.microsoft.com/fwlink/?linkid=2265122 -O mssql-jdbc-12.8.1.jre11.jar

# Or use Maven Central
wget https://repo1.maven.org/maven2/com/microsoft/sqlserver/mssql-jdbc/12.8.1.jre11/mssql-jdbc-12.8.1.jre11.jar
```

**Option B: Maven Coordinates**
```xml
<dependency>
    <groupId>com.microsoft.sqlserver</groupId>
    <artifactId>mssql-jdbc</artifactId>
    <version>12.8.1.jre11</version>
</dependency>
```

### Step 3: Add Driver to Spark

**Method 1: SparkApplication YAML (Kubernetes)**

```yaml
apiVersion: sparkoperator.k8s.io/v1beta2
kind: SparkApplication
metadata:
  name: mssql-to-iceberg
spec:
  deps:
    jars:
      - s3a://jars/mssql-jdbc-12.8.1.jre11.jar  # ✅ Add this
      # Or from Maven
      - "https://repo1.maven.org/maven2/com/microsoft/sqlserver/mssql-jdbc/12.8.1.jre11/mssql-jdbc-12.8.1.jre11.jar"
  mainApplicationFile: local:///app/mssql_to_iceberg.py
  sparkConf:
    spark.jars.packages: "org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.4.2"
```

**Method 2: spark-submit**

```bash
spark-submit \
  --jars /path/to/mssql-jdbc-12.8.1.jre11.jar \
  --packages org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.4.2 \
  mssql_to_iceberg.py \
  --mssql-table dbo.customers \
  --iceberg-table integration.customers \
  --primary-key id
```

**Method 3: PySpark Code (Not Recommended)**

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("mssql-to-iceberg") \
    .config("spark.jars", "/path/to/mssql-jdbc-12.8.1.jre11.jar") \
    .getOrCreate()
```

**Method 4: Docker Image (Recommended for Production)**

```dockerfile
FROM bitnami/spark:3.5.1

# Download MS SQL JDBC driver
USER root
RUN wget https://repo1.maven.org/maven2/com/microsoft/sqlserver/mssql-jdbc/12.8.1.jre11/mssql-jdbc-12.8.1.jre11.jar \
    -O /opt/bitnami/spark/jars/mssql-jdbc-12.8.1.jre11.jar

USER 1001
```

## Verification

### Test JDBC Driver Loading

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("test-mssql-driver") \
    .getOrCreate()

# Test driver class loading
try:
    spark._jvm.Class.forName("com.microsoft.sqlserver.jdbc.SQLServerDriver")
    print("✅ MS SQL JDBC driver loaded successfully!")
except Exception as e:
    print(f"❌ Driver not found: {e}")
```

### Test Connection

```python
from utils.configs import mssql_config

cfg = mssql_config()
jdbc_url = cfg.jdbc_url

# Test connection
df = spark.read \
    .format("jdbc") \
    .option("url", jdbc_url) \
    .option("dbtable", "(SELECT 1 AS test) t") \
    .option("user", cfg.username) \
    .option("password", cfg.password) \
    .option("driver", "com.microsoft.sqlserver.jdbc.SQLServerDriver") \
    .load()

df.show()
# Should display: +----+
#                 |test|
#                 +----+
#                 |   1|
#                 +----+
```

## Version Compatibility Matrix

| Spark Version | Java Version | MS SQL JDBC Driver | Status |
|---------------|--------------|-------------------|--------|
| 3.5.x | Java 11 | `12.8.1.jre11` | ✅ Recommended |
| 3.5.x | Java 11 | `12.6.4.jre11` | ✅ Stable |
| 3.5.x | Java 11 | `12.4.2.jre11` | ✅ Stable |
| 3.5.x | Java 11 | `12.10.1.jre11` | ❌ Does not exist |
| 3.4.x | Java 11 | `12.2.0.jre11` | ✅ Stable |
| 3.3.x | Java 11 | `11.2.3.jre11` | ✅ Stable |
| 3.x | Java 8 | `12.8.1.jre8` | ✅ Legacy |

## Common Issues

### Issue 1: Wrong Java Version

**Error:**
```
UnsupportedClassVersionError: com/microsoft/sqlserver/jdbc/SQLServerDriver
```

**Solution:**
- Check Java version: `java -version`
- For Java 11: Use `.jre11` driver
- For Java 8: Use `.jre8` driver

### Issue 2: Driver Not in Classpath

**Error:**
```
ClassNotFoundException: com.microsoft.sqlserver.jdbc.SQLServerDriver
```

**Solution:**
- Verify JAR location: `ls -la /opt/bitnami/spark/jars/mssql-jdbc*.jar`
- Check SparkApplication YAML has correct `deps.jars`
- Ensure JAR is accessible (S3/HTTP URL or local path)

### Issue 3: Multiple Driver Versions

**Symptom:**
- Inconsistent behavior
- Version conflicts

**Solution:**
```bash
# Remove old versions
rm /opt/bitnami/spark/jars/mssql-jdbc-*.jar

# Add only one version
wget https://repo1.maven.org/maven2/com/microsoft/sqlserver/mssql-jdbc/12.8.1.jre11/mssql-jdbc-12.8.1.jre11.jar \
    -O /opt/bitnami/spark/jars/mssql-jdbc-12.8.1.jre11.jar
```

## Recommended Setup for Kubernetes

### 1. Upload Driver to S3/MinIO

```bash
# Upload to S3
aws s3 cp mssql-jdbc-12.8.1.jre11.jar s3://spark-jars/mssql-jdbc-12.8.1.jre11.jar

# Or MinIO
mc cp mssql-jdbc-12.8.1.jre11.jar minio/spark-jars/mssql-jdbc-12.8.1.jre11.jar
```

### 2. SparkApplication YAML

```yaml
apiVersion: sparkoperator.k8s.io/v1beta2
kind: SparkApplication
metadata:
  name: mssql-to-iceberg
  namespace: spark-jobs
spec:
  type: Python
  pythonVersion: "3"
  mode: cluster
  image: "bitnami/spark:3.5.1"
  imagePullPolicy: Always
  mainApplicationFile: local:///app/mssql_to_iceberg.py
  
  deps:
    jars:
      - s3a://spark-jars/mssql-jdbc-12.8.1.jre11.jar  # ✅ MS SQL driver
      - s3a://spark-jars/iceberg-spark-runtime-3.5_2.12-1.4.2.jar
  
  sparkConf:
    # S3/MinIO configuration
    spark.hadoop.fs.s3a.endpoint: "http://minio.minio.svc.cluster.local:9000"
    spark.hadoop.fs.s3a.access.key: "${AWS_ACCESS_KEY_ID}"
    spark.hadoop.fs.s3a.secret.key: "${AWS_SECRET_ACCESS_KEY}"
    spark.hadoop.fs.s3a.path.style.access: "true"
    spark.hadoop.fs.s3a.impl: "org.apache.hadoop.fs.s3a.S3AFileSystem"
    
    # Iceberg configuration
    spark.sql.catalog.spark_catalog: "org.apache.iceberg.spark.SparkSessionCatalog"
    spark.sql.catalog.spark_catalog.type: "hive"
    spark.sql.extensions: "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions"
  
  driver:
    cores: 1
    memory: "2g"
    serviceAccount: spark
    env:
      - name: MSSQL_HOST
        value: "mssql.database.svc.cluster.local"
      - name: MSSQL_PORT
        value: "1433"
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
  
  executor:
    cores: 2
    instances: 2
    memory: "4g"
```

### 3. Create Secret

```bash
kubectl create secret generic mssql-credentials \
  --from-literal=username=etl_user \
  --from-literal=password=your_password \
  -n spark-jobs
```

## Download Links

### Official Microsoft Downloads

- **Latest (12.8.1):** https://go.microsoft.com/fwlink/?linkid=2265122
- **Previous (12.6.4):** https://go.microsoft.com/fwlink/?linkid=2259539
- **Previous (12.4.2):** https://go.microsoft.com/fwlink/?linkid=2223050

### Maven Central

```
https://repo1.maven.org/maven2/com/microsoft/sqlserver/mssql-jdbc/{VERSION}/mssql-jdbc-{VERSION}.jar
```

Replace `{VERSION}` with:
- `12.8.1.jre11`
- `12.6.4.jre11`
- `12.4.2.jre11`

## References

- [MS SQL JDBC Driver Documentation](https://learn.microsoft.com/en-us/sql/connect/jdbc/)
- [Driver Download Page](https://learn.microsoft.com/en-us/sql/connect/jdbc/download-microsoft-jdbc-driver-for-sql-server)
- [Support Matrix](https://learn.microsoft.com/en-us/sql/connect/jdbc/microsoft-jdbc-driver-for-sql-server-support-matrix)
- [Spark JDBC Documentation](https://spark.apache.org/docs/3.5.1/sql-data-sources-jdbc.html)
- [GitHub Repository](https://github.com/microsoft/mssql-jdbc)

## Quick Fix Summary

```bash
# 1. Download correct version
wget https://repo1.maven.org/maven2/com/microsoft/sqlserver/mssql-jdbc/12.8.1.jre11/mssql-jdbc-12.8.1.jre11.jar

# 2. Upload to S3/MinIO
aws s3 cp mssql-jdbc-12.8.1.jre11.jar s3://spark-jars/

# 3. Update SparkApplication YAML
# Add to spec.deps.jars:
#   - s3a://spark-jars/mssql-jdbc-12.8.1.jre11.jar

# 4. Apply and run
kubectl apply -f spark-application.yaml
```
