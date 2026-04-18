"""AzureUri — Azure Blob Storage URI type."""

from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

from anyuri import AnyUri
from anyuri._exceptions import UriSchemaError


class AzureUri(AnyUri):
    """URI for Azure Blob Storage resources.

    Accepts ``abfs://``, ``abfss://`` (ADLS Gen2), and HTTPS Blob Storage forms.
    Stores internally as HTTPS; ``as_uri()`` returns the ``abfs://`` canonical form.

    The ABFS format is: ``abfs://<container>@<account>.dfs.core.windows.net/<path>``

    Examples:
        >>> AzureUri("abfs://container@account.dfs.core.windows.net/file.txt")
        AzureUri("abfs://container@account.dfs.core.windows.net/file.txt")

        >>> AzureUri("https://account.blob.core.windows.net/container/file.txt")
        AzureUri("abfs://container@account.dfs.core.windows.net/file.txt")
    """

    def __new__(cls, value: Any) -> AzureUri:
        return str.__new__(cls, cls._validate(value))

    @classmethod
    def _validate(cls, value: Any) -> str:
        v = str(value)
        p = urlparse(v)

        if p.scheme in {"abfs", "abfss"}:
            # abfs://container@account.dfs.core.windows.net/path
            hostname = p.hostname or ""
            if not hostname.endswith(".dfs.core.windows.net"):
                raise UriSchemaError(f"Invalid host for AzureUri: {value!r}")
            account = hostname.split(".")[0]
            container = p.username
            if not container:
                raise UriSchemaError(f"Missing container in AzureUri: {value!r}")
            path = p.path  # /path/file
            return f"https://{account}.blob.core.windows.net/{container}{path}"

        if p.scheme in {"http", "https"}:
            hostname = p.hostname or ""
            if not hostname.endswith(".blob.core.windows.net"):
                raise UriSchemaError(f"Invalid host for AzureUri: {value!r}")
            return v

        raise UriSchemaError(f"Invalid AzureUri: {value!r}")

    @classmethod
    def validate(cls, value: Any) -> AzureUri:
        return cls(cls._validate(value))

    def as_uri(self) -> str:
        # https://account.blob.core.windows.net/container/path/file
        # → abfs://container@account.dfs.core.windows.net/path/file
        p = urlparse(str(self))
        account = (p.hostname or "").split(".")[0]
        # path: /container/rest/of/path
        path_parts = p.path.lstrip("/").split("/", 1)
        container = path_parts[0]
        remaining = f"/{path_parts[1]}" if len(path_parts) > 1 else "/"
        return f"abfs://{container}@{account}.dfs.core.windows.net{remaining}"


# Auto-register when this module is imported
AnyUri.register(AzureUri)

__all__ = ["AzureUri"]
