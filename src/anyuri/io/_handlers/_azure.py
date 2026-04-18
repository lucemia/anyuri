from __future__ import annotations

from urllib.parse import urlparse

from anyuri import FileUri
from anyuri.providers._azure import AzureUri
from anyuri.io._registry import register_download, register_upload


@register_download(AzureUri)
def _azure_download(uri: AzureUri, target: FileUri) -> FileUri:
    try:
        from azure.storage.blob import BlobServiceClient  # type: ignore[import]
    except ImportError:
        raise ImportError("Install anyuri[azure] for Azure support: pip install anyuri[azure]")
    p = urlparse(uri.as_uri())  # abfs://container@account.dfs.core.windows.net/path
    account = (p.hostname or "").split(".")[0]
    container = p.username or ""
    blob_name = p.path.lstrip("/")
    client = BlobServiceClient(account_url=f"https://{account}.blob.core.windows.net")
    blob = client.get_blob_client(container=container, blob=blob_name)
    with open(str(target), "wb") as f:
        f.write(blob.download_blob().readall())
    return target


@register_upload(AzureUri)
def _azure_upload(src: FileUri, dst: AzureUri) -> AzureUri:
    try:
        from azure.storage.blob import BlobServiceClient  # type: ignore[import]
    except ImportError:
        raise ImportError("Install anyuri[azure] for Azure support: pip install anyuri[azure]")
    p = urlparse(dst.as_uri())  # abfs://container@account.dfs.core.windows.net/path
    account = (p.hostname or "").split(".")[0]
    container = p.username or ""
    blob_name = p.path.lstrip("/")
    client = BlobServiceClient(account_url=f"https://{account}.blob.core.windows.net")
    blob = client.get_blob_client(container=container, blob=blob_name)
    with open(str(src), "rb") as f:
        blob.upload_blob(f, overwrite=True)
    return dst


__all__ = ["_azure_download", "_azure_upload"]
