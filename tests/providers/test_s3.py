import pytest

from anyuri import AnyUri
from anyuri._exceptions import UriSchemaError
from anyuri.providers._s3 import S3Uri  # importing registers S3Uri


@pytest.mark.parametrize(
    "uri, expected_uri, expected_source",
    [
        (
            "s3://mybucket/key.jpg",
            "s3://mybucket/key.jpg",
            "https://mybucket.s3.amazonaws.com/key.jpg",
        ),
        (
            "https://mybucket.s3.amazonaws.com/key.jpg",
            "s3://mybucket/key.jpg",
            "https://mybucket.s3.amazonaws.com/key.jpg",
        ),
        (
            "https://mybucket.s3.us-east-1.amazonaws.com/key.jpg",
            "s3://mybucket/key.jpg",
            "https://mybucket.s3.amazonaws.com/key.jpg",
        ),
        (
            "https://s3.amazonaws.com/mybucket/key.jpg",
            "s3://mybucket/key.jpg",
            "https://mybucket.s3.amazonaws.com/key.jpg",
        ),
        (
            "https://s3.us-west-2.amazonaws.com/mybucket/subdir/key.jpg",
            "s3://mybucket/subdir/key.jpg",
            "https://mybucket.s3.amazonaws.com/subdir/key.jpg",
        ),
        (
            "s3://mybucket/key.jpg?versionId=abc123",
            "s3://mybucket/key.jpg",
            "https://mybucket.s3.amazonaws.com/key.jpg?versionId=abc123",
        ),
    ],
)
def test_s3uri(uri: str, expected_uri: str, expected_source: str) -> None:
    result = AnyUri(uri)
    assert isinstance(result, S3Uri)
    assert result.as_uri() == expected_uri
    assert result.as_source() == expected_source
    assert str(result) == expected_source


def test_s3uri_isinstance_anyuri() -> None:
    uri = AnyUri("s3://bucket/key.jpg")
    assert isinstance(uri, AnyUri)
    assert isinstance(uri, S3Uri)


def test_s3uri_invalid_scheme() -> None:
    with pytest.raises(UriSchemaError):
        S3Uri("gs://bucket/key.jpg")


def test_s3uri_invalid_http_host() -> None:
    with pytest.raises(UriSchemaError):
        S3Uri("https://example.com/key.jpg")
