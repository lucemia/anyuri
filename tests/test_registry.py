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
