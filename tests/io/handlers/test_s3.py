import pathlib
import sys
from unittest.mock import MagicMock

import pytest

from anyuri import FileUri
from anyuri.providers._s3 import S3Uri
from anyuri.io._handlers._s3 import _s3_download, _s3_upload


def test_s3_download(tmp_path: pathlib.Path, mock_boto3: MagicMock) -> None:
    mock_s3 = mock_boto3.client.return_value

    uri = S3Uri("s3://my-bucket/path/video.mp4")
    target = FileUri(str(tmp_path / "video.mp4"))

    result = _s3_download(uri, target)

    mock_boto3.client.assert_called_once_with("s3")
    mock_s3.download_file.assert_called_once_with("my-bucket", "path/video.mp4", str(target))
    assert result == target


def test_s3_upload(tmp_path: pathlib.Path, mock_boto3: MagicMock) -> None:
    mock_s3 = mock_boto3.client.return_value

    src_path = str(tmp_path / "src.mp4")
    open(src_path, "w").close()
    src = FileUri(src_path)
    dst = S3Uri("s3://my-bucket/output/video.mp4")

    result = _s3_upload(src, dst)

    mock_boto3.client.assert_called_once_with("s3")
    mock_s3.upload_file.assert_called_once_with(str(src), "my-bucket", "output/video.mp4")
    assert result == dst


def test_s3_download_missing_sdk(tmp_path: pathlib.Path) -> None:
    original = sys.modules.pop("boto3", None)
    try:
        with pytest.raises(ImportError, match="anyuri\\[s3\\]"):
            uri = S3Uri("s3://bucket/file.mp4")
            target = FileUri(str(tmp_path / "file.mp4"))
            _s3_download(uri, target)
    finally:
        if original is not None:
            sys.modules["boto3"] = original
