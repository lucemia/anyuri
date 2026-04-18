from __future__ import annotations

from urllib.parse import urlparse

from anyuri import FileUri
from anyuri.providers._s3 import S3Uri
from anyuri.io._registry import register_download, register_upload


@register_download(S3Uri)
def _s3_download(uri: S3Uri, target: FileUri) -> FileUri:
    try:
        import boto3  # type: ignore[import]
    except ImportError:
        raise ImportError("Install anyuri[s3] for S3 support: pip install anyuri[s3]")
    p = urlparse(uri.as_uri())
    bucket_name = p.netloc
    key = p.path.lstrip("/")
    boto3.client("s3").download_file(bucket_name, key, str(target))
    return target


@register_upload(S3Uri)
def _s3_upload(src: FileUri, dst: S3Uri) -> S3Uri:
    try:
        import boto3  # type: ignore[import]
    except ImportError:
        raise ImportError("Install anyuri[s3] for S3 support: pip install anyuri[s3]")
    p = urlparse(dst.as_uri())
    bucket_name = p.netloc
    key = p.path.lstrip("/")
    boto3.client("s3").upload_file(str(src), bucket_name, key)
    return dst


__all__ = ["_s3_download", "_s3_upload"]
