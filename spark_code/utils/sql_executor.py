"""SQL Executor Utility - Executes SQL statements and tracks results"""
from typing import Dict, Any, List
from datetime import datetime
from pyspark.sql import SparkSession
from .logging import get_logger

log = get_logger(__name__)


def execute_single_statement(spark: SparkSession, sql: str, statement_id: int) -> Dict[str, Any]:
    """
    Execute a single SQL statement and return result metadata.
    
    Args:
        spark: Active Spark session
        sql: SQL statement to execute
        statement_id: Sequential ID for tracking
        
    Returns:
        Dictionary with execution metadata (status, duration, etc.)
    """
    start_time = datetime.now()
    result = {
        "statement_id": statement_id,
        "sql": sql[:100] + "..." if len(sql) > 100 else sql,
        "start_time": start_time.isoformat(),
        "status": "running"
    }
    
    try:
        log.info(f"Executing SQL statement {statement_id}: {sql[:100]}...")
        df = spark.sql(sql)
        
        # Handle different SQL types
        sql_upper = sql.strip().upper()
        if sql_upper.startswith(('SELECT', 'SHOW', 'DESCRIBE', 'EXPLAIN')):
            # Query: show results
            df.show(10)
            rows = df.collect()
            log.info(f"Query completed: {len(rows)} rows returned")
        elif sql_upper.startswith(('CREATE', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'ALTER')):
            # DDL/DML: just execute
            df.collect()
            result["message"] = "Statement executed successfully"
            log.info("DDL/DML statement completed")
        else:
            # Other statements
            df.collect()
            result["message"] = "Statement executed"
            log.info("Statement executed")
        
        # Record success
        end_time = datetime.now()
        result["end_time"] = end_time.isoformat()
        result["duration_seconds"] = (end_time - start_time).total_seconds()
        result["status"] = "success"
        log.info(f"✓ Statement {statement_id} completed in {result['duration_seconds']:.2f}s")
        
    except Exception as e:
        # Record failure
        end_time = datetime.now()
        result["end_time"] = end_time.isoformat()
        result["duration_seconds"] = (end_time - start_time).total_seconds()
        result["status"] = "error"
        result["error"] = str(e)
        log.error(f"✗ Statement {statement_id} failed: {e}")
    
    return result


def execute_statements(
    spark: SparkSession,
    statements: List[str],
    continue_on_error: bool = True,
    default_database: str = None
) -> List[Dict[str, Any]]:
    """
    Execute multiple SQL statements sequentially.
    
    Args:
        spark: Active Spark session
        statements: List of SQL statements
        continue_on_error: Whether to continue if a statement fails
        default_database: Optional database to use before execution
        
    Returns:
        List of result dictionaries for each statement
    """
    # Set default database if specified
    if default_database:
        log.info(f"Setting default database: {default_database}")
        spark.sql(f"USE {default_database}")
    
    results = []
    success_count = 0
    error_count = 0
    
    for i, sql in enumerate(statements, 1):
        result = execute_single_statement(spark, sql, i)
        results.append(result)
        
        if result["status"] == "success":
            success_count += 1
        else:
            error_count += 1
            if not continue_on_error:
                log.error(f"Stopping execution due to error in statement {i}")
                break
    
    # Log summary
    log.info("=== Execution Summary ===")
    log.info(f"Total statements: {len(statements)}")
    log.info(f"Successful: {success_count}")
    log.info(f"Failed: {error_count}")
    
    return results


def save_results(spark: SparkSession, results: List[Dict[str, Any]], output_path: str = None):
    """
    Save execution results to JSON file.
    
    Args:
        spark: Active Spark session
        results: List of execution results
        output_path: Optional output path (defaults to S3 with timestamp)
    """
    if not results:
        log.info("No results to save")
        return
    
    if not output_path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"s3a://data/sql-execution-results/results_{timestamp}.json"
    
    try:
        log.info(f"Saving execution results to: {output_path}")
        results_df = spark.createDataFrame([results])
        results_df.coalesce(1).write \
            .mode("overwrite") \
            .option("multiline", "true") \
            .json(output_path)
        log.info(f"✓ Results saved to: {output_path}")
    except Exception as e:
        log.warning(f"Failed to save results: {e}")
