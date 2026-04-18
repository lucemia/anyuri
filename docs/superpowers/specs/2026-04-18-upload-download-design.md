# Upload & Download Service for AnyUri

**Date:** 2026-04-18
**Status:** Approved

## Problem

AnyUri is a pure URI type system with no I/O. Users who need to download or upload files across multiple storage backends (GCS, S3, Azure, R2, B2, HTTP, local) must wire their own dispatch logic — the same scattered `startswith()` pattern that AnyUri eliminates for URI parsing.

The reference implementation (`genv-fs-core`) solves this for GCS only. This spec generalizes it to all providers.

## Goals

- `download(uri)` — fetch any URI to a local temp file, return `FileUri`
- `upload(src, dst)` — push any URI to a cloud destination, return typed URI
- All 5 cloud providers supported as both download sources and upload targets
- Sync only
- Core `anyuri` package stays zero-dependency and pure

## Non-Goals

- Async support
- Download caching or integrity verification (hashing)
- ACL / permissions management
- Streaming (no chunked transfers)
- A `transfer()` helper — `upload()` already handles remote `src` natively

## Module Structure

```
src/anyuri/
├── __init__.py          # unchanged
├── _exceptions.py       # add DownloadError, UploadError
├── providers/           # unchanged — pure URI parsing, no I/O
└── io/
    ├── __init__.py      # exports: download, upload
    ├── _registry.py     # register_download, register_upload decorators
    ├── _core.py         # download(), upload() dispatch + temp logic
    └── _handlers/
        ├── _http.py     # HttpUri → local (urllib)
        ├── _file.py     # FileUri → local (shutil.copy)
        ├── _gcs.py      # GSUri (google-cloud-storage)
        ├── _s3.py       # S3Uri (boto3)
        ├── _azure.py    # AzureUri (azure-storage-blob)
        ├── _r2.py       # R2Uri (boto3 with custom endpoint)
        └── _b2.py       # B2Uri (b2sdk)
```

`providers/` remains pure — all I/O lives in `io/`. The two packages share no imports.

## Public API

```python
from anyuri.io import download, upload

# Download any URI to a local temp file (extension preserved)
local: FileUri = download("gs://bucket/video.mp4")
local: FileUri = download("s3://bucket/video.mp4")
local: FileUri = download("https://example.com/video.mp4")
local: FileUri = download("/local/path/video.mp4")  # copies to temp

# Upload to cloud (dst is a prefix; filename is UUID-generated)
result: GSUri = upload("/local/video.mp4", "gs://bucket/videos/")
result: S3Uri = upload("/local/video.mp4", "s3://bucket/")

# Remote src is downloaded automatically before upload
result: GSUri = upload("https://example.com/img.jpg", "gs://bucket/")
result: S3Uri = upload("gs://src/video.mp4", "s3://dst/")  # cloud-to-cloud
```

### Signatures

```python
def download(uri: AnyUri | str) -> FileUri: ...
def upload(src: AnyUri | str, dst: AnyUri | str) -> AnyUri: ...
```

**`dst` path semantics:**
- If `dst` ends with `/`, it is treated as a prefix — the final filename is `<uuid><ext>` appended automatically (e.g. `gs://bucket/videos/` → `gs://bucket/videos/abc123.mp4`)
- If `dst` does not end with `/`, it is treated as an exact destination path (e.g. `gs://bucket/output.mp4` → `gs://bucket/output.mp4`)

The return type is the concrete URI type matching `dst` (e.g. `GSUri`, `S3Uri`).

## Registry Mechanism

```python
# anyuri/io/_registry.py
_download_registry: dict[type[AnyUri], Callable[[AnyUri, FileUri], FileUri]] = {}
_upload_registry:   dict[type[AnyUri], Callable[[FileUri, AnyUri], AnyUri]]  = {}

def register_download(uri_cls: type[AnyUri]):
    def decorator(fn):
        _download_registry[uri_cls] = fn
        return fn
    return decorator

def register_upload(uri_cls: type[AnyUri]):
    def decorator(fn):
        _upload_registry[uri_cls] = fn
        return fn
    return decorator
```

Each handler file self-registers via decorators on import. `anyuri/io/__init__.py` imports all handler modules to trigger registration — the same pattern as `anyuri/providers/__init__.py`.

Users who register custom URI types via `@AnyUri.register` can also register their own I/O handlers using the same decorators.

## Core Dispatch

