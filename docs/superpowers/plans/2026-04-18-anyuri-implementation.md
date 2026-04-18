# anyuri Open-Source Package Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create and publish `anyuri` — a standalone PyPI package of polymorphic URI types extracted from `genv-fs-core`, with multi-cloud provider support and a public registry API.

**Architecture:** Zero mandatory dependencies. `AnyUri` is a `str` subclass that auto-dispatches to `HttpUri`, `FileUri`, or a registered cloud provider. Cloud providers live in `anyuri/providers/` and self-register when imported. Built with TDD using pytest + syrupy snapshots.

**Tech Stack:** Python 3.10+, stdlib only for core; optional extras: `google-cloud-storage`, `boto3`, `azure-storage-blob`, `b2sdk`, `pydantic`; `pytest` + `syrupy` for tests; `ruff` + `mypy` for linting; GitHub Actions for CI; PyPI Trusted Publishing for release.

---

## File Map

| File | Responsibility |
|---|---|
| `src/anyuri/__init__.py` | `AnyUri`, `HttpUri`, `FileUri`, registry API, pydantic integration |
| `src/anyuri/_exceptions.py` | `UriSchemaError` |
| `src/anyuri/_utils.py` | `normalize_url`, `uri_to_path` (stdlib only) |
| `src/anyuri/providers/__init__.py` | Re-exports `GSUri`, `S3Uri`, `AzureUri`, `R2Uri`, `B2Uri` |
| `src/anyuri/providers/_gcs.py` | `GSUri` — GCS URIs |
| `src/anyuri/providers/_s3.py` | `S3Uri` — AWS S3 URIs |
| `src/anyuri/providers/_azure.py` | `AzureUri` — Azure Blob Storage URIs |
| `src/anyuri/providers/_r2.py` | `R2Uri` — Cloudflare R2 URIs |
| `src/anyuri/providers/_b2.py` | `B2Uri` — Backblaze B2 URIs |
| `tests/conftest.py` | pytest fixtures (pydantic helper, registry cleanup) |
| `tests/test_core.py` | `AnyUri`, `HttpUri`, `FileUri` snapshot + validation tests |
| `tests/test_registry.py` | `AnyUri.register()` and `@AnyUri.register` tests |
| `tests/providers/test_gcs.py` | `GSUri` parametrized tests |
| `tests/providers/test_s3.py` | `S3Uri` parametrized tests |
| `tests/providers/test_azure.py` | `AzureUri` parametrized tests |
| `tests/providers/test_r2.py` | `R2Uri` parametrized tests |
| `tests/providers/test_b2.py` | `B2Uri` parametrized tests |
| `pyproject.toml` | Package metadata, extras, dev deps |
| `ruff.toml` | Ruff linting config |
| `mypy.ini` | mypy config |
| `.github/workflows/test.yml` | CI: pytest on Python 3.10–3.13 |
| `.github/workflows/lint.yml` | CI: ruff + mypy |
| `.github/workflows/release.yml` | CD: publish to PyPI on version tag |
| `README.md` | Usage docs |

---

### Task 1: Project Scaffold

**Files:**
- Create: `pyproject.toml`
- Create: `ruff.toml`
- Create: `mypy.ini`
- Create: `.gitignore`
- Create: `src/anyuri/__init__.py` (empty)
- Create: `src/anyuri/providers/__init__.py` (empty)
- Create: `tests/__init__.py` (empty)
- Create: `tests/providers/__init__.py` (empty)
- Create: `tests/data/test_relative_fileuri/foo.bar` (test fixture file)

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p src/anyuri/providers tests/providers tests/data/test_relative_fileuri
touch src/anyuri/__init__.py src/anyuri/providers/__init__.py
touch tests/__init__.py tests/providers/__init__.py
```

- [ ] **Step 2: Create `pyproject.toml`**

```toml
[project]
name = "anyuri"
dynamic = ["version"]
description = "Polymorphic URI types for Python: AnyUri, HttpUri, FileUri, GSUri, S3Uri, AzureUri, R2Uri, B2Uri"
authors = [{ name = "lucemia", email = "lucemia@gmail.com" }]
readme = "README.md"
requires-python = ">=3.10"
dependencies = []
license = { text = "MIT" }
keywords = ["uri", "url", "gcs", "s3", "azure", "pydantic"]
classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]

[project.urls]
Homepage = "https://github.com/lucemia/anyuri"
Repository = "https://github.com/lucemia/anyuri"

[project.optional-dependencies]
gcs     = ["google-cloud-storage"]
s3      = ["boto3"]
azure   = ["azure-storage-blob"]
r2      = ["boto3"]
b2      = ["b2sdk"]
all     = ["google-cloud-storage", "boto3", "azure-storage-blob", "b2sdk"]
pydantic = ["pydantic>=1.0"]

[dependency-groups]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=5.0.0",
    "pytest-datadir>=1.5.0",
    "syrupy>=4.6.0",
    "mypy>=1.9.0",
    "ruff",
    "pydantic>=2.0",
]

[tool.setuptools.packages.find]
where = ["src"]
exclude = ["*tests*", "*__pycache__*"]

[tool.setuptools_scm]
fallback_version = "0.0.0"

[build-system]
requires = ["setuptools>=64", "setuptools-scm>=8"]
build-backend = "setuptools.build_meta"
```

- [ ] **Step 3: Create `ruff.toml`**

```toml
line-length = 120
target-version = "py310"

[lint]
select = ["E", "F", "I", "UP"]
ignore = ["E501"]
```

- [ ] **Step 4: Create `mypy.ini`**

```ini
[mypy]
python_version = 3.10
strict = true
ignore_missing_imports = true
```

- [ ] **Step 5: Create `.gitignore`**

```
__pycache__/
*.pyc
*.pyo
.pytest_cache/
.mypy_cache/
.ruff_cache/
dist/
build/
*.egg-info/
.venv/
venv/
.coverage
htmlcov/
```

- [ ] **Step 6: Create test fixture file**

```bash
echo "test fixture" > tests/data/test_relative_fileuri/foo.bar
mkdir -p tests/data/test_relative_fileuri/tmp
echo "test fixture" > tests/data/test_relative_fileuri/tmp/dummy
```

- [ ] **Step 7: Install dev dependencies**

```bash
uv sync
```

Expected: dependencies installed without error.

- [ ] **Step 8: Commit**

```bash
git add pyproject.toml ruff.toml mypy.ini .gitignore src/ tests/
git commit -m "chore: scaffold anyuri package structure"
```

---

### Task 2: Exceptions and Utilities

**Files:**
- Create: `src/anyuri/_exceptions.py`
- Create: `src/anyuri/_utils.py`
- Create: `tests/test_utils.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_utils.py`:

```python
import pytest
from anyuri._exceptions import UriSchemaError
from anyuri._utils import normalize_url, uri_to_path


