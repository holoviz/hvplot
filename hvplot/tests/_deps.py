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


# The data libraries run by the `tabular_lib` and `gridded_lib` fixtures. A new library is added
# here and in the fixture, and then runs in every test using the fixture.
TABULAR_LIBS = ['pandas', 'dask', 'polars', 'duckdb', 'ibis']
GRIDDED_LIBS = ['xarray', 'dask']

# These tests come from the old Dask test subclasses: they need an index and the pandas API, and
# dask has its own code paths in hvPlot (index reset, melt, compute of ranges, persist).
# The other libraries are compared with pandas in `data_libraries/test_tabular_parity.py`.
pandas_and_dask = pytest.mark.parametrize('tabular_lib', ['pandas', 'dask'], indirect=True)
