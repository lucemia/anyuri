from __future__ import annotations

import shutil

from anyuri import FileUri
from anyuri.io._registry import register_download


@register_download(FileUri)
def _file_download(uri: FileUri, target: FileUri) -> FileUri:
    shutil.copy(str(uri), str(target))
    return target