def test_uri_schema_error_is_value_error() -> None:
    with pytest.raises(ValueError):
        raise UriSchemaError("bad uri")


def test_normalize_url_resolves_dotdot() -> None:
    assert normalize_url("https://example.com/foo/../bar.jpg") == "https://example.com/bar.jpg"


def test_normalize_url_resolves_multiple_dotdot() -> None:
    assert normalize_url("https://example.com/a/b/../../c.jpg") == "https://example.com/c.jpg"


def test_normalize_url_preserves_query_and_fragment() -> None:
    result = normalize_url("https://example.com/foo/../bar.jpg?q=1#sec")
    assert result == "https://example.com/bar.jpg?q=1#sec"


def test_normalize_url_no_op_for_clean_url() -> None:
    assert normalize_url("https://example.com/path/file.jpg") == "https://example.com/path/file.jpg"


def test_uri_to_path_converts_file_uri() -> None:
    assert uri_to_path("file:///tmp/test.jpg") == "/tmp/test.jpg"


def test_uri_to_path_with_localhost() -> None:
    assert uri_to_path("file://localhost/tmp/test.jpg") == "/tmp/test.jpg"


def test_uri_to_path_decodes_percent_encoding() -> None:
    result = uri_to_path("file:///tmp/my%20file.jpg")
    assert result == "/tmp/my file.jpg"


def test_uri_to_path_rejects_non_file_scheme() -> None:
    with pytest.raises(ValueError):
        uri_to_path("https://example.com/file.jpg")
```

- [ ] **Step 2: Run to verify failure**

```bash
uv run pytest tests/test_utils.py -v
```

Expected: `ImportError` — `anyuri._exceptions` does not exist yet.

- [ ] **Step 3: Create `src/anyuri/_exceptions.py`**

```python
class UriSchemaError(ValueError):
    """Raised when a URI cannot be validated by any registered URI type."""


__all__ = ["UriSchemaError"]
```

- [ ] **Step 4: Create `src/anyuri/_utils.py`**

```python
import os
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse, urlunparse


def normalize_url(http_uri: str) -> str:
    """Normalize an HTTP URI by resolving '..' and '.' segments in the path."""
    parsed = urlparse(http_uri)
    resolved = urljoin(http_uri, parsed.path)
    return urlunparse(parsed._replace(path=urlparse(resolved).path))


def uri_to_path(file_uri: str) -> str:
    """Convert a file:// URI to a local filesystem path."""
    parsed = urlparse(file_uri)
    if parsed.scheme != "file":
        raise ValueError(f"Unsupported scheme: {parsed.scheme!r}")
    path_str = unquote(parsed.path)
    # Windows: "/C:/..." → "C:/..."
    if os.name == "nt" and path_str.startswith("/") and len(path_str) > 2 and path_str[2] == ":":
        path_str = path_str[1:]
    return os.path.normpath(Path(path_str))


__all__ = ["normalize_url", "uri_to_path"]
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
uv run pytest tests/test_utils.py -v
```

Expected: all 9 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add src/anyuri/_exceptions.py src/anyuri/_utils.py tests/test_utils.py
git commit -m "feat: add UriSchemaError and URI utility functions"
```

---

### Task 3: Core AnyUri, HttpUri, FileUri with Registry

**Files:**
- Modify: `src/anyuri/__init__.py`

- [ ] **Step 1: Write `src/anyuri/__init__.py`**

