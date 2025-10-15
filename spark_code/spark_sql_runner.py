#!/usr/bin/env python3
"""
Spark SQL Executor - Simplified Version (WITH TUNING)
========================================

Execute SQL statements from files or text using Spark SQL.
Simplified architecture using utility modules for better maintainability.

**NEW**: Integrated with spark_tuning for performance monitoring and optimization

Usage:
    python spark_sql_runner.py --sql-file queries.sql
    python spark_sql_runner.py --sql-file queries.sql --database demo
    python spark_sql_runner.py --sql-text "SELECT * FROM demo.customers; SHOW TABLES;"
    python spark_sql_runner.py --sql-file queries.sql --enable-tuning  # With optimization analysis

Version: 2.1.0 - Added spark_tuning integration
"""

import sys
import argparse
from typing import List, Dict, Any

# Import utilities
from utils.logging import get_logger
from utils.spark import create_spark
from utils.sql_reader import read_sql_file
import os
from utils.sql_parser import parse_sql_statements
from utils.sql_executor import execute_statements, save_results

# Import spark_tuning for performance monitoring
from spark_tuning import (
    MetricsCollector,
    PerformanceProfiler,
    QueryOptimizer,
    ResourceTracker
)

log = get_logger(__name__)

def execute_sql_file_wrapper(
    spark,
    file_path: str,
    continue_on_error: bool = True,
    default_database: str = None,
    profiler: PerformanceProfiler = None
) -> List[Dict[str, Any]]:
    """Execute SQL file with multiple statements (with optional profiling)"""
    log.info(f"=== Executing SQL file: {file_path} ===")
    
    # Read and parse SQL file
    if profiler:
        @profiler.profile_function("read_sql_file")
        def read_file():
            return read_sql_file(spark, file_path)
        sql_content = read_file()
    else:
        sql_content = read_sql_file(spark, file_path)
    # Substitute branch placeholder
    branch_val = None
    try:
        branch_val = spark.conf.get('spark.wap.branch')
    except Exception:
        branch_val = os.environ.get('WAP_BRANCH')
    if branch_val:
        sql_content = sql_content.replace('${WAP_BRANCH}', branch_val)
    
    statements = parse_sql_statements(sql_content)
    
    if not statements:
        log.warning("No SQL statements found in file")
        return []
    
    # Execute statements
    if profiler:
        @profiler.profile_function("execute_statements")
        def exec_stmts():
            return execute_statements(spark, statements, continue_on_error, default_database)
        return exec_stmts()
    else:
        return execute_statements(spark, statements, continue_on_error, default_database)


def execute_sql_text_wrapper(
    spark,
    sql_text: str,
    continue_on_error: bool = True,
    default_database: str = None,
    profiler: PerformanceProfiler = None
) -> List[Dict[str, Any]]:
    """Execute SQL text with multiple statements (with optional profiling)"""
    log.info("=== Executing SQL text ===")
    
    # Substitute branch placeholder
    branch_val = None
    try:
        branch_val = spark.conf.get('spark.wap.branch')
    except Exception:
        branch_val = os.environ.get('WAP_BRANCH')
    if branch_val:
        sql_text = sql_text.replace('${WAP_BRANCH}', branch_val)
    # Parse SQL statements
    statements = parse_sql_statements(sql_text)
    
    if not statements:
        log.warning("No SQL statements found in text")
        return []
    
    # Execute statements
    if profiler:
        @profiler.profile_function("execute_statements")
        def exec_stmts():
            return execute_statements(spark, statements, continue_on_error, default_database)
        return exec_stmts()
    else:
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
    
    # Tuning options
    parser.add_argument("--enable-tuning", action="store_true",
                       help="Enable performance monitoring and optimization analysis")
    parser.add_argument("--export-metrics", help="Export metrics to JSON file")
    
    args = parser.parse_args()
    continue_on_error = not args.stop_on_error
    
    # Create Spark session
    spark = create_spark("spark-sql-runner")
    
    # Initialize tuning tools if enabled
    collector = None
    profiler = None
    tracker = None
    
    if args.enable_tuning:
        log.info("=== Spark Tuning Enabled ===")
        collector = MetricsCollector(spark)
        profiler = PerformanceProfiler(spark, auto_analyze=True)
        tracker = ResourceTracker(spark, enable_alerts=True)
        tracker.capture_snapshot()  # Initial snapshot
    
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
                spark, args.sql_file, continue_on_error, args.database, profiler
            )
        else:
            results = execute_sql_text_wrapper(
                spark, args.sql_text, continue_on_error, args.database, profiler
            )
        
        # Save results if requested
        if args.output_path and results:
            save_results(spark, results, args.output_path)
        
        # Print tuning reports if enabled
        if args.enable_tuning:
            log.info("\n" + "="*80)
            log.info("SPARK TUNING REPORT")
            log.info("="*80)
            
            # Print metrics summary
            if collector:
                collector.print_summary()
            
            # Print performance profile
            if profiler:
                profiler.print_profile_summary()
            
            # Print resource summary and alerts
            if tracker:
                tracker.capture_snapshot()  # Final snapshot
                tracker.print_resource_summary()
                
                # Show critical alerts
                alerts = tracker.get_active_alerts("CRITICAL")
                if alerts:
                    log.warning(f"\n⚠️  {len(alerts)} CRITICAL ALERTS:")
                    for alert in alerts[:3]:  # Top 3
                        log.warning(f"  - {alert.message}")
            
            # Export metrics if requested
            if args.export_metrics and collector:
                collector.export_to_json(args.export_metrics)
                log.info(f"\n📊 Metrics exported to: {args.export_metrics}")
        
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