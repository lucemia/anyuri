# I/O — Download & Upload

`anyuri.io` adds download and upload to the AnyUri type system. It requires no changes to the zero-dependency core; cloud SDKs are lazy-imported and only needed when the corresponding handler is actually called.

```python
from anyuri.io import download, upload
```

## Functions

::: anyuri.io.download

::: anyuri.io.upload

## Extending with custom handlers

Register handlers for your own URI types using the same decorators the built-in providers use:

```python
from anyuri import AnyUri, FileUri
from anyuri.io._registry import register_download, register_upload

@AnyUri.register
class SFTPUri(AnyUri): ...

@register_download(SFTPUri)
def _sftp_download(uri: SFTPUri, target: FileUri) -> FileUri:
    # fetch from SFTP, write to target
    return target

@register_upload(SFTPUri)
def _sftp_upload(src: FileUri, dst: SFTPUri) -> SFTPUri:
    # push src to SFTP
    return dst
```

## Registry

::: anyuri.io.register_download

::: anyuri.io.register_upload
