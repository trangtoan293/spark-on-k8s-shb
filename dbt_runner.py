#!/usr/bin/env python3
"""
dbt Runner for External Git Repository Integration
Wrapper script để run dbt từ external git repository với Spark environment
"""

import sys
import os
from pathlib import Path
from pyspark.sql import SparkSession
import subprocess
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Main entry point for external dbt runner"""
    
    # Set up paths
    dbt_project_dir = "/opt/spark/work-dir/dbt-project"
    
    # Validate dbt project directory exists
    if not Path(dbt_project_dir).exists():
        logger.error(f"dbt project directory not found: {dbt_project_dir}")
        logger.error("Make sure git-sync init container has pulled the dbt project")
        sys.exit(1)
    
    # Change to dbt project directory
    os.chdir(dbt_project_dir)
    logger.info(f"Changed working directory to: {dbt_project_dir}")
    
    # Set environment variables
    os.environ['DBT_PROFILES_DIR'] = dbt_project_dir
    os.environ['DBT_PROJECT_DIR'] = dbt_project_dir
    
    # Get dbt command arguments from Spark args
    dbt_args = []
    skip_next = False
    
    for i, arg in enumerate(sys.argv[1:], 1):
        if skip_next:
            skip_next = False
            continue
            
        # Skip Spark-specific arguments
        if arg in ['driver', '--properties-file', '--class']:
            skip_next = True
            continue
        elif arg.startswith('org.apache.spark') or arg.startswith('local://'):
            continue
        else:
            dbt_args.append(arg)
    
    # Default command if no args provided
    if not dbt_args:
        dbt_args = ['run', '--target', 'dev']
    
    logger.info(f"🚀 Starting dbt with args: {dbt_args}")
    
    # Initialize Spark Session (reuse existing context if available)
    try:
        spark = SparkSession.getActiveSession()
        if spark is None:
            logger.info("No active Spark session found, creating new one")
            spark = SparkSession.builder.appName("dbt-external-runner").getOrCreate()
        else:
            logger.info("Reusing existing Spark session")
    except Exception as e:
        logger.warning(f"Spark session setup issue: {e}")
        spark = None
    
    try:
        # Validate dbt project files
        required_files = ['dbt_project.yml', 'profiles.yml']
        for file in required_files:
            if not Path(file).exists():
                logger.error(f"Required file not found: {file}")
                sys.exit(1)
        
        # List project contents for debugging
        logger.info("dbt project contents:")
        for item in Path('.').iterdir():
            logger.info(f"  - {item.name}")
        
        # Run dbt command
        cmd = ['dbt'] + dbt_args
        logger.info(f"🔧 Executing: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("✅ dbt command completed successfully")
            print(result.stdout)
        else:
            logger.error("❌ dbt command failed")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            sys.exit(result.returncode)
            
    except Exception as e:
        logger.error(f"❌ Error running dbt: {str(e)}")
        sys.exit(1)
    finally:
        if spark:
            try:
                spark.stop()
                logger.info("Spark session stopped")
            except:
                pass

if __name__ == "__main__":
    main()