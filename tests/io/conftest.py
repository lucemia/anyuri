# tests/io/conftest.py
import pytest
from anyuri.io._registry import _download_registry, _upload_registry


@pytest.fixture
def clean_io_registry():
    orig_down = dict(_download_registry)
    orig_up = dict(_upload_registry)
    yield
    _download_registry.clear()
    _download_registry.update(orig_down)
    _upload_registry.clear()
    _upload_registry.update(orig_up)
