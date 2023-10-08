"""Basic ibis tests"""

import numpy as np
import pandas as pd
import pytest

try:
    import hvplot.ibis  # noqa
    import ibis
except ImportError:
    pytest.skip(allow_module_level=True)


def test_ibis_hist():
    df = pd.DataFrame(dict(x=np.arange(10)))
    table = ibis.memtable(df)
    table.hvplot.hist('x')
