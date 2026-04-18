from __future__ import annotations

from anyuri import FileUri
from anyuri.providers._azure import AzureUri
from anyuri.io._registry import register_download, register_upload


@register_download(AzureUri)
def _azure_download(uri: AzureUri, target: FileUri) -> FileUri:
    try:
        from azure.storage.blob import BlobServiceClient  # type: ignore[import]
    except ImportError:
        raise ImportError("Install anyuri[azure] for Azure support: pip install anyuri[azure]")
    # _parsed is backed by as_uri() which is abfs://container@account.dfs.core.windows.net/path
    account = (uri._parsed.hostname or "").split(".")[0]
    container = uri._parsed.username or ""
    client = BlobServiceClient(account_url=f"https://{account}.blob.core.windows.net")
    blob = client.get_blob_client(container=container, blob=uri.path.lstrip("/"))
    with open(str(target), "wb") as f:
        blob.download_blob().readinto(f)
    return target


@register_upload(AzureUri)
def _azure_upload(src: FileUri, dst: AzureUri) -> AzureUri:
    try:
        from azure.storage.blob import BlobServiceClient  # type: ignore[import]
    except ImportError:
        raise ImportError("Install anyuri[azure] for Azure support: pip install anyuri[azure]")
    account = (dst._parsed.hostname or "").split(".")[0]
    container = dst._parsed.username or ""
    client = BlobServiceClient(account_url=f"https://{account}.blob.core.windows.net")
    blob = client.get_blob_client(container=container, blob=dst.path.lstrip("/"))
    with open(str(src), "rb") as f:
        blob.upload_blob(f, overwrite=True)
    return dst
