# tests/io/handlers/test_r2.py
import pathlib
import sys
from unittest.mock import MagicMock

import pytest

from anyuri import FileUri
from anyuri.providers._r2 import R2Uri
from anyuri.io._handlers._r2 import _r2_download, _r2_upload


def _mock_boto3() -> MagicMock:
    mock_boto3 = MagicMock()
    sys.modules["boto3"] = mock_boto3
    return mock_boto3


def test_r2_download(tmp_path: pathlib.Path) -> None:
    mock_boto3 = _mock_boto3()
    mock_s3 = mock_boto3.client.return_value

    uri = R2Uri("r2://accountid/bucket/path/video.mp4")
    target = FileUri(str(tmp_path / "video.mp4"))

    result = _r2_download(uri, target)

    mock_boto3.client.assert_called_once_with(
        "s3", endpoint_url="https://accountid.r2.cloudflarestorage.com"
    )
    mock_s3.download_file.assert_called_once_with("bucket", "path/video.mp4", str(target))
    assert result == target


def test_r2_upload(tmp_path: pathlib.Path) -> None:
    mock_boto3 = _mock_boto3()
    mock_s3 = mock_boto3.client.return_value

    src_path = str(tmp_path / "src.mp4")
    open(src_path, "w").close()
    src = FileUri(src_path)
    dst = R2Uri("r2://accountid/bucket/output/video.mp4")

    result = _r2_upload(src, dst)

    mock_boto3.client.assert_called_once_with(
        "s3", endpoint_url="https://accountid.r2.cloudflarestorage.com"
    )
    mock_s3.upload_file.assert_called_once_with(str(src), "bucket", "output/video.mp4")
    assert result == dst


def test_r2_download_missing_sdk(tmp_path: pathlib.Path) -> None:
    original = sys.modules.pop("boto3", None)
    try:
        with pytest.raises(ImportError, match="anyuri\\[r2\\]"):
            uri = R2Uri("r2://account/bucket/file.mp4")
            target = FileUri(str(tmp_path / "file.mp4"))
            _r2_download(uri, target)
    finally:
        if original is not None:
            sys.modules["boto3"] = original
