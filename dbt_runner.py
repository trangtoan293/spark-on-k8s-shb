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
import argparse

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def install_dbt_dependencies(use_subprocess=False, dbt_command="dbt"):
    """Install dbt project dependencies if packages.yml exists
    
    Args:
        use_subprocess: If True, use subprocess to run dbt deps command
        dbt_command: Command to use (default: 'dbt', can be 'ktl_dbt')
    """
    
    packages_file = Path("packages.yml")
    if not packages_file.exists():
        logger.info("📦 No packages.yml found, skipping dependency installation")
        return True
    
    logger.info("📦 Found packages.yml, installing dbt dependencies...")
    
    try:
        if use_subprocess:
            from dbt.cli.main import dbtRunner
            dbt = dbtRunner()
            result = dbt.invoke(['deps'])
            
            if result.success:
                logger.info("✅ dbt dependencies installed successfully")
                return True
            else:
                logger.error("❌ dbt deps command failed")
                if result.exception:
                    logger.error(f"Exception: {result.exception}")
                return False
        else:
            # Use dbtRunner (original method)
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

def run_dbt_subprocess(dbt_command, dbt_args):
    """Run dbt command using subprocess
    
    Args:
        dbt_command: Command to use ('dbt' or 'ktl_dbt')
        dbt_args: List of arguments to pass to dbt command
    
    Returns:
        bool: True if command succeeded, False otherwise
    """
    try:
        cmd = [dbt_command] + dbt_args
        logger.info(f"🚀 Running command via subprocess: {' '.join(cmd)}")
        
        # Run command with real-time output
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Print output in real-time
        for line in process.stdout:
            print(line, end='')
        
        # Wait for process to complete
        return_code = process.wait()
        
        if return_code == 0:
            logger.info("✅ dbt command completed successfully")
            return True
        else:
            logger.error(f"❌ dbt command failed with return code: {return_code}")
            return False
            
    except FileNotFoundError:
        logger.error(f"❌ Command not found: {dbt_command}")
        logger.error(f"Make sure {dbt_command} is installed and available in PATH")
        return False
    except Exception as e:
        logger.error(f"❌ Error running dbt command: {str(e)}")
        return False

def main():
    """Main entry point for external dbt runner"""
    
    # Parse arguments
    parser = argparse.ArgumentParser(description='dbt Runner with subprocess support')
    parser.add_argument('--use-subprocess', action='store_true', 
                        help='Use subprocess to run dbt command instead of dbtRunner')
    parser.add_argument('--dbt-command', default='dbt', 
                        help='dbt command to use (default: dbt, can use ktl_dbt)')
    
    # Parse known args to separate our flags from dbt args
    args, remaining_args = parser.parse_known_args()
    
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
    
    # Get dbt command arguments
    dbt_args = []
    skip_next = False
    
    for arg in remaining_args:
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
    logger.info(f"📋 Execution mode: {'subprocess' if args.use_subprocess else 'dbtRunner'}")
    if args.use_subprocess:
        logger.info(f"📋 Using command: {args.dbt_command}")
    
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
        if not install_dbt_dependencies(
            use_subprocess=args.use_subprocess, 
            dbt_command=args.dbt_command
        ):
            logger.error("Failed to install dbt dependencies")
            sys.exit(1)
        
        # Run dbt command based on execution mode
        if args.use_subprocess:
            # Use subprocess method
            success = run_dbt_subprocess(args.dbt_command, dbt_args)
            if not success:
                sys.exit(1)
        else:
            # Use dbtRunner method (original)
            from dbt.cli.main import dbtRunner, dbtRunnerResult
            dbt = dbtRunner()
            
            # Run command
            logger.info(f"🚀 Running dbt command: {' '.join(dbt_args)}")

            res: dbtRunnerResult = dbt.invoke(dbt_args)
            # inspect the results
            for r in res.result:
                logger.info(f"{r.node.name}: {r.status}")
            if res.success:
                logger.info("✅ dbt command completed successfully")
            else:
                logger.error("❌ dbt command failed")
                if res.exception:
                    logger.error(f"Exception: {res.exception}")
                sys.exit(1)
            
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