```python
"""
anyuri — Polymorphic URI types for Python.

Constructing an AnyUri instance auto-dispatches to the correct subclass:

    >>> AnyUri("https://example.com/1.jpg")
    HttpUri("https://example.com/1.jpg")

    >>> AnyUri("/local/path.jpg")
    FileUri("/local/path.jpg")

Cloud providers register themselves when their module is imported:

    >>> from anyuri.providers import GSUri
    >>> AnyUri("gs://bucket/key.jpg")
    GSUri("gs://bucket/key.jpg")

Custom types can be registered:

    >>> @AnyUri.register
    ... class SFTPUri(AnyUri): ...

    >>> AnyUri.register(SFTPUri)  # equivalent explicit call
"""

from __future__ import annotations

import pathlib
from functools import cached_property
from typing import Any, no_type_check
from urllib.parse import ParseResult, urlparse

from ._exceptions import UriSchemaError
from ._utils import normalize_url, uri_to_path


class AnyUri(str):
    """
    Polymorphic virtual superclass for URI types.

    Constructing an instance auto-dispatches to the registered subclass that
    matches the input. Behaves like a plain ``str`` in all contexts.

    Examples:
        >>> AnyUri("https://example.com/1.jpg")
        HttpUri("https://example.com/1.jpg")

        >>> AnyUri("file:///1.jpg")
        FileUri("/1.jpg")

        >>> AnyUri("https://example.com/1.jpg") == "https://example.com/1.jpg"
        True
    """

    _registry: list[type[AnyUri]] = []

    def __new__(cls, value: Any) -> AnyUri:
        if cls is AnyUri:
            return AnyUri.validate(value)
        return str.__new__(cls, value)

    @classmethod
    def register(cls, uri_cls: type[AnyUri]) -> type[AnyUri]:
        """Register a URI subclass. May be used as a decorator or called directly.

        Registered types are tried before built-in types. If multiple custom
        types are registered, the most recently registered is tried first.

        Args:
            uri_cls: An AnyUri subclass to register.

        Returns:
            The registered class (enables use as a class decorator).

        Examples:
            >>> AnyUri.register(MyUri)

            >>> @AnyUri.register
            ... class MyUri(AnyUri): ...
        """
        if uri_cls not in cls._registry:
            cls._registry.insert(0, uri_cls)
        return uri_cls

    @classmethod
    def validate(cls, value: Any) -> AnyUri:
        """Validate and return the appropriate AnyUri subclass for ``value``.

        Raises:
            UriSchemaError: if no registered type accepts the input.
        """
        for _cls in cls._registry:
            try:
                return _cls(value)
            except UriSchemaError:
                continue
        raise UriSchemaError(f"Invalid URI: {value!r}")

    @cached_property
    def _parsed(self) -> ParseResult:
        return urlparse(self.as_uri())

    @property
    def scheme(self) -> str:
        """The URI scheme (e.g. ``"https"``, ``"gs"``, ``"s3"``)."""
        return self._parsed.scheme

    @property
    def netloc(self) -> str:
        """The network location (host + optional port)."""
        return self._parsed.netloc

    @property
    def path(self) -> str:
        """The path component of the URI."""
        return self._parsed.path

    @property
    def params(self) -> str:
        """The parameters component of the URI."""
        return self._parsed.params

    @property
    def query(self) -> str:
        """The query string."""
        return self._parsed.query

    @property
    def fragment(self) -> str:
        """The fragment identifier."""
        return self._parsed.fragment

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}("{self.as_uri()}")'

    def as_uri(self) -> str:
        """Canonical URI form (e.g. ``gs://bucket/key`` for GCS).

        Returns:
            The canonical URI string.
        """
        return self.as_source()

    def as_source(self) -> str:
        """Tool-compatible form — the most widely accepted representation.

        This is what ``str(uri)`` returns. For GCS it is the HTTPS URL;
        for local files it is the POSIX path.

        Returns:
            The source string.
        """
        return str(self)

    @no_type_check
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: Any) -> Any:
        from pydantic_core import core_schema

        return core_schema.no_info_after_validator_function(cls.validate, core_schema.any_schema())

    @classmethod
    def __get_validators__(cls) -> Any:
        yield cls.validate


class HttpUri(AnyUri):
    """URI for HTTP or HTTPS resources.

    Examples:
        >>> HttpUri("https://example.com/1.jpg")
        HttpUri("https://example.com/1.jpg")

        >>> HttpUri("http://example.com/1.jpg")
        HttpUri("http://example.com/1.jpg")
    """

    def __new__(cls, value: Any) -> HttpUri:
        return str.__new__(cls, cls._validate(value))

    @classmethod
    def _validate(cls, value: Any) -> str:
        v = str(value)
        p = urlparse(v)
        if p.scheme not in {"http", "https"}:
            raise UriSchemaError(f"Invalid scheme for HttpUri: {value!r}")
        return normalize_url(v)

    @classmethod
    def validate(cls, value: Any) -> HttpUri:
        return cls(cls._validate(value))


class FileUri(AnyUri):
    """URI for local filesystem resources. Accepts paths, ``file:///``, and ``file://localhost/``.

    Note:
        The ``query``, ``fragment``, and ``params`` components are ignored.

    Examples:
        >>> FileUri("/tmp/1.jpg")
        FileUri("/tmp/1.jpg")

        >>> FileUri("file:///tmp/1.jpg")
        FileUri("/tmp/1.jpg")
    """

    def __new__(cls, value: Any) -> FileUri:
        return str.__new__(cls, cls._validate(value))

    @classmethod
    def _validate(cls, value: Any) -> str:
        v = str(value)
        if "://" not in v:
            v = pathlib.Path(v).resolve().as_uri()
        p = urlparse(v)
        if p.scheme != "file":
            raise UriSchemaError(f"Invalid scheme for FileUri: {value!r}")
        if p.netloc not in {"", "localhost"}:
            raise UriSchemaError(f"Invalid netloc for FileUri: {value!r}")
        return uri_to_path(v)

    @classmethod
    def validate(cls, value: Any) -> FileUri:
        return cls(cls._validate(value))

    def as_uri(self) -> str:
        return f"file://localhost{self}"


# HttpUri and FileUri are the fallback types — always last in the registry.
# Cloud providers prepend themselves when imported.
AnyUri._registry = [HttpUri, FileUri]


__all__ = ["AnyUri", "HttpUri", "FileUri", "UriSchemaError"]
```

- [ ] **Step 2: Verify it imports cleanly**

```bash
uv run python -c "from anyuri import AnyUri, HttpUri, FileUri; print(AnyUri('https://example.com/1.jpg'))"
```

Expected output: `https://example.com/1.jpg`

- [ ] **Step 3: Commit**

```bash
git add src/anyuri/__init__.py
git commit -m "feat: add AnyUri, HttpUri, FileUri with registry"
```

---

### Task 4: Core Type Tests

**Files:**
- Create: `tests/conftest.py`
- Create: `tests/test_core.py`

- [ ] **Step 1: Create `tests/conftest.py`**

```python
from __future__ import annotations

from typing import Any, no_type_check

import pytest
from anyuri import AnyUri


@no_type_check
def parse_obj_as(cls: type[AnyUri], obj: Any) -> AnyUri:
    """Validate using Pydantic v1 or v2, whichever is installed."""
    try:
        from pydantic import TypeAdapter
        return TypeAdapter(cls).validate_python(obj)
    except ImportError:
        from pydantic import parse_obj_as as _parse
        return _parse(cls, obj)


@pytest.fixture
def clean_registry():
    """Restore the AnyUri registry after the test (prevents test pollution)."""
    original = AnyUri._registry.copy()
    yield
    AnyUri._registry = original
```

- [ ] **Step 2: Create `tests/test_core.py`**

