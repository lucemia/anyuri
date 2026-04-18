"""R2Uri — Cloudflare R2 URI type."""

from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

from anyuri import AnyUri
from anyuri._exceptions import UriSchemaError


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
        """Validate and return an ``R2Uri`` for ``value``.

        Args:
            value: An ``r2://account/bucket/key`` or
                ``https://<account>.r2.cloudflarestorage.com/`` URI string.

        Raises:
            UriSchemaError: If ``value`` is not a valid R2 URI.
        """
        return cls(cls._validate(value))

    def as_uri(self) -> str:
        """Return the canonical ``r2://account/bucket/key`` form.

        Returns:
            An ``r2://`` URI string.
        """
        # https://accountid.r2.cloudflarestorage.com/bucket/key → r2://accountid/bucket/key
        p = urlparse(str(self))
        account = (p.hostname or "").split(".")[0]
        return f"r2://{account}{p.path}"


# Auto-register when this module is imported
AnyUri.register(R2Uri)

__all__ = ["R2Uri"]
