import os
from pathlib import Path

import pydantic
import pytest
from syrupy.assertion import SnapshotAssertion
from syrupy.extensions.json import JSONSnapshotExtension

from anyuri import AnyUri, FileUri, HttpUri
from tests.conftest import parse_obj_as


class Foo(pydantic.BaseModel):
    uri: AnyUri


@pytest.mark.parametrize(
    "uri",
    [
        # FileUri
        "/absolute.jpg",
        "/%e8.txt",
        "file:///1.jpg",
        "file:///test_converter_download%5Bstoryblock%5D/43b5f971a5c37b8cc008db83999d027d6d0b9b5c.mp4",
        "file://localhost/test_converter_download%5Bstoryblock%5D/43b5f971a5c37b8cc008db83999d027d6d0b9b5c.mp4",
        "file://localhost/1.jpg",
        "file://localhost/1.jpg?q=1",
        "file://localhost/1.jpg?q=1#fragment",
        # HttpUri
        "http://example.com/1.jpg",
        "http://example.com/1.jpg?q=1",
        "https://example.com/foo/../1.jpg",
        "https://example.com/foo/../../1.jpg",
        "https://example.com/foo/../1.jpg?q=1",
        "https://example.com/foo/../1.jpg?q=1#fragment",
        "https://example.com/foo/",
        "https://example.com/foo2",
        "https://test.com",
    ],
)
def test_anyuri(uri: str, snapshot: SnapshotAssertion) -> None:
    any_uri_init = AnyUri(uri)
    any_uri_parse = parse_obj_as(AnyUri, uri)
    foo = Foo(uri=uri)  # type: ignore[arg-type]

    assert type(any_uri_init) is type(any_uri_parse) is type(foo.uri), "type consistency"
    assert any_uri_init == any_uri_parse == foo.uri, "value consistency"
    assert isinstance(any_uri_init, AnyUri)

    assert snapshot(extension_class=JSONSnapshotExtension) == {
        "self": any_uri_init,
        "type": type(any_uri_init),
        "str": str(any_uri_init),
        "repr": repr(any_uri_init),
        "as_uri": any_uri_init.as_uri(),
        "as_source": any_uri_init.as_source(),
        "scheme": any_uri_init.scheme,
        "netloc": any_uri_init.netloc,
        "path": any_uri_init.path,
        "params": any_uri_init.params,
        "query": any_uri_init.query,
        "fragment": any_uri_init.fragment,
    }


def test_validate_success() -> None:
    assert isinstance(FileUri.validate("file:///1.jpg"), FileUri)
    assert isinstance(FileUri.validate("file://localhost/1.jpg"), FileUri)
    assert isinstance(HttpUri.validate("http://example.com/1.jpg"), HttpUri)


@pytest.mark.parametrize(
    "cls, uri",
    [
        (HttpUri, "xxx"),
        (HttpUri, "foo://123.jpg"),
        (FileUri, "foo://123.jpg"),
        (FileUri, "file://xxxx/1.jpg"),
        (AnyUri, "foo://123.jpg"),
    ],
)
def test_validate_failed(cls: type[AnyUri], uri: str) -> None:
    with pytest.raises(ValueError):
        cls.validate(uri)
    with pytest.raises(ValueError):
        cls(uri)


@pytest.mark.parametrize(
    "filename",
    [
        "foo.bar",
        "tmp/../foo.bar",
    ],
)
def test_relative_fileuri(filename: str, datadir: Path) -> None:
    p = datadir / filename
    file_uri = AnyUri(p)

    assert isinstance(file_uri, FileUri)
    from urllib.parse import urlparse
    parsed = urlparse(file_uri.as_uri())
    assert parsed.scheme == "file"
    assert parsed.netloc == "localhost"
    assert parsed.path.endswith(p.name)
    assert os.path.exists(file_uri.as_source())
    assert isinstance(file_uri, AnyUri)
