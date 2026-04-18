# Upload & Download Service Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `anyuri.io` subpackage with `download(uri) -> FileUri` and `upload(src, dst) -> AnyUri` functions backed by a handler registry, supporting all 5 cloud providers plus HTTP and local files.

**Architecture:** A handler registry (`_registry.py`) maps URI types to download/upload functions. Core dispatch (`_core.py`) resolves URI type, creates temp file, and invokes the registered handler. Each provider's handler file self-registers via decorator on import; `anyuri/io/__init__.py` imports all handlers to trigger registration.

**Tech Stack:** Python stdlib (`tempfile`, `shutil`, `urllib.request`, `uuid`, `re`); cloud SDKs lazy-imported per handler (`google-cloud-storage`, `boto3`, `azure-storage-blob`, `b2sdk`).

---

## File Map

| Action | Path | Responsibility |
|--------|------|----------------|
| Modify | `src/anyuri/_exceptions.py` | Add `DownloadError`, `UploadError` |
| Create | `src/anyuri/io/__init__.py` | Public API: `download`, `upload`; imports all handlers |
| Create | `src/anyuri/io/_registry.py` | Registry dicts + `register_download`/`register_upload` decorators |
| Create | `src/anyuri/io/_core.py` | `download()`, `upload()`, `_extract_ext()` |
| Create | `src/anyuri/io/_handlers/__init__.py` | Empty |
| Create | `src/anyuri/io/_handlers/_http.py` | `HttpUri` download via `urllib.request` |
| Create | `src/anyuri/io/_handlers/_file.py` | `FileUri` download via `shutil.copy` |
| Create | `src/anyuri/io/_handlers/_gcs.py` | `GSUri` download + upload via `google-cloud-storage` |
| Create | `src/anyuri/io/_handlers/_s3.py` | `S3Uri` download + upload via `boto3` |
| Create | `src/anyuri/io/_handlers/_azure.py` | `AzureUri` download + upload via `azure-storage-blob` |
| Create | `src/anyuri/io/_handlers/_r2.py` | `R2Uri` download + upload via `boto3` + custom endpoint |
| Create | `src/anyuri/io/_handlers/_b2.py` | `B2Uri` download + upload via `b2sdk` |
| Create | `tests/io/__init__.py` | Empty |
| Create | `tests/io/conftest.py` | `clean_io_registry` fixture |
| Create | `tests/io/test_registry.py` | Registry register/dispatch tests |
| Create | `tests/io/test_core.py` | `download()`/`upload()` dispatch + prefix logic tests |
| Create | `tests/io/handlers/__init__.py` | Empty |
| Create | `tests/io/handlers/test_http.py` | HTTP handler tests |
| Create | `tests/io/handlers/test_file.py` | FileUri handler tests |
| Create | `tests/io/handlers/test_gcs.py` | GCS handler tests (mocked SDK) |
| Create | `tests/io/handlers/test_s3.py` | S3 handler tests (mocked SDK) |
| Create | `tests/io/handlers/test_azure.py` | Azure handler tests (mocked SDK) |
| Create | `tests/io/handlers/test_r2.py` | R2 handler tests (mocked SDK) |
| Create | `tests/io/handlers/test_b2.py` | B2 handler tests (mocked SDK) |

---

## Task 1: Add DownloadError and UploadError

**Files:**
- Modify: `src/anyuri/_exceptions.py`
- Test: `tests/io/test_exceptions.py` (inline in test_registry.py)

- [ ] **Step 1: Write the failing test**

Create `tests/io/__init__.py` (empty) and `tests/io/handlers/__init__.py` (empty) first:

```bash
touch tests/io/__init__.py tests/io/handlers/__init__.py
```

Then write the test inline in `tests/io/test_registry.py` (create the file):

```python
# tests/io/test_registry.py
from anyuri._exceptions import DownloadError, UriSchemaError, UploadError


def test_download_error_is_exception() -> None:
    err = DownloadError("failed")
    assert isinstance(err, Exception)
    assert str(err) == "failed"


def test_upload_error_is_exception() -> None:
    err = UploadError("failed")
    assert isinstance(err, Exception)
    assert str(err) == "failed"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /Users/davidchen/repo/anyuri && python -m pytest tests/io/test_registry.py -v
```

Expected: `ImportError: cannot import name 'DownloadError'`

- [ ] **Step 3: Add exceptions**

Replace the full content of `src/anyuri/_exceptions.py`:

```python
class UriSchemaError(ValueError):
    """Raised when a URI cannot be validated by any registered URI type."""


class DownloadError(Exception):
    """Raised when a download operation fails."""


class UploadError(Exception):
    """Raised when an upload operation fails."""


__all__ = ["UriSchemaError", "DownloadError", "UploadError"]
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd /Users/davidchen/repo/anyuri && python -m pytest tests/io/test_registry.py::test_download_error_is_exception tests/io/test_registry.py::test_upload_error_is_exception -v
```

Expected: 2 passed

- [ ] **Step 5: Commit**

```bash
git add src/anyuri/_exceptions.py tests/io/__init__.py tests/io/handlers/__init__.py tests/io/test_registry.py
git commit -m "feat(io): add DownloadError and UploadError exceptions"
```

---

## Task 2: Registry Module

