"""
Centralized Configuration Management
=====================================

All environment variable configurations for the Spark ETL pipeline.
Supports Oracle, MySQL, and control table configurations.

Environment Variables:
----------------------

Oracle Connection:
- ORACLE_HOST (required)
- ORACLE_PORT (default: 1521)
- ORACLE_SERVICE (required)
- ORACLE_USERNAME (required)
- ORACLE_PASSWORD (required)

MySQL Connection:
- MYSQL_HOST (required)
- MYSQL_PORT (default: 3306)
- MYSQL_DATABASE (required)
- MYSQL_USERNAME (required)
- MYSQL_PASSWORD (required)

MS SQL Server Connection:
- MSSQL_HOST (required)
- MSSQL_PORT (default: 1433)
- MSSQL_DATABASE (required)
- MSSQL_USERNAME (required)
- MSSQL_PASSWORD (required)

Control Tables:
- CONTROL_DB (default: etladmin)
- CHECKPOINT_TABLE (default: {CONTROL_DB}.cdc_checkpoint)
- JOB_LOG_TABLE (default: {CONTROL_DB}.job_run_logs)

Checkpoint:
- CHECKPOINT_BACKEND (default: table, options: table|json)
- CHECKPOINT_LOCATION (default: s3a://data/checkpoints)

Logging:
- LOG_LEVEL (default: INFO)
- LOG_FORMAT (default: standard format)
"""

import os
from typing import Dict, Optional
from dataclasses import dataclass


# ============================================================================
# Helper Functions
# ============================================================================

def require_env(name: str, default: Optional[str] = None, required: bool = True) -> str:
    """Get environment variable with validation."""
    val = os.getenv(name, default)
    if required and (val is None or val == ""):
        raise ValueError(f"Missing required environment variable: {name}")
    return val


def get_env(name: str, default: str = "") -> str:
    """Get environment variable with default."""
    return os.getenv(name, default)


# ============================================================================
# Oracle Configuration
# ============================================================================

REQUIRED_ORACLE_VARS = [
    "ORACLE_HOST",
    "ORACLE_SERVICE",
    "ORACLE_USERNAME",
    "ORACLE_PASSWORD",
]


@dataclass
class OracleConfig:
    """Oracle database connection configuration."""
    host: str
    port: str
    service: str
    username: str
    password: str
    
    @property
    def jdbc_url(self) -> str:
        """Build JDBC URL."""
        # Do NOT embed credentials in the URL to avoid issues with special characters (e.g., '@').
        # Credentials are passed separately via Spark options (user/password).
        return f"jdbc:oracle:thin:@//{self.host}:{self.port}/{self.service}"
    
    @property
    def safe_url(self) -> str:
        """JDBC URL with masked credentials."""
        # No credentials embedded; show sanitized URL
        return f"jdbc:oracle:thin:@//{self.host}:{self.port}/{self.service}"


def oracle_config() -> OracleConfig:
    """Get Oracle configuration from environment variables."""
    return OracleConfig(
        host=require_env("ORACLE_HOST"),
        port=get_env("ORACLE_PORT", "1521"),
        service=require_env("ORACLE_SERVICE"),
        username=require_env("ORACLE_USERNAME"),
        password=require_env("ORACLE_PASSWORD"),
    )


# ============================================================================
# MySQL Configuration
# ============================================================================

REQUIRED_MYSQL_VARS = [
    "MYSQL_HOST",
    "MYSQL_DATABASE",
    "MYSQL_USERNAME",
    "MYSQL_PASSWORD",
]


@dataclass
class MySQLConfig:
    """MySQL database connection configuration."""
    host: str
    port: str
    database: str
    username: str
    password: str
    
    @property
    def jdbc_url(self) -> str:
        """Build JDBC URL."""
        return f"jdbc:mysql://{self.host}:{self.port}/{self.database}?useSSL=false&allowPublicKeyRetrieval=true"
    
    @property
    def safe_url(self) -> str:
        """JDBC URL with masked credentials."""
        return f"jdbc:mysql://{self.host}:{self.port}/{self.database}"


