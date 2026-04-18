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