**Files:**
- Create: `src/anyuri/io/__init__.py` (stub)
- Create: `src/anyuri/io/_registry.py`
- Test: `tests/io/test_registry.py` (append)

- [ ] **Step 1: Write the failing tests**

Create `src/anyuri/io/__init__.py` as an empty stub:

```python
# src/anyuri/io/__init__.py
```

Create `tests/io/conftest.py`:

```python
# tests/io/conftest.py
import pytest
from anyuri.io._registry import _download_registry, _upload_registry


@pytest.fixture
def clean_io_registry():
    """Restore I/O registries after each test."""
    orig_down = dict(_download_registry)
    orig_up = dict(_upload_registry)
    yield
    _download_registry.clear()
    _download_registry.update(orig_down)
    _upload_registry.clear()
    _upload_registry.update(orig_up)
```

Append to `tests/io/test_registry.py`:

```python
from anyuri import AnyUri, FileUri
from anyuri._exceptions import UriSchemaError
from anyuri.io._registry import (
    _download_registry,
    _upload_registry,
    register_download,
    register_upload,
)


def test_register_download_adds_to_registry(clean_io_registry: None) -> None:
    class DummyUri(AnyUri):
        pass

    @register_download(DummyUri)
    def _handler(uri: DummyUri, target: FileUri) -> FileUri:
        return target

    assert _download_registry[DummyUri] is _handler


def test_register_upload_adds_to_registry(clean_io_registry: None) -> None:
    class DummyUri(AnyUri):
        pass

    @register_upload(DummyUri)
    def _handler(src: FileUri, dst: DummyUri) -> DummyUri:
        return dst

    assert _upload_registry[DummyUri] is _handler


def test_register_download_returns_function(clean_io_registry: None) -> None:
    class DummyUri(AnyUri):
        pass

    def _handler(uri: DummyUri, target: FileUri) -> FileUri:
        return target

    result = register_download(DummyUri)(_handler)
    assert result is _handler


def test_register_upload_returns_function(clean_io_registry: None) -> None:
    class DummyUri(AnyUri):
        pass

    def _handler(src: FileUri, dst: DummyUri) -> DummyUri:
        return dst

    result = register_upload(DummyUri)(_handler)
    assert result is _handler
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /Users/davidchen/repo/anyuri && python -m pytest tests/io/test_registry.py -v -k "register"
```

Expected: `ModuleNotFoundError: No module named 'anyuri.io._registry'`

- [ ] **Step 3: Create the registry module**

Create `src/anyuri/io/_registry.py`:

```python
from __future__ import annotations

from collections.abc import Callable
from typing import Any

from anyuri import AnyUri, FileUri

_download_registry: dict[type[AnyUri], Callable[[Any, FileUri], FileUri]] = {}
_upload_registry: dict[type[AnyUri], Callable[[FileUri, Any], AnyUri]] = {}


def register_download(uri_cls: type[AnyUri]) -> Callable[[Callable[[Any, FileUri], FileUri]], Callable[[Any, FileUri], FileUri]]:
    def decorator(fn: Callable[[Any, FileUri], FileUri]) -> Callable[[Any, FileUri], FileUri]:
        _download_registry[uri_cls] = fn
        return fn

    return decorator


def register_upload(uri_cls: type[AnyUri]) -> Callable[[Callable[[FileUri, Any], AnyUri]], Callable[[FileUri, Any], AnyUri]]:
    def decorator(fn: Callable[[FileUri, Any], AnyUri]) -> Callable[[FileUri, Any], AnyUri]:
        _upload_registry[uri_cls] = fn
        return fn

    return decorator


__all__ = ["register_download", "register_upload", "_download_registry", "_upload_registry"]
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd /Users/davidchen/repo/anyuri && python -m pytest tests/io/test_registry.py -v
```

Expected: all 6 tests pass

- [ ] **Step 5: Commit**

```bash
git add src/anyuri/io/__init__.py src/anyuri/io/_registry.py tests/io/conftest.py tests/io/test_registry.py
git commit -m "feat(io): add handler registry with register_download/register_upload"
```

---

## Task 3: Core Dispatch Module

**Files:**
- Create: `src/anyuri/io/_core.py`
- Test: `tests/io/test_core.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/io/test_core.py`:

