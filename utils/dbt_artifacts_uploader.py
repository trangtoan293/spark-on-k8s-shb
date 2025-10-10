import logging
import mimetypes
import os
import subprocess
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)


def _detect_mime(path: Path) -> str:
    mime, _ = mimetypes.guess_type(str(path))
    return mime or "application/octet-stream"


def collect_artifacts(
    base_dir: str,
    target_dir: str = "target",
    logs_dir: str = "logs",
    extra_files: Optional[List[str]] = None,
) -> List[Path]:
    """Collect common dbt artifacts from a dbt project directory.

    Args:
        base_dir: The dbt project directory (cwd during run).
        target_dir: Target dir name or relative path within base_dir.
        logs_dir: Logs dir name or relative path within base_dir.
        extra_files: Additional file paths (relative to base_dir) to include.

    Returns:
        List of Paths to upload (existing files only).
    """
    base = Path(base_dir)
    tdir = base / target_dir
    ldir = base / logs_dir

    candidates = [
        tdir / "manifest.json",
        tdir / "run_results.json",
        tdir / "catalog.json",
        ldir / "dbt.log",
    ]

    if extra_files:
        candidates.extend(base / f for f in extra_files)

    artifacts = [p for p in candidates if p.exists() and p.is_file()]

    if not artifacts:
        logger.warning("No dbt artifacts found to upload (checked target/logs)")

    return artifacts


def _upload_via_boto3(
    paths: List[Path],
    bucket: str,
    prefix: str,
    endpoint_url: Optional[str] = None,
    region_name: Optional[str] = None,
    access_key: Optional[str] = None,
    secret_key: Optional[str] = None,
    session_token: Optional[str] = None,
    verify_ssl: bool = True,
) -> bool:
    try:
        import boto3  # type: ignore
        from botocore.exceptions import BotoCoreError, ClientError  # type: ignore

        # Fallbacks from environment
        endpoint = endpoint_url or os.environ.get("AWS_ENDPOINT_URL")
        region = region_name or os.environ.get("AWS_DEFAULT_REGION")

        client_kwargs = {}
        if endpoint:
            client_kwargs["endpoint_url"] = endpoint
        if region:
            client_kwargs["region_name"] = region
        if access_key and secret_key:
            client_kwargs["aws_access_key_id"] = access_key
            client_kwargs["aws_secret_access_key"] = secret_key
            if session_token:
                client_kwargs["aws_session_token"] = session_token
        # SSL verification control
        client_kwargs["verify"] = verify_ssl

        s3 = boto3.client("s3", **client_kwargs)

        # Normalize prefix
        norm_prefix = prefix.rstrip("/") if prefix else ""

        ok = True
        for p in paths:
            try:
                key = f"{norm_prefix}/{p.name}" if norm_prefix else p.name
                extra_args = {"ContentType": _detect_mime(p)}
                logger.info(f"Uploading via boto3 s3://{bucket}/{key} <- {p}")
                s3.upload_file(str(p), bucket, key, ExtraArgs=extra_args)
            except (ClientError, BotoCoreError, Exception) as e:
                ok = False
                logger.error(f"boto3 upload failed for {p}: {e}")
        return ok
    except ModuleNotFoundError:
        logger.info("boto3 not installed; will try AWS CLI fallback")
        return False
    except Exception as e:
        logger.error(f"boto3 upload failed: {e}")
        return False


def _upload_via_aws_cli(
    paths: List[Path],
    bucket: str,
    prefix: str,
    endpoint_url: Optional[str] = None,
) -> bool:
    ok = True
    for p in paths:
        key = f"{prefix.rstrip('/')}/{p.name}" if prefix else p.name
        dest = f"s3://{bucket}/{key}"
        cmd = ["aws", "s3", "cp", str(p), dest]
        if endpoint_url or os.environ.get("AWS_ENDPOINT_URL"):
            cmd.extend(["--endpoint-url", endpoint_url or os.environ.get("AWS_ENDPOINT_URL")])
        logger.info(f"Uploading via aws cli: {' '.join(cmd)}")
        try:
            res = subprocess.run(cmd, check=False, capture_output=True, text=True)
            if res.returncode != 0:
                ok = False
                logger.error(
                    f"aws s3 cp failed for {p} -> {dest}, code={res.returncode}, stderr={res.stderr.strip()}"
                )
        except FileNotFoundError:
            logger.error("AWS CLI not found. Please install boto3 or awscli, or set up another uploader.")
            return False
        except Exception as e:
            logger.error(f"AWS CLI upload error for {p}: {e}")
            ok = False
    return ok


def upload_dbt_artifacts(
    bucket: str,
    prefix: str = "",
    project_dir: Optional[str] = None,
    target_dir: str = "target",
    logs_dir: str = "logs",
    extra_files: Optional[List[str]] = None,
    # MinIO/AWS options
    endpoint_url: Optional[str] = None,
    region_name: Optional[str] = None,
    access_key: Optional[str] = None,
    secret_key: Optional[str] = None,
    session_token: Optional[str] = None,
    verify_ssl: bool = True,
) -> bool:
    """Collect and upload dbt artifacts to S3.

    Attempts boto3 first, then falls back to AWS CLI.

    Args:
        bucket: Target S3 bucket name.
        prefix: Optional prefix within bucket (e.g. "dbt/artifacts/2025-10-10").
        project_dir: dbt project directory; defaults to current working dir.
        target_dir: Relative path/name of target folder.
        logs_dir: Relative path/name of logs folder.
        extra_files: Additional relative file paths.

    Returns:
        True if all uploads succeed; False otherwise.
    """
    pdir = project_dir or os.getcwd()

    artifacts = collect_artifacts(
        base_dir=pdir, target_dir=target_dir, logs_dir=logs_dir, extra_files=extra_files
    )
    if not artifacts:
        logger.warning("No artifacts to upload. Skipping S3 upload.")
        return False

    # Try boto3 first
    if _upload_via_boto3(
        artifacts,
        bucket=bucket,
        prefix=prefix,
        endpoint_url=endpoint_url,
        region_name=region_name,
        access_key=access_key,
        secret_key=secret_key,
        session_token=session_token,
        verify_ssl=verify_ssl,
    ):
        return True

    # Fallback to AWS CLI
    return _upload_via_aws_cli(
        artifacts,
        bucket=bucket,
        prefix=prefix,
        endpoint_url=endpoint_url or os.environ.get("AWS_ENDPOINT_URL"),
    )
