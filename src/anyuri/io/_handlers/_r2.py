from __future__ import annotations

from urllib.parse import urlparse

from anyuri import FileUri
from anyuri.providers._r2 import R2Uri
from anyuri.io._registry import register_download, register_upload


@register_download(R2Uri)
def _r2_download(uri: R2Uri, target: FileUri) -> FileUri:
    try:
        import boto3  # type: ignore[import]
    except ImportError:
        raise ImportError("Install anyuri[r2] for R2 support: pip install anyuri[r2]")
    p = urlparse(uri.as_uri())  # r2://accountid/bucket/key
    account_id = p.netloc
    path_parts = p.path.lstrip("/").split("/", 1)
    bucket_name = path_parts[0]
    key = path_parts[1] if len(path_parts) > 1 else ""
    s3 = boto3.client("s3", endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com")
    s3.download_file(bucket_name, key, str(target))
    return target


@register_upload(R2Uri)
def _r2_upload(src: FileUri, dst: R2Uri) -> R2Uri:
    try:
        import boto3  # type: ignore[import]
    except ImportError:
        raise ImportError("Install anyuri[r2] for R2 support: pip install anyuri[r2]")
    p = urlparse(dst.as_uri())  # r2://accountid/bucket/key
    account_id = p.netloc
    path_parts = p.path.lstrip("/").split("/", 1)
    bucket_name = path_parts[0]
    key = path_parts[1] if len(path_parts) > 1 else ""
    s3 = boto3.client("s3", endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com")
    s3.upload_file(str(src), bucket_name, key)
    return dst


__all__ = ["_r2_download", "_r2_upload"]
