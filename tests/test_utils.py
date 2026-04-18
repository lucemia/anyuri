import pytest
from anyuri._exceptions import UriSchemaError
from anyuri._utils import normalize_url, uri_to_path


def test_uri_schema_error_is_value_error() -> None:
    with pytest.raises(ValueError):
        raise UriSchemaError("bad uri")


def test_normalize_url_resolves_dotdot() -> None:
    assert normalize_url("https://example.com/foo/../bar.jpg") == "https://example.com/bar.jpg"


def test_normalize_url_resolves_multiple_dotdot() -> None:
    assert normalize_url("https://example.com/a/b/../../c.jpg") == "https://example.com/c.jpg"


def test_normalize_url_preserves_query_and_fragment() -> None:
    result = normalize_url("https://example.com/foo/../bar.jpg?q=1#sec")
    assert result == "https://example.com/bar.jpg?q=1#sec"


def test_normalize_url_no_op_for_clean_url() -> None:
    assert normalize_url("https://example.com/path/file.jpg") == "https://example.com/path/file.jpg"


def test_uri_to_path_converts_file_uri() -> None:
    assert uri_to_path("file:///tmp/test.jpg") == "/tmp/test.jpg"


def test_uri_to_path_with_localhost() -> None:
    assert uri_to_path("file://localhost/tmp/test.jpg") == "/tmp/test.jpg"


def test_uri_to_path_decodes_percent_encoding() -> None:
    result = uri_to_path("file:///tmp/my%20file.jpg")
    assert result == "/tmp/my file.jpg"


def test_uri_to_path_rejects_non_file_scheme() -> None:
    with pytest.raises(ValueError):
        uri_to_path("https://example.com/file.jpg")
