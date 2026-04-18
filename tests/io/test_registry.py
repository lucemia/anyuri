# tests/io/test_registry.py
from anyuri._exceptions import DownloadError, UriSchemaError, UploadError


def test_download_error_is_exception() -> None:
    err = DownloadError("failed")
    assert isinstance(err, Exception)
    assert str(err) == "failed"


def test_upload_error_is_exception() -> None:
    err = UploadError("failed")
    assert isinstance(err, Exception)
    assert str(err) == "failed"
