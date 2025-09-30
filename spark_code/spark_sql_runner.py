#!/usr/bin/env python3
"""
Spark SQL Executor - Simplified Version
========================================

Execute SQL statements from files or text using Spark SQL.
Simplified architecture using utility modules for better maintainability.

Usage:
    python spark_sql_runner.py --sql-file queries.sql
    python spark_sql_runner.py --sql-file queries.sql --database demo
    python spark_sql_runner.py --sql-text "SELECT * FROM demo.customers; SHOW TABLES;"

Version: 2.0.0 - Refactored with utility modules
"""

import sys
import argparse
from typing import List, Dict, Any

# Import utilities
from utils.logging import get_logger
from utils.spark import create_spark
from utils.sql_reader import read_sql_file
from utils.sql_parser import parse_sql_statements
from utils.sql_executor import execute_statements, save_results

log = get_logger(__name__)

def execute_sql_file_wrapper(
    spark,
    file_path: str,
    continue_on_error: bool = True,
    default_database: str = None
) -> List[Dict[str, Any]]:
    """Execute SQL file with multiple statements"""
    log.info(f"=== Executing SQL file: {file_path} ===")
    
    # Read and parse SQL file
    sql_content = read_sql_file(spark, file_path)
    statements = parse_sql_statements(sql_content)
    
    if not statements:
        log.warning("No SQL statements found in file")
        return []
    
    # Execute statements
    return execute_statements(spark, statements, continue_on_error, default_database)


def execute_sql_text_wrapper(
    spark,
    sql_text: str,
    continue_on_error: bool = True,
    default_database: str = None
) -> List[Dict[str, Any]]:
    """Execute SQL text with multiple statements"""
    log.info("=== Executing SQL text ===")
    
    # Parse SQL statements
    statements = parse_sql_statements(sql_text)
    
    if not statements:
        log.warning("No SQL statements found in text")
        return []
    
    # Execute statements
    return execute_statements(spark, statements, continue_on_error, default_database)

def main():
    """Main function - simplified argument handling"""
    parser = argparse.ArgumentParser(
        description="Spark SQL Executor - Simplified version using utility modules"
    )
    
    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--sql-file", help="Path to SQL file")
    input_group.add_argument("--sql-text", help="SQL text to execute")
    
    # Execution options
    parser.add_argument("--database", help="Default database")
    parser.add_argument("--stop-on-error", action="store_true", 
                       help="Stop on first error")
    parser.add_argument("--output-path", help="Save results path")
    
    # Debug options
    parser.add_argument("--dry-run", action="store_true", 
                       help="Parse only, don't execute")
    parser.add_argument("--verbose", action="store_true", 
                       help="Verbose logging")
    
    args = parser.parse_args()
    continue_on_error = not args.stop_on_error
    
    # Create Spark session
    spark = create_spark("spark-sql-runner")
    
    try:
        # Dry run mode
        if args.dry_run:
            log.info("=== DRY RUN MODE ===")
            if args.sql_file:
                content = read_sql_file(spark, args.sql_file)
            else:
                content = args.sql_text
            
            statements = parse_sql_statements(content)
            log.info(f"Parsed {len(statements)} statements:")
            for i, sql in enumerate(statements, 1):
                log.info(f"Statement {i}: {sql[:100]}...")
            return
        
        # Execute SQL
        if args.sql_file:
            results = execute_sql_file_wrapper(
                spark, args.sql_file, continue_on_error, args.database
            )
        else:
            results = execute_sql_text_wrapper(
                spark, args.sql_text, continue_on_error, args.database
            )
        
        # Save results if requested
        if args.output_path and results:
            save_results(spark, results, args.output_path)
        
        # Exit with appropriate code
        error_count = sum(1 for r in results if r["status"] == "error")
        if error_count > 0:
            log.warning(f"Completed with {error_count} errors")
            sys.exit(1)
        else:
            log.info("All statements executed successfully")
            sys.exit(0)
    
    except KeyboardInterrupt:
        log.info("Execution stopped by user")
        sys.exit(0)
    except Exception as e:
        log.error(f"Execution failed: {e}")
        sys.exit(1)
    finally:
        spark.stop()
        log.info("Spark session closed")

if __name__ == "__main__":
    main()