```python
# anyuri/io/_core.py

def download(uri: AnyUri | str) -> FileUri:
    any_uri = AnyUri(uri)
    handler = _download_registry.get(type(any_uri))
    if handler is None:
        raise UriSchemaError(f"No download handler registered for {type(any_uri).__name__}")
    target = FileUri(tempfile.mktemp(suffix=_extract_ext(any_uri) or ".tmp"))
    return handler(any_uri, target)

def upload(src: AnyUri | str, dst: AnyUri | str) -> AnyUri:
    src_uri = AnyUri(src)
    dst_uri = AnyUri(dst)
    if not isinstance(src_uri, FileUri):
        src_uri = download(src_uri)
    # If dst is a prefix (ends with /), append UUID + preserved extension
    if str(dst_uri).endswith("/"):
        ext = _extract_ext(src_uri) or ".tmp"
        dst_uri = AnyUri(str(dst_uri) + uuid4().hex + ext)
    handler = _upload_registry.get(type(dst_uri))
    if handler is None:
        raise UriSchemaError(f"No upload handler registered for {type(dst_uri).__name__}")
    return handler(src_uri, dst_uri)
```

## Handler Contract

Each handler is a plain function registered via decorator:

```python
# Download handler signature
def _handler(uri: SpecificUri, target: FileUri) -> FileUri: ...

# Upload handler signature  
def _handler(src: FileUri, dst: SpecificUri) -> SpecificUri: ...
```

Handlers lazy-import their cloud SDK:

```python
@register_download(GSUri)
def _gcs_download(uri: GSUri, target: FileUri) -> FileUri:
    try:
        from google.cloud import storage
    except ImportError:
        raise ImportError("Install anyuri[gcs] for GCS support")
    client = storage.Client()
    bucket = client.bucket(uri_bucket(uri))
    bucket.blob(uri_key(uri)).download_to_filename(str(target))
    return target

@register_upload(GSUri)
def _gcs_upload(src: FileUri, dst: GSUri) -> GSUri:
    try:
        from google.cloud import storage
    except ImportError:
        raise ImportError("Install anyuri[gcs] for GCS support")
    client = storage.Client()
    bucket = client.bucket(uri_bucket(dst))
    bucket.blob(uri_key(dst)).upload_from_filename(str(src))
    return dst
```

`_http.py` and `_file.py` use stdlib only (no lazy import needed).

## Temp File Management

`tempfile.mktemp()` — stdlib, no extra abstraction. The caller owns the temp file after `download()` returns; cleanup is the caller's responsibility. Users needing scoped cleanup use standard `tempfile.NamedTemporaryFile` or `contextlib.ExitStack`.

Extension is extracted from the source URI path and preserved on the temp file (e.g. `video.mp4` → `/tmp/abc123.mp4`). Falls back to `.tmp` if no extension is found.

## Error Handling

Two new exceptions added to `anyuri/_exceptions.py`:

```python
class DownloadError(Exception): ...
class UploadError(Exception): ...
```

- `UriSchemaError` — raised by `download`/`upload` when no handler is registered for the URI type (already exists)
- `DownloadError` — raised by handlers on SDK/network failure during download
- `UploadError` — raised by handlers on SDK failure during upload
- `ImportError` — raised by handlers when the required cloud SDK is not installed

## Dependencies

No new optional extras are needed. The `io` handlers reuse the existing cloud SDK extras (`gcs`, `s3`, `azure`, `r2`, `b2`). Lazy imports inside handlers mean importing `anyuri.io` is always safe — errors surface only when a handler is invoked without its SDK installed.

## Data Flow

```
download("gs://bucket/video.mp4")
    → AnyUri() → GSUri
    → lookup _download_registry[GSUri]
    → mktemp("/tmp/uuid.mp4")
    → _gcs_download(uri, target)
        → google.cloud.storage client
        → blob.download_to_filename(target)
    → return FileUri("/tmp/uuid.mp4")

upload("/local/video.mp4", "s3://bucket/videos/")
    → AnyUri(src) → FileUri  (already local, skip download)
    → AnyUri(dst) → S3Uri
    → dst = S3Uri("s3://bucket/videos/<uuid>.mp4")  (append generated filename)
    → lookup _upload_registry[S3Uri]
    → _s3_upload(src, dst)
        → boto3 client
        → s3.upload_file(src, bucket, key)
    → return S3Uri("s3://bucket/videos/<uuid>.mp4")
```

## Testing Strategy

- Unit tests per handler using mock SDK clients
- Integration markers (`@pytest.mark.integration`) for real cloud tests, skipped in CI unless credentials present
- Parametrized tests across all providers where logic is symmetric
- Snapshot tests for URI construction in upload destination path