```python
import os
from pathlib import Path
from typing import Any

import pydantic
import pytest
from syrupy.assertion import SnapshotAssertion
from syrupy.extensions.json import JSONSnapshotExtension

from anyuri import AnyUri, FileUri, HttpUri
from anyuri._exceptions import UriSchemaError
from tests.conftest import parse_obj_as


class Foo(pydantic.BaseModel):
    uri: AnyUri


@pytest.mark.parametrize(
    "uri",
    [
        # FileUri
        "/absolute.jpg",
        "/%e8.txt",
        "file:///1.jpg",
        "file:///test_converter_download%5Bstoryblock%5D/43b5f971a5c37b8cc008db83999d027d6d0b9b5c.mp4",
        "file://localhost/test_converter_download%5Bstoryblock%5D/43b5f971a5c37b8cc008db83999d027d6d0b9b5c.mp4",
        "file://localhost/1.jpg",
        "file://localhost/1.jpg?q=1",
        "file://localhost/1.jpg?q=1#fragment",
        # HttpUri
        "http://example.com/1.jpg",
        "http://example.com/1.jpg?q=1",
        "https://example.com/foo/../1.jpg",
        "https://example.com/foo/../../1.jpg",
        "https://example.com/foo/../1.jpg?q=1",
        "https://example.com/foo/../1.jpg?q=1#fragment",
        "https://example.com/foo/",
        "https://example.com/foo2",
        "https://test.com",
    ],
)
def test_anyuri(uri: str, snapshot: SnapshotAssertion) -> None:
    any_uri_init = AnyUri(uri)
    any_uri_parse = parse_obj_as(AnyUri, uri)
    foo = Foo(uri=uri)  # type: ignore[arg-type]

    assert type(any_uri_init) is type(any_uri_parse) is type(foo.uri), "type consistency"
    assert any_uri_init == any_uri_parse == foo.uri, "value consistency"
    assert isinstance(any_uri_init, AnyUri)

    assert snapshot(extension_class=JSONSnapshotExtension) == {
        "self": any_uri_init,
        "type": type(any_uri_init),
        "str": str(any_uri_init),
        "repr": repr(any_uri_init),
        "as_uri": any_uri_init.as_uri(),
        "as_source": any_uri_init.as_source(),
        "scheme": any_uri_init.scheme,
        "netloc": any_uri_init.netloc,
        "path": any_uri_init.path,
        "params": any_uri_init.params,
        "query": any_uri_init.query,
        "fragment": any_uri_init.fragment,
    }


def test_validate_success() -> None:
    assert isinstance(FileUri.validate("file:///1.jpg"), FileUri)
    assert isinstance(FileUri.validate("file://localhost/1.jpg"), FileUri)
    assert isinstance(HttpUri.validate("http://example.com/1.jpg"), HttpUri)


@pytest.mark.parametrize(
    "cls, uri",
    [
        (HttpUri, "xxx"),
        (HttpUri, "foo://123.jpg"),
        (FileUri, "foo://123.jpg"),
        (FileUri, "file://xxxx/1.jpg"),
        (AnyUri, "foo://123.jpg"),
    ],
)
def test_validate_failed(cls: type[AnyUri], uri: str) -> None:
    with pytest.raises(ValueError):
        cls.validate(uri)
    with pytest.raises(ValueError):
        cls(uri)


@pytest.mark.parametrize(
    "filename",
    [
        "foo.bar",
        "tmp/../foo.bar",
    ],
)
def test_relative_fileuri(filename: str, datadir: Path) -> None:
    p = datadir / filename
    file_uri = AnyUri(p)

    assert isinstance(file_uri, FileUri)
    from urllib.parse import urlparse
    parsed = urlparse(file_uri.as_uri())
    assert parsed.scheme == "file"
    assert parsed.netloc == "localhost"
    assert parsed.path.endswith(p.name)
    assert os.path.exists(file_uri.as_source())
    assert isinstance(file_uri, AnyUri)
```

- [ ] **Step 3: Run tests — they will fail on snapshot assertion (no snapshots yet)**

```bash
uv run pytest tests/test_core.py -v --ignore=tests/providers
```

Expected: FAIL with `snapshot does not exist`.

- [ ] **Step 4: Generate snapshots**

```bash
uv run pytest tests/test_core.py --snapshot-update --ignore=tests/providers -v
```

Expected: snapshots created in `tests/__snapshots__/test_core/`. All tests PASS.

- [ ] **Step 5: Run again to confirm snapshots pass**

```bash
uv run pytest tests/test_core.py -v --ignore=tests/providers
```

Expected: all tests PASS.

- [ ] **Step 6: Commit**

```bash
git add tests/conftest.py tests/test_core.py tests/__snapshots__/ tests/data/
git commit -m "test: add core AnyUri snapshot tests"
```

---

### Task 5: Registry Tests

**Files:**
- Create: `tests/test_registry.py`

- [ ] **Step 1: Create `tests/test_registry.py`**

```python
import pytest
from anyuri import AnyUri, HttpUri
from anyuri._exceptions import UriSchemaError
from tests.conftest import clean_registry  # noqa: F401 — imported for fixture


def test_register_explicit(clean_registry: None) -> None:  # type: ignore[type-arg]
    class SFTPUri(AnyUri):
        def __new__(cls, value: object) -> "SFTPUri":
            return str.__new__(cls, cls._validate(value))

        @classmethod
        def _validate(cls, value: object) -> str:
            v = str(value)
            if not v.startswith("sftp://"):
                raise UriSchemaError(f"Not an SFTP URI: {v!r}")
            return v

        @classmethod
        def validate(cls, value: object) -> "SFTPUri":
            return cls(cls._validate(value))

    AnyUri.register(SFTPUri)
    result = AnyUri("sftp://host/path/file.txt")
    assert isinstance(result, SFTPUri)
    assert str(result) == "sftp://host/path/file.txt"


def test_register_decorator(clean_registry: None) -> None:  # type: ignore[type-arg]
    @AnyUri.register
    class FTPUri(AnyUri):
        def __new__(cls, value: object) -> "FTPUri":
            return str.__new__(cls, cls._validate(value))

        @classmethod
        def _validate(cls, value: object) -> str:
            v = str(value)
            if not v.startswith("ftp://"):
                raise UriSchemaError(f"Not an FTP URI: {v!r}")
            return v

        @classmethod
        def validate(cls, value: object) -> "FTPUri":
            return cls(cls._validate(value))

    result = AnyUri("ftp://host/path/file.txt")
    assert isinstance(result, FTPUri)


def test_register_returns_class(clean_registry: None) -> None:  # type: ignore[type-arg]
    class MyUri(AnyUri):
        def __new__(cls, value: object) -> "MyUri":
            raise UriSchemaError("never matches")

        @classmethod
        def validate(cls, value: object) -> "MyUri":
            raise UriSchemaError("never matches")

    returned = AnyUri.register(MyUri)
    assert returned is MyUri


def test_register_custom_takes_priority_over_http(clean_registry: None) -> None:  # type: ignore[type-arg]
    """Custom registered type should be tried before HttpUri."""

    class SpecialHttpUri(AnyUri):
        def __new__(cls, value: object) -> "SpecialHttpUri":
            return str.__new__(cls, cls._validate(value))

        @classmethod
        def _validate(cls, value: object) -> str:
            v = str(value)
            if not v.startswith("https://special.example.com"):
                raise UriSchemaError(f"Not special: {v!r}")
            return v

        @classmethod
        def validate(cls, value: object) -> "SpecialHttpUri":
            return cls(cls._validate(value))

    AnyUri.register(SpecialHttpUri)
    result = AnyUri("https://special.example.com/1.jpg")
    assert isinstance(result, SpecialHttpUri)

    # Non-matching https:// still falls back to HttpUri
    fallback = AnyUri("https://other.example.com/1.jpg")
    assert isinstance(fallback, HttpUri)


def test_register_no_duplicates(clean_registry: None) -> None:  # type: ignore[type-arg]
    class MyUri(AnyUri):
        def __new__(cls, value: object) -> "MyUri":
            raise UriSchemaError("never matches")

        @classmethod
        def validate(cls, value: object) -> "MyUri":
            raise UriSchemaError("never matches")

    before_count = len(AnyUri._registry)
    AnyUri.register(MyUri)
    AnyUri.register(MyUri)  # second call should not add a duplicate
    assert len(AnyUri._registry) == before_count + 1


def test_unregistered_scheme_raises(clean_registry: None) -> None:  # type: ignore[type-arg]
    with pytest.raises(UriSchemaError):
        AnyUri("foo://unknown/scheme")
```

