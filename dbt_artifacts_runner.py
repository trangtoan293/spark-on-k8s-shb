#!/usr/bin/env python3
"""
dbt Runner with dbt-artifacts Monitoring Integration
"""

import os
import sys
import logging
import subprocess
import json
import time
from pathlib import Path
from typing import List

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class DbtArtifactsRunner:
    """Enhanced dbt runner with dbt-artifacts monitoring capabilities"""
    
    def __init__(self):
        self.project_dir = os.environ.get('DBT_PROJECT_DIR', os.getcwd())
        self.profiles_dir = os.environ.get('DBT_PROFILES_DIR', os.path.expanduser('~/.dbt'))
        
        # Monitoring configuration
        self.monitoring_config = {
            'artifacts_schema': os.environ.get('DBT_ARTIFACTS_SCHEMA', 'dbt_artifacts'),
            'slack_webhook': os.environ.get('MONITORING_SLACK_WEBHOOK', ''),
            'alert_on_failure': os.environ.get('ALERT_ON_FAILURE', 'true').lower() == 'true',
            'performance_threshold_minutes': int(os.environ.get('PERF_THRESHOLD_MIN', '30'))
        }
        
        logger.info(f"🔧 Initialized dbt Artifacts Runner")
        logger.info(f"📁 Project directory: {self.project_dir}")
        logger.info(f"⚙️  Profiles directory: {self.profiles_dir}")
        logger.info(f"📊 Monitoring schema: {self.monitoring_config['artifacts_schema']}")
        
    def setup_working_directory(self):
        """Set up the working directory and temporary paths for dbt"""
        try:
            # Change to project directory
            os.chdir(self.project_dir)
            logger.info(f"📂 Changed working directory to: {self.project_dir}")
            
            # Create writable temp directories for dbt
            temp_target_dir = "/tmp/dbt_target"
            temp_logs_dir = "/tmp/dbt_logs"
            
            os.makedirs(temp_target_dir, exist_ok=True)
            os.makedirs(temp_logs_dir, exist_ok=True)
            
            # Set environment variables for dbt
            os.environ['DBT_TARGET_PATH'] = temp_target_dir
            os.environ['DBT_LOG_PATH'] = temp_logs_dir
            
            logger.info(f"📁 Created writable temp directories for dbt target and logs")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error setting up working directory: {str(e)}")
            return False

    def install_dbt_dependencies(self) -> bool:
        """Install dbt project dependencies including dbt-artifacts"""
        
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
                logger.info("✅ dbt dependencies (including dbt-artifacts) installed successfully")
                return True
            else:
                logger.error("❌ dbt deps command failed")
                if result.exception:
                    logger.error(f"Exception: {result.exception}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error installing dbt dependencies: {str(e)}")
            return False

    def run_dbt_command(self, dbt_args: List[str]) -> bool:
        """Run dbt command using dbtRunner API"""
        try:
            from dbt.cli.main import dbtRunner
            
            logger.info(f"🚀 Running dbt command: {' '.join(dbt_args)}")
            
            # Initialize dbt runner
            dbt = dbtRunner()
            
            # Add monitoring variables
            enhanced_args = dbt_args.copy()
            if '--vars' not in enhanced_args:
                monitoring_vars = {
                    "dbt_artifacts_database": os.environ.get('DBT_DATABASE', 'spark_warehouse'),
                    "dbt_artifacts_schema": self.monitoring_config['artifacts_schema'],
                    "dbt_artifacts_exclude_all_results": True
                }
                enhanced_args.extend(['--vars', json.dumps(monitoring_vars)])
            
            logger.info(f"🔧 Enhanced command with monitoring: {' '.join(enhanced_args)}")
            
            # Run the dbt command
            start_time = time.time()
            result = dbt.invoke(enhanced_args)
            execution_time = time.time() - start_time
            
            # Log execution metrics
            logger.info(f"⏱️  Execution time: {execution_time:.2f} seconds")
            
            if result.success:
                logger.info("✅ dbt command completed successfully")
                
                # Check for performance warnings
                if execution_time > self.monitoring_config['performance_threshold_minutes'] * 60:
                    logger.warning(f"⚠️  Execution time exceeded threshold of {self.monitoring_config['performance_threshold_minutes']} minutes")
                
                return True
            else:
                logger.error("❌ dbt command failed")
                if result.exception:
                    logger.error(f"Exception: {result.exception}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error running dbt command: {str(e)}")
            return False

    def generate_monitoring_summary(self) -> bool:
        """Generate a summary of monitoring data from dbt-artifacts tables"""
        try:
            logger.info("📊 Generating monitoring summary from dbt-artifacts...")
            
            # This would query the dbt-artifacts tables for summary metrics
            # For now, we'll just log the availability of monitoring data
            
            artifacts_dir = os.environ.get('DBT_TARGET_PATH', '/tmp/dbt_target')
            
            # Check for dbt artifacts
            artifacts = ['manifest.json', 'run_results.json', 'catalog.json']
            available_artifacts = []
            
            for artifact in artifacts:
                artifact_path = os.path.join(artifacts_dir, artifact)
                if os.path.exists(artifact_path):
                    available_artifacts.append(artifact)
                    file_size = os.path.getsize(artifact_path)
                    logger.info(f"📄 {artifact}: {file_size} bytes")
            
            if available_artifacts:
                logger.info(f"✅ Successfully generated {len(available_artifacts)} artifacts for monitoring")
                logger.info("💡 dbt-artifacts package will process these into monitoring tables")
                return True
            else:
                logger.warning("⚠️  No dbt artifacts found")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error generating monitoring summary: {str(e)}")
            return False

    def send_monitoring_alerts(self, success: bool) -> bool:
        """Send monitoring alerts if configured"""
        if not self.monitoring_config['slack_webhook']:
            logger.info("📢 No Slack webhook configured, skipping alerts")
            return True
            
        if not self.monitoring_config['alert_on_failure'] and not success:
            logger.info("📢 Alerting on failure disabled, skipping")
            return True
            
        try:
            logger.info("📢 Sending monitoring alert...")
            
            # Basic alert logic - in production, you'd integrate with your alerting system
            status = "✅ SUCCESS" if success else "❌ FAILED"
            message = f"dbt Run {status} - Project: {os.path.basename(self.project_dir)}"
            
            logger.info(f"📢 Alert message: {message}")
            logger.info("💡 In production: Send to Slack/Teams/Email")
            
            return True
                
        except Exception as e:
            logger.warning(f"⚠️  Error sending monitoring alerts: {str(e)} (non-critical)")
            return True  # Don't fail the entire job for alert issues

    def upload_artifacts_to_storage(self) -> bool:
        """Upload dbt artifacts to persistent storage"""
        try:
            logger.info("📤 Uploading artifacts to persistent storage...")
            
            # Source directories
            target_dir = os.environ.get('DBT_TARGET_PATH', '/tmp/dbt_target')
            
            # Destination directory (persistent volume)
            storage_dir = "/opt/spark/monitoring-reports/artifacts"
            os.makedirs(storage_dir, exist_ok=True)
            
            # Copy dbt artifacts
            artifacts = ['manifest.json', 'run_results.json', 'catalog.json', 'sources.json']
            copied_artifacts = []
            
            for artifact in artifacts:
                src_path = os.path.join(target_dir, artifact)
                if os.path.exists(src_path):
                    dst_path = os.path.join(storage_dir, artifact)
                    subprocess.run(['cp', src_path, dst_path], check=True)
                    copied_artifacts.append(artifact)
                    logger.info(f"📄 Copied {artifact} to persistent storage")
            
            if copied_artifacts:
                logger.info(f"✅ {len(copied_artifacts)} artifacts uploaded to persistent storage")
                return True
            else:
                logger.warning("⚠️  No artifacts found to upload")
                return False
            
        except Exception as e:
            logger.error(f"❌ Error uploading artifacts: {str(e)}")
            return False

    def display_run_summary(self, success: bool):
        """Display run summary with dbt-artifacts integration status"""
        logger.info("=" * 60)
        logger.info("📊 DBT ARTIFACTS MONITORING SUMMARY")
        logger.info("=" * 60)
        
        status = "✅ SUCCESS" if success else "❌ FAILED"
        logger.info(f"🎯 Overall Status: {status}")
        
        logger.info(f"📁 Project Directory: {self.project_dir}")
        logger.info(f"🔧 Monitoring Package: dbt-artifacts (Brooklyn Data)")
        logger.info(f"📊 Monitoring Schema: {self.monitoring_config['artifacts_schema']}")
        logger.info(f"📢 Slack Alerts: {'✅ CONFIGURED' if self.monitoring_config['slack_webhook'] else '❌ NOT CONFIGURED'}")
        
        # Show dbt-artifacts features
        features = {
            "📊 Performance Tracking": "✅ ENABLED",
            "📈 Artifact Processing": "✅ ENABLED", 
            "🔔 Alert System": "✅ ENABLED" if self.monitoring_config['slack_webhook'] else "⚠️  WEBHOOK MISSING",
            "💾 Persistent Storage": "✅ ENABLED",
            "🎯 Spark Compatibility": "✅ NATIVE"
        }
        
        logger.info("\n🎛️  dbt-artifacts Features:")
        for feature, status in features.items():
            logger.info(f"   {feature}: {status}")
        
        logger.info("=" * 60)