def mysql_config() -> MySQLConfig:
    """Get MySQL configuration from environment variables."""
    return MySQLConfig(
        host=require_env("MYSQL_HOST"),
        port=get_env("MYSQL_PORT", "3306"),
        database=require_env("MYSQL_DATABASE"),
        username=require_env("MYSQL_USERNAME"),
        password=require_env("MYSQL_PASSWORD"),
    )


# ============================================================================
# MS SQL Server Configuration
# ============================================================================

REQUIRED_MSSQL_VARS = [
    "MSSQL_HOST",
    "MSSQL_DATABASE",
    "MSSQL_USERNAME",
    "MSSQL_PASSWORD",
]


@dataclass
class MSSQLConfig:
    """MS SQL Server database connection configuration."""
    host: str
    port: str
    database: str
    username: str
    password: str
    
    @property
    def jdbc_url(self) -> str:
        """Build JDBC URL."""
        return f"jdbc:sqlserver://{self.host}:{self.port};databaseName={self.database};encrypt=true;trustServerCertificate=true"
    
    @property
    def safe_url(self) -> str:
        """JDBC URL with masked credentials."""
        return f"jdbc:sqlserver://{self.host}:{self.port};databaseName={self.database}"


def mssql_config() -> MSSQLConfig:
    """Get MS SQL Server configuration from environment variables."""
    return MSSQLConfig(
        host=require_env("MSSQL_HOST"),
        port=get_env("MSSQL_PORT", "1433"),
        database=require_env("MSSQL_DATABASE"),
        username=require_env("MSSQL_USERNAME"),
        password=require_env("MSSQL_PASSWORD"),
    )


# ============================================================================
# Control Tables Configuration
# ============================================================================

@dataclass
class ControlConfig:
    """Control tables configuration."""
    control_db: str
    checkpoint_table: str
    job_log_table: str
    
    @property
    def full_checkpoint_table(self) -> str:
        """Full checkpoint table name."""
        return f"{self.control_db}.{self.checkpoint_table}"
    
    @property
    def full_job_log_table(self) -> str:
        """Full job log table name."""
        return f"{self.control_db}.{self.job_log_table}"


def control_config() -> ControlConfig:
    """Get control tables configuration from environment variables."""
    control_db = get_env("CONTROL_DB", "etladmin")
    return ControlConfig(
        control_db=control_db,
        checkpoint_table=get_env("CHECKPOINT_TABLE", "cdc_checkpoint"),
        job_log_table=get_env("JOB_LOG_TABLE", "job_run_logs"),
    )


# ============================================================================
# Checkpoint Configuration
# ============================================================================

@dataclass
class CheckpointConfig:
    """Checkpoint backend configuration."""
    backend: str  # "table" or "json"
    location: str  # S3/MinIO path for JSON backend
    
    @property
    def is_table_backend(self) -> bool:
        """Check if using table backend."""
        return self.backend == "table"
    
    @property
    def is_json_backend(self) -> bool:
        """Check if using JSON backend."""
        return self.backend == "json"


def checkpoint_config() -> CheckpointConfig:
    """Get checkpoint configuration from environment variables."""
    backend = get_env("CHECKPOINT_BACKEND", "table").lower()
    if backend not in ("table", "json"):
        backend = "table"
    
    return CheckpointConfig(
        backend=backend,
        location=get_env("CHECKPOINT_LOCATION", "s3a://data/checkpoints"),
    )


# ============================================================================
# Logging Configuration
# ============================================================================

def log_level() -> str:
    """Get log level from environment."""
    return get_env("LOG_LEVEL", "INFO").upper()


def log_format() -> str:
    """Get log format from environment."""
    return get_env("LOG_FORMAT", "%(asctime)s [%(levelname)s] %(name)s - %(message)s")
