#!/usr/bin/env python3
"""
Spark SQL Executor
==================

Python application for executing SQL statements from files using Spark SQL.
Designed for SparkApplication deployment with support for:
- Reading SQL from text files
- Statement separation by semicolon
- Configurable Spark session with Iceberg and Hive support
- Comprehensive error handling and logging
- Flexible deployment options

Usage:
    python spark_sql_executor.py --sql-file queries.sql
    python spark_sql_executor.py --sql-file queries.sql --database demo
    python spark_sql_executor.py --sql-text "SELECT * FROM demo.customers; SHOW TABLES;"

Environment Variables:
    AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY - S3/MinIO credentials
    AWS_REGION - AWS region (typically "us-east-1")

Version: 1.0.0 - SQL File Executor for SparkApplication
"""

import os
import sys
import argparse
import logging
import re
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SparkSQLExecutor:
    """Spark SQL Executor for running SQL files and statements"""
    
    def __init__(self, default_database: Optional[str] = None):
        self.spark = None
        self.default_database = default_database
        self.execution_results = []
        
    def create_spark_session(self) -> SparkSession:
        """Create Spark session optimized for SQL execution"""
        try:
            spark = SparkSession.getActiveSession()
            if spark is None:
                logger.info("Creating Spark session for SQL execution")
                spark = SparkSession.builder \
                    .appName("spark-sql-executor") \
                    .config("spark.sql.adaptive.enabled", "true") \
                    .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
                    .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
                    .getOrCreate()
                    
                spark.sparkContext.setLogLevel("WARN")
            else:
                logger.info("Reusing existing Spark session")
                
            return spark
        except Exception as e:
            logger.error(f"Failed to create Spark session: {e}")
            raise
    
    def read_sql_file(self, file_path: str) -> str:
        """Read SQL content from file"""
        try:
            logger.info(f"Reading SQL file: {file_path}")
            
            # Check if file exists locally first
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                logger.info(f"✓ Read SQL file locally: {len(content)} characters")
                return content
            
            # Try reading from mounted volume (K8s deployment)
            volume_path = f"/opt/spark/work-dir/{os.path.basename(file_path)}"
            if os.path.exists(volume_path):
                with open(volume_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                logger.info(f"✓ Read SQL file from volume: {len(content)} characters")
                return content
            
            # Try reading from S3/MinIO using Spark
            try:
                sql_df = self.spark.read.text(file_path)
                rows = sql_df.collect()
                content = '\n'.join([row.value for row in rows])
                logger.info(f"✓ Read SQL file from S3: {len(content)} characters")
                return content
            except Exception as s3_error:
                logger.warning(f"Failed to read from S3: {s3_error}")
            
            raise FileNotFoundError(f"SQL file not found: {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to read SQL file '{file_path}': {e}")
            raise
    
    def parse_sql_statements(self, sql_content: str) -> List[str]:
        """Parse SQL content into individual statements"""
        try:
            logger.info("Parsing SQL statements")
            
            # Remove comments and empty lines
            lines = []
            for line in sql_content.split('\n'):
                line = line.strip()
                # Skip empty lines and comments
                if line and not line.startswith('--') and not line.startswith('#'):
                    lines.append(line)
            
            # Join lines and split by semicolon
            combined_sql = ' '.join(lines)
            
            # Split by semicolon but preserve quoted strings
            statements = []
            current_statement = ""
            in_quotes = False
            quote_char = None
            
            i = 0
            while i < len(combined_sql):
                char = combined_sql[i]
                
                # Handle quotes
                if char in ('"', "'") and not in_quotes:
                    in_quotes = True
                    quote_char = char
                elif char == quote_char and in_quotes:
                    in_quotes = False
                    quote_char = None
                
                # Handle semicolon
                if char == ';' and not in_quotes:
                    if current_statement.strip():
                        statements.append(current_statement.strip())
                    current_statement = ""
                else:
                    current_statement += char
                
                i += 1
            
            # Add final statement if exists
            if current_statement.strip():
                statements.append(current_statement.strip())
            
            # Filter out empty statements
            statements = [stmt for stmt in statements if stmt.strip()]
            
            logger.info(f"✓ Parsed {len(statements)} SQL statements")
            return statements
            
        except Exception as e:
            logger.error(f"Failed to parse SQL statements: {e}")
            raise
    
    def execute_sql_statement(self, sql: str, statement_id: int) -> Dict[str, Any]:
        """Execute single SQL statement"""
        start_time = datetime.now()
        result = {
            "statement_id": statement_id,
            "sql": sql[:100] + "..." if len(sql) > 100 else sql,
            "start_time": start_time.isoformat(),
            "status": "running"
        }
        
        try:
            logger.info(f"Executing SQL statement {statement_id}: {sql[:100]}...")
            
            # Execute SQL
            df = self.spark.sql(sql)
            
            # Handle different SQL types
            if sql.strip().upper().startswith(('SELECT', 'SHOW', 'DESCRIBE', 'EXPLAIN')):
                # For queries, show and collect results
                df.show(10)  # Display results
                rows = df.collect()  # Get actual data
                logger.info(f"Query completed: {len(rows)} rows returned")
                    
            elif sql.strip().upper().startswith(('CREATE', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'ALTER')):
                # For DDL/DML, just execute
                df.collect()  # Trigger execution
                result["message"] = "Statement executed successfully"
                logger.info(f"DDL/DML statement completed successfully")
                
            else:
                # For other statements
                df.collect()  # Trigger execution
                result["message"] = "Statement executed"
                logger.info(f"Statement executed")
            
            end_time = datetime.now()
            result["end_time"] = end_time.isoformat()
            result["duration_seconds"] = (end_time - start_time).total_seconds()
            result["status"] = "success"
            
            logger.info(f"✓ Statement {statement_id} completed in {result['duration_seconds']:.2f}s")
            return result
            
        except Exception as e:
            end_time = datetime.now()
            result["end_time"] = end_time.isoformat()
            result["duration_seconds"] = (end_time - start_time).total_seconds()
            result["status"] = "error"
            result["error"] = str(e)
            
            logger.error(f"✗ Statement {statement_id} failed: {e}")
            return result
    
    def execute_sql_file(self, file_path: str, continue_on_error: bool = True) -> List[Dict[str, Any]]:
        """Execute SQL file with multiple statements"""
        try:
            logger.info(f"=== Executing SQL file: {file_path} ===")
            
            # Set default database if specified
            if self.default_database:
                logger.info(f"Setting default database: {self.default_database}")
                self.spark.sql(f"USE {self.default_database}")
            
            # Read and parse SQL file
            sql_content = self.read_sql_file(file_path)
            statements = self.parse_sql_statements(sql_content)
            
            if not statements:
                logger.warning("No SQL statements found in file")
                return []
            
            # Execute statements
            results = []
            success_count = 0
            error_count = 0
            
            for i, sql in enumerate(statements, 1):
                result = self.execute_sql_statement(sql, i)
                results.append(result)
                
                if result["status"] == "success":
                    success_count += 1
                else:
                    error_count += 1
                    if not continue_on_error:
                        logger.error(f"Stopping execution due to error in statement {i}")
                        break
            
            # Summary
            logger.info(f"=== Execution Summary ===")
            logger.info(f"Total statements: {len(statements)}")
            logger.info(f"Successful: {success_count}")
            logger.info(f"Failed: {error_count}")
            
            self.execution_results = results
            return results
            
        except Exception as e:
            logger.error(f"Failed to execute SQL file: {e}")
            raise
    
    def execute_sql_text(self, sql_text: str, continue_on_error: bool = True) -> List[Dict[str, Any]]:
        """Execute SQL text with multiple statements"""
        try:
            logger.info("=== Executing SQL text ===")
            
            # Set default database if specified
            if self.default_database:
                logger.info(f"Setting default database: {self.default_database}")
                self.spark.sql(f"USE {self.default_database}")
            
            # Parse SQL statements
            statements = self.parse_sql_statements(sql_text)
            
            if not statements:
                logger.warning("No SQL statements found in text")
                return []
            
            # Execute statements
            results = []
            success_count = 0
            error_count = 0
            
            for i, sql in enumerate(statements, 1):
                result = self.execute_sql_statement(sql, i)
                results.append(result)
                
                if result["status"] == "success":
                    success_count += 1
                else:
                    error_count += 1
                    if not continue_on_error:
                        logger.error(f"Stopping execution due to error in statement {i}")
                        break
            
            # Summary
            logger.info(f"=== Execution Summary ===")
            logger.info(f"Total statements: {len(statements)}")
            logger.info(f"Successful: {success_count}")
            logger.info(f"Failed: {error_count}")
            
            self.execution_results = results
            return results
            
        except Exception as e:
            logger.error(f"Failed to execute SQL text: {e}")
            raise
    
    def save_results(self, output_path: Optional[str] = None):
        """Save execution results to file"""
        if not self.execution_results:
            logger.info("No results to save")
            return
        
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"s3a://data/sql-execution-results/results_{timestamp}.json"
        
        try:
            logger.info(f"Saving execution results to: {output_path}")
            
            # Create results DataFrame
            results_df = self.spark.createDataFrame([self.execution_results])
            
            # Save as JSON
            results_df.coalesce(1).write \
                .mode("overwrite") \
                .option("multiline", "true") \
                .json(output_path)
            
            logger.info(f"✓ Results saved to: {output_path}")
            
        except Exception as e:
            logger.warning(f"Failed to save results: {e}")
    
    def close(self):
        """Close Spark session"""
        if self.spark:
            self.spark.stop()
            logger.info("Spark session closed")

def main():
    """Main function with comprehensive argument handling"""
    parser = argparse.ArgumentParser(
        description="Spark SQL Executor - Execute SQL files and statements"
    )
    
    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--sql-file", 
                            help="Path to SQL file (local, S3, or mounted volume)")
    input_group.add_argument("--sql-text", 
                            help="SQL text to execute directly")
    
    # Execution options
    parser.add_argument("--database", 
                       help="Default database to use")
    parser.add_argument("--continue-on-error", action="store_true", default=True,
                       help="Continue execution if a statement fails")
    parser.add_argument("--stop-on-error", action="store_true",
                       help="Stop execution on first error")
    parser.add_argument("--output-path", 
                       help="Path to save execution results (JSON)")
    
    # Debug options
    parser.add_argument("--dry-run", action="store_true",
                       help="Parse SQL but don't execute")
    parser.add_argument("--verbose", action="store_true",
                       help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Determine continue_on_error setting
    continue_on_error = not args.stop_on_error if args.stop_on_error else args.continue_on_error
    
    executor = None
    try:
        # Initialize executor
        executor = SparkSQLExecutor(default_database=args.database)
        
        # Create Spark session
        executor.spark = executor.create_spark_session()
        
        if args.dry_run:
            logger.info("=== DRY RUN MODE ===")
            if args.sql_file:
                content = executor.read_sql_file(args.sql_file)
                statements = executor.parse_sql_statements(content)
                logger.info(f"Parsed {len(statements)} statements:")
                for i, sql in enumerate(statements, 1):
                    logger.info(f"Statement {i}: {sql[:100]}...")
            elif args.sql_text:
                statements = executor.parse_sql_statements(args.sql_text)
                logger.info(f"Parsed {len(statements)} statements:")
                for i, sql in enumerate(statements, 1):
                    logger.info(f"Statement {i}: {sql[:100]}...")
            return
        
        # Execute SQL
        if args.sql_file:
            results = executor.execute_sql_file(args.sql_file, continue_on_error)
        elif args.sql_text:
            results = executor.execute_sql_text(args.sql_text, continue_on_error)
        
        # Save results if requested
        if args.output_path and results:
            executor.save_results(args.output_path)
        
        # Exit with appropriate code
        error_count = sum(1 for r in results if r["status"] == "error")
        if error_count > 0:
            logger.warning(f"Completed with {error_count} errors")
            sys.exit(1)
        else:
            logger.info("All statements executed successfully")
            sys.exit(0)
        
    except KeyboardInterrupt:
        logger.info("SQL execution stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"SQL execution failed: {e}")
        sys.exit(1)
        
    finally:
        if executor:
            executor.close()

if __name__ == "__main__":
    main()