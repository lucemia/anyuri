from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeAlias

from anyuri import AnyUri, FileUri

DownloadHandler: TypeAlias = Callable[[Any, FileUri], FileUri]
UploadHandler: TypeAlias = Callable[[FileUri, Any], AnyUri]

_download_registry: dict[type[AnyUri], DownloadHandler] = {}
_upload_registry: dict[type[AnyUri], UploadHandler] = {}


def register_download(uri_cls: type[AnyUri]) -> Callable[[DownloadHandler], DownloadHandler]:
    """Register a download handler for a URI type.

    The decorated function is called by :func:`anyuri.io.download` when it
    encounters a URI of type ``uri_cls``.

    Args:
        uri_cls: The ``AnyUri`` subclass this handler handles.

    Returns:
        A decorator that registers the function and returns it unchanged.

    Examples:
        >>> from anyuri.io._registry import register_download
        >>> @register_download(MyUri)
        ... def _my_download(uri: MyUri, target: FileUri) -> FileUri:
        ...     # fetch uri, write to target, return target
        ...     return target
    """

    def decorator(fn: DownloadHandler) -> DownloadHandler:
        _download_registry[uri_cls] = fn
        return fn

    return decorator


def register_upload(uri_cls: type[AnyUri]) -> Callable[[UploadHandler], UploadHandler]:
    """Register an upload handler for a URI type.

    The decorated function is called by :func:`anyuri.io.upload` when the
    destination URI is of type ``uri_cls``.

    Args:
        uri_cls: The ``AnyUri`` subclass this handler handles as a destination.

    Returns:
        A decorator that registers the function and returns it unchanged.

    Examples:
        >>> from anyuri.io._registry import register_upload
        >>> @register_upload(MyUri)
        ... def _my_upload(src: FileUri, dst: MyUri) -> MyUri:
        ...     # push src to dst, return dst
        ...     return dst
    """

    def decorator(fn: UploadHandler) -> UploadHandler:
        _upload_registry[uri_cls] = fn
        return fn

    return decorator


__all__ = ["register_download", "register_upload"]
