from __future__ import annotations

from anyuri._exceptions import DownloadError, UploadError

from anyuri import AnyUri, FileUri
from anyuri.io._registry import (
    _download_registry,
    _upload_registry,
    register_download,
    register_upload,
)


def test_download_error_is_exception() -> None:
    err = DownloadError("failed")
    assert isinstance(err, Exception)
    assert str(err) == "failed"


def test_upload_error_is_exception() -> None:
    err = UploadError("failed")
    assert isinstance(err, Exception)
    assert str(err) == "failed"


def test_register_download_adds_to_registry(clean_io_registry: None) -> None:
    class DummyUri(AnyUri):
        pass

    @register_download(DummyUri)
    def _handler(uri: DummyUri, target: FileUri) -> FileUri:
        return target

    assert _download_registry[DummyUri] is _handler


def test_register_upload_adds_to_registry(clean_io_registry: None) -> None:
    class DummyUri(AnyUri):
        pass

    @register_upload(DummyUri)
    def _handler(src: FileUri, dst: DummyUri) -> DummyUri:
        return dst

    assert _upload_registry[DummyUri] is _handler


def test_register_download_returns_function(clean_io_registry: None) -> None:
    class DummyUri(AnyUri):
        pass

    def _handler(uri: DummyUri, target: FileUri) -> FileUri:
        return target

    result = register_download(DummyUri)(_handler)
    assert result is _handler


def test_register_upload_returns_function(clean_io_registry: None) -> None:
    class DummyUri(AnyUri):
        pass

    def _handler(src: FileUri, dst: DummyUri) -> DummyUri:
        return dst

    result = register_upload(DummyUri)(_handler)
    assert result is _handler
