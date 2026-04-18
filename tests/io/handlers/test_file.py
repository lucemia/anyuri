# tests/io/handlers/test_file.py
import pathlib

from anyuri import FileUri
from anyuri.io._handlers._file import _file_download


def test_file_download_copies_file(tmp_path: pathlib.Path) -> None:
    src_path = str(tmp_path / "src.txt")
    dst_path = str(tmp_path / "dst.txt")
    with open(src_path, "w") as f:
        f.write("hello world")

    src = FileUri(src_path)
    target = FileUri(dst_path)

    result = _file_download(src, target)

    assert result == target
    with open(dst_path) as f:
        assert f.read() == "hello world"


def test_file_download_returns_target(tmp_path: pathlib.Path) -> None:
    src_path = str(tmp_path / "a.bin")
    dst_path = str(tmp_path / "b.bin")
    with open(src_path, "wb") as f:
        f.write(b"\x00\x01\x02")

    src = FileUri(src_path)
    target = FileUri(dst_path)

    result = _file_download(src, target)
    assert result is target