- [ ] **Step 2: Run tests**

```bash
uv run pytest tests/test_registry.py -v
```

Expected: all 6 tests PASS.

- [ ] **Step 3: Commit**

```bash
git add tests/test_registry.py
git commit -m "test: add registry API tests"
```

---

### Task 6: GSUri Provider

**Files:**
- Create: `src/anyuri/providers/_gcs.py`
- Create: `tests/providers/test_gcs.py`

- [ ] **Step 1: Write failing tests**

Create `tests/providers/test_gcs.py`:

```python
import pytest
from anyuri import AnyUri
from anyuri._exceptions import UriSchemaError
from anyuri.providers._gcs import GSUri  # importing registers GSUri


@pytest.mark.parametrize(
    "uri, expected_uri, expected_source",
    [
        (
            "gs://bucket/1.jpg",
            "gs://bucket/1.jpg",
            "https://storage.googleapis.com/bucket/1.jpg",
        ),
        (
            "https://storage.googleapis.com/bucket/1.jpg",
            "gs://bucket/1.jpg",
            "https://storage.googleapis.com/bucket/1.jpg",
        ),
        (
            "gs://bucket/path/to/file.mp4",
            "gs://bucket/path/to/file.mp4",
            "https://storage.googleapis.com/bucket/path/to/file.mp4",
        ),
        (
            "gs://bucket/1.jpg?q=2",
            "gs://bucket/1.jpg?q=2",
            "https://storage.googleapis.com/bucket/1.jpg?q=2",
        ),
        (
            "https://storage.googleapis.com/bucket/file.html?q=1#frag",
            "gs://bucket/file.html?q=1#frag",
            "https://storage.googleapis.com/bucket/file.html?q=1#frag",
        ),
    ],
)
def test_gsuri(uri: str, expected_uri: str, expected_source: str) -> None:
    result = AnyUri(uri)
    assert isinstance(result, GSUri)
    assert result.as_uri() == expected_uri
    assert result.as_source() == expected_source
    assert str(result) == expected_source


def test_gsuri_isinstance_anyuri() -> None:
    uri = AnyUri("gs://bucket/1.jpg")
    assert isinstance(uri, AnyUri)
    assert isinstance(uri, GSUri)


def test_gsuri_invalid_netloc() -> None:
    with pytest.raises(UriSchemaError):
        GSUri("https://example.com/1.jpg")


def test_gsuri_invalid_scheme() -> None:
    with pytest.raises(UriSchemaError):
        GSUri("foo://bucket/1.jpg")
```

- [ ] **Step 2: Run to verify failure**

```bash
uv run pytest tests/providers/test_gcs.py -v
```

Expected: `ImportError` — `anyuri.providers._gcs` does not exist.

- [ ] **Step 3: Create `src/anyuri/providers/_gcs.py`**

```python
"""GSUri — Google Cloud Storage URI type."""

from __future__ import annotations

from typing import Any
from urllib.parse import urlparse, urlunparse

from anyuri._exceptions import UriSchemaError
from anyuri import AnyUri


class GSUri(AnyUri):
    """URI for Google Cloud Storage resources.

    Accepts both ``gs://`` and ``https://storage.googleapis.com/`` forms.
    Stores internally as HTTPS; ``as_uri()`` returns the ``gs://`` form.

    Examples:
        >>> GSUri("gs://bucket/1.jpg")
        GSUri("gs://bucket/1.jpg")

        >>> GSUri("https://storage.googleapis.com/bucket/1.jpg")
        GSUri("gs://bucket/1.jpg")
    """

    def __new__(cls, value: Any) -> GSUri:
        return str.__new__(cls, cls._validate(value))

    @classmethod
    def _validate(cls, value: Any) -> str:
        v = str(value)
        p = urlparse(v)
        if p.scheme in {"http", "https"}:
            if p.netloc != "storage.googleapis.com":
                raise UriSchemaError(f"Invalid netloc for GSUri: {value!r}")
            return urlunparse(("https", "storage.googleapis.com", p.path, p.params, p.query, p.fragment))
        if p.scheme == "gs":
            return urlunparse(
                ("https", "storage.googleapis.com", f"{p.netloc}{p.path}", p.params, p.query, p.fragment)
            )
        raise UriSchemaError(f"Invalid GSUri: {value!r}")

    @classmethod
    def validate(cls, value: Any) -> GSUri:
        return cls(cls._validate(value))

    def as_uri(self) -> str:
        return str(self).replace("https://storage.googleapis.com/", "gs://", 1)


# Auto-register when this module is imported
AnyUri.register(GSUri)

__all__ = ["GSUri"]
```

- [ ] **Step 4: Run tests**

```bash
uv run pytest tests/providers/test_gcs.py -v
```

Expected: all 4 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/anyuri/providers/_gcs.py tests/providers/test_gcs.py
git commit -m "feat: add GSUri provider for Google Cloud Storage"
```

---

### Task 7: S3Uri Provider

**Files:**
- Create: `src/anyuri/providers/_s3.py`
- Create: `tests/providers/test_s3.py`

- [ ] **Step 1: Write failing tests**

Create `tests/providers/test_s3.py`:

```python
import pytest
from anyuri import AnyUri
from anyuri._exceptions import UriSchemaError
from anyuri.providers._s3 import S3Uri  # importing registers S3Uri


