from __future__ import annotations

from collections.abc import Callable
from typing import Any

from anyuri import AnyUri, FileUri

_download_registry: dict[type[AnyUri], Callable[[Any, FileUri], FileUri]] = {}
_upload_registry: dict[type[AnyUri], Callable[[FileUri, Any], AnyUri]] = {}


def register_download(
    uri_cls: type[AnyUri],
) -> Callable[[Callable[[Any, FileUri], FileUri]], Callable[[Any, FileUri], FileUri]]:
    def decorator(fn: Callable[[Any, FileUri], FileUri]) -> Callable[[Any, FileUri], FileUri]:
        _download_registry[uri_cls] = fn
        return fn

    return decorator


def register_upload(
    uri_cls: type[AnyUri],
) -> Callable[[Callable[[FileUri, Any], AnyUri]], Callable[[FileUri, Any], AnyUri]]:
    def decorator(fn: Callable[[FileUri, Any], AnyUri]) -> Callable[[FileUri, Any], AnyUri]:
        _upload_registry[uri_cls] = fn
        return fn

    return decorator


__all__ = ["register_download", "register_upload", "_download_registry", "_upload_registry"]
