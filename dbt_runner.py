#!/usr/bin/env python3
"""
dbt Runner for External Git Repository Integration
Wrapper script để run dbt từ external git repository với Spark environment
"""

import sys
import os
from pathlib import Path
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
            # Run deps in a separate process to avoid importing adapters in-runner
            logger.info("🔄 Running dbt deps via subprocess")
            return run_dbt_subprocess(dbt_command, ['deps'])
        else:
            # Use dbtRunner (in-process)
            from dbt.cli.main import dbtRunner
            dbt = dbtRunner()

            logger.info("🔄 Running dbt deps (in-process)")
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
    # Optional: upload artifacts to S3 after successful run
    parser.add_argument('--upload-artifacts', action='store_true',
                        help='Upload dbt artifacts (manifest, run_results, catalog, dbt.log) to S3 after a successful run')
    parser.add_argument('--s3-bucket',
                        help='Target S3 bucket for artifacts (required when --upload-artifacts)')
    parser.add_argument('--s3-prefix', default='',
                        help='Optional S3 key prefix for uploaded artifacts, e.g. "dbt/artifacts/2025-10-10"')
    parser.add_argument('--artifacts-target-dir', default='target',
                        help='Relative target dir containing dbt artifacts (default: target)')
    parser.add_argument('--artifacts-logs-dir', default='logs',
                        help='Relative logs dir containing dbt.log (default: logs)')
    # MinIO/S3 options
    parser.add_argument('--s3-endpoint-url', default=None,
                        help='Custom S3/MinIO endpoint URL (e.g., http://minio:9000)')
    parser.add_argument('--s3-region', default=None,
                        help='AWS region name (default inferred or env AWS_DEFAULT_REGION)')
    parser.add_argument('--s3-access-key-id', default=None,
                        help='Explicit S3 access key ID (MinIO/AWS)')
    parser.add_argument('--s3-secret-access-key', default=None,
                        help='Explicit S3 secret access key (MinIO/AWS)')
    parser.add_argument('--s3-session-token', default=None,
                        help='Optional AWS session token')
    parser.add_argument('--s3-no-verify-ssl', action='store_true',
                        help='Disable SSL verification for S3/MinIO (useful for self-signed)')
    # Note: uploads run sequentially; no concurrency settings needed
    
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

    # Import uploader only when needed and after switching into the project dir so that
    # Python can resolve the local package path (fixes ModuleNotFoundError in k8s driver)
    if args.upload_artifacts:
        try:
            # Ensure the dbt project directory is on sys.path for module resolution
            if dbt_project_dir not in sys.path:
                sys.path.insert(0, dbt_project_dir)
            from utils.dbt_artifacts_uploader import upload_dbt_artifacts
        except ModuleNotFoundError:
            logger.error("No module named 'utils.dbt_artifacts_uploader'. Ensure the project contains 'utils/' with __init__.py and the uploader module, and that we run from the project root.")
            sys.exit(1)
    
    # Create writable directories in temp space
    os.makedirs("/tmp/dbt_target", exist_ok=True)
    os.makedirs("/tmp/dbt_logs", exist_ok=True)
    logger.info("Created writable temp directories for dbt target and logs")
    # Honor deprecation guidance: prefer env/CLI over dbt_project.yml for target/log paths
    # Set env defaults only if not already provided from outside
    if not os.environ.get('DBT_TARGET_PATH'):
        os.environ['DBT_TARGET_PATH'] = "/tmp/dbt_target"
    if not os.environ.get('DBT_LOG_PATH'):
        os.environ['DBT_LOG_PATH'] = "/tmp/dbt_logs"
    logger.info(f"Using DBT_TARGET_PATH={os.environ.get('DBT_TARGET_PATH')}, DBT_LOG_PATH={os.environ.get('DBT_LOG_PATH')}")

    # Compute initial effective artifact directories for uploader (can be overridden by CLI)
    effective_target_dir = args.artifacts_target_dir
    effective_logs_dir = args.artifacts_logs_dir
    if effective_target_dir == 'target' and os.environ.get('DBT_TARGET_PATH'):
        effective_target_dir = os.environ['DBT_TARGET_PATH']
    if effective_logs_dir == 'logs' and os.environ.get('DBT_LOG_PATH'):
        effective_logs_dir = os.environ['DBT_LOG_PATH']
    logger.info(f"Initial artifact dirs: target_dir={effective_target_dir}, logs_dir={effective_logs_dir}")
    
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

    # Detect explicit CLI overrides for paths and align env/effective dirs
    cli_target_path = None
    cli_log_path = None
    i = 0
    while i < len(dbt_args):
        tok = dbt_args[i]
        if tok == '--target-path' and i + 1 < len(dbt_args):
            cli_target_path = dbt_args[i + 1]
            i += 2
            continue
        if tok.startswith('--target-path='):
            cli_target_path = tok.split('=', 1)[1]
            i += 1
            continue
        if tok == '--log-path' and i + 1 < len(dbt_args):
            cli_log_path = dbt_args[i + 1]
            i += 2
            continue
        if tok.startswith('--log-path='):
            cli_log_path = tok.split('=', 1)[1]
            i += 1
            continue
        i += 1

    if cli_target_path:
        os.environ['DBT_TARGET_PATH'] = cli_target_path
        effective_target_dir = cli_target_path
        logger.info(f"Detected CLI --target-path, using {cli_target_path}")
    if cli_log_path:
        os.environ['DBT_LOG_PATH'] = cli_log_path
        effective_logs_dir = cli_log_path
        logger.info(f"Detected CLI --log-path, using {cli_log_path}")

    logger.info(f"Artifacts will be collected from target_dir={effective_target_dir}, logs_dir={effective_logs_dir}")
    
    # Default command if no args provided
    if not dbt_args:
        dbt_args = ['run', '--target', 'dev']
    
    logger.info(f"🚀 Starting dbt with args: {dbt_args}")
    logger.info(f"📋 Execution mode: {'subprocess' if args.use_subprocess else 'dbtRunner'}")
    if args.use_subprocess:
        logger.info(f"📋 Using command: {args.dbt_command}")
    
    # Do NOT create a SparkSession here.
    # dbt-spark will manage SparkSession/Context internally. Creating one here can
    # lead to "Only one SparkContext should be running in this JVM" (SPARK-2243).
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
            # After a successful run, optionally upload artifacts to S3
            if args.upload_artifacts:
                if not args.s3_bucket:
                    logger.error("--s3-bucket is required when --upload-artifacts is set")
                    sys.exit(1)
                # Get credentials from CLI args or environment variables
                access_key = args.s3_access_key_id or os.environ.get('AWS_ACCESS_KEY_ID')
                secret_key = args.s3_secret_access_key or os.environ.get('AWS_SECRET_ACCESS_KEY')
                session_token = args.s3_session_token or os.environ.get('AWS_SESSION_TOKEN')
                endpoint_url = args.s3_endpoint_url or os.environ.get('AWS_ENDPOINT_URL')
                region = args.s3_region or os.environ.get('AWS_DEFAULT_REGION')

                uploaded = upload_dbt_artifacts(
                    bucket=args.s3_bucket,
                    prefix=args.s3_prefix or '',
                    project_dir=dbt_project_dir,
                    target_dir=effective_target_dir,
                    logs_dir=effective_logs_dir,
                    endpoint_url=endpoint_url,
                    region_name=region,
                    access_key=access_key,
                    secret_key=secret_key,
                    session_token=session_token,
                    verify_ssl=(not args.s3_no_verify_ssl),
                )
                if uploaded:
                    logger.info("✅ Uploaded dbt artifacts to S3")
                else:
                    logger.error("❌ Failed to upload dbt artifacts to S3")
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
                # After a successful run, optionally upload artifacts to S3
                if args.upload_artifacts:
                    if not args.s3_bucket:
                        logger.error("--s3-bucket is required when --upload-artifacts is set")
                        sys.exit(1)
                    # Get credentials from CLI args or environment variables
                    access_key = args.s3_access_key_id or os.environ.get('AWS_ACCESS_KEY_ID')
                    secret_key = args.s3_secret_access_key or os.environ.get('AWS_SECRET_ACCESS_KEY')
                    session_token = args.s3_session_token or os.environ.get('AWS_SESSION_TOKEN')
                    endpoint_url = args.s3_endpoint_url or os.environ.get('AWS_ENDPOINT_URL')
                    region = args.s3_region or os.environ.get('AWS_DEFAULT_REGION')

                    uploaded = upload_dbt_artifacts(
                        bucket=args.s3_bucket,
                        prefix=args.s3_prefix or '',
                        project_dir=dbt_project_dir,
                        target_dir=effective_target_dir,
                        logs_dir=effective_logs_dir,
                        endpoint_url=endpoint_url,
                        region_name=region,
                        access_key=access_key,
                        secret_key=secret_key,
                        session_token=session_token,
                        verify_ssl=(not args.s3_no_verify_ssl),
                    )
                    if uploaded:
                        logger.info("✅ Uploaded dbt artifacts to S3")
                    else:
                        logger.error("❌ Failed to upload dbt artifacts to S3")
            else:
                logger.error("❌ dbt command failed")
                if res.exception:
                    logger.error(f"Exception: {res.exception}")
                sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Error running dbt: {str(e)}")
        sys.exit(1)
    finally:
        # Nothing to stop; let dbt-spark manage Spark lifecycle
        pass

if __name__ == "__main__":
    main()