```python
# tests/io/test_core.py
from __future__ import annotations

import tempfile
from unittest.mock import MagicMock

import pytest

from anyuri import AnyUri, FileUri, HttpUri
from anyuri._exceptions import UriSchemaError
from anyuri.io._core import _extract_ext, download, upload
from anyuri.io._registry import register_download, register_upload


@pytest.mark.parametrize(
    "uri_str, expected_ext",
    [
        ("https://example.com/video.mp4", ".mp4"),
        ("https://example.com/archive.tar.gz", ".gz"),
        ("/tmp/file.jpg", ".jpg"),
        ("https://example.com/no-ext", None),
        ("https://example.com/", None),
        ("https://example.com/toolong.abcdefghijk", None),  # >10 chars
    ],
)
def test_extract_ext(uri_str: str, expected_ext: str | None) -> None:
    uri = AnyUri(uri_str)
    assert _extract_ext(uri) == expected_ext


def test_download_calls_handler_with_uri_and_target(clean_io_registry: None) -> None:
    class FooUri(AnyUri):
        def __new__(cls, v: object) -> FooUri:
            return str.__new__(cls, str(v))

        @classmethod
        def validate(cls, v: object) -> FooUri:
            return cls(v)

    AnyUri._registry.insert(0, FooUri)

    captured: dict[str, object] = {}

    @register_download(FooUri)
    def _handler(uri: FooUri, target: FileUri) -> FileUri:
        captured["uri"] = uri
        captured["target"] = target
        return target

    try:
        result = download(FooUri("foo://test/video.mp4"))
        assert isinstance(result, FileUri)
        assert captured["uri"] == "foo://test/video.mp4"
        assert str(result).endswith(".mp4")
    finally:
        AnyUri._registry.remove(FooUri)


def test_download_raises_for_unregistered_uri(clean_io_registry: None) -> None:
    class UnknownUri(AnyUri):
        def __new__(cls, v: object) -> UnknownUri:
            return str.__new__(cls, str(v))

    with pytest.raises(UriSchemaError, match="No download handler"):
        from anyuri.io._core import _dispatch_download
        _dispatch_download(UnknownUri("x://foo"))


def test_upload_uses_exact_dst_path(clean_io_registry: None, tmp_path: pathlib.Path) -> None:
    import os
    src_path = str(tmp_path / "src.mp4")
    open(src_path, "w").close()
    src = FileUri(src_path)

    class DstUri(AnyUri):
        def __new__(cls, v: object) -> DstUri:
            return str.__new__(cls, str(v))

        @classmethod
        def validate(cls, v: object) -> DstUri:
            return cls(v)

    captured: dict[str, object] = {}

    @register_upload(DstUri)
    def _handler(s: FileUri, d: DstUri) -> DstUri:
        captured["dst"] = str(d)
        return d

    AnyUri._registry.insert(0, DstUri)
    try:
        dst = DstUri("dst://bucket/exact.mp4")
        upload(src, dst)
        assert captured["dst"] == "dst://bucket/exact.mp4"
    finally:
        AnyUri._registry.remove(DstUri)


def test_upload_appends_uuid_for_prefix_dst(clean_io_registry: None, tmp_path: pathlib.Path) -> None:
    src_path = str(tmp_path / "src.mp4")
    open(src_path, "w").close()
    src = FileUri(src_path)

    class DstUri(AnyUri):
        def __new__(cls, v: object) -> DstUri:
            return str.__new__(cls, str(v))

        @classmethod
        def validate(cls, v: object) -> DstUri:
            return cls(v)

    captured: dict[str, object] = {}

    @register_upload(DstUri)
    def _handler(s: FileUri, d: DstUri) -> DstUri:
        captured["dst"] = str(d)
        return d

    AnyUri._registry.insert(0, DstUri)
    try:
        dst = DstUri("dst://bucket/folder/")
        upload(src, dst)
        result_dst = str(captured["dst"])
        assert result_dst.startswith("dst://bucket/folder/")
        assert result_dst.endswith(".mp4")
        assert result_dst != "dst://bucket/folder/"
    finally:
        AnyUri._registry.remove(DstUri)


def test_upload_raises_for_unregistered_dst(clean_io_registry: None, tmp_path: pathlib.Path) -> None:
    src_path = str(tmp_path / "src.mp4")
    open(src_path, "w").close()
    src = FileUri(src_path)

    class NoHandlerUri(AnyUri):
        def __new__(cls, v: object) -> NoHandlerUri:
            return str.__new__(cls, str(v))

    with pytest.raises(UriSchemaError, match="No upload handler"):
        from anyuri.io._core import _dispatch_upload
        _dispatch_upload(src, NoHandlerUri("x://foo/bar.mp4"))
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /Users/davidchen/repo/anyuri && python -m pytest tests/io/test_core.py -v
```

Expected: `ModuleNotFoundError: No module named 'anyuri.io._core'`

- [ ] **Step 3: Create the core module**

Create `src/anyuri/io/_core.py`:

```python
from __future__ import annotations

import os
import re
import tempfile
from uuid import uuid4

from anyuri import AnyUri, FileUri
from anyuri._exceptions import UriSchemaError
from anyuri.io._registry import _download_registry, _upload_registry


def _extract_ext(uri: AnyUri) -> str | None:
    from urllib.parse import urlparse
    path = urlparse(str(uri)).path
    name = path.rstrip("/").rsplit("/", 1)[-1]
    m = re.search(r"\.[A-Za-z0-9]{1,10}$", name)
    return m.group(0) if m else None


def _dispatch_download(uri: AnyUri) -> FileUri:
    handler = _download_registry.get(type(uri))
    if handler is None:
        raise UriSchemaError(f"No download handler registered for {type(uri).__name__}")
    fd, path = tempfile.mkstemp(suffix=_extract_ext(uri) or ".tmp")
    os.close(fd)
    target = FileUri(path)
    return handler(uri, target)


def _dispatch_upload(src: FileUri, dst: AnyUri) -> AnyUri:
    handler = _upload_registry.get(type(dst))
    if handler is None:
        raise UriSchemaError(f"No upload handler registered for {type(dst).__name__}")
    return handler(src, dst)


def download(uri: AnyUri | str) -> FileUri:
    return _dispatch_download(AnyUri(uri))


def upload(src: AnyUri | str, dst: AnyUri | str) -> AnyUri:
    src_uri = AnyUri(src)
    dst_uri = AnyUri(dst)
    if not isinstance(src_uri, FileUri):
        src_uri = download(src_uri)
    if str(dst_uri).endswith("/"):
        ext = _extract_ext(src_uri) or ".tmp"
        dst_uri = AnyUri(str(dst_uri) + uuid4().hex + ext)
    return _dispatch_upload(src_uri, dst_uri)


__all__ = ["download", "upload"]
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd /Users/davidchen/repo/anyuri && python -m pytest tests/io/test_core.py -v
```

