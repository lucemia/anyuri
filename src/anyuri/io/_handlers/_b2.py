from __future__ import annotations

from urllib.parse import urlparse

from anyuri import FileUri
from anyuri.providers._b2 import B2Uri
from anyuri.io._registry import register_download, register_upload


@register_download(B2Uri)
def _b2_download(uri: B2Uri, target: FileUri) -> FileUri:
    try:
        import b2sdk.v2 as b2  # type: ignore[import]
    except ImportError:
        raise ImportError("Install anyuri[b2] for B2 support: pip install anyuri[b2]")
    p = urlparse(uri.as_uri())  # b2://bucket/key
    bucket_name = p.netloc
    file_name = p.path.lstrip("/")
    api = b2.B2Api(b2.InMemoryAccountInfo())
    bucket = api.get_bucket_by_name(bucket_name)
    bucket.download_file_by_name(file_name).save_to(str(target))
    return target


@register_upload(B2Uri)
def _b2_upload(src: FileUri, dst: B2Uri) -> B2Uri:
    try:
        import b2sdk.v2 as b2  # type: ignore[import]
    except ImportError:
        raise ImportError("Install anyuri[b2] for B2 support: pip install anyuri[b2]")
    p = urlparse(dst.as_uri())  # b2://bucket/key
    bucket_name = p.netloc
    file_name = p.path.lstrip("/")
    api = b2.B2Api(b2.InMemoryAccountInfo())
    bucket = api.get_bucket_by_name(bucket_name)
    bucket.upload_local_file(local_file=str(src), file_name=file_name)
    return dst


__all__ = ["_b2_download", "_b2_upload"]
