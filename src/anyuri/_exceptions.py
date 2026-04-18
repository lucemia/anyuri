class UriSchemaError(ValueError):
    """Raised when a URI cannot be validated by any registered URI type."""


class DownloadError(Exception):
    """Raised when a download operation fails."""


class UploadError(Exception):
    """Raised when an upload operation fails."""


__all__ = ["UriSchemaError", "DownloadError", "UploadError"]
