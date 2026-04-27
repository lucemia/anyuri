"""
I/O extension for anyuri — download and upload across all supported providers.

Importing this module registers built-in handlers for all seven URI types.
Cloud SDKs are lazy-imported, so ``import anyuri.io`` is always safe even if
no cloud SDK is installed; errors only surface when a handler is actually called.

    >>> from anyuri.io import download, upload
    >>> local = download("gs://bucket/video.mp4")
    >>> result = upload("/local/video.mp4", "s3://bucket/videos/")
"""

from anyuri.io._core import download, upload
from anyuri.io._handlers import _azure, _file, _gcs, _http, _r2, _s3  # noqa: F401
from anyuri.io._registry import register_download, register_upload

__all__ = ["download", "upload", "register_download", "register_upload"]
