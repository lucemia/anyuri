class UriSchemaError(ValueError):
    """Raised when a URI string does not match any registered URI type.

    This is a subclass of ``ValueError`` so it integrates naturally with
    Pydantic validation — an invalid URI field raises a ``ValidationError``
    whose cause is a ``UriSchemaError``.

    Also raised by :func:`anyuri.io.download` and :func:`anyuri.io.upload`
    when no I/O handler is registered for the given URI type.
    """


class DownloadError(Exception):
    """Raised when a download handler fails to fetch a remote resource.

    The original SDK or network exception is chained as ``__cause__``.
    An ``ImportError`` (not a ``DownloadError``) is raised instead when
    the required cloud SDK is not installed.
    """


class UploadError(Exception):
    """Raised when an upload handler fails to push a local file to a destination.

    The original SDK exception is chained as ``__cause__``.
    An ``ImportError`` (not an ``UploadError``) is raised instead when
    the required cloud SDK is not installed.
    """


__all__ = ["UriSchemaError", "DownloadError", "UploadError"]
