from __future__ import annotations

import sys
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_boto3() -> MagicMock:
    m = MagicMock()
    orig = sys.modules.get("boto3")
    sys.modules["boto3"] = m
    yield m
    if orig is None:
        sys.modules.pop("boto3", None)
    else:
        sys.modules["boto3"] = orig
