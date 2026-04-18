from __future__ import annotations

import os
import re
import tempfile
from uuid import uuid4

from anyuri import AnyUri, FileUri
from anyuri._exceptions import UriSchemaError
from anyuri.io._registry import _download_registry, _upload_registry


def _extract_ext(uri: AnyUri) -> str | None:
    name = uri.path.rstrip("/").rsplit("/", 1)[-1]
    m = re.search(r"\.[A-Za-z0-9]{1,10}$", name)
    return m.group(0) if m else None


def _dispatch_download(uri: AnyUri) -> FileUri:
    handler = _download_registry.get(type(uri))
    if handler is None:
        raise UriSchemaError(f"No download handler registered for {type(uri).__name__}")
    fd, path = tempfile.mkstemp(suffix=_extract_ext(uri) or ".tmp")
    os.close(fd)
    return handler(uri, FileUri(path))


def _dispatch_upload(src: FileUri, dst: AnyUri) -> AnyUri:
    handler = _upload_registry.get(type(dst))
    if handler is None:
        raise UriSchemaError(f"No upload handler registered for {type(dst).__name__}")
    return handler(src, dst)


def download(uri: AnyUri | str) -> FileUri:
    return _dispatch_download(uri if isinstance(uri, AnyUri) else AnyUri(uri))


def upload(src: AnyUri | str, dst: AnyUri | str) -> AnyUri:
    src_uri = src if isinstance(src, AnyUri) else AnyUri(src)
    dst_uri = dst if isinstance(dst, AnyUri) else AnyUri(dst)
    if not isinstance(src_uri, FileUri):
        src_uri = download(src_uri)
    if str(dst_uri).endswith("/"):
        ext = _extract_ext(src_uri) or ".tmp"
        dst_uri = AnyUri(str(dst_uri) + uuid4().hex + ext)
    return _dispatch_upload(src_uri, dst_uri)


__all__ = ["download", "upload"]
