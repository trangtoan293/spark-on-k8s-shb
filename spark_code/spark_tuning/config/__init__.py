"""
Configuration Module

Generates optimal Spark configurations for different environments and workload types.
"""

from spark_tuning.config.config_generator import ConfigGenerator
from spark_tuning.config.optimal_configs import OptimalConfigs

__all__ = ["ConfigGenerator", "OptimalConfigs"]