Expected: all tests pass

- [ ] **Step 5: Commit**

```bash
git add src/anyuri/io/_core.py tests/io/test_core.py
git commit -m "feat(io): add core download/upload dispatch with _extract_ext"
```

---

## Task 4: HTTP and FileUri Handlers

**Files:**
- Create: `src/anyuri/io/_handlers/__init__.py`
- Create: `src/anyuri/io/_handlers/_http.py`
- Create: `src/anyuri/io/_handlers/_file.py`
- Test: `tests/io/handlers/test_http.py`, `tests/io/handlers/test_file.py`

- [ ] **Step 1: Write the failing tests**

Create `src/anyuri/io/_handlers/__init__.py` (empty):

```python
```

Create `tests/io/handlers/test_http.py`:

```python
# tests/io/handlers/test_http.py
from unittest.mock import MagicMock, patch

from anyuri import FileUri, HttpUri
from anyuri.io._handlers._http import _http_download


def test_http_download_calls_urlopen(tmp_path: pathlib.Path) -> None:
    uri = HttpUri("https://example.com/video.mp4")
    target = FileUri(str(tmp_path / "video.mp4")

    mock_response = MagicMock()
    mock_response.__enter__ = lambda s: s
    mock_response.__exit__ = MagicMock(return_value=False)
    mock_response.read.return_value = b"video content"

    with patch("anyuri.io._handlers._http.urlopen", return_value=mock_response):
        result = _http_download(uri, target)

    assert result == target
    with open(str(target), "rb") as f:
        assert f.read() == b"video content"


def test_http_download_sets_user_agent(tmp_path: pathlib.Path) -> None:
    uri = HttpUri("https://example.com/img.jpg")
    target = FileUri(str(tmp_path / "img.jpg")

    mock_response = MagicMock()
    mock_response.__enter__ = lambda s: s
    mock_response.__exit__ = MagicMock(return_value=False)
    mock_response.read.return_value = b""

    with patch("anyuri.io._handlers._http.urlopen") as mock_urlopen:
        mock_urlopen.return_value = mock_response
        _http_download(uri, target)
        call_args = mock_urlopen.call_args[0][0]
        assert call_args.get_header("User-agent") == "Mozilla/5.0"
```

Create `tests/io/handlers/test_file.py`:

```python
# tests/io/handlers/test_file.py
from anyuri import FileUri
from anyuri.io._handlers._file import _file_download


def test_file_download_copies_file(tmp_path: pathlib.Path) -> None:
    src_path = str(tmp_path / "src.txt")
    dst_path = str(tmp_path / "dst.txt")
    with open(src_path, "w") as f:
        f.write("hello world")

    src = FileUri(src_path)
    target = FileUri(dst_path)

    result = _file_download(src, target)

    assert result == target
    with open(dst_path) as f:
        assert f.read() == "hello world"


def test_file_download_returns_target(tmp_path: pathlib.Path) -> None:
    src_path = str(tmp_path / "a.bin")
    dst_path = str(tmp_path / "b.bin")
    with open(src_path, "wb") as f:
        f.write(b"\x00\x01\x02")

    src = FileUri(src_path)
    target = FileUri(dst_path)

    result = _file_download(src, target)
    assert result is target
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /Users/davidchen/repo/anyuri && python -m pytest tests/io/handlers/test_http.py tests/io/handlers/test_file.py -v
```

Expected: `ModuleNotFoundError: No module named 'anyuri.io._handlers._http'`

- [ ] **Step 3: Implement HTTP handler**

Create `src/anyuri/io/_handlers/_http.py`:

```python
from __future__ import annotations

from urllib.request import Request, urlopen

from anyuri import FileUri, HttpUri
from anyuri.io._registry import register_download


@register_download(HttpUri)
def _http_download(uri: HttpUri, target: FileUri) -> FileUri:
    req = Request(str(uri), headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req) as response:
        with open(str(target), "wb") as f:
            f.write(response.read())
    return target


__all__ = ["_http_download"]
```

- [ ] **Step 4: Implement FileUri handler**

Create `src/anyuri/io/_handlers/_file.py`:

```python
from __future__ import annotations

import shutil

from anyuri import FileUri
from anyuri.io._registry import register_download


@register_download(FileUri)
def _file_download(uri: FileUri, target: FileUri) -> FileUri:
    shutil.copy(str(uri), str(target))
    return target


__all__ = ["_file_download"]
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
cd /Users/davidchen/repo/anyuri && python -m pytest tests/io/handlers/test_http.py tests/io/handlers/test_file.py -v
```

