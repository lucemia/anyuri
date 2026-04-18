import pytest

from anyuri import AnyUri
from anyuri._exceptions import UriSchemaError
from anyuri.providers._azure import AzureUri  # importing registers AzureUri


@pytest.mark.parametrize(
    "uri, expected_uri, expected_source",
    [
        (
            "abfs://container@myaccount.dfs.core.windows.net/path/file.txt",
            "abfs://container@myaccount.dfs.core.windows.net/path/file.txt",
            "https://myaccount.blob.core.windows.net/container/path/file.txt",
        ),
        (
            "https://myaccount.blob.core.windows.net/container/path/file.txt",
            "abfs://container@myaccount.dfs.core.windows.net/path/file.txt",
            "https://myaccount.blob.core.windows.net/container/path/file.txt",
        ),
        (
            "abfss://mycontainer@account.dfs.core.windows.net/dir/file.parquet",
            "abfs://mycontainer@account.dfs.core.windows.net/dir/file.parquet",
            "https://account.blob.core.windows.net/mycontainer/dir/file.parquet",
        ),
    ],
)
def test_azureuri(uri: str, expected_uri: str, expected_source: str) -> None:
    result = AnyUri(uri)
    assert isinstance(result, AzureUri)
    assert result.as_uri() == expected_uri
    assert result.as_source() == expected_source
    assert str(result) == expected_source


def test_azureuri_isinstance_anyuri() -> None:
    uri = AnyUri("abfs://container@account.dfs.core.windows.net/file.txt")
    assert isinstance(uri, AnyUri)
    assert isinstance(uri, AzureUri)


def test_azureuri_invalid_scheme() -> None:
    with pytest.raises(UriSchemaError):
        AzureUri("s3://bucket/key")


def test_azureuri_invalid_host() -> None:
    with pytest.raises(UriSchemaError):
        AzureUri("https://account.notazure.com/container/key")
