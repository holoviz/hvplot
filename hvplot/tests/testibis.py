"""Basic ibis tests"""

import numpy as np
import pandas as pd
import pytest

from hvplot.util import hv_version
from packaging.version import Version

try:
    import hvplot.ibis  # noqa
    import ibis
except ImportError:
    pytest.skip(allow_module_level=True)


@pytest.mark.skipif(hv_version <= Version("1.17"), reason="Not supported")
def test_ibis_hist():
    df = pd.DataFrame(dict(x=np.arange(10)))
    table = ibis.memtable(df)
    table.hvplot.hist('x')
