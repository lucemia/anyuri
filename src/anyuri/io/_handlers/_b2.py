from __future__ import annotations

from anyuri import FileUri
from anyuri.io._registry import register_download, register_upload
from anyuri.providers._b2 import B2Uri


@register_download(B2Uri)
def _b2_download(uri: B2Uri, target: FileUri) -> FileUri:
    try:
        import b2sdk.v2 as b2
    except ImportError:
        raise ImportError("Install anyuri[b2] for B2 support: pip install anyuri[b2]")
    api = b2.B2Api(b2.InMemoryAccountInfo())
    bucket = api.get_bucket_by_name(uri.netloc)
    bucket.download_file_by_name(uri.path.lstrip("/")).save_to(str(target))
    return target


@register_upload(B2Uri)
def _b2_upload(src: FileUri, dst: B2Uri) -> B2Uri:
    try:
        import b2sdk.v2 as b2
    except ImportError:
        raise ImportError("Install anyuri[b2] for B2 support: pip install anyuri[b2]")
    api = b2.B2Api(b2.InMemoryAccountInfo())
    bucket = api.get_bucket_by_name(dst.netloc)
    bucket.upload_local_file(local_file=str(src), file_name=dst.path.lstrip("/"))
    return dst
