from __future__ import annotations

from anyuri import FileUri
from anyuri.providers._s3 import S3Uri
from anyuri.io._registry import register_download, register_upload


@register_download(S3Uri)
def _s3_download(uri: S3Uri, target: FileUri) -> FileUri:
    try:
        import boto3  # type: ignore[import]
    except ImportError:
        raise ImportError("Install anyuri[s3] for S3 support: pip install anyuri[s3]")
    boto3.client("s3").download_file(uri.netloc, uri.path.lstrip("/"), str(target))
    return target


@register_upload(S3Uri)
def _s3_upload(src: FileUri, dst: S3Uri) -> S3Uri:
    try:
        import boto3  # type: ignore[import]
    except ImportError:
        raise ImportError("Install anyuri[s3] for S3 support: pip install anyuri[s3]")
    boto3.client("s3").upload_file(str(src), dst.netloc, dst.path.lstrip("/"))
    return dst
