# anyuri

Polymorphic URI types for Python. `AnyUri` auto-dispatches to the right subclass based on the input string, works as a plain `str`, and integrates with Pydantic v1/v2.

```python
from anyuri import AnyUri
from anyuri.providers import GSUri, S3Uri  # registers cloud providers

AnyUri("https://example.com/1.jpg")    # → HttpUri
AnyUri("gs://bucket/key.jpg")          # → GSUri
AnyUri("s3://bucket/key.jpg")          # → S3Uri
AnyUri("/local/path.jpg")              # → FileUri

uri = AnyUri("gs://bucket/key.jpg")
uri.as_uri()     # "gs://bucket/key.jpg"
uri.as_source()  # "https://storage.googleapis.com/bucket/key.jpg"
str(uri)         # "https://storage.googleapis.com/bucket/key.jpg"
uri == "https://storage.googleapis.com/bucket/key.jpg"  # True
```

## Installation

```bash
pip install anyuri                  # core only (HttpUri, FileUri)
pip install anyuri[gcs]             # + GSUri
pip install anyuri[s3]              # + S3Uri
pip install anyuri[azure]           # + AzureUri
pip install anyuri[all]             # all cloud providers
pip install anyuri[all,pydantic]    # + Pydantic integration
```

## Supported URI Types

| Class | Schemes accepted | as_uri() | as_source() |
|---|---|---|---|
| `HttpUri` | `http://`, `https://` | original URL | original URL |
| `FileUri` | `/path`, `file:///path` | `file://localhost/path` | `/path` |
| `GSUri` | `gs://`, `https://storage.googleapis.com/` | `gs://bucket/key` | `https://storage.googleapis.com/bucket/key` |
| `S3Uri` | `s3://`, virtual-hosted/path-style HTTPS | `s3://bucket/key` | `https://bucket.s3.amazonaws.com/key` |
| `AzureUri` | `abfs://`, `abfss://`, `https://*.blob.core.windows.net/` | `abfs://container@account.dfs.core.windows.net/path` | `https://account.blob.core.windows.net/container/path` |
| `R2Uri` | `r2://`, `https://*.r2.cloudflarestorage.com/` | `r2://account/bucket/key` | `https://account.r2.cloudflarestorage.com/bucket/key` |
| `B2Uri` | `b2://`, `https://f*.backblazeb2.com/file/` | `b2://bucket/key` | `b2://bucket/key` |

## Custom URI Types

```python
from anyuri import AnyUri
from anyuri._exceptions import UriSchemaError

@AnyUri.register
class SFTPUri(AnyUri):
    def __new__(cls, value):
        return str.__new__(cls, cls._validate(value))

    @classmethod
    def _validate(cls, value):
        v = str(value)
        if not v.startswith("sftp://"):
            raise UriSchemaError(f"Not an SFTP URI: {v!r}")
        return v

    @classmethod
    def validate(cls, value):
        return cls(cls._validate(value))

AnyUri("sftp://host/path")  # → SFTPUri
```

## Pydantic Integration

```python
from pydantic import BaseModel
from anyuri import AnyUri
from anyuri.providers import GSUri

class Asset(BaseModel):
    uri: AnyUri

Asset(uri="gs://bucket/key.jpg").uri  # GSUri instance
Asset(uri="https://example.com").uri  # HttpUri instance
```
