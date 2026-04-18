import os
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse, urlunparse


def normalize_url(http_uri: str) -> str:
    """Normalize an HTTP URI by resolving ``..`` and ``.`` path segments.

    Args:
        http_uri: A well-formed HTTP or HTTPS URI string.

    Returns:
        The same URI with dot-segments resolved in the path component.

    Examples:
        >>> normalize_url("https://example.com/a/../b.jpg")
        'https://example.com/b.jpg'
    """
    parsed = urlparse(http_uri)
    resolved = urljoin(http_uri, parsed.path)
    return urlunparse(parsed._replace(path=urlparse(resolved).path))


def uri_to_path(file_uri: str) -> str:
    """Convert a ``file://`` URI to a local filesystem path string.

    Handles percent-encoded characters and Windows drive letters.

    Args:
        file_uri: A ``file:///path`` or ``file://localhost/path`` URI string.

    Returns:
        A normalized local filesystem path (uses ``os.sep`` on Windows).

    Raises:
        ValueError: If the URI scheme is not ``file``.

    Examples:
        >>> uri_to_path("file:///tmp/video.mp4")
        '/tmp/video.mp4'
        >>> uri_to_path("file:///tmp/my%20file.mp4")
        '/tmp/my file.mp4'
    """
    parsed = urlparse(file_uri)
    if parsed.scheme != "file":
        raise ValueError(f"Unsupported scheme: {parsed.scheme!r}")
    path_str = unquote(parsed.path)
    # Windows: "/C:/..." → "C:/..."
    if os.name == "nt" and path_str.startswith("/") and len(path_str) > 2 and path_str[2] == ":":
        path_str = path_str[1:]
    return os.path.normpath(Path(path_str))


__all__ = ["normalize_url", "uri_to_path"]
