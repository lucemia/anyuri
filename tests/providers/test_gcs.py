import pytest
from anyuri import AnyUri
from anyuri._exceptions import UriSchemaError
from anyuri.providers._gcs import GSUri  # importing registers GSUri


@pytest.mark.parametrize(
    "uri, expected_uri, expected_source",
    [
        (
            "gs://bucket/1.jpg",
            "gs://bucket/1.jpg",
            "https://storage.googleapis.com/bucket/1.jpg",
        ),
        (
            "https://storage.googleapis.com/bucket/1.jpg",
            "gs://bucket/1.jpg",
            "https://storage.googleapis.com/bucket/1.jpg",
        ),
        (
            "gs://bucket/path/to/file.mp4",
            "gs://bucket/path/to/file.mp4",
            "https://storage.googleapis.com/bucket/path/to/file.mp4",
        ),
        (
            "gs://bucket/1.jpg?q=2",
            "gs://bucket/1.jpg?q=2",
            "https://storage.googleapis.com/bucket/1.jpg?q=2",
        ),
        (
            "https://storage.googleapis.com/bucket/file.html?q=1#frag",
            "gs://bucket/file.html?q=1#frag",
            "https://storage.googleapis.com/bucket/file.html?q=1#frag",
        ),
    ],
)
def test_gsuri(uri: str, expected_uri: str, expected_source: str) -> None:
    result = AnyUri(uri)
    assert isinstance(result, GSUri)
    assert result.as_uri() == expected_uri
    assert result.as_source() == expected_source
    assert str(result) == expected_source


def test_gsuri_isinstance_anyuri() -> None:
    uri = AnyUri("gs://bucket/1.jpg")
    assert isinstance(uri, AnyUri)
    assert isinstance(uri, GSUri)


def test_gsuri_invalid_netloc() -> None:
    with pytest.raises(UriSchemaError):
        GSUri("https://example.com/1.jpg")


def test_gsuri_invalid_scheme() -> None:
    with pytest.raises(UriSchemaError):
        GSUri("foo://bucket/1.jpg")