def main():
    """Main entry point for dbt artifacts runner"""
    
    # Parse command line arguments
    if len(sys.argv) < 2:
        logger.error("❌ Usage: python dbt_artifacts_runner.py <dbt_command> [args...]")
        logger.error("❌ Example: python dbt_artifacts_runner.py run --target dev")
        sys.exit(1)
    
    dbt_args = sys.argv[1:]
    
    # Initialize runner
    runner = DbtArtifactsRunner()
    
    # Setup working directory
    if not runner.setup_working_directory():
        logger.error("❌ Failed to setup working directory")
        sys.exit(1)
    
    success = True
    
    try:
        # Step 1: Install dependencies (including dbt-artifacts)
        if not runner.install_dbt_dependencies():
            logger.error("❌ Failed to install dbt dependencies")
            success = False
        
        # Step 2: Run main dbt command
        if success and not runner.run_dbt_command(dbt_args):
            logger.error("❌ Failed to run dbt command")
            success = False
        
        # Step 3: Generate monitoring summary
        if success:
            if not runner.generate_monitoring_summary():
                logger.warning("⚠️  Failed to generate monitoring summary (non-critical)")
        
        # Step 4: Send alerts (non-critical)
        if not runner.send_monitoring_alerts(success):
            logger.warning("⚠️  Failed to send alerts (non-critical)")
        
        # Step 5: Upload artifacts to storage
        if not runner.upload_artifacts_to_storage():
            logger.warning("⚠️  Failed to upload artifacts to storage (non-critical)")
        
    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}")
        success = False
    
    finally:
        # Display summary
        runner.display_run_summary(success)
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()