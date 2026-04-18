import pytest

from anyuri import AnyUri
from anyuri._exceptions import UriSchemaError
from anyuri.providers._r2 import R2Uri  # importing registers R2Uri


@pytest.mark.parametrize(
    "uri, expected_uri, expected_source",
    [
        (
            "r2://accountid/mybucket/key.jpg",
            "r2://accountid/mybucket/key.jpg",
            "https://accountid.r2.cloudflarestorage.com/mybucket/key.jpg",
        ),
        (
            "https://accountid.r2.cloudflarestorage.com/mybucket/key.jpg",
            "r2://accountid/mybucket/key.jpg",
            "https://accountid.r2.cloudflarestorage.com/mybucket/key.jpg",
        ),
        (
            "r2://acc/bucket/dir/file.parquet",
            "r2://acc/bucket/dir/file.parquet",
            "https://acc.r2.cloudflarestorage.com/bucket/dir/file.parquet",
        ),
    ],
)
def test_r2uri(uri: str, expected_uri: str, expected_source: str) -> None:
    result = AnyUri(uri)
    assert isinstance(result, R2Uri)
    assert result.as_uri() == expected_uri
    assert result.as_source() == expected_source
    assert str(result) == expected_source


def test_r2uri_isinstance_anyuri() -> None:
    uri = AnyUri("r2://accountid/bucket/key.jpg")
    assert isinstance(uri, AnyUri)
    assert isinstance(uri, R2Uri)


def test_r2uri_invalid_scheme() -> None:
    with pytest.raises(UriSchemaError):
        R2Uri("s3://bucket/key")


def test_r2uri_invalid_host() -> None:
    with pytest.raises(UriSchemaError):
        R2Uri("https://account.notcloudflare.com/bucket/key")
