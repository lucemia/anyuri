from __future__ import annotations

import os
import re
import tempfile
from uuid import uuid4

from anyuri import AnyUri, FileUri
from anyuri._exceptions import UriSchemaError
from anyuri.io._registry import _download_registry, _upload_registry


def _extract_ext(uri: AnyUri) -> str | None:
    name = uri.path.rstrip("/").rsplit("/", 1)[-1]
    m = re.search(r"\.[A-Za-z0-9]{1,10}$", name)
    return m.group(0) if m else None


def _dispatch_download(uri: AnyUri) -> FileUri:
    handler = _download_registry.get(type(uri))
    if handler is None:
        raise UriSchemaError(f"No download handler registered for {type(uri).__name__}")
    fd, path = tempfile.mkstemp(suffix=_extract_ext(uri) or ".tmp")
    os.close(fd)
    return handler(uri, FileUri(path))


def _dispatch_upload(src: FileUri, dst: AnyUri) -> AnyUri:
    handler = _upload_registry.get(type(dst))
    if handler is None:
        raise UriSchemaError(f"No upload handler registered for {type(dst).__name__}")
    return handler(src, dst)


def download(uri: AnyUri | str) -> FileUri:
    """Download any URI to a local temp file.

    Fetches the resource at ``uri`` and writes it to a new temporary file,
    preserving the source file extension (e.g. ``video.mp4`` → ``/tmp/abc123.mp4``).
    Falls back to ``.tmp`` if no extension is found.

    The caller owns the returned file and is responsible for cleanup.

    Args:
        uri: Any supported URI — ``https://``, ``gs://``, ``s3://``,
            ``abfs://``, ``r2://``, or a local path/``file://``.
            Accepts a plain string or any ``AnyUri`` subclass.

    Returns:
        A ``FileUri`` pointing to the downloaded temp file.

    Raises:
        UriSchemaError: If no download handler is registered for the URI type.
        ImportError: If the required cloud SDK is not installed
            (e.g. ``pip install anyuri[gcs]``).
        DownloadError: If the underlying SDK or network call fails.

    Examples:
        >>> from anyuri.io import download
        >>> local = download("https://example.com/video.mp4")
        >>> local = download("gs://bucket/video.mp4")
        >>> local = download("/existing/local/file.mp4")  # copies to temp
    """
    return _dispatch_download(uri if isinstance(uri, AnyUri) else AnyUri(uri))


def upload(src: AnyUri | str, dst: AnyUri | str) -> AnyUri:
    """Upload a file to a cloud destination.

    If ``src`` is not a local file, it is downloaded first via :func:`download`.
    If ``dst`` ends with ``/``, a filename of ``<uuid><ext>`` is appended
    automatically (e.g. ``gs://bucket/videos/`` → ``gs://bucket/videos/abc123.mp4``).
    Otherwise ``dst`` is used as the exact destination path.

    Args:
        src: Source file — a local path, ``file://`` URI, or any remote URI
            (which will be downloaded automatically before uploading).
        dst: Destination URI. Must be a supported cloud provider scheme
            (``gs://``, ``s3://``, ``abfs://``, ``r2://``).
            Append a trailing ``/`` to auto-generate a filename.

    Returns:
        The concrete URI of the uploaded file, typed to match ``dst``
        (e.g. ``GSUri``, ``S3Uri``).

    Raises:
        UriSchemaError: If no upload handler is registered for the destination URI type.
        ImportError: If the required cloud SDK is not installed.
        UploadError: If the underlying SDK call fails.

    Examples:
        >>> from anyuri.io import upload
        >>> result = upload("/local/video.mp4", "gs://bucket/videos/")
        >>> result = upload("/local/video.mp4", "s3://bucket/output.mp4")
        >>> result = upload("https://example.com/img.jpg", "gs://bucket/")  # remote src
        >>> result = upload("gs://src/video.mp4", "s3://dst/")  # cloud-to-cloud
    """
    src_uri = src if isinstance(src, AnyUri) else AnyUri(src)
    dst_uri = dst if isinstance(dst, AnyUri) else AnyUri(dst)
    if not isinstance(src_uri, FileUri):
        src_uri = download(src_uri)
    if str(dst_uri).endswith("/"):
        ext = _extract_ext(src_uri) or ".tmp"
        dst_uri = AnyUri(str(dst_uri) + uuid4().hex + ext)
    return _dispatch_upload(src_uri, dst_uri)


__all__ = ["download", "upload"]
