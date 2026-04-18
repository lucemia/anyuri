import pathlib
import sys
from unittest.mock import MagicMock

import pytest

from anyuri import FileUri
from anyuri.providers._azure import AzureUri
from anyuri.io._handlers._azure import _azure_download, _azure_upload


def _mock_azure() -> MagicMock:
    mock_blob_module = MagicMock()
    mock_azure = MagicMock()
    mock_azure_storage = MagicMock()
    mock_azure_storage.blob = mock_blob_module
    sys.modules["azure"] = mock_azure
    sys.modules["azure.storage"] = mock_azure_storage
    sys.modules["azure.storage.blob"] = mock_blob_module
    return mock_blob_module


def test_azure_download(tmp_path: pathlib.Path) -> None:
    mock_blob_module = _mock_azure()
    mock_client = mock_blob_module.BlobServiceClient.return_value
    mock_blob = mock_client.get_blob_client.return_value

    def _readinto(f: object) -> int:
        assert hasattr(f, "write")
        f.write(b"azure content")  # type: ignore[union-attr]
        return len(b"azure content")

    mock_blob.download_blob.return_value.readinto.side_effect = _readinto

    uri = AzureUri("abfs://container@account.dfs.core.windows.net/path/file.mp4")
    target = FileUri(str(tmp_path / "file.mp4"))

    result = _azure_download(uri, target)

    mock_blob_module.BlobServiceClient.assert_called_once_with(
        account_url="https://account.blob.core.windows.net"
    )
    mock_client.get_blob_client.assert_called_once_with(container="container", blob="path/file.mp4")
    mock_blob.download_blob.assert_called_once()
    assert result == target
    with open(str(target), "rb") as f:
        assert f.read() == b"azure content"


def test_azure_upload(tmp_path: pathlib.Path) -> None:
    mock_blob_module = _mock_azure()
    mock_client = mock_blob_module.BlobServiceClient.return_value
    mock_blob = mock_client.get_blob_client.return_value

    src_path = str(tmp_path / "src.mp4")
    with open(src_path, "wb") as f:
        f.write(b"content")
    src = FileUri(src_path)
    dst = AzureUri("abfs://container@account.dfs.core.windows.net/output/file.mp4")

    result = _azure_upload(src, dst)

    mock_blob_module.BlobServiceClient.assert_called_once_with(
        account_url="https://account.blob.core.windows.net"
    )
    mock_client.get_blob_client.assert_called_once_with(container="container", blob="output/file.mp4")
    mock_blob.upload_blob.assert_called_once()
    assert result == dst


def test_azure_download_missing_sdk(tmp_path: pathlib.Path) -> None:
    original = sys.modules.pop("azure.storage.blob", None)
    original_as = sys.modules.pop("azure.storage", None)
    original_a = sys.modules.pop("azure", None)
    try:
        with pytest.raises(ImportError, match="anyuri\\[azure\\]"):
            uri = AzureUri("abfs://c@a.dfs.core.windows.net/file.mp4")
            target = FileUri(str(tmp_path / "file.mp4"))
            _azure_download(uri, target)
    finally:
        for k, v in [("azure.storage.blob", original), ("azure.storage", original_as), ("azure", original_a)]:
            if v is not None:
                sys.modules[k] = v
