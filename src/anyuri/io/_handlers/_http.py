from __future__ import annotations

from urllib.request import Request, urlopen

from anyuri import FileUri, HttpUri
from anyuri.io._registry import register_download


@register_download(HttpUri)
def _http_download(uri: HttpUri, target: FileUri) -> FileUri:
    req = Request(str(uri), headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req) as response:
        with open(str(target), "wb") as f:
            while chunk := response.read(1 << 16):
                f.write(chunk)
    return target
