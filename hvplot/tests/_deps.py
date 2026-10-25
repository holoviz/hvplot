from importlib.metadata import version
from importlib.util import find_spec

import pytest
from packaging.version import Version


def requires(*modules):
    """Skip marker for tests that need optional modules.

    Use it on a test (`@requires('datashader')`) or on a whole module
    (`pytestmark = requires('geoviews', 'cartopy')`).
    """
    missing = [m for m in modules if find_spec(m) is None]
    return pytest.mark.skipif(bool(missing), reason=f'requires {", ".join(missing)}')


# pl.NUMERIC_DTYPES, used by hvPlot, was removed in polars 2.0.
POLARS_2 = find_spec('polars') is not None and Version(version('polars')).major >= 2


# The data libraries run by the `tabular_lib` and `gridded_lib` fixtures. To add a library:
# 1. Add it here and a branch to the fixture in `conftest.py`, converting a pandas DataFrame (or an
#    xarray object) to the library's object and skipping the test if it isn't installed
#    (`pytest.importorskip`). It now runs in every test using the fixture.
# 2. Add it to the `test` feature of `pixi.toml` and to the `tests` extra of `pyproject.toml`.
# 3. Add it to `PATCHED` and `CLASSES` in `data_libraries/test_accessors.py`. Don't add a test
#    module for it: what only this library does is tested with the kinds and options.
# 4. Run the test suite and mark the failures: `lib_xfail` (hvPlot bugs) or `lib_skip` (not
#    applicable) on the tests, `BUGS` or `SKIPS` in `data_libraries/test_tabular_parity.py` and
#    `LIB_FAILURES` in `kinds/test_all_kinds.py`. The tests restricted with `pandas_and_dask` don't
#    run with it, check that `test_tabular_parity.py` covers what is specific to it.
# 5. Add it to the table of `doc/ref/data_libraries.ipynb`.
TABULAR_LIBS = ['pandas', 'dask', 'polars', 'duckdb', 'ibis']
GRIDDED_LIBS = ['xarray', 'dask']

# These tests come from the old Dask test subclasses: they need an index and the pandas API, and
# dask has its own code paths in hvPlot (index reset, melt, compute of ranges, persist).
# The other libraries are compared with pandas in `data_libraries/test_tabular_parity.py`.
pandas_and_dask = pytest.mark.parametrize('tabular_lib', ['pandas', 'dask'], indirect=True)
