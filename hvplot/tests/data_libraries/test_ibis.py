"""Basic ibis tests"""

import numpy as np
import pandas as pd
import pytest
from packaging import version

import hvplot

try:
    # Used as default in-memory backend by ibis
    import duckdb  # noqa: F401
    import ibis
except ImportError:
    pytest.skip(allow_module_level=True)


@pytest.fixture(autouse=True)
def hvplot_ibis():
    import hvplot.ibis  # noqa: F401


def test_ibis_hist():
    import duckdb

    if version.parse(ibis.__version__) <= version.parse('10.8.0') and version.parse(
        duckdb.__version__
    ) >= version.parse('1.4'):
        pytest.skip('Ibis <= 10.8.0 is incompatible with DuckDB >= 1.4')

    df = pd.DataFrame({'x': np.arange(10)})
    table = ibis.memtable(df)
    table.hvplot.hist('x')


def _patched(classes, attrs):
    return all(attr in vars(cls) for cls in classes for attr in attrs)


def _unpatched(classes, attrs):
    return not any(attr in vars(cls) for cls in classes for attr in attrs)


def _round_trip(ext, classes, attrs=('hvplot',)):
    # Ends patched, so the _isolate_hvplot fixture unpatches the extension
    # and removes its module from sys.modules after the test.
    ext.patch()
    assert _patched(classes, attrs)
    assert ext.__name__ in hvplot._module_extensions

    ext._unpatch()
    assert _unpatched(classes, attrs)
    assert ext.__name__ not in hvplot._module_extensions

    ext.patch()
    assert _patched(classes, attrs)
    assert ext.__name__ in hvplot._module_extensions


def test_unpatch_ibis():
    ibis = pytest.importorskip('ibis')
    import hvplot.ibis

    _round_trip(hvplot.ibis, [ibis.Expr])
