import pathlib
import sys
from unittest.mock import MagicMock

import pytest

from anyuri import FileUri
from anyuri.io._handlers._b2 import _b2_download, _b2_upload
from anyuri.providers._b2 import B2Uri


def _mock_b2sdk() -> MagicMock:
    mock_b2sdk = MagicMock()
    mock_b2sdk_v2 = MagicMock()
    mock_b2sdk.v2 = mock_b2sdk_v2
    sys.modules["b2sdk"] = mock_b2sdk
    sys.modules["b2sdk.v2"] = mock_b2sdk_v2
    return mock_b2sdk_v2


def test_b2_download(tmp_path: pathlib.Path) -> None:
    mock_b2 = _mock_b2sdk()
    mock_api = mock_b2.B2Api.return_value
    mock_bucket = mock_api.get_bucket_by_name.return_value
    mock_downloaded = mock_bucket.download_file_by_name.return_value

    uri = B2Uri("b2://mybucket/path/video.mp4")
    target = FileUri(str(tmp_path / "video.mp4"))

    result = _b2_download(uri, target)

    mock_b2.B2Api.assert_called_once()
    mock_api.get_bucket_by_name.assert_called_once_with("mybucket")
    mock_bucket.download_file_by_name.assert_called_once_with("path/video.mp4")
    mock_downloaded.save_to.assert_called_once_with(str(target))
    assert result == target


def test_b2_upload(tmp_path: pathlib.Path) -> None:
    mock_b2 = _mock_b2sdk()
    mock_api = mock_b2.B2Api.return_value
    mock_bucket = mock_api.get_bucket_by_name.return_value

    src_path = str(tmp_path / "src.mp4")
    open(src_path, "w").close()
    src = FileUri(src_path)
    dst = B2Uri("b2://mybucket/output/video.mp4")

    result = _b2_upload(src, dst)

    mock_api.get_bucket_by_name.assert_called_once_with("mybucket")
    mock_bucket.upload_local_file.assert_called_once_with(
        local_file=str(src), file_name="output/video.mp4"
    )
    assert result == dst


def test_b2_download_missing_sdk(tmp_path: pathlib.Path) -> None:
    original = sys.modules.pop("b2sdk", None)
    original_v2 = sys.modules.pop("b2sdk.v2", None)
    try:
        with pytest.raises(ImportError, match="anyuri\\[b2\\]"):
            uri = B2Uri("b2://bucket/file.mp4")
            target = FileUri(str(tmp_path / "file.mp4"))
            _b2_download(uri, target)
    finally:
        if original is not None:
            sys.modules["b2sdk"] = original
        if original_v2 is not None:
            sys.modules["b2sdk.v2"] = original_v2
