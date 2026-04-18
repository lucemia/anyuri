from __future__ import annotations

from anyuri import FileUri
from anyuri.io._registry import register_download, register_upload
from anyuri.providers._r2 import R2Uri


@register_download(R2Uri)
def _r2_download(uri: R2Uri, target: FileUri) -> FileUri:
    try:
        import boto3
    except ImportError:
        raise ImportError("Install anyuri[r2] for R2 support: pip install anyuri[r2]")
    path_parts = uri.path.lstrip("/").split("/", 1)
    bucket_name = path_parts[0]
    key = path_parts[1] if len(path_parts) > 1 else ""
    s3 = boto3.client("s3", endpoint_url=f"https://{uri.netloc}.r2.cloudflarestorage.com")
    s3.download_file(bucket_name, key, str(target))
    return target


@register_upload(R2Uri)
def _r2_upload(src: FileUri, dst: R2Uri) -> R2Uri:
    try:
        import boto3
    except ImportError:
        raise ImportError("Install anyuri[r2] for R2 support: pip install anyuri[r2]")
    path_parts = dst.path.lstrip("/").split("/", 1)
    bucket_name = path_parts[0]
    key = path_parts[1] if len(path_parts) > 1 else ""
    s3 = boto3.client("s3", endpoint_url=f"https://{dst.netloc}.r2.cloudflarestorage.com")
    s3.upload_file(str(src), bucket_name, key)
    return dst