@pytest.mark.parametrize(
    "uri, expected_uri, expected_source",
    [
        (
            "s3://mybucket/key.jpg",
            "s3://mybucket/key.jpg",
            "https://mybucket.s3.amazonaws.com/key.jpg",
        ),
        (
            "https://mybucket.s3.amazonaws.com/key.jpg",
            "s3://mybucket/key.jpg",
            "https://mybucket.s3.amazonaws.com/key.jpg",
        ),
        (
            "https://mybucket.s3.us-east-1.amazonaws.com/key.jpg",
            "s3://mybucket/key.jpg",
            "https://mybucket.s3.amazonaws.com/key.jpg",
        ),
        (
            "https://s3.amazonaws.com/mybucket/key.jpg",
            "s3://mybucket/key.jpg",
            "https://mybucket.s3.amazonaws.com/key.jpg",
        ),
        (
            "https://s3.us-west-2.amazonaws.com/mybucket/subdir/key.jpg",
            "s3://mybucket/subdir/key.jpg",
            "https://mybucket.s3.amazonaws.com/subdir/key.jpg",
        ),
    ],
)
def test_s3uri(uri: str, expected_uri: str, expected_source: str) -> None:
    result = AnyUri(uri)
    assert isinstance(result, S3Uri)
    assert result.as_uri() == expected_uri
    assert result.as_source() == expected_source
    assert str(result) == expected_source


def test_s3uri_isinstance_anyuri() -> None:
    uri = AnyUri("s3://bucket/key.jpg")
    assert isinstance(uri, AnyUri)
    assert isinstance(uri, S3Uri)


def test_s3uri_invalid_scheme() -> None:
    with pytest.raises(UriSchemaError):
        S3Uri("gs://bucket/key.jpg")


def test_s3uri_invalid_http_host() -> None:
    with pytest.raises(UriSchemaError):
        S3Uri("https://example.com/key.jpg")
```

- [ ] **Step 2: Run to verify failure**

```bash
uv run pytest tests/providers/test_s3.py -v
```

Expected: `ImportError` — `anyuri.providers._s3` does not exist.

- [ ] **Step 3: Create `src/anyuri/providers/_s3.py`**

```python
"""S3Uri — AWS S3 URI type."""

from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

from anyuri._exceptions import UriSchemaError
from anyuri import AnyUri


class S3Uri(AnyUri):
    """URI for AWS S3 resources.

    Accepts ``s3://``, virtual-hosted HTTPS, and path-style HTTPS forms.
    Stores internally as virtual-hosted HTTPS; ``as_uri()`` returns ``s3://``.

    Examples:
        >>> S3Uri("s3://bucket/key.jpg")
        S3Uri("s3://bucket/key.jpg")

        >>> S3Uri("https://bucket.s3.amazonaws.com/key.jpg")
        S3Uri("s3://bucket/key.jpg")
    """

    def __new__(cls, value: Any) -> S3Uri:
        return str.__new__(cls, cls._validate(value))

    @classmethod
    def _validate(cls, value: Any) -> str:
        v = str(value)
        p = urlparse(v)

        if p.scheme == "s3":
            bucket = p.netloc
            key = p.path
            return f"https://{bucket}.s3.amazonaws.com{key}"

        if p.scheme in {"http", "https"}:
            hostname = p.hostname or ""
            if not hostname.endswith(".amazonaws.com"):
                raise UriSchemaError(f"Invalid host for S3Uri: {value!r}")

            parts = hostname.split(".")
            # Virtual-hosted: bucket.s3.amazonaws.com or bucket.s3.region.amazonaws.com
            if len(parts) >= 3 and parts[1] == "s3":
                bucket = parts[0]
                return f"https://{bucket}.s3.amazonaws.com{p.path}"

            # Path-style: s3.amazonaws.com or s3.region.amazonaws.com
            if parts[0] == "s3":
                path_parts = p.path.lstrip("/").split("/", 1)
                if not path_parts[0]:
                    raise UriSchemaError(f"Missing bucket in S3 path-style URL: {value!r}")
                bucket = path_parts[0]
                key = f"/{path_parts[1]}" if len(path_parts) > 1 else "/"
                return f"https://{bucket}.s3.amazonaws.com{key}"

            raise UriSchemaError(f"Unrecognized S3 URL format: {value!r}")

        raise UriSchemaError(f"Invalid S3Uri: {value!r}")

    @classmethod
    def validate(cls, value: Any) -> S3Uri:
        return cls(cls._validate(value))

    def as_uri(self) -> str:
        # https://bucket.s3.amazonaws.com/key → s3://bucket/key
        p = urlparse(str(self))
        bucket = (p.hostname or "").split(".")[0]
        return f"s3://{bucket}{p.path}"


# Auto-register when this module is imported
AnyUri.register(S3Uri)

__all__ = ["S3Uri"]
```

- [ ] **Step 4: Run tests**

```bash
uv run pytest tests/providers/test_s3.py -v
```

Expected: all 4 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/anyuri/providers/_s3.py tests/providers/test_s3.py
git commit -m "feat: add S3Uri provider for AWS S3"
```

---

### Task 8: AzureUri Provider

**Files:**
- Create: `src/anyuri/providers/_azure.py`
- Create: `tests/providers/test_azure.py`

- [ ] **Step 1: Write failing tests**

Create `tests/providers/test_azure.py`:

```python
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
```

- [ ] **Step 2: Run to verify failure**

```bash
uv run pytest tests/providers/test_azure.py -v
```

Expected: `ImportError` — `anyuri.providers._azure` does not exist.

- [ ] **Step 3: Create `src/anyuri/providers/_azure.py`**

```python
"""AzureUri — Azure Blob Storage URI type."""

from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

from anyuri._exceptions import UriSchemaError
from anyuri import AnyUri


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
```

- [ ] **Step 4: Run tests**

```bash
uv run pytest tests/providers/test_azure.py -v
```

Expected: all 4 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/anyuri/providers/_azure.py tests/providers/test_azure.py
git commit -m "feat: add AzureUri provider for Azure Blob Storage"
```

---

### Task 9: R2Uri Provider

**Files:**
- Create: `src/anyuri/providers/_r2.py`
- Create: `tests/providers/test_r2.py`

- [ ] **Step 1: Write failing tests**

Create `tests/providers/test_r2.py`:

```python
import pytest
from anyuri import AnyUri
from anyuri._exceptions import UriSchemaError
from anyuri.providers._r2 import R2Uri  # importing registers R2Uri