Expected: all 4 tests pass

- [ ] **Step 6: Commit**

```bash
git add src/anyuri/io/_handlers/__init__.py src/anyuri/io/_handlers/_http.py src/anyuri/io/_handlers/_file.py tests/io/handlers/test_http.py tests/io/handlers/test_file.py
git commit -m "feat(io): add HTTP and FileUri download handlers"
```

---

## Task 5: GCS Handler

**Files:**
- Create: `src/anyuri/io/_handlers/_gcs.py`
- Test: `tests/io/handlers/test_gcs.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/io/handlers/test_gcs.py`:

```python
# tests/io/handlers/test_gcs.py
import sys
from unittest.mock import MagicMock

import pytest

from anyuri import FileUri
from anyuri.providers._gcs import GSUri
from anyuri.io._handlers._gcs import _gcs_download, _gcs_upload


def _mock_gcs() -> MagicMock:
    mock_storage = MagicMock()
    mock_gc = MagicMock()
    mock_gc.storage = mock_storage
    sys.modules.setdefault("google", MagicMock())
    sys.modules["google.cloud"] = mock_gc
    sys.modules["google.cloud.storage"] = mock_storage
    return mock_storage


def test_gcs_download(tmp_path: pathlib.Path) -> None:
    mock_storage = _mock_gcs()
    mock_blob = mock_storage.Client.return_value.bucket.return_value.blob.return_value

    uri = GSUri("gs://my-bucket/path/video.mp4")
    target = FileUri(str(tmp_path / "video.mp4")

    result = _gcs_download(uri, target)

    mock_storage.Client.assert_called_once()
    mock_storage.Client.return_value.bucket.assert_called_once_with("my-bucket")
    mock_storage.Client.return_value.bucket.return_value.blob.assert_called_once_with("path/video.mp4")
    mock_blob.download_to_filename.assert_called_once_with(str(target))
    assert result == target


def test_gcs_upload(tmp_path: pathlib.Path) -> None:
    mock_storage = _mock_gcs()
    mock_blob = mock_storage.Client.return_value.bucket.return_value.blob.return_value

    src_path = str(tmp_path / "src.mp4")
    open(src_path, "w").close()
    src = FileUri(src_path)
    dst = GSUri("gs://my-bucket/output/video.mp4")

    result = _gcs_upload(src, dst)

    mock_storage.Client.assert_called_once()
    mock_storage.Client.return_value.bucket.assert_called_once_with("my-bucket")
    mock_storage.Client.return_value.bucket.return_value.blob.assert_called_once_with("output/video.mp4")
    mock_blob.upload_from_filename.assert_called_once_with(str(src))
    assert result == dst


def test_gcs_download_missing_sdk(tmp_path: pathlib.Path) -> None:
    original = sys.modules.pop("google.cloud.storage", None)
    original_gc = sys.modules.pop("google.cloud", None)
    original_g = sys.modules.pop("google", None)
    try:
        with pytest.raises(ImportError, match="anyuri\\[gcs\\]"):
            uri = GSUri("gs://bucket/file.mp4")
            target = FileUri(str(tmp_path / "file.mp4")
            _gcs_download(uri, target)
    finally:
        if original is not None:
            sys.modules["google.cloud.storage"] = original
        if original_gc is not None:
            sys.modules["google.cloud"] = original_gc
        if original_g is not None:
            sys.modules["google"] = original_g
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /Users/davidchen/repo/anyuri && python -m pytest tests/io/handlers/test_gcs.py -v
```

Expected: `ModuleNotFoundError: No module named 'anyuri.io._handlers._gcs'`

- [ ] **Step 3: Implement the GCS handler**

Create `src/anyuri/io/_handlers/_gcs.py`:

```python
from __future__ import annotations

from urllib.parse import urlparse

from anyuri import FileUri
from anyuri.providers._gcs import GSUri
from anyuri.io._registry import register_download, register_upload


@register_download(GSUri)
def _gcs_download(uri: GSUri, target: FileUri) -> FileUri:
    try:
        from google.cloud import storage  # type: ignore[import]
    except ImportError:
        raise ImportError("Install anyuri[gcs] for GCS support: pip install anyuri[gcs]")
    p = urlparse(uri.as_uri())
    bucket_name = p.netloc
    key = p.path.lstrip("/")
    client = storage.Client()
    client.bucket(bucket_name).blob(key).download_to_filename(str(target))
    return target


@register_upload(GSUri)
def _gcs_upload(src: FileUri, dst: GSUri) -> GSUri:
    try:
        from google.cloud import storage  # type: ignore[import]
    except ImportError:
        raise ImportError("Install anyuri[gcs] for GCS support: pip install anyuri[gcs]")
    p = urlparse(dst.as_uri())
    bucket_name = p.netloc
    key = p.path.lstrip("/")
    client = storage.Client()
    client.bucket(bucket_name).blob(key).upload_from_filename(str(src))
    return dst


__all__ = ["_gcs_download", "_gcs_upload"]
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd /Users/davidchen/repo/anyuri && python -m pytest tests/io/handlers/test_gcs.py -v
```

Expected: all 3 tests pass

- [ ] **Step 5: Commit**

```bash
git add src/anyuri/io/_handlers/_gcs.py tests/io/handlers/test_gcs.py
git commit -m "feat(io): add GCS download and upload handlers"
```

