# anyuri

[![Tests](https://github.com/lucemia/anyuri/actions/workflows/test.yml/badge.svg)](https://github.com/lucemia/anyuri/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/lucemia/anyuri/branch/main/graph/badge.svg)](https://codecov.io/gh/lucemia/anyuri)
[![Docs](https://img.shields.io/badge/docs-lucemia.github.io%2Fanyuri-blue)](https://lucemia.github.io/anyuri/)

Polymorphic URI types for Python. `AnyUri` auto-dispatches to the right subclass based on the input string, works as a plain `str`, and integrates with Pydantic v1/v2.

## The Problem

Python data pipelines routinely handle assets from multiple backends — a thumbnail might live at `gs://bucket/img.jpg`, a report at `s3://bucket/report.pdf`, and a local fixture at `/tmp/test.png`. Without a shared abstraction, code degrades into scattered `if uri.startswith("gs://")` checks, duplicated normalization logic, and type annotations that lie (`str` accepts anything).

Cloud storage also has a dual-representation problem: the same GCS object is `gs://bucket/key` in SDK calls but `https://storage.googleapis.com/bucket/key` in HTTP clients and CDNs. Converting between them by hand is error-prone and leaks storage-specific logic everywhere.

`anyuri` solves both:

- **Polymorphic dispatch** — `AnyUri(value)` returns the right subtype for the scheme; your code branches on type, not string prefixes.
- **Dual representation** — `as_uri()` gives the canonical SDK form; `str(uri)` gives the HTTPS form accepted by any HTTP client. Conversion is automatic.
- **Zero friction** — every `AnyUri` subclass *is* a `str`, so it passes to any existing API without casting or adapters.

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

## Acknowledgements

This project would not exist without the support of my wife, Agnes, whose patience and encouragement make everything possible.

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
