class UriSchemaError(ValueError):
    """Raised when a URI cannot be validated by any registered URI type."""


__all__ = ["UriSchemaError"]
