"""S3Uri — AWS S3 URI type."""

from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

from anyuri import AnyUri
from anyuri._exceptions import UriSchemaError


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
