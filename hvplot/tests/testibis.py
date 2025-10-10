"""Basic ibis tests"""

import numpy as np
import pandas as pd
import pytest

from packaging import version


try:
    import hvplot.ibis  # noqa
    import ibis

    # Used as default in-memory backend by ibis
    import duckdb  # noqa
except ImportError:
    pytest.skip(allow_module_level=True)


def test_ibis_hist():
    import duckdb

    if version.parse(ibis.__version__) <= version.parse('10.8.0') and version.parse(
        duckdb.__version__
    ) >= version.parse('1.4'):
        pytest.skip('Ibis <= 10.8.0 is incompatible with DuckDB >= 1.4')

    df = pd.DataFrame(dict(x=np.arange(10)))
    table = ibis.memtable(df)
    table.hvplot.hist('x')
