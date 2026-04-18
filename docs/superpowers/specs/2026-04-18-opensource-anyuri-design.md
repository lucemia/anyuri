# anyuri — Open-Source Package Design

**Date:** 2026-04-18
**Status:** Approved

## Overview

Extract `anyuri.py` from the private `genv-fs-core` package and publish it as a standalone, zero-mandatory-dependency Python package on PyPI under the name `anyuri`.

`anyuri` provides polymorphic URI types for Python. Constructing an `AnyUri` auto-dispatches to the correct subclass (`HttpUri`, `FileUri`, `GSUri`, `S3Uri`, etc.) based on the input string. It behaves exactly like a `str` and integrates with Pydantic v1 and v2.

## Package Structure

```
anyuri/
├── src/
│   └── anyuri/
│       ├── __init__.py          # AnyUri, HttpUri, FileUri + registry API
│       ├── _exceptions.py       # UriSchemaError
│       ├── _utils.py            # normalize_url, uri_to_path (stdlib only)
│       └── providers/
│           ├── __init__.py      # exports all provider classes
│           ├── _gcs.py          # GSUri
│           ├── _s3.py           # S3Uri
│           ├── _azure.py        # AzureUri
│           ├── _r2.py           # R2Uri (Cloudflare)
│           └── _b2.py           # B2Uri (Backblaze)
├── tests/
├── docs/
├── pyproject.toml
└── README.md
```

## Dependencies

**Mandatory:** none (stdlib only for core)

**Optional extras:**

```toml
[project.optional-dependencies]
gcs     = ["google-cloud-storage"]
s3      = ["boto3"]
azure   = ["azure-storage-blob"]
r2      = ["boto3"]
b2      = ["b2sdk"]
all     = ["google-cloud-storage", "boto3", "azure-storage-blob", "b2sdk"]
pydantic = ["pydantic"]
```

## Core API

```python
# Auto-dispatch construction
AnyUri("https://example.com/1.jpg")   # → HttpUri
AnyUri("gs://bucket/1.jpg")           # → GSUri
AnyUri("s3://bucket/key.jpg")         # → S3Uri
AnyUri("/local/path.jpg")             # → FileUri

# Key methods
uri.as_uri()     # canonical URI form:   "gs://bucket/1.jpg"
uri.as_source()  # tool-compatible form: "https://storage.googleapis.com/bucket/1.jpg"

# Properties
uri.scheme, uri.netloc, uri.path, uri.query, uri.fragment

# isinstance / issubclass checks work naturally
isinstance(AnyUri("gs://bucket/1.jpg"), GSUri)  # True
```

## Registry

Built-in cloud providers auto-register when their module is imported. Users register custom types via:

```python
# Explicit
AnyUri.register(MyCloudUri)

# Decorator
@AnyUri.register
class MyCloudUri(AnyUri):
    ...
```

`AnyUri.validate()` iterates the registry in order. `HttpUri` and `FileUri` are always registered last as fallbacks.

Cloud provider modules are imported by the user to activate them:

```python
from anyuri.providers import GSUri, S3Uri   # registers both
```

## Cloud Providers

| Provider | Native scheme | HTTPS equivalent accepted | `as_uri()` | `as_source()` |
|---|---|---|---|---|
| `GSUri` | `gs://bucket/key` | `storage.googleapis.com/bucket/key` | `gs://bucket/key` | `https://storage.googleapis.com/bucket/key` |
| `S3Uri` | `s3://bucket/key` | `<bucket>.s3.amazonaws.com/key` or `s3.amazonaws.com/<bucket>/key` | `s3://bucket/key` | `https://<bucket>.s3.amazonaws.com/key` |
| `AzureUri` | `abfs://<container>@<account>.dfs.core.windows.net/<path>` | `<account>.blob.core.windows.net/<container>/<path>` | `abfs://<container>@<account>.dfs.core.windows.net/<path>` | `https://<account>.blob.core.windows.net/<container>/<path>` |
| `R2Uri` | `r2://<account>/bucket/key` | `<account>.r2.cloudflarestorage.com/bucket/key` | `r2://<account>/bucket/key` | `https://<account>.r2.cloudflarestorage.com/bucket/key` |
| `B2Uri` | `b2://bucket/key` | `f<N>.backblazeb2.com/file/bucket/key` | `b2://bucket/key` | `https://f<N>.backblazeb2.com/file/bucket/key` |

Cloud SDK imports are lazy — no SDK is imported at module load time; SDKs are only needed for actual I/O (out of scope for this package).

## Pydantic Integration

Both v1 (`__get_validators__`) and v2 (`__get_pydantic_core_schema__`) are supported, gated behind `try/except ImportError`. Activated via `pip install anyuri[pydantic]`.

```python
from pydantic import BaseModel
from anyuri import AnyUri

class MyModel(BaseModel):
    uri: AnyUri

MyModel(uri="https://example.com/1.jpg")  # validated as HttpUri
```

## Testing

- Snapshot tests migrated from `genv-fs-core` for existing types
- New snapshot tests for `S3Uri`, `AzureUri`, `R2Uri`, `B2Uri`
- Tests for custom registration (explicit + decorator)
- Python 3.10, 3.11, 3.12, 3.13

## CI/CD (GitHub Actions)

- `test.yml` — pytest on all supported Python versions
- `lint.yml` — ruff + mypy
- `release.yml` — build and publish to PyPI via Trusted Publishing on tag push

## Versioning & Release

- Initial release: `0.1.0`
- Published to pypi.org as `anyuri`
- `genv-fs-core` to be updated in a follow-up to depend on `anyuri[gcs]` instead of the local `anyuri.py`
