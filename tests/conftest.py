from __future__ import annotations

from typing import Any, no_type_check

import pytest

from anyuri import AnyUri


@no_type_check
def parse_obj_as(cls: type[AnyUri], obj: Any) -> AnyUri:
    """Validate using Pydantic v1 or v2, whichever is installed."""
    try:
        from pydantic import TypeAdapter
        return TypeAdapter(cls).validate_python(obj)
    except ImportError:
        from pydantic import parse_obj_as as _parse
        return _parse(cls, obj)


@pytest.fixture
def clean_registry():
    """Restore the AnyUri registry after the test (prevents test pollution)."""
    original = AnyUri._registry.copy()
    yield
    AnyUri._registry = original