@pytest.mark.parametrize(
    "uri, expected_uri, expected_source",
    [
        (
            "r2://accountid/mybucket/key.jpg",
            "r2://accountid/mybucket/key.jpg",
            "https://accountid.r2.cloudflarestorage.com/mybucket/key.jpg",
        ),
        (
            "https://accountid.r2.cloudflarestorage.com/mybucket/key.jpg",
            "r2://accountid/mybucket/key.jpg",
            "https://accountid.r2.cloudflarestorage.com/mybucket/key.jpg",
        ),
        (
            "r2://acc/bucket/dir/file.parquet",
            "r2://acc/bucket/dir/file.parquet",
            "https://acc.r2.cloudflarestorage.com/bucket/dir/file.parquet",
        ),
    ],
)
def test_r2uri(uri: str, expected_uri: str, expected_source: str) -> None:
    result = AnyUri(uri)
    assert isinstance(result, R2Uri)
    assert result.as_uri() == expected_uri
    assert result.as_source() == expected_source
    assert str(result) == expected_source


def test_r2uri_isinstance_anyuri() -> None:
    uri = AnyUri("r2://accountid/bucket/key.jpg")
    assert isinstance(uri, AnyUri)
    assert isinstance(uri, R2Uri)


def test_r2uri_invalid_scheme() -> None:
    with pytest.raises(UriSchemaError):
        R2Uri("s3://bucket/key")


def test_r2uri_invalid_host() -> None:
    with pytest.raises(UriSchemaError):
        R2Uri("https://account.notcloudflare.com/bucket/key")
```

- [ ] **Step 2: Run to verify failure**

```bash
uv run pytest tests/providers/test_r2.py -v
```

Expected: `ImportError` — `anyuri.providers._r2` does not exist.

- [ ] **Step 3: Create `src/anyuri/providers/_r2.py`**

```python
"""R2Uri — Cloudflare R2 URI type."""

from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

from anyuri._exceptions import UriSchemaError
from anyuri import AnyUri


class R2Uri(AnyUri):
    """URI for Cloudflare R2 resources.

    Accepts ``r2://<account>/<bucket>/<key>`` and HTTPS R2 storage forms.
    Stores internally as HTTPS; ``as_uri()`` returns the ``r2://`` form.

    Examples:
        >>> R2Uri("r2://accountid/bucket/key.jpg")
        R2Uri("r2://accountid/bucket/key.jpg")

        >>> R2Uri("https://accountid.r2.cloudflarestorage.com/bucket/key.jpg")
        R2Uri("r2://accountid/bucket/key.jpg")
    """

    def __new__(cls, value: Any) -> R2Uri:
        return str.__new__(cls, cls._validate(value))

    @classmethod
    def _validate(cls, value: Any) -> str:
        v = str(value)
        p = urlparse(v)

        if p.scheme == "r2":
            # r2://accountid/bucket/key → https://accountid.r2.cloudflarestorage.com/bucket/key
            account = p.netloc
            path = p.path  # /bucket/key
            return f"https://{account}.r2.cloudflarestorage.com{path}"

        if p.scheme in {"http", "https"}:
            hostname = p.hostname or ""
            if not hostname.endswith(".r2.cloudflarestorage.com"):
                raise UriSchemaError(f"Invalid host for R2Uri: {value!r}")
            return v

        raise UriSchemaError(f"Invalid R2Uri: {value!r}")

    @classmethod
    def validate(cls, value: Any) -> R2Uri:
        return cls(cls._validate(value))

    def as_uri(self) -> str:
        # https://accountid.r2.cloudflarestorage.com/bucket/key → r2://accountid/bucket/key
        p = urlparse(str(self))
        account = (p.hostname or "").split(".")[0]
        return f"r2://{account}{p.path}"


# Auto-register when this module is imported
AnyUri.register(R2Uri)

__all__ = ["R2Uri"]
```

- [ ] **Step 4: Run tests**

```bash
uv run pytest tests/providers/test_r2.py -v
```

Expected: all 4 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/anyuri/providers/_r2.py tests/providers/test_r2.py
git commit -m "feat: add R2Uri provider for Cloudflare R2"
```

---

### Task 10: B2Uri Provider

**Files:**
- Create: `src/anyuri/providers/_b2.py`
- Create: `tests/providers/test_b2.py`

> **Note:** B2Uri always normalizes to the native ``b2://bucket/key`` form because the download cluster number (``f003``, etc.) is not encoded in the native scheme. ``as_source()`` returns ``b2://bucket/key`` for all inputs. Users who need the HTTPS URL must retain the original string.

- [ ] **Step 1: Write failing tests**

Create `tests/providers/test_b2.py`:

```python
import pytest
from anyuri import AnyUri
from anyuri._exceptions import UriSchemaError
from anyuri.providers._b2 import B2Uri  # importing registers B2Uri


@pytest.mark.parametrize(
    "uri, expected_uri, expected_source",
    [
        (
            "b2://mybucket/key.jpg",
            "b2://mybucket/key.jpg",
            "b2://mybucket/key.jpg",
        ),
        (
            "https://f003.backblazeb2.com/file/mybucket/key.jpg",
            "b2://mybucket/key.jpg",
            "b2://mybucket/key.jpg",
        ),
        (
            "b2://bucket/subdir/file.parquet",
            "b2://bucket/subdir/file.parquet",
            "b2://bucket/subdir/file.parquet",
        ),
    ],
)
def test_b2uri(uri: str, expected_uri: str, expected_source: str) -> None:
    result = AnyUri(uri)
    assert isinstance(result, B2Uri)
    assert result.as_uri() == expected_uri
    assert result.as_source() == expected_source
    assert str(result) == expected_source


def test_b2uri_isinstance_anyuri() -> None:
    uri = AnyUri("b2://bucket/key.jpg")
    assert isinstance(uri, AnyUri)
    assert isinstance(uri, B2Uri)


def test_b2uri_invalid_scheme() -> None:
    with pytest.raises(UriSchemaError):
        B2Uri("s3://bucket/key")


def test_b2uri_invalid_host() -> None:
    with pytest.raises(UriSchemaError):
        B2Uri("https://example.com/file/bucket/key")


def test_b2uri_invalid_https_path() -> None:
    with pytest.raises(UriSchemaError):
        B2Uri("https://f003.backblazeb2.com/notfile/bucket/key")
```

- [ ] **Step 2: Run to verify failure**

```bash
uv run pytest tests/providers/test_b2.py -v
```

Expected: `ImportError` — `anyuri.providers._b2` does not exist.

- [ ] **Step 3: Create `src/anyuri/providers/_b2.py`**