---

## Task 6: S3 Handler

**Files:**
- Create: `src/anyuri/io/_handlers/_s3.py`
- Test: `tests/io/handlers/test_s3.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/io/handlers/test_s3.py`:

```python
# tests/io/handlers/test_s3.py
import sys
from unittest.mock import MagicMock

import pytest

from anyuri import FileUri
from anyuri.providers._s3 import S3Uri
from anyuri.io._handlers._s3 import _s3_download, _s3_upload


def _mock_boto3() -> MagicMock:
    mock_boto3 = MagicMock()
    sys.modules["boto3"] = mock_boto3
    return mock_boto3


def test_s3_download(tmp_path: pathlib.Path) -> None:
    mock_boto3 = _mock_boto3()
    mock_s3 = mock_boto3.client.return_value

    uri = S3Uri("s3://my-bucket/path/video.mp4")
    target = FileUri(str(tmp_path / "video.mp4")

    result = _s3_download(uri, target)

    mock_boto3.client.assert_called_once_with("s3")
    mock_s3.download_file.assert_called_once_with("my-bucket", "path/video.mp4", str(target))
    assert result == target


def test_s3_upload(tmp_path: pathlib.Path) -> None:
    mock_boto3 = _mock_boto3()
    mock_s3 = mock_boto3.client.return_value

    src_path = str(tmp_path / "src.mp4")
    open(src_path, "w").close()
    src = FileUri(src_path)
    dst = S3Uri("s3://my-bucket/output/video.mp4")

    result = _s3_upload(src, dst)

    mock_boto3.client.assert_called_once_with("s3")
    mock_s3.upload_file.assert_called_once_with(str(src), "my-bucket", "output/video.mp4")
    assert result == dst


def test_s3_download_missing_sdk(tmp_path: pathlib.Path) -> None:
    original = sys.modules.pop("boto3", None)
    try:
        with pytest.raises(ImportError, match="anyuri\\[s3\\]"):
            uri = S3Uri("s3://bucket/file.mp4")
            target = FileUri(str(tmp_path / "file.mp4")
            _s3_download(uri, target)
    finally:
        if original is not None:
            sys.modules["boto3"] = original
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /Users/davidchen/repo/anyuri && python -m pytest tests/io/handlers/test_s3.py -v
```

Expected: `ModuleNotFoundError: No module named 'anyuri.io._handlers._s3'`

- [ ] **Step 3: Implement the S3 handler**

Create `src/anyuri/io/_handlers/_s3.py`:

```python
from __future__ import annotations

from urllib.parse import urlparse

from anyuri import FileUri
from anyuri.providers._s3 import S3Uri
from anyuri.io._registry import register_download, register_upload


@register_download(S3Uri)
def _s3_download(uri: S3Uri, target: FileUri) -> FileUri:
    try:
        import boto3  # type: ignore[import]
    except ImportError:
        raise ImportError("Install anyuri[s3] for S3 support: pip install anyuri[s3]")
    p = urlparse(uri.as_uri())
    bucket_name = p.netloc
    key = p.path.lstrip("/")
    boto3.client("s3").download_file(bucket_name, key, str(target))
    return target


@register_upload(S3Uri)
def _s3_upload(src: FileUri, dst: S3Uri) -> S3Uri:
    try:
        import boto3  # type: ignore[import]
    except ImportError:
        raise ImportError("Install anyuri[s3] for S3 support: pip install anyuri[s3]")
    p = urlparse(dst.as_uri())
    bucket_name = p.netloc
    key = p.path.lstrip("/")
    boto3.client("s3").upload_file(str(src), bucket_name, key)
    return dst


__all__ = ["_s3_download", "_s3_upload"]
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd /Users/davidchen/repo/anyuri && python -m pytest tests/io/handlers/test_s3.py -v
```

Expected: all 3 tests pass

- [ ] **Step 5: Commit**

```bash
git add src/anyuri/io/_handlers/_s3.py tests/io/handlers/test_s3.py
git commit -m "feat(io): add S3 download and upload handlers"
```

---

## Task 7: Azure Handler

**Files:**
- Create: `src/anyuri/io/_handlers/_azure.py`
- Test: `tests/io/handlers/test_azure.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/io/handlers/test_azure.py`:

```python
# tests/io/handlers/test_azure.py
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
    mock_blob.download_blob.return_value.readall.return_value = b"azure content"

    uri = AzureUri("abfs://container@account.dfs.core.windows.net/path/file.mp4")
    target = FileUri(str(tmp_path / "file.mp4")

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
            target = FileUri(str(tmp_path / "file.mp4")
            _azure_download(uri, target)
    finally:
        for k, v in [("azure.storage.blob", original), ("azure.storage", original_as), ("azure", original_a)]:
            if v is not None:
                sys.modules[k] = v
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /Users/davidchen/repo/anyuri && python -m pytest tests/io/handlers/test_azure.py -v
```

Expected: `ModuleNotFoundError: No module named 'anyuri.io._handlers._azure'`

- [ ] **Step 3: Implement the Azure handler**

