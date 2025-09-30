import os
from typing import Dict, Optional

REQUIRED_ORACLE_VARS = [
    "ORACLE_HOST",
    "ORACLE_SERVICE",
    "ORACLE_USERNAME",
    "ORACLE_PASSWORD",
]


def require_env(name: str, default: Optional[str] = None, required: bool = True) -> str:
    val = os.getenv(name, default)
    if required and (val is None or val == ""):
        raise ValueError(f"Missing environment variable: {name}")
    return val


def oracle_config() -> Dict[str, str]:
    # Validate required variables
    for v in REQUIRED_ORACLE_VARS:
        require_env(v)
    return {
        "host": require_env("ORACLE_HOST"),
        "port": os.getenv("ORACLE_PORT", "1521"),
        "service": require_env("ORACLE_SERVICE"),
        "username": require_env("ORACLE_USERNAME"),
        "password": require_env("ORACLE_PASSWORD"),
    }


def checkpoint_backend(default: str = "table") -> str:
    backend = os.getenv("CHECKPOINT_BACKEND", default).lower()
    if backend not in ("table", "json"):
        backend = default
    return backend
