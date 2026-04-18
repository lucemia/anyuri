from __future__ import annotations

from urllib.parse import urlparse

from anyuri import FileUri
from anyuri.providers._gcs import GSUri
from anyuri.io._registry import register_download, register_upload


@register_download(GSUri)
def _gcs_download(uri: GSUri, target: FileUri) -> FileUri:
    try:
        from google.cloud import storage  # type: ignore[import]
    except ImportError:
        raise ImportError("Install anyuri[gcs] for GCS support: pip install anyuri[gcs]")
    p = urlparse(uri.as_uri())
    bucket_name = p.netloc
    key = p.path.lstrip("/")
    client = storage.Client()
    client.bucket(bucket_name).blob(key).download_to_filename(str(target))
    return target


@register_upload(GSUri)
def _gcs_upload(src: FileUri, dst: GSUri) -> GSUri:
    try:
        from google.cloud import storage  # type: ignore[import]
    except ImportError:
        raise ImportError("Install anyuri[gcs] for GCS support: pip install anyuri[gcs]")
    p = urlparse(dst.as_uri())
    bucket_name = p.netloc
    key = p.path.lstrip("/")
    client = storage.Client()
    client.bucket(bucket_name).blob(key).upload_from_filename(str(src))
    return dst


__all__ = ["_gcs_download", "_gcs_upload"]
