from __future__ import annotations

from anyuri import FileUri
from anyuri.providers._gcs import GSUri
from anyuri.io._registry import register_download, register_upload


@register_download(GSUri)
def _gcs_download(uri: GSUri, target: FileUri) -> FileUri:
    try:
        from google.cloud import storage  # type: ignore[import]
    except ImportError:
        raise ImportError("Install anyuri[gcs] for GCS support: pip install anyuri[gcs]")
    client = storage.Client()
    client.bucket(uri.netloc).blob(uri.path.lstrip("/")).download_to_filename(str(target))
    return target


@register_upload(GSUri)
def _gcs_upload(src: FileUri, dst: GSUri) -> GSUri:
    try:
        from google.cloud import storage  # type: ignore[import]
    except ImportError:
        raise ImportError("Install anyuri[gcs] for GCS support: pip install anyuri[gcs]")
    client = storage.Client()
    client.bucket(dst.netloc).blob(dst.path.lstrip("/")).upload_from_filename(str(src))
    return dst
