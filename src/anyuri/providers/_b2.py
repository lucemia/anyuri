"""B2Uri — Backblaze B2 URI type."""

from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

from anyuri import AnyUri
from anyuri._exceptions import UriSchemaError


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
        """Validate and return a ``B2Uri`` for ``value``.

        Args:
            value: A ``b2://bucket/key`` or
                ``https://f<N>.backblazeb2.com/file/bucket/key`` URI string.

        Raises:
            UriSchemaError: If ``value`` is not a valid B2 URI.
        """
        return cls(cls._validate(value))

    def as_uri(self) -> str:
        """Return the canonical ``b2://bucket/key`` form.

        Returns:
            A ``b2://`` URI string.
        """
        return str(self)  # already in b2:// form


# Auto-register when this module is imported
AnyUri.register(B2Uri)

__all__ = ["B2Uri"]
