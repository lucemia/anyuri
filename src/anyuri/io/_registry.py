from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeAlias

from anyuri import AnyUri, FileUri

DownloadHandler: TypeAlias = Callable[[Any, FileUri], FileUri]
UploadHandler: TypeAlias = Callable[[FileUri, Any], AnyUri]

_download_registry: dict[type[AnyUri], DownloadHandler] = {}
_upload_registry: dict[type[AnyUri], UploadHandler] = {}


def register_download(uri_cls: type[AnyUri]) -> Callable[[DownloadHandler], DownloadHandler]:
    def decorator(fn: DownloadHandler) -> DownloadHandler:
        _download_registry[uri_cls] = fn
        return fn

    return decorator


def register_upload(uri_cls: type[AnyUri]) -> Callable[[UploadHandler], UploadHandler]:
    def decorator(fn: UploadHandler) -> UploadHandler:
        _upload_registry[uri_cls] = fn
        return fn

    return decorator


__all__ = ["register_download", "register_upload"]
