# Comparison with Similar Packages

This page compares `anyuri` with other Python URI/URL libraries across the features that matter most for real-world data pipelines: cloud storage support, `str` compatibility, Pydantic integration, and polymorphic dispatch.

## Feature Matrix

| Feature | anyuri | pydantic `AnyUrl` | furl | yarl | cloudpathlib | smart-open |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| Plain `str` subclass | ✅ | ❌ (v2) | ❌ | ❌ | ❌ | ❌ |
| Pydantic v1 integration | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Pydantic v2 integration | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ |
| HTTP/HTTPS URIs | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| Local file URIs | ✅ | ❌ | ✅ | ✅ | ❌ | ✅ |
| GCS (`gs://`) | ✅ | ❌ | ❌ | ❌ | ✅ | ✅ |
| S3 (`s3://`) | ✅ | ❌ | ❌ | ❌ | ✅ | ✅ |
| Azure Blob Storage | ✅ | ❌ | ❌ | ❌ | ✅ | ✅ |
| R2 (`r2://`) | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Polymorphic dispatch | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| URI ↔ HTTPS conversion | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Extensible (custom types) | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Zero hard dependencies | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Download / upload I/O | ✅ | ❌ | ❌ | ❌ | ✅ | ✅ |

## Package Summaries

### pydantic `AnyUrl` / `HttpUrl`

Pydantic's built-in network types validate URL structure and are deeply integrated with Pydantic models. However, in Pydantic v2 they are **no longer `str` subclasses** — they return `pydantic_core.Url` objects, which breaks code that passes them directly to APIs expecting strings. They have no concept of cloud storage schemes.

```python
# pydantic v2
from pydantic import HttpUrl
url = HttpUrl("https://example.com/file.jpg")
isinstance(url, str)  # False — breaks string APIs
```

```python
# anyuri — always a str
from anyuri import AnyUri
uri = AnyUri("https://example.com/file.jpg")
isinstance(uri, str)  # True
```

**Choose pydantic URLs when** you only need HTTP validation inside Pydantic models and don't pass URIs to string-based APIs.

**Choose anyuri when** your URIs flow through string-based libraries (logging, templating, HTTP clients) or span multiple storage backends.

---

### furl

`furl` excels at **URL construction and mutation** — building query strings, replacing path segments, and chaining operations. It is not designed for validation or cloud storage, and is not a `str` subclass.

```python
from furl import furl
f = furl("https://example.com").add(path="file.jpg").add(args={"v": "1"})
str(f)  # "https://example.com/file.jpg?v=1"
```

**Choose furl when** you need to programmatically construct or mutate HTTP URLs.

**Choose anyuri when** you receive URIs from external sources and need to identify and normalize them across storage backends.

---

### yarl

`yarl` provides immutable URL objects with full RFC 3986 component access and is the URL type used internally by `aiohttp`. It has Pydantic v2 support but is not a `str` subclass and has no cloud storage awareness.

```python
from yarl import URL
url = URL("gs://bucket/key.jpg")
url.scheme  # "gs" — parsed, but no cloud-specific semantics
```

**Choose yarl when** you are building async HTTP clients or need strict RFC 3986 parsing.

**Choose anyuri when** you need cloud-aware semantics (`as_uri()` / `as_source()` conversions) or must pass URIs as plain strings.

---

### cloudpathlib

`cloudpathlib` provides a `pathlib.Path`-style interface for GCS, S3, and Azure — great for filesystem operations (open, stat, iterdir). It is not `str`-based, has no Pydantic integration, and does not handle HTTP or local file URIs.

```python
from cloudpathlib import S3Path
p = S3Path("s3://bucket/key.jpg")
p.read_bytes()  # reads from S3
```

**Choose cloudpathlib when** you need path manipulation and file I/O against cloud storage buckets.

**Choose anyuri when** you need a lightweight URI type that serializes cleanly as a string and works across local, HTTP, and cloud schemes without pulling in cloud SDKs unless you opt in.

---

### smart-open

`smart-open` is a streaming I/O library — it opens `s3://`, `gs://`, `azure://`, and local file URIs as file-like objects. URI parsing is a means to an end (opening the file), not an exposed type system.

```python
import smart_open
with smart_open.open("s3://bucket/key.txt") as f:
    data = f.read()
```

**Choose smart-open when** your primary need is streaming reads/writes across storage backends.

**Choose anyuri when** you need to store, pass, compare, and convert URIs as values — decoupled from any I/O operation.

---

## Why anyuri

`anyuri` fills a specific gap: a **zero-dependency URI value type** that:

1. **Is a `str`** — passes transparently to any API that accepts strings.
2. **Auto-dispatches** — `AnyUri("gs://...")` returns a `GSUri`, not a generic object.
3. **Normalizes across representations** — `as_uri()` gives the canonical form; `as_source()` (= `str()`) gives the HTTPS form accepted by most HTTP clients and CDNs.
4. **Works with Pydantic v1 and v2** — field validation and serialization just work.
5. **Is opt-in for cloud** — cloud providers register themselves on import; the core package has no dependencies.
6. **Is extensible** — register your own URI types with `@AnyUri.register`.