Create `src/anyuri/io/_handlers/_azure.py`:

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd /Users/davidchen/repo/anyuri && python -m pytest tests/io/handlers/test_azure.py -v
```

Expected: all 3 tests pass

- [ ] **Step 5: Commit**

```bash
git add src/anyuri/io/_handlers/_azure.py tests/io/handlers/test_azure.py
git commit -m "feat(io): add Azure Blob Storage download and upload handlers"
```

---

## Task 8: R2 Handler

**Files:**
- Create: `src/anyuri/io/_handlers/_r2.py`
- Test: `tests/io/handlers/test_r2.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/io/handlers/test_r2.py`:

```python
# tests/io/handlers/test_r2.py
import sys
from unittest.mock import MagicMock, call

import pytest

from anyuri import FileUri
from anyuri.providers._r2 import R2Uri
from anyuri.io._handlers._r2 import _r2_download, _r2_upload


def _mock_boto3() -> MagicMock:
    mock_boto3 = MagicMock()
    sys.modules["boto3"] = mock_boto3
    return mock_boto3


def test_r2_download(tmp_path: pathlib.Path) -> None:
    mock_boto3 = _mock_boto3()
    mock_s3 = mock_boto3.client.return_value

    uri = R2Uri("r2://accountid/bucket/path/video.mp4")
    target = FileUri(str(tmp_path / "video.mp4")

    result = _r2_download(uri, target)

    mock_boto3.client.assert_called_once_with(
        "s3", endpoint_url="https://accountid.r2.cloudflarestorage.com"
    )
    mock_s3.download_file.assert_called_once_with("bucket", "path/video.mp4", str(target))
    assert result == target


def test_r2_upload(tmp_path: pathlib.Path) -> None:
    mock_boto3 = _mock_boto3()
    mock_s3 = mock_boto3.client.return_value

    src_path = str(tmp_path / "src.mp4")
    open(src_path, "w").close()
    src = FileUri(src_path)
    dst = R2Uri("r2://accountid/bucket/output/video.mp4")

    result = _r2_upload(src, dst)

    mock_boto3.client.assert_called_once_with(
        "s3", endpoint_url="https://accountid.r2.cloudflarestorage.com"
    )
    mock_s3.upload_file.assert_called_once_with(str(src), "bucket", "output/video.mp4")
    assert result == dst


def test_r2_download_missing_sdk(tmp_path: pathlib.Path) -> None:
    original = sys.modules.pop("boto3", None)
    try:
        with pytest.raises(ImportError, match="anyuri\\[r2\\]"):
            uri = R2Uri("r2://account/bucket/file.mp4")
            target = FileUri(str(tmp_path / "file.mp4")
            _r2_download(uri, target)
    finally:
        if original is not None:
            sys.modules["boto3"] = original
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /Users/davidchen/repo/anyuri && python -m pytest tests/io/handlers/test_r2.py -v
```

Expected: `ModuleNotFoundError: No module named 'anyuri.io._handlers._r2'`

- [ ] **Step 3: Implement the R2 handler**

Create `src/anyuri/io/_handlers/_r2.py`:

```python
from __future__ import annotations

from urllib.parse import urlparse

from anyuri import FileUri
from anyuri.providers._r2 import R2Uri
from anyuri.io._registry import register_download, register_upload


@register_download(R2Uri)
def _r2_download(uri: R2Uri, target: FileUri) -> FileUri:
    try:
        import boto3  # type: ignore[import]
    except ImportError:
        raise ImportError("Install anyuri[r2] for R2 support: pip install anyuri[r2]")
    p = urlparse(uri.as_uri())  # r2://accountid/bucket/key
    account_id = p.netloc
    path_parts = p.path.lstrip("/").split("/", 1)
    bucket_name = path_parts[0]
    key = path_parts[1] if len(path_parts) > 1 else ""
    s3 = boto3.client("s3", endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com")
    s3.download_file(bucket_name, key, str(target))
    return target


@register_upload(R2Uri)
def _r2_upload(src: FileUri, dst: R2Uri) -> R2Uri:
    try:
        import boto3  # type: ignore[import]
    except ImportError:
        raise ImportError("Install anyuri[r2] for R2 support: pip install anyuri[r2]")
    p = urlparse(dst.as_uri())  # r2://accountid/bucket/key
    account_id = p.netloc
    path_parts = p.path.lstrip("/").split("/", 1)
    bucket_name = path_parts[0]
    key = path_parts[1] if len(path_parts) > 1 else ""
    s3 = boto3.client("s3", endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com")
    s3.upload_file(str(src), bucket_name, key)
    return dst


__all__ = ["_r2_download", "_r2_upload"]
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd /Users/davidchen/repo/anyuri && python -m pytest tests/io/handlers/test_r2.py -v
```

Expected: all 3 tests pass

- [ ] **Step 5: Commit**

```bash
git add src/anyuri/io/_handlers/_r2.py tests/io/handlers/test_r2.py
git commit -m "feat(io): add Cloudflare R2 download and upload handlers"
```

---

## Task 9: B2 Handler

**Files:**
- Create: `src/anyuri/io/_handlers/_b2.py`
- Test: `tests/io/handlers/test_b2.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/io/handlers/test_b2.py`:

```python
# tests/io/handlers/test_b2.py
import sys
from unittest.mock import MagicMock

import pytest

from anyuri import FileUri
from anyuri.providers._b2 import B2Uri
from anyuri.io._handlers._b2 import _b2_download, _b2_upload


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
    target = FileUri(str(tmp_path / "video.mp4")

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
            target = FileUri(str(tmp_path / "file.mp4")
            _b2_download(uri, target)
    finally:
        if original is not None:
            sys.modules["b2sdk"] = original
        if original_v2 is not None:
            sys.modules["b2sdk.v2"] = original_v2
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /Users/davidchen/repo/anyuri && python -m pytest tests/io/handlers/test_b2.py -v
```

Expected: `ModuleNotFoundError: No module named 'anyuri.io._handlers._b2'`

- [ ] **Step 3: Implement the B2 handler**

Create `src/anyuri/io/_handlers/_b2.py`:

```python
from __future__ import annotations

from urllib.parse import urlparse

from anyuri import FileUri
from anyuri.providers._b2 import B2Uri
from anyuri.io._registry import register_download, register_upload


@register_download(B2Uri)
def _b2_download(uri: B2Uri, target: FileUri) -> FileUri:
    try:
        import b2sdk.v2 as b2  # type: ignore[import]
    except ImportError:
        raise ImportError("Install anyuri[b2] for B2 support: pip install anyuri[b2]")
    p = urlparse(uri.as_uri())  # b2://bucket/key
    bucket_name = p.netloc
    file_name = p.path.lstrip("/")
    api = b2.B2Api(b2.InMemoryAccountInfo())
    bucket = api.get_bucket_by_name(bucket_name)
    bucket.download_file_by_name(file_name).save_to(str(target))
    return target


@register_upload(B2Uri)
def _b2_upload(src: FileUri, dst: B2Uri) -> B2Uri:
    try:
        import b2sdk.v2 as b2  # type: ignore[import]
    except ImportError:
        raise ImportError("Install anyuri[b2] for B2 support: pip install anyuri[b2]")
    p = urlparse(dst.as_uri())  # b2://bucket/key
    bucket_name = p.netloc
    file_name = p.path.lstrip("/")
    api = b2.B2Api(b2.InMemoryAccountInfo())
    bucket = api.get_bucket_by_name(bucket_name)
    bucket.upload_local_file(local_file=str(src), file_name=file_name)
    return dst


__all__ = ["_b2_download", "_b2_upload"]
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd /Users/davidchen/repo/anyuri && python -m pytest tests/io/handlers/test_b2.py -v
```

Expected: all 3 tests pass

- [ ] **Step 5: Commit**

```bash
git add src/anyuri/io/_handlers/_b2.py tests/io/handlers/test_b2.py
git commit -m "feat(io): add Backblaze B2 download and upload handlers"
```

---

## Task 10: Wire Public API and Full Suite

**Files:**
- Modify: `src/anyuri/io/__init__.py`
- Test: run full suite

- [ ] **Step 1: Write the end-to-end import test**

Append to `tests/io/test_core.py`:

```python
def test_public_api_importable() -> None:
    from anyuri.io import download, upload
    assert callable(download)
    assert callable(upload)


def test_all_providers_registered_after_import() -> None:
    import anyuri.io  # noqa: F401 — triggers registration
    from anyuri.io._registry import _download_registry, _upload_registry
    from anyuri.providers._gcs import GSUri
    from anyuri.providers._s3 import S3Uri
    from anyuri.providers._azure import AzureUri
    from anyuri.providers._r2 import R2Uri
    from anyuri.providers._b2 import B2Uri
    from anyuri import HttpUri, FileUri

    for uri_cls in [HttpUri, FileUri, GSUri, S3Uri, AzureUri, R2Uri, B2Uri]:
        assert uri_cls in _download_registry, f"No download handler for {uri_cls.__name__}"

    for uri_cls in [GSUri, S3Uri, AzureUri, R2Uri, B2Uri]:
        assert uri_cls in _upload_registry, f"No upload handler for {uri_cls.__name__}"
```

- [ ] **Step 2: Run the test to verify it fails**

```bash
cd /Users/davidchen/repo/anyuri && python -m pytest tests/io/test_core.py::test_public_api_importable tests/io/test_core.py::test_all_providers_registered_after_import -v
```

Expected: `ImportError` — `download` not exported from `anyuri.io`

- [ ] **Step 3: Implement io/__init__.py**

Replace `src/anyuri/io/__init__.py`:

```python
from anyuri.io._core import download, upload
from anyuri.io._handlers import _http, _file, _gcs, _s3, _azure, _r2, _b2  # noqa: F401

__all__ = ["download", "upload"]
```

- [ ] **Step 4: Run the new tests to verify they pass**

```bash
cd /Users/davidchen/repo/anyuri && python -m pytest tests/io/test_core.py::test_public_api_importable tests/io/test_core.py::test_all_providers_registered_after_import -v
```

Expected: both pass

- [ ] **Step 5: Run the full test suite**

```bash
cd /Users/davidchen/repo/anyuri && python -m pytest tests/ -v
```

Expected: all tests pass (existing + new io tests)

- [ ] **Step 6: Commit**

```bash
git add src/anyuri/io/__init__.py tests/io/test_core.py
git commit -m "feat(io): wire anyuri.io public API, register all handlers on import"
```