```python
"""B2Uri — Backblaze B2 URI type."""

from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

from anyuri._exceptions import UriSchemaError
from anyuri import AnyUri


class B2Uri(AnyUri):
    """URI for Backblaze B2 resources.

    Accepts ``b2://bucket/key`` and ``https://f<N>.backblazeb2.com/file/bucket/key``.
    Always normalizes to the native ``b2://`` form; the cluster number is discarded
    because it is not derivable from the bucket name alone.

    Examples:
        >>> B2Uri("b2://mybucket/key.jpg")
        B2Uri("b2://mybucket/key.jpg")

        >>> B2Uri("https://f003.backblazeb2.com/file/mybucket/key.jpg")
        B2Uri("b2://mybucket/key.jpg")
    """

    def __new__(cls, value: Any) -> B2Uri:
        return str.__new__(cls, cls._validate(value))

    @classmethod
    def _validate(cls, value: Any) -> str:
        v = str(value)
        p = urlparse(v)

        if p.scheme == "b2":
            return v  # already canonical

        if p.scheme in {"http", "https"}:
            hostname = p.hostname or ""
            if not hostname.endswith(".backblazeb2.com"):
                raise UriSchemaError(f"Invalid host for B2Uri: {value!r}")
            # path: /file/bucket/key
            parts = p.path.lstrip("/").split("/", 2)
            if len(parts) < 2 or parts[0] != "file":
                raise UriSchemaError(f"Invalid B2 download URL path: {value!r}")
            bucket = parts[1]
            key = f"/{parts[2]}" if len(parts) > 2 else "/"
            return f"b2://{bucket}{key}"

        raise UriSchemaError(f"Invalid B2Uri: {value!r}")

    @classmethod
    def validate(cls, value: Any) -> B2Uri:
        return cls(cls._validate(value))

    def as_uri(self) -> str:
        return str(self)  # already in b2:// form


# Auto-register when this module is imported
AnyUri.register(B2Uri)

__all__ = ["B2Uri"]
```

- [ ] **Step 4: Run tests**

```bash
uv run pytest tests/providers/test_b2.py -v
```

Expected: all 5 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/anyuri/providers/_b2.py tests/providers/test_b2.py
git commit -m "feat: add B2Uri provider for Backblaze B2"
```

---

### Task 11: providers/__init__.py and Full Test Suite

**Files:**
- Modify: `src/anyuri/providers/__init__.py`

- [ ] **Step 1: Write `src/anyuri/providers/__init__.py`**

```python
"""
anyuri cloud provider URI types.

Importing from this module registers the providers with AnyUri automatically:

    >>> from anyuri.providers import GSUri, S3Uri
    >>> from anyuri import AnyUri
    >>> AnyUri("gs://bucket/key.jpg")
    GSUri("gs://bucket/key.jpg")
"""

from anyuri.providers._gcs import GSUri
from anyuri.providers._s3 import S3Uri
from anyuri.providers._azure import AzureUri
from anyuri.providers._r2 import R2Uri
from anyuri.providers._b2 import B2Uri

__all__ = ["GSUri", "S3Uri", "AzureUri", "R2Uri", "B2Uri"]
```

- [ ] **Step 2: Run the full test suite**

```bash
uv run pytest -v
```

Expected: all tests PASS.

- [ ] **Step 3: Commit**

```bash
git add src/anyuri/providers/__init__.py
git commit -m "feat: export all providers from anyuri.providers"
```

---

### Task 12: GitHub Actions CI/CD

**Files:**
- Create: `.github/workflows/test.yml`
- Create: `.github/workflows/lint.yml`
- Create: `.github/workflows/release.yml`

- [ ] **Step 1: Create `.github/workflows/test.yml`**

```yaml
name: Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12", "3.13"]

    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v4

      - name: Set up Python ${{ matrix.python-version }}
        run: uv python install ${{ matrix.python-version }}

      - name: Install dependencies
        run: uv sync --python ${{ matrix.python-version }}

      - name: Run tests
        run: uv run pytest --cov=anyuri --cov-report=term-missing -v
```

- [ ] **Step 2: Create `.github/workflows/lint.yml`**

```yaml
name: Lint

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v4

      - name: Install dependencies
        run: uv sync

      - name: Run ruff
        run: uv run ruff check src/ tests/

      - name: Run mypy
        run: uv run mypy src/anyuri/
```

- [ ] **Step 3: Create `.github/workflows/release.yml`**

```yaml
name: Release

on:
  push:
    tags:
      - "v*.*.*"

jobs:
  release:
    runs-on: ubuntu-latest
    environment: release
    permissions:
      id-token: write  # required for PyPI Trusted Publishing

    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # required for setuptools-scm to determine version

      - name: Install uv
        uses: astral-sh/setup-uv@v4

      - name: Install build deps
        run: uv sync

      - name: Build package
        run: uv run python -m build

      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
```

- [ ] **Step 4: Commit**

```bash
git add .github/
git commit -m "ci: add GitHub Actions for test, lint, and release"
```

- [ ] **Step 5: Push to GitHub**

```bash
git push origin main
```

- [ ] **Step 6: Configure PyPI Trusted Publishing**

In PyPI (pypi.org), create the `anyuri` project and configure a Trusted Publisher:
- Publisher: GitHub Actions
- Owner: `lucemia`
- Repository: `anyuri`
- Workflow filename: `release.yml`
- Environment name: `release`

In GitHub, create the `release` environment under Settings → Environments.

---

### Task 13: README

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Write `README.md`**

```markdown
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
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add README with usage examples and provider table"
```

- [ ] **Step 3: Push all commits**

```bash
git push origin main
```

---

## Self-Review

**Spec coverage check:**

| Spec requirement | Task |
|---|---|
| Standalone package, zero mandatory deps | Task 1 (pyproject.toml) |
| `AnyUri`, `HttpUri`, `FileUri` | Task 3 |
| Registry: `AnyUri.register()` + `@AnyUri.register` | Task 3 + 5 |
| `GSUri` | Task 6 |
| `S3Uri` | Task 7 |
| `AzureUri` (abfs://) | Task 8 |
| `R2Uri` | Task 9 |
| `B2Uri` | Task 10 |
| Pydantic v1/v2 integration | Task 3 (`__init__.py`) |
| Optional extras | Task 1 (`pyproject.toml`) |
| Snapshot tests | Task 4 |
| CI: test, lint, release | Task 12 |
| README | Task 13 |

All requirements covered. No placeholders. Types are consistent across tasks.
