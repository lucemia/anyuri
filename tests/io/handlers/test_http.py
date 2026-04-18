# tests/io/handlers/test_http.py
import pathlib
from unittest.mock import MagicMock, patch

from anyuri import FileUri, HttpUri
from anyuri.io._handlers._http import _http_download


def test_http_download_writes_response(tmp_path: pathlib.Path) -> None:
    uri = HttpUri("https://example.com/video.mp4")
    target = FileUri(str(tmp_path / "video.mp4"))

    mock_response = MagicMock()
    mock_response.__enter__ = lambda s: s
    mock_response.__exit__ = MagicMock(return_value=False)
    mock_response.read.return_value = b"video content"

    with patch("anyuri.io._handlers._http.urlopen", return_value=mock_response):
        result = _http_download(uri, target)

    assert result == target
    with open(str(target), "rb") as f:
        assert f.read() == b"video content"


def test_http_download_sets_user_agent(tmp_path: pathlib.Path) -> None:
    uri = HttpUri("https://example.com/img.jpg")
    target = FileUri(str(tmp_path / "img.jpg"))

    mock_response = MagicMock()
    mock_response.__enter__ = lambda s: s
    mock_response.__exit__ = MagicMock(return_value=False)
    mock_response.read.return_value = b""

    with patch("anyuri.io._handlers._http.urlopen") as mock_urlopen:
        mock_urlopen.return_value = mock_response
        _http_download(uri, target)
        call_args = mock_urlopen.call_args[0][0]
        assert call_args.get_header("User-agent") == "Mozilla/5.0"
