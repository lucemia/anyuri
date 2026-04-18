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
