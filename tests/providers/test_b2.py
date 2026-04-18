import pytest

from anyuri import AnyUri
from anyuri._exceptions import UriSchemaError
from anyuri.providers._b2 import B2Uri  # importing registers B2Uri


@pytest.mark.parametrize(
    "uri, expected_uri, expected_source",
    [
        (
            "b2://mybucket/key.jpg",
            "b2://mybucket/key.jpg",
            "b2://mybucket/key.jpg",
        ),
        (
            "https://f003.backblazeb2.com/file/mybucket/key.jpg",
            "b2://mybucket/key.jpg",
            "b2://mybucket/key.jpg",
        ),
        (
            "b2://bucket/subdir/file.parquet",
            "b2://bucket/subdir/file.parquet",
            "b2://bucket/subdir/file.parquet",
        ),
    ],
)
def test_b2uri(uri: str, expected_uri: str, expected_source: str) -> None:
    result = AnyUri(uri)
    assert isinstance(result, B2Uri)
    assert result.as_uri() == expected_uri
    assert result.as_source() == expected_source
    assert str(result) == expected_source


def test_b2uri_isinstance_anyuri() -> None:
    uri = AnyUri("b2://bucket/key.jpg")
    assert isinstance(uri, AnyUri)
    assert isinstance(uri, B2Uri)


def test_b2uri_invalid_scheme() -> None:
    with pytest.raises(UriSchemaError):
        B2Uri("s3://bucket/key")


def test_b2uri_invalid_host() -> None:
    with pytest.raises(UriSchemaError):
        B2Uri("https://example.com/file/bucket/key")


def test_b2uri_invalid_https_path() -> None:
    with pytest.raises(UriSchemaError):
        B2Uri("https://f003.backblazeb2.com/notfile/bucket/key")
