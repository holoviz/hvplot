import sys
from collections.abc import Callable

import param
import pytest

param.parameterized.warnings_as_exceptions = True


@pytest.fixture
def unimport(monkeypatch: pytest.MonkeyPatch) -> Callable[[str], None]:
    """
    Return a function for unimporting modules and preventing reimport.

    This will block any new modules from being imported.
    """

    def unimport_module(modname: str) -> None:
        # Remove if already imported
        monkeypatch.delitem(sys.modules, modname, raising=False)
        items = [m for m in sys.modules if m.startswith(f'{modname}.')]
        for item in items:
            monkeypatch.delitem(sys.modules, item, raising=False)
        # Prevent import:
        monkeypatch.setattr(sys, 'path', [])

    return unimport_module


@pytest.fixture
def disable_param_warnings_as_exceptions():
    original = param.parameterized.warnings_as_exceptions
    param.parameterized.warnings_as_exceptions = False
    try:
        yield
    finally:
        param.parameterized.warnings_as_exceptions = original
