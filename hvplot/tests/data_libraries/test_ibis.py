import numpy as np
import pandas as pd
import pytest
from packaging.version import Version

import hvplot
from hvplot.tests._deps import requires

# ibis is optional, it is imported in the tests. duckdb is its default backend.
pytestmark = requires('ibis', 'duckdb')


@pytest.fixture(autouse=True)
def hvplot_ibis():
    import hvplot.ibis  # noqa: F401


def test_ibis_hist():
    import duckdb
    import ibis

    if Version(ibis.__version__) <= Version('10.8.0') and Version(duckdb.__version__) >= Version(
        '1.4'
    ):
        pytest.skip('Ibis <= 10.8.0 is incompatible with DuckDB >= 1.4')

    table = ibis.memtable(pd.DataFrame({'x': np.arange(10)}))
    table.hvplot.hist('x')


def test_unpatch_ibis():
    import ibis

    hvplot.ibis._unpatch()
    assert 'hvplot' not in vars(ibis.Expr)
    assert 'hvplot.ibis' not in hvplot._module_extensions

    # Ends patched, the _isolate_hvplot fixture unpatches it after the test.
    hvplot.ibis.patch()
    assert 'hvplot' in vars(ibis.Expr)
    assert 'hvplot.ibis' in hvplot._module_extensions
