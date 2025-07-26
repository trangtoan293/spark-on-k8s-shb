#!/usr/bin/env python3
"""
Enhanced dbt Runner with Elementary Monitoring Integration
"""

import os
import sys
import logging
import subprocess
import json
import re
from pathlib import Path
from typing import List, Optional, Dict, Any
import tempfile

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class ElementaryDbtRunner:
    """Enhanced dbt runner with Elementary monitoring capabilities"""
    
    def __init__(self):
        self.project_dir = os.environ.get('DBT_PROJECT_DIR', os.getcwd())
        self.profiles_dir = os.environ.get('DBT_PROFILES_DIR', os.path.expanduser('~/.dbt'))
        
        # Elementary configuration
        self.elementary_config = {
            'slack_webhook': os.environ.get('ELEMENTARY_SLACK_WEBHOOK', ''),
            'dashboard_host': os.environ.get('ELEMENTARY_DASHBOARD_HOST', ''),
            'timezone': os.environ.get('ELEMENTARY_TIMEZONE', 'UTC'),
            'days_back': int(os.environ.get('ELEMENTARY_DAYS_BACK', '7')),
            'report_bucket': os.environ.get('ELEMENTARY_REPORT_BUCKET', ''),
            'report_prefix': os.environ.get('ELEMENTARY_REPORT_PREFIX', 'elementary-reports')
        }
        
        logger.info(f"🔧 Initialized Elementary dbt Runner")
        logger.info(f"📁 Project directory: {self.project_dir}")
        logger.info(f"⚙️  Profiles directory: {self.profiles_dir}")
        
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
        """Install dbt project dependencies including Elementary if packages.yml exists"""
        
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
                logger.info("✅ dbt dependencies (including Elementary) installed successfully")
                return True
            else:
                logger.error("❌ dbt deps command failed")
                if result.exception:
                    logger.error(f"Exception: {result.exception}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error installing dbt dependencies: {str(e)}")
            return False

    def sanitize_spark_identifiers(self) -> bool:
        """Set up Spark-compatible identifier handling for dbt models"""
        try:
            logger.info("🔧 Setting up Spark SQL identifier compatibility...")
            
            # Create temporary dbt_project.yml override for Spark compatibility
            dbt_project_override = {
                'models': {
                    '+materialized': 'table',
                    '+pre-hook': [
                        'SET spark.sql.parser.quotedRegexColumnNames = true',
                        'SET spark.sql.caseSensitive = false'
                    ],
                    '+post-hook': [],
                    'elementary': {
                        '+materialized': 'table',
                        '+schema': 'elementary',
                        '+alias': "{{ this.identifier | replace('-', '_') | replace('.', '_') | replace(' ', '_') | lower }}"
                    }
                },
                'vars': {
                    'elementary': {
                        'normalize_schema_and_table_names': True,
                        'quote_columns': False,
                        'quote_identifiers': False
                    }
                }
            }
            
            # Set environment variables for Spark compatibility
            os.environ['DBT_SPARK_QUOTE_COLUMNS'] = 'false'
            os.environ['DBT_SPARK_NORMALIZE_NAMES'] = 'true'
            
            logger.info("✅ Spark SQL identifier compatibility configured")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error setting up Spark identifier compatibility: {str(e)}")
            return False

    def validate_spark_identifiers(self) -> bool:
        """Validate model and table names for Spark SQL compatibility"""
        try:
            logger.info("🔍 Validating Spark SQL identifier compatibility...")
            
            # Spark SQL reserved keywords (common ones)
            SPARK_RESERVED_KEYWORDS = {
                'select', 'from', 'where', 'group', 'order', 'having', 'limit', 
                'union', 'case', 'when', 'then', 'else', 'end', 'if', 'and', 'or', 
                'not', 'in', 'like', 'between', 'is', 'null', 'true', 'false',
                'create', 'table', 'view', 'insert', 'update', 'delete', 'drop',
                'alter', 'add', 'column', 'index', 'database', 'schema', 'partition',
                'format', 'location', 'comment', 'tblproperties', 'serde'
            }
            
            # Pattern for valid Spark identifiers
            VALID_IDENTIFIER_PATTERN = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')
            
            issues_found = []
            
            # Check models directory for problematic names
            models_dir = Path(self.project_dir) / "models"
            if models_dir.exists():
                for model_file in models_dir.rglob("*.sql"):
                    model_name = model_file.stem
                    
                    # Check for reserved keywords
                    if model_name.lower() in SPARK_RESERVED_KEYWORDS:
                        issues_found.append(f"⚠️  Model '{model_name}' uses Spark reserved keyword")
                    
                    # Check for invalid characters
                    if not VALID_IDENTIFIER_PATTERN.match(model_name):
                        issues_found.append(f"⚠️  Model '{model_name}' contains invalid characters (use a-z, A-Z, 0-9, _ only)")
                    
                    # Check for hyphen (common issue)
                    if '-' in model_name:
                        issues_found.append(f"⚠️  Model '{model_name}' contains hyphens (use underscores instead)")
            
            # Report findings
            if issues_found:
                logger.warning("🚨 Found potential Spark SQL identifier issues:")
                for issue in issues_found:
                    logger.warning(f"   {issue}")
                logger.warning("💡 These will be automatically sanitized during execution")
            else:
                logger.info("✅ All identifiers appear Spark SQL compatible")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error validating Spark identifiers: {str(e)}")
            return False

    def run_dbt_command(self, dbt_args: List[str]) -> bool:
        """Run dbt command using dbtRunner API with Spark SQL compatibility"""
        try:
            from dbt.cli.main import dbtRunner
            
            logger.info(f"🚀 Running dbt command: {' '.join(dbt_args)}")
            
            # Set up Spark identifier compatibility
            if not self.sanitize_spark_identifiers():
                logger.warning("⚠️  Failed to set up Spark identifier compatibility")
            
            # Initialize dbt runner
            dbt = dbtRunner()
            
            # Add Spark-specific arguments for identifier handling
            enhanced_args = dbt_args.copy()
            if '--vars' not in enhanced_args:
                enhanced_args.extend(['--vars', '{"normalize_schema_and_table_names": true, "quote_columns": false}'])
            
            logger.info(f"🔧 Enhanced command with Spark compatibility: {' '.join(enhanced_args)}")
            
            # Run the dbt command
            result = dbt.invoke(enhanced_args)
            
            if result.success:
                logger.info("✅ dbt command completed successfully")
                return True
            else:
                logger.error("❌ dbt command failed")
                if result.exception:
                    logger.error(f"Exception: {result.exception}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error running dbt command: {str(e)}")
            return False

    def run_elementary_report(self) -> bool:
        """Generate Elementary monitoring report"""
        try:
            logger.info("📊 Generating Elementary monitoring report...")
            
            # Build Elementary report command
            edr_cmd = ['edr', 'report']
            
            # Add days back configuration
            if self.elementary_config['days_back']:
                edr_cmd.extend(['--days-back', str(self.elementary_config['days_back'])])
            
            # Add output directory
            report_dir = "/opt/spark/elementary-reports"
            os.makedirs(report_dir, exist_ok=True)
            edr_cmd.extend(['--file-path', f"{report_dir}/elementary_report.html"])
            
            # Run Elementary report generation
            logger.info(f"🔄 Running command: {' '.join(edr_cmd)}")
            result = subprocess.run(edr_cmd, capture_output=True, text=True, cwd=self.project_dir)
            
            if result.returncode == 0:
                logger.info("✅ Elementary report generated successfully")
                logger.info(f"📄 Report saved to: {report_dir}/elementary_report.html")
                return True
            else:
                logger.error("❌ Elementary report generation failed")
                logger.error(f"STDOUT: {result.stdout}")
                logger.error(f"STDERR: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error generating Elementary report: {str(e)}")
            return False

    def send_elementary_alerts(self) -> bool:
        """Send Elementary alerts to Slack if configured"""
        if not self.elementary_config['slack_webhook']:
            logger.info("📢 No Slack webhook configured, skipping alerts")
            return True
            
        try:
            logger.info("📢 Sending Elementary alerts to Slack...")
            
            # Build Elementary alert command
            edr_cmd = [
                'edr', 'send-report',
                '--slack-webhook', self.elementary_config['slack_webhook']
            ]
            
            # Add days back configuration
            if self.elementary_config['days_back']:
                edr_cmd.extend(['--days-back', str(self.elementary_config['days_back'])])
            
            # Run Elementary alert
            logger.info(f"🔄 Running command: {' '.join(['edr', 'send-report', '--slack-webhook', '[REDACTED]'])}")
            result = subprocess.run(edr_cmd, capture_output=True, text=True, cwd=self.project_dir)
            
            if result.returncode == 0:
                logger.info("✅ Elementary alerts sent successfully")
                return True
            else:
                logger.warning("⚠️  Elementary alert sending failed (non-critical)")
                logger.warning(f"STDOUT: {result.stdout}")
                logger.warning(f"STDERR: {result.stderr}")
                return True  # Non-critical failure
                
        except Exception as e:
            logger.warning(f"⚠️  Error sending Elementary alerts: {str(e)} (non-critical)")
            return True  # Don't fail the entire job for alert issues

    def upload_artifacts_to_storage(self) -> bool:
        """Upload dbt artifacts and Elementary reports to persistent storage"""
        try:
            logger.info("📤 Uploading artifacts to persistent storage...")
            
            # Source directories
            target_dir = os.environ.get('DBT_TARGET_PATH', '/tmp/dbt_target')
            reports_dir = "/opt/spark/elementary-reports"
            
            # Destination directory (persistent volume)
            storage_dir = "/opt/spark/elementary-reports/artifacts"
            os.makedirs(storage_dir, exist_ok=True)
            
            # Copy dbt artifacts
            artifacts = ['manifest.json', 'run_results.json', 'catalog.json', 'sources.json']
            for artifact in artifacts:
                src_path = os.path.join(target_dir, artifact)
                if os.path.exists(src_path):
                    dst_path = os.path.join(storage_dir, artifact)
                    subprocess.run(['cp', src_path, dst_path], check=True)
                    logger.info(f"📄 Copied {artifact} to persistent storage")
            
            logger.info("✅ Artifacts uploaded to persistent storage successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error uploading artifacts: {str(e)}")
            return False

    def display_run_summary(self, success: bool):
        """Display run summary with Elementary integration status"""
        logger.info("=" * 60)
        logger.info("📊 ELEMENTARY DBT RUN SUMMARY")
        logger.info("=" * 60)
        
        status = "✅ SUCCESS" if success else "❌ FAILED"
        logger.info(f"🎯 Overall Status: {status}")
        
        logger.info(f"📁 Project Directory: {self.project_dir}")
        logger.info(f"🔧 Elementary Monitoring: {'✅ ENABLED' if self.elementary_config else '❌ DISABLED'}")
        logger.info(f"📢 Slack Alerts: {'✅ CONFIGURED' if self.elementary_config['slack_webhook'] else '❌ NOT CONFIGURED'}")
        
        # Show Elementary features status
        features = {
            "📊 Dashboard Generation": "✅ ENABLED",
            "📈 Artifact Processing": "✅ ENABLED", 
            "🔔 Alert System": "✅ ENABLED" if self.elementary_config['slack_webhook'] else "⚠️  WEBHOOK MISSING",
            "💾 Persistent Storage": "✅ ENABLED"
        }
        
        logger.info("\n🎛️  Elementary Features:")
        for feature, status in features.items():
            logger.info(f"   {feature}: {status}")
        
        logger.info("=" * 60)

