import os
import logging
import mimetypes
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


def _resolve_dir(base_dir: str, path: str) -> Path:
    p = Path(path)
    if not p.is_absolute():
        p = Path(base_dir) / p
    return p


def _detect_mime(path: Path) -> str:
    mime, _ = mimetypes.guess_type(str(path))
    return mime or "application/octet-stream"


def collect_artifacts(
    base_dir: str,
    target_dir: str,
    logs_dir: str,
):
    base = Path(base_dir)
    tdir = _resolve_dir(base, target_dir)
    ldir = _resolve_dir(base, logs_dir)

    candidates = [
        tdir / "manifest.json",
        tdir / "run_results.json",
        tdir / "catalog.json",
        tdir / "sources.json",
        ldir / "dbt.log",
    ]

    artifacts = [p for p in candidates if p.exists() and p.is_file()]
    if not artifacts:
        logger.warning("No dbt artifacts found to upload (checked target/logs)")
    return artifacts


def _make_s3_client(endpoint_url, region_name, access_key, secret_key, session_token, verify_ssl):
    try:
        import boto3  # type: ignore
    except ImportError:
        return None

    # Fallbacks from environment if not provided
    endpoint = endpoint_url or os.environ.get("AWS_ENDPOINT_URL")
    region = region_name or os.environ.get("AWS_DEFAULT_REGION")
    ak = access_key or os.environ.get("AWS_ACCESS_KEY_ID")
    sk = secret_key or os.environ.get("AWS_SECRET_ACCESS_KEY")
    st = session_token or os.environ.get("AWS_SESSION_TOKEN")

    client_kwargs = {"verify": verify_ssl}
    if endpoint:
        client_kwargs["endpoint_url"] = endpoint
    if region:
        client_kwargs["region_name"] = region
    if ak and sk:
        client_kwargs["aws_access_key_id"] = ak
        client_kwargs["aws_secret_access_key"] = sk
        if st:
            client_kwargs["aws_session_token"] = st

    try:
        import boto3  # type: ignore
        s3 = boto3.client("s3", **client_kwargs)
        return s3
    except Exception:
        return None


def _upload_via_boto3(s3, bucket: str, key: str, local_path: Path) -> bool:
    try:
        extra_args = {"ContentType": _detect_mime(local_path)}
        s3.upload_file(str(local_path), bucket, key, ExtraArgs=extra_args)
        logger.info(f"Uploaded via boto3 s3://{bucket}/{key} <- {local_path}")
        return True
    except Exception as e:
        logger.error(f"boto3 upload failed for {local_path}: {e}")
        return False


def _upload_via_aws_cli(bucket: str, key: str, local_path: Path, endpoint_url: str | None) -> bool:
    dest = f"s3a://{bucket}/{key}"
    cmd = ["aws", "s3", "cp", str(local_path), dest]
    ep = endpoint_url or os.environ.get("AWS_ENDPOINT_URL")
    if ep:
        cmd.extend(["--endpoint-url", ep])
    logger.info(f"Uploading via aws cli: {' '.join(cmd)}")
    try:
        res = subprocess.run(cmd, check=False, capture_output=True, text=True)
        if res.returncode != 0:
            logger.error(
                f"aws s3 cp failed for {local_path} -> {dest}, code={res.returncode}, stderr={res.stderr.strip()}"
            )
            return False
        return True
    except FileNotFoundError:
        logger.error("AWS CLI not found. Please install boto3 or awscli, or set up another uploader.")
        return False
    except Exception as e:
        logger.error(f"AWS CLI upload error for {local_path}: {e}")
        return False


def upload_dbt_artifacts(
    bucket: str,
    prefix: str,
    project_dir: str,
    target_dir: str,
    logs_dir: str,
    endpoint_url=None,
    region_name=None,
    access_key=None,
    secret_key=None,
    session_token=None,
    verify_ssl=True,
) -> bool:
    # Collect artifacts
    artifacts = collect_artifacts(
        base_dir=project_dir, target_dir=target_dir, logs_dir=logs_dir
    )
    if not artifacts:
        logger.error("No dbt artifacts found to upload")
        return False

    pref = (prefix or "").strip("/")
    s3 = _make_s3_client(endpoint_url, region_name, access_key, secret_key, session_token, verify_ssl)

    uploaded_all = True
    for p in artifacts:
        key = f"{pref}/{p.name}" if pref else p.name
        ok = False
        if s3 is not None:
            ok = _upload_via_boto3(s3, bucket, key, p)
        if not ok:
            if not _upload_via_aws_cli(bucket, key, p, endpoint_url):
                uploaded_all = False

    return uploaded_all
