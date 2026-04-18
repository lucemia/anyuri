from __future__ import annotations

import pathlib

import pytest

from anyuri import AnyUri, FileUri, HttpUri
from anyuri._exceptions import UriSchemaError
from anyuri.io._core import _dispatch_download, _dispatch_upload, _extract_ext, download, upload
from anyuri.io._registry import register_download, register_upload


@pytest.mark.parametrize(
    "uri_str, expected_ext",
    [
        ("https://example.com/video.mp4", ".mp4"),
        ("https://example.com/archive.tar.gz", ".gz"),
        ("/tmp/file.jpg", ".jpg"),
        ("https://example.com/no-ext", None),
        ("https://example.com/", None),
        ("https://example.com/toolong.abcdefghijk", None),
    ],
)
def test_extract_ext(uri_str: str, expected_ext: str | None) -> None:
    uri = AnyUri(uri_str)
    assert _extract_ext(uri) == expected_ext


def test_download_calls_handler_with_uri_and_target(clean_io_registry: None) -> None:
    class FooUri(AnyUri):
        def __new__(cls, v: object) -> FooUri:
            return str.__new__(cls, str(v))

        @classmethod
        def validate(cls, v: object) -> FooUri:
            return cls(v)

    AnyUri._registry.insert(0, FooUri)

    captured: dict[str, object] = {}

    @register_download(FooUri)
    def _handler(uri: FooUri, target: FileUri) -> FileUri:
        captured["uri"] = uri
        captured["target"] = target
        return target

    try:
        result = download(FooUri("foo://test/video.mp4"))
        assert isinstance(result, FileUri)
        assert captured["uri"] == "foo://test/video.mp4"
        assert str(result).endswith(".mp4")
    finally:
        AnyUri._registry.remove(FooUri)


def test_download_raises_for_unregistered_uri(clean_io_registry: None) -> None:
    class UnknownUri(AnyUri):
        def __new__(cls, v: object) -> UnknownUri:
            return str.__new__(cls, str(v))

    with pytest.raises(UriSchemaError, match="No download handler"):
        _dispatch_download(UnknownUri("x://foo"))


def test_upload_uses_exact_dst_path(clean_io_registry: None, tmp_path: pathlib.Path) -> None:
    src_path = str(tmp_path / "src.mp4")
    open(src_path, "w").close()
    src = FileUri(src_path)

    class DstUri(AnyUri):
        def __new__(cls, v: object) -> DstUri:
            return str.__new__(cls, str(v))

        @classmethod
        def validate(cls, v: object) -> DstUri:
            return cls(v)

    captured: dict[str, object] = {}

    @register_upload(DstUri)
    def _handler(s: FileUri, d: DstUri) -> DstUri:
        captured["dst"] = str(d)
        return d

    AnyUri._registry.insert(0, DstUri)
    try:
        dst = DstUri("dst://bucket/exact.mp4")
        upload(src, dst)
        assert captured["dst"] == "dst://bucket/exact.mp4"
    finally:
        AnyUri._registry.remove(DstUri)


def test_upload_appends_uuid_for_prefix_dst(clean_io_registry: None, tmp_path: pathlib.Path) -> None:
    src_path = str(tmp_path / "src.mp4")
    open(src_path, "w").close()
    src = FileUri(src_path)

    class DstUri(AnyUri):
        def __new__(cls, v: object) -> DstUri:
            return str.__new__(cls, str(v))

        @classmethod
        def validate(cls, v: object) -> DstUri:
            return cls(v)

    captured: dict[str, object] = {}

    @register_upload(DstUri)
    def _handler(s: FileUri, d: DstUri) -> DstUri:
        captured["dst"] = str(d)
        return d

    AnyUri._registry.insert(0, DstUri)
    try:
        dst = DstUri("dst://bucket/folder/")
        upload(src, dst)
        result_dst = str(captured["dst"])
        assert result_dst.startswith("dst://bucket/folder/")
        assert result_dst.endswith(".mp4")
        assert result_dst != "dst://bucket/folder/"
    finally:
        AnyUri._registry.remove(DstUri)


def test_upload_raises_for_unregistered_dst(clean_io_registry: None, tmp_path: pathlib.Path) -> None:
    src_path = str(tmp_path / "src.mp4")
    open(src_path, "w").close()
    src = FileUri(src_path)

    class NoHandlerUri(AnyUri):
        def __new__(cls, v: object) -> NoHandlerUri:
            return str.__new__(cls, str(v))

    with pytest.raises(UriSchemaError, match="No upload handler"):
        _dispatch_upload(src, NoHandlerUri("x://foo/bar.mp4"))


def test_public_api_importable() -> None:
    from anyuri.io import download, upload
    assert callable(download)
    assert callable(upload)


def test_all_providers_registered_after_import() -> None:
    import anyuri.io  # noqa: F401 — triggers handler registration
    from anyuri.io._registry import _download_registry, _upload_registry
    from anyuri.providers._gcs import GSUri
    from anyuri.providers._s3 import S3Uri
    from anyuri.providers._azure import AzureUri
    from anyuri.providers._r2 import R2Uri
    from anyuri.providers._b2 import B2Uri
    from anyuri import HttpUri, FileUri

    for uri_cls in [HttpUri, FileUri, GSUri, S3Uri, AzureUri, R2Uri, B2Uri]:
        assert uri_cls in _download_registry, f"No download handler for {uri_cls.__name__}"

    for uri_cls in [GSUri, S3Uri, AzureUri, R2Uri, B2Uri]:
        assert uri_cls in _upload_registry, f"No upload handler for {uri_cls.__name__}"