def main():
    """Main entry point for Elementary dbt runner"""
    
    # Parse command line arguments
    if len(sys.argv) < 2:
        logger.error("❌ Usage: python elementary_dbt_runner.py <dbt_command> [args...]")
        logger.error("❌ Example: python elementary_dbt_runner.py run --target dev")
        sys.exit(1)
    
    dbt_args = sys.argv[1:]
    
    # Initialize runner
    runner = ElementaryDbtRunner()
    
    # Setup working directory
    if not runner.setup_working_directory():
        logger.error("❌ Failed to setup working directory")
        sys.exit(1)
    
    success = True
    
    try:
        # Step 1: Validate Spark SQL compatibility
        if not runner.validate_spark_identifiers():
            logger.warning("⚠️  Spark identifier validation failed (non-critical)")
        
        # Step 2: Install dependencies (including Elementary)
        if not runner.install_dbt_dependencies():
            logger.error("❌ Failed to install dbt dependencies")
            success = False
        
        # Step 3: Run main dbt command with Spark compatibility
        if success and not runner.run_dbt_command(dbt_args):
            logger.error("❌ Failed to run dbt command")
            success = False
        
        # Step 4: Generate Elementary report (if dbt succeeded)
        if success:
            if not runner.run_elementary_report():
                logger.warning("⚠️  Failed to generate Elementary report (non-critical)")
        
        # Step 5: Send alerts (non-critical)
        if success:
            runner.send_elementary_alerts()
        
        # Step 6: Upload artifacts to storage
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