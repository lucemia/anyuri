# tests/io/handlers/test_gcs.py
import pathlib
import sys
from unittest.mock import MagicMock

import pytest

from anyuri import FileUri
from anyuri.providers._gcs import GSUri
from anyuri.io._handlers._gcs import _gcs_download, _gcs_upload


def _mock_gcs() -> MagicMock:
    mock_storage = MagicMock()
    mock_gc = MagicMock()
    mock_gc.storage = mock_storage
    sys.modules.setdefault("google", MagicMock())
    sys.modules["google.cloud"] = mock_gc
    sys.modules["google.cloud.storage"] = mock_storage
    return mock_storage


def test_gcs_download(tmp_path: pathlib.Path) -> None:
    mock_storage = _mock_gcs()
    mock_blob = mock_storage.Client.return_value.bucket.return_value.blob.return_value

    uri = GSUri("gs://my-bucket/path/video.mp4")
    target = FileUri(str(tmp_path / "video.mp4"))

    result = _gcs_download(uri, target)

    mock_storage.Client.assert_called_once()
    mock_storage.Client.return_value.bucket.assert_called_once_with("my-bucket")
    mock_storage.Client.return_value.bucket.return_value.blob.assert_called_once_with("path/video.mp4")
    mock_blob.download_to_filename.assert_called_once_with(str(target))
    assert result == target


def test_gcs_upload(tmp_path: pathlib.Path) -> None:
    mock_storage = _mock_gcs()
    mock_blob = mock_storage.Client.return_value.bucket.return_value.blob.return_value

    src_path = str(tmp_path / "src.mp4")
    open(src_path, "w").close()
    src = FileUri(src_path)
    dst = GSUri("gs://my-bucket/output/video.mp4")

    result = _gcs_upload(src, dst)

    mock_storage.Client.assert_called_once()
    mock_storage.Client.return_value.bucket.assert_called_once_with("my-bucket")
    mock_storage.Client.return_value.bucket.return_value.blob.assert_called_once_with("output/video.mp4")
    mock_blob.upload_from_filename.assert_called_once_with(str(src))
    assert result == dst


def test_gcs_download_missing_sdk(tmp_path: pathlib.Path) -> None:
    original = sys.modules.pop("google.cloud.storage", None)
    original_gc = sys.modules.pop("google.cloud", None)
    original_g = sys.modules.pop("google", None)
    try:
        with pytest.raises(ImportError, match="anyuri\\[gcs\\]"):
            uri = GSUri("gs://bucket/file.mp4")
            target = FileUri(str(tmp_path / "file.mp4"))
            _gcs_download(uri, target)
    finally:
        if original is not None:
            sys.modules["google.cloud.storage"] = original
        if original_gc is not None:
            sys.modules["google.cloud"] = original_gc
        if original_g is not None:
            sys.modules["google"] = original_g
