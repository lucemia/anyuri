import os
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse, urlunparse


def normalize_url(http_uri: str) -> str:
    """Normalize an HTTP URI by resolving '..' and '.' segments in the path."""
    parsed = urlparse(http_uri)
    resolved = urljoin(http_uri, parsed.path)
    return urlunparse(parsed._replace(path=urlparse(resolved).path))


def uri_to_path(file_uri: str) -> str:
    """Convert a file:// URI to a local filesystem path."""
    parsed = urlparse(file_uri)
    if parsed.scheme != "file":
        raise ValueError(f"Unsupported scheme: {parsed.scheme!r}")
    path_str = unquote(parsed.path)
    # Windows: "/C:/..." → "C:/..."
    if os.name == "nt" and path_str.startswith("/") and len(path_str) > 2 and path_str[2] == ":":
        path_str = path_str[1:]
    return os.path.normpath(Path(path_str))


__all__ = ["normalize_url", "uri_to_path"]
