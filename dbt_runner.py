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

def install_dbt_dependencies():
    """Install dbt project dependencies if packages.yml exists"""
    
    packages_file = Path("packages.yml")
    if not packages_file.exists():
        logger.info("📦 No packages.yml found, skipping dependency installation")
        return True
    
    logger.info("📦 Found packages.yml, installing dbt dependencies...")
    
    try:
        from dbt.cli.main import dbtRunner
        dbt = dbtRunner()
        
        # Run dbt deps command
        logger.info("🔄 Running dbt deps command")
        result = dbt.invoke(['deps'])
        
        if result.success:
            logger.info("✅ dbt dependencies installed successfully")
            return True
        else:
            logger.error("❌ dbt deps command failed")
            if result.exception:
                logger.error(f"Exception: {result.exception}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error installing dbt dependencies: {str(e)}")
        return False

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
    
    # Create writable directories in temp space
    os.makedirs("/tmp/dbt_target", exist_ok=True)
    os.makedirs("/tmp/dbt_logs", exist_ok=True)
    logger.info("Created writable temp directories for dbt target and logs")
    
    # Get dbt command arguments from Spark args
    dbt_args = []
    skip_next = False
    
    for arg in sys.argv[1:]:
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
        
        # Install dbt dependencies first
        if not install_dbt_dependencies():
            logger.error("Failed to install dbt dependencies")
            sys.exit(1)
        
        from dbt.cli.main import dbtRunner
        dbt = dbtRunner()
        
        # Run command
        logger.info(f"🚀 Running dbt command: {' '.join(dbt_args)}")
        
        result = dbt.invoke(dbt_args)
        
        if result.success:
            logger.info("✅ dbt command completed successfully")
            return True
        else:
            logger.error("❌ dbt command failed")
            if result.exception:
                logger.error(f"Exception: {result.exception}")
            return False
            
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